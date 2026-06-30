# Execution Results — Fischertechnik Lab C Simulation

## Run Summary

| Metric | Value |
|---|---|
| Total events | 497 |
| Simulation time | 4656s (77.6 min) |
| Warm-up period | 466s (10%) |
| Post-warmup events | 489 |
| Success events | 489 |
| Failure events | 8 |
| Average processing time | 30.43s |
| Seed | 42 |

## Variant Distribution

| Variant | Events |
|---|---|
| WF_103 | 133 |
| WF_105 | 71 |
| WF_101 | 62 |
| WF_102 | 61 |
| WF_104 | 58 |
| WF_109 | 39 |
| WF_1106 | 33 |
| WF_108 | 22 |
| WF_1107 | 18 |

## Resource Utilization (Event Count)

| Resource | Events |
|---|---|
| hbw_2 | 92 |
| vgr_1 | 81 |
| vgr_2 | 43 |
| mm_1 | 41 |
| ov_1 | 40 |
| hbw_1 | 30 |
| sm_1 | 28 |
| wt_1 | 26 |
| mm_2 | 20 |
| hw_1 | 20 |
| ov_2 | 17 |
| pm_1 | 17 |
| sm_2 | 17 |
| wt_2 | 15 |
| dm_2 | 10 |

## Lifecycle States

| State | Count |
|---|---|
| success | 489 |
| failure | 8 |

## Activity Distribution

| Activity | Count |
|---|---|
| /vgr/pick_up_and_transport | 124 |
| /hbw/unload | 49 |
| /hbw/store_empty_bucket | 43 |
| /ov/burn | 42 |
| /wt/pick_up_and_transport | 41 |
| /mm/deburr | 33 |
| /sm/transport | 27 |
| /hw/human_review | 20 |
| /mm/mill | 19 |
| /sm/sort | 18 |
| /hbw/get_empty_bucket | 16 |
| /ov/temper | 15 |
| /hbw/store | 14 |
| /mm/drill | 9 |
| /pm/punch_recesses | 8 |
| /pm/punch_gill | 6 |
| /dm/lower | 6 |
| /pm/punch_ribbing | 3 |
| /dm/cylindrical_drill | 2 |
| /dm/drill | 2 |

## Contract Conformance

- ✅ `run_single_replication(seed)` returns non-empty DataFrame
- ✅ All required columns present: case_id, variant, activity, resource, time:timestamp, operation_end_time, lifecycle:state, response_status_code
- ✅ All resource values are keys in RESOURCE_CAPACITIES
- ✅ All variant values match report vocabulary (WF_101–WF_1107)
- ✅ All activity values match report vocabulary
- ✅ lifecycle:state contains only 'success' and 'failure'
- ✅ operation_end_time ≥ time:timestamp for all rows
- ✅ File is importable with no simulation work at import time
- ✅ Demo run guarded behind `if __name__ == "__main__":`

## Notes

- The simulation uses a bursty two-stage arrival process with exponential inter-burst gaps (mean 612s) and constant intra-burst IAT (13s).
- Processing times use empirical means as constants for N < 30, with parametric distributions (triangular, uniform, normal, exponential) for larger samples.
- WF_104 includes a deterministic rework loop (1 cycle) as observed in the data.
- Human review is conditional per process model with probabilities from the quantities_quality_report.
- Failure rates: /hbw/unload at 5.4%, /vgr/pick_up_and_transport at 2.9%.