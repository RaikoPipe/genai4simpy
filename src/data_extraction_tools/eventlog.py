"""Normalisation of raw event logs into activity instances.

Every deterministic discovery / verification tool works on the same table of
activity instances, built from the raw log via a ``LogSchema`` that the data
analysis agent confirms once (and stores in the simulation spec).

Activity-instance table columns (times in seconds from the first event, t0):

    case_id, variant, activity, resource,
    enabled   - time the step was requested / queued (NaN if not observable)
    start     - service start
    end       - service end
    state     - 'success' | 'failure' | other label

Two raw layouts are supported:

* lifecycle layout: one row per lifecycle transition (e.g. scheduled / start /
  complete), linked by ``instance_col``. ``enabled`` comes from the
  ``enabled_value`` row, ``start``/``end`` from the ``start_value`` row, and the
  outcome from the ``complete_value`` row's ``state_col``.
* flat layout: one row per activity instance with start and end columns.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

INSTANCE_COLUMNS = ["case_id", "variant", "activity", "resource", "enabled", "start", "end", "state"]


class LogSchema(BaseModel):
    """Column semantics of the raw event log (confirmed by the data analysis agent)."""

    case_col: str = Field(description="Case / work-piece identifier column.")
    activity_col: str = Field(description="Activity name column.")
    resource_col: str = Field(description="Executing resource column.")
    start_col: str = Field(description="Timestamp column holding the service start (on start rows in lifecycle layout).")
    end_col: str | None = Field(None, description="Timestamp column holding the service end. None -> use the complete row's start_col.")
    variant_col: str | None = Field(None, description="Product variant / process model column, if any.")
    lifecycle_col: str | None = Field(None, description="Lifecycle transition column (lifecycle layout only).")
    instance_col: str | None = Field(None, description="Column linking the lifecycle rows of one activity instance.")
    enabled_value: str | None = Field(None, description="Lifecycle value marking the request / queue-entry row, e.g. 'scheduled'.")
    start_value: str | None = Field(None, description="Lifecycle value marking the service-start row, e.g. 'start'.")
    complete_value: str | None = Field(None, description="Lifecycle value marking the completion row, e.g. 'complete'.")
    state_col: str | None = Field(None, description="Outcome column, e.g. 'lifecycle:state'.")
    success_values: list[str] = Field(default_factory=lambda: ["success"])
    failure_values: list[str] = Field(default_factory=lambda: ["failure"])


def _to_ts(s: pd.Series) -> pd.Series:
    try:
        return pd.to_datetime(s, format="ISO8601", utc=True)
    except (ValueError, TypeError):
        return pd.to_datetime(s, errors="coerce", utc=True)


def _norm_state(v: Any, schema: LogSchema) -> str:
    if pd.isna(v):
        return "unknown"
    v = str(v)
    if v in schema.success_values:
        return "success"
    if v in schema.failure_values:
        return "failure"
    return v


def build_instances(df: pd.DataFrame, schema: LogSchema | dict) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return (activity-instance table, meta) for ``df`` under ``schema``.

    ``meta`` holds ``t0`` (ISO string), ``T`` (window length in seconds, last
    observed timestamp), and counts useful for a sanity check.
    """
    if isinstance(schema, dict):
        schema = LogSchema(**schema)
    needed = [schema.case_col, schema.activity_col, schema.resource_col, schema.start_col]
    for c in [schema.end_col, schema.variant_col, schema.lifecycle_col, schema.instance_col, schema.state_col]:
        if c:
            needed.append(c)
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"LogSchema columns not in dataset: {missing}. Available: {list(df.columns)}")

    d = df.copy()
    d["_ts"] = _to_ts(d[schema.start_col])
    d["_te"] = _to_ts(d[schema.end_col]) if schema.end_col else pd.NaT
    t_cols = [d["_ts"]] + ([d["_te"]] if schema.end_col else [])
    t0 = min(c.min() for c in t_cols)
    t_last = max(c.max() for c in t_cols)
    sec = lambda s: (s - t0).dt.total_seconds()
    variant = (lambda x: x[schema.variant_col]) if schema.variant_col else (lambda x: pd.Series("all", index=x.index))

    if schema.lifecycle_col:
        if not (schema.instance_col and schema.start_value):
            raise ValueError("lifecycle layout needs instance_col and start_value")
        lc = d[schema.lifecycle_col].astype(str)
        st = d[lc == schema.start_value].drop_duplicates(schema.instance_col).set_index(schema.instance_col)
        out = pd.DataFrame({
            "case_id": st[schema.case_col].astype(str),
            "variant": variant(st).astype(str),
            "activity": st[schema.activity_col].astype(str),
            "resource": st[schema.resource_col].astype(str),
            "start": sec(st["_ts"]),
        })
        if schema.end_col:
            out["end"] = sec(st["_te"])
        if schema.complete_value:
            co = d[lc == schema.complete_value].drop_duplicates(schema.instance_col).set_index(schema.instance_col)
            if not schema.end_col:
                out["end"] = sec(co["_ts"]).reindex(out.index)
            out["state"] = (co[schema.state_col].reindex(out.index) if schema.state_col
                            else pd.Series("success", index=out.index))
        else:
            out["state"] = st[schema.state_col] if schema.state_col else "success"
        if schema.enabled_value:
            en = d[lc == schema.enabled_value].drop_duplicates(schema.instance_col).set_index(schema.instance_col)
            out["enabled"] = sec(en["_ts"]).reindex(out.index)
        else:
            out["enabled"] = np.nan
        out = out.reset_index(drop=True)
    else:
        if not schema.end_col:
            raise ValueError("flat layout needs end_col")
        out = pd.DataFrame({
            "case_id": d[schema.case_col].astype(str),
            "variant": variant(d).astype(str),
            "activity": d[schema.activity_col].astype(str),
            "resource": d[schema.resource_col].astype(str),
            "enabled": np.nan,
            "start": sec(d["_ts"]),
            "end": sec(d["_te"]),
            "state": d[schema.state_col] if schema.state_col else "success",
        })

    out["state"] = out["state"].map(lambda v: _norm_state(v, schema))
    out = out[INSTANCE_COLUMNS].dropna(subset=["start"]).sort_values(["start", "case_id"]).reset_index(drop=True)
    meta = {
        "t0": t0.isoformat(),
        "T": float((t_last - t0).total_seconds()),
        "instances": int(len(out)),
        "cases": int(out["case_id"].nunique()),
        "activities": int(out["activity"].nunique()),
        "resources": int(out["resource"].nunique()),
        "enabled_observed_frac": float(out["enabled"].notna().mean()) if len(out) else 0.0,
        "end_missing": int(out["end"].isna().sum()),
    }
    return out, meta


def resource_class(resource: pd.Series) -> pd.Series:
    """Default resource-class heuristic: strip a trailing ``_<n>`` / ``<n>`` index."""
    return resource.astype(str).str.replace(r"[_\-]?\d+$", "", regex=True)
