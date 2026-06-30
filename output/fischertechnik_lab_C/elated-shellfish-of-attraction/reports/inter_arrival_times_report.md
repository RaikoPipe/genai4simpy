# Inter-Arrival Times Report — Fischertechnik Lab C

## 1. Dataset Characteristics

| Property | Value |
|---|---|
| Source file | `eventlog_cleaned.parquet` |
| Total cases (workpieces) | 37 |
| Unique process models | 9 (WF_101–WF_1107) |
| Observation window | 2021-07-01 18:48:23 – 20:05:59 UTC |
| Time span | 77.61 minutes |
| Arrival definition | Earliest `time:timestamp` per `case` (first `scheduled` event) |

## 2. Global Inter-Arrival Time Statistics

### 2.1 All Inter-Arrival Times (36 values)

| Statistic | Value |
|---|---|
| Mean | 2.1558 min (129.35 s) |
| Std Dev | 4.4060 min (264.36 s) |
| Min | 0.0085 min (0.51 s) |
| Max | 16.4879 min (989.28 s) |
| Median | 0.0273 min (1.64 s) |
| **CV** | **2.0438** |

### 2.2 IQR Outlier Detection

| Parameter | Value |
|---|---|
| Method | IQR (Tukey fences, k=1.5) |
| Q1 | 0.0156 min (0.94 s) |
| Q3 | 1.1736 min (70.42 s) |
| IQR | 1.1580 min (69.48 s) |
| Lower bound | -1.7214 min (clamped to 0) |
| Upper bound | 2.9105 min (174.63 s) |
| **Outliers detected** | **7 out of 36 (19.4%)** |

**Outlier values (all are inter-burst gaps > 1 min):**

| IAT (min) | IAT (s) | Between Cases |
|---|---|---|
| 16.488 | 989.3 | WF_109_12 → WF_1106_16 |
| 14.763 | 885.8 | WF_102_29 → WF_101_29 |
| 11.586 | 695.2 | WF_109_13 → WF_105_19 |
| 8.691 | 521.5 | WF_102_30 → WF_1106_20 |
| 8.211 | 492.7 | WF_105_18 → WF_102_28 |
| 6.947 | 416.8 | WF_1106_16 → WF_101_26 |
| 4.776 | 286.5 | WF_108_16 → WF_102_29 |

### 2.3 Clean Inter-Arrival Times (29 values, excluding 7 outliers)

| Statistic | Value |
|---|---|
| Mean | 0.2119 min (12.71 s) |
| Std Dev | 0.5135 min (30.81 s) |
| Min | 0.0085 min (0.51 s) |
| Max | 2.2461 min (134.77 s) |
| Median | 0.0209 min (1.25 s) |
| **CV** | **2.4232** |

## 3. Burst Structure Analysis

The arrival process exhibits a **strong burst pattern** rather than a steady Poisson stream. Cases arrive in tightly clustered groups separated by idle gaps.

### 3.1 Burst Clusters (11 bursts identified)

| Burst | Cases | Time Span | Duration | Models Present |
|---|---|---|---|---|
| 1 | 9 | 18:48:23 – 18:48:30 | 7.9 s | All 9 models |
| 2 | 1 | 19:05:00 | 0 s | WF_1106 |
| 3 | 5 | 19:11:57 – 19:12:00 | 3.6 s | WF_101, WF_102, WF_103, WF_104, WF_105 |
| 4 | 5 | 19:20:13 – 19:20:16 | 3.5 s | WF_102, WF_1106, WF_1107, WF_108, WF_109 |
| 5 | 2 | 19:31:52 – 19:31:53 | 1.4 s | WF_105, WF_103 |
| 6 | 2 | 19:34:08 – 19:34:09 | 1.3 s | WF_1106, WF_1107 |
| 7 | 2 | 19:35:14 – 19:35:16 | 2.6 s | WF_101, WF_108 |
| 8 | 1 | 19:40:02 | 0 s | WF_102 |
| 9 | 6 | 19:54:48 – 19:55:32 | 44.3 s | WF_101, WF_1106, WF_103, WF_104, WF_105, WF_109 |
| 10 | 1 | 19:56:58 | 0 s | WF_102 |
| 11 | 3 | 20:05:39 – 20:05:59 | 20.7 s | WF_1106, WF_103, WF_1107 |

### 3.2 Intra-Burst vs Inter-Burst Statistics

| Metric | Intra-Burst (26 IATs) | Inter-Burst (10 gaps) |
|---|---|---|
| Mean | 0.0530 min (3.18 s) | 7.62 min (457.2 s) |
| Std Dev | 0.1142 min (6.85 s) | — |
| Median | 0.0181 min (1.09 s) | — |
| CV | 2.1567 | — |
| Min | 0.0085 min (0.51 s) | 1.086 min (65.2 s) |
| Max | 0.5549 min (33.30 s) | 16.488 min (989.3 s) |

**Key observation:** Within bursts, cases arrive within seconds of each other (median 1.09 s). Between bursts, idle gaps average 7.6 minutes. This two-regime structure is characteristic of batch release or production scheduling, not a Poisson process.

## 4. Process Model Mix Proportions

The 9 process models are interleaved draws from a single global arrival stream. The observed mix proportions are:

| Process Model | Cases | Proportion | Percentage |
|---|---|---|---|
| WF_101 | 4 | 0.1081 | 10.8% |
| WF_102 | 5 | 0.1351 | 13.5% |
| WF_103 | 5 | 0.1351 | 13.5% |
| WF_104 | 3 | 0.0811 | 8.1% |
| WF_105 | 4 | 0.1081 | 10.8% |
| WF_108 | 3 | 0.0811 | 8.1% |
| WF_109 | 3 | 0.0811 | 8.1% |
| WF_1106 | 6 | 0.1622 | 16.2% |
| WF_1107 | 4 | 0.1081 | 10.8% |
| **Total** | **37** | **1.0000** | **100.0%** |

**Most frequent:** WF_1106 (16.2%), WF_102 and WF_103 (13.5% each)
**Least frequent:** WF_104, WF_108, WF_109 (8.1% each)

## 5. Per-Process-Model Inter-Arrival Times

Per-model IATs are computed from the subsequence of arrivals for each model. These reflect the spacing between consecutive cases of the same type, not the global arrival process.

| Process Model | Cases | Mean (min) | Std (min) | Min (min) | Max (min) | Median (min) | CV | Outliers |
|---|---|---|---|---|---|---|---|---|
| WF_101 | 4 | 22.14 | 2.24 | 19.56 | 23.56 | 23.29 | 0.101 | 0 |
| WF_102 | 5 | 17.14 | 6.51 | 8.26 | 23.56 | 18.38 | 0.380 | 0 |
| WF_103 | 5 | 19.38 | 6.15 | 10.51 | 23.56 | 21.72 | 0.318 | 0 |
| WF_104 | 3 | 33.53 | 14.08 | 23.57 | 43.49 | 33.53 | 0.420 | 0 |
| WF_105 | 4 | 22.35 | 2.16 | 19.86 | 23.64 | 23.56 | 0.097 | 0 |
| WF_108 | 3 | 23.38 | 11.85 | 15.00 | 31.76 | 23.38 | 0.507 | 0 |
| WF_109 | 3 | 33.51 | 2.47 | 31.77 | 35.26 | 33.51 | 0.074 | 0 |
| WF_1106 | 6 | 13.99 | 2.69 | 10.30 | 16.53 | 14.57 | 0.192 | 1 |
| WF_1107 | 4 | 25.84 | 10.34 | 13.90 | 31.84 | 31.77 | 0.400 | 0 |

**Note:** Per-model IATs are much larger (14–34 min) because each model only accounts for ~8–16% of arrivals. These values are informative for understanding model-specific throughput but are **not** used as the arrival process parameter in the DES model.

## 6. CV Analysis & Distribution Assessment

| Metric | Value | Interpretation |
|---|---|---|
| Global CV (all 36 IATs) | 2.0438 | **CV >> 1** — highly bursty, non-Poisson |
| Clean CV (29 IATs, no outliers) | 2.4232 | **CV >> 1** — burstiness persists even after removing inter-burst gaps |
| Intra-burst CV (26 IATs) | 2.1567 | **CV >> 1** — even within bursts, arrivals are irregular |

### 6.1 Key Findings

1. **Not Poisson:** A Poisson process would have CV ≈ 1. All three CV measures (global, clean, intra-burst) are well above 2, indicating a highly bursty arrival process.

2. **Two-regime structure:** The arrival process has two distinct regimes:
   - **Intra-burst:** Cases arrive within seconds of each other (mean 3.18 s, median 1.09 s)
   - **Inter-burst:** Idle gaps between bursts average 7.6 minutes (range: 1.1–16.5 min)

3. **Burst sizes vary:** Bursts contain 1–9 cases (mean ~3.4 cases per burst). The first burst contains all 9 process models, suggesting a deliberate batch release pattern.

4. **Small sample warning:** With only 37 cases and 36 IATs, statistical estimates have high uncertainty. The per-model IATs have particularly small samples (3–6 cases each).

## 7. DES Simulation Recommendations

### 7.1 Arrival Process Modeling

Given the burst structure, the arrival process should **not** be modeled as a simple Poisson/exponential inter-arrival process. Recommended approaches:

1. **Two-stage arrival process:**
   - **Stage 1 (Burst generation):** Generate bursts with inter-burst gaps drawn from a distribution fitted to the 10 observed gaps (mean 7.6 min).
   - **Stage 2 (Within-burst):** Generate burst sizes (1–9 cases) and release cases within each burst with very small intra-burst IATs (mean ~3 s).

2. **Alternative — Deterministic batch release:** If the burst pattern reflects a production schedule, model arrivals as deterministic batches at fixed intervals with random batch sizes.

3. **Simple approximation — Exponential with adjusted rate:** If a simple model is required, use an exponential distribution with mean IAT = 2.16 min (global mean), but acknowledge this will not reproduce the burst structure.

### 7.2 Process Model Assignment

At each arrival, assign the process model using a categorical distribution with the observed proportions:

```python
model_weights = {
    'WF_101': 0.1081, 'WF_102': 0.1351, 'WF_103': 0.1351,
    'WF_104': 0.0811, 'WF_105': 0.1081, 'WF_108': 0.0811,
    'WF_109': 0.0811, 'WF_1106': 0.1622, 'WF_1107': 0.1081
}
```

### 7.3 Data Quality Flags

| Flag | Status | Detail |
|---|---|---|
| Sample size | ⚠️ Low | Only 37 cases (36 IATs); per-model samples as low as 3 |
| CV > 1 | ⚠️ Yes | Global CV = 2.04, Clean CV = 2.42 — non-Poisson |
| Outlier rate | ⚠️ High | 19.4% of IATs are outliers (inter-burst gaps) |
| Time span | ⚠️ Short | Single day (77.6 min observation window) |

## 8. Summary

| Parameter | Value | Notes |
|---|---|---|
| Global arrival rate | 37 cases / 77.6 min ≈ 0.477 cases/min | ≈ 1 case per 2.1 min (including idle gaps) |
| Clean IAT mean | 0.2119 min (12.71 s) | Excludes 7 inter-burst gap outliers |
| Clean IAT CV | 2.4232 | Highly bursty |
| Burst count | 11 | Sizes: 1–9 cases |
| Intra-burst IAT mean | 0.0530 min (3.18 s) | Cases within bursts arrive nearly simultaneously |
| Inter-burst gap mean | 7.62 min | Idle time between bursts |
| Process models | 9 | Mix proportions range from 8.1% to 16.2% |

**Conclusion:** The arrival process is bursty with two distinct time scales (seconds within bursts, minutes between bursts). A simple Poisson/exponential model is inappropriate. The DES should model the two-stage burst structure or use a compound arrival process to faithfully reproduce the observed behavior.
