# Distribution Fitting Report — fischertechnik_lab_B (run significant-hilarious-cuscus)

**Scope.** Finalise every distribution in spec `activities` (23 service-time entries) and `arrivals` (3 components), plus the wt_1 retry delay. All numbers are copied verbatim from `fit_activity_durations` (service times) and the arrival component samples in `work_files/` (gaps / burst sizes / within-burst IAT). No trace-replay inputs (no case ids or timestamps) are used as model parameters.

## 1. Method & goodness-of-fit gate (restated)

A **parametric** family is used **only if all** hold:
- N ≥ 30;
- theoretical mean within 15 % and std within 25 % of the empirical moments;
- p99 ≤ 2 × observed max (tail gate);
- non-degenerate parameters;
- the **parametric-bootstrap KS test** (Lilliefors-type: parameters re-estimated in every bootstrap sample, B=99) does **not** reject at 5 %.

Otherwise the recommendation is a **bounded empirical fallback**: the empirical quantile table (inverse-CDF sampling), or `triangular(min, median, max)` for N < 10. A fallback is **never** replaced by a rejected parametric fit, and **no** distribution is replaced by its mean — variability is preserved. Empirical-quantile tables are the sample's own CDF, so no in-sample GOF test is reported for them (any in-sample test would be trivially passed).

**Result:** exactly **one** service-time distribution passed the parametric gate — `/hbw/unload` (triangular). Every other service time and all three arrival components use the empirical fallback (N < 30, or no parametric fit passed the gate).

## 2. Service-time distributions (spec `activities`)

| Parameter (activity @ resource) | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| /vgr/pick_up_and_transport @ vgr_1 | 84 | empirical_quantiles | 36.5033 | 36.5033 | 13.8229 | 13.8229 | — | ⚠️ fallback (no parametric passed) |
| /vgr/pick_up_and_transport @ vgr_2 | 42 | empirical_quantiles | 40.8278 | 40.8278 | 4.2253 | 4.2253 | — | ⚠️ fallback (no parametric passed) |
| /wt/pick_up_and_transport @ wt_1 | 23 | empirical_quantiles | 26.2049 | 26.2049 | 0.5942 | 0.5942 | — | ⚠️ fallback (N<30) |
| /wt/pick_up_and_transport @ wt_2 | 14 | empirical_quantiles | 29.4984 | 29.4984 | 0.1275 | 0.1275 | — | ⚠️ fallback (N<30) |
| /hbw/store_empty_bucket @ hbw_1+hbw_2 | 35 | empirical_quantiles | 36.8164 | 36.8164 | 5.8628 | 5.8628 | — | ⚠️ fallback (no parametric passed) |
| /hbw/unload @ hbw_2 | 36 | **triang**(c=1e-06, loc=32.530974, scale=22.094764) | 39.8734 | 39.8959 | 5.7461 | 5.2078 | **0.48** | **PASS** |
| /hbw/get_empty_bucket @ hbw_1 | 15 | empirical_quantiles | 39.4026 | 39.4026 | 5.1100 | 5.1100 | — | ⚠️ fallback (N<30) |
| /hbw/store @ hbw_1 | 14 | empirical_quantiles | 37.7296 | 37.7296 | 2.7976 | 2.7976 | — | ⚠️ fallback (N<30) |
| /hw/human_review @ hw_1 | 24 | empirical_quantiles | 20.9192 | 20.9192 | 29.9365 | 29.9365 | — | ⚠️ fallback (N<30) |
| /mm/deburr @ mm_1+mm_2 | 25 | empirical_quantiles | 14.3934 | 14.3934 | 0.6101 | 0.6101 | — | ⚠️ fallback (N<30) |
| /mm/drill @ mm_2 | 7 | **triang**(c=0.978412, loc=5.281, scale=10.376) | 11.1264 | 12.1237 | 5.4634 | — | — | ⚠️ fallback (N<10) |
| /mm/mill @ mm_1+mm_2 | 19 | empirical_quantiles | 7.6111 | 7.6111 | 4.1345 | 4.1345 | — | ⚠️ fallback (N<30) |
| /mm/transport_from_to @ mm_1+mm_2 | 3 | **triang**(c=0.041346, loc=11.751, scale=11.295) | 15.6717 | 15.6717 | 6.3906 | — | — | ⚠️ fallback (N<10) |
| /ov/burn @ ov_1 | 21 | empirical_quantiles | 26.7901 | 26.7901 | 5.2730 | 5.2730 | — | ⚠️ fallback (N<30) |
| /ov/burn @ ov_2 | 12 | empirical_quantiles | 47.0314 | 47.0314 | 54.7230 | 54.7230 | — | ⚠️ fallback (N<30) |
| /ov/temper @ ov_1 | 14 | empirical_quantiles | 52.6866 | 52.6866 | 1.2846 | 1.2846 | — | ⚠️ fallback (N<30) |
| /pm/punch_gill @ pm_1 | 3 | **triang**(c=0.073406, loc=27.453, scale=0.831) | 27.7503 | 27.7503 | 0.4632 | — | — | ⚠️ fallback (N<10) |
| /pm/punch_recesses @ pm_1 | 5 | **triang**(c=0.482301, loc=23.157, scale=0.452) | 23.3470 | 23.3803 | 0.1832 | — | — | ⚠️ fallback (N<10) |
| /pm/punch_ribbing @ pm_1 | 5 | **triang**(c=0.04196, loc=22.828, scale=8.532) | 24.7464 | 25.7913 | 3.7033 | — | — | ⚠️ fallback (N<10) |
| /sm/sort @ sm_1+sm_2 | 16 | empirical_quantiles | 14.1144 | 14.1144 | 9.4265 | 9.4265 | — | ⚠️ fallback (N<30) |
| /sm/transport @ sm_1+sm_2 | 21 | empirical_quantiles | 19.8682 | 19.8682 | 7.2148 | 7.2148 | — | ⚠️ fallback (N<30) |
| /dm/cylindrical_drill @ dm_2 | 4 | **triang**(c=0.823938, loc=26.907, scale=5.907) | 30.8172 | 30.4983 | 2.6529 | — | — | ⚠️ fallback (N<10) |
| /dm/lower @ dm_2 | 4 | **triang**(c=0.613953, loc=13.814, scale=0.215) | 13.9337 | 13.9297 | 0.1061 | — | — | ⚠️ fallback (N<10) |

**Notes**
- **Fit mean / Fit std** for `empirical_quantiles` equal the empirical moments by construction (the table is the sample's own CDF). For the N<10 `triang` fallbacks, "Fit mean" is the triangular(min, median, max) theoretical mean, which can deviate from the empirical mean (e.g. /mm/drill 12.12 vs 11.13; /pm/punch_ribbing 25.79 vs 24.75) — expected for a 3-point bounded fallback with very small N.
- **/hbw/unload** is the only parametric pass: triang, bootstrap KS p = 0.48 (B=99), AIC 217.16; mean rel. err 0.06 %, std rel. err 9.4 %, tail ratio 1.001. Gamma (p=0.40) and lognorm (p=0.36) also passed but were not selected (higher AIC).
- **/ov/burn @ ov_2** (CV 1.16, max 218.7 s) and **/hw/human_review** (CV 1.43, max 98.1 s) are the most variable; the empirical quantile tables retain the full observed spread and range (no trimming — long service times are real variability, not defects).
- **Failure probabilities** (unchanged, from the 6 retryable failures only): /wt/pick_up_and_transport @ wt_1 **p = 0.1481** (4/27, `on_failure = retry`); /hbw/store_empty_bucket @ hbw_2 **p = 0.0541** (2/37, `on_failure = none` — failure-without-retry, bucket absorbed). All other combos p = 0.

## 3. Arrival process (spec `arrivals`, `two_regime_bursts`)

The mixed mean IAT (140.3 s, CV 2.0) is **not** modeled; the process is decomposed into three components (threshold 17.85 s). All three use the empirical fallback because N < 30.

| Component | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| inter_burst_gap | 13 | empirical_quantiles | 394.6721 | 394.6721 | 357.47 | 357.47 | — | ⚠️ fallback (N<30) |
| burst_size | 14 | categorical {1:0.5714, 2:0.0714, 4:0.1429, 5:0.0714, 6:0.0714, 9:0.0714} | 2.714 | 2.714 | — | — | — | ⚠️ fallback (N<30, discrete) |
| intra_burst_iat | 24 | empirical_quantiles | 2.4435 | 2.4435 | 2.38 | 2.38 | — | ⚠️ fallback (N<30) |

**Rationale**
- **Gaps (n=13):** long idle periods between release batches (min 32.3 s, max 1336.6 s, CV 0.91). Exponential/lognormal/gamma were considered but N=13 < 30, so no parametric fit is trusted; the empirical quantile table preserves the observed long-tail (the 1336.6 s gap is a real part of the process and was **not** trimmed).
- **Burst size (n=14):** discrete; empirical categorical over the 14 observed sizes (mean 2.71, max 9). A geometric/Poisson fit is not defensible at N=14 with a max of 9 and a heavy mass at 1 (57 %); the empirical categorical is the safe choice.
- **Within-burst IAT (n=24):** near-simultaneous releases inside a batch (mean 2.44 s, median 1.44 s, CV 0.98). Exponential was considered but N=24 < 30; the empirical quantile table is used.
- **No pre-window gap is modeled** — the first burst (size 4) starts at the window start (t0), so the gap preceding it is truncated by the observation window.

## 4. Retry delay (wt_1)

Observed retry setup delays (retry `start` − failed `complete`) on wt_1, from the log:

| Case | Delay (s) |
|---|---|
| WF_104_8 (1st retry) | 11.917 |
| WF_104_8 (2nd retry, double-retry chain) | 71.755 |
| WF_109_6 | 15.822 |
| WF_1107_7 | 21.232 |

- **N = 4** — too small for a defensible parametric fit. The 71.755 s value includes queueing (the resource was busy), so the raw mean (30.18 s) overstates the pure setup delay; the mean excluding the queueing outlier is 16.32 s.
- **Recommendation:** model as a **fixed setup delay = 30.182 s** (observed mean) on wt_1 retry, added to the retry instance. Recorded in the spec as `retry_delay: {family: constant, value: 30.182, n: 4, observed_values: [11.917, 15.822, 21.232, 71.755]}`. A distribution is **not** fitted (N too small); the fixed mean is the best-evidence choice and is flagged here.

## 5. Planned-vs-actual validation

Planned durations are taken from the authoritative **`planned_operation_time`** column of the log (22 distinct values, 5–222 s, per extraction plan §3.1-B) — a separate set, never mixed into the service-time fitting. Ratio = actual mean / planned.

| Activity | Planned (s) | Actual mean (s) | Ratio (mean) | Note |
|---|---|---|---|---|
| /vgr/pick_up_and_transport (vgr_2) | 40 | 40.83 | 1.02 | initial pick-up; matches plan |
| /vgr/pick_up_and_transport (vgr_1) | 15–47 (10 classes) | 36.50 | ~0.91 (pooled) | multi-class; pooled ratio indicative only |
| /wt/pick_up_and_transport (wt_1) | 27 | 26.20 | 0.97 | near-deterministic |
| /wt/pick_up_and_transport (wt_2) | 27 | 29.50 | 1.09 | near-deterministic |
| /hbw/store_empty_bucket | 46 / 47 | 36.82 | 0.79 | runs ~20 % faster than plan |
| /hbw/unload | 52 | 39.87 | 0.77 | runs faster than plan |
| /hbw/get_empty_bucket | 46 | 39.40 | 0.86 | |
| /hbw/store | 46 | 37.73 | 0.82 | |
| /hw/human_review | 102 | 20.92 | **0.21** | ⚠️ actuals far below plan (human-driven, high variance) |
| /mm/deburr | 14 / 15 | 14.39 | 1.00 | |
| /mm/drill | 12 / 22 | 11.13 | 0.51–0.93 | two planned classes |
| /mm/mill | 5 / 14 | 7.61 | 0.54–1.52 | two planned classes |
| /mm/transport_from_to | 12 | 15.67 | 1.31 | |
| /ov/burn (ov_1) | 222 | 26.79 | **0.12** | ⚠️ plan is a nominal/maximum; actual much shorter |
| /ov/burn (ov_2) | 222 | 47.03 | **0.21** | ⚠️ same as above |
| /ov/temper | 56 | 52.69 | 0.94 | |
| /pm/punch_gill | 35 | 27.75 | 0.79 | |
| /pm/punch_recesses | 39 | 23.35 | 0.60 | |
| /pm/punch_ribbing | 39 | 24.75 | 0.63 | |
| /sm/sort | 11 / 12 | 14.11 | 1.18–1.28 | |
| /sm/transport | 15 / 18 | 19.87 | 1.10–1.32 | |
| /dm/cylindrical_drill | 47 | 30.82 | 0.66 | |
| /dm/lower | 14 | 13.93 | 1.00 | |

**Findings**
- Most machine activities run within ~10–30 % of plan (ratios 0.77–1.31), consistent with a well-tuned line.
- **Systematic deviations** to flag: `/ov/burn` (plan 222 s is clearly a nominal/maximum — actuals 27–47 s), and `/hw/human_review` (plan 102 s vs actual mean 21 s, CV 1.43 — human-driven, highly variable). These two are the main reasons the planned set is **not** used as a service-time model; actuals drive the distributions.
- **Data discrepancy:** the durations report's "planned" column (e.g. /hbw/unload 40, /hw/human_review 60, /ov/burn 30/40, /ov/temper 55) does **not** match the authoritative `planned_operation_time` (52, 102, 222, 56). This report uses the log's `planned_operation_time` (22 values, 5–222 s) as the planned set, per the extraction plan. The durations report's planned table appears to be a different (rounded/nominal) set and should be reconciled.

## 6. Resource-split decisions (per plan)

- **SPLIT** (real, measurable difference): `/vgr/pick_up_and_transport` (vgr_1 n=84 mean 36.5 CV 0.38 vs vgr_2 n=42 mean 40.8 CV 0.10); `/wt/pick_up_and_transport` (wt_1 n=23 mean 26.2 vs wt_2 n=14 mean 29.5, ~3.3 s offset); `/ov/burn` (ov_1 n=21 mean 26.8 vs ov_2 n=12 mean 47.0, heavy right tail).
- **POOLED** (low-sample per-resource combos, n<10): `/mm/mill`, `/mm/deburr`, `/mm/transport_from_to`, `/sm/sort`, `/sm/transport`, `/hbw/store_empty_bucket` (hbw_1 n=1 + hbw_2 n=34).

## 7. Assumptions & data notes

1. Service duration = `operation_end_time` − `timestamp` on the **`start` row only**; `complete_service_time` (includes queueing) is never used as a service time.
2. **452 successful instances** used for service-time fitting; **9 failed attempts** (6 retryable + 3 terminal artifacts) recorded separately and excluded from the nominal service distributions.
3. No censored durations (end_missing = 0); early exits occur after completed activities.
4. **No data-defect removals** (`remove_outliers` never set); all long service times (ov_2 burn 218.7 s, human_review 98.1 s) are retained as real variability.
5. The 3 terminal failure-only cases (WF_102_16, WF_102_17, WF_104_9) are excluded from failure-probability/routing estimation but **included** in arrivals (their releases are real inputs).
6. hbw_2 `store_empty_bucket` failure is modeled `on_failure = none` (absorbed, no retry) because the log shows no retry after those 2 failures.
7. wt_1 retry delay is a fixed setup delay (observed mean 30.18 s), not a separate activity; the 71.755 s observation includes queueing.
8. The first arrival burst starts at the window start; no pre-window gap is modeled.
9. The planned-vs-actual table uses the log's `planned_operation_time` (authoritative); the durations report's planned column is inconsistent with it and is flagged for reconciliation.

## QUESTIONS FOR USER

1. **Planned-duration discrepancy:** the durations report's planned set (e.g. /hbw/unload 40 s, /hw/human_review 60 s, /ov/burn 30/40 s) does not match the log's `planned_operation_time` (52 s, 102 s, 222 s). This report uses the log's `planned_operation_time` (22 values, 5–222 s) as the authoritative planned set. Please confirm which planned set is intended for validation, or whether the durations report's table should be regenerated from `planned_operation_time`.
2. **wt_1 retry delay:** with only 4 observations (one of which, 71.755 s, includes queueing), I modeled the retry delay as a **fixed 30.18 s** (observed mean). If you prefer, I can instead use the queueing-adjusted mean (16.32 s, excluding the 71.755 s outlier) or keep the raw empirical values [11.9, 15.8, 21.2, 71.8] as a discrete sample. Which is preferred?
