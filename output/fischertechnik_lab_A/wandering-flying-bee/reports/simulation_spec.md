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
| /mm/deburr | mm_1, mm_2 | triang(c=0.3596, loc=14.05, scale=1.001) (mean 14.46; n=9; src fit_activity_durations) | 0.000 |
| /mm/drill | mm_1, mm_2 | triang(c=0.6725, loc=5.281, scale=15.62) (mean 14.44; n=4; src fit_activity_durations) | 0.000 |
| /mm/mill | mm_1, mm_2 | triang(c=0.005911, loc=5.047, scale=9.39) (mean 6.672; n=6; src fit_activity_durations) | 0.000 |
| /mm/transport_from_to | mm_2 | triang(c=0.5, loc=12.59, scale=0.547) (mean 12.87; n=2; src fit_activity_durations) | 0.000 |
| /ov/burn | ov_1, ov_2 | empirical quantiles [21.4 … 31.6 … 41.8] (mean 30.14; n=13; src fit_activity_durations) | 0.000 |
| /ov/temper | ov_1 | triang(c=0.5924, loc=51.45, scale=0.157) (mean 51.54; n=5; src fit_activity_durations) | 0.000 |
| /pm/punch_gill | pm_1 | constant(value=27.48) (mean 27.48; n=1; src fit_activity_durations) | 0.000 |
| /pm/punch_recesses | pm_1 | triang(c=0.5, loc=23.45, scale=0.375) (mean 23.64; n=2; src fit_activity_durations) | 0.000 |
| /pm/punch_ribbing | pm_1 | triang(c=0.5, loc=23.56, scale=7.657) (mean 27.39; n=2; src fit_activity_durations) | 0.000 |
| /sm/sort | sm_1, sm_2 | triang(c=0.01593, loc=8.36, scale=237.3) (mean 50.15; n=6; src fit_activity_durations) | 0.000 |
| /sm/transport | sm_1, sm_2 | triang(c=0.537, loc=14.39, scale=7.188) (mean 17.52; n=9; src fit_activity_durations) | 0.000 |
| /vgr/pick_up_and_transport | vgr_1, vgr_2 | empirical quantiles [13.1 … 42.8 … 88.4] (mean 41.97; n=50; src fit_activity_durations) | 0.091 |
| /wt/pick_up_and_transport | wt_1, wt_2 | empirical quantiles [25.9 … 26.4 … 29.2] (mean 27.38; n=14; src fit_activity_durations) | 0.000 |

## Variants
### WF_101 — p=0.111, early exit p=0.00
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

### WF_102 — p=0.111, early exit p=0.00
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

### WF_103 — p=0.111, early exit p=0.00
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
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
16. /vgr/pick_up_and_transport [vgr_1 100%]
17. /hbw/store [hbw_1 100%]

### WF_104 — p=0.111, early exit p=0.00
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
15. /vgr/pick_up_and_transport [vgr_1 100%]
16. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
17. /vgr/pick_up_and_transport [vgr_1 100%]
18. /hbw/store [hbw_1 100%]

### WF_105 — p=0.111, early exit p=0.00
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
13. /vgr/pick_up_and_transport [vgr_1 100%]
14. /hbw/store [hbw_1 100%]

### WF_108 — p=0.111, early exit p=0.00
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

### WF_109 — p=0.111, early exit p=0.00
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
14. /vgr/pick_up_and_transport [vgr_1 100%]
15. /hbw/get_empty_bucket [hbw_1 100%] ∥ concurrent with previous
16. /vgr/pick_up_and_transport [vgr_1 100%]
17. /hbw/store [hbw_1 100%]

### WF_1106 — p=0.111, early exit p=0.00
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

### WF_1107 — p=0.111, early exit p=0.00
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
- burst_size: categorical 1:0.50, 2:0.33, 3:0.17 (n=6; src control_policies.release_bursts.burst_size values [8,1,1,2,2,3,1] minus initial burst 8 -> 6 bursts [1,1,2,2,3,1]: P(1)=3/6, P(2)=2/6, P(3)=1/6, mean 1.667)
- intra_burst_iat: lognorm(s=0.774, loc=0, scale=1.178) (mean 1.589; n=11; src control_policies.release_bursts.burst_iat_s (mean 1.589, std 1.44, n 11); lognormal fitted to mean+std: s=sqrt(ln(1+(1.44/1.589)^2))=0.774, scale=1.589/exp(s^2/2)=1.178. (A triangular was infeasible: min 0.51/max 5.531 with mean 1.589 implies mode -1.27 s.))
- inter_burst_gap: triang(c=0.2061, loc=93.41, scale=706.6) (mean 377.5; n=6; src control_policies.release_bursts.gap_iat_s (mean 377.458, min 93.406, max 799.957, n 6); mode m=3*mean-min-max=239.01, c=(m-min)/(max-min)=0.2061 so (min+max+mode)/3=377.458. Infinite two-regime process (no max_bursts): long-run rate = burst_mean/gap_mean = 1.667/377.458 = 1 release per 226 s, matching the observed 10 post-initial-burst releases over ~1960 s. The observed 7 bursts / 18 releases is a censored finite-window draw (last ~911 s release-free), not a cap; an infinite process is required for MR4 (cases scale with horizon).)

## Control policies
- queue discipline: {'hbw': 'priority', 'vgr': 'fifo', 'mm': 'fifo', 'ov': 'fifo', 'wt': 'fifo', 'sm': 'fifo', 'pm': 'fifo', 'dm': 'fifo', 'hw': 'fifo'}
- priority order: {'hbw': ['/hbw/store', '/hbw/store_empty_bucket', '/hbw/get_empty_bucket', '/hbw/unload']}
- release rule: open (bursty releases)
- intra-case concurrency: /hbw/store_empty_bucket || /ov/burn; /hbw/store_empty_bucket || /vgr/pick_up_and_transport; /vgr/pick_up_and_transport || /hbw/get_empty_bucket

## Assumptions
- Canonical return tail: the end-of-process warehouse-return sequence (hbw_1/get_empty_bucket -> vgr_1/pick_up_and_transport -> hbw_1/store) is canonical for EVERY variant. Any absence in the log is time-window truncation, not optionality (authoritative context).
- No real early exits: discover_variant_routings flagged 'early_exit_probability' for 6 variants, but those are window truncation (cases cut before the return tail), not scrap/abandonment. early_exit_probability=0 for all variants (authoritative context).
- Routing inference excludes the 4 incomplete cases WF_104_21, WF_108_18, WF_109_16, WF_1107_17 (right-censored at window end); they are retained for service-time / arrival estimation (authoritative context).
- Retryable failures: the 8 failure events (7x HTTP 418 precondition, 1x HTTP 401 auth) are modelled as retryable - the operation retries and eventually succeeds; the workpiece continues (authoritative context).
- Role-based VGR assignment: vgr_2 performs the first transport of each case (hbw_2 -> first machine), vgr_1 performs all subsequent transports (authoritative context). Documented exceptions honored: WF_104 (cross-line, vgr_2 also used mid-route at step 7) and WF_108 (vgr_2 re-used at step 9).
- Cross-line routing: WF_104 is intentionally two-stage and is the ONLY variant allowed to route across lines (line-1 hbw_2/vgr_2 -> line-2 hbw_1/vgr_1 and back) (authoritative context).
- Stochastic sorting ejection: /sm/sort ejection position is modelled as uniform over {1,2,3} (authoritative context).
- Two-line physical layout (from transport start/end positions): Line 1 = hbw_2 (intake warehouse) -> vgr_2 -> machines (ov_1/ov_2, mm_1/mm_2, wt_1/wt_2, sm_1/sm_2, dm_2, pm_1); Line 2 = hbw_1 (return warehouse) -> vgr_1 -> hw_1 (human review) and the return path.
- HBW semantics: hbw_2 = intake warehouse (workpiece unload + empty-bucket store); hbw_1 = return warehouse (empty-bucket get + finished workpiece store). /hbw/store_empty_bucket and /hbw/unload are on hbw_2; /hbw/get_empty_bucket and /hbw/store are on hbw_1.
- Queue discipline: hbw uses activity priority (97.1% agreement vs 56% FIFO over 34 decision points) with order [store, store_empty_bucket, get_empty_bucket, unload]; vgr is FIFO (100% over 10 decision points); all other resource classes (mm, ov, wt, sm, pm, dm, hw) default to FIFO - no overtaking observed (contention share ~0).
- Release rule: open (no WIP cap, no completion trigger). Arrivals are bursty with a two-regime inter-arrival process (burst_iat ~1.6 s, gap_iat ~377 s, burst_size mean 2.57). Model the gap process and burst size separately, not the mixed mean IAT.
- Intra-case concurrency: bucket operations overlap with workpiece steps - /hbw/store_empty_bucket || /ov/burn (4 cases), /hbw/store_empty_bucket || /vgr/pick_up_and_transport (3), /vgr/pick_up_and_transport || /hbw/get_empty_bucket (2). The next step is requested before the previous releases its resource; model as concurrent SimPy processes.
- Per-step resource assignment is taken from the longest observed case per variant (resources_by_step). Machine assignment may vary between cases (e.g. mm_1 vs mm_2, ov_1 vs ov_2, sm_1 vs sm_2); the spec pins the dominant observed resource per step.
- Window: t0=2021-07-06T15:08:27.914751Z, horizon 3183.2 s (~53 min), 18 cases, 192 activity instances. terminal_activity=/hbw/store, first_activity=/hbw/unload.
- Initial WIP at window start = 0 (no cases in progress at t0).
- WF_104 starts with /vgr/pick_up_and_transport on vgr_2 (no /hbw/unload) - consistent with its cross-line two-stage design where the workpiece is picked up directly by vgr_2.
- WF_1106 does NOT use /hbw/store_empty_bucket (it uses /hbw/get_empty_bucket on hbw_1 mid-route at step 5) - a variant-specific bucket flow distinct from the other 8 variants.
- Failure-retry semantics: a failed instance (418/401) is followed by a re-request of the same activity that succeeds; the failed attempt's service time is not counted as a completed operation.
- Quantity is a per-variant deterministic parameter, observable only at feature-processing steps (drill/punch): WF_102=6 (/mm/drill), WF_103=6 (/pm/punch_recesses), WF_104=8 (/pm/punch_gill), WF_108=4 (/mm/drill), WF_109=6 (/pm/punch_ribbing), WF_1106=4 (/dm/cylindrical_drill). WF_1107 is step-dependent (6 at /mm/drill, 10 at /pm/punch_ribbing) - flagged, model per-step not per-variant. WF_101/WF_105 have no quantity parameter (no drill/punch step) - N/A, not 1.
- workpiece_size at /ov/burn is CATEGORICAL and deterministic per variant: WF_101=regular, WF_102=middle, WF_103=large, WF_104=maxi, WF_105=regular, WF_108=maxi, WF_109=regular, WF_1106=middle, WF_1107=large. burn_workpiece_thickness is also deterministic per variant: thin (WF_101/102/103/104/109), thick (WF_105/108/1106/1107).
- workpiece_size at drill steps is NUMERIC, extracted separately from the burn encoding (not merged): /mm/drill: WF_102=30, WF_108=30, WF_1107=40 (all deterministic); /dm/cylindrical_drill WF_1106 varies across cases (50 vs 60) - flagged, not deterministic, model as discrete {50,60}.
- No quality/rework/scrap data exist in the log; no scrap (early_exit_probability=0 for all variants, incomplete cases are window truncation); the only quality signal is the 8 retryable failures (7x HTTP 418, 1x HTTP 401) handled by the failure-rate extraction.
- Routing inconsistency flagged during quantity extraction: log contains an /ov/burn instance for WF_102_32 (size middle, thin) although the spec WF_102 route has no burn; WF_1106_21 has no /ov/burn instance although the spec WF_1106 route has burn at step 3 - burn presence varies across cases within WF_102/WF_1106, verify at modeling stage.
- Service-time duration rule: actual service time = operation_end_time - time:timestamp on the `start` row only. complete_service_time (includes queueing) is never used; planned_operation_time is reference only.
- Service-time sample: successful attempts only (n=184). The 8 failed attempts (7x HTTP 418, 1x HTTP 401) are excluded from service times; a failed attempt is not a completed operation. Failure rates are computed over all 192 attempts (failed in denominator).
- The 4 incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) are RETAINED for service-time estimation per confirmed decision (window truncation, not abandonment).
- Grouping: per activity, pooling only across machine pairs performing the same activity (mm_1+mm_2, ov_1+ov_2, wt_1+wt_2, sm_1+sm_2); never across different activities. Single pooled transport distribution for vgr_1+vgr_2 (identical hardware) per confirmed decision - flagged for revisit at the modeling stage.
- /ov/burn duration is size-dependent: burn_workpiece_size (regular/middle/large/maxi, deterministic per variant) shows non-overlapping duration ranges - regular 21.4-26.6 s (n=5, mean 23.55), middle 26.9-31.8 s (n=2, mean 29.37), large 31.6-36.7 s (n=3, mean 33.30), maxi 36.9-41.8 s (n=3, mean 38.50). The spec carries the single pooled per-activity distribution (n=13, mean 30.14 s); per-category distributions are recommended for the modeling stage (flagged).
- Sparse/low-confidence groups (n <= 5): /pm/punch_gill (n=1, constant), /dm/cylindrical_drill (n=2), /dm/lower (n=2), /mm/transport_from_to (n=2), /pm/punch_recesses (n=2), /pm/punch_ribbing (n=2), /hbw/store (n=3), /mm/drill (n=4), /ov/temper (n=5), /mm/mill (n=6), /sm/sort (n=6). Estimates flagged low confidence; no cross-activity pooling used.
- Outliers kept (real variability, not removed): /sm/sort max 245.7 s (WF_108_17, ~10x the other 5 values of 8.4-14.0 s); /mm/mill max 14.437 s (mm_2 vs ~5.1 s on mm_1); /vgr max 88.375 s; /hw/human_review max 62.25 s (human-paced, CV=1.37). No data-defect removals were made.
- /mm/mill is dominated by mm_1 at ~5.0-5.3 s; the single mm_2 observation (14.437 s) inflates the pooled mean to 6.67 s - flagged for the modeling stage.
- VGR pooled transport: vgr_1 (n=32, mean 42.64 s, includes 5 failed-attempt retries and the 88.4 s max) vs vgr_2 (n=18, mean 40.76 s, tighter). Pooled mean 41.97 s; the single pooled distribution is used per confirmed decision.
- Per-resource check (activity x resource): machine pairs are poolable within each activity - /mm/deburr mm_1 14.49 s (n=8) vs mm_2 14.24 s (n=1); /wt wt_1 26.09 s (n=8) vs wt_2 29.09 s (n=6); /ov/burn ov_1 27.20 s (n=8) vs ov_2 34.85 s (n=5) is confounded with workpiece size (ov_2 handles the larger pieces), consistent with the size-dependence flag. Exception: /sm/transport sm_1 19.92 s (n=5) vs sm_2 14.53 s (n=4) differ by ~37% - pooled distribution (mean 17.52 s) is used per the confirmed pooling decision, but a per-resource split is recommended for the modeling stage.

## Provenance
| Section | Author | Written |
|---|---|---|
| log_schema | data-analysis-agent | 2026-10-15T07:45:17.620163+00:00 |
| window | topology-analysis-agent (draft_topology_spec) | 2026-10-15T08:11:28.432578+00:00 |
| resources | topology-analysis-agent (draft_topology_spec) | 2026-10-15T08:11:28.439270+00:00 |
| variants | topology-analysis-agent | 2026-10-15T08:43:12.797959+00:00 |
| control_policies | topology-analysis-agent | 2026-10-15T08:16:14.202422+00:00 |
| initial_state | topology-analysis-agent | 2026-10-15T08:22:30.176375+00:00 |
| assumptions | durations-processing-times-agent | 2026-10-15T09:34:03.379859+00:00 |
| activities | durations-processing-times-agent | 2026-10-15T09:32:01.735272+00:00 |
| arrivals | simulation-evaluator-agent | 2026-10-15T13:29:36.704425+00:00 |
