# Distribution Fitting Report — fischertechnik_lab_C

**Window:** 2021-07-01 18:48:23.227 → 20:19:24.734 UTC (horizon ≈ 5,461.5 s)
**Data:** 1,137 rows → 379 `start` lifecycle rows (100% coverage), 37 cases, 9 variants, 21 activities.
**Scope:** final review of all distributions in spec `activities` and `arrivals`; rework branch and failure probabilities as fixed estimates.

---

## 1. Fitting gate (enforced by `fit_activity_durations`)

A parametric family is used **only if all** hold: N ≥ 30, theoretical mean within 15 % and std within 25 % of the empirical moments, p99 ≤ 2 × observed max, and the parametric-bootstrap KS test (Lilliefors-type: parameters re-estimated in every bootstrap sample, B=99) does not reject at 5 %. Otherwise the **empirical quantile table** is used (10 ≤ N < 30), or **triangular(min, median, max)** for N < 10. No fallback was replaced by a rejected parametric fit, and no distribution was replaced by its mean — variability is preserved.

All spec values were re-verified against a fresh `fit_activity_durations` run (group_by = `activity`) and against the raw event log; they match verbatim. An `activity_resource` cross-check found no resource-specific service-time behaviour that would change the pooled fits (see §5).

## 2. Service-time distributions (spec `activities`, 21 entries)

| Parameter | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| /vgr/pick_up_and_transport | 101 | triang(c=0.976708, loc=4.832668, scale=47.71674) | 36.270 | 36.273 | 11.968 | 11.118 | 0.09 | ✅ parametric |
| /hbw/store_empty_bucket | 34 | uniform(loc=31.734, scale=12.297) | 37.013 | 37.883 | 3.702 | 3.550 | 0.26 | ✅ parametric |
| /hbw/unload | 35 | triang(c=1e-06, loc=31.593, scale=21.134) ≈ uniform(31.593, 51.200) | 38.249 | 38.638 | 5.220 | 4.981 | 0.27 | ✅ parametric |
| /ov/burn | 32 | uniform(loc=21.421, scale=20.111) | 30.453 | 31.477 | 6.054 | 5.806 | 0.17 | ✅ parametric |
| /wt/pick_up_and_transport | 29 ⚠️ | empirical_quantiles (21-pt table) | 27.715 | 27.715 | 1.692 | 1.692 | n/a (in-sample CDF) | ⚠️ fallback, N<30 |
| /mm/deburr | 19 ⚠️ | empirical_quantiles (21-pt table) | 17.053 | 17.053 | 11.998 | 11.998 | n/a | ⚠️ fallback, N<30 |
| /sm/transport | 19 ⚠️ | empirical_quantiles (21-pt table) | 18.920 | 18.920 | 9.822 | 9.821 | n/a | ⚠️ fallback, N<30 |
| /hw/human_review | 17 ⚠️ | empirical_quantiles (21-pt table) | 41.303 | 41.303 | 53.077 | 53.077 | n/a | ⚠️ fallback, N<30 |
| /hbw/get_empty_bucket | 14 ⚠️ | empirical_quantiles (21-pt table) | 38.381 | 38.381 | 4.226 | 4.226 | n/a | ⚠️ fallback, N<30 |
| /hbw/store | 13 ⚠️ | empirical_quantiles (21-pt table) | 37.200 | 37.200 | 3.437 | 3.437 | n/a | ⚠️ fallback, N<30 |
| /sm/sort | 13 ⚠️ | empirical_quantiles (21-pt table) | 11.775 | 11.775 | 3.347 | 3.347 | n/a | ⚠️ fallback, N<30 |
| /mm/mill | 11 ⚠️ | empirical_quantiles (21-pt table) | 8.713 | 8.713 | 4.451 | 4.451 | n/a | ⚠️ fallback, N<30 |
| /mm/drill | 8 ⚠️ | triang(c=0.356553, loc=5.078, scale=27.125) | 13.711 | 17.344 | 9.056 | 5.612 | n/a | ⚠️ low-confidence (N<10) |
| /ov/temper | 8 ⚠️ | triang(c=0.070377, loc=51.437, scale=1.563) | 51.717 | 51.995 | 0.520 | 0.356 | n/a | ⚠️ low-confidence (N<10) |
| /dm/drill | 4 ⚠️ | triang(c=0.36581, loc=15.812, scale=26.142) | 27.129 | 27.714 | 10.935 | 5.400 | n/a | ⚠️ low-confidence (N<10) |
| /dm/lower | 4 ⚠️ | triang(c=0.96875, loc=13.828, scale=0.016) | 13.840 | 13.839 | 0.008 | 0.004 | n/a | ⚠️ low-confidence (N<10) |
| /pm/punch_gill | 4 ⚠️ | triang(c=0.910159, loc=23.859, scale=3.829) | 26.559 | 26.297 | 1.809 | 0.865 | n/a | ⚠️ low-confidence (N<10) |
| /mm/transport_from_to | 3 ⚠️ | triang(c=0.752, loc=12.203, scale=0.25) | 12.349 | 12.349 | 0.130 | 0.053 | n/a | ⚠️ low-confidence (N<10) |
| /dm/cylindrical_drill | 2 ⚠️ | triang(c=0.5, loc=39.078, scale=7.75) | 42.953 | 42.953 | 5.480 | 1.582 | n/a | ⚠️ low-confidence (N<10) |
| /pm/punch_recesses | 2 ⚠️ | triang(c=0.5, loc=23.672, scale=0.157) | 23.751 | 23.751 | 0.111 | 0.032 | n/a | ⚠️ low-confidence (N<10) |
| /pm/punch_ribbing | 2 ⚠️ | triang(c=0.5, loc=23.344, scale=0.453) | 23.571 | 23.571 | 0.320 | 0.093 | n/a | ⚠️ low-confidence (N<10) |

Notes:
- **Parametric (4 activities, N ≥ 30):** all four passed the moment/tail gate and bootstrap KS (p = 0.09–0.27). `/hbw/unload`'s triangular has c ≈ 1e-6, i.e. effectively uniform over [31.593, 51.200].
- **Empirical quantile tables (7 activities, 10 ≤ N < 30):** the table *is* the sample's own CDF, so fit mean/std equal the empirical moments exactly and no goodness-of-fit test is reported (an in-sample test would be trivially passed).
- **Triangular min/median/max (9 activities, N < 10):** low-confidence fallbacks with **no** goodness-of-fit evidence. Fit means stay within 26.5 % of empirical means (worst: `/mm/drill`, driven by a 5.078 s fast-drill observation among 8 points); fit stds are structurally damped (triangular shape) — flagged, not corrected.
- Duration-fit N sums to 374 = 379 − 5 failed attempts (excluded from duration fits, counted in failure probabilities).

## 3. Special handling (confirmed decisions — enforced)

| Item | Decision | Status in spec |
|---|---|---|
| `/ov/burn` | Fitted to observed values (uniform 21.421–41.532 s, mean 30.45 s), **not** the planned 222 s | ✅ uniform(21.421, 20.111) |
| `/hbw/unload` sub-1 s rows (0.031 s / 0.047 s) | Failed unload attempts (transport/NFC errors): excluded from duration fit (n=35), counted in failure probability (2/37) | ✅ |
| 2 zero-duration `/hw/human_review` starts (WF_1106_16, WF_102_28) | Kept as-is (instant hand-offs), included in quantile table (n=17, min = 0.000), flagged | ✅ table verified against raw data (max abs diff < 1e-13) |
| Small-sample activities | `/ov/temper`, `/pm/punch_recesses`, `/pm/punch_ribbing`, `/dm/lower`, `/dm/drill`, `/dm/cylindrical_drill` (+ `/mm/drill`, `/pm/punch_gill`, `/mm/transport_from_to`) remain flagged low-confidence | ✅ §2 |
| Outliers (185.06 s human_review, 66.56 s deburr, 58.33 s sm/transport, 10.84 s vgr min) | Kept — real variability, no data defect | ✅ |

## 4. Arrival process (spec `arrivals`)

Single global stream into `hbw`, model `two_regime_bursts`. Release time per case = `scheduled` row of `/hbw/unload`; all 37 cases included (incl. 19 stubs — real released orders). Verified against raw data: 37 releases, 36 IATs (mean 129.35 s, std 264.36 s, CV 2.04, min 0.510 s, max 989.28 s). Two-regime decomposition threshold 23.26 s; gap:burst IAT ratio ≈ 212 → two regimes are separated by >2 orders of magnitude, so a single mean IAT would be qualitatively wrong.

| Parameter | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| burst_size | 12 ⚠️ | categorical: {1: 0.3333, 2: 0.25, 3: 0.0833, 5: 0.25, 9: 0.0833} | 3.083 | 3.083 | 2.466 | 2.466 | n/a (empirical category counts) | ⚠️ small sample (12 bursts) |
| intra_burst_iat | 25 ⚠️ | empirical_quantiles (21-pt table, 0.510–16.250 s) | 1.974 | 1.974 | 3.105 | 3.105 | n/a | ⚠️ fallback, N<30 |
| inter_burst_gap | 11 ⚠️ | empirical_quantiles (21-pt table, 33.30–989.28 s) | 418.83 | 418.83 | 334.42 | 334.42 | n/a | ⚠️ fallback, N<30 |
| initial_burst | — | constant 9 (window opens at the first release; first burst has 9 cases) | — | — | — | — | n/a | seeding constant |

- Empirical quantiles (not parametric) for both IAT regimes: samples are small and clearly non-exponential (intra-burst CV 1.57 with mass near 0.5–1.6 s plus a 16.25 s tail; gaps near-lognormal, CV 0.80). Quantile sampling preserves the observed shape without overfitting.
- The long gaps between bursts (up to 989.3 s) are part of the arrival process and were **not** trimmed (statistics policy).
- **Variant mix** (interleaved draws from the single stream; WF_104 removed, renormalized over 34 non-WF_104 cases — verified against raw counts): WF_101 0.1176, WF_102 0.1471, WF_103 0.1471, WF_105 0.1176, WF_108 0.0882, WF_109 0.0882, WF_1106 0.1765, WF_1107 0.1176.
- Observed arrival times are **not** replayed; the model samples burst sizes, intra-burst IATs and inter-burst gaps.

## 5. Resource-specific cross-check

`fit_activity_durations` with `group_by = activity_resource` was run to test the plan's pooling decision. No activity shows resource-specific service-time behaviour that would justify a split:
- `/wt/pick_up_and_transport`: wt_1 ≈ 26.00 s (n=14) vs wt_2 ≈ 29.32 s (n=15) — the two tracks are simply configured differently; pooling (empirical quantiles, n=29) keeps both modes in one distribution.
- `/ov/burn`: ov_1 ≈ 27.3 s (n=14) vs ov_2 ≈ 32.9 s (n=18); pooled uniform(21.421, 41.532) covers both.
- `/mm/mill`: mm_1 ≈ 5.5 s (n=7) vs mm_2 ≈ 14.3 s (n=4) — different operations on different tracks; pooled empirical table (n=11) retains both.
- `/sm/transport`: sm_1 ≈ 23.6 s (n=9, incl. 58.3 s outlier) vs sm_2 ≈ 14.7 s (n=10); pooled table (n=19) retains both.
- `/vgr/pick_up_and_transport`: vgr_1 (n=65, mean 34.2 s, wide) vs vgr_2 (n=36, mean 40.0 s, tight); per-resource parametric fits **failed** the gate (both rejected by bootstrap KS), so even the split would fall back to empirical tables — the pooled triang (n=101, gate-passed) is the validated choice.

**Decision: keep the pooled per-activity fits** (as in the extraction plan).

## 6. Failure probabilities & on_failure (spec `activities`)

Transport/NFC errors, not quality defects. Verified against raw log (5 failure rows):

| Activity | failed / attempts | p_fail | Failing cases |
|---|---|---|---|
| /hbw/unload | 2 / 37 | **0.0541** | WF_101_26, WF_101_28 |
| /vgr/pick_up_and_transport | 3 / 104 | **0.0288** | WF_103_27, WF_104_17, WF_1107_13 |
| all other 19 activities | 0 | 0.0 | — |

Small-sample estimates (2 and 3 failures). **`on_failure` corrected from the `retry` placeholder to `scrap` for all 21 activities**: in the log the failed attempts terminate the case (early exit / scrap) — the 5 real scrap cases end in failure states. This matches observed behaviour (confirmed decision).

## 7. Rework branch (fixed probability — no fit)

`p_rework = 1/17 ≈ 0.0588` of `/hw/human_review` completions — a **fixed, small-sample estimate** (1 observed rework out of 17 reviews). No distribution is fitted. Applies to every variant with a human-review step (all 8 arrival variants). The rework loop is the observed WF_104 sequence (T2 → T1 → T2 round-trip), terminated by an explicit `/hbw/store`. WF_104 case data contributes to duration fits of the rework-loop activities but is **not** in the arrival mix.

## 8. Summary of changes made during this review

1. `on_failure: retry → scrap` for all 21 activities (matches observed case termination on failure; confirmed decision).
2. `assumptions` updated: abort/scrap behaviour documented; `p_rework = 1/17` recorded as fixed small-sample estimate; arrival-process summary and variant mix recorded.
3. All other spec values (21 duration distributions, arrivals block) verified verbatim against fresh `fit_activity_durations` runs and the raw event log — no numeric changes required.

**Confidence summary:** 4 parametric fits (validated, N ≥ 30); 7 empirical quantile tables (exact in-sample CDF, 10 ≤ N < 30, ⚠️ flagged); 9 triangular low-confidence fallbacks (N < 10, ⚠️ flagged); 3 arrival distributions (empirical, ⚠️ small samples); 2 fixed failure probabilities + 1 fixed rework probability (small-sample estimates).
