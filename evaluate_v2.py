"""evaluate_v2 — window-consistent, interval-based evaluation harness for GenAI4SimPy.

Differences to evaluate.py (v1):
  * Ground truth is COMPUTED from the raw block CSV with the very same KPI
    function that is applied to the simulated log (no hand-written constants).
  * KPI bases are explicit and identical across blocks: completed cases
    (successful TERMINAL activity inside the window) AND cases entered.
  * Arrival definition explicit: 'first_start' (always available) and
    'release' (needs the optional contract column `case_arrival`).
  * Verdicts: bias, 95 % prediction interval (PI) of per-replication KPIs,
    GT percentile rank, median per-replication |error|.  CI-of-mean is kept
    only for reference.  With >1 pipeline run per block a between-run PI is
    computed over run means.
  * Activity-duration MAPE over ALL GT activities; missing ones score 100 %.
  * Flow-time decomposition (service union / intra-case overlap / idle gaps)
    and per-resource idle-gap attribution + utilisation.

Usage:
  python evaluate_v2.py --models m1.py [m2.py ...] --block-csv block-C.csv -m 1000 -o out/
"""
import argparse, contextlib, importlib.util, io, json, os, sys
import numpy as np, pandas as pd
from scipy import stats

sys.dont_write_bytecode = True
TERMINAL = "/hbw/store"
EPS = 1e-9


# ------------------------------------------------------------- logs ---------
def load_real(csv_path):
    d = pd.read_csv(csv_path)
    ts = pd.to_datetime(d["time:timestamp"], format="ISO8601")
    te = pd.to_datetime(d["operation_end_time"], format="ISO8601")
    t0 = ts.min()
    d["t"] = (ts - t0).dt.total_seconds(); d["e"] = (te - t0).dt.total_seconds()
    k = "identifier:id"
    sc, st, co = (d[d["lifecycle:transition"] == x].set_index(k) for x in ("scheduled", "start", "complete"))
    assert sc.index.is_unique and st.index.is_unique and co.index.is_unique
    assert set(sc.index) == set(st.index) == set(co.index), "unpaired lifecycle transitions"
    log = pd.DataFrame({
        "case_id": st["case"], "variant": st["process_model_id"], "activity": st["concept:name"],
        "resource": st["org:resource"], "step_release": sc.loc[st.index, "t"],
        "service_start": st["t"], "operation_end_time": st["e"],
        "lifecycle:state": co.loc[st.index, "lifecycle:state"]}).reset_index(drop=True)
    log["case_arrival"] = log.groupby("case_id")["step_release"].transform("min")
    return log, float(d["t"].max())


def load_module(path, name=None):
    s = importlib.util.spec_from_file_location(name or f"m_{abs(hash(path))}", path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    if not hasattr(m, "run_single_replication"):
        raise AttributeError(f"{path}: contract requires run_single_replication(seed)")
    return m


def simulate(mod, seed, T):
    mod.SIMULATION_TIME = T
    with contextlib.redirect_stdout(io.StringIO()):
        out = mod.run_single_replication(seed)
    df = out[0] if isinstance(out, tuple) else out
    need = {"case_id", "variant", "activity", "resource", "time:timestamp", "operation_end_time", "lifecycle:state"}
    miss = need - set(df.columns)
    if miss:
        raise ValueError(f"seed {seed}: log missing {sorted(miss)}")
    df = df.copy()
    if "service_start" not in df:            # v1 models log service start in time:timestamp
        df["service_start"] = df["time:timestamp"]
    if "case_arrival" not in df:
        df["case_arrival"] = np.nan
    return df


# ------------------------------------------------------------ KPIs ----------
def _union_length(iv):
    iv = sorted(iv); tot = 0.0; cs, ce = iv[0]
    for s, e in iv[1:]:
        if s > ce: tot += ce - cs; cs, ce = s, e
        else: ce = max(ce, e)
    return tot + ce - cs


def kpis(log, T, ref=None):
    """Identical definitions for real and simulated logs. `ref` = GT KPI dict
    (from the real log) for reference-dependent KPIs (JSD, MAPE)."""
    L = log[log["operation_end_time"] <= T + EPS].sort_values(["case_id", "service_start"]).copy()
    L["dur"] = L["operation_end_time"] - L["service_start"]
    c = L.groupby("case_id").agg(a=("service_start", "min"), z=("operation_end_time", "max"),
                                 rel=("case_arrival", "min"), v=("variant", "first"))
    done_ids = L.loc[(L["activity"] == TERMINAL) & (L["lifecycle:state"] == "success"), "case_id"].unique()
    cd = c.loc[c.index.isin(done_ids)]
    k = {"cases_entered": len(c), "completed_cases": len(cd), "wip_at_T": len(c) - len(cd),
         "flow_time_completed_s": float((cd.z - cd.a).mean()) if len(cd) else np.nan,
         "time_in_system_all_s": float((c.z - c.a).mean()) if len(c) else np.nan,
         "flow_time_completed_release_s": float((cd.z - cd.rel).mean()) if len(cd) and cd.rel.notna().all() else np.nan,
         "failure_rate": float((L["lifecycle:state"] == "failure").mean())}
    # ---- flow-time decomposition over completed cases
    Lc = L[L["case_id"].isin(done_ids)].copy()
    if len(Lc):
        g = Lc.groupby("case_id")
        union = g.apply(lambda x: _union_length(list(zip(x.service_start, x.operation_end_time))), include_groups=False)
        ssum = g["dur"].sum()
        flow = (cd.z - cd.a).loc[union.index]
        k.update(service_union_s=float(union.mean()), overlap_s=float((ssum - union).mean()),
                 idle_s=float((flow - union).mean()), steps_per_completed_case=float(g.size().mean()))
        Lc["prev_end"] = g["operation_end_time"].shift()
        Lc["gap"] = (Lc["service_start"] - Lc["prev_end"]).clip(lower=0)
        k["idle_by_resource_class_s"] = (Lc.groupby(Lc["resource"].str.split("_").str[0])["gap"].sum()
                                         / len(cd)).to_dict()           # mean idle per completed case
        k["overlapping_steps_per_case"] = float(((Lc["service_start"] - Lc["prev_end"]) < -0.5).sum() / len(cd))
    else:
        k.update(service_union_s=np.nan, overlap_s=np.nan, idle_s=np.nan, steps_per_completed_case=np.nan,
                 idle_by_resource_class_s={}, overlapping_steps_per_case=np.nan)
    k["utilization"] = (L.groupby("resource")["dur"].sum() / T).to_dict()
    succ = L[L["lifecycle:state"] == "success"]
    k["activity_means"] = succ.groupby("activity")["dur"].mean().to_dict()
    k["variant_dist"] = c["v"].value_counts(normalize=True).to_dict()
    if ref is not None:
        apes = []
        for a, gm in ref["activity_means"].items():
            apes.append(abs(k["activity_means"][a] - gm) / gm * 100 if a in k["activity_means"] and gm > 0 else 100.0)
        k["activity_mape"] = float(np.mean(apes))
        k["activity_coverage"] = float(np.mean([a in k["activity_means"] for a in ref["activity_means"]]))
        k["variant_jsd"] = jsd(k["variant_dist"], ref["variant_dist"])
        k["utilization_mae_pp"] = float(np.mean([abs(k["utilization"].get(r, 0) - u) * 100
                                                 for r, u in ref["utilization"].items()]))
    return k


def jsd(p, q):
    lab = sorted(set(p) | set(q))
    pv = np.array([p.get(l, 0) for l in lab], float); qv = np.array([q.get(l, 0) for l in lab], float)
    pv, qv = pv / pv.sum(), qv / qv.sum(); m = (pv + qv) / 2
    f = lambda a: np.sum(np.where(a > 0, a * np.log2(np.where(a > 0, a, 1) / m), 0))
    return float(0.5 * f(pv) + 0.5 * f(qv))


SCALAR = ["cases_entered", "completed_cases", "wip_at_T", "flow_time_completed_s", "time_in_system_all_s",
          "flow_time_completed_release_s", "failure_rate", "service_union_s", "overlap_s", "idle_s",
          "steps_per_completed_case", "overlapping_steps_per_case",
          "activity_mape", "activity_coverage", "variant_jsd", "utilization_mae_pp"]
ERROR_KPIS = {"activity_mape", "variant_jsd", "utilization_mae_pp", "activity_coverage"}       # target 0, not a GT point value


def summarize(x, gt):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if len(x) == 0:
        return {"n": 0}
    n = len(x); mu = x.mean(); sd = x.std(ddof=1) if n > 1 else 0.0
    hw = stats.t.ppf(.975, n - 1) * sd / np.sqrt(n) if n > 1 and sd > 0 else 0.0
    lo, hi = np.percentile(x, [2.5, 97.5])
    out = {"n": n, "mean": mu, "sd": sd, "pi_lo": lo, "pi_hi": hi, "ci_lo": mu - hw, "ci_hi": mu + hw}
    if gt is not None and not np.isnan(gt):
        out.update(gt=gt, bias_pct=(mu - gt) / gt * 100 if gt else np.nan,
                   pi_covered=bool(lo <= gt <= hi), ci_covered=bool(mu - hw <= gt <= mu + hw),
                   gt_percentile=float((np.mean(x < gt) + 0.5 * np.mean(x == gt)) * 100),
                   median_abs_err_pct=float(np.median(np.abs(x - gt) / abs(gt) * 100)) if gt else np.nan)
    return out


# ------------------------------------------------------------ driver --------
def evaluate(model_paths, block_csv, m=1000, base_seed=42):
    real, T = load_real(block_csv)
    gt = kpis(real, T)
    gt_ref = kpis(real, T, ref=gt)                       # self-reference: MAPE/JSD = 0 sanity check
    assert gt_ref["activity_mape"] < 1e-9 and gt_ref["variant_jsd"] < 1e-12
    gt = gt_ref
    runs, reps_all = [], []
    for r_i, p in enumerate(model_paths):
        mod = load_module(p, f"model_{r_i}")
        reps = []
        for i in range(m):
            k = kpis(simulate(mod, base_seed + i, T), T, ref=gt)
            reps.append(k)
        R = pd.DataFrame([{s: k[s] for s in SCALAR} for k in reps]); R["run"] = r_i
        reps_all.append(R)
        idle_cls = pd.DataFrame([k["idle_by_resource_class_s"] for k in reps]).mean().to_dict()
        runs.append({"model": p, "summary": {s: summarize(R[s], None if s in ERROR_KPIS else gt[s]) for s in SCALAR},
                     "idle_by_resource_class_s": idle_cls,
                     "utilization_mean": pd.DataFrame([k["utilization"] for k in reps]).mean().to_dict()})
    allR = pd.concat(reps_all, ignore_index=True)
    between = None
    if len(model_paths) > 1:   # between-run PI over run means (generative variance)
        means = allR.groupby("run")[SCALAR].mean()
        between = {s: summarize(means[s], None if s in ERROR_KPIS else gt[s]) for s in SCALAR}
    return {"block_csv": block_csv, "T": T, "m": m, "base_seed": base_seed,
            "ground_truth": {s: gt[s] for s in SCALAR if s in gt} | {
                "idle_by_resource_class_s": gt["idle_by_resource_class_s"], "utilization": gt["utilization"]},
            "runs": runs, "between_run": between}, allR


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--block-csv", required=True)
    ap.add_argument("-m", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("-o", "--output", default="eval_v2_out")
    a = ap.parse_args()
    res, reps = evaluate(a.models, a.block_csv, a.m, a.seed)
    os.makedirs(a.output, exist_ok=True)
    json.dump(res, open(os.path.join(a.output, "evaluation_v2.json"), "w"), indent=2, default=float)
    reps.to_csv(os.path.join(a.output, "replications_v2.csv"), index=False)
    g = res["ground_truth"]
    for s in ["completed_cases", "flow_time_completed_s", "time_in_system_all_s", "failure_rate", "activity_mape", "variant_jsd"]:
        r = res["runs"][0]["summary"][s]
        print(f"{s:<26} GT={g.get(s, 0):>9.3f} mean={r['mean']:>9.3f} PI=[{r['pi_lo']:.3f},{r['pi_hi']:.3f}]"
              + (f" bias={r['bias_pct']:+.1f}% pct={r['gt_percentile']:.1f}" if 'bias_pct' in r else ""))


if __name__ == "__main__":
    main()
