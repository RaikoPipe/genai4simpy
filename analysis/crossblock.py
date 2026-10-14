"""A1 hold-out: every generated model (source block X) evaluated on every block Y
with evaluate_v2 definitions. Arms: FIFO (as generated) and in-process hbw priority.
Reference: 'copy source statistics' = empirical activity means / variant mix of X scored against Y.

    M=300 python analysis/crossblock.py   -> crossblock_A1.csv"""
import os
import simpy, numpy as np, pandas as pd
from _common import RUN, OrigResource, HbwPriority, block_csv, model_path
import evaluate_v2 as ev

M = int(os.environ.get("M", 300))
GT = {}
for y in RUN:
    real, T = ev.load_real(block_csv(y)); g = ev.kpis(real, T); GT[y] = (ev.kpis(real, T, ref=g), T)
rows = []
KP = ["completed_cases", "flow_time_completed_s", "time_in_system_all_s", "failure_rate", "activity_mape", "variant_jsd", "activity_coverage"]
for x in RUN:
    for y in RUN:
        gt, T = GT[y]
        # reference: copy source-block statistics
        src = GT[x][0]
        apes = [abs(src["activity_means"][a] - m) / m * 100 if a in src["activity_means"] else 100.0 for a, m in gt["activity_means"].items()]
        rows.append(dict(source=x, target=y, arm="copy source statistics", kpi="activity_mape", mean=np.mean(apes)))
        rows.append(dict(source=x, target=y, arm="copy source statistics", kpi="variant_jsd", mean=ev.jsd(src["variant_dist"], gt["variant_dist"])))
        for arm in ("FIFO (as generated)", "in-process hbw priority"):
            mod = ev.load_module(model_path(x), f"{x}{y}{arm[:2]}")
            if arm.startswith("in-process"):
                mod.simpy.Resource = HbwPriority
            try:
                ks = [ev.kpis(ev.simulate(mod, 42 + i, T), T, ref=gt) for i in range(M)]
            finally:
                simpy.Resource = OrigResource
            for kp in KP:
                s = ev.summarize([k[kp] for k in ks], None if kp in ev.ERROR_KPIS else gt[kp])
                rows.append(dict(source=x, target=y, arm=arm, kpi=kp, **s))
        print(x, "->", y, "done", flush=True)
pd.DataFrame(rows).to_csv("crossblock_A1.csv", index=False)
