# Durations / Processing Times Report — fischertechnik_lab_A (run: eager-nice-cow)

## 1. Method

- **Duration rule (binding):** service time = `operation_end_time` − `time:timestamp` on **`start` lifecycle rows only** (192 instances, all positive, none ≤ 0 s). `complete_service_time` (includes queueing) was never used.
- **Attempt semantics:** one `event_id` = one attempt; the `complete` row is terminal. 8 failed attempts (418 ×7 precondition, 401 ×1 auth) are **excluded from service-time samples** (short precondition/auth failures, not full service) and retained only for per-activity failure rates. → 184 service-time samples.
- **Grouping:** per activity; same-class machine pairs pooled only for the *same* activity (ov_1+ov_2, mm_1+mm_2, sm_1+sm_2, wt_1+wt_2). Never pooled across activities. hbw activities are resource-exclusive per activity (hbw_2: unload / store_empty_bucket; hbw_1: get_empty_bucket / store), so no pooling needed.
- **VGR exception:** one transport-time distribution per VGR resource (vgr_1, vgr_2), recorded in `resource_durations`; pooled 50-sample fit kept as primary. Flagged for revisit (distance profiles differ: vgr_2 early transports, vgr_1 back half + terminal tail).
- **Incomplete cases retained:** WF_104_21 (4 ok attempts), WF_109_16 (1), WF_1107_17 (2), WF_108_18 (0 ok — its only in-window attempt is the failed 401 unload). Their observed steps are complete service observations.
- **Censored cases** (initial_state.excluded_from_estimation: WF_104_21, WF_108_18, WF_109_16) are excluded by the fitter where applicable; per binding rule 8 they are retained for duration extraction, and their 5 ok attempts are included in the samples above.
- Fitting: `fit_activity_durations` (gate: moment/tail + bootstrap KS; else empirical quantile table; triang/constant fallback for n < 10). All numbers below are copied verbatim from the tool.

## 2. Per-activity service times (failed attempts excluded)

| Activity | N | mean (s) | std (s) | CV | min (s) | max (s) | recommended | failure p |
|---|---|---|---|---|---|---|---|---|
| /dm/cylindrical_drill | 2 | 23.992 | 2.861 | 0.119 | 21.969 | 26.015 | triang (fallback, n=2) | 0.0 |
| /dm/lower | 2 | 14.008 | 0.188 | 0.013 | 13.875 | 14.141 | triang (fallback, n=2) | 0.0 |
| /hbw/get_empty_bucket | 11 | 37.062 | 5.038 | 0.136 | 30.797 | 48.594 | empirical_quantiles | 0.0 |
| /hbw/store | 3 | 37.985 | 3.951 | 0.104 | 34.641 | 42.344 | triang (fallback, n=3) | 0.0 |
| /hbw/store_empty_bucket | 13 | 39.429 | 3.852 | 0.098 | 32.641 | 44.867 | empirical_quantiles | 0.1333 (2/15) |
| /hbw/unload | 16 | 39.292 | 5.798 | 0.148 | 32.735 | 52.248 | empirical_quantiles | 0.0588 (1/17) |
| /hw/human_review | 14 | 13.996 | 19.210 | 1.373 | 0.438 | 62.250 | empirical_quantiles | 0.0 |
| /mm/deburr | 9 | 14.463 | 0.361 | 0.025 | 14.046 | 15.047 | triang (fallback, n=9) | 0.0 |
| /mm/drill | 4 | 14.441 | 6.570 | 0.455 | 5.281 | 20.906 | triang (fallback, n=4) | 0.0 |
| /mm/mill | 6 | 6.672 | 3.805 | 0.570 | 5.047 | 14.437 | triang (fallback, n=6) | 0.0 |
| /mm/transport_from_to | 2 | 12.868 | 0.387 | 0.030 | 12.594 | 13.141 | triang (fallback, n=2) | 0.0 |
| /ov/burn | 13 | 30.145 | 6.665 | 0.221 | 21.422 | 41.782 | empirical_quantiles | 0.0 |
| /ov/temper | 5 | 51.537 | 0.056 | 0.001 | 51.453 | 51.610 | triang (fallback, n=5) | 0.0 |
| /pm/punch_gill | 1 | 27.484 | 0.0 | — | 27.484 | 27.484 | constant (fallback, n=1) | 0.0 |
| /pm/punch_recesses | 2 | 23.641 | 0.265 | 0.011 | 23.453 | 23.828 | triang (fallback, n=2) | 0.0 |
| /pm/punch_ribbing | 2 | 27.391 | 5.414 | 0.198 | 23.562 | 31.219 | triang (fallback, n=2) | 0.0 |
| /sm/sort | 6 | 50.146 | 95.827 | 1.911 | 8.360 | 245.700 | triang (fallback, n=6) | 0.0 |
| /sm/transport | 9 | 17.523 | 3.011 | 0.172 | 14.390 | 21.578 | triang (fallback, n=9) | 0.0 |
| /vgr/pick_up_and_transport | 50 | 41.965 | 12.795 | 0.305 | 13.109 | 88.375 | empirical_quantiles (pooled); per-resource in resource_durations | 0.0909 (5/55) |
| /wt/pick_up_and_transport | 14 | 27.377 | 1.546 | 0.057 | 25.906 | 29.235 | empirical_quantiles (pooled); per-resource in resource_durations | 0.0 |

Only one parametric fit passed the full gate: **vgr_1 transport → norm(loc=42.6437, scale=15.5574), n=32, bootstrap KS p=0.17**. All other activities fell back to the empirical quantile table (n ≥ 10) or bounded triang/constant (n < 10), as designed for small samples.

## 3. Per-resource splits (recorded in `resource_durations`)

| Activity × Resource | N | mean (s) | std (s) | range (s) | fit |
|---|---|---|---|---|---|
| /vgr/pick_up_and_transport × vgr_1 | 32 | 42.644 | 15.557 | 13.11–88.38 | norm (passed gate, p=0.17) |
| /vgr/pick_up_and_transport × vgr_2 | 18 | 40.759 | 3.729 | 35.73–45.30 | empirical_quantiles |
| /sm/transport × sm_1 | 5 | 19.747 | 1.413 | 18.25–21.58 | triang |
| /sm/transport × sm_2 | 4 | 14.528 | 0.130 | 14.39–14.66 | triang |
| /wt/pick_up_and_transport × wt_1 | 8 | 26.106 | 0.184 | 25.91–26.37 | triang |
| /wt/pick_up_and_transport × wt_2 | 6 | 29.087 | 0.165 | 28.88–29.24 | triang |
| /mm/deburr × mm_1 | 8 | 14.505 | 0.375 | 14.05–15.05 | triang |
| /mm/deburr × mm_2 | 1 | 14.235 | — | 14.24 | constant |
| /mm/mill × mm_1 | 5 | 5.136 | 0.096 | 5.05–5.28 | triang |
| /mm/mill × mm_2 | 1 | 14.437 | — | 14.44 | constant |
| /mm/drill × mm_1 | 1 | 20.906 | — | 20.91 | constant |
| /mm/drill × mm_2 | 3 | 12.286 | 6.073 | 5.28–16.06 | triang |
| /ov/burn × ov_1 | 8 | 28.203 | 5.668 | 21.42–36.67 | triang |
| /ov/burn × ov_2 | 5 | 35.178 | 5.667 | 26.89–41.78 | triang |

**Resources clearly differ (no overlap in ranges):** `/sm/transport` (sm_1 18.3–21.6 s vs sm_2 14.4–14.7 s) and `/wt/pick_up_and_transport` (wt_1 25.9–26.4 s vs wt_2 28.9–29.2 s). Pooled fits are kept as primary per the plan; per-resource values are recorded and **flagged for per-resource conditioning at the modeling stage**. `/mm/deburr` resources do not differ (pooled is fine). `/ov/burn` ov_1 vs ov_2 difference is explained by size-class mix (see §4), not by the machine.

## 4. Size dependence

### /ov/burn (categorical size, deterministic per variant)

| Size class | n | durations (s) | mean (s) |
|---|---|---|---|
| regular (WF_101, WF_105, WF_109) | 5 | 21.42, 21.64, 21.64, 26.47, 26.56 | 23.55 |
| middle (WF_102, WF_1106) | 2 | 26.89, 31.84 | 29.37 |
| large (WF_103, WF_1107) | 3 | 31.56, 31.67, 36.67 | 33.30 |
| maxi (WF_104, WF_108) | 3 | 36.86, 36.86, 41.78 | 38.50 |

Duration rises monotonically with size class (~+4 s per class), but is **not (near-)constant within a class** (within-class spread up to ~5 s, e.g. regular 21.4–26.6), and per-class n=2–3 is too sparse for per-class fits. **Decision: pooled empirical-quantile fit; per-class means recorded as reference for size conditioning at the modeling stage.** `planned_operation_time` = 222 s is a nominal cycle, not a service-time reference.

### Drill steps (numeric size 30–60)

- `/mm/drill` (n=4): size 30 → 5.28/15.52/16.06 s, size 40 → 20.91 s. corr(size, dur) = **0.656** (not significant at n=4) → **pooled** per plan. However corr(quantity, dur) = **0.930** (qty 4 → 5.28 s; qty 6 → 15.5–20.9 s) → **flagged for quantity conditioning at the modeling stage**.
- `/dm/cylindrical_drill` (n=2): size 50 → 21.97 s, size 60 → 26.02 s. Untestable at n=2 → pooled, flagged.

## 5. Failure / retry rates (418 + 401 unified, failed attempts / total attempts)

| Activity | attempts | failed | rate |
|---|---|---|---|
| /hbw/store_empty_bucket | 15 | 2 (418: resource not ready) | 0.1333 |
| /vgr/pick_up_and_transport | 55 | 5 (418, all on vgr_1: 5/37=0.1351; vgr_2 0/18) | 0.0909 |
| /hbw/unload | 17 | 1 (401: business_key not in warehouse, WF_108_18) | 0.0588 |
| all other 17 activities | — | 0 | 0.0 (small-sample flag) |

All 8 failures are retryable; every failed attempt was followed by a successful retry on the same resource, and the workpiece continued. No scrap is modelled.

## 6. Flagged outliers (kept — real variability, no data defect)

| Instance | Activity | duration (s) | note |
|---|---|---|---|
| WF_108_17 (event 2542) | /sm/sort | 245.70 | Genuine start→end span (planned 11 s). Skews pooled fit (median 12.1 s). Flagged: cap or separate slow-sort mode at modeling stage. |
| WF_104_20 | /mm/mill (mm_2) | 14.44 | end_position = sm_2_lb_1_pos (others: mm_1_initial_pos) — suggests combined mill+transport. Kept; flagged. |
| /hw/human_review (14 obs) | /hw/human_review | 0.44–62.25 | Human approval time, CV 1.37. Kept as empirical quantiles. |

**No values were removed** (no `remove_outliers` applied; no documented data defect).

## 7. Sparse samples (n < 5) — wide confidence, flagged for modeling stage

/dm/lower (2), /dm/cylindrical_drill (2), /mm/transport_from_to (2), /mm/drill (4), /pm/punch_gill (1), /pm/punch_recesses (2), /pm/punch_ribbing (2), /hbw/store (3), /ov/temper (5). Bounded empirical fallbacks (triang/constant) used; `planned_operation_time` recorded as reference only (actuals supersede): dm/lower 14 s, dm/cylindrical_drill 47 s, mm/transport_from_to 12 s, pm/punch_gill 35 s, pm/punch_recesses 39 s, pm/punch_ribbing 39 s, hbw/store 46 s, ov/temper 56 s.

## 8. Questions for the modeling stage (not blockers)

1. **/sm/sort 245.7 s outlier** — cap the service time, or model a slow-sort mode? (affects mean heavily: 50.1 s pooled vs 12.1 s median)
2. **/mm/drill** — condition duration on `quantity` (r=0.93) instead of size?
3. **/ov/burn** — condition on size class (means 23.55/29.37/33.30/38.50 s) once more data exist?
4. **/sm/transport and /wt/pick_up_and_transport** — adopt the per-resource splits (recorded in `resource_durations`)?
5. **VGR** — keep per-resource distributions (norm for vgr_1, quantiles for vgr_2) as primary?
6. **/mm/mill mm_2 14.44 s** — treat as mill+transport combined step or as a variant of /mm/mill?
