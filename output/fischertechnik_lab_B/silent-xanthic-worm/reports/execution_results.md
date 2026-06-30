# Execution Results

## Simulation Run (seed=42)

**Status:** SUCCESS

### Summary
- Total events logged: 405
- Unique cases: 33
- Workflow types: 9
- Successful operations: 400
- Failed operations: 5

### Events by Resource
| Resource | Count |
|----------|-------|
| vgr_1    | 80    |
| hbw_2    | 64    |
| vgr_2    | 36    |
| mm_1     | 34    |
| ov_1     | 31    |
| hbw_1    | 30    |
| hw_1     | 26    |
| wt_1     | 22    |
| sm_1     | 20    |
| mm_2     | 13    |
| pm_1     | 12    |
| wt_2     | 11    |
| sm_2     | 11    |
| ov_2      | 9    |
| dm_2      | 6    |

### Events by Workflow Type
| Variant | Count |
|---------|-------|
| WF_101  | 99    |
| WF_109  | 65    |
| WF_104  | 55    |
| WF_102  | 49    |
| WF_103  | 39    |
| WF_108  | 33    |
| WF_1106 | 28    |
| WF_105  | 22    |
| WF_1107 | 15    |

### Time Range
- First event: 199.4s
- Last event: 7190.0s

### Schema Verification
All 8 required columns present with correct types:
- case_id (str)
- variant (str)
- activity (str)
- resource (str)
- time:timestamp (float64)
- operation_end_time (float64)
- lifecycle:state (str)
- response_status_code (int64)

### Fixes Applied
1. **FIX 1:** BATCH_SIZE_PROBS corrected to sum to 1.0 (adjusted to [0.53, 0.08, 0.15, 0.08, 0.08, 0.08])
2. **FIX 2:** wt_1 retry logic now logs initial failure before retry loop (both main workflow and storage tail)
3. **FIX 3:** Workflow-specific storage tails with pre-storage vgr_1 for WF_102, WF_104, WF_105
4. **FIX 4:** WF_105 routing now includes vgr_1 transport before human_review