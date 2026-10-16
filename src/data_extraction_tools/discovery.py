"""Deterministic process-mining discovery tools (proposal P2 censoring + P4 control logic).

The LLM agents *call and interpret* these tools instead of re-implementing the
analyses in ``run_python``. All functions work on the activity-instance table
built by :func:`src.data_extraction_tools.eventlog.build_instances` and return
compact, JSON-serialisable summaries (top-k, rounded) suitable for an LLM context.

Functions
---------
two_regime_iat               burst / gap decomposition of an inter-arrival series
detect_censoring             cases cut by the observation window, initial WIP, step presence
decompose_waiting_times      waiting split into contention / prioritization / extraneous
test_dispatching_rules       FIFO vs LIFO vs case-age vs progress vs learned activity priority
detect_release_control       WIP at release, completion-triggered release, release bursts
detect_intra_case_concurrency  steps of a case that overlap in time
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from typing import Any, Callable, Literal

import numpy as np
import pandas as pd
from langchain_core.tools import tool

from src.data_extraction_tools.eventlog import LogSchema, build_instances, resource_class

OVERLAP_TOL_S = 0.5      # same tolerance as evaluate_v2.overlapping_steps_per_case


# =============================================================================
# Helpers
# =============================================================================

def _r(x: Any, nd: int = 3) -> Any:
    """Round floats (and numpy scalars) for compact JSON output; NaN -> None."""
    if isinstance(x, (float, np.floating)):
        return None if not np.isfinite(x) else round(float(x), nd)
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


def _stats(x: np.ndarray | pd.Series, nd: int = 3) -> dict[str, Any]:
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return {"n": 0}
    mean = float(x.mean())
    sd = float(x.std(ddof=1)) if len(x) > 1 else 0.0
    return {"n": int(len(x)), "mean": _r(mean, nd), "std": _r(sd, nd),
            "cv": _r(sd / mean, nd) if mean > 0 else None,
            "median": _r(float(np.median(x)), nd), "min": _r(float(x.min()), nd), "max": _r(float(x.max()), nd)}


def _union_length(iv: list[tuple[float, float]]) -> float:
    iv = sorted((s, e) for s, e in iv if e > s)
    if not iv:
        return 0.0
    tot, (cs, ce) = 0.0, iv[0]
    for s, e in iv[1:]:
        if s > ce:
            tot += ce - cs
            cs, ce = s, e
        else:
            ce = max(ce, e)
    return tot + ce - cs


def _otsu_threshold(v: np.ndarray) -> tuple[float, float]:
    """Otsu threshold on a 1-D sample; returns (threshold, between-class variance ratio)."""
    v = np.sort(v)
    best_t, best_s = float(v[0]), -1.0
    tot_var = v.var() * len(v)
    for i in range(1, len(v)):
        a, b = v[:i], v[i:]
        s = len(a) * len(b) * (a.mean() - b.mean()) ** 2 / len(v)
        if s > best_s:
            best_s, best_t = s, (v[i - 1] + v[i]) / 2
    return float(best_t), float(best_s / tot_var) if tot_var > 0 else 0.0


# =============================================================================
# 6. Two-regime arrivals
# =============================================================================

def two_regime_iat(iat_seconds: np.ndarray, min_ratio: float = 20.0, min_sep: float = 0.8) -> dict[str, Any]:
    """Burst / gap decomposition of an inter-arrival-time series (seconds).

    Zero IATs (simultaneous arrivals) belong to bursts. The positive IATs are
    split by an Otsu threshold on log10(IAT). The split is accepted as two
    regimes only when the gap mean is at least ``min_ratio`` x the burst mean
    and the log-scale separation (between-class / total variance) is at least
    ``min_sep``; otherwise a single regime is reported.

    Returns raw overall IAT stats, the regime verdict, burst IAT stats (within
    a burst), gap stats (between bursts), and the burst-size distribution
    (arrivals per burst) — the parameters a batch/burst arrival model needs.
    """
    x = np.asarray(iat_seconds, float)
    x = x[np.isfinite(x) & (x >= 0)]
    out: dict[str, Any] = {"overall": _stats(x), "arrivals": int(len(x) + 1)}
    pos = x[x > 0]
    if len(pos) < 4:
        out.update(regime="single", reason="too few positive inter-arrival times for a split")
        return out
    thr_log, sep = _otsu_threshold(np.log10(pos))
    thr = 10 ** thr_log
    burst, gap = x[x <= thr], x[x > thr]
    ratio = gap.mean() / burst.mean() if len(burst) and burst.mean() > 0 else np.inf
    two = len(gap) >= 1 and len(burst) >= 2 and ratio >= min_ratio and sep >= min_sep
    out.update(threshold_s=_r(thr), log_separation=_r(sep), gap_to_burst_ratio=_r(ratio))
    if not two:
        out.update(regime="single", reason="no clear burst/gap separation; use the overall IAT")
        return out
    # burst sizes: arrivals between consecutive gaps
    sizes, cur = [], 1
    for v in x:
        if v > thr:
            sizes.append(cur)
            cur = 1
        else:
            cur += 1
    sizes.append(cur)
    out.update(
        regime="two_regime",
        burst_iat=_stats(burst),
        gap_iat=_stats(gap),
        burst_size={"mean": _r(float(np.mean(sizes))), "values": sizes[:50], "n_bursts": len(sizes)},
        note=("Arrivals come in bursts: model a gap process between bursts (gap_iat) and "
              "burst_size arrivals per burst spaced by burst_iat. The overall mean IAT mixes both "
              "regimes; never drop the gaps as outliers."),
    )
    return out


# =============================================================================
# 1. Censoring
# =============================================================================

def _infer_boundary_activity(seqs: dict[str, list[str]], which: Literal["first", "last"]) -> str | None:
    """Activity that, when it occurs in a case, is most often its first/last step."""
    occ, pos = Counter(), Counter()
    for s in seqs.values():
        if not s:
            continue
        for a in set(s):
            occ[a] += 1
        pos[s[0] if which == "first" else s[-1]] += 1
    min_support = max(2, int(0.1 * len(seqs)))
    cands = [(pos[a] / occ[a], pos[a], a) for a in pos if pos[a] >= min_support]
    return max(cands)[2] if cands else None


def detect_censoring(inst: pd.DataFrame, T: float, terminal_activity: str | None = None,
                     first_activity: str | None = None, edge_tol_s: float | None = None) -> dict[str, Any]:
    """Classify cases by how the observation window [0, T] cuts them.

    * complete         — contains a successful terminal activity
    * right_censored   — no terminal activity and the last step ended within
                         ``edge_tol_s`` of T (the case could still be running)
    * left_censored    — missing the typical first activity and starts within
                         ``edge_tol_s`` of 0 (it began before the window)
    * incomplete_interior — no terminal activity but ended well inside the
                         window (scrap, abandonment or missing data)

    ``edge_tol_s`` defaults to the 95th percentile of idle gaps between
    consecutive steps of complete cases (how long a live case can stay silent).
    """
    d = inst.sort_values(["case_id", "start"])
    seqs = {c: g["activity"].tolist() for c, g in d.groupby("case_id")}
    first_activity = first_activity or _infer_boundary_activity(seqs, "first")
    terminal_activity = terminal_activity or _infer_boundary_activity(seqs, "last")
    rel = d["enabled"].fillna(d["start"])
    c = d.assign(rel=rel).groupby("case_id").agg(
        first=("rel", "min"), last_end=("end", "max"), variant=("variant", "first"))
    c["first_act"] = [seqs[i][0] for i in c.index]
    done = set(d.loc[(d["activity"] == terminal_activity) & (d["state"] == "success"), "case_id"])
    c["complete"] = c.index.isin(done)

    if edge_tol_s is None:
        dc = d[d["case_id"].isin(done)]
        gaps = (dc["start"] - dc.groupby("case_id")["end"].shift()).dropna().clip(lower=0)
        edge_tol_s = float(np.percentile(gaps, 95)) if len(gaps) >= 5 else 120.0
        edge_tol_s = max(edge_tol_s, 30.0)

    c["right"] = ~c["complete"] & (T - c["last_end"] <= edge_tol_s)
    c["left"] = (c["first_act"] != first_activity) & (c["first"] <= edge_tol_s)
    c["interior"] = ~c["complete"] & ~c["right"]
    missing_first = c.index[c["first_act"] != first_activity].tolist()

    # step presence per variant: all cases vs complete cases only
    pres: dict[str, Any] = {}
    for v, g in d.groupby("variant"):
        cases_all = g["case_id"].unique()
        cases_done = [x for x in cases_all if x in done]
        acts = sorted(g["activity"].unique())
        row = {}
        for a in acts:
            has = set(g.loc[g["activity"] == a, "case_id"])
            p_all = len(has & set(cases_all)) / len(cases_all)
            p_done = len(has & set(cases_done)) / len(cases_done) if cases_done else None
            if p_done is not None and abs(p_all - p_done) >= 0.15 or (p_done == 1.0 and p_all < 1.0):
                row[a] = {"all": _r(p_all, 2), "complete_only": _r(p_done, 2)}
        if row:
            pres[str(v)] = {"n_all": int(len(cases_all)), "n_complete": len(cases_done),
                            "steps_biased_by_truncation": row}

    init = c[c["left"]]
    initial_wip = [{"case_id": i, "first_observed_activity": r.first_act} for i, r in init.iterrows()]
    vm_all = c["variant"].value_counts(normalize=True)
    vm_done = c.loc[c["complete"], "variant"].value_counts(normalize=True)
    warnings = []
    if c["complete"].sum() < max(5, 0.3 * len(c)):
        warnings.append(f"Only {int(c['complete'].sum())}/{len(c)} cases are complete: per-variant routing "
                        f"estimates from complete cases are thin; pool variants or flag them as low confidence.")
    if len(c[c["interior"]]) > 0.3 * len(c):
        warnings.append(f"{int(c['interior'].sum())} cases end inside the window without the terminal activity "
                        f"(not window truncation): check whether they are scrap/abandoned or missing data.")
    return {
        "warnings": warnings,
        "window_T_s": _r(T, 1),
        "inferred_first_activity": first_activity,
        "inferred_terminal_activity": terminal_activity,
        "edge_tol_s": _r(edge_tol_s, 1),
        "n_cases": int(len(c)),
        "n_complete": int(c["complete"].sum()),
        "right_censored": c.index[c["right"]].tolist(),
        "left_censored": c.index[c["left"]].tolist(),
        "incomplete_interior": c.index[c["interior"]].tolist(),
        "missing_first_activity": missing_first,
        "initial_wip_at_window_start": {"count": len(initial_wip), "cases": initial_wip},
        "variant_mix": {"all_cases": {k: _r(v, 3) for k, v in vm_all.items()},
                        "complete_cases": {k: _r(v, 3) for k, v in vm_done.items()}},
        "step_presence": pres,
        "guidance": (
            "Estimate routing probabilities, step-presence (optional vs always-present steps) and "
            "per-variant sequences from COMPLETE cases only; right-censored cases are cut by the window "
            "end, not real early exits. Arrival rates and service times may use all cases. If "
            "initial_wip > 0, initialise the simulation with those cases in progress instead of "
            "replaying them. Never hard-code observed case ids."),
    }


# =============================================================================
# 2. Waiting-time decomposition
# =============================================================================

def decompose_waiting_times(inst: pd.DataFrame, top_k: int = 25) -> dict[str, Any]:
    """Split each step's waiting time (start - enabled) into causes.

    For the concrete resource that served the step, during the waiting interval:
    * contention     — resource busy with other cases enabled EARLIER (FIFO-consistent)
    * prioritization — resource busy with cases enabled LATER (they overtook this one)
    * extraneous     — resource idle while the case waited (unavailability, hand-off,
                       transport, or waiting for another resource / batching)
    """
    d = inst.dropna(subset=["enabled", "start", "end"]).copy()
    d["wait"] = (d["start"] - d["enabled"]).clip(lower=0)
    by_res = {r: g[["enabled", "start", "end", "case_id"]].to_numpy() for r, g in d.groupby("resource")}
    cont, prio, extr = [], [], []
    for _, row in d.iterrows():
        e, s = row["enabled"], row["start"]
        if s - e <= 1e-9:
            cont.append(0.0); prio.append(0.0); extr.append(0.0)
            continue
        oth = by_res[row["resource"]]
        iv_c, iv_p = [], []
        for en, st, en_d, cid in oth:
            if cid == row["case_id"] and st == s:
                continue
            a, b = max(st, e), min(en_d, s)
            if b > a:
                (iv_p if en > e else iv_c).append((a, b))
        p = _union_length(iv_p)
        tot = _union_length(iv_c + iv_p)
        cont.append(tot - p); prio.append(p); extr.append(max(s - e - tot, 0.0))
    d["contention"], d["prioritization"], d["extraneous"] = cont, prio, extr
    d["rclass"] = resource_class(d["resource"])

    def agg(g: pd.DataFrame) -> dict[str, Any]:
        w = g["wait"].sum()
        sh = (lambda col: _r(g[col].sum() / w, 3) if w > 0 else 0.0)
        return {"n": int(len(g)), "mean_wait_s": _r(g["wait"].mean(), 1), "p90_wait_s": _r(g["wait"].quantile(.9), 1),
                "share_contention": sh("contention"), "share_prioritization": sh("prioritization"),
                "share_extraneous": sh("extraneous")}

    by_act = {a: agg(g) for a, g in d.groupby("activity")}
    by_act = dict(sorted(by_act.items(), key=lambda kv: -kv[1]["mean_wait_s"] * kv[1]["n"])[:top_k])
    by_cls = {k: agg(g) for k, g in d.groupby("rclass")}
    findings = []
    for k, v in by_cls.items():
        if v["share_prioritization"] and v["share_prioritization"] >= 0.2:
            findings.append(f"{k}: {v['share_prioritization']:.0%} of waiting is caused by later-enabled steps "
                            f"overtaking -> queue is NOT FIFO; run test_dispatching_rules for '{k}'.")
        if v["share_extraneous"] and v["share_extraneous"] >= 0.5 and v["mean_wait_s"] >= 5:
            findings.append(f"{k}: {v['share_extraneous']:.0%} of waiting happens while the resource is idle "
                            f"-> delay is not caused by this resource (hand-off/transport/release control).")
    return {"n_steps_with_enabled_time": int(len(d)), "overall": agg(d), "by_resource_class": by_cls,
            "by_activity_top": by_act, "findings": findings}


# =============================================================================
# 3. Dispatching rules
# =============================================================================

def _decision_points(d: pd.DataFrame, key: str) -> list[dict[str, Any]]:
    """Every service start at which >1 instance was waiting on the same server/pool."""
    pts = []
    for k, g in d.groupby(key):
        arr = g[["enabled", "start", "activity", "case_age", "progress", "uid"]].to_numpy()
        for i in range(len(arr)):
            s_i = arr[i][1]
            if not (arr[i][0] <= s_i + 1e-9):
                continue
            cand = [j for j in range(len(arr)) if arr[j][0] <= s_i + 1e-9 and arr[j][1] >= s_i]
            if len(cand) < 2:
                continue
            pts.append({"group": k, "chosen": arr[i][5],
                        "cands": [{"uid": arr[j][5], "enabled": arr[j][0], "activity": arr[j][2],
                                   "case_age": arr[j][3], "progress": arr[j][4]} for j in cand]})
    return pts


def _pick(cands: list[dict], keyf: Callable[[dict], Any]) -> set:
    best = min(keyf(c) for c in cands)
    return {c["uid"] for c in cands if keyf(c) == best}


def _priority_order(pts: list[dict]) -> tuple[list[str], Counter]:
    """Copeland order of activities from pairwise 'chosen over waiting' counts."""
    wins: Counter = Counter()
    acts: set = set()
    for p in pts:
        ch = next(c for c in p["cands"] if c["uid"] == p["chosen"])
        for c in p["cands"]:
            acts.add(c["activity"])
            if c["uid"] != p["chosen"] and c["activity"] != ch["activity"]:
                wins[(ch["activity"], c["activity"])] += 1
    score = {a: 0.0 for a in acts}
    for a in acts:
        for b in acts:
            if a < b:
                ab, ba = wins[(a, b)], wins[(b, a)]
                if ab > ba:
                    score[a] += 1; score[b] -= 1
                elif ba > ab:
                    score[b] += 1; score[a] -= 1
    return sorted(acts, key=lambda a: (-score[a], a)), wins


def test_dispatching_rules(inst: pd.DataFrame, by: Literal["resource", "resource_class"] = "resource",
                           top_k: int = 8) -> dict[str, Any]:
    """Score candidate queue disciplines against the observed service order.

    Decision point: a service start on a server (``by='resource'``) or pool
    (``by='resource_class'``) while at least one other step was already enabled
    and still waiting there. Rules (agreement = observed choice is among the
    rule's picks, ties split fractionally):
    FIFO (earliest enabled), LIFO, case_age (earliest case release first),
    most_progressed (most completed steps in its case), activity_priority
    (activity ranking learned from pairwise overtaking; scored leave-one-out).
    """
    d = inst.dropna(subset=["enabled", "start"]).copy().sort_values("start").reset_index(drop=True)
    d["uid"] = np.arange(len(d))
    rel = inst["enabled"].fillna(inst["start"]).groupby(inst["case_id"]).min()
    d["case_age"] = d["case_id"].map(rel)
    d["progress"] = d.groupby("case_id").cumcount()
    d["rclass"] = resource_class(d["resource"])
    pts = _decision_points(d, "resource" if by == "resource" else "rclass")
    cls_of = dict(zip(d["uid"], d["rclass"]))

    rules: dict[str, Callable[[dict], Any]] = {
        "FIFO": lambda c: c["enabled"], "LIFO": lambda c: -c["enabled"],
        "case_age": lambda c: c["case_age"], "most_progressed": lambda c: -c["progress"],
    }
    res: dict[str, Any] = {}
    for rc in sorted({cls_of[p["chosen"]] for p in pts}):
        P = [p for p in pts if cls_of[p["chosen"]] == rc]
        score = {}
        for name, f in rules.items():
            score[name] = np.mean([(p["chosen"] in (s := _pick(p["cands"], f))) / len(s) for p in P])
        order, wins = _priority_order(P)
        loo = []
        for i, p in enumerate(P):
            o_i, _ = _priority_order(P[:i] + P[i + 1:])
            rank = {a: j for j, a in enumerate(o_i)}
            s = _pick(p["cands"], lambda c: (rank.get(c["activity"], len(rank)), c["enabled"]))
            loo.append((p["chosen"] in s) / len(s))
        score["activity_priority"] = float(np.mean(loo))
        acts_present = {c["activity"] for p in P for c in p["cands"]}
        mixed = sum(len({c["activity"] for c in p["cands"]}) > 1 for p in P)
        best = max(score, key=lambda k: (round(score[k], 6), k == "FIFO"))
        equivalent = [k for k in score if k != best and score[best] - score[k] <= 0.03]
        res[rc] = {
            "n_decision_points": len(P), "n_mixed_activity_points": int(mixed),
            "agreement": {k: _r(v, 3) for k, v in score.items()},
            "best_rule": best,
            "equivalent_rules": equivalent,
            "fifo_rejected": bool(score[best] - score["FIFO"] >= 0.1 and len(P) >= 5),
            "learned_activity_priority": order if len(acts_present) > 1 else [],
            "top_overtakes": [{"chosen": a, "over_waiting": b, "count": n} for (a, b), n in wins.most_common(top_k)],
        }
    findings = []
    for k, v in res.items():
        if v["fifo_rejected"]:
            findings.append(
                f"{k}: FIFO rejected - best rule {v['best_rule']} ({v['agreement'][v['best_rule']]:.0%}"
                + (f", equivalent: {', '.join(v['equivalent_rules'])}" if v["equivalent_rules"] else "")
                + f") vs FIFO ({v['agreement']['FIFO']:.0%}) over {v['n_decision_points']} decisions. Model a "
                f"priority queue (simpy.PriorityResource) for {k}"
                + (f" with activity order {v['learned_activity_priority']}." if v["learned_activity_priority"] else "."))
        else:
            findings.append(f"{k}: FIFO consistent ({v['agreement']['FIFO']:.0%} over {v['n_decision_points']} decisions).")
    return {"by": by, "n_decision_points": len(pts), "by_resource_class": res, "findings": findings,
            "note": "activity_priority agreement is leave-one-out; FIFO wins ties."}


# =============================================================================
# 4. Release control
# =============================================================================

def detect_release_control(inst: pd.DataFrame, T: float, first_activity: str | None = None,
                           deltas: tuple[float, ...] = (5.0, 30.0)) -> dict[str, Any]:
    """Examine how cases are released into the system.

    Release = first enabled (else start) time of a case. Reports WIP at each
    release, max WIP, release spacing (with burst/gap decomposition), and the
    share of releases happening within ``deltas`` seconds after a case finished
    (lift vs. chance) as evidence of completion-triggered / CONWIP release.
    """
    d = inst.copy()
    d["rel"] = d["enabled"].fillna(d["start"])
    if first_activity:
        d = d[d["case_id"].isin(d.loc[d["activity"] == first_activity, "case_id"])]
    c = d.groupby("case_id").agg(release=("rel", "min"), finish=("end", "max")).sort_values("release")
    rel, fin = c["release"].to_numpy(), c["finish"].to_numpy()
    wip_at = np.array([int(((rel < r) & (fin > r)).sum()) for r in rel])
    grid = np.linspace(0, T, 2000)
    wip_t = np.array([int(((rel <= t) & (fin > t)).sum()) for t in grid])
    max_wip = int(wip_t.max()) if len(wip_t) else 0

    fins_in = np.sort(fin[fin < T - 1])
    trig = {}
    for dl in deltas:
        hit = [bool(((r - fins_in >= 0) & (r - fins_in <= dl)).any()) for r in rel]
        rate = len(fins_in) / T if T > 0 else 0
        p0 = 1 - np.exp(-rate * dl)
        frac = float(np.mean(hit)) if len(hit) else 0.0
        trig[f"within_{int(dl)}s"] = {"share": _r(frac), "chance": _r(p0), "lift": _r(frac / p0) if p0 > 0 else None}

    arr = two_regime_iat(np.diff(rel))
    # WIP level reached right after each release burst (is the burst filling up to a cap?)
    post_burst = []
    if arr.get("regime") == "two_regime":
        thr = arr["threshold_s"]
        gaps = np.diff(rel)
        ends = [i for i in range(len(rel)) if i == len(rel) - 1 or gaps[i] > thr]
        post_burst = [int(wip_at[i] + 1) for i in ends]

    t30 = trig.get("within_30s", {})
    share_at_max = float(np.mean(wip_t >= max_wip)) if max_wip else 0.0
    if t30.get("lift") and t30["lift"] >= 2 and t30["share"] >= 0.5:
        verdict = "completion_triggered"
    elif post_burst and len(post_burst) >= 3 and np.std(post_burst) <= 1.0 and max_wip >= 3:
        verdict = f"wip_cap({int(round(np.median(post_burst)))})"
    elif arr.get("regime") == "two_regime":
        verdict = "open (bursty releases)"
    else:
        verdict = "open (no control detected)"
    return {
        "n_releases": int(len(rel)),
        "max_wip": max_wip,
        "time_avg_wip": _r(float(wip_t.mean()), 2),
        "share_time_at_max_wip": _r(share_at_max),
        "wip_at_release": _stats(wip_at),
        "release_spacing": arr,
        "wip_after_each_release_burst": post_burst,
        "completion_triggered_release": trig,
        "verdict": verdict,
        "guidance": ("If verdict is completion_triggered or wip_cap(k), model a release controller "
                     "(e.g. release a new order when WIP < k) instead of an open arrival stream; "
                     "if releases come in bursts, use the burst/gap parameters, not the mixed mean IAT."),
    }


# =============================================================================
# 5. Intra-case concurrency
# =============================================================================

def detect_intra_case_concurrency(inst: pd.DataFrame, completed_cases: list[str] | None = None,
                                  top_k: int = 8) -> dict[str, Any]:
    """Detect steps of the same case that run in parallel.

    A step overlaps when it starts more than 0.5 s before the previous step of
    the case (in start order) ends — the definition of evaluate_v2's
    ``overlapping_steps_per_case``. If ``completed_cases`` is given, the
    per-case figure is also reported over those cases (comparable to evaluate_v2).
    """
    d = inst.sort_values(["case_id", "start"]).copy()
    g = d.groupby("case_id")
    d["prev_end"] = g["end"].shift()
    d["prev_act"] = g["activity"].shift()
    d["ov"] = (d["start"] - d["prev_end"]) < -OVERLAP_TOL_S
    d["ov_s"] = (d["prev_end"] - d["start"]).clip(lower=0).where(d["ov"], 0.0)
    per_case = d.groupby("case_id")["ov"].sum()
    pairs = (d[d["ov"]].groupby(["prev_act", "activity"])["ov_s"].agg(["size", "mean"])
             .sort_values("size", ascending=False).head(top_k))
    out = {
        "overlapping_steps_per_case_all": _r(float(per_case.mean()), 3),
        "share_cases_with_overlap": _r(float((per_case > 0).mean()), 3),
        "share_steps_overlapping": _r(float(d["ov"].mean()), 3),
        "top_overlapping_pairs": [{"previous": a, "next": b, "count": int(r["size"]), "mean_overlap_s": _r(r["mean"], 1)}
                                  for (a, b), r in pairs.iterrows()],
    }
    if completed_cases is not None:
        pc = per_case[per_case.index.isin(completed_cases)]
        out["overlapping_steps_per_completed_case"] = _r(float(pc.mean()), 3) if len(pc) else None
    out["guidance"] = ("If overlap is material (> ~0.3 steps per case), the next step of a case is "
                       "requested before the previous one releases its resource (e.g. a transporter "
                       "is called while the machine still works). Model these steps as concurrent "
                       "SimPy processes (or request the next resource before releasing the current one), "
                       "not as a strictly sequential chain.") if out["share_steps_overlapping"] else \
        "No intra-case concurrency: a sequential step chain is adequate."
    return out


# =============================================================================
# Tool factories
# =============================================================================

# Module-level aliases: the tool functions below reuse these names.
_censoring, _waiting, _dispatching = detect_censoring, decompose_waiting_times, test_dispatching_rules
_release, _concurrency = detect_release_control, detect_intra_case_concurrency


def _dump(evidence_dir: str, name: str, result: dict) -> str:
    os.makedirs(os.path.join(os.getcwd(), evidence_dir), exist_ok=True)
    rel = os.path.join(evidence_dir, f"{name}.json")
    with open(os.path.join(os.getcwd(), rel), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    return rel


def make_set_log_schema_tool(df: pd.DataFrame, on_confirm: Callable[[dict, dict], None]):
    """Return the ``set_log_schema`` tool; ``on_confirm(schema, meta)`` persists it (e.g. into the spec)."""

    @tool
    def set_log_schema(
        case_col: str,
        activity_col: str,
        resource_col: str,
        start_col: str,
        end_col: str | None = None,
        variant_col: str | None = None,
        lifecycle_col: str | None = None,
        instance_col: str | None = None,
        enabled_value: str | None = None,
        start_value: str | None = None,
        complete_value: str | None = None,
        state_col: str | None = None,
        success_values: list[str] | None = None,
        failure_values: list[str] | None = None,
    ) -> dict[str, Any]:
        """Confirm how the raw event log maps to activity instances (case, activity, resource, times).

        All discovery tools (censoring, waiting-time causes, dispatching rules, release
        control, concurrency) and the behavioural verifier read the log through this
        schema, so call it once the column roles are confirmed. Two layouts:

        * lifecycle layout — one row per lifecycle transition: set lifecycle_col,
          instance_col (links the rows of one activity instance), start_value (e.g.
          'start'), enabled_value (row marking queue entry / request, e.g. 'scheduled')
          and complete_value (e.g. 'complete', whose state_col gives success/failure).
        * flat layout — one row per activity instance: set start_col and end_col only.

        Args:
            case_col: Case / work-piece id column.
            activity_col: Activity name column.
            resource_col: Executing resource column.
            start_col: Timestamp column of the service start.
            end_col: Timestamp column of the service end (None: use the complete row's start_col).
            variant_col: Product variant / process model column, if any.
            lifecycle_col: Lifecycle transition column (lifecycle layout).
            instance_col: Column linking the lifecycle rows of one activity instance.
            enabled_value: Lifecycle value of the request / queue-entry row.
            start_value: Lifecycle value of the service-start row.
            complete_value: Lifecycle value of the completion row.
            state_col: Outcome column (e.g. success/failure).
            success_values: Outcome values meaning success (default ['success']).
            failure_values: Outcome values meaning failure (default ['failure']).
        """
        args = {k: v for k, v in dict(
            case_col=case_col, activity_col=activity_col, resource_col=resource_col, start_col=start_col,
            end_col=end_col, variant_col=variant_col, lifecycle_col=lifecycle_col, instance_col=instance_col,
            enabled_value=enabled_value, start_value=start_value, complete_value=complete_value,
            state_col=state_col, success_values=success_values, failure_values=failure_values).items()
            if v is not None}
        try:
            schema = LogSchema(**args)
            inst, meta = build_instances(df, schema)
        except Exception as exc:
            return {"error": f"{type(exc).__name__}: {exc}"}
        warnings = []
        if meta["instances"] == 0:
            return {"error": "Schema produced no activity instances; check start_value / columns.", "meta": meta}
        if meta["enabled_observed_frac"] == 0:
            warnings.append("No enabled/request time: waiting-time decomposition and dispatching-rule "
                            "tests are unavailable (they need the queue-entry time).")
        elif meta["enabled_observed_frac"] < 0.9:
            warnings.append(f"Only {meta['enabled_observed_frac']:.0%} of instances have an enabled time.")
        if meta["end_missing"]:
            warnings.append(f"{meta['end_missing']} instances have no end time.")
        states = inst["state"].value_counts().to_dict()
        if set(states) - {"success", "failure"}:
            warnings.append(f"Unmapped outcome values {sorted(set(states) - {'success', 'failure'})}; "
                            f"extend success_values / failure_values.")
        schema_dict = schema.model_dump(exclude_none=True)
        on_confirm(schema_dict, meta)
        sample = inst.head(5).copy()
        for col in ("enabled", "start", "end"):
            sample[col] = sample[col].round(2)
        return {"status": "log schema confirmed and stored", "meta": meta, "state_counts": states,
                "warnings": warnings, "sample_instances": sample.to_dict(orient="records")}

    return set_log_schema


def make_discovery_tools(df: pd.DataFrame, schema_provider: Callable[[], dict | None], evidence_dir: str) -> list:
    """Return the deterministic discovery tools bound to ``df`` and the confirmed log schema."""

    _cache: dict[str, Any] = {}

    def _inst() -> tuple[pd.DataFrame, dict] | str:
        schema = schema_provider()
        if not schema:
            return ("ERROR: the log schema is not confirmed yet. The data analysis phase must call "
                    "`set_log_schema` first (it maps case / activity / resource / timestamp columns).")
        key = json.dumps(schema, sort_keys=True)
        if _cache.get("key") != key:
            _cache["key"], _cache["val"] = key, build_instances(df, schema)
        return _cache["val"]

    def _run(name: str, fn: Callable[[pd.DataFrame, dict], dict]) -> dict | str:
        got = _inst()
        if isinstance(got, str):
            return got
        inst, meta = got
        try:
            result = fn(inst, meta)
        except Exception as exc:
            return {"error": f"{type(exc).__name__}: {exc}"}
        result["evidence_file"] = _dump(evidence_dir, name, result)
        return result

    @tool
    def detect_censoring(terminal_activity: str | None = None, first_activity: str | None = None) -> dict | str:
        """Find cases cut by the observation window and the initial WIP at window start.

        Classifies cases as complete / right-censored (cut by the window end) /
        left-censored (started before the window) / incomplete_interior, infers the
        typical first and terminal activity, compares the variant mix and per-variant
        step presence on complete cases vs all cases (truncation makes always-present
        steps look optional), and states which estimates must use complete cases only.

        Args:
            terminal_activity: Activity that marks case completion (inferred if omitted).
            first_activity: Activity that marks case start (inferred if omitted).
        """
        return _run("detect_censoring", lambda i, m: _censoring(
            i, m["T"], terminal_activity=terminal_activity, first_activity=first_activity))

    @tool
    def decompose_waiting_times() -> dict | str:
        """Split waiting time (enabled -> start) per activity and resource class into causes.

        contention = resource busy with earlier-enabled cases (FIFO queueing);
        prioritization = resource busy with LATER-enabled cases that overtook (non-FIFO
        queue discipline); extraneous = resource idle while the case waited (hand-off,
        transport, release control). A high prioritization share means the queue is not
        FIFO; follow up with test_dispatching_rules.
        """
        return _run("decompose_waiting_times", lambda i, m: _waiting(i))

    @tool
    def test_dispatching_rules(group_by: Literal["resource", "resource_class"] = "resource") -> dict | str:
        """Test which queue discipline explains the observed service order per resource class.

        At every service start where other steps were waiting, compares the observed
        choice with FIFO, LIFO, case_age (oldest case first), most_progressed (case with
        most completed steps first) and a learned activity_priority rule (pairwise
        overtaking between activities, scored leave-one-out). Returns agreement rates,
        the best rule, whether FIFO is rejected, and the learned activity priority order
        to implement with simpy.PriorityResource.

        Args:
            group_by: 'resource' treats every concrete resource as its own queue
                      (default); 'resource_class' pools resources of one class.
        """
        return _run("test_dispatching_rules", lambda i, m: _dispatching(i, by=group_by))

    @tool
    def detect_release_control(first_activity: str | None = None) -> dict | str:
        """Analyse how new cases are released: WIP at release, release bursts, completion-triggered release.

        Returns max / time-averaged WIP, WIP at each release, release spacing with a
        burst/gap decomposition, the share of releases within 5 s / 30 s after a case
        finished (with lift over chance), and a verdict: completion_triggered,
        wip_cap(k), open (bursty releases) or open (no control detected).

        Args:
            first_activity: Restrict to cases that contain this release activity (optional).
        """
        return _run("detect_release_control", lambda i, m: _release(i, m["T"], first_activity))

    @tool
    def detect_intra_case_concurrency(terminal_activity: str | None = None) -> dict | str:
        """Detect steps of the same case that overlap in time (intra-case parallelism).

        Reports overlapping steps per case (all cases and completed cases), the share of
        cases / steps with overlap and the activity pairs that overlap most. Material
        overlap means the model must not be a strictly sequential step chain.

        Args:
            terminal_activity: Activity marking completion, used for the completed-case
                               figure (inferred if omitted).
        """
        def fn(i: pd.DataFrame, m: dict) -> dict:
            cen = _censoring(i, m["T"], terminal_activity=terminal_activity)
            term = cen["inferred_terminal_activity"]
            done = i.loc[(i["activity"] == term) & (i["state"] == "success"), "case_id"].unique().tolist()
            return _concurrency(i, completed_cases=done)
        return _run("detect_intra_case_concurrency", fn)

    return [detect_censoring, decompose_waiting_times, test_dispatching_rules,
            detect_release_control, detect_intra_case_concurrency]
