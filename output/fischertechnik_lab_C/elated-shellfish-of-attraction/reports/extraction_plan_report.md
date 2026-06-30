# Extraction Plan Report — Fischertechnik Lab C Manufacturing System

## 1. Dataset Characteristics

| Property | Value |
|---|---|
| Source file | `eventlog_cleaned.parquet` |
| Total rows | 1,137 (379 operations × 3 lifecycle transitions) |
| Unique operations | 379 |
| Unique cases (workpieces) | 37 |
| Unique process models | 9 (WF_101–WF_1107) |
| Unique activities | 21 |
| Unique resources | 15 |
| Time span | 2021-07-01 (single simulated day) |
| Lifecycle transitions | scheduled → start → complete |
| Failure events | 5 (1.3% of operations) |

## 2. Routing Sequences Summary

The system comprises **two parallel production tracks** with shared bottleneck resources:

- **Track 1 (Shop Floor 1):** ov_1 → wt_1 → mm_1 → sm_1 → pm_1 (optional)
- **Track 2 (Shop Floor 2):** ov_2 → wt_2 → mm_2 → sm_2 → dm_2 (optional)
- **Shared:** hw_1 (human review), hbw_1/hbw_2 (storage), vgr_1/vgr_2 (transport)

**9 process models** define distinct routing patterns:
- **WF_101:** Full process with temper (Track 1) — mandatory human review
- **WF_102:** Drill & lower (Track 2) — conditional human review
- **WF_103:** Punch recesses (Track 1) — conditional human review
- **WF_104:** Cross-track rework loop — mandatory human review with probabilistic rework
- **WF_105:** Simple deburr (Track 1) — conditional human review
- **WF_108:** Drill & deburr (Track 2) — conditional human review
- **WF_109:** Punch ribbing (Track 1) — conditional human review
- **WF_1106:** Variable milling & drilling (Track 2) — high routing variability
- **WF_1107:** Punch gill (Track 1) — conditional human review

**Key non-deterministic elements:**
- Conditional human review (7 of 9 process models)
- WF_104 rework loop (feedback from hw_1 to Track 2)
- Optional transport steps (vgr_2, wt_1, wt_2)
- Variable mm_2 activities in WF_1106 (4 types)
- Variable dm_2 activities in WF_1106 (2 types)

## 3. Extraction Steps

### Step 1: Extract Processing Times Per Activity-Resource Pair

**Objective:** Compute actual processing durations for each (resource, activity) combination from the cleaned event log.

**Method:**
- Filter to `start` lifecycle transitions to isolate processing events
- Use `actual_processing_duration` column (computed as `operation_end_time − time:timestamp`)
- Group by `(org:resource, concept:name)` to get per-activity processing times
- Exclude `scheduled` and `complete` transitions (they represent queueing and completion events, not processing)

**Special handling:**
- **/ov/burn:** Use actual observed mean (~31s), not planned time (222s). The planned time is incorrect for the digital twin; actual behavior reflects the true processing duration.
- **/hbw/unload 0.03s outlier:** Flag and exclude this data error from processing time statistics.
- **Batch operations:** For dm and pm activities, note that `parameter_quantity` indicates batch sizes (dm/cylindrical_drill: 8, dm/drill: 6, mm/drill: 4, pm/punch_gill: 8, pm/punch_recesses: 6, pm/punch_ribbing: 6). Processing times should be reported both per-operation and per-unit (divided by batch quantity).

**Output:** Table of processing time statistics (mean, std, min, max, count) per (resource, activity) pair.

### Step 2: Extract Inter-Arrival Times

**Objective:** Determine the global arrival process for workpieces entering the system.

**Method:**
- Identify case arrival times as the `scheduled` timestamp of the first operation in each case (typically `hbw_2/unload`)
- Sort cases by arrival time and compute inter-arrival times between consecutive cases
- Record the process model (`process_model_id`) for each arriving case to determine the mix proportions

**Special handling:**
- **Single global arrival process:** All 9 process models are interleaved draws from one arrival stream. The arrival process is not per-model but global, with the process model assigned at arrival according to observed proportions.
- **Process model mix:** Compute the proportion of each process model in the arrival stream (WF_101: 4/37, WF_102: 5/37, etc.) to define the product mix for the simulation.

**Output:** Inter-arrival time series, process model mix proportions, and arrival rate statistics.

### Step 3: Extract Quality and Rework Parameters

**Objective:** Quantify the quality mechanisms that drive conditional routing and rework.

**Method:**
- **Human review pass/fail rates:** For each process model, compute the proportion of cases that undergo human review and the pass rate among those reviewed.
  - Mandatory review: WF_101, WF_104
  - Conditional review: WF_102, WF_103, WF_105, WF_108, WF_109, WF_1106, WF_1107
- **WF_104 rework probability:** From the observed WF_104 cases, determine the probability that a failed human review triggers a rework loop (feedback to Track 2).
- **Failure rates:** Compute per-activity failure rates from the 5 observed failure events. Note that the sample size is small (5/379 = 1.3%), so failure rates should be reported with appropriate uncertainty.

**Special handling:**
- **WF_104 rework:** Treat as a probabilistic branch after human review. The rework loop sends the workpiece back through Track 2 (ov_2 → mm_2 → sm_2) before returning to Track 1 for deburr → punch_gill → human review.
- **Truncated cases:** Distinguish real scrap (failure state) from missing data (success state but incomplete sequence). Only count confirmed failures in failure rate calculations.

**Output:** Human review probabilities per process model, WF_104 rework probability, per-activity failure rates.

### Step 4: Extract Workpiece Size Distribution

**Objective:** Determine if workpiece size affects processing times and should be modeled as a covariate.

**Method:**
- Extract `parameter_burn_workpiece_size` from ov/burn operations (sizes: regular, middle, large, maxi)
- Cross-reference workpiece sizes with processing times for downstream activities
- Perform correlation analysis to determine if size significantly affects processing durations

**Special handling:**
- All observed cases have `parameter_burn_workpiece_thickness` = "thin", so thickness is not a variable factor.
- If size does not significantly affect processing times, it can be excluded from the simulation model.

**Output:** Workpiece size distribution, size-dependent processing time analysis (if significant).

### Step 5: Fit Distributions to Processing and Inter-Arrival Times

**Objective:** Identify parametric distributions that best fit the observed processing times and inter-arrival times for use in the discrete-event simulation.

**Method:**
- For each (resource, activity) processing time series, fit candidate distributions (exponential, normal, lognormal, gamma, Weibull) using maximum likelihood estimation
- Select the best-fitting distribution using goodness-of-fit tests (Kolmogorov-Smirnov, Anderson-Darling) and information criteria (AIC, BIC)
- Fit the global inter-arrival time series to candidate distributions
- Report distribution parameters and goodness-of-fit metrics for each selected distribution

**Special handling:**
- **Small sample sizes:** Some activity-resource combinations have very few observations (e.g., pm_1 activities: 24 total across 3 activity types). For small samples, report the empirical distribution alongside parametric fits and note the uncertainty.
- **/ov/burn:** Use the actual observed distribution (~31s mean), not the planned time.
- **Batch operations:** Fit distributions to per-unit processing times (total time divided by batch quantity) for dm and pm activities.

**Output:** Best-fitting distribution and parameters for each processing time and inter-arrival time series.

## 4. What to Skip and Why

| Extraction | Decision | Reason |
|---|---|---|
| Queueing times as separate extraction | Skip | Queueing times are derived from the interaction of arrival rates, processing times, and resource capacity in the simulation. They do not need to be extracted as input parameters. |
| Planned operation times | Skip (except for comparison) | The digital twin models actual behavior. Planned times are only useful for validating discrepancies (e.g., /ov/burn planned=222s vs actual=31s). |
| Complete service times | Skip | These include queueing delays and are not pure processing times. They are useful for validation but not as simulation inputs. |
| Resource pooling parameters | Skip | Resource pooling is determined by the topology (two independent tracks with shared bottlenecks), not by statistical extraction. |
| Transport time variability by distance | Skip | Transport operations are modeled as single activities per resource. Distance-based variability is not observable from the current data. |

## 5. Agent Deployment Table

| Sub-Agent | Deploy? | Reason |
|---|---|---|
| **durations-processing-times** | ✅ Yes | Timestamp pairs exist for all 379 operations. Need to extract processing times per (resource, activity) pair, handle /ov/burn actual vs planned discrepancy, filter /hbw/unload outlier, and account for batch quantities. |
| **inter-arrival-times** | ✅ Yes | Case arrival timestamps exist (first `scheduled` event per case). Need to compute global inter-arrival times and process model mix proportions for the single arrival stream. |
| **quantities-quality** | ✅ Yes | Batch quantities exist in dm/pm operations (6 different quantity values). Workpiece sizes (4 categories) may affect processing times. WF_104 rework loop and conditional human review require quality parameter extraction. |
| **distribution-fitting** | ✅ Yes | Processing times and inter-arrival times require parametric distribution fitting for the discrete-event simulation. Small sample sizes for some activities require careful handling. |

## 6. Extraction Execution Order

1. **Processing times** (Step 1) — foundational data for all downstream analysis
2. **Inter-arrival times** (Step 2) — independent of processing times
3. **Quality and rework parameters** (Step 3) — depends on processing times for failure rate context
4. **Workpiece size distribution** (Step 4) — depends on processing times for correlation analysis
5. **Distribution fitting** (Step 5) — depends on all extracted time series

## 7. Data Quality Notes

- **/hbw/unload 0.03s outlier:** This is a data error and must be excluded from processing time statistics.
- **/ov/burn planned time (222s):** This is incorrect for the digital twin. Use actual observed mean (~31s).
- **Truncated cases:** 12 cases end with incomplete sequences. Distinguish real scrap (5 failure events) from missing data (7 incomplete success cases).
- **Small samples:** Some activity-resource combinations have fewer than 10 observations. Distribution fitting for these should be reported with appropriate uncertainty warnings.
- **Batch quantities:** dm and pm operations process multiple workpieces per operation. Processing times must be normalized by batch quantity for per-unit analysis.

---

*Extraction plan generated from analysis of `eventlog_cleaned.parquet` (1,137 rows, 379 operations, 37 cases, 9 process models, 15 resources)*
