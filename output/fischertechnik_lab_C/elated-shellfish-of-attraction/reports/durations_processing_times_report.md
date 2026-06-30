# Durations & Processing Times Report — Fischertechnik Lab C

## 1. Duration Computation Results

### 1.1 Methodology

Actual processing durations were computed from **start-transition events only**:

```
actual_duration = operation_end_time − time:timestamp  (where lifecycle:transition == 'start')
```

This isolates the time the resource spent actively processing each operation, excluding queueing delays (captured in `scheduled` events) and completion overhead.

### 1.2 Duration Column Summary

| Property | Value |
|---|---|
| Source column | `duration_seconds` (computed) |
| Filter | `lifecycle:transition == 'start'` only |
| Total start events | 379 |
| Valid positive durations | 379 |
| Negative durations | 0 |
| Zero durations | 0 |

### 1.3 Global Duration Statistics (All Start Events)

| Statistic | Value (seconds) |
|---|---|
| Mean | 30.45 |
| Std | 18.92 |
| Median | 26.78 |
| Min | 0.03 |
| Max | 185.06 |

### 1.4 Duration vs. Planned Time Comparison

| Metric | Planned (seconds) | Actual (seconds) | Ratio |
|---|---|---|---|
| Mean | 52.90 | 30.45 | 0.58 |
| Median | 45.00 | 26.78 | 0.60 |

**Key discrepancy:** `/ov/burn` planned time is 222s but actual observed mean is ~30.5s (ov_1: 27.3s, ov_2: 32.9s). The planned time is incorrect for the digital twin; actual observed values are used.

---

## 2. Processing Time Statistics Per Activity-Resource Pair

### 2.1 Summary Table

Outlier detection: IQR method (1.5× fence) applied per group after manual flagging of known data errors.

| Activity | Resource | Count | Clean | Mean (s) | Std (s) | Median (s) | Min (s) | Max (s) | Outlier Summary |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| /dm/cylindrical_drill | dm_2 | 2 | 2 | 42.95 | 5.48 | 42.95 | 39.08 | 46.83 | 0/2 (0.0%) |
| /dm/drill | dm_2 | 4 | 4 | 27.13 | 10.93 | 25.38 | 15.81 | 41.95 | 0/4 (0.0%) |
| /dm/lower | dm_2 | 4 | 3 | 13.84 | 0.00 | 13.84 | 13.84 | 13.84 | ⚠️ 1/4 (25.0%) |
| /hbw/get_empty_bucket | hbw_1 | 14 | 14 | 38.38 | 4.23 | 36.73 | 32.95 | 48.11 | 0/14 (0.0%) |
| /hbw/store | hbw_1 | 13 | 13 | 37.20 | 3.44 | 39.30 | 30.73 | 40.19 | 0/13 (0.0%) |
| /hbw/store_empty_bucket | hbw_2 | 34 | 34 | 37.01 | 3.70 | 36.14 | 31.73 | 44.03 | 0/34 (0.0%) |
| /hbw/unload | hbw_2 | 37 | 35 | 38.25 | 5.22 | 36.05 | 31.59 | 51.20 | ⚠️ 2/37 (5.4%) |
| /hw/human_review | hw_1 | 17 | 11 | 46.83 | 39.63 | 34.78 | 5.71 | 115.72 | ⚠️ 6/17 (35.3%) |
| /mm/deburr | mm_1 | 14 | 13 | 14.35 | 0.56 | 14.06 | 13.84 | 15.66 | ⚠️ 1/14 (7.1%) |
| /mm/deburr | mm_2 | 5 | 5 | 14.19 | 0.09 | 14.23 | 14.09 | 14.27 | 0/5 (0.0%) |
| /mm/drill | mm_2 | 8 | 7 | 11.07 | 5.53 | 14.06 | 5.08 | 16.86 | ⚠️ 1/8 (12.5%) |
| /mm/mill | mm_1 | 7 | 7 | 5.52 | 0.48 | 5.28 | 5.08 | 6.31 | 0/7 (0.0%) |
| /mm/mill | mm_2 | 4 | 4 | 14.30 | 0.21 | 14.38 | 14.02 | 14.45 | 0/4 (0.0%) |
| /mm/transport_from_to | mm_1 | 1 | 1 | 12.39 | — | 12.39 | 12.39 | 12.39 | 0/1 (0.0%) |
| /mm/transport_from_to | mm_2 | 2 | 2 | 12.33 | 0.18 | 12.33 | 12.20 | 12.45 | 0/2 (0.0%) |
| /ov/burn | ov_1 | 14 | 14 | 27.29 | 5.54 | 26.60 | 21.42 | 36.78 | 0/14 (0.0%) |
| /ov/burn | ov_2 | 18 | 18 | 32.92 | 5.36 | 31.55 | 26.44 | 41.53 | 0/18 (0.0%) |
| /ov/temper | ov_1 | 8 | 6 | 51.55 | 0.02 | 51.55 | 51.53 | 51.58 | ⚠️ 2/8 (25.0%) |
| /pm/punch_gill | pm_1 | 4 | 3 | 27.46 | 0.23 | 27.45 | 27.23 | 27.69 | ⚠️ 1/4 (25.0%) |
| /pm/punch_recesses | pm_1 | 2 | 2 | 23.75 | 0.11 | 23.75 | 23.67 | 23.83 | 0/2 (0.0%) |
| /pm/punch_ribbing | pm_1 | 2 | 2 | 23.57 | 0.32 | 23.57 | 23.34 | 23.80 | 0/2 (0.0%) |
| /sm/sort | sm_1 | 6 | 6 | 12.52 | 0.98 | 12.70 | 10.78 | 13.42 | 0/6 (0.0%) |
| /sm/sort | sm_2 | 7 | 6 | 9.45 | 0.87 | 9.47 | 8.58 | 10.38 | ⚠️ 1/7 (14.3%) |
| /sm/transport | sm_1 | 9 | 8 | 19.29 | 0.58 | 19.02 | 18.92 | 20.53 | ⚠️ 1/9 (11.1%) |
| /sm/transport | sm_2 | 10 | 10 | 14.69 | 0.27 | 14.74 | 14.22 | 14.97 | 0/10 (0.0%) |
| /vgr/pick_up_and_transport | vgr_1 | 68 | 68 | 34.47 | 14.24 | 41.77 | 10.84 | 52.20 | 0/68 (0.0%) |
| /vgr/pick_up_and_transport | vgr_2 | 36 | 36 | 39.96 | 4.18 | 40.91 | 30.48 | 46.38 | 0/36 (0.0%) |
| /wt/pick_up_and_transport | wt_1 | 14 | 14 | 26.00 | 0.08 | 26.03 | 25.81 | 26.14 | 0/14 (0.0%) |
| /wt/pick_up_and_transport | wt_2 | 15 | 15 | 29.32 | 0.13 | 29.31 | 29.09 | 29.53 | 0/15 (0.0%) |

### 2.2 Outlier Details

#### ⚠️ /dm/lower | dm_2 (1/4, 25.0%)
- **IQR outlier:** 13.828s (vs. cluster at 13.843–13.844s; difference of 0.016s)
- **Assessment:** Extremely tight cluster; the 13.828s value is technically an IQR outlier but the deviation is negligible (16ms). Likely noise, not a data error.

#### ⚠️ /hbw/unload | hbw_2 (2/37, 5.4%)
- **Flagged data errors:** 0.031s and 0.047s (near-zero durations)
- **Assessment:** These are confirmed data errors per extraction plan. Excluded from clean statistics. Remaining 35 observations show consistent processing times (31.6–51.2s, mean 38.3s).

#### ⚠️ /hw/human_review | hw_1 (6/17, 35.3%)
- **Flagged data errors:** 0.000s (×2), 0.328s, 0.765s, 0.875s — near-zero durations indicating instant reviews (data errors)
- **IQR outlier:** 185.063s (extreme high value)
- **Assessment:** 5 near-zero values are data errors (human review cannot be instantaneous). The 185s value is a legitimate IQR outlier representing an unusually long review. Clean mean: 46.8s (highly variable, CV = 0.85).

#### ⚠️ /mm/deburr | mm_1 (1/14, 7.1%)
- **IQR outlier:** 66.562s (vs. cluster at 13.8–15.7s)
- **Assessment:** Clear anomaly — 4× the normal range. Likely a data error or exceptional event. Excluded from clean statistics.

#### ⚠️ /mm/drill | mm_2 (1/8, 12.5%)
- **IQR outlier:** 32.203s (vs. cluster at 5.1–16.9s)
- **Assessment:** Note bimodal distribution: 3 values at 5.1–5.3s and 4 values at 14.1–16.9s. The 32.2s value is an outlier. The bimodality may reflect different drill types or batch sizes.

#### ⚠️ /ov/temper | ov_1 (2/8, 25.0%)
- **IQR outliers:** 51.437s and 53.000s (vs. tight cluster at 51.531–51.578s)
- **Assessment:** The 53.0s value deviates by ~1.5s from the cluster. The 51.437s is slightly below. Both are borderline; the core cluster is extremely tight (CV ≈ 0.0003).

#### ⚠️ /pm/punch_gill | pm_1 (1/4, 25.0%)
- **IQR outlier:** 23.859s (vs. cluster at 27.235–27.688s)
- **Assessment:** 3.4s below the cluster. May represent a different configuration or data error.

#### ⚠️ /sm/sort | sm_2 (1/7, 14.3%)
- **IQR outlier:** 21.266s (vs. cluster at 8.6–10.4s)
- **Assessment:** ~2× the normal range. Likely an exceptional event or data error.

#### ⚠️ /sm/transport | sm_1 (1/9, 11.1%)
- **IQR outlier:** 58.328s (vs. tight cluster at 18.9–20.5s)
- **Assessment:** ~3× the normal range. Clear anomaly.

---

## 3. Processing Time Patterns by Resource Class

### 3.1 High Bay Warehouse (hbw_1, hbw_2)

| Activity | Resource | Mean (s) | Std (s) | Count |
|---|---|---:|---:|---:|
| /hbw/unload | hbw_2 | 38.25 | 5.22 | 35 |
| /hbw/store_empty_bucket | hbw_2 | 37.01 | 3.70 | 34 |
| /hbw/get_empty_bucket | hbw_1 | 38.38 | 4.23 | 14 |
| /hbw/store | hbw_1 | 37.20 | 3.44 | 13 |

**Observation:** HBW operations are remarkably consistent across activities and resources (37–38s mean, low CV ≈ 0.1). This suggests a fixed mechanical cycle time.

### 3.2 Vacuum Gripper (vgr_1, vgr_2)

| Activity | Resource | Mean (s) | Std (s) | Count |
|---|---|---:|---:|---:|
| /vgr/pick_up_and_transport | vgr_1 | 34.47 | 14.24 | 68 |
| /vgr/pick_up_and_transport | vgr_2 | 39.96 | 4.18 | 36 |

**Observation:** vgr_1 has much higher variability (CV = 0.41) than vgr_2 (CV = 0.10). This likely reflects vgr_1's role in cross-track transport with varying distances, while vgr_2 operates on a more fixed route.

### 3.3 Oven (ov_1, ov_2)

| Activity | Resource | Mean (s) | Std (s) | Count |
|---|---|---:|---:|---:|
| /ov/burn | ov_1 | 27.29 | 5.54 | 14 |
| /ov/burn | ov_2 | 32.92 | 5.36 | 18 |
| /ov/temper | ov_1 | 51.55 | 0.02 | 6 |

**Observation:** Burn times differ between ovens (ov_1: 27.3s, ov_2: 32.9s), possibly reflecting workpiece size differences. Temper is extremely deterministic (CV ≈ 0.0003). **Note:** Actual burn mean (~30.5s) used instead of planned time (222s).

### 3.4 Milling Machine (mm_1, mm_2)

| Activity | Resource | Mean (s) | Std (s) | Count |
|---|---|---:|---:|---:|
| /mm/mill | mm_1 | 5.52 | 0.48 | 7 |
| /mm/mill | mm_2 | 14.30 | 0.21 | 4 |
| /mm/deburr | mm_1 | 14.35 | 0.56 | 13 |
| /mm/deburr | mm_2 | 14.19 | 0.09 | 5 |
| /mm/drill | mm_2 | 11.07 | 5.53 | 7 |
| /mm/transport_from_to | mm_1 | 12.39 | — | 1 |
| /mm/transport_from_to | mm_2 | 12.33 | 0.18 | 2 |

**Observation:** Mill times differ significantly between mm_1 (5.5s) and mm_2 (14.3s), suggesting different mill configurations. Deburr is consistent across both machines (~14.2s). Drill on mm_2 shows bimodality (possible different drill types).

### 3.5 Sorting Machine (sm_1, sm_2)

| Activity | Resource | Mean (s) | Std (s) | Count |
|---|---|---:|---:|---:|
| /sm/sort | sm_1 | 12.52 | 0.98 | 6 |
| /sm/sort | sm_2 | 9.45 | 0.87 | 6 |
| /sm/transport | sm_1 | 19.29 | 0.58 | 8 |
| /sm/transport | sm_2 | 14.69 | 0.27 | 10 |

**Observation:** Sort and transport times differ between sm_1 and sm_2, possibly reflecting different downstream routing distances.

### 3.6 Wheel Transporter (wt_1, wt_2)

| Activity | Resource | Mean (s) | Std (s) | Count |
|---|---|---:|---:|---:|
| /wt/pick_up_and_transport | wt_1 | 26.00 | 0.08 | 14 |
| /wt/pick_up_and_transport | wt_2 | 29.32 | 0.13 | 15 |

**Observation:** Extremely deterministic (CV < 0.005). Fixed transport cycle times.

### 3.7 Human Workstation (hw_1)

| Activity | Resource | Mean (s) | Std (s) | Count |
|---|---|---:|---:|---:|
| /hw/human_review | hw_1 | 46.83 | 39.63 | 11 |

**Observation:** Highly variable (CV = 0.85) after removing 6 data errors. Range: 5.7–115.7s. This variability is expected for human tasks.

### 3.8 Punch Machine (pm_1)

| Activity | Resource | Mean (s) | Std (s) | Count |
|---|---|---:|---:|---:|
| /pm/punch_gill | pm_1 | 27.46 | 0.23 | 3 |
| /pm/punch_recesses | pm_1 | 23.75 | 0.11 | 2 |
| /pm/punch_ribbing | pm_1 | 23.57 | 0.32 | 2 |

**Observation:** Very low variability within each activity type. Punch gill takes longer (~27.5s) than recesses/ribbing (~23.6s), consistent with different batch quantities (gill: 8, recesses: 6, ribbing: 6).

### 3.9 Drill Machine (dm_2)

| Activity | Resource | Mean (s) | Std (s) | Count |
|---|---|---:|---:|---:|
| /dm/cylindrical_drill | dm_2 | 42.95 | 5.48 | 2 |
| /dm/drill | dm_2 | 27.13 | 10.93 | 4 |
| /dm/lower | dm_2 | 13.84 | 0.00 | 3 |

**Observation:** Cylindrical drill is longest (43s), drill is intermediate (27s), lower is shortest (14s). Consistent with batch quantities (cylindrical_drill: 8, drill: 6, lower: not batched).

---

## 4. Data Quality Flags

### 4.1 Groups with Outlier Rate > 5%

| Activity | Resource | Outlier Rate | Issue |
|---|---|---:|---|
| ⚠️ /hw/human_review | hw_1 | 35.3% | 5 near-zero data errors + 1 extreme high outlier |
| ⚠️ /dm/lower | dm_2 | 25.0% | 1 IQR outlier (negligible 16ms deviation) |
| ⚠️ /ov/temper | ov_1 | 25.0% | 2 borderline outliers in tight cluster |
| ⚠️ /pm/punch_gill | pm_1 | 25.0% | 1 outlier 3.4s below cluster |
| ⚠️ /mm/drill | mm_2 | 12.5% | 1 outlier + bimodal distribution |
| ⚠️ /sm/sort | sm_2 | 14.3% | 1 outlier at 2× normal range |
| ⚠️ /sm/transport | sm_1 | 11.1% | 1 outlier at 3× normal range |
| ⚠️ /mm/deburr | mm_1 | 7.1% | 1 outlier at 4× normal range |
| ⚠️ /hbw/unload | hbw_2 | 5.4% | 2 near-zero data errors |

### 4.2 Known Data Errors (Manually Flagged)

| Activity | Resource | Values (s) | Action |
|---|---|---|---|
| /hbw/unload | hbw_2 | 0.031, 0.047 | Excluded (confirmed data errors) |
| /hw/human_review | hw_1 | 0.000 (×2), 0.328, 0.765, 0.875 | Excluded (instant reviews are impossible) |

### 4.3 Small Sample Warnings

Groups with fewer than 5 clean observations:

| Activity | Resource | Clean Count | Warning |
|---|---|---:|---|
| /dm/cylindrical_drill | dm_2 | 2 | ⚠️ Very small sample |
| /dm/drill | dm_2 | 4 | Small sample |
| /dm/lower | dm_2 | 3 | Small sample |
| /mm/mill | mm_2 | 4 | Small sample |
| /mm/transport_from_to | mm_1 | 1 | ⚠️ Single observation |
| /mm/transport_from_to | mm_2 | 2 | ⚠️ Very small sample |
| /pm/punch_recesses | pm_1 | 2 | ⚠️ Very small sample |
| /pm/punch_ribbing | pm_1 | 2 | ⚠️ Very small sample |

---

## 5. Key Findings for DES Parameterization

1. **Use actual observed durations**, not planned times. The `/ov/burn` planned time (222s) is ~7× the actual observed mean (~30.5s).

2. **Most processing times are deterministic** (CV < 0.1) for mechanical operations: wt (CV < 0.005), ov/temper (CV ≈ 0.0003), mm/deburr (CV ≈ 0.04), hbw operations (CV ≈ 0.1).

3. **High variability activities:** `/hw/human_review` (CV = 0.85), `/vgr/pick_up_and_transport` on vgr_1 (CV = 0.41), `/ov/burn` (CV ≈ 0.18).

4. **Bimodal distributions:** `/mm/drill` on mm_2 shows two clusters (5s and 15s), suggesting different drill configurations.

5. **Resource-specific differences:** `/ov/burn` differs between ov_1 (27.3s) and ov_2 (32.9s); `/mm/mill` differs between mm_1 (5.5s) and mm_2 (14.3s).

6. **Batch operations:** pm and dm activities process multiple units per operation. Per-unit times would be obtained by dividing by batch quantity (e.g., pm/punch_gill: 27.5s / 8 units = 3.4s per unit).

---

*Report generated from `eventlog_cleaned.parquet` (1,137 rows, 379 start events, 29 activity-resource pairs, 15 resources)*
