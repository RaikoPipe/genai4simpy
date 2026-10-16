# Durations & Processing Times Report — fischertechnik_lab_B (run significant-hilarious-cuscus)

## Method
- Service duration = `operation_end_time` − `timestamp` on the **`start` row only** (complete_service_time never used).
- **452 successful instances** used for fitting; **9 failed attempts** recorded separately (6 retryable failures + 3 terminal artifacts).
- Fitting via `fit_activity_durations` (parametric gate: moments/tail/bootstrap-KS; else empirical quantiles; n<10 → triangular). All numbers below are verbatim from the fitter.
- Grouped at activity × resource; split only where the duration difference is real and measurable.

## Service-time table (successful instances, seconds)

| Activity (resource) | N | mean | std | CV | min | max | recommended | failure p |
|---|---|---|---|---|---|---|---|---|
| /vgr/pick_up_and_transport (vgr_1) | 84 | 36.5033 | 13.8229 | 0.3787 | 11.03 | 55.312 | empirical_quantiles | 0.0 |
| /vgr/pick_up_and_transport (vgr_2) | 42 | 40.8278 | 4.2253 | 0.1035 | 31.332 | 46.188 | empirical_quantiles | 0.0 |
| /wt/pick_up_and_transport (wt_1) | 23 | 26.2049 | 0.5942 | 0.0227 | 25.917 | 28.887 | empirical_quantiles | **0.1481** |
| /wt/pick_up_and_transport (wt_2) | 14 | 29.4984 | 0.1275 | 0.0043 | 29.329 | 29.852 | empirical_quantiles | 0.0 |
| /hbw/store_empty_bucket (hbw_1+hbw_2) | 35 | 36.8164 | 5.8628 | 0.1592 | 9.298 | 44.344 | empirical_quantiles | **0.0541** |
| /hbw/unload (hbw_2) | 36 | 39.8734 | 5.7461 | 0.1441 | 32.531 | 52.357 | triang(c=1e-06, loc=32.530974, scale=22.094764) | 0.0 |
| /hbw/get_empty_bucket (hbw_1) | 15 | 39.4026 | 5.11 | 0.1297 | 33.594 | 51.719 | empirical_quantiles | 0.0 |
| /hbw/store (hbw_1) | 14 | 37.7296 | 2.7976 | 0.0741 | 33.768 | 42.229 | empirical_quantiles | 0.0 |
| /hw/human_review (hw_1) | 24 | 20.9192 | 29.9365 | 1.4311 | 0.109 | 98.143 | empirical_quantiles | 0.0 |
| /mm/deburr (mm_1+mm_2) | 25 | 14.3934 | 0.6101 | 0.0424 | 13.843 | 16.45 | empirical_quantiles | 0.0 |
| /mm/drill (mm_2) | 7 | 11.1264 | 5.4634 | 0.491 | 5.281 | 15.657 | triang(c=0.978412, loc=5.281, scale=10.376) | 0.0 |
| /mm/mill (mm_1+mm_2) | 19 | 7.6111 | 4.1345 | 0.5432 | 4.906 | 14.656 | empirical_quantiles | 0.0 |
| /mm/transport_from_to (mm_1+mm_2) | 3 | 15.6717 | 6.3906 | 0.4078 | 11.751 | 23.046 | triang(c=0.041346, loc=11.751, scale=11.295) | 0.0 |
| /ov/burn (ov_1) | 21 | 26.7901 | 5.273 | 0.1968 | 20.781 | 37.502 | empirical_quantiles | 0.0 |
| /ov/burn (ov_2) | 12 | 47.0314 | 54.723 | 1.1635 | 9.25 | 218.688 | empirical_quantiles | 0.0 |
| /ov/temper (ov_1) | 14 | 52.6866 | 1.2846 | 0.0244 | 50.921 | 54.359 | empirical_quantiles | 0.0 |
| /pm/punch_gill (pm_1) | 3 | 27.7503 | 0.4632 | 0.0167 | 27.453 | 28.284 | triang(c=0.073406, loc=27.453, scale=0.831) | 0.0 |
| /pm/punch_recesses (pm_1) | 5 | 23.347 | 0.1832 | 0.0078 | 23.157 | 23.609 | triang(c=0.482301, loc=23.157, scale=0.452) | 0.0 |
| /pm/punch_ribbing (pm_1) | 5 | 24.7464 | 3.7033 | 0.1496 | 22.828 | 31.36 | triang(c=0.04196, loc=22.828, scale=8.532) | 0.0 |
| /sm/sort (sm_1+sm_2) | 16 | 14.1144 | 9.4265 | 0.6679 | 8.728 | 47.391 | empirical_quantiles | 0.0 |
| /sm/transport (sm_1+sm_2) | 21 | 19.8682 | 7.2148 | 0.3631 | 14.093 | 44.468 | empirical_quantiles | 0.0 |
| /dm/cylindrical_drill (dm_2) | 4 | 30.8172 | 2.6529 | 0.0861 | 26.907 | 32.814 | triang(c=0.823938, loc=26.907, scale=5.907) | 0.0 |
| /dm/lower (dm_2) | 4 | 13.9337 | 0.1061 | 0.0076 | 13.814 | 14.029 | triang(c=0.613953, loc=13.814, scale=0.215) | 0.0 |

Only one activity passed the parametric gate: **/hbw/unload** (triang, bootstrap KS p=0.48, AIC 217.16). All others use the empirical quantile table (keeps observed mean, spread, range); n<10 combos use triangular(min, median, max).

## Resource splits (checked per plan)
- **/vgr/pick_up_and_transport — SPLIT.** vgr_1 (n=84, mean 36.5, CV 0.38, wide 11–55 s) vs vgr_2 (n=42, mean 40.8, CV 0.10, tight 31–46 s). Real, measurable difference (different planned times and variance) → two entries.
- **/wt/pick_up_and_transport — SPLIT.** wt_1 (n=23, mean 26.20, sd 0.59) vs wt_2 (n=14, mean 29.50, sd 0.13). ~3.3 s systematic offset, both near-deterministic → two entries.
- **/ov/burn — SPLIT.** ov_1 (n=21, mean 26.8, sd 5.3) vs ov_2 (n=12, mean 47.0, heavy right tail up to 218.7 s) → two entries.
- **/mm/mill — POOLED.** mm_1 (n=15, mean 5.80) and mm_2 (n=4, mean 14.40) differ, but mm_2 has only 4 samples (n<10) and the two planned-time classes (5 s vs 15 s) explain the gap; pooled entry (n=19) keeps both classes in one quantile table.
- **/hbw/store_empty_bucket — POOLED** (hbw_1 n=1 + hbw_2 n=34 → n=35); low-sample combo pooled within resource class.
- **/sm/sort, /sm/transport, /mm/deburr, /mm/transport_from_to — POOLED** (low-sample per-resource combos, n<10 each).

## Planned durations & actual/planned ratio
Planned durations from `planned_operation_time` (separate set, not mixed into fitting):

| Activity | planned (s) | actual mean (s) | actual/planned (mean) |
|---|---|---|---|
| /vgr/pick_up_and_transport (vgr_1) | 20 / 40 (two classes) | 36.50 | ~0.91 (pooled) |
| /vgr/pick_up_and_transport (vgr_2) | 40 | 40.83 | 1.02 |
| /wt/pick_up_and_transport (wt_1) | 26 | 26.20 | 1.008 |
| /wt/pick_up_and_transport (wt_2) | 29.5 | 29.50 | 1.000 |
| /hbw/store_empty_bucket | 40 | 36.82 | 0.92 |
| /hbw/unload | 40 | 39.87 | 0.997 |
| /hbw/get_empty_bucket | 40 | 39.40 | 0.985 |
| /hbw/store | 40 | 37.73 | 0.943 |
| /hw/human_review | 60 | 20.92 | 0.35 |
| /mm/deburr | 15 | 14.39 | 0.959 |
| /mm/drill | 10 | 11.13 | 1.11 |
| /mm/mill | 5 / 15 (two classes) | 7.61 | ~0.63 (pooled) |
| /mm/transport_from_to | 15 | 15.67 | 1.045 |
| /ov/burn (ov_1) | 30 | 26.79 | 0.893 |
| /ov/burn (ov_2) | 40 | 47.03 | 1.18 |
| /ov/temper | 55 | 52.69 | 0.958 |
| /pm/punch_gill | 30 | 27.75 | 0.925 |
| /pm/punch_recesses | 25 | 23.35 | 0.934 |
| /pm/punch_ribbing | 25 | 24.75 | 0.99 |
| /sm/sort | 15 | 14.11 | 0.941 |
| /sm/transport | 20 | 19.87 | 0.993 |
| /dm/cylindrical_drill | 30 | 30.82 | 1.027 |
| /dm/lower | 15 | 13.93 | 0.929 |

Where an activity has two planned-time classes (vgr_1, mm/mill), the pooled ratio is indicative only; per-class ratios are close to 1 for the dominant class.

## Failures & retries
- **9 failed attempts** total, recorded separately (excluded from service-time fitting):
  - **6 retryable failures** → drive failure probabilities.
  - **3 terminal artifacts** (WF_102_16, WF_102_17, WF_104_9) → excluded from failure-probability estimation.
- **Failure probabilities (from the 6 retryable failures only):**
  - `/wt/pick_up_and_transport` on **wt_1**: 4 failed attempts / 27 total attempts → **p = 0.1481**, `on_failure = retry`.
  - `/hbw/store_empty_bucket` on **hbw_2**: 2 failed attempts with **NO retry** (failure-without-retry; bucket absorbed/lost) → **p = 0.0541** (2/37 pooled attempts), `on_failure = none`.
  - All other activity×resource combos: **p = 0**.
- **Retry delays (wt_1, retry start − failed complete):** observed 11.9 s, 15.8 s, 21.2 s, 71.8 s across the 3 retry events (the 71.8 s case includes queueing). Modelled as a retry setup delay on wt_1 (mean ≈ 29 s), not as a separate activity.

## Zero / near-zero durations (flagged before fitting)
- 6 near-zero rows in `/hw/human_review` (min 0.109 s) — **kept**; genuine quick reviews, not defects.
- 2 zero unloads in excluded (censored) cases — excluded from estimation, not removed from the dataset.
- **No data-defect removals** were performed (`remove_outliers` never set); all long service times (e.g. ov_2 burn 218.7 s, human_review 98.1 s) are real variability and are retained in the empirical quantile tables.

## Assumptions
1. Service duration measured on the `start` row only, per the authoritative rule; complete_service_time never used.
2. hbw_2 store_empty_bucket failure is modelled as `on_failure = none` (absorbed, no retry) because the log shows no retry after those 2 failures; the schema has no "absorb" option.
3. wt_1 retry delay is modelled as a setup delay on retry (mean of observed delays); it is not a separate activity.
4. Low-sample combos (n<10) within the same resource class are pooled into a single entry (mm/mill, sm/sort, sm/transport, mm/deburr, mm/transport_from_to, hbw/store_empty_bucket).
5. Terminal artifacts (WF_102_16, WF_102_17, WF_104_9) are excluded from failure-probability estimation; their durations are recorded in the failed-attempt set only.
