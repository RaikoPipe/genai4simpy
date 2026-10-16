"""Deterministic routing discovery per variant.

Main sequences and step presence come from COMPLETE cases (reached the terminal
activity); early exits (cases that stop mid-process well inside the window)
come from uncensored incomplete cases. Cases overlapping the window edges
(censored) are excluded from both.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from typing import Any, Callable

import pandas as pd
from langchain_core.tools import tool

from src.data_extraction_tools.eventlog import build_instances


def discover_routings(inst: pd.DataFrame, terminal_activity: str,
                      censored_ids: set[str] | None = None, top_k: int = 3) -> dict[str, Any]:
    """Per variant: shares, main step sequence, alternatives, step presence, resources
    per activity and early-exit points (last step of cases that stopped mid-process)."""
    data = inst if not censored_ids else inst[~inst["case_id"].isin(censored_ids)]
    data = data.sort_values(["case_id", "start"])
    done = set(data.loc[(data["activity"] == terminal_activity) & (data["state"] == "success"), "case_id"])
    ok = data[data["state"] == "success"]
    seqs = ok.groupby("case_id")["activity"].apply(tuple)
    variant_of = data.groupby("case_id")["variant"].first()
    last = data.groupby("case_id").agg(last=("activity", "last"), state=("state", "last"))
    n_all = len(variant_of)
    out: dict[str, Any] = {
        "terminal_activity": terminal_activity,
        "cases_used": n_all, "complete_cases": len(done), "censored_excluded": len(censored_ids or ()),
        "variants": {},
    }
    for v, ids in variant_of.groupby(variant_of).groups.items():
        ids = list(ids)
        comp = [i for i in ids if i in done]
        inc = [i for i in ids if i not in done]
        cs = seqs.reindex(comp).dropna()
        cnt = Counter(cs)
        presence = Counter(a for s in cs for a in set(s))
        vok = ok[ok["case_id"].isin(ids)]
        exits = Counter(f"{r.last} ({r.state})" for r in last.loc[inc].itertuples())
        n_done = Counter(len(seqs.get(i, ())) for i in inc)
        entry = {
            "cases": len(ids),
            "share_of_released": round(len(ids) / n_all, 4) if n_all else 0.0,
            "completed": len(comp),
            "early_exit_probability": round(len(inc) / len(ids), 3),
            "early_exit_points": dict(exits.most_common(5)),
            "early_exit_after_n_steps": {str(k): round(c / len(inc), 3) for k, c in sorted(n_done.items())} if inc else {},
            "failed_attempts": int(((data["case_id"].isin(ids)) & (data["state"] == "failure")).sum()),
        }
        if cnt:
            main = cnt.most_common(1)[0][0]
            entry.update(
                main_sequence=list(main), main_sequence_share=round(cnt[main] / len(cs), 3),
                resources_by_step=_resources_by_position(main, vok),
                other_sequences=[{"sequence": list(s), "cases": c} for s, c in cnt.most_common(top_k)[1:]],
                step_presence_complete_cases={a: round(c / len(cs), 3) for a, c in presence.items()},
            )
        else:
            # No complete case: fall back to the longest observed sequence.
            longest = max((seqs.get(i, ()) for i in ids), key=len)
            entry.update(main_sequence=list(longest), main_sequence_share=None,
                         resources_by_step=_resources_by_position(longest, vok),
                         note="no complete case of this variant; main_sequence is the longest observed (partial) sequence")
        out["variants"][str(v)] = entry
    return out


def _resources_by_position(sequence: tuple, ok: pd.DataFrame) -> list[dict[str, float]]:
    """Resource shares for each position of ``sequence``, aligning the k-th occurrence of an
    activity in a case with the k-th occurrence in the sequence (role-based assignment,
    e.g. the first transport by one vehicle and later ones by another)."""
    counts: dict[tuple[str, int], Counter] = {}
    for _, g in ok.sort_values("start").groupby("case_id"):
        seen: Counter = Counter()
        for a, r in zip(g["activity"], g["resource"]):
            counts.setdefault((a, seen[a]), Counter())[r] += 1
            seen[a] += 1
    out, seen = [], Counter()
    for a in sequence:
        c = counts.get((a, seen[a]), Counter())
        seen[a] += 1
        tot = sum(c.values())
        out.append({res: round(n / tot, 3) for res, n in c.most_common()} if tot else {})
    return out


def make_routing_tool(df: pd.DataFrame, schema_provider: Callable[[], dict | None],
                      censoring_provider: Callable[[], dict | None], evidence_dir: str):
    """Tool factory: ``discover_variant_routings``."""

    @tool
    def discover_variant_routings(terminal_activity: str | None = None) -> dict[str, Any]:
        """
        Discover the routing of every variant from the activity instances. Run
        detect_censoring first: censored cases (overlapping the window start/end)
        are excluded. Returns per variant: share of released cases, the main step
        sequence and alternatives (from COMPLETE cases, so truncation cannot make
        always-present steps look optional), step presence,
        resource shares per step position of the main sequence (``resources_by_step``),
        and early exits — the probability that a case stops mid-process, after how many
        successful steps (``early_exit_after_n_steps``) and at which activity (real
        abandonment/scrap, not window truncation).

        Args:
            terminal_activity: Activity that marks completion. Default: the one
                               inferred by detect_censoring.
        """
        schema = schema_provider()
        if not schema:
            return {"error": "No confirmed log schema. The data analysis phase must call set_log_schema first."}
        cens = censoring_provider()
        if cens is None:
            return {"error": "Run detect_censoring first."}
        inst, _ = build_instances(df, schema)
        term = terminal_activity or cens.get("inferred_terminal_activity")
        censored = set(cens.get("left_censored", [])) | set(cens.get("right_censored", []))
        res = discover_routings(inst, term, censored)
        os.makedirs(os.path.join(os.getcwd(), evidence_dir), exist_ok=True)
        path = os.path.join(evidence_dir, "discover_variant_routings.json")
        with open(os.path.join(os.getcwd(), path), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, default=str)
        res["evidence_file"] = path
        return res

    return discover_variant_routings
