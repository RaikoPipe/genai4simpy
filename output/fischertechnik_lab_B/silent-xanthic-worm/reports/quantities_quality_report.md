# Quantities & Quality Report — Fischertechnik Lab B

## 1. Dataset Summary

| Property | Value |
|---|---|
| Source | `eventlog_cleaned.parquet` |
| Total events | 1,383 (461 entities × 3 transitions) |
| Unique entities (operations) | 461 |
| Unique workflow instances (cases) | 38 |
| Workflow templates | 9 |
| Distinct resources | 15 |
| Time span | ~2 hours (2021-06-30 16:04–18:03 UTC) |

## 2. Overall Yield & Quality

| Metric | Value |
|---|---|
| Total completed operations | 461 |
| Successful operations | 452 |
| Failed operations | 9 |
| **Overall yield** | **98.05%** |
| **Overall failure rate** | **1.95%** |
| Cases with ≥1 failure | 7 / 38 (18.4%) |
| Cases terminated at first step | 2 (WF_102_17, WF_104_9) |

## 3. Failure Probability by Activity–Resource

Only 4 activity–resource pairs exhibit failures. All other 26 pairs have 0 failures.

| Activity | Resource | Total Ops | Failures | Failure Rate |
|---|---|---|---|---|
| `/wt/pick_up_and_transport` | `wt_1` | 27 | 4 | **14.81%** |
| `/hbw/store_empty_bucket` | `hbw_2` | 36 | 2 | **5.56%** |
| `/hbw/unload` | `hbw_2` | 38 | 2 | **5.26%** |
| `/vgr/pick_up_and_transport` | `vgr_1` | 85 | 1 | **1.18%** |

### 3.1 Failure Probability by Resource (Aggregated)

| Resource | Total Ops | Failures | Failure Rate |
|---|---|---|---|
| `wt_1` | 27 | 4 | **14.81%** |
| `hbw_2` | 74 | 4 | **5.41%** |
| `vgr_1` | 85 | 1 | **1.18%** |
| All others (12 resources) | 375 | 0 | **0.00%** |

### 3.2 Failure Probability by Workflow

| Workflow | Total Ops | Failures | Failure Rate |
|---|---|---|---|
| WF_104 | 59 | 4 | **6.78%** |
| WF_102 | 48 | 3 | **6.25%** |
| WF_1107 | 31 | 1 | **3.23%** |
| WF_109 | 53 | 1 | **1.89%** |
| WF_101, WF_103, WF_105, WF_108, WF_1106 | 260 | 0 | **0.00%** |

## 4. Failure Classification

### 4.1 Terminal Failures (entity removed from workflow)

| Entity | Case | Operation | Resource | Notes |
|---|---|---|---|---|
| a_13354 | WF_102_15 | `/hbw/store_empty_bucket` | hbw_2 | Terminal — no retry |
| a_13611 | WF_104_8 | `/hbw/store_empty_bucket` | hbw_2 | Terminal — no retry |
| a_14015 | WF_104_8 | `/wt/pick_up_and_transport` | wt_1 | Terminal — retried (a_14055) |
| a_14055 | WF_104_8 | `/wt/pick_up_and_transport` | wt_1 | Terminal — retried (a_14239) |
| a_15150 | WF_104_9 | `/hbw/unload` | hbw_2 | Terminal — case truncated |
| a_15339 | WF_102_16 | `/vgr/pick_up_and_transport` | vgr_1 | Terminal — case truncated |
| a_16268 | WF_102_17 | `/hbw/unload` | hbw_2 | Terminal — case truncated |

### 4.2 Non-Terminal Failures (workflow continued)

| Entity | Case | Operation | Resource | Retry Entity | Retry Delay |
|---|---|---|---|---|---|
| a_16539 | WF_109_6 | `/wt/pick_up_and_transport` | wt_1 | a_16822 | 73.87 s |
| a_17498 | WF_1107_7 | `/wt/pick_up_and_transport` | wt_1 | a_17555 | 79.08 s |

### 4.3 Retried with Success

| Entity | Case | Operation | Resource | Outcome |
|---|---|---|---|---|
| a_14239 | WF_104_8 | `/wt/pick_up_and_transport` | wt_1 | Success (3rd attempt) |

## 5. Retry-Delay Parameters

### 5.1 WF_104_8 — Three-Attempt Retry Pattern

Three consecutive `/wt/pick_up_and_transport` attempts on `wt_1`:

| Attempt | Entity | Outcome | Start Time (s) |
|---|---|---|---|
| 1 | a_14015 | Failure | 1.625068e+09 |
| 2 | a_14055 | Failure | 1.625068e+09 |
| 3 | a_14239 | Success | 1.625069e+09 |

| Delay | Seconds | Minutes |
|---|---|---|
| Attempt 1 → 2 | 69.14 s | 1.15 min |
| Attempt 2 → 3 | 129.61 s | 2.16 min |
| **Mean retry delay** | **99.37 s** | **1.66 min** |

### 5.2 Non-Terminal Retry Delays

| Case | Failed Entity | Retry Entity | Delay (s) | Delay (min) |
|---|---|---|---|---|
| WF_109_6 | a_16539 | a_16822 | 73.87 | 1.23 |
| WF_1107_7 | a_17498 | a_17555 | 79.08 | 1.32 |

### 5.3 Summary of All Retry Delays

| Statistic | Value (seconds) | Value (minutes) |
|---|---|---|
| Minimum | 69.14 | 1.15 |
| Maximum | 129.61 | 2.16 |
| Mean (all 3 delays) | 90.69 | 1.51 |
| Median | 79.08 | 1.32 |

**Note:** Only 3 retry-delay observations exist. Do not fit a distribution — use the mean (90.7 s) or median (79.1 s) as a point estimate for simulation retry-delay parameters.

## 6. Case-Level Yield Statistics

| Case | Workflow | Total Ops | Failures | Yield | Status |
|---|---|---|---|---|---|
| WF_101_13 | WF_101 | 15 | 0 | 100.0% | Complete |
| WF_101_14 | WF_101 | 16 | 0 | 100.0% | Complete |
| WF_101_15 | WF_101 | 12 | 0 | 100.0% | Complete |
| WF_101_16 | WF_101 | 12 | 0 | 100.0% | Complete |
| WF_101_17 | WF_101 | 12 | 0 | 100.0% | Complete |
| WF_101_18 | WF_101 | 16 | 0 | 100.0% | Complete |
| WF_102_14 | WF_102 | 10 | 0 | 100.0% | Complete |
| WF_102_15 | WF_102 | 14 | 1 | 92.9% | Failure |
| WF_102_16 | WF_102 | 9 | 1 | 88.9% | Failure |
| WF_102_17 | WF_102 | 1 | 1 | 0.0% | Failure (truncated) |
| WF_102_18 | WF_102 | 14 | 0 | 100.0% | Complete |
| WF_103_14 | WF_103 | 5 | 0 | 100.0% | Truncated (no failure) |
| WF_103_15 | WF_103 | 13 | 0 | 100.0% | Complete |
| WF_103_16 | WF_103 | 13 | 0 | 100.0% | Complete |
| WF_103_17 | WF_103 | 13 | 0 | 100.0% | Complete |
| WF_103_18 | WF_103 | 13 | 0 | 100.0% | Complete |
| WF_104_10 | WF_104 | 14 | 0 | 100.0% | Complete |
| WF_104_11 | WF_104 | 19 | 0 | 100.0% | Complete |
| WF_104_7 | WF_104 | 4 | 0 | 100.0% | Truncated (no failure) |
| WF_104_8 | WF_104 | 21 | 3 | 85.7% | Failure (retried) |
| WF_104_9 | WF_104 | 1 | 1 | 0.0% | Failure (truncated) |
| WF_105_10 | WF_105 | 8 | 0 | 100.0% | Complete |
| WF_105_11 | WF_105 | 8 | 0 | 100.0% | Complete |
| WF_105_8 | WF_105 | 14 | 0 | 100.0% | Complete |
| WF_105_9 | WF_105 | 14 | 0 | 100.0% | Complete |
| WF_108_7 | WF_108 | 15 | 0 | 100.0% | Complete |
| WF_108_8 | WF_108 | 10 | 0 | 100.0% | Complete |
| WF_108_9 | WF_108 | 15 | 0 | 100.0% | Complete |
| WF_109_5 | WF_109 | 13 | 0 | 100.0% | Complete |
| WF_109_6 | WF_109 | 14 | 1 | 92.9% | Failure (retried) |
| WF_109_7 | WF_109 | 13 | 0 | 100.0% | Complete |
| WF_109_8 | WF_109 | 13 | 0 | 100.0% | Complete |
| WF_1106_6 | WF_1106 | 10 | 0 | 100.0% | Complete |
| WF_1106_7 | WF_1106 | 14 | 0 | 100.0% | Complete |
| WF_1106_8 | WF_1106 | 14 | 0 | 100.0% | Complete |
| WF_1106_9 | WF_1106 | 8 | 0 | 100.0% | Truncated (no failure) |
| WF_1107_6 | WF_1107 | 15 | 0 | 100.0% | Complete |
| WF_1107_7 | WF_1107 | 16 | 1 | 93.8% | Failure (retried) |

## 7. Quantity Notes

**No batch/quantity columns exist in the dataset.** All entities represent single-unit operations (one workpiece processed at a time). The system operates in a unit-flow regime with no batching observed.

## 8. DES Simulation Parameters for Quality

### 8.1 Failure Probability Parameters

Use the following per-activity-resource failure probabilities in the simulation:

| Activity | Resource | P(failure) | Sample Size | Confidence |
|---|---|---|---|---|
| `/wt/pick_up_and_transport` | `wt_1` | **0.148** | 27 | Medium (n=27, 4 failures) |
| `/hbw/store_empty_bucket` | `hbw_2` | **0.056** | 36 | Low (n=36, 2 failures) |
| `/hbw/unload` | `hbw_2` | **0.053** | 38 | Low (n=38, 2 failures) |
| `/vgr/pick_up_and_transport` | `vgr_1` | **0.012** | 85 | Low (n=85, 1 failure) |
| All other pairs | — | **0.000** | varies | High (0 failures observed) |

### 8.2 Failure Outcome Behavior

| Failure Type | Count | Behavior |
|---|---|---|
| Terminal (no retry) | 5 | Entity removed; workflow truncated |
| Terminal (with retry) | 2 | Failed, then retried as new entity |
| Non-terminal (absorbed) | 2 | Failed, immediately retried; workflow continued |

### 8.3 Retry-Delay Parameter

| Parameter | Value |
|---|---|
| Mean retry delay | 90.7 seconds |
| Median retry delay | 79.1 seconds |
| Range | 69.1 – 129.6 seconds |
| Sample size | 3 observations |
| Recommendation | Use **Exponential(λ = 1/90.7)** or **Uniform(69, 130)** for retry delay in simulation. Do not fit distribution (n=3). |

### 8.4 Failure Modeling Guidance

1. **`wt_1` (`/wt/pick_up_and_transport`)** is the dominant failure source (14.8% failure rate). Model with explicit retry logic: on failure, generate a new entity for the same operation after a delay drawn from the retry-delay distribution.
2. **`hbw_2` failures** (`/hbw/unload` and `/hbw/store_empty_bucket`) are typically terminal — the case is truncated. Model as scrap/reject with no retry.
3. **`vgr_1` failure** is rare (1.2%) and terminal. Model as scrap with no retry.
4. **Non-terminal failures** (WF_109_6, WF_1107_7) show the system can absorb `wt_1` failures by immediately scheduling a retry. Model this as a retry-on-failure policy for `wt_1` with a maximum retry count of 3 (based on WF_104_8 pattern).

## 9. Data Quality Flags

| Flag | Status | Detail |
|---|---|---|
| Low sample size for failure rates | ⚠️ | Most failure rates based on 1–4 events; treat as point estimates, not precise probabilities |
| Retry delay distribution | ⚠️ | Only 3 observations; do not fit distribution |
| Truncated cases | ⚠️ | 5 cases (WF_102_17, WF_104_9, WF_104_7, WF_103_14, WF_1106_9) are incomplete — may affect workflow-level statistics |
| No batch/quantity data | ℹ️ | System operates in unit-flow mode; no batch size parameters to extract |

---

*Report generated from `eventlog_cleaned.parquet` (1,383 events, 461 entities, 38 cases, 9 workflow types, 9 failure events).*
