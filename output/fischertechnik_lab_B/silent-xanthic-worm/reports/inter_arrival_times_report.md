# Inter-Arrival Times Report — Fischertechnik Lab B

## 1. Methodology

| Property | Value |
|---|---|
| Data source | `eventlog_cleaned.parquet` (1,383 events, 461 entities, 38 cases) |
| Case identifier | `case` column (38 unique workflow instances) |
| Arrival time definition | Earliest `time:timestamp` per case (minimum across all events in that case) |
| Scope | All 38 cases, including 3 failure-only truncated cases (WF_102_17, WF_104_9, WF_104_7) |
| Outlier detection | IQR method with k = 1.5 (Tukey fences) |
| Time unit | Seconds |

**Rationale:** Each case represents a workpiece entering the system. The arrival time is the timestamp of the first event (`scheduled` transition) for that case. All 38 cases are included because even the 3 failure-only cases represent real system inputs — a workpiece was scheduled and attempted processing.

---

## 2. Global Inter-Arrival Times (All 38 Cases)

### 2.1 Raw Statistics (37 IATs)

| Statistic | Value |
|---|---|
| Count | 37 inter-arrival intervals |
| Mean | 140.25 s |
| Std Dev | 280.42 s |
| Min | 0.56 s |
| Max | 1,336.65 s |
| Median | 3.19 s |
| **CV** | **1.999** |

### 2.2 Outlier Detection (IQR Method)

| Parameter | Value |
|---|---|
| Q1 (25th percentile) | 1.11 s |
| Q3 (75th percentile) | 193.35 s |
| IQR | 192.24 s |
| Lower bound (Q1 − 1.5×IQR) | −287.25 s (clamped to 0) |
| Upper bound (Q3 + 1.5×IQR) | 481.72 s |
| **Outliers detected** | **3** |
| Outlier rate | 8.11% |
| Outlier values | 858.66 s, 1,336.65 s, 524.73 s |

The 3 outliers correspond to **between-batch gaps** — long idle periods between groups of cases that arrived in rapid succession.

### 2.3 Clean Statistics (34 IATs, Outliers Removed)

| Statistic | Value |
|---|---|
| Count | 34 inter-arrival intervals |
| Mean | 72.63 s |
| Std Dev | 132.58 s |
| Min | 0.56 s |
| Max | 478.22 s |
| Median | 2.86 s |
| **CV** | **1.825** |

---

## 3. Batch Arrival Structure

The arrival pattern exhibits a clear **batch structure**: cases arrive in rapid groups separated by long idle periods.

### 3.1 Batch Identification

Using a 60-second gap threshold, 13 distinct batches are identified:

| Batch | Cases | Size | Time Span (s) | Within-Batch IAT Range |
|---|---|---|---|---|
| 0 | WF_101_13, WF_102_14, WF_103_14, WF_104_7 | 4 | 3.8 | 1.11–1.37 |
| 1 | WF_101_14, WF_102_15, WF_103_15, WF_104_8, WF_105_8, WF_1106_6, WF_108_7, WF_109_5, WF_1107_6 | 9 | 13.1 | 0.56–6.70 |
| 2 | WF_102_16, WF_101_15, WF_104_9, WF_103_16 | 4 | 5.5 | 1.51–2.33 |
| 3 | WF_104_10, WF_105_9, WF_1106_7, WF_108_8, WF_109_6 | 5 | 21.9 | 0.65–9.87 |
| 4 | WF_102_17 | 1 | 0 | — |
| 5 | WF_101_16 | 1 | 0 | — |
| 6 | WF_103_17 | 1 | 0 | — |
| 7 | WF_102_18 | 1 | 0 | — |
| 8 | WF_109_7, WF_1107_7, WF_1106_8, WF_105_10, WF_101_17, WF_104_11, WF_108_9 | 7 | 43.0 | 0.62–32.27 |
| 9 | WF_103_18 | 1 | 0 | — |
| 10 | WF_109_8 | 1 | 0 | — |
| 11 | WF_101_18, WF_105_11 | 2 | 3.2 | 3.19 |
| 12 | WF_1106_9 | 1 | 0 | — |

### 3.2 Within-Batch vs. Between-Batch IATs

| Metric | Within-Batch (25 IATs) | Between-Batch (12 IATs) |
|---|---|---|
| Mean | 3.64 s | 424.87 s |
| Std Dev | 6.40 s | 355.62 s |
| Min | 0.56 s | 61.95 s |
| Max | 32.27 s | 1,336.65 s |
| Median | 1.51 s | 296.73 s |
| CV | 1.761 | 0.837 |

**Key observation:** Within-batch IATs are very short (mean 3.6 s), indicating cases are released in rapid succession. Between-batch IATs are much longer (mean 424.9 s ≈ 7 minutes), representing idle periods between production runs.

### 3.3 Batch Size Distribution

| Batch Size | Count | Proportion |
|---|---|---|
| 1 | 7 | 53.8% |
| 2 | 1 | 7.7% |
| 4 | 2 | 15.4% |
| 5 | 1 | 7.7% |
| 7 | 1 | 7.7% |
| 9 | 1 | 7.7% |
| **Mean** | **2.9** | |

---

## 4. Per-Workflow-Type Inter-Arrival Times

Computed by grouping cases by `process_model_id` and measuring IATs between consecutive cases of the same type.

| Workflow | Cases | IATs | Mean (s) | Std (s) | Min (s) | Max (s) | Median (s) | CV |
|---|---|---|---|---|---|---|---|---|
| WF_101 | 6 | 5 | 977.4 | 224.5 | 759.1 | 1,203.4 | 907.1 | 0.230 |
| WF_102 | 5 | 4 | 850.1 | 356.2 | 567.5 | 1,348.9 | 742.1 | 0.419 |
| WF_103 | 5 | 4 | 1,065.4 | 207.9 | 861.8 | 1,353.5 | 1,023.2 | 0.195 |
| WF_104 | 5 | 4 | 983.5 | 396.2 | 479.7 | 1,351.4 | 1,051.5 | 0.403 |
| WF_105 | 4 | 3 | 1,341.5 | 449.6 | 957.9 | 1,836.3 | 1,230.3 | 0.335 |
| WF_108 | 3 | 2 | 1,551.0 | 408.4 | 1,262.2 | 1,839.8 | 1,551.0 | 0.263 |
| WF_109 | 4 | 3 | 1,198.3 | 656.0 | 537.1 | 1,848.9 | 1,208.9 | 0.547 |
| WF_1106 | 4 | 3 | 1,441.0 | 342.5 | 1,229.0 | 1,836.2 | 1,257.9 | 0.238 |
| WF_1107 | 2 | 1 | 3,055.3 | — | 3,055.3 | 3,055.3 | 3,055.3 | — |

**Notes:**
- Per-type IATs are much larger than global IATs because cases of the same type are spread across different batches.
- WF_1107 has only 2 cases (1 IAT), so statistics are not meaningful.
- All per-type CVs are < 0.55, suggesting relatively regular spacing within each workflow type.

---

## 5. CV Analysis and Distribution Implications

| Metric | CV | Interpretation |
|---|---|---|
| Global IAT (raw, 37 values) | 1.999 | **Highly bursty** — not Poisson |
| Global IAT (clean, 34 values) | 1.825 | **Bursty** — not Poisson |
| Within-batch IAT (25 values) | 1.761 | **Bursty** — rapid but variable release |
| Between-batch IAT (12 values) | 0.837 | **Sub-Poisson** — somewhat regular |
| Per-type IATs | 0.195–0.547 | **Regular** — near-deterministic spacing |

### 5.1 Key Findings

1. **CV >> 1 for global IATs:** The global CV of ~2.0 strongly indicates a **non-Poisson, bursty arrival process**. Cases arrive in clusters (batches) rather than independently.

2. **Two-phase arrival process:** The data is best modeled as a **batch arrival process** with:
   - **Batch inter-arrival times:** Mean ≈ 425 s, CV ≈ 0.84 (between-batch gaps)
   - **Batch sizes:** Mean ≈ 2.9 cases per batch, ranging from 1 to 9
   - **Within-batch release times:** Mean ≈ 3.6 s between consecutive cases in a batch

3. **Per-type regularity:** Within each workflow type, arrivals are relatively regular (CV < 0.55), suggesting a production schedule or planned release pattern.

4. **Sample size caveat:** With only 37 global IATs and as few as 2–5 per workflow type, distribution fitting should be done with caution. The small sample limits statistical power for goodness-of-fit tests.

### 5.2 Simulation Modeling Recommendations

For DES simulation, consider one of these approaches:

- **Option A — Batch arrival generator:** Model arrivals as batches with random batch size (mean ~3) and random inter-batch delay (mean ~425 s). Within each batch, release cases with short delays (mean ~3.6 s).
- **Option B — Two-phase Poisson:** Use a compound process with a Poisson batch arrival rate (λ ≈ 1/425 s⁻¹) and a geometric or Poisson batch size distribution.
- **Option C — Empirical:** Use the observed 37 IAT values directly in a discrete-event simulation with empirical sampling.

**Do not use a simple Poisson arrival process** — the CV of ~2.0 would be severely misrepresented by an exponential inter-arrival distribution (CV = 1.0).

---

## 6. Data Quality Flags

| Flag | Status | Detail |
|---|---|---|
| Sample size (global) | ⚠️ Small | 37 IATs — distribution fitting has low power |
| Sample size (per-type) | ⚠️ Very small | 1–5 IATs per workflow type |
| CV > 1 (global) | ✅ Expected | CV = 1.999 — bursty arrivals confirmed |
| Outlier rate | ⚠️ Elevated | 8.11% (3/37) — reflects batch structure, not data errors |
| WF_1107 | ⚠️ Insufficient | Only 2 cases, 1 IAT — cannot compute meaningful statistics |

---

*Report generated from `eventlog_cleaned.parquet` (1,383 events, 461 entities, 38 cases, 9 workflow types). All 38 cases included, including 3 failure-only truncated cases.*
