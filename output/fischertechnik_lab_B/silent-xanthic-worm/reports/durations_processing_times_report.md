# Durations & Processing Times Report — Fischertechnik Lab B

## 1. Duration Computation Results

### 1.1 Duration Columns

| Duration Column | Source | Available On | Count | Unit |
|---|---|---|---|---|
| `actual_duration` | `operation_end_time − time:timestamp` | `start` transitions | 461 | seconds |
| `planned_operation_time` | System-configured expected duration | All rows | 1,383 | seconds |
| `complete_service_time` | Full response time (scheduled→complete) | `complete` transitions | 461 | seconds |
| `queue_time` (derived) | `complete_service_time − actual_duration` | Merged start+complete | 461 | seconds |

### 1.2 Duration Computation Tool Output

The `compute_duration` tool was invoked on `time:timestamp` → `operation_end_time` across all 1,383 rows:

| Metric | Value |
|---|---|
| Total rows | 1,383 |
| Valid durations | 1,377 |
| Zero durations | 423 (scheduled events where start=end) |
| Positive durations | 954 |
| Negative durations | 0 |
| Mean | 34.35 s |
| Median | 14.06 s |
| Std Dev | 89.28 s |
| Min | 0.006 s |
| Max | 1,034.30 s |

**Note:** The high mean/median discrepancy and large std dev reflect the mix of zero-duration scheduled events and positive-duration start events. The `actual_duration` column (pre-computed on start events only) is the primary source for processing time analysis.

### 1.3 Aggregate Duration Statistics

| Metric | `actual_duration` | `planned_operation_time` | `complete_service_time` | `queue_time` |
|---|---|---|---|---|
| Count | 461 | 461 | 461 | 461 |
| Mean (s) | 30.4 | 51.5 | 73.6 | 43.2 |
| Median (s) | 31.9 | 42.0 | 40.1 | 6.2 |
| Std (s) | 17.4 | 52.3 | 129.4 | 126.6 |
| Min (s) | 0.0 | 5.0 | 3.4 | 2.2 |
| Max (s) | 218.7 | 222.0 | 1,079.1 | 1,035.1 |

**Key observation:** Actual processing times average 30.4 s vs planned 51.5 s (ratio 0.86). Queue time averages 43.2 s but is heavily right-skewed (median 6.2 s), indicating most operations start shortly after scheduling, with a few experiencing long waits.

---

## 2. Processing Times by Activity-Resource

Processing times are extracted from `actual_duration` on `start` transition events, grouped by `(concept:name, org:resource)`. Outlier detection uses IQR method (threshold 1.5×IQR).

### 2.1 Full Processing Time Table

| Activity | Resource | N | Clean | Outliers | Rate% | Mean (s) | Std (s) | Median (s) | Min (s) | Max (s) | Planned (s) | SvcTime (s) | Queue (s) | Failures |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/dm/cylindrical_drill` | dm_2 | 4 | 3 | 1 | 25.0% ⚠️ | 30.8 | 2.7 | 31.8 | 26.9 | 32.8 | 47 | 34.4 | 3.6 | 0 |
| `/dm/lower` | dm_2 | 4 | 4 | 0 | 0.0% | 13.9 | 0.1 | 13.9 | 13.8 | 14.0 | 14 | 18.3 | 4.3 | 0 |
| `/hbw/get_empty_bucket` | hbw_1 | 15 | 13 | 2 | 13.3% ⚠️ | 39.4 | 5.1 | 37.2 | 33.6 | 51.7 | 46 | 46.6 | 7.2 | 0 |
| `/hbw/store` | hbw_1 | 14 | 14 | 0 | 0.0% | 37.7 | 2.8 | 37.2 | 33.8 | 42.2 | 46 | 42.4 | 4.7 | 0 |
| `/hbw/store_empty_bucket` | hbw_1 | 1 | 1 | 0 | 0.0% | 37.3 | 0.0 | 37.3 | 37.3 | 37.3 | 46 | 169.8 | 132.5 | 0 |
| `/hbw/store_empty_bucket` | hbw_2 | 36 | 35 | 1 | 2.8% | 36.9 | 5.9 | 37.3 | 9.3 | 44.3 | 47 | 43.7 | 6.8 | 2 |
| `/hbw/unload` | hbw_2 | 38 | 36 | 2 | 5.3% ⚠️ | 37.8 | 10.6 | 38.3 | 0.0 | 52.4 | 52 | 424.6 | 386.8 | 2 |
| `/hw/human_review` | hw_1 | 30 | 25 | 5 | 16.7% ⚠️ | 16.7 | 28.0 | 2.3 | 0.0 | 98.1 | 102 | 20.9 | 4.2 | 0 |
| `/mm/deburr` | mm_1 | 21 | 18 | 3 | 14.3% ⚠️ | 14.4 | 0.7 | 14.2 | 13.8 | 16.5 | 14 | 20.6 | 6.2 | 0 |
| `/mm/deburr` | mm_2 | 4 | 3 | 1 | 25.0% ⚠️ | 14.3 | 0.1 | 14.3 | 14.2 | 14.5 | 15 | 20.6 | 6.2 | 0 |
| `/mm/drill` | mm_2 | 7 | 7 | 0 | 0.0% | 11.1 | 5.5 | 15.4 | 5.3 | 15.7 | 18 | 16.8 | 5.7 | 0 |
| `/mm/mill` | mm_1 | 15 | 13 | 2 | 13.3% ⚠️ | 5.8 | 2.3 | 5.1 | 4.9 | 14.0 | 6 | 11.8 | 6.0 | 0 |
| `/mm/mill` | mm_2 | 4 | 4 | 0 | 0.0% | 14.4 | 0.2 | 14.4 | 14.2 | 14.7 | 14 | 19.5 | 5.1 | 0 |
| `/mm/transport_from_to` | mm_1 | 1 | 1 | 0 | 0.0% | 23.0 | 0.0 | 23.0 | 23.0 | 23.0 | 12 | 29.6 | 6.5 | 0 |
| `/mm/transport_from_to` | mm_2 | 2 | 2 | 0 | 0.0% | 12.0 | 0.3 | 12.0 | 11.8 | 12.2 | 12 | 19.3 | 7.4 | 0 |
| `/ov/burn` | ov_1 | 21 | 21 | 0 | 0.0% | 26.8 | 5.3 | 26.1 | 20.8 | 37.5 | 222 | 33.3 | 6.5 | 0 |
| `/ov/burn` | ov_2 | 12 | 10 | 2 | 16.7% ⚠️ | 47.0 | 54.7 | 34.4 | 9.2 | 218.7 | 222 | 53.3 | 6.3 | 0 |
| `/ov/temper` | ov_1 | 14 | 14 | 0 | 0.0% | 52.7 | 1.3 | 52.4 | 50.9 | 54.4 | 56 | 58.7 | 6.1 | 0 |
| `/pm/punch_gill` | pm_1 | 3 | 3 | 0 | 0.0% | 27.8 | 0.5 | 27.5 | 27.5 | 28.3 | 35 | 31.2 | 3.5 | 0 |
| `/pm/punch_recesses` | pm_1 | 5 | 5 | 0 | 0.0% | 23.3 | 0.2 | 23.4 | 23.2 | 23.6 | 39 | 26.5 | 3.2 | 0 |
| `/pm/punch_ribbing` | pm_1 | 5 | 4 | 1 | 20.0% ⚠️ | 24.7 | 3.7 | 23.2 | 22.8 | 31.4 | 39 | 27.9 | 3.2 | 0 |
| `/sm/sort` | sm_1 | 10 | 9 | 1 | 10.0% ⚠️ | 16.9 | 11.2 | 12.4 | 10.8 | 47.4 | 12 | 20.5 | 3.6 | 0 |
| `/sm/sort` | sm_2 | 6 | 6 | 0 | 0.0% | 9.4 | 0.8 | 9.4 | 8.7 | 10.4 | 11 | 13.6 | 4.1 | 0 |
| `/sm/transport` | sm_1 | 13 | 11 | 2 | 15.4% ⚠️ | 23.2 | 7.4 | 20.7 | 18.1 | 44.5 | 18 | 26.6 | 3.4 | 0 |
| `/sm/transport` | sm_2 | 8 | 8 | 0 | 0.0% | 14.5 | 0.3 | 14.4 | 14.1 | 14.8 | 15 | 18.2 | 3.7 | 0 |
| `/vgr/pick_up_and_transport` | vgr_1 | 85 | 85 | 0 | 0.0% | 36.6 | 13.8 | 41.6 | 11.0 | 55.3 | 36 | 70.0 | 33.4 | 1 |
| `/vgr/pick_up_and_transport` | vgr_2 | 42 | 42 | 0 | 0.0% | 40.8 | 4.2 | 43.3 | 31.3 | 46.2 | 38 | 51.2 | 10.3 | 0 |
| `/wt/pick_up_and_transport` | wt_1 | 27 | 25 | 2 | 7.4% ⚠️ | 26.2 | 0.5 | 26.0 | 25.9 | 28.9 | 22 | 38.8 | 12.6 | 4 |
| `/wt/pick_up_and_transport` | wt_2 | 14 | 13 | 1 | 7.1% ⚠️ | 29.5 | 0.1 | 29.5 | 29.3 | 29.9 | 27 | 37.7 | 8.2 | 0 |

**⚠️ = Outlier rate > 5% for that group**

### 2.2 Outlier Summary

| Activity | Resource | Outlier Count / Total | Rate | Notes |
|---|---|---|---|---|
| `/dm/cylindrical_drill` | dm_2 | 1/4 | 25.0% ⚠️ | Low sample (n=4); 1 high value |
| `/hbw/get_empty_bucket` | hbw_1 | 2/15 | 13.3% ⚠️ | 2 high outliers |
| `/hbw/unload` | hbw_2 | 2/38 | 5.3% ⚠️ | Includes 0.0s failure event |
| `/hw/human_review` | hw_1 | 5/30 | 16.7% ⚠️ | Highly variable (0–98s); human-dependent |
| `/mm/deburr` | mm_1 | 3/21 | 14.3% ⚠️ | Mostly tight; 3 high outliers |
| `/mm/deburr` | mm_2 | 1/4 | 25.0% ⚠️ | Low sample (n=4) |
| `/mm/mill` | mm_1 | 2/15 | 13.3% ⚠️ | 1 outlier at 14.0s (vs median 5.1s) |
| `/ov/burn` | ov_2 | 2/12 | 16.7% ⚠️ | 1 extreme outlier at 218.7s |
| `/pm/punch_ribbing` | pm_1 | 1/5 | 20.0% ⚠️ | Low sample (n=5) |
| `/sm/sort` | sm_1 | 1/10 | 10.0% ⚠️ | 1 outlier at 47.4s |
| `/sm/transport` | sm_1 | 2/13 | 15.4% ⚠️ | 2 high outliers |
| `/wt/pick_up_and_transport` | wt_1 | 2/27 | 7.4% ⚠️ | Includes failure events |
| `/wt/pick_up_and_transport` | wt_2 | 1/14 | 7.1% ⚠️ | 1 outlier |

**Groups with outlier_rate > 5% are flagged.** Many flagged groups have low sample sizes (n < 10), which inflates outlier rates. The most concerning high-sample groups are `/hw/human_review` (16.7%, n=30) and `/vgr/pick_up_and_transport @ vgr_1` (0%, n=85 — clean).

---

## 3. Planned vs. Actual Comparison

### 3.1 Ratio Analysis by Activity

| Activity | N | Mean Ratio (Actual/Planned) | Median Ratio | Std Ratio | Interpretation |
|---|---|---|---|---|---|
| `/dm/cylindrical_drill` | 4 | 0.656 | 0.676 | 0.056 | Actual 34% faster than planned |
| `/dm/lower` | 4 | 0.995 | 0.996 | 0.008 | Matches planned almost exactly |
| `/hbw/get_empty_bucket` | 15 | 0.857 | 0.810 | 0.111 | Actual 14% faster |
| `/hbw/store` | 14 | 0.820 | 0.809 | 0.061 | Actual 18% faster |
| `/hbw/store_empty_bucket` | 37 | 0.787 | 0.806 | 0.123 | Actual 21% faster |
| `/hbw/unload` | 38 | 0.726 | 0.736 | 0.204 | Actual 27% faster |
| `/hw/human_review` | 30 | 0.164 | 0.023 | 0.274 | ⚠️ Highly variable; planned 102s is unrealistic |
| `/mm/deburr` | 25 | 1.017 | 1.016 | 0.052 | Matches planned |
| `/mm/drill` | 7 | 0.592 | 0.702 | 0.141 | Actual 41% faster |
| `/mm/mill` | 19 | 1.037 | 1.019 | 0.049 | Matches planned |
| `/mm/transport_from_to` | 3 | 1.306 | 1.018 | 0.533 | Variable; low sample |
| `/ov/burn` | 33 | 0.154 | 0.128 | 0.152 | ⚠️ Planned 222s is unrealistic; actual ~27–47s |
| `/ov/temper` | 14 | 0.941 | 0.936 | 0.023 | Close to planned (56s) |
| `/pm/punch_gill` | 3 | 0.793 | 0.786 | 0.013 | Actual 21% faster |
| `/pm/punch_recesses` | 5 | 0.599 | 0.599 | 0.005 | Actual 40% faster; very consistent |
| `/pm/punch_ribbing` | 5 | 0.635 | 0.595 | 0.095 | Actual 37% faster |
| `/sm/sort` | 16 | 1.203 | 0.929 | 0.772 | ⚠️ High variance; sm_1 much slower than planned |
| `/sm/transport` | 21 | 1.165 | 1.050 | 0.358 | Slightly slower than planned |
| `/vgr/pick_up_and_transport` | 127 | 1.042 | 1.080 | 0.129 | Matches planned |
| `/wt/pick_up_and_transport` | 41 | 1.157 | 1.183 | 0.051 | Actual 16% slower than planned |

### 3.2 Key Findings

1. **Oven burn (`/ov/burn`):** Planned time of 222s is grossly inflated. Actual times are 26.8s (ov_1) and 47.0s (ov_2). The planned value likely includes a safety margin or represents a worst-case scenario. **Recommendation:** Use actual observed times for simulation.

2. **Human review (`/hw/human_review`):** Planned 102s vs actual median of 2.3s. The planned time is unrealistic; actual times range from 0–98s with extreme variability. **Recommendation:** Model as highly variable (possibly exponential) with mean ~17s.

3. **Punching operations:** All three pm_1 activities run 40–60% faster than planned. The planned times appear to include generous safety margins.

4. **Well-calibrated activities:** `/mm/deburr` (ratio 1.02), `/mm/mill` (1.04), `/vgr/pick_up_and_transport` (1.04), `/ov/temper` (0.94), and `/dm/lower` (1.00) closely match planned times.

5. **Transport operations:** `/wt/pick_up_and_transport` runs 16% slower than planned, while `/vgr/pick_up_and_transport` matches closely.

---

## 4. Queue Time Analysis

### 4.1 Queue Time by Resource

| Resource | N | Mean (s) | Median (s) | Std (s) | Min (s) | Max (s) |
|---|---|---|---|---|---|---|
| dm_2 | 8 | 4.0 | 3.7 | 1.7 | 2.2 | 7.7 |
| hbw_1 | 30 | 10.2 | 4.2 | 24.4 | 2.4 | 132.5 |
| hbw_2 | 74 | 201.9 | 17.1 | 261.7 | 3.2 | 1,035.1 |
| hw_1 | 30 | 4.2 | 3.7 | 1.2 | 2.2 | 6.4 |
| mm_1 | 37 | 6.1 | 5.7 | 1.1 | 4.6 | 9.4 |
| mm_2 | 17 | 5.9 | 5.6 | 1.1 | 4.7 | 9.1 |
| ov_1 | 35 | 6.3 | 5.9 | 1.6 | 4.6 | 12.2 |
| ov_2 | 12 | 6.3 | 5.7 | 1.8 | 5.2 | 11.6 |
| pm_1 | 13 | 3.2 | 2.9 | 0.9 | 2.4 | 5.2 |
| sm_1 | 23 | 3.5 | 3.0 | 1.4 | 2.3 | 7.3 |
| sm_2 | 14 | 3.9 | 3.9 | 1.0 | 2.5 | 6.0 |
| vgr_1 | 85 | 33.4 | 21.1 | 30.3 | 2.6 | 145.1 |
| vgr_2 | 42 | 10.3 | 6.6 | 11.0 | 3.3 | 59.5 |
| wt_1 | 27 | 12.6 | 8.5 | 10.2 | 7.4 | 37.7 |
| wt_2 | 14 | 8.2 | 7.7 | 1.2 | 7.0 | 10.9 |

### 4.2 Queue Time Insights

1. **hbw_2 (entry point):** Mean queue 201.9s but median only 17.1s. The extreme right tail (max 1,035s) reflects the system startup phase where the first workpiece waits for the system to initialize. After warmup, queue times are low.

2. **vgr_1 (primary interconnect):** Mean 33.4s, median 21.1s. This is the busiest resource (85 operations) and serves as the main bottleneck for inter-station transport. Queue times are consistently higher than other resources.

3. **Processing stations (mm, ov, pm, sm):** Queue times are uniformly low (3–6s median), indicating that workpieces rarely wait for these resources. The system is not resource-constrained at processing stations.

4. **wt_1 vs wt_2:** wt_1 has higher queue times (mean 12.6s vs 8.2s), consistent with its higher load and the 4 failure events that cause retries.

---

## 5. Failure and Rework Parameters

### 5.1 Failure Summary

| Metric | Value |
|---|---|
| Total failure events | 9 out of 461 entities (1.96%) |
| Cases with failures | 3 out of 38 (7.9%) |
| Terminal failures | 6 (entity removed from workflow) |
| Non-terminal (absorbed) | 2 (workflow continued) |
| Retried with success | 1 (3rd attempt succeeded) |

### 5.2 Failure Probability by Activity-Resource

| Activity | Resource | Failures | Total | Failure Rate |
|---|---|---|---|---|
| `/hbw/store_empty_bucket` | hbw_2 | 2 | 36 | 5.6% |
| `/hbw/unload` | hbw_2 | 2 | 38 | 5.3% |
| `/wt/pick_up_and_transport` | wt_1 | 4 | 27 | 14.8% |
| `/vgr/pick_up_and_transport` | vgr_1 | 1 | 85 | 1.2% |
| All others | — | 0 | 355 | 0.0% |

### 5.3 Retry Pattern (WF_104_8)

Three consecutive `/wt/pick_up_and_transport` attempts on `wt_1`:

| Attempt | Entity | Outcome | Start Time | Duration (s) |
|---|---|---|---|---|
| 1 | a_14015 | Failure | 1625068340.3 | 26.1 |
| 2 | a_14055 | Failure | 1625068409.4 | 26.0 |
| 3 | a_14239 | Success | 1625068539.0 | 25.9 |

**Retry delays:**
- Delay 1→2: **69.1 seconds**
- Delay 2→3: **129.6 seconds**

The retry delay increases between attempts, suggesting an exponential backoff or manual intervention pattern.

---

## 6. Simulation Parameter Recommendations

### 6.1 Processing Time Parameters

For simulation, use **cleaned means** (outlier-removed) where sample size permits (n ≥ 5). For low-sample groups, pool with sibling resources in the same class.

#### Recommended Processing Time Distributions (seconds)

| Activity-Resource | N | Mean | Std | Median | Recommended Distribution | Notes |
|---|---|---|---|---|---|---|
| `/dm/cylindrical_drill @ dm_2` | 4 | 30.8 | 2.7 | 31.8 | Normal(31, 3) | Low sample; pool with `/dm/lower` if needed |
| `/dm/lower @ dm_2` | 4 | 13.9 | 0.1 | 13.9 | Deterministic(14) | Very tight |
| `/hbw/get_empty_bucket @ hbw_1` | 15 | 39.4 | 5.1 | 37.2 | Normal(39, 5) | |
| `/hbw/store @ hbw_1` | 14 | 37.7 | 2.8 | 37.2 | Normal(38, 3) | |
| `/hbw/store_empty_bucket @ hbw_2` | 36 | 36.9 | 5.9 | 37.3 | Normal(37, 6) | |
| `/hbw/unload @ hbw_2` | 38 | 37.8 | 10.6 | 38.3 | Normal(38, 11) | Exclude 0s failure events |
| `/hw/human_review @ hw_1` | 30 | 16.7 | 28.0 | 2.3 | **Exponential(17)** | ⚠️ Highly variable; ignore planned 102s |
| `/mm/deburr @ mm_1/mm_2` (pooled) | 25 | 14.4 | 0.7 | 14.2 | Normal(14, 1) | Very tight; pool mm_1+mm_2 |
| `/mm/drill @ mm_2` | 7 | 11.1 | 5.5 | 15.4 | Uniform(5, 16) | Variable |
| `/mm/mill @ mm_1` | 15 | 5.8 | 2.3 | 5.1 | Normal(6, 2) | |
| `/mm/mill @ mm_2` | 4 | 14.4 | 0.2 | 14.4 | Deterministic(14) | Different from mm_1! |
| `/mm/transport_from_to @ mm_1/mm_2` (pooled) | 3 | 15.7 | 6.0 | 12.0 | Normal(16, 6) | Low sample; pooled |
| `/ov/burn @ ov_1` | 21 | 26.8 | 5.3 | 26.1 | Normal(27, 5) | Ignore planned 222s |
| `/ov/burn @ ov_2` | 12 | 47.0 | 54.7 | 34.4 | **Exponential(34)** | ⚠️ Highly variable; exclude 218s outlier |
| `/ov/temper @ ov_1` | 14 | 52.7 | 1.3 | 52.4 | Deterministic(53) | Very tight |
| `/pm/punch_gill @ pm_1` | 3 | 27.8 | 0.5 | 27.5 | Deterministic(28) | |
| `/pm/punch_recesses @ pm_1` | 5 | 23.3 | 0.2 | 23.4 | Deterministic(23) | |
| `/pm/punch_ribbing @ pm_1` | 5 | 24.7 | 3.7 | 23.2 | Normal(25, 4) | |
| `/sm/sort @ sm_1` | 10 | 16.9 | 11.2 | 12.4 | **Exponential(17)** | Variable; exclude 47s outlier |
| `/sm/sort @ sm_2` | 6 | 9.4 | 0.8 | 9.4 | Normal(9, 1) | |
| `/sm/transport @ sm_1` | 13 | 23.2 | 7.4 | 20.7 | Normal(21, 7) | |
| `/sm/transport @ sm_2` | 8 | 14.5 | 0.3 | 14.4 | Deterministic(15) | |
| `/vgr/pick_up_and_transport @ vgr_1` | 85 | 36.6 | 13.8 | 41.6 | Normal(37, 14) | |
| `/vgr/pick_up_and_transport @ vgr_2` | 42 | 40.8 | 4.2 | 43.3 | Normal(41, 4) | |
| `/wt/pick_up_and_transport @ wt_1` | 27 | 26.2 | 0.5 | 26.0 | Normal(26, 1) | Exclude failure events |
| `/wt/pick_up_and_transport @ wt_2` | 14 | 29.5 | 0.1 | 29.5 | Deterministic(30) | |

### 6.2 Queue Time Modeling

| Resource Class | Recommended Queue Model | Parameters |
|---|---|---|
| Processing stations (mm, ov, pm, sm) | Deterministic | 5–6 seconds |
| vgr_1 | Exponential | Mean 33s (high contention) |
| vgr_2 | Exponential | Mean 10s |
| wt_1 | Exponential | Mean 13s |
| wt_2 | Deterministic | 8 seconds |
| hbw_2 (after warmup) | Exponential | Mean 17s (exclude startup) |
| hw_1 | Deterministic | 4 seconds |

### 6.3 Failure Modeling

| Activity-Resource | Failure Probability | Retry Policy |
|---|---|---|
| `/wt/pick_up_and_transport @ wt_1` | 14.8% | Retry up to 3× with increasing delay (69s, 130s) |
| `/hbw/store_empty_bucket @ hbw_2` | 5.6% | Terminal (no retry observed) |
| `/hbw/unload @ hbw_2` | 5.3% | Terminal (no retry observed) |
| `/vgr/pick_up_and_transport @ vgr_1` | 1.2% | Terminal (no retry observed) |
| All others | ~0% | N/A |

### 6.4 Resource Pooling Notes

- **mm_1 vs mm_2:** `/mm/mill` has very different durations on mm_1 (5.8s) vs mm_2 (14.4s). Do NOT pool these — they represent different milling operations.
- **vgr_1 vs vgr_2:** Similar activity but different loads. vgr_1 has higher variability (std 13.8s vs 4.2s). Keep separate in simulation.
- **wt_1 vs wt_2:** Similar durations (26.2s vs 29.5s). Can be pooled if lane constraints are relaxed.
- **sm_1 vs sm_2:** `/sm/sort` differs significantly (16.9s vs 9.4s). Keep separate.

### 6.5 Data Quality Flags

| Flag | Groups Affected |
|---|---|
| ⚠️ Outlier rate > 5% | 13 of 29 groups (many with n < 10) |
| ⚠️ Low sample (n < 5) | `/dm/cylindrical_drill`, `/dm/lower`, `/mm/mill@mm_2`, `/mm/deburr@mm_2`, `/mm/transport_from_to@mm_1`, `/mm/transport_from_to@mm_2`, `/pm/punch_gill`, `/pm/punch_recesses`, `/pm/punch_ribbing`, `/hbw/store_empty_bucket@hbw_1` |
| ⚠️ Planned time unrealistic | `/ov/burn` (222s planned vs 27–47s actual), `/hw/human_review` (102s planned vs 2–98s actual) |
| ⚠️ High variability (CV > 2) | `/hw/human_review` (CV=1.68), `/ov/burn@ov_2` (CV=1.16) |

---

*Report generated from `eventlog_cleaned.parquet` (1,383 events, 461 entities, 29 activity-resource groups). Outlier detection: IQR method, threshold 1.5×IQR.*
