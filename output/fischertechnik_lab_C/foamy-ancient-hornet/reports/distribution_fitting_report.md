# Distribution Fitting Report — fischertechnik_lab_C (run: foamy-ancient-hornet), Phase 4

## 1. Scope & Method

- **Data**: `eventlog_cleaned.parquet` (1,137 rows, 379 activity instances, 37 cases, horizon ≈ 5,461.5 s). Service time = `operation_end_time − timestamp` on the **start row only** (excludes queueing).
- **Fitter**: `fit_activity_durations` (confirmed log schema, failed attempts excluded, no censored cases). Every number below was re-verified against the raw data in this phase.
- **Gate (enforced by the tool, restated here)**: a parametric family is used **only if** N ≥ 30, theoretical mean within 15 % and std within 25 % of the empirical moments, p99 ≤ 2 × observed max, and the parametric-bootstrap KS test (Lilliefors-type: parameters re-estimated in every bootstrap sample, B=99) does not reject at 5 %. Otherwise the **empirical quantile table** (inverse-CDF sampling) is used, or **triangular(min, median, max)** for N < 10. No fallback was replaced by a rejected parametric fit, and no distribution was replaced by its mean — variability is preserved.
- **Exclusions (documented data defects)**: 0.031 s `/hbw/unload` instance WF_101_28 (NFC 418 data error), 0.047 s failed attempt WF_101_26, and 2 zero-duration `/hw/human_review` start rows (WF_1106_16, WF_102_28, logging artifacts). Failed attempts are excluded from duration fits but count toward failure probabilities.
- **Constraints honoured**: `/ov/burn` fitted to observed data (mean 30.45 s), **not** the planned 222 s; the vgr→hbw hand-off delay is an **explicit** transfer delay, not folded into vgr service times; early-exit (scrap) cases retained; no censored cases to drop.

## 2. Service Times — Final Distributions

⚠️ = fallback / N < 30 (wide uncertainty). "Fit mean/std" for empirical-quantile rows are the table's own moments (identical to empirical by construction; no goodness-of-fit test applies to a self-referential table).

| Parameter | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| /vgr/pick_up_and_transport | 101 | triang (c=0.9767, loc=4.833, scale=47.717) | 36.270 | 36.273 | 11.968 | 11.118 | 0.09 | PASS |
| /hbw/unload | 35 | triang (c≈0, loc=31.593, scale=21.134) | 38.249 | 38.638 | 5.220 | 4.981 | 0.27 | PASS |
| /hbw/store_empty_bucket | 34 | uniform (loc=31.734, scale=12.297) | 37.013 | 37.883 | 3.702 | 3.550 | 0.26 | PASS |
| /ov/burn | 32 | uniform (loc=21.421, scale=20.111) | 30.453 | 31.477 | 6.054 | 5.806 | 0.17 | PASS |
| /wt/pick_up_and_transport | 29 ⚠️ | empirical_quantiles (21 pts, 25.81–29.53 s) | 27.715 | 27.715 | 1.692 | 1.692 | n/a | FALLBACK (N<30) |
| /mm/deburr | 19 ⚠️ | empirical_quantiles (21 pts, 13.84–66.56 s) | 17.053 | 17.053 | 11.998 | 11.998 | n/a | FALLBACK (N<30) |
| /sm/transport | 19 ⚠️ | empirical_quantiles (21 pts, 14.22–58.33 s) | 18.920 | 18.920 | 9.821 | 9.821 | n/a | FALLBACK (N<30) |
| /hw/human_review | 15 ⚠️ | empirical_quantiles (21 pts, 0.33–185.06 s) | 46.810 | 46.810 | 54.253 | 54.253 | n/a | FALLBACK (N<30) |
| /hbw/get_empty_bucket | 14 ⚠️ | empirical_quantiles (21 pts, 32.95–48.11 s) | 38.381 | 38.381 | 4.226 | 4.226 | n/a | FALLBACK (N<30) |
| /hbw/store | 13 ⚠️ | empirical_quantiles (21 pts, 30.73–40.19 s) | 37.200 | 37.200 | 3.437 | 3.437 | n/a | FALLBACK (N<30) |
| /sm/sort | 13 ⚠️ | empirical_quantiles (21 pts, 8.58–21.27 s) | 11.775 | 11.775 | 3.347 | 3.347 | n/a | FALLBACK (N<30) |
| /mm/mill | 11 ⚠️ | empirical_quantiles (21 pts, 5.08–14.45 s) | 8.713 | 8.713 | 4.451 | 4.451 | n/a | FALLBACK (N<30) |
| /mm/drill | 8 ⚠️ | empirical_quantiles (21 pts, 5.08–32.20 s) — **revised** | 13.711 | 13.711 | 9.056 | 9.056 | n/a | FALLBACK (N<10, revised) |
| /ov/temper | 8 ⚠️ | triang (c=0.070, loc=51.437, scale=1.563) | 51.717 | 51.995 | 0.520 | 0.491 | n/a | FALLBACK (N<10) |
| /pm/punch_gill | 4 ⚠️ | triang (c=0.910, loc=23.859, scale=3.829) | 26.559 | 26.297 | 1.809 | 1.112 | n/a | FALLBACK (N<10) |
| /dm/lower | 4 ⚠️ | triang (c=0.969, loc=13.828, scale=0.016) | 13.840 | 13.839 | 0.008 | 0.005 | n/a | FALLBACK (N<10) |
| /dm/drill | 4 ⚠️ | triang (c=0.366, loc=15.812, scale=26.142) | 27.129 | 27.714 | 10.935 | 7.956 | n/a | FALLBACK (N<10) |
| /mm/transport_from_to | 3 ⚠️ | triang (c=0.752, loc=12.203, scale=0.250) | 12.349 | 12.349 | 0.130 | 0.074 | n/a | FALLBACK (N<10) |
| /dm/cylindrical_drill | 2 ⚠️ | triang (c=0.5, loc=39.078, scale=7.750) | 42.953 | 42.953 | 5.480 | 2.329 | n/a | FALLBACK (N<10) |
| /pm/punch_ribbing | 2 ⚠️ | triang (c=0.5, loc=23.344, scale=0.453) | 23.571 | 23.571 | 0.320 | 0.136 | n/a | FALLBACK (N<10) |
| /pm/punch_recesses | 2 ⚠️ | triang (c=0.5, loc=23.672, scale=0.157) | 23.751 | 23.751 | 0.111 | 0.047 | n/a | FALLBACK (N<10) |

### Review findings

1. **Parametric fits (4)**: all four passed the full gate (moments, tail, bootstrap KS). Mean deviations ≤ 3.4 %, std deviations ≤ 7.1 % — consistent with the empirical moments. `/hbw/unload`'s triangle is degenerate (c≈0), i.e. a bounded near-uniform over 31.6–51.2 s; this is the tool's recommendation and is kept verbatim.
2. **`/mm/drill` revised (only change to `activities`)**: the tool's triangular(min, median, max) fallback implied a mean of 17.34 s, **+26.5 %** above the empirical 13.71 s — the sample is bimodal (3 instances ≈ 5.3 s, 5 instances 14–32 s) and the min/median/max triangle misplaces the mass. Replaced with the empirical quantile table (N=8), which preserves mean, spread and range exactly. Source recorded as the distribution-fitting-agent review.
3. **Small-sample activities (n < 5)**: `/dm/cylindrical_drill`, `/dm/drill`, `/dm/lower`, `/pm/punch_gill`, `/pm/punch_recesses`, `/pm/punch_ribbing` (plus `/mm/transport_from_to`, n=3) keep the triangular(min, median, max) fallbacks with **wide uncertainty** — for n=2–4 the triangle std underestimates the empirical std (up to ~58 %), so treat these as near-constant values with large confidence intervals; revisit in calibration. All fallback means are within 3 % of the empirical means (except the replaced /mm/drill).
4. **Long tails kept (real variability, not defects)**: `/mm/deburr` 66.56 s, `/sm/transport` 58.33 s, `/hw/human_review` 185.06 s, `/vgr` min 10.84 s.
5. **`/hw/human_review` lower tail**: 5 instances have unreliable start-row end timestamps (recorded 0.0–0.875 s vs actual 1.3–2.8 s); the quantile table keeps recorded values, so the lower tail is slightly compressed. Median (27.1 s) and upper tail are reliable.
6. **Pooled resources** (per extraction plan): per-resource differences exist and track planned times (`/mm/mill` mm_1 5.5 s vs mm_2 14.3 s; `/wt` 26.0 vs 29.3 s; `/sm/transport` 23.6 vs 14.7 s; `/vgr` 33.7 vs 40.0 s; `/ov/burn` 27.3 vs 32.9 s). Pooled values are used as directed; the pooled distributions are bimodal where resources differ — a calibration candidate for per-resource splits.
7. **Failure probabilities** (observed event rates, too sparse for distributions): `/hbw/unload` 2/37 = 0.0541, `/vgr/pick_up_and_transport` 3/104 = 0.0288; all others 0.

## 3. Arrival Process — Final Distributions

Single global exogenous batch arrival into hbw (operator-driven, not completion-triggered, no WIP cap). 37 releases, 36 IATs, span 4,656.4 s. Two-regime decomposition (threshold 23.26 s; gap/burst mean ratio ≈ 212×) → **`two_regime_bursts`**. All values re-verified against raw data in this phase.

| Parameter | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| burst_size | 12 ⚠️ | categorical: values [1, 2, 3, 5, 9], probs [0.3333, 0.25, 0.0833, 0.25, 0.0833] | 3.083 | 3.083 | — | — | n/a | FALLBACK (N<30, observed-size categorical) |
| intra_burst_iat | 25 ⚠️ | empirical_quantiles (21 pts, 0.51–16.25 s) | 1.974 | 1.974 | 3.105 | 3.105 | n/a | FALLBACK (N<30) |
| inter_burst_gap | 11 ⚠️ | empirical_quantiles (21 pts, 33.30–989.28 s) | 418.827 | 418.827 | 334.421 | 334.421 | n/a | FALLBACK (N<30) |

Notes:
- **Burst sizes** observed: [9, 1, 5, 5, 2, 2, 2, 1, 1, 5, 1, 3] (12 bursts). The categorical over observed sizes is the only defensible fit at N=12; wide uncertainty (a single 9-case burst drives 8 % of the mass).
- **No gaps trimmed**: the 33.3 s minimum gap and the 989.3 s maximum gap are real observations; long inter-burst gaps are part of the arrival process.
- The 16.25 s intra-burst outlier is retained (no documented data defect).
- After arrival, each case is split into a variant by interleaved categorical draw using the spec `variants` proportions (WF_101 0.1081, WF_102 0.1351, WF_103 0.1351, WF_104 0.0811, WF_105 0.1081, WF_108 0.0811, WF_109 0.0811, WF_1106 0.1622, WF_1107 0.1081).
- Small samples (N=11 gaps, N=25 intra-burst IATs) → empirical quantiles preserve observed variability; revisit in calibration if more data becomes available.

## 4. vgr → hbw Hand-off Delay — Final Distribution

| Parameter | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| vgr_to_hbw_handoff_delay | 13 ⚠️ | empirical_quantiles (21 pts, 2.35–6.66 s) | 3.546 | 3.546 | 1.117 | 1.117 | n/a | FALLBACK (N<30) |

- Estimated from the **13 `/hbw/store` idle gaps** (hbw_1 idle at wait time; gap = hbw start − preceding vgr completion): a tight, consistent physical transfer (CV 0.31). Re-verified against raw data: all 13 values match the spec quantile table exactly.
- The **9 `/hbw/get_empty_bucket` idle gaps** (5.5–122 s, mean 26.5 s) contain additional operator/bucket-availability waiting and are **excluded** from the base transfer delay (and from vgr service times). The 5 busy gaps (67.6–195.4 s) are pure queueing and excluded.
- Modelled as the explicit spec activity `vgr_to_hbw_handoff_delay` on hbw_1 — **not** folded into vgr service times.

## 5. Spec Changes Made in This Phase

1. `activities`: `/mm/drill` distribution replaced — triangular(min, median, max) fallback (implied mean 17.34 s, +26.5 % off) → empirical quantile table (mean 13.711 s, n=8), with source and note updated.
2. `activities`: all entries re-confirmed verbatim against a fresh `fit_activity_durations` run; `source`, `n`, and gate/KS details added to the four parametric entries; uncertainty notes added to all fallback entries.
3. `arrivals`: re-confirmed verbatim against raw release times (12 bursts, sizes [9,1,5,5,2,2,2,1,1,5,1,3], intra-burst mean 1.9737 s n=25, gap mean 418.8268 s n=11); uncertainty notes added.
4. `vgr_to_hbw_handoff_delay`: re-confirmed (13 store idle gaps, mean 3.5457 s); note retained.

## 6. Open Items for Calibration

- Per-resource splits for `/mm/mill`, `/wt/pick_up_and_transport`, `/sm/transport`, `/vgr/pick_up_and_transport` (pooled distributions are bimodal; per-resource means track planned times).
- Small-sample activities (n < 5) and the arrival components (N = 11–25) carry wide uncertainty.
- WF_104 rework pass/fail probability (3 cases) and per-activity failure rates (5 events) remain deferred to calibration.
- If the twin underestimates `/hbw/get_empty_bucket` waiting, the excluded operator/bucket-availability component (5.5–122 s) is the first place to look.
