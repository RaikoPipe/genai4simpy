# Quantities & Quality Report — Fischertechnik Manufacturing System

## 1. Dataset Summary

| Property | Value |
|---|---|
| Source file | `eventlog_cleaned.parquet` |
| Total events | 576 (192 operations × 3 lifecycle events) |
| Operations (complete events) | 192 |
| Product variants | 9 |
| Case instances | 18 (4 incomplete due to time-window truncation) |
| Successful operations | 184 (95.8%) |
| Failed operations | 8 (4.2%) |
| Failure codes | 7 × HTTP 418, 1 × HTTP 401 |

---

## 2. Process Quantities

### 2.1 Workpiece Counts Per Case

| Case | Variant | Operations | Status |
|---|---|---|---|
| WF_104_20 | WF_104 | 16 | Complete |
| WF_101_30 | WF_101 | 15 | Complete |
| WF_103_29 | WF_103 | 15 | Complete |
| WF_103_30 | WF_103 | 15 | Complete |
| WF_109_15 | WF_109 | 15 | Complete |
| WF_1106_22 | WF_1106 | 14 | Complete |
| WF_108_17 | WF_108 | 13 | Complete |
| WF_1107_16 | WF_1107 | 13 | Complete |
| WF_102_31 | WF_102 | 13 | Complete |
| WF_101_31 | WF_101 | 12 | Complete |
| WF_105_21 | WF_105 | 12 | Complete |
| WF_1106_21 | WF_1106 | 10 | Complete |
| WF_102_32 | WF_102 | 10 | Complete |
| WF_105_22 | WF_105 | 10 | Complete |
| WF_104_21 | WF_104 | 4 | Incomplete (truncated) |
| WF_1107_17 | WF_1107 | 3 | Incomplete (truncated) |
| WF_109_16 | WF_109 | 1 | Incomplete (truncated) |
| WF_108_18 | WF_108 | 1 | Failed at first step (HTTP 401) |

### 2.2 Operations Per Variant

| Variant | Total Ops | Cases | Complete Cases | Avg Ops/Case |
|---|---|---|---|---|
| WF_103 | 30 | 2 | 2 | 15.0 |
| WF_101 | 27 | 2 | 2 | 13.5 |
| WF_1106 | 24 | 2 | 2 | 12.0 |
| WF_102 | 23 | 2 | 2 | 11.5 |
| WF_105 | 22 | 2 | 2 | 11.0 |
| WF_104 | 20 | 2 | 1 | 10.0 |
| WF_109 | 16 | 2 | 1 | 8.0 |
| WF_1107 | 16 | 2 | 1 | 8.0 |
| WF_108 | 14 | 2 | 1 | 7.0 |

### 2.3 Batch Quantities (Drill/Punch Operations)

The `quantity` parameter is present on drill and punch activities. All values are **deterministic per variant-activity pair** (zero standard deviation within each group).

| Activity | Variant | Quantity | Interpretation |
|---|---|---|---|
| `/mm/drill` | WF_102 | 6 | 6 holes drilled |
| `/mm/drill` | WF_108 | 4 | 4 holes drilled |
| `/mm/drill` | WF_1107 | 6 | 6 holes drilled |
| `/pm/punch_recesses` | WF_103 | 6 | 6 recesses punched |
| `/pm/punch_gill` | WF_104 | 8 | 8 gills punched |
| `/pm/punch_ribbing` | WF_109 | 6 | 6 ribbing punches |
| `/pm/punch_ribbing` | WF_1107 | 10 | 10 ribbing punches |
| `/dm/cylindrical_drill` | WF_1106 | 4 | 4 cylindrical drills |

**Observation:** Quantities are deterministic per variant-activity pair. No stochasticity observed. Model as fixed parameters in simulation.

### 2.4 Burn Workpiece Size (Context-Dependent)

The `burn_workpiece_size` parameter has **dual semantics** depending on the activity context:

#### At `/ov/burn` — Categorical (Deterministic Per Variant)

| Variant | Size | Thickness |
|---|---|---|
| WF_101 | regular | thin |
| WF_102 | middle | thin |
| WF_103 | large | thin |
| WF_104 | maxi | thin |
| WF_105 | regular | thick |
| WF_108 | maxi | thick |
| WF_109 | regular | thin |
| WF_1106 | middle | thick |
| WF_1107 | large | thick |

**Observation:** Each variant has a fixed burn size and thickness. Model as a variant lookup table, not a stochastic parameter.

#### At `/mm/drill` — Numeric (Drill Diameter in mm)

| Variant | Drill Size |
|---|---|
| WF_102 | 30 mm |
| WF_108 | 30 mm |
| WF_1107 | 40 mm |

#### At `/dm/cylindrical_drill` — Numeric

| Variant | Drill Size |
|---|---|
| WF_1106 | 50–60 mm (varies across lifecycle events) |

**Note:** WF_1106 shows both 50 and 60 for `burn_workpiece_size` at the cylindrical drill activity, suggesting this parameter may encode multiple drill passes or sizes within a single operation.

### 2.5 Sorting Machine Ejection Position

| Position | Count | Percentage |
|---|---|---|
| 1 | 6 | 33.3% |
| 2 | 6 | 33.3% |
| 3 | 6 | 33.3% |

**Distribution:** Discrete uniform over {1, 2, 3}. Model as `np.random.choice([1, 2, 3])` at each sort operation.

---

## 3. Quality Metrics

### 3.1 Overall Quality Summary

| Metric | Value |
|---|---|
| Total operations | 192 |
| Successful (HTTP 200) | 184 |
| Failed (HTTP 418/401) | 8 |
| Overall success rate | **95.8%** |
| Overall failure rate | **4.2%** |

### 3.2 Failure Rate By Activity

| Activity | Total Attempts | Failures | Failure Rate | HTTP 418 | HTTP 401 |
|---|---|---|---|---|---|
| `/vgr/pick_up_and_transport` | 55 | 5 | **9.1%** | 5 | 0 |
| `/hbw/store_empty_bucket` | 15 | 2 | **13.3%** | 2 | 0 |
| `/hbw/unload` | 17 | 1 | **5.9%** | 0 | 1 |
| All other activities | 105 | 0 | 0.0% | 0 | 0 |

**Observation:** Failures are concentrated in three activities. All other 17 activity types had zero failures.

### 3.3 Failure Rate By Resource

| Resource | Total Attempts | Failures | Failure Rate |
|---|---|---|---|
| `vgr_1` | 37 | 5 | **13.5%** |
| `hbw_2` | 32 | 3 | **9.4%** |
| All other resources | 123 | 0 | 0.0% |

**Observation:** All 8 failures occurred on just two resources: `vgr_1` (5 failures, all HTTP 418) and `hbw_2` (3 failures: 2 × HTTP 418, 1 × HTTP 401).

### 3.4 Success Rate By Variant

| Variant | Total Ops | Success | Failure | Success Rate |
|---|---|---|---|---|
| WF_101 | 27 | 27 | 0 | 100.0% |
| WF_102 | 23 | 23 | 0 | 100.0% |
| WF_1107 | 16 | 16 | 0 | 100.0% |
| WF_1106 | 24 | 23 | 1 | 95.8% |
| WF_104 | 20 | 19 | 1 | 95.0% |
| WF_105 | 22 | 21 | 1 | 95.5% |
| WF_109 | 16 | 15 | 1 | 93.8% |
| WF_108 | 14 | 13 | 1 | 92.9% |
| WF_103 | 30 | 27 | 3 | 90.0% |

### 3.5 Individual Failure Events

| Event ID | Case | Activity | Resource | HTTP Code | Description |
|---|---|---|---|---|---|
| 2473 | WF_103_29 | `/hbw/store_empty_bucket` | hbw_2 | 418 | Precondition failed |
| 2513 | WF_103_29 | `/vgr/pick_up_and_transport` | vgr_1 | 418 | Precondition failed |
| 2536 | WF_104_20 | `/vgr/pick_up_and_transport` | vgr_1 | 418 | Precondition failed |
| 2541 | WF_1106_21 | `/vgr/pick_up_and_transport` | vgr_1 | 418 | Precondition failed |
| 2575 | WF_105_22 | `/hbw/store_empty_bucket` | hbw_2 | 418 | Precondition failed |
| 2587 | WF_109_15 | `/vgr/pick_up_and_transport` | vgr_1 | 418 | Precondition failed |
| 2604 | WF_103_30 | `/vgr/pick_up_and_transport` | vgr_1 | 418 | Precondition failed |
| 2645 | WF_108_18 | `/hbw/unload` | hbw_2 | 401 | Authentication failed |

**Retry behavior:** All 7 HTTP 418 failures were followed by successful retries — the workpiece continued its route. The single HTTP 401 failure (event 2645) caused case WF_108_18 to be truncated (only 1 operation recorded).

### 3.6 Failure Modeling Recommendation

Treat HTTP 418 and 401 as a **unified retry mechanism**:
- **System-wide failure rate:** 8/192 = 4.2%
- **Per-activity failure rates** (where observed):
  - `/vgr/pick_up_and_transport`: 5/55 = 9.1%
  - `/hbw/store_empty_bucket`: 2/15 = 13.3%
  - `/hbw/unload`: 1/17 = 5.9%
  - All others: 0% (insufficient evidence to claim zero risk)

**Caution:** With only 8 failures across 192 operations, per-activity failure rates have wide confidence intervals. Consider modeling a single system-wide failure rate (~4%) with retry, rather than per-activity rates.

---

## 4. Outlier Detection Results

### 4.1 Response Status Code Outliers (IQR Method)

The IQR-based outlier detection on `response_status_code` (grouped by activity × resource) identified outliers corresponding to the 8 failure events:

| Activity × Resource | Count | Outliers | Outlier Rate |
|---|---|---|---|
| `/vgr/pick_up_and_transport` × `vgr_1` | 37 | 5 | **13.5%** ⚠️ |
| `/hbw/store_empty_bucket` × `hbw_2` | 15 | 2 | **13.3%** ⚠️ |
| `/hbw/unload` × `hbw_2` | 17 | 1 | **5.9%** ⚠️ |
| All other groups | — | 0 | 0.0% |

⚠️ Groups with outlier_rate > 5% are flagged. These correspond to the known failure events and are expected (not data quality issues).

### 4.2 Quantity Parameter Outliers

No outliers detected — all quantity values are deterministic per variant-activity pair (zero variance within groups).

---

## 5. Variant Parameter Lookup Table

This table consolidates all deterministic process parameters for simulation input:

| Variant | Burn Size | Burn Thickness | Drill Qty | Drill Size | Punch Type | Punch Qty | CylDrill Qty |
|---|---|---|---|---|---|---|---|
| WF_101 | regular | thin | — | — | — | — | — |
| WF_102 | middle | thin | 6 | 30 mm | — | — | — |
| WF_103 | large | thin | — | — | recesses | 6 | — |
| WF_104 | maxi | thin | — | — | gill | 8 | — |
| WF_105 | regular | thick | — | — | — | — | — |
| WF_108 | maxi | thick | 4 | 30 mm | — | — | — |
| WF_109 | regular | thin | — | — | ribbing | 6 | — |
| WF_1106 | middle | thick | — | — | — | — | 4 |
| WF_1107 | large | thick | 6 | 40 mm | ribbing | 10 | — |

---

## 6. Data Quality Flags

| Flag | Status | Details |
|---|---|---|
| Sample size | ⚠️ Low | Only 192 operations across 20 activities; many groups have < 10 observations |
| Failure sample | ⚠️ Low | Only 8 failures; per-activity rates have wide confidence intervals |
| Incomplete cases | ⚠️ Present | 4 cases truncated (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) |
| Quantity variability | ✅ None | All quantities deterministic per variant-activity pair |
| Burn parameters | ✅ Deterministic | Fixed per variant; no stochasticity |
| Ejection position | ✅ Uniform | Perfect uniform distribution over {1, 2, 3} |
| Failure retry | ✅ Consistent | All HTTP 418 failures followed by successful retry |

---

## 7. Simulation Modeling Recommendations

1. **Quantities:** Model as fixed parameters per variant-activity pair (no stochasticity needed).
2. **Burn parameters:** Use the variant lookup table (Section 5) as a deterministic mapping.
3. **Sorting ejection:** Sample from discrete uniform {1, 2, 3}.
4. **Failure/retry:** Model as a system-wide Bernoulli trial with p ≈ 0.04 per operation attempt. On failure, retry once (all observed failures resolved on first retry).
5. **Per-activity failure rates:** Not recommended due to insufficient sample size (8 failures total). Use system-wide rate instead.
6. **Incomplete cases:** Exclude WF_104_21, WF_108_18, WF_109_16, WF_1107_17 from parameter estimation to avoid bias.
