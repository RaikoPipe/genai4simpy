"""Re-evaluation of the three GenAI4SimPy models (shortcomings A2 + A5).

A2: replace CI-of-the-mean coverage by a 95 % prediction interval (PI) over
    per-replication KPIs and the ground-truth (GT) percentile rank.
A5: compute KPIs with ONE function applied identically to the real and the
    simulated event log (same window, same arrival / completion definitions).

    M_REPS=500 python analysis/reeval.py   -> reeval_A2_A5.csv, reeval_meta.json, reps_*.csv
"""
import sys, io, os, json, contextlib, importlib.util
import numpy as np, pandas as pd

sys.dont_write_bytecode = True
from _common import R, RUN as RUNS
TERMINAL = "/hbw/store"
M = int(os.environ.get("M_REPS", 500))
BASE_SEED = 42                      # evaluate.py default


def _load(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


EV = _load(f"{R}/evaluate.py", "evaluate_orig")


# ---------------------------------------------------------------- real log ---
def real_standard_log(b):
    """Raw block CSV -> one row per activity instance, sim-log schema plus
    'release' (= scheduled time) and 'service_start'."""
    d = pd.read_csv(f"{R}/data/fischertechnik_lab_{b}/block-{b}.csv")
    ts = pd.to_datetime(d["time:timestamp"], format="ISO8601")
    te = pd.to_datetime(d["operation_end_time"], format="ISO8601")
    t0 = ts.min()
    d["t"] = (ts - t0).dt.total_seconds(); d["e"] = (te - t0).dt.total_seconds()
    key = "identifier:id"
    sc = d[d["lifecycle:transition"] == "scheduled"].set_index(key)
    st = d[d["lifecycle:transition"] == "start"].set_index(key)
    co = d[d["lifecycle:transition"] == "complete"].set_index(key)
    assert sc.index.is_unique and st.index.is_unique and co.index.is_unique
    assert set(sc.index) == set(st.index) == set(co.index), "unpaired transitions"
    out = pd.DataFrame({
        "case_id": st["case"], "variant": st["process_model_id"],
        "activity": st["concept:name"], "resource": st["org:resource"],
        "release": sc.loc[st.index, "t"], "service_start": st["t"],
        "operation_end_time": st["e"],
        "lifecycle:state": co.loc[st.index, "lifecycle:state"]}).reset_index(drop=True)
    out["time:timestamp"] = out["service_start"]
    T = float(d["t"].max())
    return out, T


# ------------------------------------------------- unified KPI function -----
def kpis(log, T, gt_act_means=None, arrival_col="service_start"):
    """Identical definitions for real and simulated logs.
    Only activity instances COMPLETED within [0, T] are counted (both logs
    contain only such rows: the real window ends at its last event; models
    append a row after the activity's timeout, and env.run(until=T))."""
    L = log[log["operation_end_time"] <= T + 1e-9]
    c = L.groupby("case_id").agg(a=(arrival_col, "min"), z=("operation_end_time", "max"),
                                 v=("variant", "first"))
    done = L.loc[(L["activity"] == TERMINAL) & (L["lifecycle:state"] == "success"), "case_id"].unique()
    cd = c.loc[c.index.isin(done)]
    k = {
        "cases_started": len(c),
        "completed_cases": len(cd),
        "wip_at_T": len(c) - len(cd),
        "flow_time_completed_s": float((cd.z - cd.a).mean()) if len(cd) else np.nan,
        "time_in_system_all_s": float((c.z - c.a).mean()) if len(c) else np.nan,  # censored at T
        "failure_rate": float((L["lifecycle:state"] == "failure").mean()),
    }
    if gt_act_means is not None:
        succ = L[L["lifecycle:state"] == "success"]
        sm = (succ["operation_end_time"] - succ["service_start"]).groupby(succ["activity"]).mean()
        apes = [abs(sm[a] - g) / g * 100 for a, g in gt_act_means.items() if a in sm.index and g > 0]
        k["activity_mape_present"] = float(np.mean(apes)) if apes else np.nan
        k["activity_coverage"] = len(apes) / len(gt_act_means)
    return k


# ------------------------------------------------------------- runner -------
def run_model(b, gt, T, m):
    mod = _load(f"{R}/output/fischertechnik_lab_{b}/{RUNS[b]}/reports/simulation/simulation.py", f"sim_{b}")
    orig_T = getattr(mod, "SIMULATION_TIME", None)
    mod.SIMULATION_TIME = T                         # same override as evaluate.py
    caps = getattr(mod, "RESOURCE_CAPACITIES", {})
    harness, unified = [], []
    for i in range(m):
        with contextlib.redirect_stdout(io.StringIO()):
            out = mod.run_single_replication(BASE_SEED + i)
        df = out[0] if isinstance(out, tuple) else out
        EV.validate_log(df, f"{b} seed {BASE_SEED+i}")
        h = EV.compute_kpis(df, gt, T, caps); h.pop("iat_values"); h.pop("per_activity_error")
        h.pop("resource_utilization"); harness.append(h)
        s = df.copy()
        s["service_start"] = s["service_start"] if "service_start" in s else s["time:timestamp"]
        unified.append(kpis(s, T, gt["activity_mean_durations_s"]))
    return pd.DataFrame(harness), pd.DataFrame(unified), orig_T


def summarize(sim, gtv):
    x = sim.dropna().to_numpy(float)
    n = len(x); mean = x.mean(); sd = x.std(ddof=1) if n > 1 else 0.0
    from scipy import stats
    hw = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n) if n > 1 and sd > 0 else 0.0
    lo, hi = np.percentile(x, [2.5, 97.5])
    # mid-rank percentile of GT in the simulated distribution
    pct = (np.mean(x < gtv) + 0.5 * np.mean(x == gtv)) * 100
    ape = np.abs(x - gtv) / abs(gtv) * 100 if gtv else np.full(n, np.nan)
    return {"gt": gtv, "sim_mean": mean, "sim_sd": sd,
            "ci_mean_lo": mean - hw, "ci_mean_hi": mean + hw,
            "ci_covered": bool(mean - hw <= gtv <= mean + hw),
            "pi_lo": lo, "pi_hi": hi, "pi_covered": bool(lo <= gtv <= hi),
            "gt_percentile": pct, "bias_pct": (mean - gtv) / gtv * 100 if gtv else np.nan,
            "median_abs_err_pct": float(np.median(ape)), "n_reps": n}


if __name__ == "__main__":
    rows, meta = [], {}
    for b in "ABC":
        gt = EV.load_ground_truth(f"{R}/data/fischertechnik_lab_{b}/ground_truth_block_{b}.py")
        real, T = real_standard_log(b)
        assert abs(T - gt["observation_period_s"]) < 0.2, (T, gt["observation_period_s"])
        H, U, orig_T = run_model(b, gt, T, M)
        H.to_csv(f"reps_harness_{b}.csv", index=False); U.to_csv(f"reps_unified_{b}.csv", index=False)
        real_k_start = kpis(real, T, gt["activity_mean_durations_s"], "service_start")
        real_k_rel = kpis(real, T, gt["activity_mean_durations_s"], "release")
        meta[b] = {"T": T, "gt_has_terminal_activity": bool(gt.get("terminal_activity")), "model_SIMULATION_TIME": orig_T,
                   "real_kpis_arrival_first_start": real_k_start,
                   "real_kpis_arrival_release": real_k_rel,
                   "published_gt": {k: gt.get(k) for k in ("throughput", "completed_cases",
                                    "mean_flow_time_s", "failure_rate")}}
        # (1) published harness definitions (reproduction) -----------------
        for kpi, gtv in [("throughput_total", gt["completed_cases"] if gt.get("terminal_activity") else gt["throughput"]),
                         ("mean_flow_time_s", gt["mean_flow_time_s"]),
                         ("failure_rate", gt["failure_rate"])]:
            rows.append({"block": b, "definition": "published harness", "kpi": kpi, **summarize(H[kpi], gtv)})
        # (2) unified, window-consistent definitions (arrival = first service start)
        for kpi in ["cases_started", "completed_cases", "wip_at_T", "flow_time_completed_s",
                    "time_in_system_all_s", "failure_rate"]:
            rows.append({"block": b, "definition": "unified (arrival = first service start)",
                         "kpi": kpi, **summarize(U[kpi], real_k_start[kpi])})
        # (3) flow time vs release-based GT (what the real system actually experiences)
        for kpi in ["flow_time_completed_s", "time_in_system_all_s"]:
            rows.append({"block": b, "definition": "GT arrival = order release (sim cannot log it)",
                         "kpi": kpi, **summarize(U[kpi], real_k_rel[kpi])})
        meta[b]["activity_coverage"] = float(U["activity_coverage"].mean())
        meta[b]["activity_mape_present_mean"] = float(U["activity_mape_present"].mean())
        print(b, "done", len(H), "reps", flush=True)
    res = pd.DataFrame(rows); res.to_csv("reeval_A2_A5.csv", index=False)
    json.dump(meta, open("reeval_meta.json", "w"), indent=2, default=float)
