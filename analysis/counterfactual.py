"""Counterfactual: replace FIFO hbw resources by priority resources where
requests from in-process cases (any activity other than /hbw/unload) precede
new-order unloads. Generated model code is otherwise untouched.

    M=300 python analysis/counterfactual.py   -> counterfactual_hbw_priority.json"""
import os, json
import simpy, numpy as np, pandas as pd
from _common import RUN, STATS, OrigResource, HbwPriority, block_csv, model_path
import evaluate_v2 as ev

M = int(os.environ.get("M", 300)); out = {}
for b in RUN:
    real, T = ev.load_real(block_csv(b)); gt = ev.kpis(real, T); gt = ev.kpis(real, T, ref=gt)
    res = {}
    for arm in ("FIFO (as generated)", "in-process priority at hbw"):
        mod = ev.load_module(model_path(b), f"{b}{arm[:3]}")
        if arm.startswith("in-process"):
            mod.simpy.Resource = HbwPriority
        try:
            ks = [ev.kpis(ev.simulate(mod, 42 + i, T), T, ref=gt) for i in range(M)]
        finally:
            simpy.Resource = OrigResource
        df = pd.DataFrame([{s: k[s] for s in ["completed_cases", "flow_time_completed_s", "time_in_system_all_s",
                                              "idle_s", "failure_rate", "activity_mape"]} for k in ks])
        res[arm] = {s: ev.summarize(df[s], None if s == "activity_mape" else gt[s]) for s in df}
        res[arm]["idle_hbw_s"] = float(np.mean([k["idle_by_resource_class_s"].get("hbw", 0) for k in ks]))
    out[b] = {"gt_idle_hbw_s": gt["idle_by_resource_class_s"].get("hbw", 0), "arms": res}
    for arm, r in res.items():
        print(b, f"{arm:<28}", "completed %.1f (GT %d) | flow bias %+.1f%% pct %.1f | TIS bias %+.1f%% | hbw idle %.1f (GT %.1f) | fail bias %+.1f%%" % (
            r["completed_cases"]["mean"], gt["completed_cases"], r["flow_time_completed_s"]["bias_pct"], r["flow_time_completed_s"]["gt_percentile"],
            r["time_in_system_all_s"]["bias_pct"], r["idle_hbw_s"], out[b]["gt_idle_hbw_s"], r["failure_rate"]["bias_pct"]))
print(STATS)
json.dump(out, open("counterfactual_hbw_priority.json", "w"), indent=2, default=float)
