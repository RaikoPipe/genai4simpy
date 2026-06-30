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
            rank_by: Literal["aic", "bic", "sum_log_likelihood"] = "aic",
            moment_tol: float = 0.15,
            std_tol: float = 0.25,
            tail_factor: float = 2.0,
            min_parametric_n: int = 30,
    ) -> dict[str, Any]:
        """
        Fit probability distributions to a numeric column for simulation input.

        Tests a set of common distributions and returns ranked fits with their
        parameters, goodness-of-fit statistics (KS test, AIC, BIC), empirical
        summary stats, theoretical moments, and a validity verdict. Essential for
        parameterising stochastic simulation models.

        A fit is marked ``"valid": True`` only when its theoretical moments are
        finite and agree with the data (mean within ``moment_tol``, std within
        ``std_tol``), its upper tail does not fabricate values far beyond the
        observed maximum (p99 <= ``tail_factor`` * empirical max), and its
        parameters are not numerically degenerate (no parameter magnitude
        exceeding 1e4 × data range). Invalid fits are retained in ``all_fits``
        for transparency but are never selected as ``best_fit``.

        When every parametric distribution fails the KS test (p-value <= 0.05),
        a non-parametric KDE entry (``"distribution": "kde"``) is appended to
        ``all_fits`` and participates in ranking. The KDE entry includes a
        21-point quantile table (keys ``"0"`` ... ``"100"`` at 5 % steps) for
        inverse-CDF sampling in simulation code without needing the raw data.

        For ``n < min_parametric_n`` no parametric distribution is recommended:
        ``best_fit`` is a bounded fallback (triangular from p5/median/p95, or an
        empirical-mean constant) and every parametric fit is flagged
        ``advisory_only`` with ``ks_reliable=False``.

        Args:
            column: Numeric column to fit distributions to.
            group_by: Optional column name to produce per-group fits
                      (e.g. fit processing times separately per resource).
            filter_col: Column to filter rows on before fitting.
            filter_values: Exact values to keep in filter_col. Supply as a
                           list even for a single value, e.g. ["D"].
            min_value: Exclude values at or below this threshold before
                       fitting (default 0.0 removes non-positive durations).
                       Pass None to disable filtering entirely.
            distributions: scipy distribution names to test. Defaults to
                           ['norm', 'expon', 'lognorm', 'gamma',
                            'weibull_min', 'uniform', 'triang'].
            rank_by: Criterion used to select among VALID fits.
                     'aic' — penalises number of parameters lightly (default).
                     'bic' — penalises number of parameters more strongly.
                     'sum_log_likelihood' — highest raw likelihood (no penalty;
                     discouraged: rewards degenerate near-delta fits).
            moment_tol: Max allowed |theoretical_mean - empirical_mean| /
                        |empirical_mean| for a fit to be valid (default 0.15).
            std_tol: Max allowed relative deviation of theoretical std from
                     empirical std for a fit to be valid (default 0.25).
            tail_factor: Max allowed theoretical p99 / empirical max for a fit
                         to be valid (default 2.0; blocks fabricated heavy tails).
            min_parametric_n: Minimum sample size to recommend a parametric fit
                              (default 30). Below this, return a bounded fallback.
        """
        from scipy import stats as sp_stats

        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]

        if column not in _df.columns:
            return {
                "error": f"Column '{column}' not found.",
                "available_columns": list(_df.columns),
            }

        if distributions is None:
            distributions = [
                "norm", "expon", "lognorm", "gamma",
                "weibull_min", "uniform", "triang",
            ]

        # Apply row-level filters
        _df = _df.copy()
        if filter_col and filter_values:
            if filter_col not in _df.columns:
                return {"error": f"filter_col '{filter_col}' not found."}
            _df = _df[_df[filter_col].isin(filter_values)]

        # ------------------------------------------------------------------
        # Helpers (dataset-agnostic)
        # ------------------------------------------------------------------
        def _empirical_fallback(d: pd.Series) -> dict[str, Any]:
            """Bounded, moment-preserving recommendation that needs no fit.

            Uses robust percentile bounds (p5, median, p95) clamped to the
            observed range, so that isolated outliers cannot drag the
            triangle far from the data mass.  Falls back to an empirical-mean
            constant when there is no spread.
            """
            mean = float(d.mean())
            p05, mid, p95 = (float(np.percentile(d, 5)),
                             float(d.median()),
                             float(np.percentile(d, 95)))
            # Clamp to observed range (never extrapolate beyond data).
            lo = max(p05, float(d.min()))
            hi = min(p95, float(d.max()))
            # Ensure lo < mid < hi after clamping; widen minimally if
            # percentiles collapse (very small or concentrated samples).
            if lo >= mid:
                lo = float(d.min())
            if hi <= mid:
                hi = float(d.max())
            if hi > lo:
                c = (mid - lo) / (hi - lo)
                c = min(max(c, 0.0), 1.0)
                return {
                    "distribution": "triangular_empirical",
                    "params": {"loc": round(lo, 6),
                               "scale": round(hi - lo, 6),
                               "c": round(c, 6)},
                    "theoretical_mean": round((lo + mid + hi) / 3.0, 6),
                    "theoretical_std": None,
                    "valid": True,
                    "fallback": True,
                    "note": ("Bounded empirical fallback: "
                             "triangular(p5, median, p95) clamped to "
                             "observed range."),
                }
            return {
                "distribution": "constant_empirical_mean",
                "params": {"value": round(mean, 6)},
                "theoretical_mean": round(mean, 6),
                "theoretical_std": 0.0,
                "valid": True,
                "fallback": True,
                "note": "Zero spread in sample; empirical-mean constant.",
            }

        def _annotate_moments(dist, params, fit, emp_mean, emp_std,
                              emp_min, emp_max, ks_reliable):
            """Attach theoretical moments, relative errors, and validity verdict."""
            try:
                m, v = dist.stats(*params, moments="mv")
                th_mean = float(m)
                th_std = float(np.sqrt(v)) if np.isfinite(v) and v >= 0 else float("nan")
            except Exception:
                th_mean = float("nan")
                th_std = float("nan")

            finite = np.isfinite(th_mean) and np.isfinite(th_std)
            mean_rel_err = (abs(th_mean - emp_mean) / (abs(emp_mean) + 1e-12)
                            if np.isfinite(th_mean) else float("inf"))
            std_rel_err = (abs(th_std - emp_std) / (emp_std + 1e-12)
                           if np.isfinite(th_std) else float("inf"))

            try:
                p99 = float(dist.ppf(0.99, *params))
                tail_ratio = p99 / (emp_max + 1e-12) if np.isfinite(p99) else float("inf")
            except Exception:
                tail_ratio = float("inf")

            moment_pass = (finite and mean_rel_err <= moment_tol
                           and std_rel_err <= std_tol)
            tail_pass = np.isfinite(tail_ratio) and tail_ratio <= tail_factor

            # ---- Degeneracy guard ----
            # Flag fits whose parameters are absurdly far from the data
            # range.  Catches e.g. lognorm(s≈0, loc≈−1.6e6) which
            # technically matches moments but is numerically fragile,
            # uninterpretable, and unreproducible across platforms.
            data_span = emp_max - emp_min + 1e-12
            degenerate = any(
                abs(float(v)) > 1e4 * data_span
                for v in params
                if np.isfinite(float(v))
            )
            fit["degenerate"] = bool(degenerate)

            fit["theoretical_mean"] = (round(th_mean, 6)
                                       if np.isfinite(th_mean) else None)
            fit["theoretical_std"] = (round(th_std, 6)
                                      if np.isfinite(th_std) else None)
            fit["mean_rel_err"] = (round(mean_rel_err, 4)
                                   if np.isfinite(mean_rel_err) else None)
            fit["std_rel_err"] = (round(std_rel_err, 4)
                                  if np.isfinite(std_rel_err) else None)
            fit["tail_ratio"] = (round(tail_ratio, 4)
                                 if np.isfinite(tail_ratio) else None)
            fit["ks_reliable"] = bool(ks_reliable)
            # KS-pass counts toward validity only when the test is reliable.
            ks_ok = fit["ks_pass"] if ks_reliable else True
            fit["valid"] = bool(moment_pass and tail_pass and ks_ok
                                and not degenerate)
            fit["advisory_only"] = not ks_reliable
            return fit

        def _fit_series(data: pd.Series, label: str = "overall") -> dict[str, Any]:
            d = pd.to_numeric(data, errors="coerce").dropna()
            if min_value is not None:
                d = d[d > min_value]
            n = len(d)
            if n < 10:
                return {
                    "label": label,
                    "error": f"Too few data points after filtering ({n}); need at least 10.",
                }

            emp_mean = float(d.mean())
            emp_std = float(d.std())
            emp_min = float(d.min())
            emp_max = float(d.max())
            ks_reliable = n >= min_parametric_n

            fits: list[dict[str, Any]] = []
            for dist_name in distributions:
                try:
                    dist = getattr(sp_stats, dist_name)
                    params = dist.fit(d)
                    ks_stat, p_value = sp_stats.kstest(d, dist_name, args=params)
                    log_lik = float(dist.logpdf(d, *params).sum())
                    k = len(params)
                    aic = 2 * k - 2 * log_lik
                    bic = k * np.log(n) - 2 * log_lik

                    shape_names = (
                        [s.strip() for s in dist.shapes.split(",")]
                        if dist.shapes
                        else []
                    )
                    param_names = shape_names + ["loc", "scale"]
                    param_dict = {
                        name: round(float(v), 6)
                        for name, v in zip(param_names, params)
                    }

                    fit = {
                        "distribution": dist_name,
                        "params": param_dict,
                        "ks_statistic": round(float(ks_stat), 6),
                        "p_value": round(float(p_value), 6),
                        "ks_pass": bool(p_value > 0.05),
                        "sum_log_likelihood": round(log_lik, 4),
                        "aic": round(aic, 2),
                        "bic": round(bic, 2),
                    }
                    _annotate_moments(dist, params, fit, emp_mean, emp_std,
                                      emp_min, emp_max, ks_reliable)
                    fits.append(fit)
                except Exception:
                    continue

            if not fits:
                return {"label": label, "error": "No distribution could be fitted."}

            # KDE fallback: triggered only when every parametric fit fails the KS test
            if all(not f["ks_pass"] for f in fits):
                try:
                    from scipy.stats import gaussian_kde

                    d_arr = d.to_numpy()
                    kde = gaussian_kde(d_arr)  # Scott's rule bandwidth

                    densities = kde.evaluate(d_arr)
                    densities = np.maximum(densities, np.finfo(float).tiny)
                    log_lik_kde = float(np.log(densities).sum())

                    k_kde = 1
                    aic_kde = 2 * k_kde - 2 * log_lik_kde
                    bic_kde = k_kde * np.log(n) - 2 * log_lik_kde

                    kde_samples = kde.resample(n, seed=0)[0]
                    ks_stat_kde, p_value_kde = sp_stats.ks_2samp(d_arr, kde_samples)

                    quantile_probs = list(range(0, 101, 5))
                    quantile_vals = {
                        str(p): round(float(np.percentile(d_arr, p)), 6)
                        for p in quantile_probs
                    }
                    # KDE is empirical-quantile based: moments track the data, so
                    # it is valid by construction (subject to KS reliability).
                    kde_mean = float(np.mean(d_arr))
                    kde_std = float(np.std(d_arr, ddof=1)) if n > 1 else 0.0

                    fits.append({
                        "distribution": "kde",
                        "params": {
                            "bandwidth": round(float(kde.factor), 6),
                            "bandwidth_method": "scott",
                        },
                        "quantiles": quantile_vals,
                        "ks_statistic": round(float(ks_stat_kde), 6),
                        "p_value": round(float(p_value_kde), 6),
                        "ks_pass": bool(p_value_kde > 0.05),
                        "sum_log_likelihood": round(log_lik_kde, 4),
                        "aic": round(aic_kde, 2),
                        "bic": round(bic_kde, 2),
                        "theoretical_mean": round(kde_mean, 6),
                        "theoretical_std": round(kde_std, 6),
                        "mean_rel_err": 0.0,
                        "std_rel_err": 0.0,
                        "tail_ratio": 1.0,
                        "ks_reliable": bool(ks_reliable),
                        "valid": True,
                        "degenerate": False,
                        "advisory_only": not ks_reliable,
                        "note": (
                            "Non-parametric KDE fallback (all parametric fits failed KS test). "
                            "Sample via: np.interp(np.random.uniform(), "
                            "np.linspace(0, 1, len(quantiles)), list(quantiles.values()))"
                        ),
                    })
                except Exception:
                    pass  # KDE failure is non-fatal; parametric results still returned

            # Rank: valid fits first, then by the chosen (penalised) criterion,
            # then by parameter count (parsimony tiebreaker — prefers e.g. norm
            # over a degenerate-but-not-caught lognorm at equal AIC).
            reverse = rank_by == "sum_log_likelihood"
            fits.sort(
                key=lambda x: (
                    not x.get("valid", False),
                    -x[rank_by] if reverse else x[rank_by],
                    len(x.get("params", {})),
                )
            )

            # Select best_fit subject to the small-N and validity policies.
            fallback = _empirical_fallback(d)
            if not ks_reliable:
                # Too few points to trust any parametric family.
                best_fit = fallback
                recommendation_reason = (
                    f"N={n} < min_parametric_n={min_parametric_n}: parametric fits "
                    "are advisory only; using bounded empirical fallback."
                )
            elif fits and fits[0].get("valid", False):
                best_fit = fits[0]
                recommendation_reason = "Best valid parametric/KDE fit by " + rank_by + "."
            else:
                best_fit = fallback
                recommendation_reason = (
                    "No parametric or KDE fit passed the moment/tail validity gate; "
                    "using bounded empirical fallback."
                )

            return {
                "label": label,
                "n_samples": n,
                "ranked_by": rank_by,
                "ks_reliable": bool(ks_reliable),
                "validity_gate": {
                    "moment_tol": moment_tol,
                    "std_tol": std_tol,
                    "tail_factor": tail_factor,
                    "min_parametric_n": min_parametric_n,
                },
                "empirical_stats": {
                    "mean": round(emp_mean, 4),
                    "std": round(emp_std, 4),
                    "min": round(float(d.min()), 4),
                    "max": round(emp_max, 4),
                    "median": round(float(d.median()), 4),
                    "skewness": round(float(d.skew()), 4),
                    "kurtosis": round(float(d.kurtosis()), 4),
                },
                "recommendation_reason": recommendation_reason,
                "best_fit": best_fit,
                "all_fits": fits,
            }

        if group_by:
            if group_by not in _df.columns:
                return {"error": f"group_by column '{group_by}' not found."}
            return {
                "column": column,
                "group_by": group_by,
                "filter": {"col": filter_col, "values": filter_values},
                "results": {
                    str(name): _fit_series(grp[column], label=str(name))
                    for name, grp in _df.groupby(group_by)
                },
            }

        return {
            "column": column,
            "filter": {"col": filter_col, "values": filter_values},
            "result": _fit_series(_df[column]),
        }

    return fit_distribution


def make_export_kde_quantiles(output_dir: str = "output/generated_reports/kde_quantiles"):
    """Return a tool that persists an empirical KDE quantile table to a CSV file.

    Call this immediately after ``fit_distribution`` returns a result whose
    ``best_fit["distribution"] == "kde"``.  The quantile dict is taken verbatim
    from the ``"quantiles"`` key of that KDE fit entry.

    One CSV file is written per (param_name, group_label) pair so each
    parameter's quantile table is self-contained and directly referenceable
    by the coding and evaluator agents.
    """

    _output_dir = os.path.join(os.getcwd(), output_dir)

    @tool(description=(
        "Persist an empirical KDE quantile table to a CSV file on disk. "
        "Call this whenever fit_distribution() returns a best_fit with "
        "distribution == 'kde'. The returned file path must be included in "
        "the distribution fitting report so downstream agents (evaluator, "
        "coding agent) can load the table for np.interp-based sampling. "
        f"Output directory: {_output_dir}"
    ))
    def export_kde_quantiles(
        param_name: str,
        group_label: str,
        quantiles: dict,
    ) -> str:
        """Write the KDE empirical quantile table for one parameter/group to CSV.

        The CSV has columns: param_name, group, percentile, value — one row
        per percentile point (21 rows for the default 0 %–100 % at 5 % steps).

        Args:
            param_name: Human-readable parameter name used in the filename and
                        the ``param_name`` CSV column. Example:
                        ``"processing_time_machine_A"``.
            group_label: Group key from the fit result's ``"label"`` field, or
                         ``"overall"`` for non-grouped fits.
            quantiles: The ``"quantiles"`` dict from the ``"kde"`` best_fit
                       entry — keys are percentile strings (``"0"`` … ``"100"``
                       at 5 % steps), values are floats.
        """
        os.makedirs(_output_dir, exist_ok=True)

        safe_param = re.sub(r"[^\w\-]", "_", str(param_name))
        safe_group = re.sub(r"[^\w\-]", "_", str(group_label))
        filename = f"{safe_param}__{safe_group}.csv"
        filepath = os.path.join(_output_dir, filename)

        rows = [
            {
                "param_name": param_name,
                "group": group_label,
                "percentile": int(k),
                "value": float(v),
            }
            for k, v in sorted(quantiles.items(), key=lambda x: int(x[0]))
        ]
        pd.DataFrame(rows).to_csv(filepath, index=False)

        return f"KDE quantile table written to {filepath}"

    return export_kde_quantiles


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
        outlier_threshold: float = 1.5,
    ) -> dict[str, Any]:
        """
        Compute processing time statistics grouped by a resource or activity column.

        Optionally filters rows by a time-type code column (e.g. keep only
        direct-work records before computing machine cycle times). Only
        positive durations above min_duration are included.

        Outlier detection is applied per group before computing statistics so
        that extreme values do not distort means and standard deviations.
        Detected outliers are reported but not silently dropped — the returned
        statistics always reflect the clean (outlier-removed) sample.

        Args:
            duration_col: Numeric column containing duration values.
            group_by_col: Column to group statistics by (typically the resource
                          or machine column).
            time_type_col: Column that encodes time categories (e.g. setup vs.
                           direct work). Supply together with time_type_filter.
            time_type_filter: List of time-type values to keep. Rows with other
                              values are excluded before computing statistics.
                              Example: ["D"] to keep only direct-work records.
            min_duration: Exclude durations at or below this value.
                          Default 0.0 removes non-positive entries.
            outlier_method: Method used to detect outliers within each group.
                            'iqr'    — Tukey fences (Q1 - k*IQR, Q3 + k*IQR).
                            'zscore' — values whose |z-score| exceeds the threshold.
                            'none'   — no outlier detection.
                            Default 'iqr'.
            outlier_threshold: Multiplier k for IQR (default 1.5, use 3.0 for
                               far-fence / less aggressive removal) or the
                               z-score cutoff when method='zscore'.
        """
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]

        for col in (duration_col, group_by_col):
            if col not in _df.columns:
                return {
                    "error": f"Column '{col}' not found.",
                    "available_columns": list(_df.columns),
                }

        if time_type_col and time_type_filter:
            if time_type_col not in _df.columns:
                return {"error": f"time_type_col '{time_type_col}' not found."}
            _df = _df[_df[time_type_col].isin(time_type_filter)]

        _df = _df.copy()
        _df[duration_col] = pd.to_numeric(_df[duration_col], errors="coerce")
        _df = _df[_df[duration_col] > min_duration]

        if _df.empty:
            return {
                "error": "No records remain after filtering.",
                "filter": {"time_type_col": time_type_col, "values": time_type_filter},
            }

        stats_dict: dict[str, Any] = {}
        all_clean_vals: list[pd.Series] = []

        for grp_name, grp_series in _df.groupby(group_by_col)[duration_col]:
            vals = grp_series.dropna()
            mask, lower, upper = _detect_outliers(vals, outlier_method, outlier_threshold)
            clean = vals[~mask]
            if len(clean) == 0:
                clean = vals  # fallback: keep all if every value is flagged
            all_clean_vals.append(clean)
            outlier_count = int(mask.sum())
            stats_dict[grp_name] = {
                "count": len(vals),
                "count_clean": len(clean),
                "mean": round(float(clean.mean()), 4),
                "std": round(float(clean.std()), 4),
                "min": round(float(clean.min()), 4),
                "max": round(float(clean.max()), 4),
                "median": round(float(clean.median()), 4),
                "outliers": {
                    "count": outlier_count,
                    "rate": round(outlier_count / len(vals), 4) if len(vals) > 0 else 0.0,
                    "method": outlier_method,
                    "threshold": outlier_threshold,
                    "lower_bound": round(lower, 4) if lower is not None else None,
                    "upper_bound": round(upper, 4) if upper is not None else None,
                },
            }

        combined_clean = pd.concat(all_clean_vals) if all_clean_vals else _df[duration_col]

        return {
            "group_by": group_by_col,
            "duration_column": duration_col,
            "filter": {"time_type_col": time_type_col, "values": time_type_filter},
            "min_duration_threshold": min_duration,
            "outlier_method": outlier_method,
            "outlier_threshold": outlier_threshold,
            "total_records": len(_df),
            "groups": len(stats_dict),
            "statistics": stats_dict,
            "overall": {
                "mean": round(float(combined_clean.mean()), 4),
                "std": round(float(combined_clean.std()), 4),
                "median": round(float(combined_clean.median()), 4),
            },
        }

    return extract_processing_times


# -----------------------------------------------------------------------------


def make_extract_inter_arrival_times(df: pd.DataFrame):
    """Return a tool that computes inter-arrival times between cases."""

    @tool
    def extract_inter_arrival_times(
        case_col: str,
        timestamp_col: str,
        group_by_col: str | None = None,
        unit: Literal["seconds", "minutes", "hours", "days"] = "minutes",
        outlier_method: Literal["none", "iqr", "zscore"] = "iqr",
        outlier_threshold: float = 1.5,
    ) -> dict[str, Any]:
        """
        Compute inter-arrival times (IAT) — the time between consecutive case
        arrivals — globally and optionally per resource or station.

        Arrival time per case is defined as the earliest timestamp for that
        case, ensuring each case contributes exactly one arrival event.
        Returns mean, std, min, max, median, and coefficient of variation (CV).
        CV > 1 suggests a non-Poisson, bursty arrival process.

        Outlier detection is applied to the IAT series before computing
        statistics. Very long idle gaps (e.g. weekends, shutdowns) that would
        otherwise inflate the mean and CV are detected and reported separately.

        Args:
            case_col: Column that uniquely identifies each case / work order.
            timestamp_col: Timestamp column used to determine arrival time.
                           The minimum value per case is used as the arrival.
            group_by_col: Optional column to compute per-group IATs in addition
                          to the global figure (e.g. per resource or shift).
            unit: Time unit for IAT values.
                  One of 'seconds', 'minutes', 'hours', 'days'. Default 'minutes'.
            outlier_method: Method used to detect outlier inter-arrival gaps.
                            'iqr'    — Tukey fences (Q1 - k*IQR, Q3 + k*IQR).
                            'zscore' — values whose |z-score| exceeds the threshold.
                            'none'   — no outlier detection.
                            Default 'iqr'.
            outlier_threshold: Multiplier k for IQR (default 1.5) or the
                               z-score cutoff when method='zscore'.
        """
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]

        for col in (case_col, timestamp_col):
            if col not in _df.columns:
                return {
                    "error": f"Column '{col}' not found.",
                    "available_columns": list(_df.columns),
                }

        divisors = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}
        _df = _df.copy()
        _df[timestamp_col] = pd.to_datetime(_df[timestamp_col], errors="coerce")

        def _iat_stats(arrivals: pd.Series, label: str = "global") -> dict[str, Any]:
            arrivals = arrivals.sort_values().dropna()
            iat = arrivals.diff().dt.total_seconds().dropna() / divisors[unit]
            iat_pos = iat[iat > 0]
            if len(iat_pos) < 2:
                return {"label": label, "error": "Too few arrivals to compute IAT."}

            mask, lower, upper = _detect_outliers(iat_pos, outlier_method, outlier_threshold)
            clean_iat = iat_pos[~mask]
            if len(clean_iat) < 2:
                clean_iat = iat_pos  # fallback: keep all if too many flagged
            outlier_count = int(mask.sum())

            mean = float(clean_iat.mean())
            std = float(clean_iat.std())
            return {
                "label": label,
                "cases": int(len(arrivals)),
                "mean": round(mean, 4),
                "std": round(std, 4),
                "min": round(float(clean_iat.min()), 4),
                "max": round(float(clean_iat.max()), 4),
                "median": round(float(clean_iat.median()), 4),
                "cv": round(std / mean, 4) if mean > 0 else None,
                "outliers": {
                    "count": outlier_count,
                    "rate": round(outlier_count / len(iat_pos), 4) if len(iat_pos) > 0 else 0.0,
                    "method": outlier_method,
                    "threshold": outlier_threshold,
                    "lower_bound": round(lower, 4) if lower is not None else None,
                    "upper_bound": round(upper, 4) if upper is not None else None,
                },
            }

        # Global: first arrival per case
        case_arrivals = _df.groupby(case_col)[timestamp_col].min()
        result: dict[str, Any] = {
            "unit": unit,
            "outlier_method": outlier_method,
            "outlier_threshold": outlier_threshold,
            "global": _iat_stats(case_arrivals),
        }

        if group_by_col:
            if group_by_col not in _df.columns:
                return {"error": f"group_by_col '{group_by_col}' not found."}
            per_group: dict[str, Any] = {}
            for name, grp in _df.groupby(group_by_col):
                arrivals = grp.groupby(case_col)[timestamp_col].min()
                per_group[str(name)] = _iat_stats(arrivals, label=str(name))
            result["by_" + group_by_col] = per_group

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
        outlier_threshold: float = 1.5,
    ) -> dict[str, Any]:
        """
        Compute grouped descriptive statistics (count, mean, std, min, max,
        median) for any numeric column. Supports optional row filtering and
        custom percentile computation.

        Use this as a flexible fallback when the dedicated extraction tools
        do not fit the analysis need — for example, grouping by a combination
        of columns, or computing statistics for a custom filtered subset.

        Outlier detection is applied per group before computing statistics.
        Detected outliers are reported alongside clean statistics so that
        extreme values are visible but do not skew simulation parameters.

        Args:
            value_col: Numeric column to aggregate.
            group_by: One or more columns to group by. Pass as a list, e.g.
                      ["resource"] or ["resource", "product"].
            filter_col: Column to filter rows on before aggregating.
            filter_values: Exact values to keep in filter_col.
            min_value: Exclude rows where value_col is at or below this
                       threshold. Pass None to disable.
            percentiles: Additional percentiles to compute, e.g. [0.90, 0.95].
                         Results appear as 'p90', 'p95', etc. alongside the
                         standard aggregations. Computed on clean data only.
            outlier_method: Method used to detect outliers within each group.
                            'iqr'    — Tukey fences (Q1 - k*IQR, Q3 + k*IQR).
                            'zscore' — values whose |z-score| exceeds the threshold.
                            'none'   — no outlier detection.
                            Default 'iqr'.
            outlier_threshold: Multiplier k for IQR (default 1.5) or the
                               z-score cutoff when method='zscore'.
        """
        _df = df.loc[:, df.columns.str.strip() != ""]
        _df = _df.loc[:, ~_df.columns.str.contains("^Unnamed")]

        if value_col not in _df.columns:
            return {
                "error": f"Column '{value_col}' not found.",
                "available_columns": list(_df.columns),
            }

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
        pct_results: dict[str, Any] = {}

        for name, grp in _df.groupby(group_by):
            key = name if not isinstance(name, tuple) else str(name)
            vals = grp[value_col].dropna()
            mask, lower, upper = _detect_outliers(vals, outlier_method, outlier_threshold)
            clean = vals[~mask]
            if len(clean) == 0:
                clean = vals  # fallback: keep all if every value is flagged
            outlier_count = int(mask.sum())
            stats_dict[key] = {
                "count": len(vals),
                "count_clean": len(clean),
                "mean": round(float(clean.mean()), 4),
                "std": round(float(clean.std()), 4),
                "min": round(float(clean.min()), 4),
                "max": round(float(clean.max()), 4),
                "median": round(float(clean.median()), 4),
                "outliers": {
                    "count": outlier_count,
                    "rate": round(outlier_count / len(vals), 4) if len(vals) > 0 else 0.0,
                    "method": outlier_method,
                    "threshold": outlier_threshold,
                    "lower_bound": round(lower, 4) if lower is not None else None,
                    "upper_bound": round(upper, 4) if upper is not None else None,
                },
            }
            if percentiles:
                pct_results[key] = {
                    f"p{int(p * 100)}": round(float(clean.quantile(p)), 4)
                    for p in percentiles
                }

        result: dict[str, Any] = {
            "value_column": value_col,
            "group_by": group_by,
            "filter": {"col": filter_col, "values": filter_values},
            "min_value_threshold": min_value,
            "outlier_method": outlier_method,
            "outlier_threshold": outlier_threshold,
            "total_records": len(_df),
            "groups": len(stats_dict),
            "statistics": stats_dict,
        }

        if percentiles:
            result["percentiles"] = pct_results

        return result

    return compute_grouped_statistics


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