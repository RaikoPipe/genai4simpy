# Simulation specification (generated from simulation_spec.json — do not edit)

## Window
t0 2021-07-06T15:08:27.914751+00:00 · horizon 3183 s · first /hbw/unload · terminal /hbw/store

## Resources
| Resource | Class | Capacity |
|---|---|---|
| dm_2 | dm | 1 |
| hbw_1 | hbw | 1 |
| hbw_2 | hbw | 1 |
| hw_1 | hw | 1 |
| mm_1 | mm | 1 |
| mm_2 | mm | 1 |
| ov_1 | ov | 1 |
| ov_2 | ov | 1 |
| pm_1 | pm | 1 |
| sm_1 | sm | 1 |
| sm_2 | sm | 1 |
| vgr_1 | vgr | 1 |
| vgr_2 | vgr | 1 |
| wt_1 | wt | 1 |
| wt_2 | wt | 1 |

## Activities
| Activity | Resources | Service time | P(failure) |
|---|---|---|---|
| /dm/cylindrical_drill | dm_2 | triang(c=0.5, loc=21.97, scale=4.046) (mean 23.99; n=2; src fit_activity_durations) | 0.000 |
| /dm/lower | dm_2 | triang(c=0.5, loc=13.88, scale=0.266) (mean 14.01; n=2; src fit_activity_durations) | 0.000 |
| /hbw/get_empty_bucket | hbw_1 | empirical quantiles [30.8 … 36.2 … 48.6] (mean 37.06; n=11; src fit_activity_durations) | 0.000 |
| /hbw/store | hbw_1 | triang(c=0.3022, loc=34.64, scale=7.703) (mean 37.98; n=3; src fit_activity_durations) | 0.000 |
| /hbw/store_empty_bucket | hbw_2 | empirical quantiles [32.6 … 40.7 … 44.9] (mean 39.43; n=13; src fit_activity_durations) | 0.133 |
| /hbw/unload | hbw_2 | empirical quantiles [32.7 … 38.4 … 52.2] (mean 39.29; n=16; src fit_activity_durations) | 0.059 |
| /hw/human_review | hw_1 | empirical quantiles [0.438 … 3.75 … 62.2] (mean 14; n=14; src fit_activity_durations) | 0.000 |
| /mm/deburr | mm_1, mm_2 | triang(c=0.3596, loc=14.05, scale=1.001) (mean 14.5; n=9; src fit_activity_durations) | 0.000 |
| /mm/drill | mm_1, mm_2 | triang(c=0.6725, loc=5.281, scale=15.62) (mean 13.99; n=4; src fit_activity_durations) | 0.000 |
| /mm/mill | mm_1, mm_2 | triang(c=0.005911, loc=5.047, scale=9.39) (mean 8.195; n=6; src fit_activity_durations) | 0.000 |
| /mm/transport_from_to | mm_2 | triang(c=0.5, loc=12.59, scale=0.547) (mean 12.87; n=2; src fit_activity_durations) | 0.000 |
| /ov/burn | ov_1, ov_2 | empirical quantiles [21.4 … 31.6 … 41.8] (mean 30.14; n=13; src fit_activity_durations) | 0.000 |
| /ov/temper | ov_1, ov_2 | triang(c=0.5924, loc=51.45, scale=0.157) (mean 51.54; n=5; src fit_activity_durations) | 0.000 |
| /pm/punch_gill | pm_1 | constant(value=27.48) (mean 27.48; n=1; src fit_activity_durations) | 0.000 |
| /pm/punch_recesses | pm_1 | triang(c=0.5, loc=23.45, scale=0.375) (mean 23.64; n=2; src fit_activity_durations) | 0.000 |
| /pm/punch_ribbing | pm_1 | triang(c=0.5, loc=23.56, scale=7.657) (mean 27.39; n=2; src fit_activity_durations) | 0.000 |
| /sm/sort | sm_1, sm_2 | triang(c=0.01593, loc=8.36, scale=237.3) (mean 88.73; n=6; src fit_activity_durations) | 0.000 |
| /sm/transport | sm_1, sm_2 | triang(c=0.537, loc=14.39, scale=7.188) (mean 18.07; n=9; src fit_activity_durations) | 0.000 |
| /vgr/pick_up_and_transport | vgr_1, vgr_2 | empirical quantiles [13.1 … 42.8 … 88.4] (mean 41.97; n=50; src fit_activity_durations) | 0.091 |
| /wt/pick_up_and_transport | wt_1, wt_2 | empirical quantiles [25.9 … 26.4 … 29.2] (mean 27.38; n=14; src fit_activity_durations) | 0.000 |

## Variants
### WF_101 — p=0.133, early exit p=0.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
5. /ov/burn [ov_1 100%]
6. /ov/temper [ov_1 100%]
7. /mm/mill [mm_1 100%]
8. /mm/deburr [mm_1 100%]
9. /sm/sort [sm_1 100%]
10. /vgr/pick_up_and_transport [vgr_1 100%]
11. /hw/human_review [hw_1 100%]
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /hbw/store [hbw_1 100%]

### WF_102 — p=0.133, early exit p=0.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /wt/pick_up_and_transport [wt_2 100%]
4. /mm/drill [mm_2 100%]
5. /sm/transport [sm_2 100%]
6. /dm/lower [dm_2 100%]
7. /hbw/store_empty_bucket [hbw_2 100%]
8. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
9. /hw/human_review [hw_1 100%]
10. /vgr/pick_up_and_transport [vgr_1 100%]
11. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /hbw/store [hbw_1 100%]

### WF_103 — p=0.133, early exit p=0.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
5. /ov/burn [ov_1 100%]
6. /ov/temper [ov_1 100%]
7. /wt/pick_up_and_transport [wt_1 100%]
8. /mm/mill [mm_1 100%]
9. /mm/deburr [mm_1 100%]
10. /sm/transport [sm_1 100%]
11. /pm/punch_recesses [pm_1 100%]
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /hw/human_review [hw_1 100%]
14. /hbw/get_empty_bucket [hbw_1 100%]
15. /vgr/pick_up_and_transport [vgr_1 100%]
16. /hbw/store [hbw_1 100%]

### WF_104 — p=0.067, early exit p=0.00
1. /vgr/pick_up_and_transport [vgr_2 100%]
2. /hbw/store_empty_bucket [hbw_2 100%]
3. /ov/burn [ov_2 100%] ∥ concurrent with previous
4. /wt/pick_up_and_transport [wt_2 100%]
5. /mm/mill [mm_2 100%]
6. /sm/sort [sm_2 100%]
7. /vgr/pick_up_and_transport [vgr_2 100%]
8. /vgr/pick_up_and_transport [vgr_1 100%]
9. /wt/pick_up_and_transport [wt_1 100%]
10. /mm/deburr [mm_1 100%]
11. /sm/transport [sm_1 100%]
12. /pm/punch_gill [pm_1 100%]
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hw/human_review [hw_1 100%]
15. /hbw/get_empty_bucket [hbw_1 100%]
16. /vgr/pick_up_and_transport [vgr_1 100%]
17. /hbw/store [hbw_1 100%]

### WF_105 — p=0.133, early exit p=0.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
5. /ov/burn [ov_1 100%]
6. /wt/pick_up_and_transport [wt_1 100%]
7. /mm/deburr [mm_1 100%]
8. /sm/sort [sm_1 100%]
9. /vgr/pick_up_and_transport [vgr_1 100%]
10. /hw/human_review [hw_1 100%]
11. /hbw/get_empty_bucket [hbw_1 100%]
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /hbw/store [hbw_1 100%]

### WF_108 — p=0.067, early exit p=0.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /ov/burn [ov_2 100%] ∥ concurrent with previous
5. /wt/pick_up_and_transport [wt_2 100%]
6. /mm/drill [mm_2 100%]
7. /mm/deburr [mm_2 100%]
8. /sm/sort [sm_2 100%]
9. /vgr/pick_up_and_transport [vgr_2 100%]
10. /vgr/pick_up_and_transport [vgr_1 100%]
11. /hw/human_review [hw_1 100%]
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /hbw/store [hbw_1 100%]

### WF_109 — p=0.067, early exit p=0.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
5. /ov/burn [ov_1 100%]
6. /ov/temper [ov_1 100%]
7. /wt/pick_up_and_transport [wt_1 100%]
8. /mm/mill [mm_1 100%]
9. /mm/deburr [mm_1 100%]
10. /sm/transport [sm_1 100%]
11. /pm/punch_ribbing [pm_1 100%]
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /hw/human_review [hw_1 100%]
14. /hbw/get_empty_bucket [hbw_1 100%]
15. /vgr/pick_up_and_transport [vgr_1 100%]
16. /hbw/store [hbw_1 100%]

### WF_1106 — p=0.133, early exit p=0.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /ov/burn [ov_2 100%]
4. /wt/pick_up_and_transport [wt_2 100%]
5. /hbw/get_empty_bucket [hbw_1 100%]
6. /mm/transport_from_to [mm_2 100%]
7. /sm/transport [sm_2 100%]
8. /dm/cylindrical_drill [dm_2 100%]
9. /vgr/pick_up_and_transport [vgr_1 100%]
10. /hw/human_review [hw_1 100%]
11. /vgr/pick_up_and_transport [vgr_1 100%]
12. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hbw/store [hbw_1 100%]

### WF_1107 — p=0.133, early exit p=0.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
5. /ov/burn [ov_1 100%]
6. /wt/pick_up_and_transport [wt_1 100%]
7. /mm/drill [mm_1 100%]
8. /sm/transport [sm_1 100%]
9. /pm/punch_ribbing [pm_1 100%]
10. /vgr/pick_up_and_transport [vgr_1 100%]
11. /hw/human_review [hw_1 100%]
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /hbw/store [hbw_1 100%]

## Arrivals
model: **two_regime_bursts**

## Control policies
- queue discipline: {'hbw': 'priority', 'vgr': 'fifo'}
- priority order: {'hbw': ['/hbw/store', '/hbw/store_empty_bucket', '/hbw/get_empty_bucket', '/hbw/unload']}
- release rule: open (bursty releases)
- intra-case concurrency: /hbw/store_empty_bucket || /ov/burn; /hbw/store_empty_bucket || /vgr/pick_up_and_transport; /vgr/pick_up_and_transport || /hbw/get_empty_bucket

## Assumptions
- Window is short (~53 min, 3183 s): only 3 of 18 cases complete (WF_101_30, WF_102_31, WF_1106_22); 3 cases are right-censored at the window end (WF_104_21, WF_108_18, WF_109_16) and 12 stop inside the window without the terminal activity. All 15 non-censored cases are treated as window-truncated, not scrap/abandonment, because 418/401 failures are retryable and the workpiece continues.
- No true early exits are modelled: early_exit_probability = 0 for all variants. The 'early exits' reported by discover_variant_routings for variants without a complete case (WF_103, WF_104, WF_105, WF_108, WF_109, WF_1107) are artifacts of window truncation and were corrected by completing those routings with the standard terminal tail.
- Standard terminal tail (verified identical on all 3 complete cases, after /hw/human_review): /vgr/pick_up_and_transport @ vgr_1 -> /hbw/get_empty_bucket @ hbw_1 (concurrent_with_previous) -> /vgr/pick_up_and_transport @ vgr_1 -> /hbw/store @ hbw_1. Applied to the 6 window-truncated variants WF_103, WF_104, WF_105, WF_108, WF_109, WF_1107.
- Failure/retry semantics: 418 (precondition) and 401 (auth) events are retryable. One event_id = one attempt; a complete row is terminal for that attempt; a retry is a new event_id repeating the same activity on the same resource. The operation retries and eventually succeeds, and the workpiece continues along its routing. No permanent scrap is modelled.
- Variant mix probabilities (0.1333 x6, 0.0667 x3) are the share of released cases over all 18 cases (detect_censoring variant_mix.all_cases), used because the complete-case mix (3 cases) is too thin to be representative.
- hbw queue discipline is activity priority (simpy.PriorityResource) with order /hbw/store > /hbw/store_empty_bucket > /hbw/get_empty_bucket > /hbw/unload (learned rule 97.1% vs FIFO 55.9% over 34 mixed-activity decision points). vgr queue is FIFO (100% agreement over 10 decision points).
- Release control is open with bursty arrivals (no WIP cap, no completion trigger): 7 bursts of mean size 2.57 (max 8), burst IAT mean 1.59 s, gap IAT mean 377.5 s; max WIP 12, time-avg WIP 7.09.
- Intra-case concurrency is modelled for the pairs with material overlap: /hbw/store_empty_bucket || /ov/burn (4 cases, mean overlap 38.7 s), /hbw/store_empty_bucket || /vgr/pick_up_and_transport (3 cases, 35.1 s), /vgr/pick_up_and_transport || /hbw/get_empty_bucket (2 cases, 26.5 s). Physically: the bucket store / next transport is requested while the previous step still holds its resource.
- Initial WIP at window start is 0 (no left-censored cases); the simulation starts empty.
- All resources have capacity 1; each concrete resource (hbw_1/hbw_2, vgr_1/vgr_2, ov_1/ov_2, mm_1/mm_2, sm_1/sm_2, wt_1/wt_2) is a separate single-server queue.
- WF_104 starts at /vgr/pick_up_and_transport (no /hbw/unload) because its first observed step in the window is a vgr_2 transport; the unload of that case predates the window (WF_104_20 has missing_first_activity).
- 64% of all waiting time is 'extraneous' (resource idle while the case waits, dominated by hbw: 64.3% of 46 hbw waits, mean 289 s) — hand-off / transport / release delays, not machine contention; vgr contention is 45.6% of vgr waits.
- workpiece_size for /ov/burn mixes categorical labels (regular/middle/large/maxi) and numeric sizes (30-60); kept as raw string, no size-class mapping applied in this phase.
- Quantity (workpiece count) is present in 33/576 rows = 11 activity instances x 3 lifecycle rows (identical value on scheduled/start/complete per instance). Only 10 of 18 cases carry it, and only on material-removal steps: /mm/drill (4 instances), /pm/punch_recesses (2), /pm/punch_gill (1), /pm/punch_ribbing (2), /dm/cylindrical_drill (2).
- Quantity is effectively deterministic per variant/step: WF_102->6, WF_103->6, WF_104->8, WF_108->4, WF_109->6, WF_1106->4, WF_1107->6 (/mm/drill) and 10 (/pm/punch_ribbing). Recommended model: deterministic per-variant step attribute; fallback discrete fit over observed support {4,6,8,10} with empirical PMF {4:0.273, 6:0.545, 8:0.091, 10:0.091} (n=33; flagged sparse, n<5 per variant). Discrete uniform over {4,6,8,10} rejected (chi2=18.27, df=3, p~0.0005; value 6 dominates with 18/33).
- Quality extraction skipped: no scrap/rework/quality columns exist in the log; all 8 failures (418 x7, 401 x1) are retryable with eventual success, so there is no quality yield to extract and no scrap/rework is modelled.
- The 4 incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) were retained for quantity extraction per the binding rule; none of their observed activities carry the quantity parameter, so they contribute 0 observations.
- Extraction plan stated quantity values 3-10, but the observed range is 4-10 (no value 3 present); the observed range 4-10 is used.
- Service times are extracted from start lifecycle rows only: actual_duration = operation_end_time - time:timestamp (start row); complete_service_time (includes queueing) is never used. 192 instances -> 184 service-time samples after excluding the 8 failed attempts (418 x7, 401 x1), which are short precondition/auth failures, not full service; they are retained only for per-activity failure-rate estimation.
- Grouping: per activity, pooling only same-class machine pairs performing the SAME activity (ov_1+ov_2, mm_1+mm_2, sm_1+sm_2, wt_1+wt_2); never pooled across activities. hbw activities are resource-exclusive per activity (hbw_2: unload/store_empty_bucket; hbw_1: get_empty_bucket/store) so no cross-resource pooling applies.
- VGR transports: one distribution per VGR resource (vgr_1: norm(42.64, 15.56) n=32; vgr_2: empirical quantiles 35.7-45.3 s n=18); the pooled 50-sample fit is kept as the primary duration. Flagged for revisit at the modeling stage: vgr_2 serves early transports, vgr_1 the back half + terminal tail, so distance profiles may differ.
- /ov/burn: duration rises monotonically with categorical size class (regular 21.4-26.6 s n=5, middle 26.9-31.8 s n=2, large 31.6-36.7 s n=3, maxi 36.9-41.8 s n=3) but is not (near-)constant within a class (within-class spread ~5 s) and per-class n=2-3 is too sparse for per-class fits; the pooled empirical-quantile fit is used, with the per-class means (23.55/29.37/33.30/38.50 s) as reference for size conditioning at the modeling stage. planned_operation_time 222 s is a nominal cycle, not a service-time reference.
- Drill steps: numeric workpiece_size (30-60) is not significantly correlated with duration at n=4 (/mm/drill r=0.656; /dm/cylindrical_drill n=2 untestable), so samples are pooled; however quantity is strongly associated with /mm/drill duration (r=0.93: qty 4 -> 5.3 s, qty 6 -> 15.5-20.9 s) and is flagged for quantity conditioning at the modeling stage.
- Per-activity failure rates (418+401 unified retry mechanism, failed attempts / total attempts): /hbw/store_empty_bucket 2/15=0.1333, /vgr/pick_up_and_transport 5/55=0.0909 (all 5 on vgr_1: 5/37=0.1351; vgr_2 0/18), /hbw/unload 1/17=0.0588; all other 17 activities 0 (small-sample flag).
- The 4 incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) are retained for duration extraction: their observed steps are complete service observations (WF_104_21 contributes 4, WF_109_16 contributes 1, WF_1107_17 contributes 2, WF_108_18 contributes 0 ok attempts - its only in-window attempt is the failed 401 unload).
- Sparse samples (n<5: /dm/lower, /dm/cylindrical_drill, /mm/transport_from_to, /mm/drill, /pm/punch_gill, /pm/punch_recesses, /pm/punch_ribbing, /hbw/store, /ov/temper) are fitted with the bounded empirical fallback (triangular/constant) and flagged for the modeling stage; planned_operation_time values are recorded as reference only (actuals supersede).
- Outliers kept (real variability, no data defect): /sm/sort 245.7 s (WF_108_17; genuine start->end span, planned 11 s) skews the pooled fit (median 12.1 s) - flagged for a cap or slow-sort mode at the modeling stage; /mm/mill single mm_2 instance 14.44 s (end_position sm_2_lb_1_pos, suggests combined mill+transport); /hw/human_review 0.4-62.3 s (human approval variability, CV 1.37). No values were removed.
- wt transports are pooled across wt_1/wt_2 per the plan (per-resource rule was specified for VGR only), but the resources clearly differ (wt_1 25.9-26.4 s, wt_2 28.9-29.2 s, no overlap; per-resource fits recorded in resource_durations) - flagged for per-resource conditioning at the modeling stage. Same for /sm/transport (sm_1 18.3-21.6 s vs sm_2 14.4-14.7 s).

## Provenance
| Section | Author | Written |
|---|---|---|
| log_schema | data-analysis-agent | 2026-10-14T16:56:12.581142+00:00 |
| window | topology-analysis-agent (draft_topology_spec) | 2026-10-14T20:46:48.122525+00:00 |
| resources | topology-analysis-agent (draft_topology_spec) | 2026-10-14T20:46:48.131494+00:00 |
| variants | topology-analysis-agent | 2026-10-14T21:40:07.431918+00:00 |
| control_policies | topology-analysis-agent (draft_topology_spec) | 2026-10-14T20:46:48.151570+00:00 |
| initial_state | topology-analysis-agent (draft_topology_spec) | 2026-10-14T20:46:48.162288+00:00 |
| assumptions | durations-processing-times-agent | 2026-10-14T23:54:25.960359+00:00 |
| activities | durations-processing-times-agent | 2026-10-14T23:53:24.665760+00:00 |
| arrivals | inter-arrival-times-agent | 2026-10-14T22:33:38.207767+00:00 |
