# Extraction Plan Report — Fischertechnik Lab B

## 1. Dataset Characteristics

| Property | Value |
|---|---|
| Source | `eventlog_cleaned.parquet` |
| Events | 1,383 (461 entities × 3 transitions: scheduled → start → complete) |
| Entities (workpiece operations) | 461 |
| Workflow instances (cases) | 38 (including 3 failure-only truncated cases) |
| Workflow templates | 9 (WF_101, WF_102, WF_103, WF_104, WF_105, WF_108, WF_109, WF_1106, WF_1107) |
| Distinct operations | 20 |
| Distinct resources | 15 (8 resource classes) |
| Time span | ~2 hours (2021-06-30 16:04–18:03 UTC) |
| Failure events | 9 (1.96% of entities) |

**Grain model:** Each entity is a single atomic operation on a workpiece. A *case* groups sequential operations that process one workpiece through its full manufacturing route. Operations within a case are ordered by timestamp.

---

## 2. Routing Sequences (Summary)

All workflows share a common backbone:

```
hbw_2 (unload) → vgr_2 (transport) → hbw_2 (store_empty_bucket) → [processing lane] → hw_1 (human_review) → [optional storage tail]
```

Two parallel processing lanes exist:
- **Lane 1 (mm_1):** ov_1 → wt_1 → mm_1 → sm_1 → pm_1 (shared)
- **Lane 2 (mm_2):** ov_2 → wt_2 → mm_2 → sm_2 → dm_2

| Workflow | Lane | Core Operations | Deterministic? | Storage Tail? |
|---|---|---|---|---|
| WF_101 | 1 | burn → temper → mill → deburr → sort | Yes | Conditional (83%) |
| WF_102 | 2 | [burn] → drill → lower | Yes (burn optional) | Conditional (60%) |
| WF_103 | 1 | burn → temper → mill → deburr → punch_recesses | Yes | No |
| WF_104 | 2→1 (dual) | [burn] → mill → sort → deburr → punch_gill | Partial (retries) | Conditional (60%) |
| WF_105 | 1 | burn → deburr → sort | Yes | Conditional (50%) |
| WF_108 | 2 | [burn] → drill → deburr → sort | Yes (burn optional) | Conditional (67%) |
| WF_109 | 1 | burn → temper → mill → deburr → punch_ribbing | Yes | No |
| WF_1106 | 2 | burn → {deburr/mill/transport} → cyl_drill | No (step 6 varies) | Conditional (50%) |
| WF_1107 | 1 | burn → {transport/mill} → {ribbing/recesses} | No (steps 7,9 vary) | Yes (100%) |

---

## 3. Sub-Agent Deployment Table

| Sub-Agent | Deploy? | Reason |
|---|---|---|
| **durations-processing-times** | **YES** | `actual_duration` (computed from start events) and `planned_operation_time` (all rows) are available for all 461 entities. Three duration measures exist: actual processing time, planned time, and complete service time (queue + processing). |
| **inter-arrival-times** | **YES** | `time:timestamp` exists for all 1,383 events. 38 workflow instances (including 3 failure-only cases) provide arrival data. Inter-arrival times computed between consecutive case starts and between consecutive operations within cases. |
| **quantities-quality** | **YES** | 9 failure events (1.96%) with explicit `lifecycle:state == 'failure'`. Retry patterns observed (WF_104_8: 3 attempts on wt_1). Failure probability and retry-delay parameters needed. |
| **distribution-fitting** | **YES** | Required for all extracted processing times, inter-arrival times, and retry delays. Fitting at activity-resource level with pooling for low-sample combinations. |

---

## 4. Extraction Steps

### Step 1 — Processing Times (Actual and Planned)

**Primary source:** `actual_duration` (available on `start` transition events, 461 values)
**Secondary source:** `planned_operation_time` (available on all 1,383 rows)
**Tertiary source:** `complete_service_time` (available on `complete` events, 461 values)

**Grouping strategy:**

1. **Activity-resource level (primary granularity):** Extract actual processing times grouped by `(concept:name, org:resource)` pairs. This is the base level for all 20 operations × 15 resources.

2. **Split only where difference is real and measurable:** For resources that perform multiple activities (e.g., `mm_1` performs `/mm/mill`, `/mm/deburr`, `/mm/transport_from_to`), keep each activity separate because planned durations differ (5–222s range). Do not merge activities on the same resource unless their actual duration distributions are statistically indistinguishable.

3. **Pool low-sample combinations within resource class:** Where an activity-resource pair has fewer than ~5 observations, pool with the same activity on the sibling resource in the same class (e.g., `/mm/mill` on `mm_1` and `mm_2` pooled if either has <5 samples). Transport operations (`/vgr/pick_up_and_transport` on `vgr_1` vs `vgr_2`) may be pooled at the resource-class level if lane-specific differences are not statistically significant.

4. **Planned durations as separate extraction:** Extract `planned_operation_time` grouped by `(concept:name, org:resource)` as a parallel dataset for comparison and validation against actual durations. These represent the system's expected processing times and serve as a baseline.

**What to extract per group:**
- Actual duration: mean, std, min, max, sample count
- Planned duration: mean, std, min, max, sample count
- Ratio of actual/planned (to identify systematic deviations)

**What to skip:**
- Do not extract processing times at the individual entity level — aggregate to activity-resource groups.
- Do not merge activities across different resource classes (e.g., `/vgr/pick_up_and_transport` and `/wt/pick_up_and_transport` are different operations despite similar names).

---

### Step 2 — Inter-Arrival Times

**Source:** `time:timestamp` for all events; `case` column to identify workflow instances.

**Scope:** All 38 cases, including the 3 failure-only truncated cases (WF_102_17, WF_104_9, WF_104_7). These represent real system inputs — a workpiece was scheduled even if it failed immediately.

**Extraction levels:**

1. **Case-level inter-arrival times:** Time between the first event (`scheduled` transition) of consecutive cases, ordered by timestamp. This captures the arrival rate of new workpieces into the system.

2. **Within-case inter-operation times:** Time between consecutive operations within the same case. This captures the handoff delay between resources (includes queueing + transport). These are not pure inter-arrival times but represent the effective delay between sequential resource requests.

3. **Workflow-type-stratified arrivals:** Group case-level inter-arrival times by `process_model_id` to detect if different workflow types arrive at different rates.

**What to skip:**
- Do not compute inter-arrival times between individual entities within a case as independent arrivals — they are sequential operations on the same workpiece.
- Do not exclude truncated cases from arrival analysis — their first timestamp is a valid arrival event.

---

### Step 3 — Failure and Rework Parameters

**Source:** `lifecycle:state` column (9 failure entries out of 461 entities).

**Extraction:**

1. **Failure probability by activity-resource:** Compute `P(failure | activity, resource)` for each `(concept:name, org:resource)` pair. Most pairs will have 0 failures; the non-zero rates are:
   - `/hbw/store_empty_bucket` @ `hbw_2`: 2 failures
   - `/hbw/unload` @ `hbw_2`: 2 failures
   - `/wt/pick_up_and_transport` @ `wt_1`: 4 failures (including 2 retries)
   - `/vgr/pick_up_and_transport` @ `vgr_1`: 1 failure

2. **Retry-delay parameters:** For the WF_104_8 retry pattern (3 consecutive wt_1 transport attempts), extract the time between failed attempt and retry attempt. This is the delay between entity `a_14015` (failed), `a_14055` (failed), and `a_14239` (succeeded).

3. **Failure outcome classification:**
   - **Terminal failure:** Entity removed from workflow (6 cases: a_13354, a_13611, a_15150, a_15339, a_16268, and the 2 terminal retries in WF_104_8)
   - **Non-terminal (absorbed):** Workflow continued despite failure (2 cases: a_16539, a_17498)
   - **Retried with success:** 1 case (a_14239, 3rd attempt succeeded)

4. **Case-level failure rate:** 3 out of 38 cases had at least one failure (7.9%). 2 cases terminated at the first step (WF_102_17, WF_104_9).

**What to skip:**
- Do not model failure as a generic parameter — extract per activity-resource pair.
- Do not defer failure modeling to manual implementation — extract explicit probabilities and retry delays.

---

### Step 4 — Distribution Fitting

**Input:** All extracted processing times (Step 1), inter-arrival times (Step 2), and retry delays (Step 3).

**Fitting strategy:**

1. **Processing times (per activity-resource group):**
   - Fit candidate distributions: Exponential, Normal, Lognormal, Weibull, Gamma, Uniform
   - Select best fit using AIC/BIC and Kolmogorov-Smirnov test
   - For groups with <5 samples, report raw statistics only and flag for pooling or manual review
   - Compare fitted actual distribution against planned duration (single value or narrow distribution)

2. **Inter-arrival times (case-level):**
   - Fit candidate distributions to the 37 inter-arrival intervals between 38 cases
   - Given the small sample (37 values), prioritize Exponential and Uniform fits
   - Report goodness-of-fit metrics with appropriate caveats about sample size

3. **Retry delays:**
   - Only 1 retry pattern observed (2 delays in WF_104_8). Report raw values; do not fit a distribution with n=2.

4. **Within-case inter-operation times:**
   - Fit distributions per sequential operation pair (e.g., time from `hbw/unload` to `vgr/transport` within a case)
   - Pool across workflow types where the same resource transition occurs

**What to skip:**
- Do not fit distributions to groups with fewer than 3 samples — report raw statistics and flag for manual handling.
- Do not force a single distribution family across all activities — each activity-resource pair may have a different best-fit distribution.

---

## 5. What to Skip and Why

| Parameter | Skip? | Reason |
|---|---|---|
| Entity-level processing times | Yes | Aggregate to activity-resource groups; individual times are noise |
| Inter-arrival times between entities within a case | Yes | These are sequential operations, not independent arrivals |
| Failure distribution fitting (n < 3) | Yes | Only 9 failures total; report probabilities, not distributions |
| Retry delay distribution fitting | Yes | Only 2 retry delays observed; report raw values |
| Quantities/batch sizes | Yes | No batch/quantity columns in dataset; all entities are single units |
| `complete_service_time` as processing time | No (but secondary) | Use for queue time analysis (service_time − actual_duration = queue time), not as primary processing time |
| Storage tail as separate extraction | No | Storage tail operations use standard resources (hbw_1, vgr_1); extract their processing times normally as part of the activity-resource groups |

---

## 6. Extraction Summary

| Step | Sub-Agent | Parameters Extracted | Data Source |
|---|---|---|---|
| 1 | durations-processing-times | Actual processing times (per activity-resource), Planned durations (per activity-resource), Actual/planned ratios | `actual_duration`, `planned_operation_time`, `complete_service_time` |
| 2 | inter-arrival-times | Case-level inter-arrival times, Within-case inter-operation times, Workflow-type-stratified arrivals | `time:timestamp`, `case`, `process_model_id` |
| 3 | quantities-quality | Failure probability (per activity-resource), Retry delay (raw values), Failure outcome classification | `lifecycle:state`, `time:timestamp`, `identifier:id` |
| 4 | distribution-fitting | Best-fit distribution per activity-resource (processing), Best-fit for case inter-arrivals, Goodness-of-fit metrics | Outputs from Steps 1–3 |

**Total sub-agents to deploy: 4 of 4**

**Estimated parameter groups:** ~25 activity-resource pairs for processing times, 1 case-level inter-arrival distribution, ~9 failure probability estimates, 2 raw retry delay values.

---

*Report generated from `column_mapping_report.md` and `topology_report.md`.*
