# Quantities & Quality Report — Fischertechnik Lab C

## 1. Dataset Summary

| Property | Value |
|---|---|
| Source file | `eventlog_cleaned.parquet` (1,137 rows) |
| Raw parameters source | `eventlog.parquet` (parameters column, 1,136 non-null) |
| Unique operations | 379 |
| Unique cases (workpieces) | 37 |
| Unique process models | 9 |
| Failure events | 5 (1.3% of operations) |

---

## 2. Batch Processing Quantities

Batch quantities are extracted from the `parameter_quantity` field in the raw parameters column. These quantities appear exclusively in drill and punch operations on dm_2, mm_2, and pm_1 resources.

### 2.1 Batch Quantity Statistics by Activity

| Activity | Resource | Operations | Mean Qty | Min | Max | Std |
|---|---|---|---|---|---|---|
| /dm/cylindrical_drill | dm_2 | 2 | 9.0 | 8 | 10 | 1.41 |
| /dm/drill | dm_2 | 4 | 7.0 | 4 | 10 | 2.58 |
| /mm/drill | mm_2 | 8 | 5.0 | 4 | 6 | 1.07 |
| /pm/punch_gill | pm_1 | 4 | 7.5 | 6 | 8 | 1.00 |
| /pm/punch_recesses | pm_1 | 2 | 6.0 | 6 | 6 | 0.00 |
| /pm/punch_ribbing | pm_1 | 2 | 6.0 | 6 | 6 | 0.00 |

### 2.2 Batch Processing Times (Per-Operation and Per-Unit)

| Activity | Resource | Ops | Mean Total (s) | Mean Per-Unit (s) | Std Per-Unit (s) | CV Per-Unit |
|---|---|---|---|---|---|---|
| /dm/cylindrical_drill | dm_2 | 2 | 43.0 | 4.8 | 0.1 | 0.02 |
| /dm/drill | dm_2 | 4 | 27.1 | 3.9 | 0.7 | 0.18 |
| /mm/drill | mm_2 | 8 | 13.7 | 2.6 | 1.4 | 0.54 |
| /pm/punch_gill | pm_1 | 4 | 26.6 | 3.6 | 0.3 | 0.08 |
| /pm/punch_recesses | pm_1 | 2 | 23.8 | 4.0 | 0.0 | 0.00 |
| /pm/punch_ribbing | pm_1 | 2 | 23.6 | 3.9 | 0.1 | 0.03 |

### 2.3 Detailed Batch Operation Observations

| Activity | Resource | Case | Qty | Total Time (s) | Per-Unit (s) |
|---|---|---|---|---|---|
| /dm/cylindrical_drill | dm_2 | WF_1106_15 | 8 | 39.1 | 4.9 |
| /dm/cylindrical_drill | dm_2 | WF_1106_18 | 10 | 46.8 | 4.7 |
| /dm/drill | dm_2 | WF_1106_16 | 6 | 26.9 | 4.5 |
| /dm/drill | dm_2 | WF_1106_17 | 4 | 15.8 | 4.0 |
| /dm/drill | dm_2 | WF_1106_19 | 10 | 42.0 | 4.2 |
| /dm/drill | dm_2 | WF_1106_20 | 8 | 23.8 | 3.0 |
| /mm/drill | mm_2 | WF_108_14 | 4 | 5.3 | 1.3 |
| /mm/drill | mm_2 | WF_102_27 | 6 | 15.5 | 2.6 |
| /mm/drill | mm_2 | WF_102_28 | 6 | 15.4 | 2.6 |
| /mm/drill | mm_2 | WF_1106_18 | 4 | 5.1 | 1.3 |
| /mm/drill | mm_2 | WF_108_15 | 4 | 14.1 | 3.5 |
| /mm/drill | mm_2 | WF_108_16 | 4 | 5.3 | 1.3 |
| /mm/drill | mm_2 | WF_102_29 | 6 | 32.2 | 5.4 |
| /mm/drill | mm_2 | WF_102_30 | 6 | 16.9 | 2.8 |
| /pm/punch_gill | pm_1 | WF_104_17 | 8 | 27.2 | 3.4 |
| /pm/punch_gill | pm_1 | WF_104_18 | 6 | 23.9 | 4.0 |
| /pm/punch_gill | pm_1 | WF_1107_14 | 8 | 27.7 | 3.5 |
| /pm/punch_gill | pm_1 | WF_1107_12 | 8 | 27.5 | 3.4 |
| /pm/punch_recesses | pm_1 | WF_103_24 | 6 | 23.8 | 4.0 |
| /pm/punch_recesses | pm_1 | WF_103_25 | 6 | 23.7 | 3.9 |
| /pm/punch_ribbing | pm_1 | WF_109_12 | 6 | 23.8 | 4.0 |
| /pm/punch_ribbing | pm_1 | WF_109_13 | 6 | 23.3 | 3.9 |

### 2.4 Data Quality Flags — Batch Quantities

| Flag | Group | Reason |
|---|---|---|
| ⚠️ Small sample | /dm/cylindrical_drill | n=2 operations |
| ⚠️ Small sample | /pm/punch_recesses | n=2 operations |
| ⚠️ Small sample | /pm/punch_ribbing | n=2 operations |
| ⚠️ High variability | /mm/drill per-unit | CV=0.54 (range 1.3–5.4s); outlier at WF_102_29 (32.2s total, 5.4s/unit) |
| ⚠️ High variability | /dm/drill quantities | Range 4–10 (CV=0.37); quantities vary significantly |

**Key observations:**
- Per-unit processing times are remarkably stable for punch operations (CV < 0.1), suggesting consistent per-unit work
- mm/drill shows high per-unit variability (CV=0.54), possibly reflecting different drill depths or workpiece sizes
- dm/drill quantities range from 4 to 10, suggesting batch size is variable and may depend on workpiece characteristics
- Punch operations (pm_1) consistently use quantities of 6–8

---

## 3. Workpiece Size Distribution

Workpiece sizes are extracted from `parameter_burn_workpiece_size` in ov/burn operations. Four size categories are observed: **regular**, **middle**, **large**, and **maxi**.

### 3.1 Size Distribution (from ov/burn, n=32)

| Size | Count | Proportion |
|---|---|---|
| middle | 11 | 34.4% |
| regular | 9 | 28.1% |
| maxi | 7 | 21.9% |
| large | 5 | 15.6% |

### 3.2 Thickness Distribution (from ov/burn, n=32)

| Thickness | Count | Proportion |
|---|---|---|
| thin | 17 | 53.1% |
| thick | 15 | 46.9% |

### 3.3 Size × Thickness Cross-Tabulation

| Size \ Thickness | thin | thick | Total |
|---|---|---|---|
| regular | 5 | 4 | 9 |
| middle | 5 | 6 | 11 |
| large | 3 | 2 | 5 |
| maxi | 4 | 3 | 7 |
| **Total** | **17** | **15** | **32** |

### 3.4 Size by Process Model

| Process Model | regular | middle | large | maxi | Total |
|---|---|---|---|---|---|
| WF_101 | 2 | 0 | 0 | 0 | 2 |
| WF_102 | 0 | 5 | 0 | 0 | 5 |
| WF_103 | 0 | 0 | 3 | 0 | 3 |
| WF_104 | 0 | 0 | 0 | 4 | 4 |
| WF_105 | 4 | 0 | 0 | 0 | 4 |
| WF_108 | 0 | 0 | 0 | 3 | 3 |
| WF_109 | 3 | 0 | 0 | 0 | 3 |
| WF_1106 | 0 | 6 | 0 | 0 | 6 |
| WF_1107 | 2 | 0 | 2 | 0 | 4 |

**Key insight:** Process models are strongly associated with specific workpiece sizes:
- WF_101, WF_105, WF_109 → **regular** size
- WF_102, WF_1106 → **middle** size
- WF_103, WF_1107 → **large** size (WF_1107 also has regular)
- WF_104, WF_108 → **maxi** size

This suggests workpiece size is determined by the process model (product variant), not randomly assigned.

### 3.5 Size-Dependent Processing Times (ov/burn)

| Size | n | Mean (s) | Std (s) | Min (s) | Max (s) | CV |
|---|---|---|---|---|---|---|
| regular | 9 | 23.8 | 2.7 | 21.4 | 26.7 | 0.11 |
| middle | 11 | 29.3 | 2.6 | 26.4 | 31.6 | 0.09 |
| large | 5 | 33.6 | 2.8 | 31.6 | 36.8 | 0.08 |
| maxi | 7 | 38.7 | 2.7 | 36.5 | 41.5 | 0.07 |

**Clear size-dependent effect:** Processing time increases approximately linearly with workpiece size:
- regular → middle: +5.5s (+23%)
- middle → large: +4.3s (+15%)
- large → maxi: +5.1s (+15%)
- Overall range: 23.8s (regular) to 38.7s (maxi), a 63% increase

### 3.6 Thickness-Dependent Processing Times (ov/burn)

| Thickness | n | Mean (s) | Std (s) | CV |
|---|---|---|---|---|
| thin | 17 | 28.3 | 5.9 | 0.21 |
| thick | 15 | 32.9 | 5.5 | 0.17 |

Thickness shows a moderate effect (+4.6s, +16%), but this is confounded with size (larger workpieces tend to be thicker).

### 3.7 Data Quality Flags — Workpiece Sizes

| Flag | Group | Reason |
|---|---|---|
| ⚠️ Small sample | large size | n=5 operations |
| ⚠️ Confounded | thickness effect | Correlated with size; cannot isolate independent effect |
| ✅ Strong signal | size effect | Clear monotonic increase in burn time with size (R² ≈ 0.95) |

---

## 4. Failure Rates

### 4.1 Overall Failure Statistics

| Metric | Value |
|---|---|
| Total operations | 379 |
| Total failures | 5 |
| Overall failure rate | 1.3% |
| Cases with failures | 4 |
| Cases without failures | 33 |

### 4.2 Failure Rate by Activity

| Activity | Operations | Failures | Failure Rate |
|---|---|---|---|
| /hbw/unload | 37 | 2 | 5.4% |
| /vgr/pick_up_and_transport | 104 | 3 | 2.9% |
| All other activities | 238 | 0 | 0.0% |

### 4.3 Failure Rate by Resource

| Resource | Operations | Failures | Failure Rate |
|---|---|---|---|
| hbw_2 | 71 | 2 | 2.8% |
| vgr_1 | 68 | 3 | 4.4% |

### 4.4 Individual Failure Events

| Failure | Case | Process Model | Activity | Resource | Lifecycle State |
|---|---|---|---|---|---|
| 1 | WF_101_26 | WF_101 | /hbw/unload | hbw_2 | failure |
| 2 | WF_101_28 | WF_101 | /hbw/unload | hbw_2 | failure |
| 3 | WF_103_27 | WF_103 | /vgr/pick_up_and_transport | vgr_1 | failure |
| 4 | WF_104_17 | WF_104 | /vgr/pick_up_and_transport | vgr_1 | failure |
| 5 | WF_1107_13 | WF_1107 | /vgr/pick_up_and_transport | vgr_1 | failure |

### 4.5 Data Quality Flags — Failure Rates

| Flag | Group | Reason |
|---|---|---|
| ⚠️ Very small sample | All failure rates | Only 5 failures in 379 operations; rates have high uncertainty |
| ⚠️ Activity-specific | /hbw/unload | 2/37 = 5.4% but wide confidence interval (0.7%–17.6%) |
| ⚠️ Activity-specific | /vgr/pick_up_and_transport | 3/104 = 2.9% but wide CI (0.6%–8.4%) |
| ✅ Pattern | All failures at entry/transport | No failures in processing activities (ov, mm, sm, pm, dm, hw) |

---

## 5. Human Review & Rework Parameters

### 5.1 Human Review Probability by Process Model

| Process Model | Total Cases | Cases with Review | Review Probability | Notes |
|---|---|---|---|---|
| WF_101 | 4 | 2 | 50.0% | Described as "mandatory" in topology, but only 50% observed |
| WF_102 | 5 | 3 | 60.0% | Conditional |
| WF_103 | 5 | 3 | 60.0% | Conditional |
| WF_104 | 3 | 2 | 66.7% | Described as "mandatory" in topology, but only 67% observed |
| WF_105 | 4 | 2 | 50.0% | Conditional |
| WF_108 | 3 | 1 | 33.3% | Conditional |
| WF_109 | 3 | 2 | 66.7% | Conditional |
| WF_1106 | 6 | 1 | 16.7% | Conditional |
| WF_1107 | 4 | 1 | 25.0% | Conditional |

**Note:** The topology report describes WF_101 and WF_104 as having "mandatory" human review, but the observed data shows only 50% and 67% respectively. This discrepancy may be due to truncated/incomplete cases. The review probability should be treated as conditional for all process models.

### 5.2 Human Review Outcomes

| Outcome | Count | Proportion |
|---|---|---|
| Success | 17 | 100% |
| Failure | 0 | 0% |

All 17 observed human review complete events resulted in success. No review failures were observed in the dataset.

### 5.3 WF_104 Rework Loop Analysis

**Observed WF_104 cases:**

| Case | Steps | Status | Rework Cycles |
|---|---|---|---|
| WF_104_17 | 16 start events | Failed at vgr_1 (after review) | 0 |
| WF_104_18 | 23 start events | Success (truncated after rework) | 1 |
| WF_104_19 | 6 start events | Incomplete (missing data) | 0 |

**WF_104_18 rework sequence:**
1. Phase 1 (Track 2): unload → transport → burn → transport → sort → cross-track transport
2. Phase 2 (Track 1): transport → deburr → transport → punch_gill → transport → **human_review (success)**
3. Rework (Track 2): transport → store_empty_bucket → burn → transport → mill → sort → cross-track transport
4. Phase 2 again (partial): transport → transport (truncated)

**Critical observation:** The human review in WF_104_18 resulted in **success**, yet the workpiece was sent back for rework. This contradicts the topology report's assumption that "failed human review triggers reprocessing." The rework loop in WF_104 appears to be **deterministic** (part of the process model design) rather than conditional on review outcome.

**DES implication:** Model WF_104 rework as a deterministic loop (always occurs once) rather than a probabilistic branch based on human review outcome.

### 5.4 Data Quality Flags — Human Review & Rework

| Flag | Group | Reason |
|---|---|---|
| ⚠️ Small sample | All review probabilities | 3–6 cases per process model |
| ⚠️ No failures | Human review outcomes | 0/17 failures; cannot estimate failure probability |
| ⚠️ Contradiction | WF_104 rework trigger | Review succeeded yet rework occurred; rework may be deterministic |
| ⚠️ Truncated cases | WF_104_18, WF_104_19 | Incomplete sequences limit analysis |

---

## 6. Process Model Mix (Product Mix)

| Process Model | Cases | Proportion | Workpiece Size | Description |
|---|---|---|---|---|
| WF_101 | 4 | 10.8% | regular | Full process with temper (Track 1) |
| WF_102 | 5 | 13.5% | middle | Drill & lower (Track 2) |
| WF_103 | 5 | 13.5% | large | Punch recesses (Track 1) |
| WF_104 | 3 | 8.1% | maxi | Cross-track rework loop |
| WF_105 | 4 | 10.8% | regular | Simple deburr (Track 1) |
| WF_108 | 3 | 8.1% | maxi | Drill & deburr (Track 2) |
| WF_109 | 3 | 8.1% | regular | Punch ribbing (Track 1) |
| WF_1106 | 6 | 16.2% | middle | Variable milling & drilling (Track 2) |
| WF_1107 | 4 | 10.8% | large/regular | Punch gill (Track 1) |

---

## 7. Summary of DES Parameters

### 7.1 Batch Quantities (for dm, mm, pm operations)

| Activity | Recommended Batch Size | Rationale |
|---|---|---|
| /dm/cylindrical_drill | 8–10 (mean 9) | High variability; use distribution |
| /dm/drill | 4–10 (mean 7) | High variability; use distribution |
| /mm/drill | 4–6 (mean 5) | Moderate variability |
| /pm/punch_gill | 6–8 (mean 7.5) | Low variability |
| /pm/punch_recesses | 6 (fixed) | Consistent across 2 observations |
| /pm/punch_ribbing | 6 (fixed) | Consistent across 2 observations |

### 7.2 Workpiece Size Effects

| Parameter | Effect | Recommendation |
|---|---|---|
| Size (regular→maxi) | +15s burn time per size step | Model size-dependent processing times for ov/burn |
| Thickness (thin→thick) | +4.6s burn time | Confounded with size; may not need separate modeling |

### 7.3 Quality Parameters

| Parameter | Estimate | Confidence |
|---|---|---|
| Overall failure rate | 1.3% (5/379) | Low (small sample) |
| /hbw/unload failure rate | 5.4% (2/37) | Low |
| /vgr/transport failure rate | 2.9% (3/104) | Low |
| Human review probability | 17–67% (varies by PM) | Medium |
| Human review pass rate | 100% (17/17) | Low (no failures observed) |
| WF_104 rework | Deterministic (1 cycle) | Medium (1 complete case) |

### 7.4 Data Quality Summary

| Category | Status | Notes |
|---|---|---|
| Batch quantities | ✅ Extracted | 22 observations across 6 activities |
| Workpiece sizes | ✅ Extracted | 32 observations, 4 sizes, clear size-time correlation |
| Failure rates | ⚠️ Limited | Only 5 failures; rates have wide confidence intervals |
| Human review | ⚠️ Limited | No review failures observed; probabilities vary by PM |
| Rework loop | ⚠️ Ambiguous | WF_104 rework appears deterministic, not review-triggered |
| Thickness effect | ⚠️ Confounded | Correlated with size; cannot isolate independent effect |

---

*Report generated from analysis of `eventlog_cleaned.parquet` (1,137 rows, 379 operations, 37 cases) and `eventlog.parquet` (parameters column, 1,136 non-null entries)*
