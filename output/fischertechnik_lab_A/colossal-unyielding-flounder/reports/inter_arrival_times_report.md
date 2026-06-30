# Inter-Arrival Times Report — Fischertechnik Manufacturing System

## 1. Dataset Characteristics

| Property | Value |
|---|---|
| Source file | `eventlog_cleaned.parquet` |
| Total events | 576 (192 operations × 3 lifecycle events) |
| Unique cases | 18 (9 variants × 2 instances each) |
| Product variants | 9 (WF_101–WF_105, WF_108–WF_109, WF_1106–WF_1107) |
| Time window | 2021-07-06 15:08:27 – 15:46:30 UTC (~38 minutes) |
| Arrival definition | Earliest `scheduled` timestamp per `case` |

---

## 2. Two-Phase Arrival Pattern

The case arrivals exhibit a **clearly bimodal pattern** with an initial near-simultaneous burst followed by a steady-state phase with intermittent sub-bursts.

### 2.1 Phase 1 — Initial Burst (Cases 1–8)

The first 8 cases arrive within a **6.9-second window** at the start of the observation period:

| Order | Case | Variant | Arrival Time | IAT (s) |
|---|---|---|---|---|
| 1 | WF_101_30 | WF_101 | 15:08:27.915 | — |
| 2 | WF_102_31 | WF_102 | 15:08:28.821 | 0.906 |
| 3 | WF_103_29 | WF_103 | 15:08:30.476 | 1.656 |
| 4 | WF_105_21 | WF_105 | 15:08:31.961 | 1.485 |
| 5 | WF_1106_21 | WF_1106 | 15:08:32.602 | 0.641 |
| 6 | WF_1107_16 | WF_1107 | 15:08:33.415 | 0.813 |
| 7 | WF_108_17 | WF_108 | 15:08:33.924 | 0.510 |
| 8 | WF_109_15 | WF_109 | 15:08:34.821 | 0.896 |

**Burst Phase Statistics:**

| Statistic | Value |
|---|---|
| Count | 8 cases |
| IAT count | 7 samples |
| Mean IAT | 0.987 s |
| Std IAT | 0.389 s |
| Min IAT | 0.510 s |
| Max IAT | 1.656 s |
| Total span | 6.906 s |

**Interpretation:** The first 8 cases represent a near-simultaneous batch arrival, likely triggered by a single production order or system startup. All inter-arrival times are under 2 seconds, indicating these cases were queued and released together.

### 2.2 Phase 2 — Steady-State (Cases 9–18)

After a **10.6-minute idle gap**, the second wave of 10 cases arrives over approximately 27 minutes:

| Order | Case | Variant | Arrival Time | IAT (s) | Classification |
|---|---|---|---|---|---|
| 9 | WF_104_20 | WF_104 | 15:19:08.317 | 633.497 | Gap |
| 10 | WF_1106_22 | WF_1106 | 15:32:28.274 | 799.957 | Gap |
| 11 | WF_103_30 | WF_103 | 15:37:46.149 | 317.875 | Gap |
| 12 | WF_105_22 | WF_105 | 15:37:48.508 | 2.359 | Sub-burst |
| 13 | WF_101_31 | WF_101 | 15:40:07.618 | 139.110 | Gap |
| 14 | WF_102_32 | WF_102 | 15:40:08.305 | 0.687 | Sub-burst |
| 15 | WF_1107_17 | WF_1107 | 15:41:41.711 | 93.406 | Gap |
| 16 | WF_104_21 | WF_104 | 15:41:47.242 | 5.531 | Sub-burst |
| 17 | WF_108_18 | WF_108 | 15:41:49.243 | 2.000 | Sub-burst |
| 18 | WF_109_16 | WF_109 | 15:46:30.148 | 280.906 | Gap |

**Steady-State Phase Statistics (all 10 IATs):**

| Statistic | Value |
|---|---|
| Count | 10 cases (9 IAT samples) |
| Mean IAT | 227.533 s (3.79 min) |
| Std IAT | 285.113 s (4.75 min) |
| Min IAT | 0.687 s |
| Max IAT | 799.957 s (13.33 min) |
| Median IAT | 93.406 s (1.56 min) |
| CV | 1.2531 |

### 2.3 Steady-State Sub-Classification

The steady-state phase contains two distinct sub-patterns:

#### Real Gaps (IAT ≥ 10 s) — 6 samples

| Statistic | Value |
|---|---|
| Mean | 377.458 s (6.29 min) |
| Std | 280.866 s (4.68 min) |
| Min | 93.406 s (1.56 min) |
| Max | 799.957 s (13.33 min) |
| CV | 0.7441 |

#### Sub-Bursts (IAT < 10 s) — 4 samples

| Statistic | Value |
|---|---|
| Mean | 2.644 s |
| Values | 2.359 s, 0.687 s, 5.531 s, 2.000 s |

**Interpretation:** The steady-state phase is itself structured as alternating gaps and sub-bursts. Cases 12–14 (WF_105_22, WF_101_31, WF_102_32) and cases 15–17 (WF_1107_17, WF_104_21, WF_108_18) form near-simultaneous pairs/triplets separated by longer gaps. This suggests a **batch-release pattern** where groups of 2–3 cases are released together, with 1.5–13 minute intervals between batches.

---

## 3. Global Inter-Arrival Statistics (All 18 Cases)

Using the `extract_inter_arrival_times` tool with IQR-based outlier detection:

| Statistic | Value |
|---|---|
| Total cases | 18 |
| IAT samples | 17 |
| Mean IAT | 56.585 s |
| Std IAT | 106.921 s |
| Min IAT | 0.510 s |
| Max IAT | 317.875 s |
| Median IAT | 1.656 s |
| CV | 1.8895 |

### 3.1 Outlier Detection (IQR Method, k = 1.5)

| Property | Value |
|---|---|
| Method | IQR (Tukey fences) |
| Lower bound | −206.424 s (clamped to 0) |
| Upper bound | 346.430 s |
| Outliers detected | 2 |
| Outlier rate | 11.76% |
| Outlier IAT values | 799.957 s (WF_1106_22), 633.497 s (WF_104_20) |

**Clean statistics (after outlier removal):** The two longest IATs (633.5 s and 800.0 s) are flagged as outliers. These correspond to the transition from the initial burst to the steady-state phase and the longest gap within the steady-state phase.

### 3.2 CV Analysis

| Phase | CV | Interpretation |
|---|---|---|
| Global (all 17 IATs) | 1.8895 | **Highly non-Poisson** — bimodal arrival pattern |
| Burst phase (7 IATs) | 0.394 | Low variability — near-constant sub-second spacing |
| Steady-state (9 IATs) | 1.2531 | Non-Poisson — mixed gaps and sub-bursts |
| Steady-state gaps only (6 IATs) | 0.7441 | Moderate variability — more consistent |

**Key finding:** A CV > 1 for the global and steady-state phases confirms that arrivals are **not Poisson-distributed**. The bimodal pattern (burst + steady-state with sub-bursts) means a single exponential distribution is inappropriate for modeling inter-arrivals.

---

## 4. Per-Variant Arrival Analysis

Each variant has exactly 2 case instances. Per-variant IAT computation requires ≥ 3 arrivals for meaningful statistics, so the `extract_inter_arrival_times` tool reports "Too few arrivals" for all variants. However, the inter-instance timing per variant is informative:

| Variant | Instance 1 | Instance 2 | Time Between Instances |
|---|---|---|---|
| WF_101 | 15:08:27.915 | 15:40:07.618 | 18 min 40 s |
| WF_102 | 15:08:28.821 | 15:40:08.305 | 18 min 40 s |
| WF_103 | 15:08:30.476 | 15:37:46.149 | 29 min 16 s |
| WF_104 | 15:19:08.317 | 15:41:47.242 | 22 min 39 s |
| WF_105 | 15:08:31.961 | 15:37:48.508 | 29 min 17 s |
| WF_108 | 15:08:33.924 | 15:41:49.243 | 33 min 15 s |
| WF_109 | 15:08:34.821 | 15:46:30.148 | 37 min 55 s |
| WF_1106 | 15:08:32.602 | 15:32:28.274 | 23 min 56 s |
| WF_1107 | 15:08:33.415 | 15:41:41.711 | 33 min 08 s |

**Observation:** All variants have their first instance in the initial burst (except WF_104, which starts at 15:19:08). The second instances arrive 19–38 minutes later, with no clear per-variant scheduling pattern. This suggests a **system-wide batch scheduling** rather than per-variant timing.

---

## 5. Simulation Modeling Recommendations

### 5.1 Recommended Arrival Process

Model inter-arrivals as a **three-component process**:

1. **Initial burst:** Release 8 cases simultaneously (or with exponential jitter, mean ≈ 1 s) at simulation start.
2. **Idle gap:** Wait ~630 s (10.5 min) before the next batch.
3. **Steady-state batch arrivals:** Release groups of 2–3 cases with:
   - Inter-batch gaps: mean ≈ 377 s (6.3 min), CV ≈ 0.74
   - Within-burst spacing: mean ≈ 2.6 s (near-simultaneous)

### 5.2 Alternative Simplified Model

If a simpler model is preferred:

- **Phase 1:** Deterministic burst of 8 cases at t = 0
- **Phase 2:** After a 630 s delay, use a **Gamma distribution** (shape ≈ 2–3, scale ≈ 150–200 s) for inter-arrival times, with occasional sub-bursts modeled as clusters of 2–3 arrivals within a 10 s window.

### 5.3 Distribution Fitting Notes

- **Exponential is inappropriate** (CV >> 1 for global, CV > 1 for steady-state)
- **Gamma or Weibull** may fit the steady-state gap distribution (6 samples, CV = 0.74)
- Sample sizes are very small (6 gap samples, 4 sub-burst samples) — distribution fitting should be flagged as **low confidence**
- Consider **deterministic batch scheduling** as the primary model, with stochastic jitter added for realism

---

## 6. Data Quality Flags

| Flag | Status | Detail |
|---|---|---|
| Sample size | ⚠️ **Low** | Only 17 IAT samples total; 6 steady-state gap samples |
| CV > 1 | ✅ **Flagged** | Global CV = 1.89; steady-state CV = 1.25 |
| Outlier rate | ⚠️ **Elevated** | 2/17 outliers (11.76%) — reflects bimodal pattern, not noise |
| Per-variant stats | ❌ **Insufficient** | Only 2 instances per variant; no per-variant IAT statistics |
| Distribution fitting | ⚠️ **Low confidence** | Too few samples for reliable goodness-of-fit tests |

---

## 7. Summary

| Phase | Cases | IAT Samples | Mean IAT | CV | Pattern |
|---|---|---|---|---|---|
| Burst (1–8) | 8 | 7 | 0.99 s | 0.39 | Near-simultaneous |
| Transition gap | — | 1 | 633.5 s | — | Idle period |
| Steady-state (9–18) | 10 | 9 | 227.5 s | 1.25 | Mixed gaps + sub-bursts |
| Steady-state gaps | — | 6 | 377.5 s | 0.74 | Batch-release intervals |
| Steady-state sub-bursts | — | 4 | 2.64 s | — | Near-simultaneous pairs |
| **Global** | **18** | **17** | **56.6 s** | **1.89** | **Bimodal** |

The arrival process is **not Poisson**. It is best modeled as a **batch-release process** with an initial burst of 8 cases, followed by intermittent batches of 2–3 cases separated by 1.5–13 minute gaps.
