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
| /hw/human_review | hw_1 | empirical quantiles [0 … 17.5 … 185] (mean 41.3; n=17; src fit_activity_durations) | 0.000 |
| /mm/deburr | mm_1, mm_2 | empirical quantiles [13.8 … 14.2 … 66.6] (mean 17.05; n=19; src fit_activity_durations) | 0.000 |
| /mm/drill | mm_2 | triang(c=0.3566, loc=5.078, scale=27.12) (mean 13.71; n=8; src fit_activity_durations) | 0.000 |
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

## Variants
### WF_101 — p=0.118, early exit p=0.50
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
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /vgr/pick_up_and_transport [vgr_1 100%]
16. /hbw/store [hbw_1 100%]

### WF_102 — p=0.147, early exit p=0.00
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
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hbw/store [hbw_1 100%]

### WF_103 — p=0.147, early exit p=0.33
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
16. /vgr/pick_up_and_transport [vgr_1 100%]
17. /hbw/store [hbw_1 100%]

### WF_105 — p=0.118, early exit p=0.00
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
12. /hbw/get_empty_bucket [hbw_1 100%]
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hbw/store [hbw_1 100%]

### WF_108 — p=0.088, early exit p=0.00
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
13. /hbw/get_empty_bucket [hbw_1 100%]
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /hbw/store [hbw_1 100%]

### WF_109 — p=0.088, early exit p=0.00
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
16. /vgr/pick_up_and_transport [vgr_1 100%]
17. /hbw/store [hbw_1 100%]

### WF_1106 — p=0.176, early exit p=0.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /ov/burn [ov_2 100%] ∥ concurrent with previous
5. /wt/pick_up_and_transport [wt_2 100%]
6. /mm/transport_from_to [mm_2 100%]
7. /sm/transport [sm_2 100%]
8. /dm/drill [dm_2 100%] (p=0.60)
9. /dm/cylindrical_drill [dm_2 100%] (p=0.40)
10. /vgr/pick_up_and_transport [vgr_1 100%]
11. /hw/human_review [hw_1 100%]
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /hbw/get_empty_bucket [hbw_1 100%]
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /hbw/store [hbw_1 100%]

### WF_1107 — p=0.118, early exit p=0.50
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
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hbw/store [hbw_1 100%]

## Arrivals
model: **two_regime_bursts**
- burst_size: categorical 1:0.33, 2:0.25, 3:0.08, 5:0.25, 9:0.08 (mean 3.083; n=12; src extract_inter_arrival_times)
- intra_burst_iat: empirical quantiles [0.51 … 1.08 … 16.2] (mean 1.974; n=25; src extract_inter_arrival_times)
- inter_burst_gap: empirical quantiles [47.3 … 593 … 1.41e+03] (mean 595.5; n=11; src extract_inter_arrival_times, recalibrated x1.42182 so expected releases over the 5461.5 s window = 37 (observed release count; authorized fix #2))

## Control policies
- queue discipline: {'hbw': 'priority', 'vgr': 'fifo'}
- priority order: {'hbw': ['/hbw/store_empty_bucket', '/hbw/unload']}
- release rule: open (bursty releases)
- intra-case concurrency: /hbw/store_empty_bucket || /ov/burn; /hbw/store_empty_bucket || /vgr/pick_up_and_transport

## Assumptions
- Service times are measured on the 'start' lifecycle row only: duration = operation_end_time - time:timestamp (complete rows have logging drift; complete_service_time includes queueing and was not used).
- All 379 start rows are used for duration fits, including completed steps of the 19 missing-data stub cases and the 5 real scrap cases (confirmed decision).
- Grouping is per activity only (21 activities), pooling across track instances (ov_1/ov_2, mm_1/mm_2, wt_1/wt_2, sm_1/sm_2) and shared hbw_1/hbw_2, vgr_1/vgr_2 pools; no per-activity x resource splits (no resource-specific service-time behaviour in the topology).
- /hbw/unload: the 0.031 s outlier (WF_101_28) and the 0.047 s near-zero (WF_101_26) are the two scrap cases' failed unload attempts (transport/NFC errors) and are excluded from the duration fit; the 35 successful unloads are fitted (n=35).
- /ov/burn is fitted to observed values (mean 30.45 s, max 41.53 s, uniform(21.421, 41.532)); the planned 222 s is NOT used (digital twin of actual behaviour, confirmed decision).
- /hw/human_review: 2 zero-duration starts (WF_1106_16, WF_102_28) are kept as-is (instant hand-off events) and included in the empirical quantile table (n=17, min=0.000); the activity has high CV (1.285) and a long tail up to 185 s.
- Low-confidence estimates (small samples): /dm/cylindrical_drill (n=2), /pm/punch_recesses (n=2), /pm/punch_ribbing (n=2), /mm/transport_from_to (n=3), /dm/drill (n=4), /dm/lower (n=4), /pm/punch_gill (n=4), /mm/drill (n=8), /ov/temper (n=8). Triangular fallbacks (min/median/max) are used for n<10; empirical quantile tables for 10<=n<30; parametric fits only where the moment/tail gate and bootstrap KS passed (n>=30).
- Failure probabilities are transport/NFC errors, not quality defects: /hbw/unload p=2/37=0.0541 (WF_101_26, WF_101_28), /vgr/pick_up_and_transport p=3/104=0.0288 (WF_103_27, WF_104_17, WF_1107_13); all other activities p=0 (no observed failures).
- on_failure='scrap' for all activities (corrected from the 'retry' placeholder): in the log the 5 failed attempts (2x /hbw/unload, 3x /vgr/pick_up_and_transport) terminate the case (early exit / scrap) rather than retry — confirmed decision.
- The 5 real scrap cases (WF_101_26, WF_101_28, WF_103_27, WF_104_17, WF_1107_13) end in failure states; their completed steps are valid service observations and are included in the fits.
- Rework branch (structured field variants[].rework_branches; fixed probability, no fit — small-sample estimate): p_rework = 1/17 = 0.0588 of /hw/human_review completions enters the quality-rework loop (the WF_104 sequence: /vgr/pick_up_and_transport, /hbw/store_empty_bucket, /ov/burn, /wt/pick_up_and_transport, /mm/mill, /sm/sort, 3x /vgr/pick_up_and_transport, /hbw/store), terminated by /hbw/store; applies to every variant with a human-review step (all 8 arrival variants). WF_104 itself is removed from the arrival mix: its 0.0811 share in the log is internal rework flow, not an arrival stream (authorized fix #1).
- Arrivals: single global stream into hbw, two_regime_bursts model (12 bursts, mean size 3.08, range 1-9; intra-burst IAT mean 1.97 s, n=25; inter-burst gaps mean 418.8 s, n=11, scaled x1.42182 -> mean 595.5 s so the expected number of releases over the 5461.5 s window is 37, matching the observed 37 releases; initial burst constant 9). Long gaps are part of the arrival process and were not trimmed. Variant mix (renormalized over 34 non-WF_104 cases): WF_101 0.1176, WF_102 0.1471, WF_103 0.1471, WF_105 0.1176, WF_108 0.0882, WF_109 0.0882, WF_1106 0.1765, WF_1107 0.1176.

## Provenance
| Section | Author | Written |
|---|---|---|
| log_schema | data-analysis-agent | 2026-10-15T07:42:17.280647+00:00 |
| window | topology-analysis-agent (draft_topology_spec) | 2026-10-15T08:03:00.042755+00:00 |
| resources | topology-analysis-agent (draft_topology_spec) | 2026-10-15T08:03:00.049062+00:00 |
| variants | simulation-evaluator-agent | 2026-10-15T13:57:50.188122+00:00 |
| control_policies | topology-analysis-agent (draft_topology_spec) | 2026-10-15T08:03:00.068289+00:00 |
| initial_state | topology-analysis-agent | 2026-10-15T08:32:27.885120+00:00 |
| assumptions | simulation-evaluator-agent | 2026-10-15T14:00:47.847279+00:00 |
| arrivals | simulation-evaluator-agent | 2026-10-15T14:00:47.829053+00:00 |
| activities | distribution-fitting-agent | 2026-10-15T11:18:40.791632+00:00 |
