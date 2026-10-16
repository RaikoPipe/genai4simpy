"""Deterministic SimPy compiler: typed simulation spec -> contract-v2 simulation.py.

Proposal P3(a). The generated module is a generic engine plus the spec embedded
as data, so every number in the model is traceable to the spec, and nothing
specific to observed cases (ids, timestamps, the log schema) is carried over.
Used (1) as the code generator in ``CODEGEN_MODE=compiler`` and (2) for the
deterministic, LLM-free reference pipeline in ``analysis/deterministic_baseline.py``.
"""
from __future__ import annotations

import json
import os
from typing import Any

from langchain_core.tools import tool

_DROP_SECTIONS = {"log_schema", "_provenance"}

ENGINE = r'''"""SimPy model compiled from the simulation spec by src/genai4simpy_agent/compiler.py.

Implements output contract v2. All parameters live in SPEC (generated, do not edit by hand).
"""
import json
import random

import numpy as np
import pandas as pd
import scipy.stats
import simpy

SPEC = json.loads(r"""__SPEC_JSON__""")

RESOURCE_CAPACITIES = {r["name"]: int(r.get("capacity", 1)) for r in SPEC["resources"]}
SIMULATION_TIME = float(SPEC.get("window", {}).get("horizon_s", 3600.0))
ARRIVAL_RATE_SCALE = 1.0
FAILURES_ENABLED = True
MAX_ATTEMPTS = 20

COLUMNS = ["case_id", "variant", "activity", "resource", "case_arrival", "queue_enter",
           "time:timestamp", "operation_end_time", "lifecycle:state"]


def make_sampler(dist, rng):
    """Spec distribution -> zero-argument sampler (never negative)."""
    fam, p = dist["family"], dist.get("params", {})
    if fam == "constant":
        return lambda: float(p["value"])
    if fam == "categorical":
        v, pr = np.asarray(dist["values"], float), np.asarray(dist["probs"], float)
        return lambda: float(rng.choice(v, p=pr / pr.sum()))
    if fam == "empirical_quantiles":
        q, pr = np.asarray(dist["quantiles"], float), np.asarray(dist["quantile_probs"], float)
        return lambda: float(np.interp(rng.uniform(), pr, q))
    d = getattr(scipy.stats, fam)(**p)
    return lambda: max(0.0, float(d.rvs(random_state=rng)))


def run_single_replication(seed):
    random.seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    log = []

    cls_of = {r["name"]: r.get("resource_class", r["name"]) for r in SPEC["resources"]}
    cp = SPEC.get("control_policies", {}) or {}
    disc, prio = cp.get("queue_discipline", {}) or {}, cp.get("priority_order", {}) or {}
    res = {}
    for name, cap in RESOURCE_CAPACITIES.items():
        if disc.get(cls_of.get(name, name)) == "priority":
            res[name] = simpy.PriorityResource(env, capacity=int(cap))
        else:
            res[name] = simpy.Resource(env, capacity=int(cap))

    acts = {a["name"]: a for a in SPEC["activities"]}
    dur = {n: make_sampler(a["duration"], rng) for n, a in acts.items()}
    variants = SPEC["variants"]
    vprob = np.array([max(v.get("probability", 0.0), 0.0) for v in variants], float)
    vprob = vprob / vprob.sum() if vprob.sum() > 0 else np.full(len(variants), 1 / len(variants))

    def priority_of(resource, activity):
        order = prio.get(cls_of.get(resource, resource), [])
        return order.index(activity) if activity in order else len(order)

    def pick_resource(step, act):
        shares = {r: w for r, w in (step.get("resources") or {}).items() if r in res and w > 0}
        if shares:
            names = list(shares)
            w = np.array([shares[n] for n in names], float)
            return names[int(rng.choice(len(names), p=w / w.sum()))]
        elig = [r for r in act.get("eligible_resources", []) if r in res] or list(res)
        return min(elig, key=lambda r: (res[r].count + len(res[r].queue), rng.uniform()))

    def do_step(case, step):
        act = acts[step["activity"]]
        p_fail = float(act.get("failure_probability", 0.0)) if FAILURES_ENABLED else 0.0
        for _ in range(MAX_ATTEMPTS):
            r = pick_resource(step, act)
            q = env.now
            req = (res[r].request(priority=priority_of(r, act["name"]))
                   if isinstance(res[r], simpy.PriorityResource) else res[r].request())
            with req:
                yield req
                s = env.now
                yield env.timeout(dur[act["name"]]())
                e = env.now
            failed = rng.uniform() < p_fail
            log.append((case["id"], case["variant"], act["name"], r, case["arrival"], q, s, e,
                        "failure" if failed else "success"))
            if not failed:
                return True
            if act.get("on_failure", "retry") != "retry":
                return False
        return False

    def case_process(case, v, start_index=0):
        steps = v["steps"]
        exit_after = None
        if rng.uniform() < float(v.get("early_exit_probability", 0.0)):
            opts = v.get("early_exit_after_n_steps") or {}
            if opts:
                ks = list(opts)
                w = np.array([opts[k] for k in ks], float)
                exit_after = int(ks[int(rng.choice(len(ks), p=w / w.sum()))])
        background, done = [], 0
        for i in range(start_index, len(steps)):
            step = steps[i]
            if exit_after is not None and done >= exit_after:
                return
            if float(step.get("probability", 1.0)) < 1.0 and rng.uniform() > float(step["probability"]):
                continue
            if i == len(steps) - 1 and background:
                yield simpy.AllOf(env, background)
            nxt_concurrent = i + 1 < len(steps) and steps[i + 1].get("concurrent_with_previous", False)
            if nxt_concurrent:
                background.append(env.process(do_step(case, step)))
                ok = True
            else:
                ok = yield env.process(do_step(case, step))
            if not ok:
                return
            done += 1

    counter = [0]

    def gated(case, v, start_index):
        with wip_gate.request() as token:
            yield token
            case["arrival"] = env.now
            yield env.process(case_process(case, v, start_index))

    def release(v=None, start_index=0):
        if v is None:
            v = variants[int(rng.choice(len(variants), p=vprob))]
        counter[0] += 1
        case = {"id": f"case_{counter[0]}", "variant": v["name"], "arrival": env.now}
        env.process(gated(case, v, start_index) if wip_gate is not None else case_process(case, v, start_index))

    arr = SPEC.get("arrivals", {}) or {}
    model = arr.get("model", "renewal")

    wip_gate = (simpy.Resource(env, capacity=int(arr["wip_cap"]))
                if model == "wip_controlled" and arr.get("wip_cap") else None)

    def arrivals():
        scale = float(ARRIVAL_RATE_SCALE)
        if arr.get("initial_burst"):
            k0 = max(1, int(round(make_sampler(arr["initial_burst"], rng)())))
            gap0 = make_sampler(arr["intra_burst_iat"], rng) if arr.get("intra_burst_iat") else (lambda: 1.0)
            for j in range(k0):
                release()
                yield env.timeout(gap0() / scale)
        if model in ("two_regime_bursts", "batch"):
            size, gap = make_sampler(arr["burst_size"], rng), make_sampler(arr["inter_burst_gap"], rng)
            intra = make_sampler(arr["intra_burst_iat"], rng) if arr.get("intra_burst_iat") else (lambda: 0.0)
            while True:
                k = max(1, int(round(size())))
                for j in range(k):
                    release()
                    if j < k - 1:
                        yield env.timeout(intra() / scale)
                yield env.timeout(gap() / scale)
        else:
            iat = make_sampler(arr["interarrival"], rng)
            while True:
                release()
                yield env.timeout(iat() / scale)

    # initial work in progress (no observed case ids are used)
    for c in (SPEC.get("initial_state", {}) or {}).get("cases_in_progress", []):
        v = next((x for x in variants if x["name"] == c.get("variant")), None)
        if v is None:
            continue
        idx = next((i for i, s in enumerate(v["steps"]) if s["activity"] == c.get("current_activity")), 0)
        release(v, idx)

    env.process(arrivals())
    env.run(until=SIMULATION_TIME)
    return pd.DataFrame(log, columns=COLUMNS)


if __name__ == "__main__":
    df = run_single_replication(1)
    print(df.groupby("activity").size().to_string())
    print("cases:", df["case_id"].nunique(), "rows:", len(df))
'''


def compile_spec(spec: dict[str, Any]) -> str:
    """Return the source of a contract-v2 SimPy model implementing ``spec``."""
    missing = [s for s in ("resources", "activities", "variants", "arrivals") if s not in spec]
    if missing:
        raise ValueError(f"spec incomplete, missing sections: {missing}")
    data = {k: v for k, v in spec.items() if k not in _DROP_SECTIONS}
    if "initial_state" in data:
        data["initial_state"] = {k: v for k, v in data["initial_state"].items() if k != "excluded_from_estimation"}
    js = json.dumps(data, indent=1, default=str)
    if '"""' in js:
        raise ValueError("spec contains a triple quote")
    return ENGINE.replace("__SPEC_JSON__", js)


def make_compile_tool(spec_provider, sim_dir: str):
    """Tool: compile the current spec into simulation.py (CODEGEN_MODE=compiler)."""
    path = os.path.join(os.getcwd(), sim_dir, "simulation.py")

    @tool(description=(
        "Compile the current simulation spec into simulation.py with the deterministic SimPy "
        "compiler (generic engine + embedded spec; satisfies output contract v2). Re-run it "
        "after the spec changes. Returns the path or the reason the spec cannot be compiled."
    ))
    def compile_spec_to_simulation() -> str:
        try:
            src = compile_spec(spec_provider() or {})
        except Exception as exc:
            return f"Error: {exc}"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        return f"simulation.py compiled from the spec ({len(src.splitlines())} lines) at {path}"

    return compile_spec_to_simulation
