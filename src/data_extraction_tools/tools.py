from __future__ import annotations

import os
import re
from typing import Any, Literal

import numpy as np
import pandas as pd
from langchain_core.tools import tool


# =============================================================================
# Tool factories
#
# Each public function accepts a DataFrame (and any fixed config) and returns
# a @tool-decorated callable whose signature contains only the parameters the
# LLM is expected to supply at runtime. The DataFrame is captured via closure
# and never appears in the tool schema.
# =============================================================================


def make_extract_table_metadata(df: pd.DataFrame):
    """Return a tool that extracts comprehensive dataset metadata."""

    @tool
    def extract_table_metadata() -> dict[str, Any]:
        """
        Extract comprehensive metadata for the loaded manufacturing event dataset.

        Returns an overview of shape, column types, data quality indicators,
        per-column statistics, and potential join-key candidates. Call this
        first to understand the dataset before any other exploration.
        """
        # Strip unnamed / empty columns once, work on a clean view
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]

        meta: dict[str, Any] = {
            "shape": {"rows": len(_df), "columns": len(_df.columns)},
            "columns": {},
            "data_quality": {
                "total_missing": int(_df.isna().sum().sum()),
                "missing_pct": round(_df.isna().sum().sum() / _df.size * 100, 2),
                "duplicate_rows": int(_df.duplicated().sum()),
            },
            "memory_mb": round(_df.memory_usage(deep=True).sum() / 1024**2, 2),
        }

        for col in _df.columns:
            s = _df[col]
            non_null = s.dropna()
            col_meta: dict[str, Any] = {
                "dtype": str(s.dtype),
                "missing": int(s.isna().sum()),
                "unique": int(s.nunique()),
                "unique_ratio": round(s.nunique() / len(s), 4) if len(s) > 0 else 0,
            }

            if len(non_null) > 0:
                col_meta["samples"] = non_null.sample(min(5, len(non_null))).tolist()

            if pd.api.types.is_numeric_dtype(s):
                col_meta["stats"] = {
                    "min": float(s.min()) if not pd.isna(s.min()) else None,
                    "max": float(s.max()) if not pd.isna(s.max()) else None,
                    "mean": round(float(s.mean()), 4) if not pd.isna(s.mean()) else None,
                    "std": round(float(s.std()), 4) if not pd.isna(s.std()) else None,
                    "zeros": int((s == 0).sum()),
                    "negative": int((s < 0).sum()),
                }

            if col_meta["unique"] <= 20 or col_meta["unique_ratio"] < 0.05:
                col_meta["value_counts"] = s.value_counts().head(10).to_dict()
                col_meta["likely_categorical"] = True

            if s.dtype == "object":
                parsed = pd.to_datetime(non_null.head(100), errors="coerce")
                if parsed.notna().sum() > len(parsed) * 0.8:
                    col_meta["likely_datetime"] = True
                    col_meta["datetime_range"] = {
                        "min": str(parsed.min()),
                        "max": str(parsed.max()),
                    }

            if col_meta["unique_ratio"] > 0.95 and col_meta["missing"] == 0:
                col_meta["likely_identifier"] = True

            meta["columns"][col] = col_meta

        # Potential join / foreign-key candidates
        id_cols = [
            c for c in _df.columns
            if c.lower().endswith(("_id", "id", "_key", "_code", "_no", "_nr"))
        ]
        meta["potential_joins"] = [
            {
                "column": col,
                "unique_values": int(_df[col].nunique()),
                "pattern": _df[col].dropna().astype(str).head(3).tolist(),
            }
            for col in id_cols
        ]

        return meta

    return extract_table_metadata


# -----------------------------------------------------------------------------


def make_detect_column_roles(df: pd.DataFrame):
    """Return a tool that heuristically classifies columns into simulation roles."""

    @tool
    def detect_column_roles() -> dict[str, list[str]]:
        """
        Heuristically classify dataset columns into likely discrete-event
        simulation roles (timestamps, identifiers, resources, products,
        activities, durations, quantities, categories).

        Returns candidate lists per role — the agent must verify them via
        inspect_column or get_unique_values before committing to a mapping.
        Does not modify any stored mapping.
        """
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]

        roles: dict[str, list[str]] = {
            "timestamp_candidates": [],
            "identifier_candidates": [],
            "resource_candidates": [],
            "product_candidates": [],
            "activity_candidates": [],
            "duration_candidates": [],
            "quantity_candidates": [],
            "category_candidates": [],
        }

        for col in _df.columns:
            col_lower = col.lower()
            s = _df[col]
            nunique = s.nunique()
            unique_ratio = nunique / len(s) if len(s) > 0 else 0

            # Timestamps
            if s.dtype == "datetime64[ns]":
                roles["timestamp_candidates"].append(col)
            elif s.dtype == "object":
                sample = s.dropna().head(50)
                parsed = pd.to_datetime(sample, errors="coerce")
                if len(parsed) > 0 and parsed.notna().sum() / len(parsed) > 0.7:
                    roles["timestamp_candidates"].append(col)

            # Identifiers — high cardinality or naming convention
            if re.search(r"(id|case|order|lot|batch|no|nr|number)$", col_lower) or (
                unique_ratio > 0.5 and nunique > 100
            ):
                roles["identifier_candidates"].append(col)

            # Resources — explicit naming or medium-cardinality strings
            if re.search(r"(machine|resource|station|equipment|worker|operator|line)", col_lower):
                roles["resource_candidates"].append(col)
            elif s.dtype == "object" and 5 < nunique < 100:
                roles["resource_candidates"].append(col)

            # Products
            if re.search(r"(part|product|sku|item|material|article)", col_lower):
                roles["product_candidates"].append(col)

            # Activities
            if re.search(r"(activity|operation|process|step|task|action)", col_lower):
                roles["activity_candidates"].append(col)

            # Durations — numeric + time-related name
            if pd.api.types.is_numeric_dtype(s) and re.search(
                r"(time|duration|minute|second|hour|elapsed|cycle)", col_lower
            ):
                roles["duration_candidates"].append(col)

            # Quantities — numeric + size-related name
            if pd.api.types.is_numeric_dtype(s) and re.search(
                r"(qty|quantity|count|amount|batch|size|pieces)", col_lower
            ):
                roles["quantity_candidates"].append(col)

            # Categories — low cardinality or type/status naming
            if nunique <= 20 and (
                re.search(r"(type|status|code|category|class|flag|report)", col_lower)
                or (s.dtype == "object" and nunique < 15)
            ):
                roles["category_candidates"].append(col)

        # Drop empty buckets to keep the response concise
        return {k: v for k, v in roles.items() if v}

    return detect_column_roles


# -----------------------------------------------------------------------------


def make_inspect_column(df: pd.DataFrame):
    """Return a tool for deep inspection of a single dataset column."""

    @tool
    def inspect_column(column: str, n_samples: int = 20) -> dict[str, Any]:
        """
        Deep-dive into a single column to support role assignment decisions.

        Returns dtype, missing/unique counts, value distribution (full for
        low-cardinality columns, top-10 otherwise), numeric statistics, and
        datetime parse diagnostics when relevant.

        Args:
            column: Exact column name to inspect.
            n_samples: Number of random sample values to include
                       (only used when cardinality is high). Default 20.
        """
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]

        if column not in _df.columns:
            return {
                "error": f"Column '{column}' not found.",
                "available_columns": list(_df.columns),
            }

        s = _df[column]
        non_null = s.dropna()

        result: dict[str, Any] = {
            "column": column,
            "dtype": str(s.dtype),
            "total": len(s),
            "missing": int(s.isna().sum()),
            "missing_pct": round(s.isna().sum() / len(s) * 100, 2),
            "unique": int(s.nunique()),
            "unique_ratio": round(s.nunique() / len(s), 4) if len(s) > 0 else 0,
        }

        if len(non_null) == 0:
            result["samples"] = []
            return result

        # Value distribution
        if s.nunique() <= 50:
            result["value_counts"] = s.value_counts().to_dict()
        else:
            result["top_values"] = s.value_counts().head(10).to_dict()
            result["sample_values"] = non_null.sample(
                min(n_samples, len(non_null))
            ).tolist()

        # Numeric statistics
        if pd.api.types.is_numeric_dtype(s):
            result["stats"] = {
                "min": float(s.min()),
                "max": float(s.max()),
                "mean": round(float(s.mean()), 4),
                "median": float(s.median()),
                "std": round(float(s.std()), 4),
                "skewness": round(float(s.skew()), 4),
                "zeros": int((s == 0).sum()),
                "negative": int((s < 0).sum()),
            }

        # Datetime parse diagnostics for object columns
        if s.dtype == "object":
            sample_size = min(100, len(non_null))
            parsed = pd.to_datetime(non_null.head(sample_size), errors="coerce")
            parse_rate = parsed.notna().sum() / sample_size
            if parse_rate > 0.5:
                result["datetime_parse_rate"] = round(float(parse_rate), 2)
                valid_dates = parsed.dropna()
                if len(valid_dates) > 0:
                    result["datetime_range"] = {
                        "min": str(valid_dates.min()),
                        "max": str(valid_dates.max()),
                    }

        return result

    return inspect_column


# -----------------------------------------------------------------------------


_DEFAULT_DISTRIBUTIONS = ["norm", "expon", "lognorm", "gamma", "weibull_min", "uniform", "triang"]


def _bootstrap_ks_pvalue(dist, params, d: np.ndarray, ks_obs: float, n_boot: int, seed: int = 0) -> float | None:
    """Parametric-bootstrap KS p-value (Lilliefors-type correction).

    The plain KS p-value is anti-conservative when the parameters were estimated
    from the same sample. Here the null distribution of the KS statistic is
    simulated by drawing ``n_boot`` samples from the fitted distribution,
    re-fitting each one and recomputing the statistic.
    """
    from scipy import stats as sp_stats

    if n_boot <= 0:
        return None
    rng = np.random.default_rng(seed)
    n = len(d)
    exceed = 0
    done = 0
    for _ in range(n_boot):
        try:
            sample = dist.rvs(*params, size=n, random_state=rng)
            p_b = dist.fit(sample)
            ks_b = sp_stats.kstest(sample, dist.cdf, args=p_b).statistic
        except Exception:
            continue
        done += 1
        exceed += ks_b >= ks_obs
    if done == 0:
        return None
    return (1 + exceed) / (done + 1)


def _empirical_fallback(d: pd.Series) -> dict[str, Any]:
    """Bounded, moment-preserving recommendation that needs no parametric fit.

    Returns the empirical quantile table (inverse-CDF sampling) when there are
    enough points, else triangular(min, median, max), else a constant.
    """
    mean = float(d.mean())
    if len(d) >= 10 and d.nunique() > 2:
        return _empirical_quantiles_entry(d, note=(
            "Bounded empirical fallback: inverse-CDF sampling from the empirical "
            "quantile table (keeps observed mean, spread and range)."))
    lo, mid, hi = float(d.min()), float(d.median()), float(d.max())
    if hi > lo:
        c = min(max((mid - lo) / (hi - lo), 0.0), 1.0)
        return {
            "distribution": "triang",
            "params": {"c": round(c, 6), "loc": round(lo, 6), "scale": round(hi - lo, 6)},
            "theoretical_mean": round((lo + mid + hi) / 3.0, 6),
            "valid": True,
            "fallback": True,
            "note": "Bounded empirical fallback: triangular(min, median, max) — too few points for quantiles.",
        }
    return {
        "distribution": "constant",
        "params": {"value": round(mean, 6)},
        "theoretical_mean": round(mean, 6),
        "theoretical_std": 0.0,
        "valid": True,
        "fallback": True,
        "note": "Zero spread in sample; constant.",
    }


def _empirical_quantiles_entry(d: pd.Series, note: str) -> dict[str, Any]:
    arr = d.to_numpy(dtype=float)
    probs = list(range(0, 101, 5))
    return {
        "distribution": "empirical_quantiles",
        "params": {},
        "quantiles": [round(float(np.percentile(arr, p)), 6) for p in probs],
        "quantile_probs": [p / 100 for p in probs],
        "theoretical_mean": round(float(arr.mean()), 6),
        "theoretical_std": round(float(arr.std(ddof=1)), 6) if len(arr) > 1 else 0.0,
        "p_value": None,
        "ks_pass": None,
        "valid": True,
        "fallback": True,
        "note": note + (" Sample with np.interp(rng.uniform(), quantile_probs, quantiles). "
                        "No goodness-of-fit test is reported: the table is the sample's own "
                        "CDF, so any in-sample test would be trivially passed."),
    }


def fit_numeric_series(
        data: pd.Series,
        label: str = "overall",
        distributions: list[str] | None = None,
        min_value: float | None = 0.0,
        rank_by: str = "aic",
        moment_tol: float = 0.15,
        std_tol: float = 0.25,
        tail_factor: float = 2.0,
        min_parametric_n: int = 30,
        n_boot: int = 99,
) -> dict[str, Any]:
    """Fit candidate distributions to one numeric sample and recommend one.

    Shared by ``fit_distribution`` (column based) and ``fit_activity_durations``
    (activity-instance based). See ``fit_distribution`` for the gate semantics.
    """
    from scipy import stats as sp_stats

    distributions = distributions or _DEFAULT_DISTRIBUTIONS
    d = pd.to_numeric(data, errors="coerce").dropna()
    if min_value is not None:
        d = d[d > min_value]
    n = len(d)
    if n == 0:
        return {"label": label, "n_samples": 0, "error": "No data points after filtering."}

    emp_mean, emp_std = float(d.mean()), float(d.std())
    emp_min, emp_max = float(d.min()), float(d.max())
    ks_reliable = n >= min_parametric_n
    d_arr = d.to_numpy(dtype=float)

    fits: list[dict[str, Any]] = []
    for dist_name in (distributions if n >= 10 else []):
        try:
            dist = getattr(sp_stats, dist_name)
            params = dist.fit(d_arr)
            ks_stat = float(sp_stats.kstest(d_arr, dist.cdf, args=params).statistic)
            log_lik = float(dist.logpdf(d_arr, *params).sum())
            k = len(params)
            shape_names = [s.strip() for s in dist.shapes.split(",")] if dist.shapes else []
            fit = {
                "distribution": dist_name,
                "params": {nm: round(float(v), 6) for nm, v in zip(shape_names + ["loc", "scale"], params)},
                "ks_statistic": round(ks_stat, 6),
                "aic": round(2 * k - 2 * log_lik, 2),
                "bic": round(k * np.log(n) - 2 * log_lik, 2),
            }
            m, v = dist.stats(*params, moments="mv")
            th_mean, th_std = float(m), float(np.sqrt(v)) if np.isfinite(v) and v >= 0 else float("nan")
            mean_rel_err = abs(th_mean - emp_mean) / (abs(emp_mean) + 1e-12) if np.isfinite(th_mean) else float("inf")
            std_rel_err = abs(th_std - emp_std) / (emp_std + 1e-12) if np.isfinite(th_std) else float("inf")
            try:
                p99 = float(dist.ppf(0.99, *params))
                tail_ratio = p99 / (emp_max + 1e-12) if np.isfinite(p99) else float("inf")
            except Exception:
                tail_ratio = float("inf")
            data_span = emp_max - emp_min + 1e-12
            degenerate = any(abs(float(p)) > 1e4 * data_span for p in params if np.isfinite(float(p)))
            moment_pass = (np.isfinite(th_mean) and np.isfinite(th_std)
                           and mean_rel_err <= moment_tol and std_rel_err <= std_tol)
            tail_pass = np.isfinite(tail_ratio) and tail_ratio <= tail_factor
            # Bootstrap only candidates that could be selected; it is the expensive step.
            p_value = (_bootstrap_ks_pvalue(dist, params, d_arr, ks_stat, n_boot)
                       if ks_reliable and moment_pass and tail_pass and not degenerate else None)
            ks_pass = None if p_value is None else bool(p_value > 0.05)
            fit.update(
                p_value=None if p_value is None else round(float(p_value), 4),
                p_value_method=f"parametric bootstrap (B={n_boot})" if p_value is not None else "not tested",
                ks_pass=ks_pass,
                theoretical_mean=round(th_mean, 6) if np.isfinite(th_mean) else None,
                theoretical_std=round(th_std, 6) if np.isfinite(th_std) else None,
                mean_rel_err=round(mean_rel_err, 4) if np.isfinite(mean_rel_err) else None,
                std_rel_err=round(std_rel_err, 4) if np.isfinite(std_rel_err) else None,
                tail_ratio=round(tail_ratio, 4) if np.isfinite(tail_ratio) else None,
                degenerate=bool(degenerate),
                valid=bool(moment_pass and tail_pass and not degenerate and ks_reliable and ks_pass),
            )
            fits.append(fit)
        except Exception:
            continue

    fits.sort(key=lambda x: (not x["valid"], x[rank_by] if rank_by in x else 0, len(x["params"])))
    if fits and fits[0]["valid"]:
        best_fit = fits[0]
        reason = f"Best valid parametric fit by {rank_by} (moment/tail gate + bootstrap KS passed)."
    else:
        best_fit = _empirical_fallback(d)
        reason = (f"N={n} < {min_parametric_n}: parametric fits not trusted; " if not ks_reliable else
                  "No parametric fit passed the moment/tail gate and the bootstrap KS test; ") + \
                 f"using {best_fit['distribution']} fallback."

    return {
        "label": label,
        "n_samples": n,
        "empirical_stats": {
            "mean": round(emp_mean, 4), "std": round(emp_std, 4) if n > 1 else 0.0,
            "cv": round(emp_std / emp_mean, 4) if emp_mean and n > 1 else None,
            "min": round(emp_min, 4), "median": round(float(d.median()), 4), "max": round(emp_max, 4),
        },
        "recommendation_reason": reason,
        "best_fit": best_fit,
        # Compact view of the alternatives (full parameters only for the best one).
        "alternatives": [
            {k: f.get(k) for k in ("distribution", "aic", "p_value", "mean_rel_err", "std_rel_err", "valid")}
            for f in fits[:4]
        ],
    }


def make_fit_distribution(df: pd.DataFrame):
    """Return a tool that fits statistical distributions to a numeric column."""

    @tool
    def fit_distribution(
            column: str,
            group_by: str | None = None,
            filter_col: str | None = None,
            filter_values: list[str] | None = None,
            min_value: float | None = 0.0,
            distributions: list[str] | None = None,
            rank_by: Literal["aic", "bic"] = "aic",
            min_parametric_n: int = 30,
    ) -> dict[str, Any]:
        """
        Fit probability distributions to a numeric column for simulation input.

        Prefer ``fit_activity_durations`` for activity service times — it works on
        the confirmed activity instances and cannot mix up lifecycle rows.

        A parametric fit is recommended only when ALL hold: theoretical mean within
        15 % and std within 25 % of the empirical moments, p99 <= 2x the observed
        max, non-degenerate parameters, N >= ``min_parametric_n``, and the
        parametric-bootstrap KS test (parameters re-estimated in every bootstrap
        sample, i.e. Lilliefors-corrected) does not reject at 5 %. Otherwise the
        recommendation is a bounded empirical fallback: the empirical quantile
        table (inverse-CDF sampling), or triangular(min, median, max) for N < 10.

        Args:
            column: Numeric column to fit distributions to.
            group_by: Optional column name to produce per-group fits.
            filter_col: Column to filter rows on before fitting.
            filter_values: Exact values to keep in filter_col, as a list.
            min_value: Exclude values at or below this threshold (default 0.0).
                       Pass None to disable filtering.
            distributions: scipy distribution names to test. Defaults to
                           norm, expon, lognorm, gamma, weibull_min, uniform, triang.
            rank_by: 'aic' (default) or 'bic' among valid fits.
            min_parametric_n: Minimum sample size for a parametric recommendation.
        """
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]
        if column not in _df.columns:
            return {"error": f"Column '{column}' not found.", "available_columns": list(_df.columns)}
        if filter_col and filter_values:
            if filter_col not in _df.columns:
                return {"error": f"filter_col '{filter_col}' not found."}
            _df = _df[_df[filter_col].isin(filter_values)]
        kw = dict(distributions=distributions, min_value=min_value, rank_by=rank_by,
                  min_parametric_n=min_parametric_n)
        if group_by:
            if group_by not in _df.columns:
                return {"error": f"group_by column '{group_by}' not found."}
            return {
                "column": column, "group_by": group_by,
                "results": {str(name): fit_numeric_series(grp[column], label=str(name), **kw)
                            for name, grp in _df.groupby(group_by)},
            }
        return {"column": column, "result": fit_numeric_series(_df[column], **kw)}

    return fit_distribution


def make_get_unique_values(df: pd.DataFrame):
    """Return a tool that retrieves value counts for any column."""

    @tool
    def get_unique_values(column: str, limit: int = 100) -> dict[str, Any]:
        """
        Return unique values and their occurrence counts for any column.

        Useful for understanding the domain of categorical or code columns
        before committing to a role mapping. Results are sorted by frequency
        descending and truncated to `limit` entries.

        Args:
            column: Exact column name to inspect.
            limit: Maximum number of distinct values to return. Default 100.
        """
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]

        if column not in _df.columns:
            return {
                "error": f"Column '{column}' not found.",
                "available_columns": list(_df.columns),
            }

        vc = _df[column].value_counts()
        return {
            "column": column,
            "unique_count": int(_df[column].nunique()),
            "missing": int(_df[column].isna().sum()),
            "values": vc.head(limit).to_dict(),
            "truncated": len(vc) > limit,
        }

    return get_unique_values


# -----------------------------------------------------------------------------


def _detect_outliers(
    series: pd.Series,
    method: Literal["none", "iqr", "zscore"] = "iqr",
    threshold: float = 1.5,
) -> tuple[pd.Series, float | None, float | None]:
    """
    Return (outlier_mask, lower_bound, upper_bound).

    method='iqr'    — Tukey fences: Q1 - k*IQR, Q3 + k*IQR  (default k=1.5)
    method='zscore' — |z| > threshold  (default threshold=3.0)
    method='none'   — no detection; all-False mask returned
    """
    if method == "none" or len(series) < 4:
        return pd.Series(False, index=series.index), None, None
    if method == "iqr":
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - threshold * iqr, q3 + threshold * iqr
        return (series < lower) | (series > upper), float(lower), float(upper)
    # zscore
    std = series.std()
    if std == 0:
        return pd.Series(False, index=series.index), None, None
    z = (series - series.mean()).abs() / std
    return z > threshold, None, None


# -----------------------------------------------------------------------------


def make_compute_duration(df: pd.DataFrame):
    """Return a tool that computes duration from a timestamp pair."""

    # Use a mutable container so the tool can write back into the caller's df
    _state = {"df": df}

    @tool
    def compute_duration(
        start_col: str,
        end_col: str,
        unit: Literal["seconds", "minutes", "hours", "days"] = "minutes",
        output_col: str = "duration_computed",
    ) -> dict[str, Any]:
        """
        Compute duration from two timestamp columns and append the result as a
        new column on the dataset.

        Returns summary statistics and flags data quality issues (negative
        durations, zeros). The computed column is immediately available to all
        subsequent tool calls.

        Args:
            start_col: Column containing the start timestamp.
            end_col: Column containing the end/completion timestamp.
            unit: Time unit for the output values.
                  One of 'seconds', 'minutes', 'hours', 'days'. Default 'minutes'.
            output_col: Name for the new duration column. Default 'duration_computed'.
        """
        _df = _state["df"]

        for col in (start_col, end_col):
            if col not in _df.columns:
                return {
                    "error": f"Column '{col}' not found.",
                    "available_columns": list(_df.columns),
                }

        divisors = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}
        start_ts = pd.to_datetime(_df[start_col], errors="coerce")
        end_ts = pd.to_datetime(_df[end_col], errors="coerce")
        delta = (end_ts - start_ts).dt.total_seconds() / divisors[unit]

        _df[output_col] = delta

        valid = delta.dropna()
        negative = int((valid < 0).sum())
        zero = int((valid == 0).sum())
        positive = valid[valid > 0]

        result: dict[str, Any] = {
            "output_column": output_col,
            "unit": unit,
            "total_rows": len(delta),
            "valid": int(valid.notna().sum()),
            "negative": negative,
            "zero": zero,
            "positive": int(len(positive)),
            "stats": None,
            "warnings": [],
        }

        if len(positive) > 0:
            result["stats"] = {
                "mean": round(float(positive.mean()), 4),
                "std": round(float(positive.std()), 4),
                "min": round(float(positive.min()), 4),
                "max": round(float(positive.max()), 4),
                "median": round(float(positive.median()), 4),
            }

        if negative > 0:
            result["warnings"].append(
                f"{negative} negative durations detected (end timestamp < start timestamp)."
            )
        if zero > 0:
            result["warnings"].append(
                f"{zero} zero durations — these rows will be excluded by tools that apply min_value > 0."
            )

        return result

    return compute_duration


# -----------------------------------------------------------------------------


def _group_stats(vals: pd.Series, method: str, threshold: float, remove: bool) -> dict[str, Any]:
    """Descriptive stats for one group; outliers are flagged and removed only on request."""
    mask, lower, upper = _detect_outliers(vals, method, threshold)
    used = vals[~mask] if remove and (~mask).any() else vals
    n_out = int(mask.sum())
    return {
        "count": len(vals),
        "count_used": len(used),
        "mean": round(float(used.mean()), 4),
        "std": round(float(used.std()), 4) if len(used) > 1 else 0.0,
        "cv": round(float(used.std() / used.mean()), 4) if len(used) > 1 and used.mean() else None,
        "min": round(float(used.min()), 4),
        "max": round(float(used.max()), 4),
        "median": round(float(used.median()), 4),
        "outliers": {
            "count": n_out,
            "rate": round(n_out / len(vals), 4) if len(vals) else 0.0,
            "removed": bool(remove and n_out > 0),
            "method": method,
            "threshold": threshold,
            "lower_bound": round(lower, 4) if lower is not None else None,
            "upper_bound": round(upper, 4) if upper is not None else None,
            "mean_if_removed": round(float(vals[~mask].mean()), 4) if n_out and (~mask).any() else None,
        },
    }


def make_extract_processing_times(df: pd.DataFrame):
    """Return a tool that computes grouped processing time statistics."""

    @tool
    def extract_processing_times(
        duration_col: str,
        group_by_col: str,
        time_type_col: str | None = None,
        time_type_filter: list[str] | None = None,
        min_duration: float = 0.0,
        outlier_method: Literal["none", "iqr", "zscore"] = "iqr",
        outlier_threshold: float = 3.0,
        remove_outliers: bool = False,
        data_quality_reason: str | None = None,
    ) -> dict[str, Any]:
        """
        Compute processing time statistics grouped by a resource or activity column.

        Outliers are DETECTED and reported per group (Tukey far fences, k=3 by
        default) but NOT removed: long service times are real variability that the
        simulation must reproduce. Set ``remove_outliers=True`` only for a
        documented data-quality defect (e.g. a sensor glitch producing 0.03 s), and
        state it in ``data_quality_reason``; the report must cite that reason.

        Args:
            duration_col: Numeric column containing duration values.
            group_by_col: Column to group statistics by (resource or activity).
            time_type_col: Column that encodes time categories (e.g. setup vs. work).
            time_type_filter: List of time-type values to keep.
            min_duration: Exclude durations at or below this value (default 0.0).
            outlier_method: 'iqr' (default), 'zscore' or 'none' — detection only.
            outlier_threshold: IQR multiplier k (default 3.0) or z cutoff.
            remove_outliers: Remove the flagged values (requires data_quality_reason).
            data_quality_reason: Why the flagged values are data errors, not variability.
        """
        if remove_outliers and not data_quality_reason:
            return {"error": "remove_outliers=True requires data_quality_reason (a documented data defect)."}
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]
        for col in (duration_col, group_by_col):
            if col not in _df.columns:
                return {"error": f"Column '{col}' not found.", "available_columns": list(_df.columns)}
        if time_type_col and time_type_filter:
            if time_type_col not in _df.columns:
                return {"error": f"time_type_col '{time_type_col}' not found."}
            _df = _df[_df[time_type_col].isin(time_type_filter)]
        _df = _df.copy()
        _df[duration_col] = pd.to_numeric(_df[duration_col], errors="coerce")
        _df = _df[_df[duration_col] > min_duration]
        if _df.empty:
            return {"error": "No records remain after filtering."}

        stats_dict = {
            str(g): _group_stats(s.dropna(), outlier_method, outlier_threshold, remove_outliers)
            for g, s in _df.groupby(group_by_col)[duration_col]
        }
        return {
            "group_by": group_by_col,
            "duration_column": duration_col,
            "filter": {"time_type_col": time_type_col, "values": time_type_filter},
            "outliers_removed": remove_outliers,
            "data_quality_reason": data_quality_reason,
            "total_records": len(_df),
            "statistics": stats_dict,
        }

    return extract_processing_times


# -----------------------------------------------------------------------------


def _spec_dist(fit: dict[str, Any], source: str) -> dict[str, Any] | None:
    """Convert a ``fit_numeric_series`` result into a spec Distribution dict."""
    if "best_fit" not in fit:
        return None
    b = fit["best_fit"]
    d = {"family": b["distribution"], "params": b.get("params", {}),
         "mean": fit["empirical_stats"]["mean"], "n": fit["n_samples"], "source": source}
    if b["distribution"] == "empirical_quantiles":
        d.update(quantiles=b["quantiles"], quantile_probs=b["quantile_probs"])
    return d


def _arrival_distributions(iat_s: np.ndarray, reg: dict[str, Any]) -> dict[str, Any]:
    """Spec-ready arrival distributions (seconds) for the single- and two-regime models."""
    src = "extract_inter_arrival_times"
    rec: dict[str, Any] = {"interarrival": _spec_dist(fit_numeric_series(pd.Series(iat_s), min_value=None), src)}
    if reg.get("regime") == "two_regime":
        thr = reg["threshold_s"]
        burst, gap = iat_s[iat_s <= thr], iat_s[iat_s > thr]
        rec["intra_burst_iat"] = _spec_dist(fit_numeric_series(pd.Series(burst), min_value=None), src)
        rec["inter_burst_gap"] = _spec_dist(fit_numeric_series(pd.Series(gap), min_value=None), src)
        sizes = pd.Series(_burst_sizes(iat_s, thr)).value_counts(normalize=True).sort_index()
        rec["burst_size"] = {"family": "categorical", "values": [int(v) for v in sizes.index],
                             "probs": [round(float(p), 4) for p in sizes.values],
                             "mean": round(float(np.mean(_burst_sizes(iat_s, thr))), 3),
                             "n": int(reg["burst_size"]["n_bursts"]), "source": src}
    return rec


def _burst_sizes(iat_s: np.ndarray, thr: float) -> list[int]:
    sizes, cur = [], 1
    for v in iat_s:
        if v > thr:
            sizes.append(cur)
            cur = 1
        else:
            cur += 1
    return sizes + [cur]


def make_extract_inter_arrival_times(df: pd.DataFrame):
    """Return a tool that computes inter-arrival times between cases."""

    @tool
    def extract_inter_arrival_times(
        case_col: str,
        timestamp_col: str,
        group_by_col: str | None = None,
        unit: Literal["seconds", "minutes", "hours", "days"] = "seconds",
        exclude_case_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Compute inter-arrival times (IAT) between consecutive case arrivals.

        Arrival time per case = earliest ``timestamp_col`` value of that case (use
        the request / release timestamp when the log has one). No gaps are removed:
        the long gaps between bursts ARE part of the arrival process, and removing
        them overstates the arrival rate. Instead the result contains a
        two-regime decomposition (``regimes``): intra-burst IATs, inter-burst gaps
        and the burst-size distribution. If the CV is high and the regimes are
        well separated, model arrivals as bursts (batch of k cases, gap between
        batches) — not as a single exponential with the overall mean.

        Args:
            case_col: Column that uniquely identifies each case.
            timestamp_col: Timestamp column used to determine arrival time.
            group_by_col: Optional column for per-group IATs (e.g. variant).
            unit: Time unit of the output, default 'seconds'.
            exclude_case_ids: Cases to leave out (e.g. left-censored cases already
                              in the system at the window start, see detect_censoring).
        """
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]
        for col in (case_col, timestamp_col):
            if col not in _df.columns:
                return {"error": f"Column '{col}' not found.", "available_columns": list(_df.columns)}
        from src.data_extraction_tools.discovery import two_regime_iat

        divisors = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}
        _df = _df.copy()
        if exclude_case_ids:
            _df = _df[~_df[case_col].astype(str).isin([str(c) for c in exclude_case_ids])]
        _df[timestamp_col] = pd.to_datetime(_df[timestamp_col], errors="coerce", format="ISO8601")

        def _iat_stats(arrivals: pd.Series, label: str = "global") -> dict[str, Any]:
            arrivals = arrivals.dropna().sort_values()
            iat_s = arrivals.diff().dt.total_seconds().dropna().to_numpy()
            if len(iat_s) < 2:
                return {"label": label, "error": "Too few arrivals to compute IAT."}
            iat = iat_s / divisors[unit]
            mean, std = float(iat.mean()), float(iat.std(ddof=1))
            out = {
                "label": label,
                "cases": int(len(arrivals)),
                "span": round(float((arrivals.iloc[-1] - arrivals.iloc[0]).total_seconds()) / divisors[unit], 4),
                "mean": round(mean, 4),
                "std": round(std, 4),
                "cv": round(std / mean, 4) if mean > 0 else None,
                "min": round(float(iat.min()), 4),
                "median": round(float(np.median(iat)), 4),
                "max": round(float(iat.max()), 4),
                "zero_iats": int((iat_s <= 0).sum()),
            }
            try:
                reg = two_regime_iat(iat_s)
                if unit != "seconds":
                    reg["unit_note"] = "regimes and recommended distributions are in seconds"
                out["regimes"] = reg
                out["recommended"] = _arrival_distributions(iat_s, reg)
            except Exception as exc:  # decomposition is advisory
                out["regimes"] = {"error": f"{type(exc).__name__}: {exc}"}
            return out

        result: dict[str, Any] = {
            "unit": unit,
            "global": _iat_stats(_df.groupby(case_col)[timestamp_col].min()),
        }
        if group_by_col:
            if group_by_col not in _df.columns:
                return {"error": f"group_by_col '{group_by_col}' not found."}
            result["by_" + group_by_col] = {
                str(name): _iat_stats(grp.groupby(case_col)[timestamp_col].min(), label=str(name))
                for name, grp in _df.groupby(group_by_col)
            }
        return result

    return extract_inter_arrival_times


# -----------------------------------------------------------------------------


def make_compute_grouped_statistics(df: pd.DataFrame):
    """Return a general-purpose grouped statistics tool."""

    @tool
    def compute_grouped_statistics(
        value_col: str,
        group_by: list[str],
        filter_col: str | None = None,
        filter_values: list[str] | None = None,
        min_value: float | None = None,
        percentiles: list[float] | None = None,
        outlier_method: Literal["none", "iqr", "zscore"] = "iqr",
        outlier_threshold: float = 3.0,
        remove_outliers: bool = False,
        data_quality_reason: str | None = None,
    ) -> dict[str, Any]:
        """
        Compute grouped descriptive statistics (count, mean, std, min, max, median)
        for any numeric column, with optional row filtering and percentiles.

        Outliers are flagged but kept unless ``remove_outliers=True`` with a
        documented ``data_quality_reason``.

        Args:
            value_col: Numeric column to aggregate.
            group_by: One or more columns to group by, as a list.
            filter_col: Column to filter rows on before aggregating.
            filter_values: Exact values to keep in filter_col.
            min_value: Exclude rows where value_col <= this threshold. None disables.
            percentiles: Additional percentiles, e.g. [0.90, 0.95].
            outlier_method: 'iqr' (default), 'zscore' or 'none' — detection only.
            outlier_threshold: IQR multiplier k (default 3.0) or z cutoff.
            remove_outliers: Remove flagged values (requires data_quality_reason).
            data_quality_reason: Why the flagged values are data errors.
        """
        if remove_outliers and not data_quality_reason:
            return {"error": "remove_outliers=True requires data_quality_reason (a documented data defect)."}
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]
        if value_col not in _df.columns:
            return {"error": f"Column '{value_col}' not found.", "available_columns": list(_df.columns)}
        missing_groups = [c for c in group_by if c not in _df.columns]
        if missing_groups:
            return {"error": f"group_by columns not found: {missing_groups}"}
        _df = _df.copy()
        _df[value_col] = pd.to_numeric(_df[value_col], errors="coerce")
        if filter_col and filter_values:
            if filter_col not in _df.columns:
                return {"error": f"filter_col '{filter_col}' not found."}
            _df = _df[_df[filter_col].isin(filter_values)]
        if min_value is not None:
            _df = _df[_df[value_col] > min_value]
        if _df.empty:
            return {"error": "No records remain after filtering."}

        stats_dict: dict[str, Any] = {}
        for name, grp in _df.groupby(group_by):
            key = str(name[0] if isinstance(name, tuple) and len(name) == 1 else name)
            vals = grp[value_col].dropna()
            stats_dict[key] = _group_stats(vals, outlier_method, outlier_threshold, remove_outliers)
            if percentiles:
                stats_dict[key]["percentiles"] = {
                    f"p{int(p * 100)}": round(float(vals.quantile(p)), 4) for p in percentiles
                }
        return {
            "value_column": value_col,
            "group_by": group_by,
            "filter": {"col": filter_col, "values": filter_values},
            "outliers_removed": remove_outliers,
            "data_quality_reason": data_quality_reason,
            "total_records": len(_df),
            "statistics": stats_dict,
        }

    return compute_grouped_statistics


# -----------------------------------------------------------------------------


def make_fit_activity_durations(df: pd.DataFrame, schema_provider):
    """Return a tool that fits service-time distributions per activity from activity instances."""

    @tool
    def fit_activity_durations(
        group_by: Literal["activity", "activity_resource", "resource"] = "activity",
        include_failures: bool = False,
        exclude_case_ids: list[str] | None = None,
        min_parametric_n: int = 30,
    ) -> dict[str, Any]:
        """
        Fit service-time distributions (end - start of each activity instance, in
        seconds) using the confirmed log schema — no duration columns needed, and
        lifecycle rows cannot be mixed up (queueing time is excluded by design).

        Returns, per group, the empirical stats and a recommended distribution
        (parametric fit that passed the moment/tail gate and the bootstrap KS test,
        else the empirical quantile table, else triangular for N < 10). Copy the
        ``best_fit`` entries verbatim into the spec section ``activities``.

        Args:
            group_by: 'activity' (default), 'activity_resource' (activity x
                      concrete resource) or 'resource'.
            include_failures: Also include failed attempts (default False).
            exclude_case_ids: Cases to leave out.
            min_parametric_n: Minimum N for a parametric recommendation (default 30).
        """
        from src.data_extraction_tools.eventlog import build_instances

        schema = schema_provider()
        if not schema:
            return {"error": "No confirmed log schema. The data analysis phase must call set_log_schema first."}
        inst, _ = build_instances(df, schema)
        if exclude_case_ids:
            inst = inst[~inst["case_id"].isin([str(c) for c in exclude_case_ids])]
        keys = {"activity": ["activity"], "activity_resource": ["activity", "resource"],
                "resource": ["resource"]}[group_by]
        attempts = inst.groupby(keys).size()
        failures = inst[inst["state"] == "failure"].groupby(keys).size().reindex(attempts.index, fill_value=0)
        if not include_failures:
            inst = inst[inst["state"] == "success"]
        inst = inst.assign(duration=inst["end"] - inst["start"])
        results = {}
        for name, grp in inst.groupby(keys):
            key = name[0] if isinstance(name, tuple) and len(name) == 1 else name
            label = "|".join(map(str, name)) if isinstance(name, tuple) else str(name)
            res = fit_numeric_series(grp["duration"], label=label, min_parametric_n=min_parametric_n)
            res["attempts"] = int(attempts.get(key, 0))
            res["failures"] = int(failures.get(key, 0))
            res["failure_probability"] = round(res["failures"] / res["attempts"], 4) if res["attempts"] else 0.0
            res["resources"] = sorted(grp["resource"].unique().tolist())
            results[label] = res
        return {"unit": "seconds", "group_by": group_by, "include_failures": include_failures,
                "results": results}

    return fit_activity_durations


# =============================================================================
# Cleaning tool
# =============================================================================

def make_apply_cleaning_and_save(df: pd.DataFrame, work_dir: str = "work_dir"):
    """Return a tool that applies user-confirmed cleaning operations and persists the result."""

    _cwd = os.getcwd()
    _default_output_path = os.path.join(work_dir, "eventlog_cleaned.parquet")

    @tool
    def apply_cleaning_and_save(
        columns_to_drop: list[str] | None = None,
        drop_missing_in: list[str] | None = None,
        drop_duplicates: bool = False,
        output_path: str = _default_output_path,
    ) -> dict[str, Any]:
        """
        Apply cleaning operations to the dataset and save the cleaned result to disk.

        Call this ONLY after the user has explicitly confirmed the cleaning operations.
        The saved file becomes the canonical dataset for all subsequent agents.

        Args:
            columns_to_drop: Non-simulation-relevant column names to remove.
            drop_missing_in: Drop rows where ANY of these columns have missing values.
                             Use for key columns: entity ID, timestamps, resource name.
            drop_duplicates: Whether to remove fully duplicate rows.
            output_path: Save path relative to working directory.
                         Default: '{work_dir}/eventlog_cleaned.parquet'.
        """
        cleaned = df.copy()
        ops: list[str] = []
        rows_before = len(cleaned)
        cols_before = len(cleaned.columns)

        if columns_to_drop:
            found = [c for c in columns_to_drop if c in cleaned.columns]
            not_found = [c for c in columns_to_drop if c not in cleaned.columns]
            if found:
                cleaned = cleaned.drop(columns=found)
                ops.append(f"Dropped {len(found)} columns: {found}")
            if not_found:
                ops.append(f"Columns not found (skipped): {not_found}")

        if drop_missing_in:
            key_cols = [c for c in drop_missing_in if c in cleaned.columns]
            if key_cols:
                before = len(cleaned)
                cleaned = cleaned.dropna(subset=key_cols)
                ops.append(
                    f"Dropped {before - len(cleaned)} rows with NaN in key columns: {key_cols}"
                )

        if drop_duplicates:
            before = len(cleaned)
            cleaned = cleaned.drop_duplicates()
            ops.append(f"Dropped {before - len(cleaned)} duplicate rows")

        full_path = os.path.join(_cwd, output_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        cleaned.to_parquet(full_path, index=False)

        return {
            "output_path": full_path,
            "rows_before": rows_before,
            "rows_after": len(cleaned),
            "rows_removed": rows_before - len(cleaned),
            "columns_before": cols_before,
            "columns_after": len(cleaned.columns),
            "columns_removed": cols_before - len(cleaned.columns),
            "operations": ops,
        }

    return apply_cleaning_and_save


# =============================================================================
# Convenience assembler
#
# Usage:
#   df = pd.read_parquet("data/eventlog.parquet")
#   tools = make_exploration_tools(df)
#   agent = create_deep_agent(tools=tools, ...)
# =============================================================================

def make_tools(df: pd.DataFrame) -> list:
    """
    Instantiate all exploration and extraction tools bound to the provided
    DataFrame. Returns a list ready to pass directly to
    create_deep_agent(tools=...).

    Included tools
    --------------
    Exploration:
        extract_table_metadata   — full dataset overview
        detect_column_roles      — heuristic role classification
        inspect_column           — deep single-column inspection
        get_unique_values        — value counts for any column

    Extraction:
        compute_duration         — derive duration from timestamp pairs
        extract_processing_times — grouped cycle/processing time stats
        extract_inter_arrival_times — case arrival IAT analysis
        compute_grouped_statistics  — general-purpose grouped aggregation

    Distribution fitting:
        fit_distribution         — fit scipy distributions to numeric columns
    """
    return [
        # Exploration
        make_extract_table_metadata(df),
        make_detect_column_roles(df),
        make_inspect_column(df),
        make_get_unique_values(df),
        # Extraction
        make_compute_duration(df),
        make_extract_processing_times(df),
        make_extract_inter_arrival_times(df),
        make_compute_grouped_statistics(df),
        # Distribution fitting
        make_fit_distribution(df),
    ]

def make_exploration_tools(df: pd.DataFrame) -> list:
    """
    Instantiate all exploration and extraction tools bound to the provided
    DataFrame. Returns a list ready to pass directly to
    create_deep_agent(tools=...).

    Included tools
    --------------
    Exploration:
        extract_table_metadata   — full dataset overview
        detect_column_roles      — heuristic role classification
        inspect_column           — deep single-column inspection
        get_unique_values        — value counts for any column

    Distribution fitting:
        fit_distribution         — fit scipy distributions to numeric columns
    """
    return [
        # Exploration
        make_extract_table_metadata(df),
        make_detect_column_roles(df),
        make_inspect_column(df),
        make_get_unique_values(df),
    ]

def make_extraction_tools(df: pd.DataFrame) -> list:
    """
    Instantiate all exploration and extraction tools bound to the provided
    DataFrame. Returns a list ready to pass directly to
    create_deep_agent(tools=...).

    Included tools
    --------------
    Exploration:
        extract_table_metadata   — full dataset overview
        detect_column_roles      — heuristic role classification
        inspect_column           — deep single-column inspection
        get_unique_values        — value counts for any column

    Extraction:
        compute_duration         — derive duration from timestamp pairs
        extract_processing_times — grouped cycle/processing time stats
        extract_inter_arrival_times — case arrival IAT analysis
        compute_grouped_statistics  — general-purpose grouped aggregation

    Distribution fitting:
        fit_distribution         — fit scipy distributions to numeric columns
    """
    return [
        # Extraction
        make_compute_duration(df),
        make_extract_processing_times(df),
        make_extract_inter_arrival_times(df),
        make_compute_grouped_statistics(df),
        # Distribution fitting
        make_fit_distribution(df),
    ]