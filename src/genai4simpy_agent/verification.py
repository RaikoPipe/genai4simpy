"""Deterministic behavioural verification of generated SimPy models (proposal P5).

Three checks the evaluator agent calls as tools instead of judging code by eye:

* ``contract_test``      - output-contract v2 conformance (dynamic, in a subprocess)
                           plus static scans for trace replay and file I/O.
* ``behavioural_check``  - simulated vs. observed behaviour on the TRAINING log
                           (the same log the pipeline sees), with evaluate_v2 KPI
                           definitions, prediction intervals and BPS distances.
* ``metamorphic_tests``  - oracle-free relations (more capacity must not hurt,
                           more arrivals must not shrink WIP, ...).

All model execution happens in a child process (``sys.executable``) with a hard
timeout, so a hanging or crashing model cannot block the agent.
"""
from __future__ import annotations

import ast
import json
import os
import pickle
import subprocess
import sys
import tempfile
from collections import Counter
import warnings
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy import stats

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import evaluate_v2 as ev  # noqa: E402
from src.data_extraction_tools.eventlog import LogSchema, build_instances, resource_class  # noqa: E402

REQUIRED_COLUMNS = ["case_id", "variant", "activity", "resource", "time:timestamp",
                    "operation_end_time", "lifecycle:state"]
V2_COLUMNS = ["case_arrival", "queue_enter"]
REQUIRED_SYMBOLS = ["run_single_replication", "RESOURCE_CAPACITIES", "SIMULATION_TIME"]
V2_SYMBOLS = ["ARRIVAL_RATE_SCALE", "FAILURES_ENABLED"]
RUNTIME_KNOBS = ["RESOURCE_CAPACITIES", "ARRIVAL_RATE_SCALE", "FAILURES_ENABLED", "SIMULATION_TIME"]
_IO_CALLS = {"open", "read_csv", "read_parquet", "read_excel", "read_json", "read_pickle", "read_table",
             "load", "loadtxt", "genfromtxt", "fromfile", "to_csv", "to_parquet", "to_excel", "to_json",
             "to_pickle", "savetxt", "save", "dump"}


# =============================================================================
# Child-process runner
# =============================================================================

_DRIVER = r'''
import contextlib, importlib.util, io, json, pickle, random, sys, time, traceback
sys.dont_write_bytecode = True
args = json.load(open(sys.argv[1]))
sys.path.insert(0, args["cwd"])
out = {"import": {}, "runs": [], "attrs": {}}
# Load the heavy libraries first so the import timing measures the model's own work only.
for _lib in ("numpy", "pandas", "scipy.stats", "simpy"):
    try:
        __import__(_lib)
    except Exception:
        pass
buf = io.StringIO(); t = time.perf_counter()
try:
    spec = importlib.util.spec_from_file_location("generated_sim_model", args["path"])
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(buf):
        spec.loader.exec_module(mod)
except BaseException as e:
    out["import"] = {"ok": False, "error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-1500:]}
    pickle.dump(out, open(args["out"], "wb")); sys.exit(0)
out["import"] = {"ok": True, "seconds": time.perf_counter() - t, "stdout_chars": len(buf.getvalue())}
for name in ["run_single_replication", "RESOURCE_CAPACITIES", "SIMULATION_TIME", "ARRIVAL_RATE_SCALE", "FAILURES_ENABLED"]:
    out["attrs"][name] = hasattr(mod, name)
caps = getattr(mod, "RESOURCE_CAPACITIES", None)
out["capacities"] = {str(k): v for k, v in caps.items()} if isinstance(caps, dict) else None
out["simulation_time"] = getattr(mod, "SIMULATION_TIME", None)

# ---- patches (harness overrides and seeded mutations)
p = args.get("patch") or {}
for k, v in (p.get("attrs") or {}).items():
    setattr(mod, k, v)
if p.get("capacity") and isinstance(caps, dict):
    for k, v in p["capacity"].items():
        caps[k] = v
if p.get("exec"):
    exec(p["exec"], {"mod": mod})
ts = p.get("timeout_scale")
if ts:
    import simpy.events as _se
    _orig = _se.Timeout.__init__
    def _init(self, env, delay, value=None):
        act = sys._getframe(1).f_locals.get("activity")
        f = ts.get("activity", {}).get(act, 1.0) if act is not None else ts.get("arrival", 1.0)
        return _orig(self, env, delay * f, value)
    _se.Timeout.__init__ = _init

if args.get("T") is not None:
    mod.SIMULATION_TIME = args["T"]
for seed in args["seeds"]:
    rec = {"seed": seed}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            t = time.perf_counter(); r = mod.run_single_replication(seed); rec["seconds"] = time.perf_counter() - t
        df = r[0] if isinstance(r, tuple) else r
        import pandas as pd
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        rec["df"] = df
    except BaseException as e:
        rec["error"] = f"{type(e).__name__}: {e}"; rec["tb"] = traceback.format_exc()[-1500:]
    out["runs"].append(rec)
pickle.dump(out, open(args["out"], "wb"))
'''


def _run_model(sim_path: str, seeds: list[int], T: float | None = None, patch: dict | None = None,
               timeout: float = 600) -> dict:
    """Import ``sim_path`` in a child process, run the given seeds and return frames + metadata."""
    with tempfile.TemporaryDirectory() as td:
        a, o = os.path.join(td, "args.json"), os.path.join(td, "out.pkl")
        json.dump({"path": os.path.abspath(sim_path), "seeds": seeds, "T": T, "patch": patch,
                   "cwd": _REPO_ROOT, "out": o}, open(a, "w"))
        try:
            pr = subprocess.run([sys.executable, "-c", _DRIVER, a], cwd=_REPO_ROOT, capture_output=True,
                                text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"fatal": f"model run exceeded {timeout:.0f} s (hanging model or too many replications)"}
        if not os.path.exists(o):
            return {"fatal": f"model process crashed (exit {pr.returncode}): {(pr.stderr or '')[-800:]}"}
        return pickle.load(open(o, "rb"))


# =============================================================================
# Helpers
# =============================================================================

def _names(spec: dict | None, key: str) -> set[str] | None:
    """Defensively read a name vocabulary from a spec section (list of dicts, dict, or list of str)."""
    if not spec:
        return None
    sec = spec.get(key)
    if not sec:
        return None
    if isinstance(sec, dict):
        return {str(k) for k in sec}
    names = set()
    for it in sec:
        if isinstance(it, dict):
            n = it.get("name") or it.get("activity") or it.get("variant") or it.get("id")
            if n is not None:
                names.add(str(n))
        else:
            names.add(str(it))
    return names or None


def _spec_capacities(spec: dict | None) -> dict[str, int]:
    sec = (spec or {}).get("resources")
    caps = {}
    if isinstance(sec, dict):
        for k, v in sec.items():
            c = v.get("capacity") if isinstance(v, dict) else v
            if isinstance(c, (int, float)):
                caps[str(k)] = int(c)
    elif isinstance(sec, list):
        for it in sec:
            if isinstance(it, dict) and it.get("name") is not None and isinstance(it.get("capacity"), (int, float)):
                caps[str(it["name"])] = int(it["capacity"])
    return caps


def terminal_from_spec(spec: dict | None) -> str | None:
    if not spec:
        return None
    for k in ("terminal_activity",):
        if isinstance(spec.get(k), str):
            return spec[k]
    for sec in ("window", "control_policies", "routing", "process", "case_completion"):
        s = spec.get(sec)
        if isinstance(s, dict) and isinstance(s.get("terminal_activity"), str):
            return s["terminal_activity"]
    return None


def _strip_main(tree: ast.Module) -> list[ast.stmt]:
    """Module body without ``if __name__ == "__main__":`` blocks."""
    body = []
    for n in tree.body:
        if isinstance(n, ast.If) and "__main__" in ast.unparse(n.test):
            continue
        body.append(n)
    return body


def static_scan(source: str, observed_case_ids: set[str] | None = None) -> list[dict]:
    """Static checks: trace replay (literal observed case ids), file I/O, run-time knob use."""
    checks = []
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [{"name": "syntax", "passed": False, "detail": str(e)}]
    body = _strip_main(tree)
    nodes = [n for b in body for n in ast.walk(b)]

    lits = {n.value for n in nodes if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    hits = sorted(lits & set(observed_case_ids or ()))
    checks.append({"name": "no_trace_replay", "passed": not hits,
                   "detail": f"literal observed case ids in code: {hits[:5]}" if hits else "no observed case ids hard-coded"})

    io_hits = []
    for n in nodes:
        if isinstance(n, ast.Call):
            f = n.func
            name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if name in _IO_CALLS:
                io_hits.append(f"line {n.lineno}: {name}()")
    checks.append({"name": "no_file_io", "passed": not io_hits,
                   "detail": ("file I/O outside __main__: " + "; ".join(io_hits[:5])) if io_hits else "no file I/O outside __main__"})

    func_names = set()
    for n in nodes:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for m in ast.walk(n):
                if isinstance(m, ast.Name):
                    func_names.add(m.id)
    missing = [k for k in RUNTIME_KNOBS if k not in func_names]
    checks.append({"name": "knobs_read_at_runtime", "passed": not missing,
                   "detail": (f"never read inside a function (harness cannot override): {missing}") if missing
                   else "all knobs read inside functions"})
    return checks


def to_eval_log(df: pd.DataFrame) -> pd.DataFrame:
    """Simulated contract log -> evaluate_v2 columns (service_start etc.)."""
    d = df.copy()
    d["service_start"] = pd.to_numeric(d["time:timestamp"], errors="coerce")
    d["operation_end_time"] = pd.to_numeric(d["operation_end_time"], errors="coerce")
    for c in V2_COLUMNS:
        d[c] = pd.to_numeric(d[c], errors="coerce") if c in d else np.nan
    d["case_id"] = d["case_id"].astype(str)
    d["resource"] = d["resource"].astype(str)
    return d


def instances_to_eval_log(inst: pd.DataFrame) -> pd.DataFrame:
    """Observed activity instances -> evaluate_v2 columns."""
    d = pd.DataFrame({
        "case_id": inst["case_id"].astype(str), "variant": inst["variant"], "activity": inst["activity"],
        "resource": inst["resource"].astype(str), "step_release": inst["enabled"], "queue_enter": inst["enabled"],
        "service_start": inst["start"], "time:timestamp": inst["start"], "operation_end_time": inst["end"],
        "lifecycle:state": inst["state"]})
    d = d.dropna(subset=["operation_end_time"])
    d["case_arrival"] = d.groupby("case_id")["step_release"].transform("min")
    return d.reset_index(drop=True)


def infer_terminal(inst: pd.DataFrame) -> str:
    """Activity that most often closes a case AND rarely occurs mid-case.

    Plain "most frequent last activity" is fooled by cases truncated at the
    window end (they end on whatever step was running), so each activity's
    last-count is weighted by the share of its occurrences that are last.
    """
    s = inst[inst["state"] == "success"].sort_values("start")
    last = s.groupby("case_id")["activity"].last().value_counts()
    occ = s["activity"].value_counts()
    frac = (last / occ.reindex(last.index)).fillna(0)
    closing = last[frac >= 0.8]          # activities that (almost) only occur as the final step
    if len(closing):
        return str(closing.idxmax())
    return str((last * frac).idxmax())


def _waiting_by_class(L: pd.DataFrame, T: float) -> dict[str, float]:
    L = L[L["operation_end_time"] <= T + 1e-9]
    if "queue_enter" not in L or L["queue_enter"].isna().all():
        return {}
    w = (L["service_start"] - L["queue_enter"]).clip(lower=0)
    return w.groupby(resource_class(L["resource"])).mean().dropna().to_dict()


def _first_starts(L: pd.DataFrame, T: float) -> np.ndarray:
    L = L[L["service_start"] <= T + 1e-9]
    arr = L.groupby("case_id")["case_arrival"].min() if L["case_arrival"].notna().any() else pd.Series(dtype=float)
    fs = L.groupby("case_id")["service_start"].min()
    if len(arr) and arr.notna().all():
        fs = arr
    return np.sort(fs.to_numpy(float))


def _flow_times(L: pd.DataFrame, T: float, terminal: str) -> np.ndarray:
    L = L[L["operation_end_time"] <= T + 1e-9]
    done = L.loc[(L["activity"] == terminal) & (L["lifecycle:state"] == "success"), "case_id"].unique()
    c = L[L["case_id"].isin(done)].groupby("case_id")
    return (c["operation_end_time"].max() - c["service_start"].min()).to_numpy(float)


def _bigrams(L: pd.DataFrame, T: float) -> Counter:
    L = L[L["operation_end_time"] <= T + 1e-9].sort_values(["case_id", "service_start"])
    cnt = Counter()
    for _, acts in L.groupby("case_id")["activity"]:
        a = ["<s>"] + list(acts)
        cnt.update(zip(a[:-1], a[1:]))
    return cnt


def _mean_wip(L: pd.DataFrame, T: float) -> float:
    c = L.groupby("case_id").agg(a=("service_start", "min"), z=("operation_end_time", "max"))
    if "case_arrival" in L and L["case_arrival"].notna().any():
        c["a"] = L.groupby("case_id")["case_arrival"].min().fillna(c["a"])
    return float((c["z"].clip(upper=T) - c["a"].clip(lower=0, upper=T)).clip(lower=0).sum() / T) if T > 0 else np.nan


def _r(x, nd=3):
    if isinstance(x, (float, np.floating)):
        return None if not np.isfinite(x) else round(float(x), nd)
    if isinstance(x, dict):
        return {k: _r(v, nd) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_r(v, nd) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


# =============================================================================
# 1. Contract test
# =============================================================================

def contract_test(sim_path: str, spec: dict | None = None, observed_case_ids: set[str] | None = None,
                  timeout: float = 300) -> dict:
    """Output-contract v2 conformance of ``sim_path`` (dynamic + static)."""
    checks: list[dict] = []
    add = lambda n, ok, d: checks.append({"name": n, "passed": bool(ok), "detail": d})
    if not os.path.exists(sim_path):
        return {"passed": False, "checks": [{"name": "file_exists", "passed": False, "detail": f"{sim_path} missing"}]}
    src = open(sim_path, encoding="utf-8").read()
    checks += static_scan(src, observed_case_ids)

    res = _run_model(sim_path, [1, 1, 2], timeout=timeout)
    if "fatal" in res:
        add("executes", False, res["fatal"])
        return {"passed": False, "checks": checks}
    imp = res["import"]
    if not imp.get("ok"):
        add("importable", False, imp.get("error", "") + "\n" + imp.get("tb", "")[-600:])
        return {"passed": False, "checks": checks}
    add("import_is_side_effect_free", imp["seconds"] < 5 and imp["stdout_chars"] == 0,
        f"import took {imp['seconds']:.2f}s, printed {imp['stdout_chars']} chars (must be ~0: guard demo code with __main__)")
    for s in REQUIRED_SYMBOLS:
        add(f"symbol:{s}", res["attrs"].get(s), "present" if res["attrs"].get(s) else "MISSING")
    for s in V2_SYMBOLS:
        add(f"symbol:{s}", res["attrs"].get(s), "present" if res["attrs"].get(s) else "MISSING (contract v2 knob)")
    caps = res.get("capacities")
    add("capacities_concrete_ints", isinstance(caps, dict) and caps and all(isinstance(v, int) and v >= 1 for v in caps.values()),
        f"{len(caps or {})} resources" if caps else "RESOURCE_CAPACITIES missing or not a dict")

    runs = res["runs"]
    errs = [r for r in runs if "error" in r]
    if errs:
        add("run_single_replication_runs", False, errs[0]["error"] + "\n" + errs[0].get("tb", "")[-800:])
        return {"passed": False, "checks": checks}
    d1, d1b, d2 = (r["df"] for r in runs)
    add("run_single_replication_runs", True, f"{len(d1)} rows, {runs[0]['seconds']:.2f}s per replication")
    add("non_empty", len(d1) > 0, f"{len(d1)} rows")
    miss = [c for c in REQUIRED_COLUMNS if c not in d1]
    add("required_columns", not miss, f"missing {miss}" if miss else "all present")
    miss2 = [c for c in V2_COLUMNS if c not in d1]
    add("v2_columns", not miss2, f"missing {miss2} (contract v2: case_arrival, queue_enter)" if miss2 else "present")
    if miss or len(d1) == 0:
        return {"passed": False, "checks": checks}

    num = {c: pd.to_numeric(d1[c], errors="coerce") for c in ["time:timestamp", "operation_end_time"] + [c for c in V2_COLUMNS if c in d1]}
    nonnum = [c for c, s in num.items() if s.isna().all() or (s.isna() & d1[c].notna()).any()]
    add("numeric_times", not nonnum, f"non-numeric: {nonnum}" if nonnum else "numeric seconds")
    bad_end = int((num["operation_end_time"] < num["time:timestamp"] - 1e-9).sum())
    add("end_ge_start", bad_end == 0, f"{bad_end} rows with operation_end_time < time:timestamp")
    if "queue_enter" in num:
        bad_q = int((num["queue_enter"] > num["time:timestamp"] + 1e-9).sum())
        add("queue_enter_le_start", bad_q == 0, f"{bad_q} rows with queue_enter > service start")
    if "case_arrival" in num:
        g = pd.DataFrame({"c": d1["case_id"], "a": num["case_arrival"], "s": num["time:timestamp"]}).groupby("c")
        bad_a = int((g["a"].min() > g["s"].min() + 1e-9).sum())
        add("case_arrival_le_first_start", bad_a == 0, f"{bad_a} cases released after their first start")
    states = set(d1["lifecycle:state"].astype(str))
    add("states_valid", states <= {"success", "failure"}, f"states {sorted(states)}")
    try:
        same = d1.reset_index(drop=True).equals(d1b.reset_index(drop=True))
    except Exception:
        same = False
    add("same_seed_reproducible", same, "seed 1 twice -> identical" if same else "seed 1 twice -> DIFFERENT logs (seed random AND np.random inside run_single_replication)")
    try:
        differ = not d1.reset_index(drop=True).equals(d2.reset_index(drop=True))
    except Exception:
        differ = True
    add("different_seeds_differ", differ, "seeds 1/2 differ" if differ else "seeds 1 and 2 give identical logs")
    if isinstance(caps, dict):
        unk = sorted(set(d1["resource"].astype(str)) - set(caps))
        add("resources_in_capacities", not unk, f"resources not in RESOURCE_CAPACITIES: {unk[:8]}" if unk else "ok")

    for key, col in (("activities", "activity"), ("variants", "variant")):
        voc = _names(spec, key)
        if voc:
            bad = sorted(set(d1[col].astype(str)) - voc)
            add(f"vocabulary:{col}", not bad, f"not in spec {key}: {bad[:8]}" if bad else "matches spec")
            unused = sorted(voc - set(d1[col].astype(str)))
            if unused and key == "activities":
                checks.append({"name": "spec_activities_emitted", "passed": True,
                               "detail": f"warning: spec activities never emitted in seed 1: {unused[:8]}"})
    scap = _spec_capacities(spec)
    if scap and isinstance(caps, dict):
        diff = {k: (caps.get(k), v) for k, v in scap.items() if k in caps and caps[k] != v}
        extra = sorted(set(caps) - set(scap))
        add("capacities_match_spec", not diff and not extra,
            (f"capacity (model, spec) differs: {diff}; " if diff else "") + (f"resources not in spec: {extra[:8]}" if extra else "") or "match")
    return {"passed": all(c["passed"] for c in checks), "checks": checks}


# =============================================================================
# 2. Behavioural check against the training log
# =============================================================================

KEY_KPIS = ["completed_cases", "cases_entered", "wip_at_T", "flow_time_completed_s", "time_in_system_all_s",
            "failure_rate", "overlapping_steps_per_case", "idle_s"]
ERROR_KPIS = ["activity_mape", "activity_coverage", "variant_jsd", "utilization_mae_pp"]


def ground_truth(block_df: pd.DataFrame, schema: LogSchema | dict, terminal_activity: str | None = None):
    inst, meta = build_instances(block_df, schema)
    G = instances_to_eval_log(inst)
    T = float(meta["T"])
    term = terminal_activity or infer_terminal(inst)
    gt = ev.kpis(G, T, terminal=term)
    gt = ev.kpis(G, T, ref=gt, terminal=term)
    return G, T, term, gt


HEADLINE_KPIS = ("completed_cases", "flow_time_completed_s", "time_in_system_all_s", "overlapping_steps_per_case")


def behavioural_verdict(summary: dict, pass_tol: float = 20.0, fail_tol: float = 50.0) -> dict:
    """Deterministic verdict on the headline KPIs: PASS if every |bias| <= pass_tol %, FAIL if any
    > fail_tol %, else PARTIAL. A wide prediction interval alone is not enough to pass."""
    biases = {k: summary[k].get("bias_pct") for k in HEADLINE_KPIS
              if k in summary and summary[k].get("bias_pct") is not None and np.isfinite(summary[k]["bias_pct"])}
    worst = max((abs(b) for b in biases.values()), default=float("nan"))
    status = ("PASS" if worst <= pass_tol else "FAIL" if worst > fail_tol else "PARTIAL") if biases else "UNKNOWN"
    return {"status": status, "rule": f"PASS if all |bias| <= {pass_tol:g}% on {list(HEADLINE_KPIS)}, "
                                      f"FAIL if any > {fail_tol:g}%",
            "bias_pct": {k: round(float(v), 1) for k, v in biases.items()}}


def behavioural_check(sim_path: str, block_df: pd.DataFrame, schema: LogSchema | dict,
                      terminal_activity: str | None = None, m: int = 30, seed: int = 42,
                      timeout: float = 900, patch: dict | None = None, _gt=None) -> dict:
    """Score ``sim_path`` against the observed (training) log with evaluate_v2 definitions."""
    G, T, term, gt = _gt or ground_truth(block_df, schema, terminal_activity)
    res = _run_model(sim_path, list(range(seed, seed + m)), T=T, patch=patch, timeout=timeout)
    if "fatal" in res:
        return {"ok": False, "error": res["fatal"]}
    if not res["import"].get("ok"):
        return {"ok": False, "error": "import failed: " + res["import"].get("error", "")}
    frames, errors = [], []
    for r in res["runs"]:
        if "error" in r:
            errors.append(r["error"])
            continue
        try:
            frames.append(to_eval_log(r["df"]))
        except Exception as e:
            errors.append(f"{type(e).__name__}: {e}")
    if not frames:
        return {"ok": False, "error": f"all replications failed: {errors[:2]}"}

    reps, waits, spacing, flows, arrivals, bigr, wips = [], [], [], [], [], Counter(), []
    for L in frames:
        try:
            reps.append(ev.kpis(L, T, ref=gt, terminal=term))
        except Exception as e:
            errors.append(f"kpi: {type(e).__name__}: {e}")
            continue
        waits.append(_waiting_by_class(L, T))
        fs = _first_starts(L, T)
        spacing.append(float(np.median(np.diff(fs))) if len(fs) > 2 else np.nan)
        flows.append(_flow_times(L, T, term))
        arrivals.append(fs)
        bigr.update(_bigrams(L, T))
        wips.append(_mean_wip(L, T))
    if not reps:
        return {"ok": False, "error": f"KPI computation failed: {errors[:2]}"}

    summary = {}
    for k in KEY_KPIS + ERROR_KPIS:
        vals = [r.get(k, np.nan) for r in reps]
        summary[k] = ev.summarize(vals, None if k in ERROR_KPIS else gt.get(k))
    summary["mean_wip"] = ev.summarize(wips, _mean_wip(G, T))

    gt_wait = _waiting_by_class(G, T)
    sim_wait = pd.DataFrame(waits).mean().to_dict() if any(waits) else {}
    gt_fs = _first_starts(G, T)
    gt_spacing = float(np.median(np.diff(gt_fs))) if len(gt_fs) > 2 else np.nan
    sim_spacing = float(np.nanmean(spacing)) if np.isfinite(spacing).any() else np.nan
    gt_idle = gt.get("idle_by_resource_class_s", {})
    sim_idle = pd.DataFrame([r.get("idle_by_resource_class_s", {}) for r in reps]).mean().to_dict()
    gt_util = gt.get("utilization", {})
    sim_util = pd.DataFrame([r.get("utilization", {}) for r in reps]).mean().to_dict()

    pooled_flow = np.concatenate([f for f in flows if len(f)]) if any(len(f) for f in flows) else np.array([])
    gt_flow = _flow_times(G, T, term)
    pooled_arr = np.concatenate(arrivals) if arrivals else np.array([])
    gt_bi = _bigrams(G, T)
    lab = set(gt_bi) | set(bigr)
    ngram = ev.jsd({str(k): bigr.get(k, 0) + 1e-12 for k in lab}, {str(k): gt_bi.get(k, 0) + 1e-12 for k in lab}) if lab else np.nan
    distances = {
        "cycle_time_emd_s": float(stats.wasserstein_distance(pooled_flow, gt_flow)) if len(pooled_flow) and len(gt_flow) else np.nan,
        "arrival_emd_s": float(stats.wasserstein_distance(pooled_arr, gt_fs)) if len(pooled_arr) and len(gt_fs) else np.nan,
        "bigram_jsd": ngram,
    }

    findings = []
    for k in KEY_KPIS + ["mean_wip"]:
        s = summary[k]
        if s.get("n") and "gt" in s and not s.get("pi_covered", True):
            findings.append(f"{k}: sim mean {s['mean']:.3g} vs observed {s['gt']:.3g} (bias {s['bias_pct']:+.0f}%), "
                            f"observed value outside the 95% PI [{s['pi_lo']:.3g}, {s['pi_hi']:.3g}]")
    if summary["activity_coverage"].get("mean", 1) < 1:
        sim_acts = set().union(*[set(r["activity_means"]) for r in reps])
        missing = sorted(set(gt["activity_means"]) - sim_acts)
        if missing:
            findings.append(f"activities never simulated: {missing[:8]}")
        else:
            findings.append(f"activity coverage {summary['activity_coverage']['mean']:.2f}: some observed activities "
                            "are missing in some replications (rare branches)")
    if summary["activity_mape"].get("mean", 0) > 20:
        worst = sorted(((abs(np.nanmean([r["activity_means"].get(a, np.nan) for r in reps]) - g) / g * 100, a)
                        for a, g in gt["activity_means"].items() if g > 0 and any(a in r["activity_means"] for r in reps)),
                       reverse=True)[:3]
        findings.append(f"activity duration MAPE {summary['activity_mape']['mean']:.0f}%; worst: "
                        + ", ".join(f"{a} {e:.0f}%" for e, a in worst))
    if summary["variant_jsd"].get("mean", 0) > 0.05:
        findings.append(f"variant mix JSD {summary['variant_jsd']['mean']:.3f} > 0.05")
    if not sim_wait:
        findings.append("model log has no queue_enter column: waiting times cannot be verified (contract v2)")
    for c, g in gt_wait.items():
        s = sim_wait.get(c)
        if s is not None and abs(s - g) > 5 and (s < 0.5 * g or s > 2 * g):
            findings.append(f"mean waiting at {c}: sim {s:.0f} s vs observed {g:.0f} s")
    go, so = gt.get("overlapping_steps_per_case", 0) or 0, summary["overlapping_steps_per_case"].get("mean", 0) or 0
    if go > 0.3 and so < 0.5 * go:
        findings.append(f"observed {go:.1f} overlapping steps per case, sim {so:.1f}: model lacks intra-case parallelism")
    if np.isfinite(gt_spacing) and np.isfinite(sim_spacing) and abs(sim_spacing - gt_spacing) > max(5, 0.5 * gt_spacing):
        findings.append(f"median case release spacing: sim {sim_spacing:.0f} s vs observed {gt_spacing:.0f} s")
    for c, g in gt_idle.items():
        s = sim_idle.get(c, 0.0)
        if abs(s - g) > 30 and (s < 0.5 * g or s > 2 * g):
            findings.append(f"idle/wait time per completed case before {c} steps: sim {s:.0f} s vs observed {g:.0f} s")
    util_dev = sorted(((abs(sim_util.get(r, 0) - u) * 100, r) for r, u in gt_util.items()), reverse=True)[:3]
    if util_dev and util_dev[0][0] > 10:
        findings.append("largest utilisation deviations (pp): " + ", ".join(f"{r} {d:.0f}" for d, r in util_dev))
    if errors:
        findings.append(f"{len(errors)} replications failed, e.g. {errors[0][:200]}")

    kp = {k: _r({x: v for x, v in summary[k].items() if x in ("gt", "mean", "pi_lo", "pi_hi", "bias_pct", "pi_covered")})
          for k in summary}
    verdict = behavioural_verdict(summary)
    return {
        "ok": True, "replications": len(reps), "T_s": round(T, 1), "terminal_activity": term,
        "verdict": verdict,
        "kpis": kp,
        "waiting_by_class_s": {c: {"observed": _r(g, 1), "sim": _r(sim_wait.get(c, np.nan), 1)} for c, g in gt_wait.items()},
        "idle_by_class_s": {c: {"observed": _r(g, 1), "sim": _r(sim_idle.get(c, 0.0), 1)} for c, g in gt_idle.items()},
        "release_spacing_median_s": {"observed": _r(gt_spacing, 1), "sim": _r(sim_spacing, 1)},
        "utilization": {r: {"observed": _r(u), "sim": _r(sim_util.get(r, 0.0))} for r, u in gt_util.items()},
        "distances": _r(distances),
        "findings": findings,
    }


# =============================================================================
# 3. Metamorphic tests
# =============================================================================

def _scen(sim_path, seeds, T, patch, timeout):
    res = _run_model(sim_path, seeds, T=T, patch=patch, timeout=timeout)
    if "fatal" in res or not res["import"].get("ok"):
        return None, res
    out = []
    for r in res["runs"]:
        if "error" in r:
            return None, {"fatal": r["error"]}
        L = to_eval_log(r["df"])
        Lt = L[L["operation_end_time"] <= T + 1e-9]
        has_q = "queue_enter" in Lt and Lt["queue_enter"].notna().any()
        fl = Lt.groupby("case_id").agg(a=("service_start", "min"), z=("operation_end_time", "max"))
        util = (Lt["operation_end_time"] - Lt["service_start"]).groupby(Lt["resource"]).sum() / T
        out.append({"cases_entered": L.loc[L["service_start"] <= T, "case_id"].nunique(),
                    "wait": float((Lt["service_start"] - Lt["queue_enter"]).clip(lower=0).mean()) if has_q else np.nan,
                    "flow": float((fl.z - fl.a).mean()) if len(fl) else np.nan,
                    "fail": float((Lt["lifecycle:state"] == "failure").mean()) if len(Lt) else 0.0,
                    "wip": _mean_wip(L, T), "util": util.to_dict()})
    return out, res


def metamorphic_tests(sim_path: str, m: int = 10, seed: int = 1000, T: float | None = None,
                      tol: float = 0.05, timeout: float = 900) -> dict:
    """Oracle-free metamorphic relations with common random numbers (same seeds for base and follow-up)."""
    seeds = list(range(seed, seed + m))
    probe = _run_model(sim_path, [], timeout=120)
    if "fatal" in probe or not probe["import"].get("ok"):
        return {"ok": False, "error": probe.get("fatal") or probe["import"].get("error")}
    attrs, caps = probe["attrs"], probe.get("capacities") or {}
    T = T or float(probe.get("simulation_time") or 3600)
    base, info = _scen(sim_path, seeds, T, None, timeout)
    if base is None:
        return {"ok": False, "error": f"base scenario failed: {info.get('fatal') or info.get('import')}"}
    def mean(rows, k):
        v = np.array([r[k] for r in rows], float)
        return float(np.nanmean(v)) if rows and np.isfinite(v).any() else np.nan
    B = {k: mean(base, k) for k in ("cases_entered", "wait", "flow", "fail", "wip")}
    rel = []

    def leq(a, b):  # a <= b within tolerance
        return not (np.isfinite(a) and np.isfinite(b)) or a <= b * (1 + tol) + 1e-6

    # MR1: +1 capacity at the bottleneck
    util = pd.DataFrame([r["util"] for r in base]).mean()
    if caps and len(util):
        bott = str(util.idxmax())
        if bott in caps:
            f, _ = _scen(sim_path, seeds, T, {"capacity": {bott: int(caps[bott]) + 1}}, timeout)
            if f is None:
                rel.append({"relation": "MR1 +1 capacity at bottleneck", "status": "error"})
            else:
                F = {k: mean(f, k) for k in ("wait", "flow")}
                ok = leq(F["wait"], B["wait"]) and leq(F["flow"], B["flow"])
                rel.append({"relation": f"MR1 +1 capacity at bottleneck {bott} (util {util.max():.2f}) must not increase waiting/flow time",
                            "status": "pass" if ok else "fail",
                            "base": _r({"wait": B["wait"], "flow": B["flow"]}, 1), "followup": _r(F, 1)})
        else:
            rel.append({"relation": "MR1 +1 capacity at bottleneck", "status": f"skip: bottleneck {bott} not a RESOURCE_CAPACITIES key"})
    else:
        rel.append({"relation": "MR1 +1 capacity at bottleneck", "status": "skip: RESOURCE_CAPACITIES missing"})

    # MR2: arrival rate x1.5
    if attrs.get("ARRIVAL_RATE_SCALE"):
        f, _ = _scen(sim_path, seeds, T, {"attrs": {"ARRIVAL_RATE_SCALE": 1.5}}, timeout)
        if f is None:
            rel.append({"relation": "MR2 arrival rate x1.5", "status": "error"})
        else:
            F = {k: mean(f, k) for k in ("cases_entered", "wip")}
            ok = F["cases_entered"] >= B["cases_entered"] * (1 - tol) and F["wip"] >= B["wip"] * (1 - tol)
            strict = F["cases_entered"] > B["cases_entered"]
            rel.append({"relation": "MR2 ARRIVAL_RATE_SCALE=1.5 must not decrease cases entered or mean WIP",
                        "status": ("pass" if strict else "warn: knob has no effect on cases entered") if ok else "fail",
                        "base": _r({"cases_entered": B["cases_entered"], "wip": B["wip"]}, 2), "followup": _r(F, 2)})
    else:
        rel.append({"relation": "MR2 arrival rate x1.5", "status": "skip: knob missing (contract v2 violation)"})

    # MR3: failures off
    if attrs.get("FAILURES_ENABLED"):
        f, _ = _scen(sim_path, seeds, T, {"attrs": {"FAILURES_ENABLED": False}}, timeout)
        if f is None:
            rel.append({"relation": "MR3 failures disabled", "status": "error"})
        else:
            F = {k: mean(f, k) for k in ("fail", "flow")}
            ok = F["fail"] == 0 and leq(F["flow"], B["flow"])
            rel.append({"relation": "MR3 FAILURES_ENABLED=False -> failure rate 0, flow time not increased",
                        "status": "pass" if ok else "fail",
                        "base": _r({"fail": B["fail"], "flow": B["flow"]}, 3), "followup": _r(F, 3)})
    else:
        rel.append({"relation": "MR3 failures disabled", "status": "skip: knob missing (contract v2 violation)"})

    # MR4: horizon doubled
    f, _ = _scen(sim_path, seeds, 2 * T, None, timeout)
    if f is None:
        rel.append({"relation": "MR4 horizon x2", "status": "error"})
    else:
        ce = mean(f, "cases_entered")
        ok = ce >= 1.5 * B["cases_entered"]
        rel.append({"relation": "MR4 SIMULATION_TIME x2 -> cases entered roughly scales (>=1.5x)",
                    "status": "pass" if ok else "warn: arrivals do not scale with horizon (finite arrival schedule / trace replay?)",
                    "base": _r(B["cases_entered"], 1), "followup": _r(ce, 1)})
    return {"ok": True, "replications": m, "T_s": T,
            "passed": all(not r["status"].startswith(("fail", "error")) for r in rel), "relations": rel}


# =============================================================================
# 4. Tool factories
# =============================================================================

def _compact_contract(r: dict) -> dict:
    failed = [f"{c['name']}: {c['detail']}" for c in r["checks"] if not c["passed"]]
    warns = [c["detail"] for c in r["checks"] if c["passed"] and str(c["detail"]).startswith("warning")]
    return {"passed": r["passed"], "n_checks": len(r["checks"]), "failed": failed, "warnings": warns}


def make_verification_tools(sim_dir: str, df: pd.DataFrame, schema_provider: Callable[[], dict | None],
                            spec_provider: Callable[[], dict | None], evidence_dir: str) -> list:
    """Return [run_contract_test, run_behavioural_check, run_metamorphic_tests] bound to this run."""
    from langchain_core.tools import tool

    sim_path = os.path.join(os.getcwd(), sim_dir, "simulation.py")
    ev_dir = os.path.join(os.getcwd(), evidence_dir)

    def _persist(name: str, obj: dict) -> str:
        os.makedirs(ev_dir, exist_ok=True)
        p = os.path.join(ev_dir, f"{name}.json")
        with open(p, "w") as f:
            json.dump(obj, f, indent=2, default=lambda o: _r(o) if not isinstance(o, (set, pd.Timestamp)) else str(o))
        return os.path.relpath(p, os.getcwd())

    def _schema():
        s = schema_provider()
        if not s:
            raise ValueError("No log schema in the simulation spec yet (section 'log_schema').")
        return s

    def _case_ids() -> set[str]:
        try:
            return set(df[_schema()["case_col"]].dropna().astype(str))
        except Exception:
            return set()

    @tool
    def run_contract_test() -> dict:
        """Run the deterministic OUTPUT CONTRACT v2 test on simulation.py.

        Imports the model in a separate process, runs run_single_replication with
        seeds 1, 1, 2 and checks: importable without side effects; required symbols
        (incl. ARRIVAL_RATE_SCALE, FAILURES_ENABLED); event-log columns incl.
        case_arrival and queue_enter; numeric times; end >= start; reproducibility
        per seed; resources in RESOURCE_CAPACITIES; activity/variant vocabulary and
        capacities against the simulation spec; and static scans for hard-coded
        observed case ids (trace replay), file I/O and knobs not read at run time.
        Returns only the failed checks; full detail is saved to the evidence file.
        """
        try:
            r = contract_test(sim_path, spec_provider(), _case_ids())
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}
        out = _compact_contract(r)
        out["evidence_file"] = _persist("contract_test", r)
        return out

    @tool
    def run_behavioural_check(replications: int = 30) -> dict:
        """Compare simulated behaviour with the OBSERVED training event log.

        Runs the model for `replications` seeds over the observed window and
        reports, per KPI, observed value vs simulated mean, 95% prediction
        interval and bias: completed cases, cases entered, WIP at end, flow
        time, time in system, failure rate, overlapping (parallel) steps per case,
        activity-duration MAPE, variant JSD, utilisation error; plus waiting
        time and idle time per resource class, case release spacing, and
        BPS distances (cycle-time EMD, arrival EMD, 2-gram JSD). `findings`
        lists the discrepancies in plain language - turn them into change
        requests. Use 30 replications (max 100).
        """
        try:
            spec = spec_provider()
            r = behavioural_check(sim_path, df, _schema(), terminal_from_spec(spec), m=max(5, min(int(replications), 100)))
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}
        if not r.get("ok"):
            return r
        ev_file = _persist("behavioural_check", r)
        kp = {k: v for k, v in r["kpis"].items()}
        return {"verdict": r["verdict"], "replications": r["replications"], "terminal_activity": r["terminal_activity"], "kpis": kp,
                "waiting_by_class_s": r["waiting_by_class_s"], "release_spacing_median_s": r["release_spacing_median_s"],
                "distances": r["distances"], "findings": r["findings"][:12], "evidence_file": ev_file}

    @tool
    def run_metamorphic_tests(replications: int = 10) -> dict:
        """Run oracle-free metamorphic relations on simulation.py (common random numbers).

        MR1: +1 capacity at the busiest resource must not increase waiting/flow time.
        MR2: ARRIVAL_RATE_SCALE=1.5 must not decrease cases entered or mean WIP.
        MR3: FAILURES_ENABLED=False must give failure rate 0 and not increase flow time.
        MR4: doubling SIMULATION_TIME should roughly double cases entered.
        A 'fail' indicates a logic error (wrong resource wiring, knob ignored,
        arrival schedule replayed from data, ...).
        """
        try:
            r = metamorphic_tests(sim_path, m=max(3, min(int(replications), 30)))
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}
        if r.get("ok"):
            r["evidence_file"] = _persist("metamorphic_tests", r)
        return r

    return [run_contract_test, run_behavioural_check, run_metamorphic_tests]
