# Simulation specification (generated from simulation_spec.json — do not edit)

## Window
t0 2021-06-30T15:24:34.013477+00:00 · horizon 5944 s · first /hbw/unload · terminal /hbw/store

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
| /vgr/pick_up_and_transport | vgr_2 | empirical quantiles [31.3 … 43.3 … 46.2] (mean 40.83; n=42; src fit_activity_durations) | 0.000 |
| /wt/pick_up_and_transport | wt_1 | empirical quantiles [25.9 … 26 … 28.9] (mean 26.2; n=23; src fit_activity_durations) | 0.148 |
| /hbw/store_empty_bucket | hbw_1, hbw_2 | empirical quantiles [9.3 … 37.3 … 44.3] (mean 36.82; n=35; src fit_activity_durations) | 0.054 |
| /hbw/unload | hbw_2 | triang(c=1e-06, loc=32.53, scale=22.09) (mean 39.87; n=36; src fit_activity_durations) | 0.000 |
| /hbw/get_empty_bucket | hbw_1 | empirical quantiles [33.6 … 37.2 … 51.7] (mean 39.4; n=15; src fit_activity_durations) | 0.000 |
| /hbw/store | hbw_1 | empirical quantiles [33.8 … 37.2 … 42.2] (mean 37.73; n=14; src fit_activity_durations) | 0.000 |
| /hw/human_review | hw_1 | empirical quantiles [0.109 … 5.63 … 98.1] (mean 20.92; n=24; src fit_activity_durations) | 0.000 |
| /mm/deburr | mm_1, mm_2 | empirical quantiles [13.8 … 14.2 … 16.4] (mean 14.39; n=25; src fit_activity_durations) | 0.000 |
| /mm/drill | mm_2 | triang(c=0.9784, loc=5.281, scale=10.38) (mean 11.13; n=7; src fit_activity_durations) | 0.000 |
| /mm/mill | mm_1, mm_2 | empirical quantiles [4.91 … 5.28 … 14.7] (mean 7.611; n=19; src fit_activity_durations) | 0.000 |
| /mm/transport_from_to | mm_1, mm_2 | triang(c=0.04135, loc=11.75, scale=11.29) (mean 15.67; n=3; src fit_activity_durations) | 0.000 |
| /ov/burn | ov_2 | empirical quantiles [9.25 … 34.4 … 219] (mean 47.03; n=12; src fit_activity_durations) | 0.000 |
| /ov/temper | ov_1 | empirical quantiles [50.9 … 52.4 … 54.4] (mean 52.69; n=14; src fit_activity_durations) | 0.000 |
| /pm/punch_gill | pm_1 | triang(c=0.07341, loc=27.45, scale=0.831) (mean 27.75; n=3; src fit_activity_durations) | 0.000 |
| /pm/punch_recesses | pm_1 | triang(c=0.4823, loc=23.16, scale=0.452) (mean 23.35; n=5; src fit_activity_durations) | 0.000 |
| /pm/punch_ribbing | pm_1 | triang(c=0.04196, loc=22.83, scale=8.532) (mean 24.75; n=5; src fit_activity_durations) | 0.000 |
| /sm/sort | sm_1, sm_2 | empirical quantiles [8.73 … 10.8 … 47.4] (mean 14.11; n=16; src fit_activity_durations) | 0.000 |
| /sm/transport | sm_1, sm_2 | empirical quantiles [14.1 … 18.9 … 44.5] (mean 19.87; n=21; src fit_activity_durations) | 0.000 |
| /dm/cylindrical_drill | dm_2 | triang(c=0.8239, loc=26.91, scale=5.907) (mean 30.82; n=4; src fit_activity_durations) | 0.000 |
| /dm/lower | dm_2 | triang(c=0.614, loc=13.81, scale=0.215) (mean 13.93; n=4; src fit_activity_durations) | 0.000 |

## Variants
### WF_101 — p=0.158, early exit p=0.67
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

### WF_102 — p=0.132, early exit p=0.33
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /ov/burn [ov_2 100%] ∥ concurrent with previous
5. /wt/pick_up_and_transport [wt_2 100%]
6. /mm/drill [mm_2 100%]
7. /sm/transport [sm_2 100%]
8. /dm/lower [dm_2 100%]
9. /vgr/pick_up_and_transport [vgr_1 100%]
10. /hw/human_review [hw_1 100%]
11. /vgr/pick_up_and_transport [vgr_1 100%]
12. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hbw/store [hbw_1 100%]

### WF_103 — p=0.132, early exit p=1.00
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

### WF_104 — p=0.132, early exit p=0.50
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /ov/burn [ov_2 100%] ∥ concurrent with previous
5. /wt/pick_up_and_transport [wt_2 100%]
6. /mm/mill [mm_2 100%]
7. /sm/sort [sm_2 100%]
8. /vgr/pick_up_and_transport [vgr_2 100%]
9. /vgr/pick_up_and_transport [vgr_1 100%]
10. /wt/pick_up_and_transport [wt_1 100%]
11. /mm/deburr [mm_1 100%]
12. /sm/transport [sm_1 100%]
13. /pm/punch_gill [pm_1 100%]
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /hw/human_review [hw_1 100%]
16. /vgr/pick_up_and_transport [vgr_1 100%]
17. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
18. /vgr/pick_up_and_transport [vgr_1 100%]
19. /hbw/store [hbw_1 100%]

### WF_105 — p=0.105, early exit p=0.50
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

### WF_108 — p=0.079, early exit p=0.33
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
12. /hbw/get_empty_bucket [hbw_1 100%]
13. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /hbw/store [hbw_1 100%]

### WF_109 — p=0.105, early exit p=1.00
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

### WF_1106 — p=0.105, early exit p=0.50
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /ov/burn [ov_2 100%] ∥ concurrent with previous
5. /wt/pick_up_and_transport [wt_2 100%]
6. /mm/mill [mm_2 100%]
7. /sm/transport [sm_2 100%]
8. /dm/cylindrical_drill [dm_2 100%]
9. /vgr/pick_up_and_transport [vgr_1 100%]
10. /hw/human_review [hw_1 100%]
11. /hbw/get_empty_bucket [hbw_1 100%]
12. /vgr/pick_up_and_transport [vgr_1 100%]
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hbw/store [hbw_1 100%]

### WF_1107 — p=0.053, early exit p=0.00
1. /hbw/unload [hbw_2 100%]
2. /vgr/pick_up_and_transport [vgr_2 100%]
3. /hbw/store_empty_bucket [hbw_2 100%]
4. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
5. /ov/burn [ov_1 100%]
6. /wt/pick_up_and_transport [wt_1 100%]
7. /mm/transport_from_to [mm_1 100%]
8. /sm/transport [sm_1 100%]
9. /pm/punch_ribbing [pm_1 100%]
10. /vgr/pick_up_and_transport [vgr_1 100%]
11. /hw/human_review [hw_1 100%]
12. /hbw/get_empty_bucket [hbw_1 100%]
13. /vgr/pick_up_and_transport [vgr_1 100%] ∥ concurrent with previous
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /hbw/store [hbw_1 100%]

## Arrivals
model: **two_regime_bursts**
- burst_size: categorical 1:0.57, 2:0.07, 4:0.14, 5:0.07, 6:0.07, 9:0.07 (mean 2.714; n=14; src extract_inter_arrival_times)
- intra_burst_iat: empirical quantiles [0.563 … 1.44 … 9.87] (mean 2.443; n=24; src extract_inter_arrival_times)
- inter_burst_gap: empirical quantiles [32.3 … 294 … 1.34e+03] (mean 394.7; n=13; src extract_inter_arrival_times)

## Control policies
- queue discipline: {'hbw': 'priority', 'vgr': 'fifo'}
- priority order: {'hbw': ['/hbw/store', '/hbw/get_empty_bucket', '/hbw/store_empty_bucket', '/hbw/unload']}
- release rule: open (bursty releases)
- intra-case concurrency: /hbw/get_empty_bucket || /vgr/pick_up_and_transport; /hbw/store_empty_bucket || /ov/burn; /hbw/store_empty_bucket || /vgr/pick_up_and_transport; /hbw/store_empty_bucket || /wt/pick_up_and_transport; /vgr/pick_up_and_transport || /hbw/get_empty_bucket

## Assumptions
- All 15 resources are modeled with capacity 1 — verified: maximum concurrent service per resource = 1 across all 461 start rows.
- Cases that terminate immediately after a failure with no recovery — WF_102_16 (vgr failure), WF_102_17 (single unload failure), WF_104_9 (single unload failure) — are truncation artifacts and are excluded from routing/early-exit estimation (recorded in initial_state.excluded_from_estimation).
- Failed steps that are followed by a retry on the same resource (wt/pick_up_and_transport in WF_104_8 x2, WF_109_6, WF_1107_7; hbw/store_empty_bucket in WF_102_15 and WF_104_8) are modeled as retry-on-same-resource with a delay; retry instances are not part of the canonical step sequence.
- Storage steps (hbw/store_empty_bucket at the start; hbw/get_empty_bucket -> hbw/store at the end) are conditional/optional but are captured in the routing; they are present in all complete cases of their variants.
- WF_103 and WF_109 have no complete case in the window; their step sequences are the longest observed (partial) sequences ending at /hw/human_review, with early_exit_probability = 1.0.
- other_sequences probabilities for WF_102 and WF_108 (0.333) are shares over non-excluded cases (1 of 3 each); these non-canonical routings (no /ov/burn; extra /hbw/store_empty_bucket on hbw_1 before transport to human review) were observed only in early-exit cases.
- Variant mix probabilities use all 38 released cases (arrival mix); main sequences, step presence and per-step resources use complete cases; early-exit statistics use non-excluded cases.
- Queue discipline: hbw is served by activity priority (store > get_empty_bucket > store_empty_bucket > unload; FIFO agreement 0.50 vs case_age 0.985 over 66 decisions); vgr is FIFO (agreement 1.00 over 21 decisions); all other resource classes show no contention (100% extraneous waiting) and are FIFO.
- Intra-case concurrency: the next step is requested while the previous step still runs for the pairs (store_empty_bucket -> burn|vgr|wt), (vgr -> get_empty_bucket), (get_empty_bucket -> vgr); modeled via concurrent_with_previous flags per variant.

## Provenance
| Section | Author | Written |
|---|---|---|
| log_schema | data-analysis-agent | 2026-10-14T16:54:19.110826+00:00 |
| window | topology-analysis-agent (draft_topology_spec) | 2026-10-14T20:00:50.712583+00:00 |
| resources | topology-analysis-agent (draft_topology_spec) | 2026-10-14T20:00:50.721923+00:00 |
| variants | topology-analysis-agent | 2026-10-14T21:19:56.160087+00:00 |
| control_policies | topology-analysis-agent | 2026-10-14T21:19:56.498485+00:00 |
| initial_state | topology-analysis-agent | 2026-10-14T21:19:56.482897+00:00 |
| assumptions | topology-analysis-agent | 2026-10-14T21:19:56.144285+00:00 |
| activities | distribution-fitting-agent | 2026-10-15T07:21:35.733276+00:00 |
| arrivals | inter-arrival-times-agent | 2026-10-14T21:49:06.883058+00:00 |
