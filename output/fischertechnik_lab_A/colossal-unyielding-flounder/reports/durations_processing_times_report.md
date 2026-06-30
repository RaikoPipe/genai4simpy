# Durations & Processing Times Report

## 1. Duration Computation

### Method

Duration was computed as `operation_end_time − time:timestamp` for all 576 rows. For DES parameter extraction, **only `start` lifecycle transitions** are used (192 rows), because they represent the actual service time from when the resource begins work until the scheduled completion.

### Summary Statistics (All Lifecycle Transitions)

| Statistic | Value |
|---|---|
| Total rows | 576 |
| Valid durations | 576 |
| Zero durations | 161 (scheduled/complete events with no work) |
| Positive durations | 415 |
| Mean | 51.90s |
| Median | 15.34s |
| Std | 155.79s |
| Min | 0.02s |
| Max | 1252.91s |

### Summary Statistics (Start Transitions Only)

| Statistic | Value |
|---|---|
| Total start rows | 192 |
| After excluding incomplete cases | 183 |
| Zero/negative durations | 0 |
| Mean | 31.95s |
| Median | 33.08s |
| Std | 21.76s |
| Min | 0.02s |
| Max | 245.70s |

**Note:** 4 incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) are excluded from all processing time extraction below.

---

## 2. Processing Times by Activity-Resource Pair

Processing times are extracted from `start` transitions only, with IQR-based outlier detection (k=1.5). Incomplete cases excluded.

### 2.1 Machine Processing Activities

| Activity | Resource | Count | Count Clean | Mean (s) | Std (s) | Median (s) | Outlier Summary |
|---|---|---|---|---|---|---|---|
| `/mm/mill` | mm_1 | 5 | 4 | 5.08 | 0.03 | 5.07 | 1/5 (20.0%) ⚠️ |
| `/mm/mill` | mm_2 | 1 | 1 | 14.44 | — | 14.44 | 0/1 (0.0%) |
| `/mm/deburr` | mm_1 | 8 | 8 | 14.49 | 0.38 | 14.42 | 0/8 (0.0%) |
| `/mm/deburr` | mm_2 | 1 | 1 | 14.24 | — | 14.24 | 0/1 (0.0%) |
| `/mm/drill` | mm_1 | 1 | 1 | 20.91 | — | 20.91 | 0/1 (0.0%) |
| `/mm/drill` | mm_2 | 3 | 3 | 12.29 | 6.07 | 15.52 | 0/3 (0.0%) |
| `/mm/transport_from_to` | mm_2 | 2 | 2 | 12.87 | 0.39 | 12.87 | 0/2 (0.0%) |
| `/ov/burn` | ov_1 | 8 | 8 | 27.20 | 5.67 | 26.52 | 0/8 (0.0%) |
| `/ov/burn` | ov_2 | 4 | 4 | 34.34 | 6.41 | 34.35 | 0/4 (0.0%) |
| `/ov/temper` | ov_1 | 5 | 3 | 51.54 | 0.01 | 51.55 | 2/5 (40.0%) ⚠️ |
| `/sm/sort` | sm_1 | 4 | 4 | 11.70 | 2.28 | 12.14 | 0/4 (0.0%) |
| `/sm/sort` | sm_2 | 2 | 2 | 127.03 | 167.82 | 127.03 | 0/2 (0.0%) |
| `/sm/transport` | sm_1 | 5 | 5 | 19.92 | 1.41 | 19.41 | 0/5 (0.0%) |
| `/sm/transport` | sm_2 | 4 | 4 | 14.53 | 0.13 | 14.54 | 0/4 (0.0%) |
| `/dm/lower` | dm_2 | 2 | 2 | 14.01 | 0.19 | 14.01 | 0/2 (0.0%) |
| `/dm/cylindrical_drill` | dm_2 | 2 | 2 | 23.99 | 2.86 | 23.99 | 0/2 (0.0%) |
| `/pm/punch_gill` | pm_1 | 1 | 1 | 27.48 | — | 27.48 | 0/1 (0.0%) |
| `/pm/punch_recesses` | pm_1 | 2 | 2 | 23.64 | 0.27 | 23.64 | 0/2 (0.0%) |
| `/pm/punch_ribbing` | pm_1 | 2 | 2 | 27.39 | 5.41 | 27.39 | 0/2 (0.0%) |

### 2.2 Warehouse Activities

| Activity | Resource | Count | Count Clean | Mean (s) | Std (s) | Median (s) | Outlier Summary |
|---|---|---|---|---|---|---|---|
| `/hbw/unload` | hbw_2 | 13 | 10 | 35.89 | 2.34 | 36.37 | 3/13 (23.1%) ⚠️ |
| `/hbw/store_empty_bucket` | hbw_2 | 13 | 12 | 38.64 | 3.46 | 38.49 | 1/13 (7.7%) ⚠️ |
| `/hbw/get_empty_bucket` | hbw_1 | 11 | 7 | 36.16 | 0.65 | 36.22 | 4/11 (36.4%) ⚠️ |
| `/hbw/store` | hbw_1 | 3 | 3 | 37.98 | 3.95 | 36.97 | 0/3 (0.0%) |

### 2.3 Human Workstation

| Activity | Resource | Count | Count Clean | Mean (s) | Std (s) | Median (s) | Outlier Summary |
|---|---|---|---|---|---|---|---|
| `/hw/human_review` | hw_1 | 14 | 12 | 7.16 | 8.35 | 2.79 | 2/14 (14.3%) ⚠️ |

### 2.4 Transport Activities

| Activity | Resource | Count | Count Clean | Mean (s) | Std (s) | Median (s) | Outlier Summary |
|---|---|---|---|---|---|---|---|
| `/vgr/pick_up_and_transport` | vgr_1 | 37 | 37 | 40.20 | 16.21 | 41.56 | 0/37 (0.0%) |
| `/vgr/pick_up_and_transport` | vgr_2 | 16 | 16 | 40.85 | 3.76 | 43.41 | 0/16 (0.0%) |
| `/wt/pick_up_and_transport` | wt_1 | 8 | 8 | 26.09 | 0.18 | 26.05 | 0/8 (0.0%) |
| `/wt/pick_up_and_transport` | wt_2 | 6 | 6 | 29.09 | 0.16 | 29.15 | 0/6 (0.0%) |

---

## 3. Pooled Processing Times (Identical Hardware, Same Activity)

Per the extraction plan, identical hardware performing the same activity is pooled. **Never pool across different activities.**

### 3.1 Mill Machines (mm_1 + mm_2)

| Activity | Pooled Count | Count Clean | Mean (s) | Std (s) | Median (s) | Outlier Summary |
|---|---|---|---|---|---|---|
| `/mm/mill` | 6 | 5 | 5.12 | 0.10 | 5.08 | 1/6 (16.7%) ⚠️ |
| `/mm/deburr` | 9 | 9 | 14.46 | 0.36 | 14.41 | 0/9 (0.0%) |
| `/mm/drill` | 4 | 3 | 17.49 | 2.97 | 16.06 | 1/4 (25.0%) ⚠️ |

**Notes:**
- `/mm/mill`: The mm_2 observation (14.44s) is a clear outlier vs mm_1 (5.05–5.28s). Investigation reveals mm_2's mill includes transport to sm_2_lb_1_pos (end_position differs), while mm_1 mill stays at mm_1_initial_pos. **These are NOT comparable** — mm_2's `/mm/mill` includes an internal transport component. Do NOT pool `/mm/mill` across mm_1/mm_2.
- `/mm/deburr`: Consistent across both machines (14.24–14.50s). Pooling is valid.
- `/mm/drill`: Sparse data (1 on mm_1, 3 on mm_2). The mm_2 value of 5.28s is flagged as outlier. Insufficient data to confirm pooling.

### 3.2 Ovens (ov_1 + ov_2)

| Activity | Pooled Count | Count Clean | Mean (s) | Std (s) | Median (s) | Outlier Summary |
|---|---|---|---|---|---|---|
| `/ov/burn` | 12 | 12 | 29.58 | 6.63 | 29.23 | 0/12 (0.0%) |

**Note:** ov_1 (n=8, mean=27.20s) and ov_2 (n=4, mean=34.34s) show a ~7s difference. This may reflect workpiece size/thickness differences rather than hardware differences. Pooling is acceptable but flagged for revisit.

### 3.3 Sorting Machines (sm_1 + sm_2)

| Activity | Pooled Count | Count Clean | Mean (s) | Std (s) | Median (s) | Outlier Summary |
|---|---|---|---|---|---|---|
| `/sm/sort` | 6 | 5 | 11.03 | 2.48 | 11.67 | 1/6 (16.7%) ⚠️ |
| `/sm/transport` | 9 | 9 | 17.52 | 3.01 | 18.25 | 0/9 (0.0%) |

**Notes:**
- `/sm/sort`: The sm_2 observation of 245.70s (WF_108_17) is a massive outlier vs the other 5 observations (8.36–13.95s). This is likely a data artifact (possibly includes queueing/waiting). After removing it, pooled mean is ~10.5s. **Flagged for manual review.**
- `/sm/transport`: sm_1 (mean=19.92s) and sm_2 (mean=14.53s) differ by ~5.4s. This likely reflects different physical distances (sm_1_corner_pos vs sm_2_corner_pos destinations). Pooling is questionable — flag for revisit.

### 3.4 VGR Transport (vgr_1 + vgr_2)

| Activity | Pooled Count | Count Clean | Mean (s) | Std (s) | Median (s) | Outlier Summary |
|---|---|---|---|---|---|---|
| `/vgr/pick_up_and_transport` | 53 | 40 | 42.12 | 6.58 | 42.79 | 13/53 (24.5%) ⚠️ |

**Note:** Pooling vgr_1 and vgr_2 produces high outlier rates because they serve **different routes with different distances**. vgr_2 serves short routes (hbw_2→ov_2: 36.6s, hbw_2→dm_2: 43.4s), while vgr_1 serves many longer routes (dm_2→ov_1: 53.9s, dm_2→hw_1: 51.7s) and some short ones (hw_1→hbw_1_waiting: 25.2s, hbw_1_waiting→hbw_1: 20.8s).

**Recommendation: Do NOT pool VGR transport times.** Use per-route distributions instead. Flag for revisit at modeling stage.

### 3.5 Work Transport (wt_1 + wt_2)

| Activity | Pooled Count | Count Clean | Mean (s) | Std (s) | Median (s) | Outlier Summary |
|---|---|---|---|---|---|---|
| `/wt/pick_up_and_transport` | 14 | 14 | 27.38 | 1.55 | 26.36 | 0/14 (0.0%) |

**Note:** wt_1 (ov_1→mm_1: mean=26.09s) and wt_2 (ov_2→mm_2: mean=29.09s) differ by ~3s. Both have very low variance (std < 0.2s). The difference likely reflects physical distance. Pooling is acceptable but flagged for revisit.

---

## 4. VGR Transport Route Breakdown

Since VGR transport times vary significantly by route, per-route statistics are provided:

### 4.1 vgr_1 Routes

| Start Position | End Position | Count | Mean (s) | Std (s) | Median (s) |
|---|---|---|---|---|---|
| dm_2_sink_pos | hw_1_pos | 5 | 51.75 | 13.37 | 46.81 |
| dm_2_sink_pos | ov_1_pos | 9 | 53.87 | 14.00 | 51.03 |
| hw_1_pos | hbw_1_waiting_platform_pos | 11 | 25.24 | 8.14 | 20.81 |
| hbw_1_waiting_platform_pos | hbw_1_pos | 3 | 20.82 | 6.68 | 24.53 |
| pm_1_sink_pos | hw_1_pos | 5 | 48.29 | 6.26 | 48.49 |
| sm_1_sink_1_pos | hw_1_pos | 1 | 39.58 | — | 39.58 |
| sm_1_sink_2_pos | hw_1_pos | 1 | 41.42 | — | 41.42 |
| sm_1_sink_3_pos | hw_1_pos | 2 | 40.68 | 1.91 | 40.68 |

### 4.2 vgr_2 Routes

| Start Position | End Position | Count | Mean (s) | Std (s) | Median (s) |
|---|---|---|---|---|---|
| hbw_2_pos | dm_2_sink_pos | 8 | 43.41 | 2.23 | 44.07 |
| hbw_2_pos | ov_2_pos | 6 | 36.56 | 0.55 | 36.60 |
| sm_2_sink_1_pos | dm_2_sink_pos | 1 | 43.63 | — | 43.63 |
| sm_2_sink_2_pos | dm_2_sink_pos | 1 | 43.25 | — | 43.25 |

---

## 5. Outlier Analysis & Data Quality Flags

### 5.1 Groups with High Outlier Rates (>5%)

| Activity | Resource | Outlier Rate | Issue |
|---|---|---|---|
| `/ov/temper` | ov_1 | 40.0% ⚠️ | IQR flags 2 of 5 nearly-identical values (51.45–51.61s) as outliers due to tiny IQR. Not a real issue — temper is extremely consistent (~51.5s). |
| `/hbw/get_empty_bucket` | hbw_1 | 36.4% ⚠️ | 4 outliers among 11 samples. Values range 30.8–48.6s. Some may reflect queueing at hbw_1. |
| `/hbw/unload` | hbw_2 | 23.1% ⚠️ | 3 outliers (45.98–52.25s) among 13 samples. Core values cluster at 32.7–38.7s. |
| `/hbw/store_empty_bucket` | hbw_2 | 7.7% ⚠️ | 1 outlier (65.14s) among 13 samples. |
| `/hw/human_review` | hw_1 | 14.3% ⚠️ | 2 outliers (47.77s, 62.25s) among 14 samples. Core values cluster at 0.44–17.97s. Human review is highly variable. |
| `/mm/mill` | mm_1 | 20.0% ⚠️ | 1 outlier (5.28s) among 5 samples. Very tight distribution (5.05–5.28s); IQR artifact. |
| `/sm/sort` (pooled) | sm_1+sm_2 | 16.7% ⚠️ | sm_2 observation of 245.70s is a massive outlier. Likely data artifact. |
| `/mm/drill` (pooled) | mm_1+mm_2 | 25.0% ⚠️ | Sparse data; 1 outlier (5.28s) among 4 samples. |
| `/vgr/pick_up_and_transport` (pooled) | vgr_1+vgr_2 | 24.5% ⚠️ | Route-dependent distances create apparent outliers when pooled. |

### 5.2 Known Data Anomalies

1. **sm_2 `/sm/sort` (WF_108_17):** 245.70s duration is ~20× the normal sort time (~10s). This is likely a data artifact where the operation_end_time includes waiting time. **Recommendation:** Exclude from distribution fitting; use sm_1 data as proxy.

2. **mm_2 `/mm/mill` (WF_104_20):** 14.44s vs mm_1's ~5.1s. Investigation shows mm_2's mill includes transport to sm_2_lb_1_pos, while mm_1's mill stays in place. **Recommendation:** Do NOT pool mm_1/mm_2 for `/mm/mill`.

3. **`/ov/temper` IQR artifacts:** All 5 values are within 0.16s of each other (51.45–51.61s). The tiny IQR causes IQR method to flag values as outliers. **Recommendation:** Model as fixed value ~51.5s.

4. **`/hw/human_review` high variance:** Ranges from 0.44s to 62.25s. Two extreme values (47.77s, 62.25s) may include waiting for human availability. **Recommendation:** Model with heavy-tailed distribution or separate queueing.

---

## 6. Recommended DES Parameters

### 6.1 Processing Times (Per Activity, Cleaned)

| Activity | Resource(s) | Recommended Mean (s) | Notes |
|---|---|---|---|
| `/mm/mill` | mm_1 | 5.08 | Very low variance (std=0.03s). Near-fixed. |
| `/mm/mill` | mm_2 | 14.44 | Single observation. Includes transport. |
| `/mm/deburr` | mm_1, mm_2 | 14.46 | Pooled. Very low variance (std=0.36s). |
| `/mm/drill` | mm_1, mm_2 | Insufficient data | n=4, high variance. Flag for expert estimation. |
| `/mm/transport_from_to` | mm_2 | 12.87 | Low variance (std=0.39s). |
| `/ov/burn` | ov_1, ov_2 | 29.58 | Pooled. Moderate variance (std=6.63s). |
| `/ov/temper` | ov_1 | 51.54 | Near-fixed (std=0.06s). |
| `/sm/sort` | sm_1 | 11.70 | Exclude sm_2 anomaly. |
| `/sm/transport` | sm_1 | 19.92 | Different from sm_2 (14.53s). Route-dependent. |
| `/sm/transport` | sm_2 | 14.53 | Very low variance (std=0.13s). |
| `/dm/lower` | dm_2 | 14.01 | Very low variance (std=0.19s). |
| `/dm/cylindrical_drill` | dm_2 | 23.99 | Low variance (std=2.86s). |
| `/pm/punch_gill` | pm_1 | 27.48 | Single observation. |
| `/pm/punch_recesses` | pm_1 | 23.64 | Low variance (std=0.27s). |
| `/pm/punch_ribbing` | pm_1 | 27.39 | Moderate variance (std=5.41s). |
| `/hbw/unload` | hbw_2 | 35.89 | After removing 3 outliers. |
| `/hbw/store_empty_bucket` | hbw_2 | 38.64 | After removing 1 outlier. |
| `/hbw/get_empty_bucket` | hbw_1 | 36.16 | After removing 4 outliers. |
| `/hbw/store` | hbw_1 | 37.98 | n=3 only. |
| `/hw/human_review` | hw_1 | 2.79 (median) | Highly variable. Use median, not mean. |

### 6.2 Transport Times (Per Route)

| Route | Resource | Mean (s) | Std (s) | Count |
|---|---|---|---|---|
| hbw_2→dm_2 | vgr_2 | 43.41 | 2.23 | 8 |
| hbw_2→ov_2 | vgr_2 | 36.56 | 0.55 | 6 |
| sm_2_sink→dm_2 | vgr_2 | 43.44 | 0.27 | 2 |
| dm_2→ov_1 | vgr_1 | 53.87 | 14.00 | 9 |
| dm_2→hw_1 | vgr_1 | 51.75 | 13.37 | 5 |
| pm_1→hw_1 | vgr_1 | 48.29 | 6.26 | 5 |
| sm_1_sink→hw_1 | vgr_1 | 40.43 | 0.95 | 4 |
| hw_1→hbw_1_waiting | vgr_1 | 25.24 | 8.14 | 11 |
| hbw_1_waiting→hbw_1 | vgr_1 | 20.82 | 6.68 | 3 |
| ov_1→mm_1 | wt_1 | 26.09 | 0.18 | 8 |
| ov_2→mm_2 | wt_2 | 29.09 | 0.16 | 6 |

---

## 7. Sample Size Warnings

Groups with fewer than 5 observations should be treated with caution:

| Activity | Resource | Count | Risk |
|---|---|---|---|
| `/mm/mill` | mm_2 | 1 | Very high — single observation |
| `/mm/deburr` | mm_2 | 1 | Very high — single observation |
| `/mm/drill` | mm_1 | 1 | Very high — single observation |
| `/pm/punch_gill` | pm_1 | 1 | Very high — single observation |
| `/dm/lower` | dm_2 | 2 | High |
| `/dm/cylindrical_drill` | dm_2 | 2 | High |
| `/pm/punch_recesses` | pm_1 | 2 | High |
| `/pm/punch_ribbing` | pm_1 | 2 | High |
| `/mm/transport_from_to` | mm_2 | 2 | High |
| `/hbw/store` | hbw_1 | 3 | High |
| `/sm/sort` | sm_2 | 2 | High (plus anomaly) |
| VGR sm_1_sink_1→hw_1 | vgr_1 | 1 | Very high |
| VGR sm_1_sink_2→hw_1 | vgr_1 | 1 | Very high |
| VGR sm_2_sink→dm_2 | vgr_2 | 1 each | Very high |

---

## 8. Summary of Key Findings

1. **Processing times are remarkably consistent** for most machine activities (std < 1s for mill, deburr, temper, transport). This suggests deterministic or near-deterministic processing.

2. **VGR transport times are route-dependent** and should NOT be pooled. Use per-route distributions.

3. **Work transport times are consistent** within each route but differ between wt_1 (26.1s) and wt_2 (29.1s) due to physical distance.

4. **Human review is highly variable** (0.44–62.25s) and should be modeled with a heavy-tailed distribution or separate queueing mechanism.

5. **Several data anomalies** require manual review: sm_2 sort (245.7s), mm_2 mill (14.4s vs 5.1s), and hbw_1 get_empty_bucket outliers.

6. **Many activity-resource pairs have very few observations** (n=1–3). Distribution fitting for these groups will have wide confidence intervals and should be flagged for expert estimation.
