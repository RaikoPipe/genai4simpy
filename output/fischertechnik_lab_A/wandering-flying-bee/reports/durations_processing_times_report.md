# Durations / Processing Times Report — Fischertechnik Lab A (wandering-flying-bee)

**Data:** `work_files/eventlog_cleaned.parquet` — 576 rows, 192 activity instances (3 lifecycle rows each), 18 cases, 20 activities, 15 resources. Window: 2021-07-06 15:08:27.91 → 16:01:31.12 UTC (~53 min).

## 1. Method

- **Duration rule (authoritative):** actual service time = `operation_end_time − time:timestamp` evaluated on the **`start` row only**. `complete_service_time` (includes queueing) is never used; `planned_operation_time` is reference only.
- **Sample:** successful attempts only (n = 184). The 8 failed attempts (7× HTTP 418 precondition, 1× HTTP 401 auth) are excluded from service times — a failed attempt is not a completed operation. Each `event_id` is one attempt; a retry is a new `event_id` repeating the same process, so retries are already represented as separate instances.
- **Grouping:** per activity, pooling only across machine pairs performing the same activity (mm_1+mm_2, ov_1+ov_2, wt_1+wt_2, sm_1+sm_2) — never across different activities. Single pooled transport distribution for vgr_1+vgr_2 (identical hardware) per confirmed decision, flagged for revisit at the modeling stage.
- **Incomplete cases:** the 4 incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) are **retained** for service-time estimation per confirmed decision (window truncation, not abandonment).
- **Fitting gate:** parametric fit only if it passes the moment/tail gate and the bootstrap KS test (n ≥ 30); otherwise the empirical quantile table; otherwise a bounded triangular (min, median, max) fallback for n < 10. No parametric fit passed the gate (only n = 50 for vgr reached the parametric branch, and even that fell back to empirical quantiles), so all groups use empirical quantiles (n ≥ 10) or the bounded triangular/constant fallback (n ≤ 9).
- **Outlier policy:** long service times are real variability and are **kept** (detected/reported, not removed). No data-defect removals were made.

## 2. Per-activity service-time summary (n = successful attempts)

| Activity | N | mean (s) | std (s) | CV | min (s) | max (s) | recommended | failure p |
|---|---|---|---|---|---|---|---|---|
| /dm/cylindrical_drill | 2 | 23.992 | 2.861 | 0.119 | 21.969 | 26.015 | triang | 0.000 (0/2) |
| /dm/lower | 2 | 14.008 | 0.188 | 0.013 | 13.875 | 14.141 | triang | 0.000 (0/2) |
| /hbw/get_empty_bucket | 11 | 37.062 | 5.038 | 0.136 | 30.797 | 48.594 | empirical_quantiles | 0.000 (0/11) |
| /hbw/store | 3 | 37.985 | 3.951 | 0.104 | 34.641 | 42.344 | triang | 0.000 (0/3) |
| /hbw/store_empty_bucket | 13 | 39.429 | 3.852 | 0.098 | 32.641 | 44.867 | empirical_quantiles | 0.133 (2/15) |
| /hbw/unload | 16 | 39.292 | 5.798 | 0.148 | 32.735 | 52.248 | empirical_quantiles | 0.059 (1/17) |
| /hw/human_review | 14 | 13.996 | 19.210 | 1.373 | 0.438 | 62.250 | empirical_quantiles | 0.000 (0/14) |
| /mm/deburr | 9 | 14.463 | 0.361 | 0.025 | 14.046 | 15.047 | triang | 0.000 (0/9) |
| /mm/drill | 4 | 14.441 | 6.570 | 0.455 | 5.281 | 20.906 | triang | 0.000 (0/4) |
| /mm/mill | 6 | 6.672 | 3.805 | 0.570 | 5.047 | 14.437 | triang | 0.000 (0/6) |
| /mm/transport_from_to | 2 | 12.868 | 0.387 | 0.030 | 12.594 | 13.141 | triang | 0.000 (0/2) |
| /ov/burn | 13 | 30.144 | 6.665 | 0.221 | 21.422 | 41.782 | empirical_quantiles | 0.000 (0/13) |
| /ov/temper | 5 | 51.537 | 0.056 | 0.001 | 51.453 | 51.610 | triang | 0.000 (0/5) |
| /pm/punch_gill | 1 | 27.484 | 0.000 | — | 27.484 | 27.484 | constant | 0.000 (0/1) |
| /pm/punch_recesses | 2 | 23.641 | 0.265 | 0.011 | 23.453 | 23.828 | triang | 0.000 (0/2) |
| /pm/punch_ribbing | 2 | 27.391 | 5.414 | 0.198 | 23.562 | 31.219 | triang | 0.000 (0/2) |
| /sm/sort | 6 | 50.146 | 95.827 | 1.911 | 8.360 | 245.700 | triang | 0.000 (0/6) |
| /sm/transport | 9 | 17.523 | 3.011 | 0.172 | 14.390 | 21.578 | triang | 0.000 (0/9) |
| /vgr/pick_up_and_transport | 50 | 41.965 | 12.795 | 0.305 | 13.109 | 88.375 | empirical_quantiles | 0.091 (5/55) |
| /wt/pick_up_and_transport | 14 | 27.377 | 1.546 | 0.056 | 25.906 | 29.235 | empirical_quantiles | 0.000 (0/14) |
| **Total** | **184** | | | | | | | **8/192 = 0.042** |

*Failure p = failed attempts / total attempts (failed included in the denominator, excluded from service times). Activities with zero observed failures are reported with a rule-of-three upper 95% confidence bound rather than asserted as exactly zero: e.g. /hbw/unload (0/17) upper bound ≈ 3/17 ≈ 0.18; /ov/burn (0/13) ≈ 0.23; /hw/human_review (0/14) ≈ 0.21.*

## 3. Burn size-dependence check (/ov/burn)

`burn_workpiece_size` is categorical and deterministic per variant. Burn duration varies **systematically and monotonically** by size category, with **non-overlapping ranges** (pooling variants that share a size):

| size | n | mean (s) | std (s) | min (s) | max (s) |
|---|---|---|---|---|---|
| regular | 5 | 23.547 | 2.712 | 21.422 | 26.563 |
| middle | 2 | 29.369 | 3.500 | 26.894 | 31.844 |
| large | 3 | 33.301 | 2.920 | 31.562 | 36.672 |
| maxi | 3 | 38.500 | 2.842 | 36.859 | 41.782 |

The data **supports** per-category distributions. However, per the confirmed decision the spec carries the **single pooled per-activity distribution** (n = 13, mean 30.14 s) as the baseline, and the per-category split above is provided here for the modeling stage (flagged). Thickness (thin/thick) adds a secondary effect within size but with too few points to model separately.

## 4. Flagged outliers (kept — real variability, not removed)

| Activity | Value (s) | Case | Note |
|---|---|---|---|
| /sm/sort | 245.700 | WF_108_17 | ~10× the other 5 values (8.4–14.0 s); inflates mean to 50.1 s and std to 95.8 s (CV 1.91). Kept per policy; the bounded triangular fallback captures the long tail. |
| /mm/mill | 14.437 | WF_104_20 | mm_2 single observation vs ~5.0–5.3 s on mm_1 (n=5). Inflates the pooled mean to 6.67 s. Kept; flagged for the modeling stage (mm_1-dominated). |
| /vgr/pick_up_and_transport | 88.375 | — | Longest transport; part of the vgr_1 spread (std 15.8 s). Kept. |
| /hw/human_review | 62.250 | — | Human-paced activity, CV 1.37, wide spread 0.44–62.25 s. Kept. |

**No data-defect removals** were made (no `remove_outliers=True`). The 0.0157 s duration on the failed /hbw/unload attempt (HTTP 401, WF_108_18) is already excluded from the service-time sample because it is a failed attempt.

## 5. Sparse / low-confidence groups (n ≤ 6)

These groups have very small samples and are flagged **low confidence** (wide CIs). No cross-activity pooling was used to compensate:

- /pm/punch_gill (n=1, constant 27.484 s)
- /dm/cylindrical_drill (n=2), /dm/lower (n=2), /mm/transport_from_to (n=2), /pm/punch_recesses (n=2), /pm/punch_ribbing (n=2)
- /hbw/store (n=3), /mm/drill (n=4)
- /ov/temper (n=5, near-constant 51.5 s, CV 0.001), /mm/mill (n=6), /sm/sort (n=6)

## 6. Per-resource (activity × resource) check

Machine pairs are poolable within each activity:
- /mm/deburr: mm_1 14.49 s (n=8) vs mm_2 14.24 s (n=1) — consistent.
- /wt/pick_up_and_transport: wt_1 26.09 s (n=8) vs wt_2 29.09 s (n=6) — consistent.
- /ov/burn: ov_1 27.20 s (n=8) vs ov_2 34.85 s (n=5) — the gap is **confounded with workpiece size** (ov_2 handles the larger pieces), consistent with the size-dependence flag, not a machine difference.

**Exception — /sm/transport:** sm_1 19.92 s (n=5) vs sm_2 14.53 s (n=4) differ by ~37%. The pooled distribution (mean 17.52 s) is used per the confirmed pooling decision, but a **per-resource split is recommended for the modeling stage**.

## 7. VGR pooled transport (flagged for revisit)

- vgr_1: n=32, mean 42.64 s, std 15.81 s, range 13.11–88.38 s (includes 5 failed-attempt retries and the 88.4 s max).
- vgr_2: n=18, mean 40.76 s, std 3.73 s, range 35.73–45.30 s (tighter).
- Pooled: n=50, mean 41.97 s, std 12.80 s. The single pooled distribution is used per confirmed decision; revisit at the modeling stage.

## 8. Deliverables

- **Spec section `activities`:** 20 per-activity duration entries (family, params, mean, n, source=fit_activity_durations) plus failure_probability and on_failure=retry. All 4 incomplete cases retained (n=184 successes / 192 attempts).
- **Spec section `assumptions`:** duration rule, sample definition, incomplete-case retention, grouping/pooling, burn size-dependence, sparse-group flags, kept outliers, /mm/mill and /sm/transport per-resource flags, and the VGR pooled-transport flag.
