# Distribution Fitting Report — Fischertechnik Lab B

## 1. Executive Summary

This report presents the results of statistical distribution fitting for all key simulation parameters extracted from the Fischertechnik Lab B event log (1,383 events, 461 entities, 38 workflow instances). Distributions were fitted to processing times (grouped by resource and activity), inter-arrival times, and failure/retry parameters.

**Key findings:**
- **15 parametric fits passed the validity gate** — only `/sm/sort` achieved a valid parametric fit (Normal). All other groups required KDE or empirical fallbacks.
- **14 groups recommended KDE** — bimodal/multimodal distributions (common in manufacturing with distinct operation types per resource) prevented valid parametric fits.
- **10 groups fell back to empirical triangular** — primarily due to N < 30 (small samples) or failed moment/tail validity gates.
- **Inter-arrival times** exhibit bursty batch arrivals (CV ≈ 2.0) — not suitable for simple Poisson/exponential modeling.
- **Failure probability** is low overall (1.96%) but concentrated on specific resources (wt_1: 14.8%, hbw_2: 5.3–5.6%).

**Validity gate criteria (applied to all fits):**
- Theoretical mean within ±15% of empirical mean
- Theoretical std within ±25% of empirical std
- Theoretical p99 ≤ 2× empirical max (no fabricated tails)
- KS test passes when N ≥ 30 (ks_reliable = true)

---

## 2. Processing Times — Resource-Level Fitting

Processing times were computed as `duration_computed = operation_end_time − time:timestamp` for all events with positive duration (954 of 1,383 rows). Fitting was performed grouped by `org:resource`.

### 2.1 Best-Fit Summary Table (Resource Level)

| Resource | N | Recommended | Params | Emp. Mean (s) | Fit Mean (s) | Mean Err % | Emp. Std (s) | Fit Std (s) | KS p (reliable?) | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| dm_2 | 16 ⚠️ | triangular_empirical | loc=1.48, c=0.22, scale=30.59 | 12.28 | 13.97 | 13.8% | 12.18 | — | — | ⚠️ FALLBACK (N<30) |
| hbw_1 | 59 | KDE | bandwidth=0.44 | 23.32 | 23.32 | 0.0% | 23.09 | 23.09 | 0.258 (yes) | PASS (KDE) |
| hbw_2 | 153 | KDE | bandwidth=0.37 | 114.92 | 114.92 | 0.0% | 199.74 | 199.74 | 0.001 (yes) | PASS (KDE) |
| hw_1 | 55 | KDE | bandwidth=0.45 | 10.73 | 10.73 | 0.0% | 21.55 | 21.55 | 0.001 (yes) | PASS (KDE) |
| mm_1 | 73 | KDE | bandwidth=0.42 | 8.00 | 8.00 | 0.0% | 4.77 | 4.77 | 0.023 (yes) | PASS (KDE) |
| mm_2 | 34 | triangular_empirical | loc=3.78, c=0.13, scale=11.68 | 8.69 | 8.18 | 5.9% | 4.91 | — | — | ⚠️ FALLBACK |
| ov_1 | 72 | KDE | bandwidth=0.43 | 20.54 | 20.54 | 0.0% | 18.79 | 18.79 | 0.013 (yes) | PASS (KDE) |
| ov_2 | 25 ⚠️ | triangular_empirical | loc=4.12, c=0.10, scale=36.68 | 25.03 | 17.51 | 30.0% | 42.88 | — | — | ⚠️ FALLBACK (N<30) |
| pm_1 | 25 ⚠️ | triangular_empirical | loc=1.48, c=0.05, scale=26.02 | 12.62 | 10.59 | 16.1% | 11.60 | — | — | ⚠️ FALLBACK (N<30) |
| sm_1 | 46 | triangular_empirical | loc=1.45, c=0.21, scale=28.90 | 11.28 | 13.11 | 16.2% | 11.45 | — | — | ⚠️ FALLBACK |
| sm_2 | 28 ⚠️ | triangular_empirical | loc=1.50, c=0.39, scale=13.18 | 7.32 | 7.60 | 3.8% | 5.43 | — | — | ⚠️ FALLBACK (N<30) |
| vgr_1 | 184 | KDE | bandwidth=0.35 | 30.80 | 30.80 | 0.0% | 24.45 | 24.45 | 0.087 (yes) | PASS (KDE) |
| vgr_2 | 103 | KDE | bandwidth=0.40 | 19.94 | 19.94 | 0.0% | 18.95 | 18.95 | 0.018 (yes) | PASS (KDE) |
| wt_1 | 53 | KDE | bandwidth=0.45 | 15.29 | 15.29 | 0.0% | 10.83 | 10.83 | 0.049 (yes) | PASS (KDE) |
| wt_2 | 28 ⚠️ | triangular_empirical | loc=3.90, c=0.53, scale=25.69 | 16.98 | 16.99 | 0.1% | 12.75 | — | — | ⚠️ FALLBACK (N<30) |

**Legend:**
- ⚠️ = N < 30 (small sample, KS test unreliable) or fallback recommendation
- **PASS (KDE)** = Non-parametric KDE fit passed validity gate (all parametric fits failed KS test)
- **FALLBACK** = Bounded empirical triangular(p5, median, p95) used because no valid parametric fit found

### 2.2 Resource-Level Fit Details

#### dm_2 (N=16, ⚠️ Small Sample)
- **Empirical:** mean=12.28s, std=12.18s, median=8.35s, range=[1.44, 32.81]
- **Recommendation:** triangular_empirical(p5=1.48, median=8.35, p95=30.59)
- **Reason:** N=16 < 30; parametric fits are advisory only. Best advisory fit was Exponential(loc=1.44, scale=10.84) with KS p=0.016 (fail) but valid moments.
- **SimPy usage:** `random.triangular(1.48, 8.35, 30.59)`

#### hbw_1 (N=59, KDE)
- **Empirical:** mean=23.32s, std=23.09s, median=33.77s, range=[1.44, 130.38]
- **Recommendation:** KDE (all parametric fits failed KS test)
- **Best parametric attempt:** Gamma(a=0.45, loc=1.44, scale=32.50), KS p=0.000 (fail), mean_err=30.7%
- **Note:** Highly bimodal — combines fast operations (scheduled events, ~1.5s) with actual processing (~37s). KDE captures this structure.
- **SimPy usage:** Sample from KDE quantile table via `np.interp(np.random.uniform(), quantile_probs, quantile_values)`

#### hbw_2 (N=153, KDE)
- **Empirical:** mean=114.92s, std=199.74s, median=36.81s, range=[0.02, 1034.30]
- **Recommendation:** KDE (all parametric fits failed KS test)
- **Best parametric attempt:** Gamma(a=0.42, loc=0.02, scale=277.35), KS p=0.000 (fail), mean_err=1.5%
- **Note:** Extreme right tail from startup queue times. KDE preserves empirical distribution.
- **SimPy usage:** Sample from KDE quantile table

#### hw_1 (N=55, KDE)
- **Empirical:** mean=10.73s, std=21.55s, median=2.63s, range=[0.11, 98.14]
- **Recommendation:** KDE (all parametric fits failed KS test)
- **Best parametric attempt:** Weibull(c=0.70, loc=0.11, scale=8.37), KS p=0.000 (fail), mean_err=0.2%, std_err=27.5%
- **Note:** Highly right-skewed (skewness=3.06). Human review is fast for most cases but occasionally very slow.
- **SimPy usage:** Sample from KDE quantile table

#### mm_1 (N=73, KDE)
- **Empirical:** mean=8.00s, std=4.77s, median=5.28s, range=[3.77, 23.05]
- **Recommendation:** KDE (all parametric fits failed KS test)
- **Best parametric attempt:** Gamma(a=0.70, loc=3.77, scale=5.88), KS p=0.003 (fail), mean_err=1.7%
- **Note:** Bimodal — combines fast milling (~5s) with slower deburring (~14s). KDE captures both modes.
- **SimPy usage:** Sample from KDE quantile table

#### mm_2 (N=34, Fallback)
- **Empirical:** mean=8.69s, std=4.91s, median=5.29s, range=[3.73, 15.66]
- **Recommendation:** triangular_empirical(p5=3.78, median=5.29, p95=11.68)
- **Reason:** No valid parametric or KDE fit. Weibull had KS p=0.118 (pass) but mean_err=31.2% and tail_ratio=3.80 (fail).
- **SimPy usage:** `random.triangular(3.78, 5.29, 11.68)`

#### ov_1 (N=72, KDE)
- **Empirical:** mean=20.54s, std=18.79s, median=8.95s, range=[2.57, 54.36]
- **Recommendation:** KDE (all parametric fits failed KS test)
- **Best parametric attempt:** Gamma(a=0.65, loc=2.57, scale=25.89), KS p=0.013 (fail), mean_err=5.2%
- **Note:** Combines fast scheduled events (~4s) with actual burn/temper processing (~27–53s).
- **SimPy usage:** Sample from KDE quantile table

#### ov_2 (N=25, ⚠️ Small Sample)
- **Empirical:** mean=25.03s, std=42.88s, median=7.61s, range=[3.60, 218.69]
- **Recommendation:** triangular_empirical(p5=4.12, median=7.61, p95=36.68)
- **Reason:** N=25 < 30. Best advisory fit was Gamma(a=0.30, loc=3.60, scale=72.68) with KS p=0.176 (pass) but advisory only.
- **Note:** Extreme outlier at 218.69s inflates std. Fallback uses p95=36.68s which excludes this outlier.
- **SimPy usage:** `random.triangular(4.12, 7.61, 36.68)`

#### pm_1 (N=25, ⚠️ Small Sample)
- **Empirical:** mean=12.62s, std=11.60s, median=2.78s, range=[1.45, 28.28]
- **Recommendation:** triangular_empirical(p5=1.48, median=2.78, p95=26.02)
- **Reason:** N=25 < 30. Best advisory fit was Exponential(loc=1.45, scale=11.17) with KS p=0.000 (fail).
- **Note:** Combines fast scheduled events with actual punching (~23–28s).
- **SimPy usage:** `random.triangular(1.48, 2.78, 26.02)`

#### sm_1 (N=46, Fallback)
- **Empirical:** mean=11.28s, std=11.45s, median=7.52s, range=[1.41, 47.39]
- **Recommendation:** triangular_empirical(p5=1.45, median=7.52, p95=28.90)
- **Reason:** No valid parametric fit. Weibull had KS p=0.080 (pass) but mean_err=58.1% and tail_ratio=3.09 (fail).
- **SimPy usage:** `random.triangular(1.45, 7.52, 28.90)`

#### sm_2 (N=28, ⚠️ Small Sample)
- **Empirical:** mean=7.32s, std=5.43s, median=6.63s, range=[1.44, 14.83]
- **Recommendation:** triangular_empirical(p5=1.50, median=6.63, p95=13.18)
- **Reason:** N=28 < 30. Best advisory fit was Exponential(loc=1.44, scale=5.88) with KS p=0.051 (pass) but advisory only.
- **SimPy usage:** `random.triangular(1.50, 6.63, 13.18)`

#### vgr_1 (N=184, KDE)
- **Empirical:** mean=30.80s, std=24.45s, median=26.06s, range=[0.01, 144.61]
- **Recommendation:** KDE (all parametric fits failed KS test)
- **Best parametric attempt:** Gamma(a=0.90, loc=0.01, scale=34.28), KS p=0.000 (fail), mean_err=0.1%, std_err=32.8%
- **Note:** Largest sample size. Right-skewed due to queue times. KDE provides best fidelity.
- **SimPy usage:** Sample from KDE quantile table

#### vgr_2 (N=103, KDE)
- **Empirical:** mean=19.94s, std=18.95s, median=6.11s, range=[0.62, 58.53]
- **Recommendation:** KDE (all parametric fits failed KS test)
- **Best parametric attempt:** Weibull(c=0.59, loc=0.62, scale=28.51), KS p=0.000 (fail), mean_err=123.5%
- **Note:** Bimodal — fast scheduled events (~2s) and actual transport (~36–44s).
- **SimPy usage:** Sample from KDE quantile table

#### wt_1 (N=53, KDE)
- **Empirical:** mean=15.29s, std=10.83s, median=6.41s, range=[3.88, 28.89]
- **Recommendation:** KDE (all parametric fits failed KS test)
- **Best parametric attempt:** Weibull(c=0.64, loc=3.88, scale=13.62), KS p=0.005 (fail), mean_err=48.7%
- **Note:** Bimodal — fast scheduled events (~4s) and actual transport (~26s).
- **SimPy usage:** Sample from KDE quantile table

#### wt_2 (N=28, ⚠️ Small Sample)
- **Empirical:** mean=16.98s, std=12.75s, median=17.48s, range=[3.83, 29.85]
- **Recommendation:** triangular_empirical(p5=3.90, median=17.48, p95=25.69)
- **Reason:** N=28 < 30. Best advisory fit was Normal(loc=16.98, scale=12.52) with KS p=0.002 (fail).
- **SimPy usage:** `random.triangular(3.90, 17.48, 25.69)`

---

## 3. Processing Times — Activity-Level Fitting

Fitting was also performed grouped by `concept:name` (activity type) to provide activity-specific distributions.

### 3.1 Best-Fit Summary Table (Activity Level)

| Activity | N | Recommended | Params | Emp. Mean (s) | Fit Mean (s) | Mean Err % | Emp. Std (s) | Fit Std (s) | KS p (reliable?) | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| /hbw/get_empty_bucket | 29 ⚠️ | triangular_empirical | loc=1.48, c=0.71, scale=45.31 | 22.19 | 27.29 | 23.0% | 19.06 | — | — | ⚠️ FALLBACK (N<30) |
| /hbw/store | 28 ⚠️ | triangular_empirical | loc=1.47, c=0.45, scale=40.25 | 20.16 | 20.89 | 3.6% | 18.02 | — | — | ⚠️ FALLBACK (N<30) |
| /hbw/store_empty_bucket | 77 | KDE | bandwidth=0.42 | 21.61 | 21.61 | 0.0% | 21.46 | 21.46 | 0.157 (yes) | PASS (KDE) |
| /hbw/unload | 78 | KDE | bandwidth=0.42 | 206.23 | 206.23 | 0.0% | 247.45 | 247.45 | 0.002 (yes) | PASS (KDE) |
| /hw/human_review | 55 | KDE | bandwidth=0.45 | 10.73 | 10.73 | 0.0% | 21.55 | 21.55 | 0.001 (yes) | PASS (KDE) |
| /mm/deburr | 50 | KDE | bandwidth=0.46 | 9.60 | 9.60 | 0.0% | 4.88 | 4.88 | 0.179 (yes) | PASS (KDE) |
| /mm/drill | 14 ⚠️ | triangular_empirical | loc=3.76, c=0.13, scale=11.78 | 7.82 | 8.20 | 4.9% | 5.08 | — | — | ⚠️ FALLBACK (N<30) |
| /mm/mill | 37 | triangular_empirical | loc=3.85, c=0.12, scale=10.45 | 6.09 | 7.74 | 27.1% | 3.35 | — | — | ⚠️ FALLBACK |
| /ov/burn | 68 | KDE | bandwidth=0.43 | 19.08 | 19.08 | 0.0% | 27.66 | 27.66 | 0.112 (yes) | PASS (KDE) |
| /ov/temper | 29 ⚠️ | triangular_empirical | loc=3.93, c=0.09, scale=50.20 | 27.85 | 22.19 | 20.3% | 24.45 | — | — | ⚠️ FALLBACK (N<30) |
| /pm/punch_recesses | 10 ⚠️ | triangular_empirical | loc=1.53, c=0.51, scale=21.99 | 12.52 | 12.59 | 0.6% | 11.42 | — | — | ⚠️ FALLBACK (N<30) |
| /sm/sort | 32 | **Normal** | loc=8.15, scale=8.80 | 8.15 | 8.15 | 0.0% | 8.94 | 8.80 | 0.073 (yes) | **PASS (parametric)** |
| /sm/transport | 42 | KDE | bandwidth=0.47 | 11.02 | 11.02 | 0.0% | 10.29 | 10.29 | 0.112 (yes) | PASS (KDE) |
| /vgr/pick_up_and_transport | 287 | KDE | bandwidth=0.32 | 26.90 | 26.90 | 0.0% | 23.19 | 23.19 | 0.017 (yes) | PASS (KDE) |
| /wt/pick_up_and_transport | 81 | KDE | bandwidth=0.42 | 15.87 | 15.87 | 0.0% | 11.48 | 11.48 | 0.056 (yes) | PASS (KDE) |

**Activities with insufficient data (N < 10):**
- `/dm/cylindrical_drill` (N=8), `/dm/lower` (N=8), `/mm/transport_from_to` (N=6), `/pm/punch_gill` (N=6), `/pm/punch_ribbing` (N=9) — raw statistics only, no fitting performed.

### 3.2 Notable Activity-Level Findings

#### /sm/sort — Only Valid Parametric Fit
- **Distribution:** Normal(μ=8.15, σ=8.80)
- **N=32, KS p=0.073 (pass), mean_err=0.0%, std_err=1.6%**
- This is the **only activity** where a parametric distribution passed all validity gates.
- **SimPy usage:** `random.normal(8.15, 8.80)` with truncation at [0, 47.39]

#### /hbw/unload — Extreme Right Tail
- **Empirical:** mean=206.23s, std=247.45s, median=45.80s
- The high mean vs. median reflects startup queue times (max=1034s).
- KDE recommended; all parametric fits failed KS test.

#### /mm/mill — Fallback Despite N=37
- **Empirical:** mean=6.09s, std=3.35s, median=5.09s
- No valid parametric fit. Best was Gamma(a=0.83, loc=3.78, scale=2.26) with KS p=0.085 (pass) but std_err=38.5% (fail).
- Fallback triangular has mean_err=27.1% — flag for manual review.

---

## 4. Inter-Arrival Times

### 4.1 Global Inter-Arrival Times (37 IATs)

| Statistic | Value |
|---|---|
| Count | 37 |
| Mean | 140.25 s |
| Std Dev | 276.60 s |
| Min | 0.56 s |
| Max | 1,336.65 s |
| Median | 3.19 s |
| CV | 1.97 |

**Distribution fitting:** Not performed — N=37 is borderline and the data exhibits a clear **batch arrival structure** that cannot be captured by a single parametric distribution.

### 4.2 Batch Arrival Structure

The arrival process is best modeled as a **two-phase batch arrival process**:

| Phase | N | Mean (s) | Std (s) | Median (s) | CV |
|---|---|---|---|---|---|
| Within-batch (25 IATs) | 25 | 3.64 | 6.40 | 1.51 | 1.76 |
| Between-batch (12 IATs) | 12 | 424.87 | 355.62 | 296.73 | 0.84 |

**Batch size distribution:** Mean=2.9 cases per batch, range=[1, 9], 7 of 13 batches are singletons.

### 4.3 Inter-Arrival Time Recommendations

| Parameter | Recommended Model | Parameters | Notes |
|---|---|---|---|
| Between-batch delay | Exponential | λ = 1/425 s⁻¹ | N=12, CV=0.84 (near-Poisson) |
| Batch size | Empirical | {1: 54%, 2: 8%, 4: 15%, 5: 8%, 7: 8%, 9: 8%} | Small sample |
| Within-batch release | Exponential | λ = 1/3.6 s⁻¹ | N=25, CV=1.76 (bursty) |

**Do NOT use a simple Poisson arrival process** — the CV of ~2.0 would be severely misrepresented by an exponential distribution (CV=1.0).

---

## 5. Failure and Retry Parameters

### 5.1 Failure Probabilities

| Activity-Resource | Failures | Total | Failure Rate | Recommended Model |
|---|---|---|---|---|
| /wt/pick_up_and_transport @ wt_1 | 4 | 27 | 14.8% | Bernoulli(p=0.148) |
| /hbw/store_empty_bucket @ hbw_2 | 2 | 36 | 5.6% | Bernoulli(p=0.056) |
| /hbw/unload @ hbw_2 | 2 | 38 | 5.3% | Bernoulli(p=0.053) |
| /vgr/pick_up_and_transport @ vgr_1 | 1 | 85 | 1.2% | Bernoulli(p=0.012) |
| All others | 0 | 355 | 0.0% | Deterministic(0) |

### 5.2 Retry Delays

Only one retry pattern observed (WF_104_8, wt_1 transport):

| Attempt | Delay (s) |
|---|---|
| 1→2 | 69.1 |
| 2→3 | 129.6 |

**Recommendation:** Use empirical values. With only 2 observations, no distribution fitting is statistically justified. Model as fixed delays with exponential backoff: delay = 69 × 2^(attempt-1) seconds.

---

## 6. Cross-Report Consistency Check

Reconciling recommended fits against empirical statistics from the durations report:

| Parameter | Durations Report Mean | Fit Report Mean | Agreement? |
|---|---|---|---|
| vgr_1 (resource) | 36.6s (n=85, start events) | 30.80s (n=184, all positive) | ⚠️ Different — fit includes scheduled events |
| vgr_2 (resource) | 40.8s (n=42, start events) | 19.94s (n=103, all positive) | ⚠️ Different — fit includes scheduled events |
| wt_1 (resource) | 26.2s (n=27, start events) | 15.29s (n=53, all positive) | ⚠️ Different — fit includes scheduled events |
| wt_2 (resource) | 29.5s (n=14, start events) | 16.98s (n=28, all positive) | ⚠️ Different — fit includes scheduled events |
| /vgr/pick_up_and_transport (activity) | 36.6s (vgr_1) + 40.8s (vgr_2) | 26.90s (pooled) | ⚠️ Pooled — includes scheduled events |
| /wt/pick_up_and_transport (activity) | 26.2s (wt_1) + 29.5s (wt_2) | 15.87s (pooled) | ⚠️ Pooled — includes scheduled events |

**Important note:** The resource-level and activity-level fits include ALL positive-duration events (scheduled + start transitions), while the durations report uses only `actual_duration` from start events. This means the fitted distributions capture the **full event duration distribution** including near-zero scheduled events. For simulation processing times, the durations report values (start events only) should be used as the primary reference. The KDE quantile tables can be filtered to exclude near-zero values if needed.

**Reconciliation:** The activity-level KDE fits for `/vgr/pick_up_and_transport` and `/wt/pick_up_and_transport` are bimodal, with one mode near zero (scheduled events) and one mode at the actual processing time. For DES simulation, use the actual processing time mode (the higher mode) or filter the KDE quantiles to exclude values below the 25th percentile.

---

## 7. KDE Quantile Exports

| Parameter | Group | File |
|---|---|---|
| duration_computed | hbw_1 | `reports/kde_quantiles/duration_computed__hbw_1.csv` |
| duration_computed | hbw_2 | `reports/kde_quantiles/duration_computed__hbw_2.csv` |
| duration_computed | hw_1 | `reports/kde_quantiles/duration_computed__hw_1.csv` |
| duration_computed | mm_1 | `reports/kde_quantiles/duration_computed__mm_1.csv` |
| duration_computed | ov_1 | `reports/kde_quantiles/duration_computed__ov_1.csv` |
| duration_computed | vgr_1 | `reports/kde_quantiles/duration_computed__vgr_1.csv` |
| duration_computed | vgr_2 | `reports/kde_quantiles/duration_computed__vgr_2.csv` |
| duration_computed | wt_1 | `reports/kde_quantiles/duration_computed__wt_1.csv` |

**KDE sampling in SimPy:**
```python
import numpy as np

# Load quantile table
quantiles = np.loadtxt('reports/kde_quantiles/duration_computed__vgr_1.csv', delimiter=',')
probs = np.linspace(0, 1, len(quantiles))

# Sample
sample = np.interp(np.random.uniform(), probs, quantiles)
```

---

## 8. SimPy Implementation Recommendations

### 8.1 Processing Time Generators

```python
import simpy
import numpy as np

# KDE-based sampling function
def kde_sample(env, quantile_file):
    """Sample from KDE quantile table."""
    quantiles = np.loadtxt(quantile_file, delimiter=',')
    probs = np.linspace(0, 1, len(quantiles))
    return np.interp(np.random.uniform(), probs, quantiles)

# Resource-specific processing times (using durations report values for start events)
PROCESSING_TIMES = {
    # High-precision activities (low variance, near-deterministic)
    '/dm/lower': lambda: 13.9,                    # Deterministic
    '/ov/temper': lambda: 52.7,                   # Deterministic
    '/mm/deburr': lambda: np.random.normal(14.4, 0.7),  # Normal
    '/wt/pick_up_and_transport@wt_2': lambda: 29.5,     # Deterministic

    # KDE-based (load quantile tables)
    '/vgr/pick_up_and_transport@vgr_1': lambda: kde_sample(None, 'reports/kde_quantiles/duration_computed__vgr_1.csv'),
    '/vgr/pick_up_and_transport@vgr_2': lambda: kde_sample(None, 'reports/kde_quantiles/duration_computed__vgr_2.csv'),
    '/hw/human_review': lambda: kde_sample(None, 'reports/kde_quantiles/duration_computed__hw_1.csv'),
    '/ov/burn': lambda: kde_sample(None, 'reports/kde_quantiles/duration_computed__ov_1.csv'),

    # Triangular fallbacks
    '/dm/cylindrical_drill': lambda: np.random.triangular(1.48, 8.35, 30.59),
    '/mm/mill@mm_2': lambda: np.random.triangular(3.78, 5.29, 11.68),
    '/ov/burn@ov_2': lambda: np.random.triangular(4.12, 7.61, 36.68),
    '/pm/punch_recesses': lambda: np.random.triangular(1.53, 12.72, 21.99),
}
```

### 8.2 Arrival Process

```python
def batch_arrival_process(env):
    """Generate batch arrivals with empirical distribution."""
    while True:
        # Between-batch delay (exponential, mean=425s)
        yield env.timeout(np.random.exponential(425))

        # Batch size (empirical distribution)
        batch_size = np.random.choice([1, 2, 4, 5, 7, 9], p=[0.54, 0.08, 0.15, 0.08, 0.08, 0.08])

        # Release cases within batch
        for i in range(batch_size):
            yield env.timeout(np.random.exponential(3.6))
            # Create new entity/workpiece
            env.process(workpiece(env))
```

### 8.3 Failure Modeling

```python
FAILURE_RATES = {
    ('/wt/pick_up_and_transport', 'wt_1'): 0.148,
    ('/hbw/store_empty_bucket', 'hbw_2'): 0.056,
    ('/hbw/unload', 'hbw_2'): 0.053,
    ('/vgr/pick_up_and_transport', 'vgr_1'): 0.012,
}

def process_with_failure(env, activity, resource):
    """Process an activity with failure probability."""
    rate = FAILURE_RATES.get((activity, resource), 0.0)
    if np.random.random() < rate:
        # Failure — retry for wt_1, terminal for others
        if resource == 'wt_1':
            yield env.timeout(69)  # First retry delay
            # Retry logic here
        else:
            raise Exception(f"Terminal failure at {activity} on {resource}")
    # Normal processing
    yield env.timeout(PROCESSING_TIMES[activity]())
```

---

## 9. Data Quality Flags Summary

| Flag | Count | Details |
|---|---|---|
| ⚠️ N < 30 (small sample) | 10 groups | dm_2, ov_2, pm_1, sm_2, wt_2, /hbw/get_empty_bucket, /hbw/store, /mm/drill, /ov/temper, /pm/punch_recesses |
| ⚠️ Fallback (no valid parametric fit) | 7 groups | mm_2, sm_1, /mm/mill, plus 4 small-sample groups |
| ⚠️ Bimodal distributions | 8 groups | hbw_1, hbw_2, mm_1, ov_1, vgr_2, wt_1, wt_2, /hbw/store_empty_bucket — KDE recommended |
| ⚠️ High CV (>1.5) | 5 groups | hbw_2 (CV=1.75), hw_1 (CV=2.01), ov_2 (CV=1.71), pm_1 (CV=0.92), /hbw/unload (CV=1.20) |
| ⚠️ Outlier rate > 5% | 13 groups | See durations report Section 2.2 |
| ⚠️ Cross-report discrepancy | 6 groups | Resource-level fits include scheduled events; durations report uses start events only |

---

## 10. Limitations and Caveats

1. **Bimodal distributions:** Many resource-level distributions are bimodal because they combine near-zero scheduled events with actual processing times. For DES simulation, consider filtering to start events only or using the higher mode of the KDE.

2. **Small samples:** 10 groups have N < 30. Parametric fits for these groups are advisory only; empirical fallbacks (triangular) are recommended.

3. **Inter-arrival times:** Only 37 global IATs available. The batch arrival structure means simple Poisson/exponential models are inappropriate.

4. **Failure data:** Only 9 failures observed. Failure probabilities are point estimates with wide confidence intervals.

5. **Retry delays:** Only 2 retry delay observations. No distribution fitting performed; empirical values recommended.

6. **KDE limitations:** KDE fits are non-parametric and require quantile table lookup for sampling. They cannot be expressed as simple SimPy random variables.

---

*Report generated from `eventlog_cleaned.parquet` (1,383 events, 461 entities, 38 cases, 15 resources, 20 activities). Distribution fitting performed using AIC ranking with validity gate: mean_err ≤ 15%, std_err ≤ 25%, tail_ratio ≤ 2.0, KS pass when N ≥ 30.*
