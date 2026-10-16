"""Compare pipeline variants per block with evaluate_v2 definitions.

Arms per block:
  paper            the WSC models (analysis/_common.RUN)
  new-llm          simulation.py written by the LLM coder in a new run
  new-spec+compiler the same run's agent-written spec compiled deterministically (IR on, compiler)
  det-naive / det-discovery   LLM-free references (analysis/deterministic_baseline.py)

    M=300 RUNS="A=eager-nice-cow B=... C=..." python analysis/compare_runs.py  -> results/compare_runs.csv
"""
import json
import os
import sys

import pandas as pd

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, R)
os.chdir(R)

import evaluate_v2 as ev  # noqa: E402
from analysis._common import RUN as PAPER_RUN  # noqa: E402
from src.genai4simpy_agent.compiler import compile_spec  # noqa: E402

M = int(os.environ.get("M", 300))
# RUNS="A=run1,run2 B=run3": several runs per block are scored as separate arms.
RUNS = {k: v.split(",") for k, v in (x.split("=") for x in os.environ.get("RUNS", "").split())}
KP = ["completed_cases", "cases_entered", "flow_time_completed_s", "time_in_system_all_s", "failure_rate",
      "overlapping_steps_per_case", "activity_mape", "variant_jsd", "utilization_mae_pp"]


def arms(b):
    out = {"paper": f"output/fischertechnik_lab_{b}/{PAPER_RUN[b]}/reports/simulation/simulation.py"}
    for run in RUNS.get(b, []):
        rd = f"output/fischertechnik_lab_{b}/{run}"
        info = json.load(open(f"{rd}/experiment_results/run_info.json")) if os.path.exists(
            f"{rd}/experiment_results/run_info.json") else {}
        mode = (info.get("model_info") or {}).get("codegen_mode", "llm")
        p = f"{rd}/reports/simulation/simulation.py"
        if os.path.exists(p):
            out[f"{run}:{mode}-code"] = p
        if mode == "llm":
            try:
                spec = json.load(open(f"{rd}/reports/simulation_spec.json"))
                cp = f"results/compare/{b}_{run}_compiled.py"
                os.makedirs(os.path.dirname(cp), exist_ok=True)
                open(cp, "w").write(compile_spec(spec))
                out[f"{run}:spec+compiler"] = cp
            except Exception as exc:
                print(b, run, "spec not compilable:", exc)
    for a in ("naive", "discovery"):
        p = f"results/deterministic/{a}_{b}/simulation.py"
        if os.path.exists(p):
            out[f"det-{a}"] = p
    return out


rows = []
for b in ("A", "B", "C"):
    real, T = ev.load_real(f"data/fischertechnik_lab_{b}/block-{b}.csv")
    gt = ev.kpis(real, T); gt = ev.kpis(real, T, ref=gt)
    for arm, path in arms(b).items():
        try:
            mod = ev.load_module(path, "cmp_" + "".join(c if c.isalnum() else "_" for c in f"{b}_{arm}"))
            ks = [ev.kpis(ev.simulate(mod, 42 + i, T), T, ref=gt) for i in range(M)]
        except Exception as exc:
            print(b, arm, "FAILED:", type(exc).__name__, exc)
            continue
        for kp in KP:
            s = ev.summarize([k[kp] for k in ks], None if kp in ev.ERROR_KPIS else gt[kp])
            rows.append(dict(block=b, arm=arm, kpi=kp, **s))
        print(b, arm, "done", flush=True)
df = pd.DataFrame(rows)
os.makedirs("results", exist_ok=True)
df.to_csv(os.environ.get("OUT_CSV", "results/compare_runs.csv"), index=False)
show = df[df.kpi.isin(["completed_cases", "flow_time_completed_s", "time_in_system_all_s"])].pivot_table(
    index=["block", "arm"], columns="kpi", values="bias_pct").round(1)
show2 = df[df.kpi.isin(["activity_mape", "variant_jsd", "overlapping_steps_per_case"])].pivot_table(
    index=["block", "arm"], columns="kpi", values="mean").round(3)
print(show.join(show2).to_string())
