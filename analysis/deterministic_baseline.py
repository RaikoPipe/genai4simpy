"""LLM-free reference pipeline: spec from the deterministic tools -> compiler -> evaluate_v2.

Arms (proposal P3/P4 ablation without the LLM):
  naive      FIFO everywhere, strictly sequential steps, no early exits, single renewal IAT
  discovery  + learned priorities, intra-case concurrency, early exits, burst/gap arrivals

Scores every arm in-sample and on the cross-block hold-out (spec from block X scored on Y).

    M=200 python analysis/deterministic_baseline.py   -> deterministic_baseline.csv
"""
import json
import os
import sys

import pandas as pd

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, R)
os.chdir(R)

import evaluate_v2 as ev  # noqa: E402
from src.data_extraction_tools.eventlog import LogSchema, build_instances  # noqa: E402
from src.genai4simpy_agent.spec_drafting import activities_section, arrivals_section, topology_sections  # noqa: E402
from src.genai4simpy_agent.compiler import compile_spec  # noqa: E402
from src.genai4simpy_agent.spec import SECTION_MODELS  # noqa: E402

M = int(os.environ.get("M", 200))
OUT = os.environ.get("OUT", "results/deterministic")
SCHEMA = LogSchema(case_col="case", activity_col="concept:name", resource_col="org:resource",
                   start_col="time:timestamp", end_col="operation_end_time", variant_col="process_model_id",
                   lifecycle_col="lifecycle:transition", instance_col="identifier:id", enabled_value="scheduled",
                   start_value="start", complete_value="complete", state_col="lifecycle:state")
BLOCKS = ["A", "B", "C"]


def build_spec(block: str, arm: str) -> dict:
    """Spec from the same drafting functions the agents' draft_* tools use, with fixed decisions."""
    df = pd.read_csv(f"data/fischertechnik_lab_{block}/block-{block}.csv")
    inst, meta = build_instances(df, SCHEMA)
    full = arm == "discovery"
    spec, _ = topology_sections(inst, meta["T"], meta["t0"],
                                concurrent_pairs=None if full else [],
                                priority_classes=None if full else [],
                                include_early_exits=full)
    excluded = set(spec["initial_state"]["excluded_from_estimation"])
    spec["activities"] = activities_section(inst, excluded)
    spec["arrivals"] = arrivals_section(inst, excluded, None if full else "renewal")
    from pydantic import TypeAdapter
    for sec, val in spec.items():           # every section must pass the spec schema
        TypeAdapter(SECTION_MODELS[sec]).validate_python(val)
    return spec


def main():
    os.makedirs(OUT, exist_ok=True)
    paths = {}
    for b in BLOCKS:
        for arm in ("naive", "discovery"):
            spec = build_spec(b, arm)
            d = os.path.join(OUT, f"{arm}_{b}")
            os.makedirs(d, exist_ok=True)
            json.dump(spec, open(os.path.join(d, "simulation_spec.json"), "w"), indent=1, default=str)
            open(os.path.join(d, "simulation.py"), "w").write(compile_spec(spec))
            paths[(arm, b)] = os.path.join(d, "simulation.py")
    rows = []
    KP = ["completed_cases", "cases_entered", "flow_time_completed_s", "time_in_system_all_s", "failure_rate",
          "activity_mape", "variant_jsd", "overlapping_steps_per_case", "utilization_mae_pp"]
    for y in BLOCKS:
        real, T = ev.load_real(f"data/fischertechnik_lab_{y}/block-{y}.csv")
        gt = ev.kpis(real, T); gt = ev.kpis(real, T, ref=gt)
        for (arm, x), p in paths.items():
            mod = ev.load_module(p, f"det_{arm}_{x}_{y}")
            ks = [ev.kpis(ev.simulate(mod, 42 + i, T), T, ref=gt) for i in range(M)]
            for kp in KP:
                s = ev.summarize([k[kp] for k in ks], None if kp in ev.ERROR_KPIS else gt[kp])
                rows.append(dict(arm=arm, source=x, target=y, kpi=kp, **s))
            print(arm, x, "->", y, "done", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "deterministic_baseline.csv"), index=False)
    ins = df[df.source == df.target].pivot_table(index=["arm", "target"], columns="kpi",
                                                 values=["mean"]).round(3)
    print(ins.to_string())


if __name__ == "__main__":
    main()
