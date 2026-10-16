# Durations & Processing Times Report — fischertechnik_lab_C (run: foamy-ancient-hornet)

## 1. Methodology

- **Dataset**: `eventlog_cleaned.parquet` — 1,137 rows, 379 activity instances, 37 cases, 21 activities, 15 resources, horizon ≈ 5,461.5 s.
- **Service time** = `operation_end_time` − `time:timestamp` on the **start row only** (lifecycle transition `start`). This measures busy service time and excludes queueing.
- **Grouping**: per activity, pooled across resources (per the extraction plan; per-resource splits would leave ~9 samples/cell). Per-resource breakdowns are reported as a sanity check (§4).
- **Distribution fitting**: `fit_activity_durations` with a moment/tail gate + bootstrap KS test; parametric only when it passes, else the empirical quantile table, else triangular/constant fallback for N < 10. Failed attempts are excluded from duration fits (`include_failures=False`) but count toward failure probabilities.
- **Exclusions** (data defects, documented in §5): the 0.031 s `/hbw/unload` instance (WF_101_28, confirmed NFC 418 data error per plan), the 0.047 s `/hbw/unload` instance (WF_101_26, same failure mode), and 2 zero-duration `/hw/human_review` start rows (logging artifact). 372 of 379 instances remain usable.
- **Benchmark** (§6): `complete_service_time` (scheduled → complete, incl. queueing) vs `planned_operation_time` (target) — for comparison only, never used for service-time extraction.
- **Hand-off delay** (§7): explicit vgr → hbw transfer delay, estimated separately and NOT folded into vgr service times.

## 2. Per-Activity Service-Time Summary

Statistics below are the tool's fitted-sample statistics (failed attempts and the two zero-duration human_review rows excluded). "Recommended" is the distribution written to the spec `activities` section (copied verbatim from `fit_activity_durations` / `draft_activities_spec`).

| Activity | N | mean (s) | std (s) | CV | min (s) | max (s) | Recommended | failure p |
|---|---|---|---|---|---|---|---|---|
| /vgr/pick_up_and_transport | 101 | 36.270 | 11.968 | 0.330 | 10.843 | 52.203 | triang (c=0.977, loc=4.833, scale=47.717) | 0.0288 |
| /hbw/unload | 35 | 38.249 | 5.220 | 0.137 | 31.593 | 51.200 | triang (c≈0, loc=31.593, scale=21.134) | 0.0541 |
| /hbw/store_empty_bucket | 34 | 37.013 | 3.702 | 0.100 | 31.734 | 44.031 | uniform (loc=31.734, scale=12.297) | 0.0 |
| /ov/burn | 32 | 30.453 | 6.054 | 0.199 | 21.421 | 41.532 | uniform (loc=21.421, scale=20.111) | 0.0 |
| /wt/pick_up_and_transport | 29 | 27.715 | 1.692 | 0.061 | 25.812 | 29.531 | empirical_quantiles | 0.0 |
| /mm/deburr | 19 | 17.053 | 11.998 | 0.704 | 13.843 | 66.562 | empirical_quantiles | 0.0 |
| /sm/transport | 19 | 18.920 | 9.821 | 0.519 | 14.219 | 58.328 | empirical_quantiles | 0.0 |
| /hw/human_review | 15 | 46.810 | 54.253 | 1.159 | 0.328 | 185.063 | empirical_quantiles | 0.0 |
| /hbw/get_empty_bucket | 14 | 38.381 | 4.226 | 0.110 | 32.953 | 48.109 | empirical_quantiles | 0.0 |
| /hbw/store | 13 | 37.200 | 3.437 | 0.092 | 30.734 | 40.188 | empirical_quantiles | 0.0 |
| /sm/sort | 13 | 11.775 | 3.347 | 0.284 | 8.578 | 21.266 | empirical_quantiles | 0.0 |
| /mm/mill | 11 | 8.713 | 4.451 | 0.511 | 5.078 | 14.453 | empirical_quantiles | 0.0 |
| /ov/temper | 8 | 51.717 | 0.520 | 0.010 | 51.437 | 53.000 | triang (c=0.070, loc=51.437, scale=1.563) | 0.0 |
| /mm/drill | 8 | 13.711 | 9.056 | 0.661 | 5.078 | 32.203 | triang (c=0.357, loc=5.078, scale=27.125) | 0.0 |
| /pm/punch_gill | 4 | 26.559 | 1.809 | 0.068 | 23.859 | 27.688 | triang (c=0.910, loc=23.859, scale=3.829) | 0.0 |
| /dm/lower | 4 | 13.840 | 0.008 | 0.001 | 13.828 | 13.844 | triang (c=0.969, loc=13.828, scale=0.016) | 0.0 |
| /dm/drill | 4 | 27.129 | 10.935 | 0.403 | 15.812 | 41.954 | triang (c=0.366, loc=15.812, scale=26.142) | 0.0 |
| /mm/transport_from_to | 3 | 12.349 | 0.130 | 0.011 | 12.203 | 12.453 | triang (c=0.752, loc=12.203, scale=0.250) | 0.0 |
| /dm/cylindrical_drill | 2 | 42.953 | 5.480 | 0.128 | 39.078 | 46.828 | triang (c=0.5, loc=39.078, scale=7.75) | 0.0 |
| /pm/punch_ribbing | 2 | 23.571 | 0.320 | 0.014 | 23.344 | 23.797 | triang (c=0.5, loc=23.344, scale=0.453) | 0.0 |
| /pm/punch_recesses | 2 | 23.751 | 0.111 | 0.005 | 23.672 | 23.829 | triang (c=0.5, loc=23.672, scale=0.157) | 0.0 |

Notes:
- **/ov/burn** uses the observed actual durations (mean 30.45 s), **not** the planned 222 s — the twin models actual behaviour (planned value is ~7× the observed; see §6).
- **Small-sample activities** (n < 5): `/dm/cylindrical_drill`, `/dm/drill`, `/dm/lower`, `/pm/punch_gill`, `/pm/punch_recesses`, `/pm/punch_ribbing`, `/mm/transport_from_to` — triangular/constant fallbacks with wide uncertainty; the distribution-fitting-agent will review these fits.
- **Flagged outliers (kept, real variability)**: `/mm/deburr` max 66.56 s (mm_1), `/sm/transport` max 58.33 s (sm_1), `/hw/human_review` max 185.06 s (operator review duration), `/vgr` min 10.84 s. These are long service times the simulation must reproduce, not data defects.
- **Failure probabilities** (failed attempts / all attempts, observed event rates — too sparse for per-activity distributions, retained as observed rates per plan): `/hbw/unload` 2/37 = 0.0541 (NFC 418 missing-workpiece), `/vgr/pick_up_and_transport` 3/104 = 0.0288 (NFC 418). All other activities: 0.

## 3. vgr → hbw Hand-off Delay (explicit transfer delay)

For each `/hbw/get_empty_bucket` and `/hbw/store` start, the gap between completion of the case's preceding `/vgr/pick_up_and_transport` and the hbw start was computed (27 gaps total). Gaps were classified by whether hbw_1 was **idle** while the case waited (no busy interval overlapping the gap window).

- **Idle gaps (22)**: mean 12.92 s, median 4.23 s, min 2.35 s, max 122.18 s.
- **Busy gaps (5)**: 67.6–195.4 s — pure queueing, not transfer delay; excluded.

The idle gaps split into two distinct populations:

| Population | N | mean (s) | std (s) | min (s) | median (s) | max (s) |
|---|---|---|---|---|---|---|
| /hbw/store (consistent physical transfer) | 13 | 3.546 | 1.117 | 2.353 | 3.384 | 6.656 |
| /hbw/get_empty_bucket (operator/bucket-availability waiting) | 9 | 26.460 | 37.011 | 5.478 | 12.328 | 122.182 |

**Modelled hand-off delay** (spec activity `vgr_to_hbw_handoff_delay`): the 13 `/hbw/store` idle gaps — a tight, consistent physical transfer (CV 0.31). Empirical quantile table, mean 3.55 s. The 9 `/hbw/get_empty_bucket` idle gaps (up to 122 s) reflect additional operator/bucket-availability waiting beyond the physical transfer and are **not** folded into either the base transfer delay or the vgr service times.

## 4. Per-Resource Sanity Check (pooled per plan)

Per-activity × resource breakdowns (usable instances only). Differences track the per-resource **planned** times, i.e. they are real machine/operation differences, not noise:

| Activity | Resource | N | mean (s) | std (s) | planned (s) |
|---|---|---|---|---|---|
| /mm/mill | mm_1 | 7 | 5.518 | 0.483 | 5 |
| /mm/mill | mm_2 | 4 | 14.305 | 0.206 | 14 |
| /wt/pick_up_and_transport | wt_1 | 14 | 25.998 | 0.082 | 22 |
| /wt/pick_up_and_transport | wt_2 | 15 | 29.318 | 0.127 | 27 |
| /sm/transport | sm_1 | 9 | 23.625 | 13.025 | 18 |
| /sm/transport | sm_2 | 10 | 14.686 | 0.266 | 15 |
| /vgr/pick_up_and_transport | vgr_1 | 63 | 33.721 | 14.156 | 15–47 |
| /vgr/pick_up_and_transport | vgr_2 | 36 | 39.958 | 4.176 | 32–47 |
| /ov/burn | ov_1 | 14 | 27.286 | 5.539 | 222 |
| /ov/burn | ov_2 | 18 | 32.917 | 5.357 | 222 |
| /mm/deburr | mm_1 | 14 | 18.076 | 13.966 | 14 |
| /mm/deburr | mm_2 | 5 | 14.188 | 0.087 | 15 |
| /sm/sort | sm_1 | 6 | 12.518 | 0.981 | 12 |
| /sm/sort | sm_2 | 7 | 11.138 | 4.536 | 11 |

All other activities are single-resource (hbw_1/hbw_2, ov_1, pm_1, dm_2, hw_1). Per the plan, pooled per-activity values are used in the spec; the calibration phase may split `/mm/mill`, `/wt`, `/sm/transport`, `/vgr` if the twin needs resource-specific times.

## 5. Data-Defect Exclusions (removed from statistics and fits)

| Instance | Activity | Recorded dur (s) | Reason |
|---|---|---|---|
| WF_101_28 | /hbw/unload | 0.031 | Confirmed data error (NFC 418 missing-workpiece failure; start→complete in 31 ms) — excluded per extraction plan |
| WF_101_26 | /hbw/unload | 0.047 | Same failure mode (NFC 418); failed attempt, excluded from fits by `include_failures=False` |
| WF_1106_16 | /hw/human_review | 0.000 | Logging artifact: start-row end timestamp equals start timestamp; actual review took ~1.3 s (complete_service_time 2.95 s incl. queue) |
| WF_102_28 | /hw/human_review | 0.000 | Same artifact; actual review ~0.8 s (complete_service_time 3.66 s) |

No censored cases (0 left-, 0 right-censored); early-exit/scrap cases are retained for estimation.

## 6. Actual-vs-Target Benchmark (complete_service_time vs planned_operation_time)

`complete_service_time` includes queueing, so ratios > 1 are dominated by waiting, not service. Used for context only.

| Activity | N | actual mean (s) | planned mean (s) | ratio |
|---|---|---|---|---|
| /vgr/pick_up_and_transport | 278 | 62.27 | 34.03 | 1.83 |
| /hbw/unload | 37 | 502.96 | 52.00 | 9.67 |
| /hbw/store_empty_bucket | 36 | 42.30 | 47.00 | 0.90 |
| /ov/burn | 34 | 37.24 | 222.00 | 0.17 |
| /wt/pick_up_and_transport | 31 | 38.17 | 24.74 | 1.54 |
| /mm/deburr | 19 | 22.83 | 14.26 | 1.60 |
| /sm/transport | 19 | 22.82 | 16.42 | 1.39 |
| /hw/human_review | 17 | 45.65 | 102.00 | 0.45 |
| /sm/sort | 15 | 16.43 | 11.40 | 1.44 |
| /hbw/get_empty_bucket | 14 | 43.80 | 46.00 | 0.95 |
| /hbw/store | 13 | 42.00 | 46.00 | 0.91 |
| /mm/mill | 11 | 14.40 | 8.27 | 1.74 |
| /ov/temper | 8 | 58.55 | 56.00 | 1.05 |
| /mm/drill | 8 | 19.64 | 18.25 | 1.08 |
| /pm/punch_gill | 4 | 30.46 | 35.00 | 0.87 |
| /dm/lower | 4 | 18.16 | 14.00 | 1.30 |
| /dm/drill | 4 | 30.40 | 42.00 | 0.72 |
| /mm/transport_from_to | 3 | 20.30 | 12.00 | 1.69 |
| /dm/cylindrical_drill | 2 | 47.64 | 47.00 | 1.01 |
| /pm/punch_ribbing | 2 | 26.70 | 39.00 | 0.68 |
| /pm/punch_recesses | 2 | 30.16 | 39.00 | 0.77 |

Observations: `/hbw/unload` actual end-to-end is ~9.7× planned — the infeed queue at hbw_2 is the dominant system bottleneck (cases wait minutes for the bucket station). `/ov/burn` actual is ~17% of planned (222 s target vs ~30 s actual), confirming the planned value does not represent real oven behaviour.

## 7. Caveats

1. **/hw/human_review lower tail**: 5 of 17 instances have unreliable start-row end timestamps (recorded 0.0–0.875 s vs actual 1.3–2.8 s per complete_service_time). The empirical quantile table keeps the recorded values, so the lower tail may be slightly compressed; the median (27.1 s) and upper tail (up to 185 s) are reliable. CV 1.16 reflects genuinely variable operator review times.
2. **Small samples**: 7 activities have n < 5; their triangular/constant fallbacks carry wide uncertainty (e.g. /dm/drill CV 0.40 from 4 samples). The distribution-fitting-agent will review all fits.
3. **Pooled resources**: per-resource differences exist (notably /mm/mill 5.5 vs 14.3 s, /sm/transport 23.6 vs 14.7 s, /vgr 33.7 vs 40.0 s) and track planned times; pooled values are used per the extraction plan and may be split during calibration.
4. **Hand-off delay**: the base transfer delay (3.55 s) is estimated from 13 /hbw/store idle gaps only. The 9 /hbw/get_empty_bucket idle gaps (5.5–122 s) include operator/bucket-availability waiting and are not modelled in the base delay; if the twin underestimates get_empty_bucket waiting, this is the first place to look.
5. **Failure rates** are observed event rates (5 failures / 379 instances), too sparse for per-activity failure distributions; per the plan they are retained as observed rates and refined in calibration. WF_104 rework pass/fail probability is deferred to calibration (3 cases, not estimable).
6. **Long service times kept**: /mm/deburr 66.6 s, /sm/transport 58.3 s, /hw/human_review 185.1 s are real variability (Tukey far-fence outliers), not data defects — retained per the statistics policy.
