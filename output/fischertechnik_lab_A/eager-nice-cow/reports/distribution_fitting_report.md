# Distribution Fitting Report — fischertechnik_lab_A (run: eager-nice-cow)

## 1. Scope & method

- Reviewed every distribution in spec `activities` (20 activities, incl. per-resource `resource_durations`) and `arrivals` (two-phase model), plus quantity and per-activity failure rates.
- All activity service-time fits re-run with `fit_activity_durations` (group_by `activity` and `activity_resource`, `include_failures=False`); all spec values match the fitter **verbatim** — **no spec corrections were required**.
- Arrival numbers re-computed independently from raw release times (first `time:timestamp` per case, 18 cases); all spec values match.
- Quantity re-computed from the `quantity` column (n=33).

**Fitting gate (enforced by the tools, restated):** a parametric family is used only if **N ≥ 30**, theoretical mean within **15 %** and std within **25 %** of the empirical moments, **p99 ≤ 2 × observed max**, and the **parametric-bootstrap KS test** (Lilliefors-type: parameters re-estimated in every bootstrap sample) does not reject at 5 %. Otherwise the **empirical quantile table** is used (or **triangular(min, median, max)** for N < 10, **constant** for N = 1). No rejected parametric fit was substituted for a fallback, and no distribution was replaced by its mean — variability is preserved throughout.

**Sample basis:** 192 activity instances → 184 service-time samples (8 failed attempts — 418 ×7, 401 ×1 — excluded from service times, used only for failure rates). Service time = `operation_end_time` − `time:timestamp` on `start` rows only. No outliers removed (no documented data defect).

## 2. Service times — pooled per activity

| Parameter | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| /dm/cylindrical_drill | 2 ⚠️ | triang (min,med,max) | 23.992 | 23.992 | 2.861 | 0.826 | n/a | ⚠️ fallback N<30 |
| /dm/lower | 2 ⚠️ | triang (min,med,max) | 14.008 | 14.008 | 0.188 | 0.054 | n/a | ⚠️ fallback N<30 |
| /hbw/get_empty_bucket | 11 | empirical_quantiles | 37.062 | 37.062 | 5.038 | 5.038 | n/a (self-CDF) | ⚠️ fallback N<30 |
| /hbw/store | 3 ⚠️ | triang (min,med,max) | 37.985 | 37.985 | 3.951 | 1.613 | n/a | ⚠️ fallback N<30 |
| /hbw/store_empty_bucket | 13 | empirical_quantiles | 39.429 | 39.429 | 3.852 | 3.852 | n/a (self-CDF) | ⚠️ fallback N<30 |
| /hbw/unload | 16 | empirical_quantiles | 39.292 | 39.292 | 5.798 | 5.798 | n/a (self-CDF) | ⚠️ fallback N<30 |
| /hw/human_review | 14 | empirical_quantiles | 13.996 | 13.996 | 19.210 | 19.210 | n/a (self-CDF) | ⚠️ fallback N<30 |
| /mm/deburr | 9 | triang (min,med,max) | 14.463 | 14.500 | 0.361 | 0.207 | n/a | ⚠️ fallback N<30 |
| /mm/drill | 4 ⚠️ | triang (min,med,max) | 14.441 | 13.992 | 6.570 | 3.252 | n/a | ⚠️ fallback N<30 |
| /mm/mill | 6 | triang (min,med,max) | 6.672 | 8.196 | 3.805 | 2.207 | n/a | ⚠️ fallback N<30 |
| /mm/transport_from_to | 2 ⚠️ | triang (min,med,max) | 12.868 | 12.868 | 0.387 | 0.112 | n/a | ⚠️ fallback N<30 |
| /ov/burn | 13 | empirical_quantiles | 30.145 | 30.145 | 6.665 | 6.665 | n/a (self-CDF) | ⚠️ fallback N<30 |
| /ov/temper | 5 ⚠️ | triang (min,med,max) | 51.537 | 51.536 | 0.056 | 0.032 | n/a | ⚠️ fallback N<30 |
| /pm/punch_gill | 1 ⚠️ | constant | 27.484 | 27.484 | 0.000 | 0.000 | n/a | ⚠️ fallback N=1 |
| /pm/punch_recesses | 2 ⚠️ | triang (min,med,max) | 23.641 | 23.641 | 0.265 | 0.077 | n/a | ⚠️ fallback N<30 |
| /pm/punch_ribbing | 2 ⚠️ | triang (min,med,max) | 27.391 | 27.391 | 5.414 | 1.563 | n/a | ⚠️ fallback N<30 |
| /sm/sort | 6 | triang (min,med,max) | 50.146 | 88.734 | 95.827 | 55.501 | n/a | ⚠️ fallback N<30 |
| /sm/transport | 9 | triang (min,med,max) | 17.523 | 18.073 | 3.011 | 1.469 | n/a | ⚠️ fallback N<30 |
| /vgr/pick_up_and_transport (pooled) | 50 | empirical_quantiles | 41.965 | 41.965 | 12.795 | 12.795 | n/a (self-CDF) | fallback: pooled norm rejected (KS p=0.01) |
| /wt/pick_up_and_transport (pooled) | 14 | empirical_quantiles | 27.377 | 27.377 | 1.546 | 1.546 | n/a (self-CDF) | ⚠️ fallback N<30 |

Notes:
- **Only one parametric fit passed the full gate in the whole dataset: vgr_1 transport → norm** (below). All other activities fell back by design (N < 30 or rejected parametric).
- Empirical-quantile rows: fit mean/std equal the empirical moments by construction (inverse-CDF sampling of the sample's own CDF); no in-sample KS test is meaningful (reported as n/a).
- **⚠️ /sm/sort:** the triang fallback mean (88.73 s) is inflated **+77 %** over the empirical mean (50.15 s) because the genuine 245.7 s observation (WF_108_17, planned 11 s) sits at the max with the mode at the min. Median is 12.1 s. Kept (no data defect) but **flagged**: at the modeling stage cap the service time or split a slow-sort mode; the pooled fallback overstates typical sort time.
- **⚠️ /mm/mill:** fallback mean 8.20 s vs empirical 6.67 s (+23 %) — driven by the single 14.44 s mm_2 instance (end_position `sm_2_lb_1_pos`, suspected combined mill+transport). Kept; flagged for the modeling stage.
- **/ov/burn size classes** (categorical, deterministic per variant): regular 21.42–26.56 s (n=5, mean 23.55), middle 26.89–31.84 (n=2, mean 29.37), large 31.56–36.67 (n=3, mean 33.30), maxi 36.86–41.78 (n=3, mean 38.50). Duration rises monotonically (~+4 s/class) but is **not near-constant within a class** (spread up to ~5 s) and per-class n=2–3 is too sparse for per-class fits → **pooled empirical quantiles kept** (per plan); per-class means recorded as reference for size conditioning. `planned_operation_time` = 222 s is a nominal cycle, not a service-time reference.
- **Drill size check:** /mm/drill size(30/40) vs duration r=0.656 (n=4, not significant) → pooled per plan; but **quantity vs duration r=0.93** (qty 4 → 5.28 s; qty 6 → 15.5–20.9 s) → **flagged for quantity conditioning**. /dm/cylindrical_drill (n=2, sizes 50/60 → 22.0/26.0 s) untestable → pooled, flagged.
- **Sparse (n<5) fallbacks** — wide confidence, planned_operation_time recorded as reference only (actuals supersede): /dm/lower (14 s), /dm/cylindrical_drill (47 s), /mm/transport_from_to (12 s), /pm/punch_gill (35 s), /pm/punch_recesses (39 s), /pm/punch_ribbing (39 s), /hbw/store (46 s), /ov/temper (56 s, near-constant CV 0.001).

## 3. Per-resource splits (`resource_durations`)

| Parameter | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| /vgr/pick_up_and_transport × vgr_1 | 32 | **norm(loc=42.6437, scale=15.5574)** | 42.644 | 42.644 | 15.806 | 15.557 | **0.17** | **PASS** (only parametric fit in dataset) |
| /vgr/pick_up_and_transport × vgr_2 | 18 | empirical_quantiles | 40.759 | 40.759 | 3.729 | 3.729 | n/a (self-CDF) | ⚠️ fallback N<30 |
| /sm/transport × sm_1 | 5 ⚠️ | triang | 19.747 | 19.747 | 1.413 | 0.810 | n/a | ⚠️ fallback N<30 |
| /sm/transport × sm_2 | 4 ⚠️ | triang | 14.528 | 14.528 | 0.130 | 0.044 | n/a | ⚠️ fallback N<30 |
| /wt/pick_up_and_transport × wt_1 | 8 | triang | 26.106 | 26.106 | 0.184 | 0.059 | n/a | ⚠️ fallback N<30 |
| /wt/pick_up_and_transport × wt_2 | 6 | triang | 29.087 | 29.087 | 0.165 | 0.055 | n/a | ⚠️ fallback N<30 |
| /ov/burn × ov_1 | 8 | triang | 28.203 | 28.203 | 5.668 | 3.187 | n/a | ⚠️ fallback N<30 |
| /ov/burn × ov_2 | 5 ⚠️ | triang | 35.178 | 35.178 | 5.667 | 3.187 | n/a | ⚠️ fallback N<30 |

Decisions:
- **VGR (per plan, one distribution per resource):** vgr_1 broad 13.1–88.4 s (distance-dependent; norm passed moment/tail gate + bootstrap KS p=0.17); vgr_2 tight 35.7–45.3 s (empirical quantiles, N<30). Pooled 50-sample fit kept as primary per plan; **flagged for per-resource conditioning at the modeling stage** (vgr_2 serves early transports, vgr_1 the back half + terminal tail; distance profiles may differ).
- **/sm/transport and /wt/pick_up_and_transport:** resources clearly differ with **no overlap** (sm_1 18.3–21.6 s vs sm_2 14.4–14.7 s; wt_1 25.9–26.4 s vs wt_2 28.9–29.2 s). Pooled fits kept as primary per plan; per-resource values recorded in `resource_durations`; **flagged for per-resource conditioning**.
- **/mm/deburr:** resources do not differ (14.05–15.05 s vs 14.24 s) → pooled is fine.
- **/ov/burn ov_1 vs ov_2** difference (28.2 vs 35.2 s) is explained by the size-class mix (ov_2 ran middle/large/maxi), not by the machine → pooling is valid.

## 4. Arrival process (two-phase, `arrivals.model = two_regime_bursts`)

Verified from raw release times (18 cases, window 15:08:27.91 → 16:01:31.12 UTC). No single mixed IAT fitted (binding T2).

| Parameter | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| Phase 1: initial burst size | 1 | categorical {8: 1.0} (fixed initial condition) | 8.0 | 8.0 | — | — | n/a | ⚠️ single observation |
| Phase 1: intra-burst IAT | 7 | empirical_quantiles | 0.987 | 0.987 | 0.426 | 0.426 | n/a (self-CDF) | ⚠️ fallback N<30 |
| Phase 2: steady-state IAT (phase-level, n=9) | 9 | empirical_quantiles | 182.426 | 182.426 | 261.842 | 261.842 | n/a (self-CDF) | ⚠️ fallback N<30 |
| Phase 2: burst size | 6 | categorical {1: 0.5, 2: 0.3333, 3: 0.1667} | 1.667 | 1.667 | — | — | n/a | ⚠️ small sample |
| Phase 2: intra-burst IAT | 4 ⚠️ | empirical_quantiles | 2.644 | 2.644 | 2.054 | 2.054 | n/a (self-CDF) | ⚠️ fallback N<30 |
| Phase 2: inter-burst gap | 5 ⚠️ | empirical_quantiles | 326.251 | 326.251 | 280.964 | 280.964 | n/a (self-CDF) | ⚠️ fallback N<30 |

- Phase split fixed by T2: first 8 cases released within 6.91 s of window start; remaining 10 releases span 1641.8 s. Transition gap (633.50 s) is a single observation — **not** modelled as a distribution and **excluded** from the steady-state IAT sample (the steady-state IATs are the 9 inter-release gaps among the 10 steady-state releases: 799.96, 317.87, 2.36, 139.11, 0.69, 93.41, 5.53, 2.00, 280.91 s — matches spec exactly).
- Steady-state burst structure: 6 bursts, sizes [1,1,2,2,3,1]; intra-burst (≤5.53 s) vs gap (≥93.4 s) classification is unambiguous with a 10 s threshold.
- **Triang rejected for the inter-burst gap:** observed mean 326.25 s is below the minimum possible triang mean on support [93.41, 799.96] (328.92 s) — no valid c exists. Empirical quantiles used.
- **Flags:** only 18 releases in one ~53-min window — all arrival parameters carry wide uncertainty; steady-state mean IAT is dominated by the single 799.96 s gap (upper tail poorly estimated: p90 = 607.1 s from 9 samples); intra-burst (n=4) and gap (n=5) sub-samples too small for parametric fits.

## 5. Quantity

- n=33 observations (11 activity instances × 3 lifecycle rows; only material-removal steps carry it). Observed range **4–10** (the plan's "3–10" is not observed; no value 3 present).
- Empirical PMF: **{4: 0.2727, 6: 0.5455, 8: 0.0909, 10: 0.0909}**.
- Discrete uniform over {4,6,8,10} **rejected** (χ²=18.27, df=3, p≈0.0005; value 6 dominates with 18/33).
- **Final model (per assumptions):** quantity is effectively deterministic per variant/step (WF_102→6, WF_103→6, WF_104→8, WF_108→4, WF_109→6, WF_1106→4, WF_1107→6 drill / 10 ribbing); fallback = the empirical categorical PMF above. **Flagged: sparse (n<5 per variant).**
- Strong association with /mm/drill duration (r=0.93) — flagged for quantity conditioning at the modeling stage.

## 6. Failure / retry rates (418 + 401 unified, failed attempts / total attempts)

| Activity | Attempts | Failed | Rate | Note |
|---|---|---|---|---|
| /hbw/store_empty_bucket | 15 | 2 | 0.1333 | 418: resource not ready |
| /vgr/pick_up_and_transport | 55 | 5 | 0.0909 | all 5 on vgr_1 (5/37 = 0.1351); vgr_2 0/18 |
| /hbw/unload | 17 | 1 | 0.0588 | 401: business_key not in warehouse (WF_108_18) |
| all other 17 activities | — | 0 | 0.0 | ⚠️ small-sample flag (zero observed, not zero true) |

All 8 failures were retried successfully on the same resource; the workpiece continued — no scrap modelled. ⚠️ Global fallback rate (8/192 ≈ 0.042) considered for zero-failure activities at the modeling stage.

## 7. Cross-section inconsistencies & assumptions

1. **/sm/sort fallback mean inflation (+77 %)** and **/mm/mill (+23 %)** — see §2; both are consequences of genuine (kept) outliers, not fitting errors. Modeling-stage decisions needed (cap / slow-sort mode; mill+transport split).
2. **Assumptions wording:** "workpiece_size for /ov/burn mixes categorical labels and numeric sizes (30–60)" — verified: all 13 /ov/burn observations are categorical (regular/middle/large/maxi); the numeric sizes (30–60) occur on the drill steps only. The /ov/burn spec (pooled quantiles + per-class reference means) is unaffected.
3. **Quantity range:** plan said 3–10; observed 4–10 (already corrected in assumptions).
4. **/ov/burn planned_operation_time = 222 s** is a nominal cycle, not a service-time reference (actuals 21.4–41.8 s supersede) — noted to avoid misuse at the modeling stage.
5. Censored cases (WF_104_21, WF_108_18, WF_109_16, listed in `initial_state.excluded_from_estimation`) are excluded by the fitter where applicable, but per binding rule their 7 observed ok attempts are retained in the service-time samples (WF_104_21: 4, WF_109_16: 1, WF_1107_17: 2; WF_108_18: 0 ok — its only in-window attempt is the failed 401 unload).
6. No values were removed anywhere (no `remove_outliers`); no documented data defect.

## 8. Verdict

- **Spec `activities`:** all 20 entries verified against `fit_activity_durations` (pooled + per-resource) — distributions, params, means, n, sources, and failure rates all consistent. **No changes written.**
- **Spec `arrivals`:** all two-phase parameters verified against raw release times — **no changes written.**
- Every distribution carries `source` and `n`; the only parametric fit (vgr_1 norm) passed the full gate; all others are legitimate bounded empirical fallbacks, each flagged above where N < 30 or the fallback distorts the mean.
