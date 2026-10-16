"""P5 mutation analysis: does the deterministic behavioural verifier detect seeded faults?

Seeded faults are injected into the three published models at run time (no source edits):
inter-arrival times x0.5 / x2, +1 capacity at the busiest resource, the most frequent
activity's duration x1.5, and reversed step order (only where routings are a data table).
A mutant counts as detected when, relative to the unmutated model, a key KPI's observed
value drops out of the 95 % PI, or an error metric / BPS distance worsens by > 25 %.

    M=20 python analysis/mutation_test.py   -> mutation_test.csv
"""
import os
import sys

import numpy as np
import pandas as pd

from _common import RUN, block_csv, model_path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_extraction_tools.eventlog import LogSchema  # noqa: E402
from src.genai4simpy_agent.verification import behavioural_check, ground_truth  # noqa: E402

M = int(os.environ.get("M", 20))
SCHEMA = LogSchema(case_col="case", activity_col="concept:name", resource_col="org:resource",
                   start_col="time:timestamp", end_col="operation_end_time", variant_col="process_model_id",
                   lifecycle_col="lifecycle:transition", instance_col="identifier:id", enabled_value="scheduled",
                   start_value="start", complete_value="complete", state_col="lifecycle:state")
KEY = ["completed_cases", "cases_entered", "wip_at_T", "flow_time_completed_s", "time_in_system_all_s",
       "failure_rate", "mean_wip"]
ERR = ["activity_mape", "variant_jsd", "utilization_mae_pp"]
DIST = ["cycle_time_emd_s", "arrival_emd_s", "bigram_jsd"]
REVERSE = """
for k, v in list(vars(mod).items()):
    if isinstance(v, dict) and v and all(isinstance(x, list) and x and isinstance(x[0], tuple)
                                         and isinstance(x[0][0], str) and x[0][0].startswith('/') for x in v.values()):
        for key in v: v[key] = list(reversed(v[key]))
        mod._REVERSED = k
if not hasattr(mod, '_REVERSED'):
    raise RuntimeError('no routing table to reverse')
"""


def detected(base, mut):
    why = []
    for k in KEY:
        b, m = base["kpis"].get(k, {}), mut["kpis"].get(k, {})
        if b.get("pi_covered") and m.get("pi_covered") is False:
            why.append(f"{k} GT left PI")
    for k in ERR:
        b, m = base["kpis"][k].get("mean"), mut["kpis"][k].get("mean")
        if b is not None and m is not None and m > b * 1.25 + 1e-3:
            why.append(f"{k} {b:.3g}->{m:.3g}")
    for k in DIST:
        b, m = base["distances"].get(k), mut["distances"].get(k)
        if b is not None and m is not None and m > b * 1.25 + 1e-3:
            why.append(f"{k} {b:.3g}->{m:.3g}")
    return why


rows = []
for b in RUN:
    df = pd.read_csv(block_csv(b))
    gt = ground_truth(df, SCHEMA)
    inst_acts = gt[0]["activity"].value_counts()
    base = behavioural_check(model_path(b), df, SCHEMA, m=M, _gt=gt)
    util = {r: v["sim"] for r, v in base["utilization"].items() if v["sim"] is not None}
    busiest = max(util, key=util.get)
    top_act = inst_acts.index[0]
    mutants = {
        "iat_x0.5": {"timeout_scale": {"arrival": 0.5}},
        "iat_x2": {"timeout_scale": {"arrival": 2.0}},
        f"capacity+1_{busiest}": {"capacity": {busiest: 2}},
        f"duration_x1.5_{top_act}": {"timeout_scale": {"activity": {top_act: 1.5}}},
        "reversed_routing": {"exec": REVERSE},
    }
    for name, patch in mutants.items():
        mut = behavioural_check(model_path(b), df, SCHEMA, m=M, patch=patch, _gt=gt)
        if not mut.get("ok"):
            rows.append(dict(block=b, mutant=name, applicable=False, detected=np.nan, evidence=mut.get("error", "")[:120]))
            print(b, name, "n/a:", mut.get("error", "")[:120], flush=True)
            continue
        why = detected(base, mut)
        rows.append(dict(block=b, mutant=name, applicable=True, detected=bool(why), evidence="; ".join(why[:4])))
        print(b, f"{name:<40}", "DETECTED" if why else "missed", "|", "; ".join(why[:4]), flush=True)

R = pd.DataFrame(rows)
R.to_csv("mutation_test.csv", index=False)
a = R[R.applicable]
print(f"\ndetection rate: {int(a.detected.sum())}/{len(a)} = {a.detected.mean():.0%} (m={M})")
