# Execution Results

## Run 1 (seed=42)

**Status:** SUCCESS

### Summary
- Total events: 232
- Unique cases: 18
- Variants: 9 (WF_101, WF_102, WF_103, WF_104, WF_105, WF_108, WF_109, WF_1106, WF_1107)
- Activities: 20 (all matching report vocabulary)
- Resources: 15 (all matching RESOURCE_CAPACITIES keys)
- States: 224 success, 8 failure
- Time range: 0.00 - 2233.74 seconds (within SIMULATION_TIME=2280)

### Per-Variant Event Counts
| Variant | Cases | Events |
|---------|-------|--------|
| WF_101  | 2     | 25     |
| WF_102  | 2     | 24     |
| WF_103  | 2     | 31     |
| WF_104  | 2     | 30     |
| WF_105  | 2     | 25     |
| WF_108  | 2     | 24     |
| WF_109  | 2     | 22     |
| WF_1106 | 2     | 27     |
| WF_1107 | 2     | 24     |

### Contract Conformance
- ✅ `run_single_replication(seed)` returns non-empty DataFrame
- ✅ All required columns present: case_id, variant, activity, resource, time:timestamp, operation_end_time, lifecycle:state, response_status_code
- ✅ All resource values are keys in RESOURCE_CAPACITIES
- ✅ All variant values match report vocabulary
- ✅ All activity values match report vocabulary
- ✅ lifecycle:state values are 'success' or 'failure' only
- ✅ Times are numeric floats (seconds from 0)
- ✅ operation_end_time >= time:timestamp
- ✅ SIMULATION_TIME = 2280
- ✅ RESOURCE_CAPACITIES has 15 entries, all capacity 1
- ✅ Module importable without side effects (demo run guarded by `if __name__ == "__main__"`)
- ✅ Both `random.seed(seed)` and `np.random.seed(seed)` called at start of replication
