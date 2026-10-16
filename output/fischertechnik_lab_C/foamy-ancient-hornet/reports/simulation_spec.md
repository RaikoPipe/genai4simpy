# Simulation specification (generated from simulation_spec.json — do not edit)

## Window
t0 2021-07-01T18:48:23.227456+00:00 · horizon 5462 s · first /hbw/unload · terminal /hbw/store

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
| /dm/cylindrical_drill | dm_2 | triang(c=0.5, loc=39.08, scale=7.75) (mean 42.95; n=2; src fit_activity_durations) | 0.000 |
| /dm/drill | dm_2 | triang(c=0.3658, loc=15.81, scale=26.14) (mean 27.13; n=4; src fit_activity_durations) | 0.000 |
| /dm/lower | dm_2 | triang(c=0.9688, loc=13.83, scale=0.016) (mean 13.84; n=4; src fit_activity_durations) | 0.000 |
| /hbw/get_empty_bucket | hbw_1 | empirical quantiles [33 … 36.7 … 48.1] (mean 38.38; n=14; src fit_activity_durations) | 0.000 |
| /hbw/store | hbw_1 | empirical quantiles [30.7 … 39.3 … 40.2] (mean 37.2; n=13; src fit_activity_durations) | 0.000 |
| /hbw/store_empty_bucket | hbw_2 | uniform(loc=31.73, scale=12.3) (mean 37.01; n=34; src fit_activity_durations) | 0.000 |
| /hbw/unload | hbw_2 | triang(c=1e-06, loc=31.59, scale=21.13) (mean 38.25; n=35; src fit_activity_durations) | 0.054 |
| /hw/human_review | hw_1 | empirical quantiles [0.328 … 27.1 … 185] (mean 46.81; n=15; src fit_activity_durations) | 0.000 |
| /mm/deburr | mm_1, mm_2 | empirical quantiles [13.8 … 14.2 … 66.6] (mean 17.05; n=19; src fit_activity_durations) | 0.000 |
| /mm/drill | mm_2 | empirical quantiles [5.08 … 14.7 … 32.2] (mean 13.71; n=8; src distribution-fitting-agent (review of fit_activity_durations; triangular min/median/max fallback replaced)) | 0.000 |
| /mm/mill | mm_1, mm_2 | empirical quantiles [5.08 … 6.11 … 14.5] (mean 8.713; n=11; src fit_activity_durations) | 0.000 |
| /mm/transport_from_to | mm_1, mm_2 | triang(c=0.752, loc=12.2, scale=0.25) (mean 12.35; n=3; src fit_activity_durations) | 0.000 |
| /ov/burn | ov_1, ov_2 | uniform(loc=21.42, scale=20.11) (mean 30.45; n=32; src fit_activity_durations) | 0.000 |
| /ov/temper | ov_1 | triang(c=0.07038, loc=51.44, scale=1.563) (mean 51.72; n=8; src fit_activity_durations) | 0.000 |
| /pm/punch_gill | pm_1 | triang(c=0.9102, loc=23.86, scale=3.829) (mean 26.56; n=4; src fit_activity_durations) | 0.000 |
| /pm/punch_recesses | pm_1 | triang(c=0.5, loc=23.67, scale=0.157) (mean 23.75; n=2; src fit_activity_durations) | 0.000 |
| /pm/punch_ribbing | pm_1 | triang(c=0.5, loc=23.34, scale=0.453) (mean 23.57; n=2; src fit_activity_durations) | 0.000 |
| /sm/sort | sm_1, sm_2 | empirical quantiles [8.58 … 10.8 … 21.3] (mean 11.78; n=13; src fit_activity_durations) | 0.000 |
| /sm/transport | sm_1, sm_2 | empirical quantiles [14.2 … 15 … 58.3] (mean 18.92; n=19; src fit_activity_durations) | 0.000 |
| /vgr/pick_up_and_transport | vgr_1, vgr_2 | triang(c=0.9767, loc=4.833, scale=47.72) (mean 36.27; n=101; src fit_activity_durations) | 0.029 |
| /wt/pick_up_and_transport | wt_1, wt_2 | empirical quantiles [25.8 … 29.1 … 29.5] (mean 27.71; n=29; src fit_activity_durations) | 0.000 |
| vgr_to_hbw_handoff_delay | hbw_1 | empirical quantiles [2.35 … 3.38 … 6.66] (mean 3.546; n=13; src run_python hand-off delay analysis (vgr completion -> hbw start where hbw_1 idle; /hbw/store population)) | 0.000 |

## Variants
### WF_101 — p=0.108, early exit p=0.50
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
5. /ov/burn [ov_1 100%]
6. /ov/temper [ov_1 100%]
7. /wt/pick_up_and_transport [wt_1 100%]
8. /mm/mill [mm_1 100%]
9. /mm/deburr [mm_1 100%]
10. /sm/sort [sm_1 100%]
11. /vgr/pick_up_and_transport [vgr_1 100%]
12. /hw/human_review [hw_1 100%]
13. /hbw/get_empty_bucket [hbw_1 100%]
14. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
15. /vgr/pick_up_and_transport [vgr_1 100%]
16. /hbw/store [hbw_1 100%]

### WF_102 — p=0.135, early exit p=0.60
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 60%, vgr_1 40%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /ov/burn [ov_2 100%] ∥ concurrent with previous
5. /wt/pick_up_and_transport [wt_2 100%]
6. /mm/drill [mm_2 100%]
7. /sm/transport [sm_2 100%]
8. /dm/lower [dm_2 100%]
9. /vgr/pick_up_and_transport [vgr_1 100%]
10. /hw/human_review [hw_1 100%]
11. /hbw/get_empty_bucket [hbw_1 100%]
12. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hbw/store [hbw_1 100%]

### WF_103 — p=0.135, early exit p=0.60
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
15. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
16. /vgr/pick_up_and_transport [vgr_1 100%]
17. /hbw/store [hbw_1 100%]

### WF_104 — p=0.081, early exit p=1.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /ov/burn [ov_2 100%] ∥ concurrent with previous
5. /wt/pick_up_and_transport [wt_2 100%]
6. /sm/sort [sm_2 100%]
7. /vgr/pick_up_and_transport [vgr_1 50%, vgr_2 50%]
8. /vgr/pick_up_and_transport [vgr_1 100%]
9. /wt/pick_up_and_transport [wt_1 100%]
10. /mm/deburr [mm_1 100%]
11. /sm/transport [sm_1 100%]
12. /pm/punch_gill [pm_1 100%]
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hw/human_review [hw_1 100%]
15. /vgr/pick_up_and_transport [vgr_2 100%]
16. /hbw/store_empty_bucket [hbw_2 100%]
17. /ov/burn [ov_2 100%] ∥ concurrent with previous
18. /wt/pick_up_and_transport [wt_2 100%]
19. /mm/mill [mm_2 100%]
20. /sm/sort [sm_2 100%]
21. /vgr/pick_up_and_transport [vgr_2 100%]
22. /vgr/pick_up_and_transport [vgr_1 100%]
23. /vgr/pick_up_and_transport [vgr_1 100%]

### WF_105 — p=0.108, early exit p=0.50
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
11. /vgr/pick_up_and_transport [vgr_1 100%]
12. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
13. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
14. /hbw/store [hbw_1 100%]

### WF_108 — p=0.081, early exit p=0.67
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
14. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
15. /hbw/store [hbw_1 100%]

### WF_109 — p=0.081, early exit p=0.33
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
15. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
16. /vgr/pick_up_and_transport [vgr_1 100%]
17. /hbw/store [hbw_1 100%]

### WF_1106 — p=0.162, early exit p=0.83
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /ov/burn [ov_2 100%] ∥ concurrent with previous
5. /wt/pick_up_and_transport [wt_2 100%]
6. /mm/transport_from_to [mm_2 100%]
7. /sm/transport [sm_2 100%]
8. /dm/drill [dm_2 100%]
9. /vgr/pick_up_and_transport [vgr_1 100%]
10. /hw/human_review [hw_1 100%]
11. /vgr/pick_up_and_transport [vgr_1 100%]
12. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
13. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
14. /hbw/store [hbw_1 100%]

### WF_1107 — p=0.108, early exit p=0.75
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
5. /ov/burn [ov_1 100%]
6. /mm/transport_from_to [mm_1 100%]
7. /sm/transport [sm_1 100%]
8. /pm/punch_gill [pm_1 100%]
9. /vgr/pick_up_and_transport [vgr_1 100%]
10. /hw/human_review [hw_1 100%]
11. /hbw/get_empty_bucket [hbw_1 100%]
12. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hbw/store [hbw_1 100%]

## Arrivals
model: **two_regime_bursts**
- burst_size: categorical 1:0.33, 2:0.25, 3:0.08, 5:0.25, 9:0.08 (mean 3.083; n=12; src extract_inter_arrival_times)
- intra_burst_iat: empirical quantiles [0.51 … 1.08 … 16.2] (mean 1.974; n=25; src extract_inter_arrival_times)
- inter_burst_gap: empirical quantiles [33.3 … 417 … 989] (mean 418.8; n=11; src extract_inter_arrival_times)

## Control policies
- queue discipline: {'hbw': 'priority', 'vgr': 'fifo'}
- priority order: {'hbw': ['/hbw/store_empty_bucket', '/hbw/unload']}
- release rule: exogenous batch release (operator-driven): single global arrival process into hbw with bursty batch structure (12 bursts, mean size 3.08, burst IAT mean 1.97 s, gap mean 418.8 s), then split by process-model proportions
- intra-case concurrency: /hbw/get_empty_bucket || /vgr/pick_up_and_transport; /hbw/store_empty_bucket || /ov/burn; /hbw/store_empty_bucket || /vgr/pick_up_and_transport; /vgr/pick_up_and_transport || /hbw/get_empty_bucket

## Assumptions
- Two parallel tracks (production lines) confirmed: Track 1 (shop floor 1) = ov_1, mm_1, wt_1, sm_1, pm_1, hw_1; Track 2 (shop floor 2) = ov_2, mm_2, wt_2, sm_2, dm_2. pm and hw are shop-floor-1 only (single-instance); dm is shop-floor-2 only (single-instance).
- hbw and vgr are shared at the exchange point (not track-specific). Evidence: hbw_1, hbw_2, vgr_1, vgr_2 are used by all variants (both track 1 and track 2). hbw_2 is the infeed bucket station, hbw_1 is the outfeed bucket station, vgr_2 is the infeed transporter, vgr_1 is the outfeed/general transporter.
- WF_104 rework loop is a real quality rework loop (failed human review → reprocessed). The spec models it as a linear sequence (the spec schema does not support conditional routing or loops). The 23-step sequence is the longest observed partial sequence (no complete cases for WF_104).
- WF_1106 variability is modeled as a single process model with conditional routing (different drill types: /dm/drill vs /dm/cylindrical_drill). The spec models it as a linear sequence (the spec schema does not support conditional routing). The main sequence uses /dm/drill; /dm/cylindrical_drill is an alternative.
- The release rule is open (bursty releases), not completion-triggered or WIP-capped. Evidence: 37 releases, max WIP 9, time-avg WIP 6.07, 12 bursts with mean size 3.08, gap mean 418.8s, burst IAT mean 1.97s.
- The queue discipline for hbw is priority (not FIFO), with priority order: /hbw/store_empty_bucket > /hbw/unload. Evidence: FIFO agreement 50.8%, case_age agreement 100%, activity_priority agreement 100%.
- The queue discipline for vgr is FIFO. Evidence: FIFO agreement 100% over 15 decision points.
- Intra-case concurrency is modeled for 4 pairs: /hbw/store_empty_bucket → /ov/burn (17 cases, mean overlap 35.5s), /hbw/store_empty_bucket → /vgr/pick_up_and_transport (13 cases, mean overlap 28.8s), /vgr/pick_up_and_transport → /hbw/get_empty_bucket (5 cases, mean overlap 17.2s), /hbw/get_empty_bucket → /vgr/pick_up_and_transport (4 cases, mean overlap 22.3s).
- Cases ending on a failure state are real scrap (early exits), not missing data. 5 such cases identified: WF_101_26, WF_101_28, WF_103_27, WF_104_17, WF_1107_13.
- Cases ending on a non-terminal activity with success state are real abandonment (early exits), except for 1-2 activity stubs which are missing data. WF_1107_15 (1-step stub) is missing data and should be excluded per user decision, but the tool included it as an early exit (impact is minor: 1 case out of 37).
- The 18 longer success-ending incomplete cases (4-12 steps) are real abandonment (early exits), not missing data. This is consistent with the tool's classification and the user's decision to only discard 1-2 activity stubs as missing data.
- Service times are extracted from start-row durations (operation_end_time - timestamp on lifecycle 'start'), pooled per activity across resources per the extraction plan. Per-resource breakdowns show real differences that track the per-resource planned times: /mm/mill mm_1 5.5 s vs mm_2 14.3 s (planned 5 vs 14), /wt wt_1 26.0 s vs wt_2 29.3 s (planned 22 vs 27), /sm/transport sm_1 23.6 s vs sm_2 14.7 s (planned 18 vs 15), /vgr vgr_1 34.2 s (CV 0.42) vs vgr_2 40.0 s (CV 0.10), /ov/burn ov_1 27.3 s vs ov_2 32.9 s. Pooled values are used as the plan directs; the distribution-fitting/calibration phase may split these if needed.
- /ov/burn service time uses the observed actual durations (n=32, mean 30.45 s, uniform 21.4-41.5 s), NOT the planned 222 s - the twin models actual behaviour.
- The vgr -> hbw hand-off delay is modelled as an explicit transfer delay (spec activity 'vgr_to_hbw_handoff_delay', empirical quantiles, mean 3.55 s, n=13) and is NOT folded into vgr service times. It was estimated from the 13 /hbw/store idle gaps (2.35-6.66 s, a consistent physical transfer). The 9 /hbw/get_empty_bucket idle gaps (5.5-122 s, mean 26.5 s) contain additional operator/bucket-availability waiting and are excluded from the base transfer delay.
- Small-sample activities (n < 5: /dm/cylindrical_drill, /dm/drill, /dm/lower, /pm/punch_gill, /pm/punch_recesses, /pm/punch_ribbing, /mm/transport_from_to) use the tool's triangular/constant fallback (min/median/max) with wide uncertainty; the distribution-fitting-agent will review these fits.
- Data-defect exclusions from service-time statistics: (1) the 0.031 s /hbw/unload instance WF_101_28 (confirmed NFC 418 failure, data error per plan); (2) the 0.047 s /hbw/unload instance WF_101_26 (same failure mode, also a failed attempt); (3) the two zero-duration /hw/human_review start rows (WF_1106_16, WF_102_28) where the recorded end timestamp equals the start timestamp (logging artifact; actual review took ~1-3 s per complete_service_time). Failed attempts are excluded from duration fits (include_failures=False) but count toward failure probabilities: /hbw/unload p=0.0541 (2/37), /vgr/pick_up_and_transport p=0.0288 (3/104).
- Five /hw/human_review instances have unreliable start-row end timestamps (recorded 0.0-0.875 s vs actual 1.3-2.8 s per complete_service_time); the empirical quantile table keeps the recorded values, so the lower tail of human_review may be slightly compressed. Median (27.1 s) and upper tail are reliable.

## Provenance
| Section | Author | Written |
|---|---|---|
| log_schema | data-analysis-agent | 2026-10-14T16:52:58.867160+00:00 |
| window | topology-analysis-agent (draft_topology_spec) | 2026-10-14T20:07:04.795041+00:00 |
| resources | topology-analysis-agent (draft_topology_spec) | 2026-10-14T20:07:04.804677+00:00 |
| variants | topology-analysis-agent | 2026-10-14T20:32:09.440467+00:00 |
| control_policies | topology-analysis-agent | 2026-10-14T20:54:45.032473+00:00 |
| initial_state | topology-analysis-agent (draft_topology_spec) | 2026-10-14T20:07:05.108728+00:00 |
| assumptions | durations-processing-times-agent | 2026-10-14T21:53:04.297074+00:00 |
| arrivals | distribution-fitting-agent | 2026-10-14T23:54:57.297187+00:00 |
| activities | distribution-fitting-agent | 2026-10-14T23:54:57.315459+00:00 |
