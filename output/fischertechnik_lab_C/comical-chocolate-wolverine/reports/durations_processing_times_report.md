# Durations & Processing Times Report — fischertechnik_lab_C

**Window:** 2021-07-01 18:48:23.227 → 20:19:24.734 UTC (≈5,461.5 s)
**Data:** 1,137 rows → 379 `start` lifecycle rows (100% coverage, no missing end times), 37 cases, 21 activities.

## 1. Measurement definition (confirmed decision)

- **Duration = `operation_end_time` − `time:timestamp`, evaluated on the `start` lifecycle row only.** `complete` rows show up to <30 s of per-row logging drift, and `complete_service_time` includes queueing — neither is used for service durations.
- **Grouping: per activity only (21 activities)**, pooling across track instances (ov_1/ov_2, mm_1/mm_2, wt_1/wt_2, sm_1/sm_2) and the shared hbw_1/hbw_2, vgr_1/vgr_2 pools. The topology shows no resource-specific service-time behaviour (no machine contention; hbw/vgr form single shared pools), so no activity × resource splits.
- **Included:** all 379 start rows — including completed steps of the 19 missing-data stub cases and the 5 real scrap cases (valid service observations).
- **Excluded from duration fits only:** the 5 failed attempts (2 × `/hbw/unload`, 3 × `/vgr/pick_up_and_transport`) — see §4.

## 2. Per-activity service-time parameters

Source: `fit_activity_durations` (group_by=activity, all 379 rows). Gate: parametric fit only if N≥30 and moment/tail gate + bootstrap KS pass; else empirical quantile table (10 ≤ N < 30); else triangular(min, median, max) fallback (N < 10). All values in seconds.

| Activity | N | mean | std | CV | min | max | recommended | failure p |
|---|---|---|---|---|---|---|---|---|
| /vgr/pick_up_and_transport | 101 | 36.270 | 11.968 | 0.330 | 10.843 | 52.203 | triang(c=0.9767, loc=4.833, scale=47.717) | 0.0288 |
| /hbw/store_empty_bucket | 34 | 37.013 | 3.702 | 0.100 | 31.734 | 44.031 | uniform(31.734, 44.031) | 0.0 |
| /ov/burn | 32 | 30.453 | 6.054 | 0.199 | 21.421 | 41.532 | uniform(21.421, 41.532) | 0.0 |
| /wt/pick_up_and_transport | 29 | 27.715 | 1.692 | 0.061 | 25.812 | 29.531 | empirical_quantiles | 0.0 |
| /mm/deburr | 19 | 17.053 | 11.998 | 0.704 | 13.843 | 66.562 | empirical_quantiles | 0.0 |
| /sm/transport | 19 | 18.920 | 9.822 | 0.519 | 14.219 | 58.328 | empirical_quantiles | 0.0 |
| /hw/human_review | 17 | 41.303 | 53.077 | 1.285 | 0.000 | 185.063 | empirical_quantiles | 0.0 |
| /hbw/get_empty_bucket | 14 | 38.381 | 4.226 | 0.110 | 32.953 | 48.109 | empirical_quantiles | 0.0 |
| /hbw/store | 13 | 37.200 | 3.437 | 0.092 | 30.734 | 40.188 | empirical_quantiles | 0.0 |
| /sm/sort | 13 | 11.775 | 3.347 | 0.284 | 8.578 | 21.266 | empirical_quantiles | 0.0 |
| /mm/mill | 11 | 8.713 | 4.451 | 0.511 | 5.078 | 14.453 | empirical_quantiles | 0.0 |
| /mm/drill | 8 | 13.711 | 9.056 | 0.660 | 5.078 | 32.203 | triang (fallback) | 0.0 |
| /ov/temper | 8 | 51.717 | 0.520 | 0.010 | 51.437 | 53.000 | triang (fallback) | 0.0 |
| /dm/drill | 4 | 27.129 | 10.935 | 0.403 | 15.812 | 41.954 | triang (fallback) | 0.0 |
| /dm/lower | 4 | 13.840 | 0.008 | 0.001 | 13.828 | 13.844 | triang (fallback) | 0.0 |
| /pm/punch_gill | 4 | 26.559 | 1.809 | 0.068 | 23.859 | 27.688 | triang (fallback) | 0.0 |
| /mm/transport_from_to | 3 | 12.349 | 0.130 | 0.010 | 12.203 | 12.453 | triang (fallback) | 0.0 |
| /dm/cylindrical_drill | 2 | 42.953 | 5.480 | 0.128 | 39.078 | 46.828 | triang (fallback) | 0.0 |
| /pm/punch_recesses | 2 | 23.751 | 0.111 | 0.005 | 23.672 | 23.829 | triang (fallback) | 0.0 |
| /pm/punch_ribbing | 2 | 23.571 | 0.320 | 0.014 | 23.344 | 23.797 | triang (fallback) | 0.0 |
| /hbw/unload | 35 | 38.249 | 5.220 | 0.137 | 31.593 | 51.200 | triang (c≈0, i.e. ≈uniform 31.593–51.200) | 0.0541 |

Duration-fit N sums to 374 = 379 − 5 failed attempts (excluded from duration fits, counted in failure probabilities).

**Fit quality notes (parametric, N≥30, passed moment/tail gate + bootstrap KS, B=99):**
- `/hbw/store_empty_bucket`: uniform, KS p=0.26, mean rel. err 2.4%, std rel. err 4.1%.
- `/ov/burn`: uniform, KS p=0.17, mean rel. err 3.4%, std rel. err 4.1%.
- `/vgr/pick_up_and_transport`: triang, KS p=0.09, mean rel. err 0.01%, std rel. err 7.1%.
- `/hbw/unload`: triang (c≈1e-6, effectively uniform), KS p=0.27, mean rel. err 1.0%, std rel. err 4.6%.

## 3. Special handling (confirmed decisions)

- **`/ov/burn` — observed, not planned.** Fitted to observed values: mean 30.45 s, max 41.53 s (uniform 21.421–41.532). The planned 222 s is **not** used — the model is a digital twin of actual behaviour.
- **`/hbw/unload` 0.03 s outlier — excluded (data error).** The 0.031 s observation (WF_101_28) and the 0.047 s observation (WF_101_26) are the two scrap cases' *failed* unload attempts (transport/NFC errors), not service observations. Both are excluded from the duration fit (n=35 successful unloads) but counted in the failure probability.
- **Two zero-duration `/hw/human_review` starts — kept as-is** (WF_1106_16 at 19:12:11.706, WF_102_28 at 19:28:48.971): instant hand-off events. They are included in the empirical quantile table (min = 0.000) and flagged here for the distribution review; they pull the mean down (41.3 s) and inflate CV to 1.285. The long tail (up to 185.06 s) reflects real human-review variability and is kept.

## 4. Failure probabilities (transport/NFC errors, not quality defects)

5 real scrap cases end in failure states; their failed activity attempts give per-activity failure evidence:

| Activity | failed / attempts | p_fail | failing cases |
|---|---|---|---|
| /hbw/unload | 2 / 37 | 0.0541 | WF_101_26, WF_101_28 |
| /vgr/pick_up_and_transport | 3 / 104 | 0.0288 | WF_103_27, WF_104_17, WF_1107_13 |
| all other activities | 0 | 0.0 | — |

These are small-sample estimates (2 and 3 failures). Note: in the log the failed attempts **terminate the case** (early exit) rather than retry; `on_failure: retry` in the spec is the default placeholder and should be revisited if the model needs to reproduce case termination on transport failure.

## 5. Flagged outliers (kept — real variability)

| Activity | Observation | Note |
|---|---|---|
| /hw/human_review | 185.063 s (max) | long human-review hold; kept |
| /hw/human_review | 0.0 s × 2 | instant hand-offs; kept, flagged (§3) |
| /mm/deburr | 66.562 s (max, median 14.24) | long deburr; kept |
| /sm/transport | 58.328 s (max, median 14.97) | long transport; kept |
| /mm/drill | 5.078 s (min, median 14.75) | fast drill; kept |
| /vgr/pick_up_and_transport | 10.843 s (min) | fast pick-up; kept |

No outliers were removed except the two documented `/hbw/unload` data errors (§3).

## 6. Low-confidence estimates (small samples)

The following activities have N < 10 and are **low-confidence estimates** (triangular min/median/max fallbacks; no goodness-of-fit evidence):

| Activity | N |
|---|---|
| /dm/cylindrical_drill | 2 |
| /pm/punch_recesses | 2 |
| /pm/punch_ribbing | 2 |
| /mm/transport_from_to | 3 |
| /dm/drill | 4 |
| /dm/lower | 4 |
| /pm/punch_gill | 4 |
| /mm/drill | 8 |
| /ov/temper | 8 |

Activities with 10 ≤ N < 30 use empirical quantile tables (reproduces the observed CDF exactly; no parametric claim). Only the four N ≥ 30 activities above carry a validated parametric fit.

## 7. Spec output

All parameters are written to spec section `activities` (21 entries, `source: fit_activity_durations`, per-activity `n`, `failure_probability`, `on_failure: retry`) and the measurement/grouping/exclusion assumptions to spec section `assumptions`.
