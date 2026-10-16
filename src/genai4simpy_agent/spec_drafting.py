"""Deterministic spec drafting from discovery evidence.

Writing a 9-variant routing table or 20 fitted distributions as one tool call is
thousands of tokens of transcription — slow on a local model and a source of
copy errors. These functions build the large spec sections directly from the
deterministic tool results; the LLM only makes the modelling DECISIONS
(which overlaps are real concurrency, which resource classes use priority
queues, whether early exits are modelled) and reviews the result.

Shared by the agent tools and by analysis/deterministic_baseline.py.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.data_extraction_tools import discovery as D
from src.data_extraction_tools.eventlog import build_instances, resource_class
from src.data_extraction_tools.routing import discover_routings
from src.data_extraction_tools.tools import _arrival_distributions, _spec_dist, fit_numeric_series


def default_concurrent_pairs(conc: dict[str, Any], n_cases: int, min_share: float = 0.2) -> list[list[str]]:
    """Overlapping (previous, next) activity pairs seen in at least ``min_share`` of the cases."""
    return [[p["previous"], p["next"]] for p in conc.get("top_overlapping_pairs", [])
            if p["count"] >= min_share * n_cases]


def topology_sections(inst: pd.DataFrame, T: float, t0: str,
                      concurrent_pairs: list[list[str]] | None = None,
                      priority_classes: list[str] | None = None,
                      include_early_exits: bool = True) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (spec sections, decisions used) for window, resources, variants,
    control_policies and initial_state. ``None`` arguments use the evidence defaults."""
    cens = D.detect_censoring(inst, T)
    term, first = cens["inferred_terminal_activity"], cens["inferred_first_activity"]
    censored = set(cens["left_censored"]) | set(cens["right_censored"])
    routes = discover_routings(inst, term, censored)
    conc = D.detect_intra_case_concurrency(inst)
    disp = D.test_dispatching_rules(inst)
    rel = D.detect_release_control(inst, T)

    if concurrent_pairs is None:
        concurrent_pairs = default_concurrent_pairs(conc, inst["case_id"].nunique())
    pairs = {tuple(p) for p in concurrent_pairs}
    by_cls = disp.get("by_resource_class", {})
    if priority_classes is None:
        priority_classes = [c for c, r in by_cls.items() if r.get("fifo_rejected") and r.get("learned_activity_priority")]

    resources = {r: {"name": r, "resource_class": c, "capacity": 1}
                 for r, c in zip(inst["resource"], resource_class(inst["resource"]))}
    variants = []
    for name, v in routes["variants"].items():
        seq = v["main_sequence"]
        steps = []
        for i, a in enumerate(seq):
            st = {"activity": a, "resources": v["resources_by_step"][i] or None}
            if i > 0 and (seq[i - 1], a) in pairs:
                st["concurrent_with_previous"] = True
            steps.append(st)
        ent = {"name": name, "probability": v["share_of_released"], "steps": steps}
        if include_early_exits and v.get("early_exit_after_n_steps"):
            ent.update(early_exit_probability=v["early_exit_probability"],
                       early_exit_after_n_steps=v["early_exit_after_n_steps"],
                       early_exit_after={k.rsplit(" (", 1)[0]: round(c / max(1, sum(v["early_exit_points"].values())), 3)
                                         for k, c in v["early_exit_points"].items()})
        variants.append(ent)

    control = {
        "queue_discipline": {c: ("priority" if c in priority_classes else "fifo") for c in by_cls},
        "priority_order": {c: by_cls[c]["learned_activity_priority"] for c in priority_classes if c in by_cls},
        "release_rule": rel.get("verdict"),
        "intra_case_concurrency": ("; ".join(f"{a} || {b}" for a, b in sorted(pairs)) or "none"),
        "evidence": {
            **{f"{c}_fifo_agreement": r["agreement"].get("FIFO") for c, r in by_cls.items()},
            **{f"{c}_best_rule": r.get("best_rule") for c, r in by_cls.items()},
            "overlapping_steps_per_completed_case": conc.get("overlapping_steps_per_completed_case"),
        },
    }
    sections = {
        "window": {"t0": t0, "horizon_s": T, "terminal_activity": term, "first_activity": first},
        "resources": sorted(resources.values(), key=lambda r: r["name"]),
        "variants": variants,
        "control_policies": control,
        "initial_state": {"wip_at_start": cens["initial_wip_at_window_start"]["count"],
                          "excluded_from_estimation": sorted(censored)},
    }
    decisions = {"concurrent_pairs": sorted(map(list, pairs)), "priority_classes": priority_classes,
                 "include_early_exits": include_early_exits}
    return sections, decisions


def activities_section(inst: pd.DataFrame, exclude_case_ids: set[str] | None = None) -> list[dict[str, Any]]:
    """Activities with fitted service-time distributions and failure probabilities."""
    data = inst if not exclude_case_ids else inst[~inst["case_id"].isin(exclude_case_ids)]
    attempts = data.groupby("activity").size()
    fails = data[data["state"] == "failure"].groupby("activity").size()
    ok = data[data["state"] == "success"]
    out = []
    for a, g in ok.groupby("activity"):
        fit = fit_numeric_series(g["end"] - g["start"], label=a)
        out.append({"name": a, "eligible_resources": sorted(g["resource"].unique()),
                    "duration": _spec_dist(fit, "fit_activity_durations"),
                    "failure_probability": round(float(fails.get(a, 0) / attempts[a]), 4),
                    "on_failure": "retry"})
    return out


def arrivals_section(inst: pd.DataFrame, exclude_case_ids: set[str] | None = None,
                     model: str | None = None) -> dict[str, Any]:
    """Arrival model from case release times (first enabled / start time per case)."""
    rel = inst.groupby("case_id")["enabled"].min().fillna(inst.groupby("case_id")["start"].min())
    if exclude_case_ids:
        rel = rel[~rel.index.isin(exclude_case_ids)]
    iat = np.diff(rel.sort_values().to_numpy())
    reg = D.two_regime_iat(iat)
    rec = _arrival_distributions(iat, reg)
    model = model or ("two_regime_bursts" if reg.get("regime") == "two_regime" else "renewal")
    if model == "two_regime_bursts":
        return {"model": model, "burst_size": rec["burst_size"], "intra_burst_iat": rec["intra_burst_iat"],
                "inter_burst_gap": rec["inter_burst_gap"]}
    return {"model": "renewal", "interarrival": rec["interarrival"]}


# ---------------------------------------------------------------------------
# Tool factories
# ---------------------------------------------------------------------------

def make_drafting_tools(df: pd.DataFrame, store, schema_provider, agent_name: str) -> list:
    """Return the drafting tools an agent may use, according to its spec sections."""
    from langchain_core.tools import tool

    from src.genai4simpy_agent.spec import SECTION_OWNERS, _cross_check, render_spec_markdown  # noqa: F401

    owned = set(SECTION_OWNERS.get(agent_name, []))

    def _inst():
        schema = schema_provider()
        if not schema:
            raise RuntimeError("No confirmed log schema (set_log_schema must run first).")
        return build_instances(df, schema)

    def _excluded() -> set[str]:
        return set((store.get("initial_state") or {}).get("excluded_from_estimation", []))

    tools = []
    if {"variants", "resources", "control_policies"} <= owned:
        @tool
        def draft_topology_spec(concurrent_pairs: list[list[str]] | None = None,
                                priority_classes: list[str] | None = None,
                                include_early_exits: bool = True) -> dict:
            """
            Write spec sections window, resources, variants, control_policies and
            initial_state deterministically from the discovery evidence (censoring,
            routings incl. per-step resources and early exits, dispatching rules,
            release control, concurrency). You only decide:

            Args:
                concurrent_pairs: [previous_activity, next_activity] pairs to model as
                    intra-case concurrency (next step starts before previous ends).
                    None = pairs that overlap in >= 20 % of the cases.
                priority_classes: resource classes served by activity priority instead of
                    FIFO. None = classes where test_dispatching_rules rejected FIFO.
                include_early_exits: model cases stopping mid-process (default True).

            Returns a compact summary. Review it; correct single entries afterwards with
            write_spec_section(section, content, merge=True).
            """
            try:
                inst, meta = _inst()
                secs, dec = topology_sections(inst, meta["T"], meta["t0"], concurrent_pairs,
                                              priority_classes, include_early_exits)
                for sec, val in secs.items():
                    store.put(sec, val, author=agent_name + " (draft_topology_spec)")
            except Exception as exc:
                return {"error": f"{type(exc).__name__}: {exc}"}
            return {
                "written": list(secs), "decisions": dec,
                "resources": len(secs["resources"]),
                "variants": [{"name": v["name"], "p": v["probability"], "steps": len(v["steps"]),
                              "concurrent_steps": sum(bool(s.get("concurrent_with_previous")) for s in v["steps"]),
                              "early_exit_p": v.get("early_exit_probability", 0)} for v in secs["variants"]],
                "control_policies": {k: secs["control_policies"][k] for k in ("queue_discipline", "priority_order", "release_rule")},
                "initial_state": {"wip_at_start": secs["initial_state"]["wip_at_start"],
                                  "excluded_cases": len(secs["initial_state"]["excluded_from_estimation"])},
                "warnings": _cross_check(store.load()),
                "review_file": store.rel_path[:-5] + ".md",
            }
        tools.append(draft_topology_spec)

    if "activities" in owned:
        @tool
        def draft_activities_spec() -> dict:
            """
            Write spec section `activities` deterministically: one entry per activity with
            its eligible resources, the recommended service-time distribution from the
            fitting gate (parametric only if it passes moments/tail/bootstrap-KS, else the
            empirical quantile table), failure probability (failed / all attempts) and
            on_failure='retry'. Censored cases (initial_state.excluded_from_estimation) are
            excluded. Returns a compact summary; correct single activities afterwards with
            write_spec_section("activities", [...], merge=True).
            """
            try:
                inst, _ = _inst()
                acts = activities_section(inst, _excluded())
                store.put("activities", acts, author=agent_name + " (draft_activities_spec)")
            except Exception as exc:
                return {"error": f"{type(exc).__name__}: {exc}"}
            return {"written": "activities",
                    "activities": [{"name": a["name"], "family": a["duration"]["family"], "mean": a["duration"]["mean"],
                                    "n": a["duration"]["n"], "p_fail": a["failure_probability"]} for a in acts],
                    "warnings": _cross_check(store.load())}
        tools.append(draft_activities_spec)

    if "arrivals" in owned:
        @tool
        def draft_arrivals_spec(model: str | None = None) -> dict:
            """
            Write spec section `arrivals` deterministically from the case release times
            (first request per case; censored cases excluded).

            Args:
                model: 'two_regime_bursts' or 'renewal'. None = two_regime_bursts when the
                       burst/gap decomposition finds two regimes, else renewal.
            """
            try:
                inst, _ = _inst()
                arr = arrivals_section(inst, _excluded(), model)
                store.put("arrivals", arr, author=agent_name + " (draft_arrivals_spec)")
            except Exception as exc:
                return {"error": f"{type(exc).__name__}: {exc}"}
            return {"written": "arrivals", "model": arr["model"],
                    "means": {k: v.get("mean") for k, v in arr.items() if isinstance(v, dict)}}
        tools.append(draft_arrivals_spec)
    return tools


# ---------------------------------------------------------------------------
# Spec vs evidence: make every deviation from the discovery results explicit
# ---------------------------------------------------------------------------

def spec_evidence_deviations(spec: dict[str, Any], evidence_dir: str) -> list[str]:
    """List places where the spec deviates from the deterministic discovery evidence.

    A deviation is not necessarily wrong (a user or context file may know better), but it
    must be a conscious, logged decision — never a silent override."""
    import json
    import os

    def ev(name):
        p = os.path.join(os.getcwd(), evidence_dir, f"{name}.json")
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

    out: list[str] = []
    routes, disp, conc, cens = (ev("discover_variant_routings"), ev("test_dispatching_rules"),
                                ev("detect_intra_case_concurrency"), ev("detect_censoring"))
    variants = {v["name"]: v for v in spec.get("variants", [])}
    if routes:
        for name, r in routes.get("variants", {}).items():
            v = variants.get(name)
            if v is None:
                out.append(f"variant {name} ({r['cases']} cases) observed but missing from the spec")
                continue
            if abs(v.get("early_exit_probability", 0) - r["early_exit_probability"]) > 0.15:
                out.append(f"variant {name}: spec early_exit_probability {v.get('early_exit_probability', 0):.2f} vs "
                           f"observed {r['early_exit_probability']:.2f} ({r['cases'] - r['completed']} of {r['cases']} "
                           f"cases stop mid-process inside the window — not censored)")
            if abs(v.get("probability", 0) - r["share_of_released"]) > 0.1:
                out.append(f"variant {name}: spec probability {v.get('probability', 0):.2f} vs observed share "
                           f"{r['share_of_released']:.2f}")
    if cens:
        n_int = len(cens.get("incomplete_interior", []))
        if n_int and all(v.get("early_exit_probability", 0) == 0 for v in variants.values()):
            out.append(f"no early exits in the spec, but {n_int} of {cens['n_cases']} cases end inside the window "
                       f"without the terminal activity; attributing this to window truncation contradicts "
                       f"detect_censoring (right-censored: {len(cens.get('right_censored', []))})")
    cp = spec.get("control_policies", {}) or {}
    qd = cp.get("queue_discipline", {}) or {}
    if disp:
        for cls, r in disp.get("by_resource_class", {}).items():
            if r.get("fifo_rejected") and qd.get(cls) != "priority":
                out.append(f"{cls}: FIFO rejected by the data (FIFO agreement {r['agreement'].get('FIFO')}, best "
                           f"{r.get('best_rule')} {r['agreement'].get(r.get('best_rule'))}) but spec queue_discipline is "
                           f"{qd.get(cls, 'unset')}")
            if not r.get("fifo_rejected") and qd.get(cls) == "priority":
                out.append(f"{cls}: spec uses priority although FIFO is consistent with the data")
    arr, win = spec.get("arrivals") or {}, spec.get("window") or {}
    if cens and arr and win.get("horizon_s"):
        implied = implied_arrivals(arr, float(win["horizon_s"]))
        observed = cens.get("n_cases")
        if implied and observed and abs(implied - observed) / observed > 0.25:
            out.append(f"arrivals: the spec implies ~{implied:.0f} released cases over the window, observed "
                       f"{observed} ({(implied / observed - 1) * 100:+.0f}%) — check gap / burst parameters")
    if conc:
        n_conc = sum(bool(s.get("concurrent_with_previous")) for v in variants.values() for s in v.get("steps", []))
        obs = conc.get("overlapping_steps_per_completed_case") or 0
        if obs > 0.3 and n_conc == 0:
            out.append(f"observed {obs:.2f} overlapping steps per completed case, but no step is concurrent_with_previous")
    return out


def _dist_mean(d: dict | None) -> float | None:
    if not d:
        return None
    if d.get("mean") is not None:
        return float(d["mean"])
    fam, p = d.get("family"), d.get("params", {})
    if fam == "constant":
        return float(p["value"])
    if fam == "categorical":
        return float(np.dot(d["values"], d["probs"]))
    if fam == "empirical_quantiles":
        return float(np.trapezoid(d["quantiles"], d["quantile_probs"]))
    try:
        from scipy import stats
        return float(getattr(stats, fam)(**p).mean())
    except Exception:
        return None


def implied_arrivals(arr: dict, horizon: float) -> float | None:
    """Expected number of released cases over ``horizon`` under the spec's arrival model."""
    init = _dist_mean(arr.get("initial_burst")) or 0.0
    if arr.get("model") in ("two_regime_bursts", "batch"):
        b, g, i = _dist_mean(arr.get("burst_size")), _dist_mean(arr.get("inter_burst_gap")), _dist_mean(arr.get("intra_burst_iat")) or 0.0
        if not b or not g:
            return None
        return init + b * horizon / (g + (b - 1) * i)
    m = _dist_mean(arr.get("interarrival"))
    return init + horizon / m if m else None


def make_deviation_tool(store, evidence_dir: str):
    from langchain_core.tools import tool

    @tool
    def check_spec_against_evidence() -> dict:
        """
        List every place where the simulation spec deviates from the deterministic discovery
        evidence (early exits, variant shares, queue disciplines, concurrency). Each deviation
        must be either corrected or justified (user / context file) and logged as a decision.
        Use it to explain behavioural KPI gaps: a gap caused by a deviation is a spec decision,
        not an implementation error and not 'window truncation'.
        """
        return {"deviations": spec_evidence_deviations(store.load(), evidence_dir)}

    return check_spec_against_evidence
