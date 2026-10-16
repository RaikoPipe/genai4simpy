# Inter-Arrival Times Report — fischertechnik_lab_A (run: eager-nice-cow)

## 1. Data basis

- Source: `work_files/eventlog_cleaned.parquet`, 18 cases, window 2021-07-06 15:08:27.91 → 16:01:31.12 UTC (~53 min, 3183 s).
- Arrival (release) time per case = earliest `time:timestamp` of that case (first observed event / first request).
- All 18 cases retained, including the 4 incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) per T2 — their release times are fully observed.
- No gaps removed: the long inter-burst gaps are part of the arrival process.

## 2. Phase split (binding T2)

Per the extraction plan, the arrival process is modelled as **two phases**, with the split fixed at the first 8 cases (not a data-driven regime change):

| Phase | Cases | Releases | Span |
|---|---|---|---|
| 1. Initial near-simultaneous burst | WF_101_30, WF_102_31, WF_103_29, WF_105_21, WF_1106_21, WF_1107_16, WF_108_17, WF_109_15 | 8 | 6.91 s (15:08:27.91 → 15:08:34.82) |
| 2. Steady state | WF_104_20, WF_1106_22, WF_103_30, WF_105_22, WF_101_31, WF_102_32, WF_1107_17, WF_104_21, WF_108_18, WF_109_16 | 10 | 1641.8 s (15:19:08.32 → 16:01:31.12) |

Transition gap (last initial-burst case → first steady-state release): **633.50 s** (single observation; not modelled as a distribution).

A single mixed IAT across both phases was explicitly **not** fitted (T2 binding). For reference only, the mixed global IAT is n=17, mean 134.25 s, CV 1.81 — it conflates the two regimes and is not used in the spec.

## 3. Phase 1 — initial burst

- **Burst size: 8** (all 8 released within 6.91 s of window start; treated as a fixed initial condition, observed once).
- **Within-burst spacing (n=7):** 0.906, 1.656, 1.485, 0.641, 0.813, 0.510, 0.896 s
  - mean 0.9865 s, std 0.4258, min 0.5096, max 1.6558, median 0.8962, CV 0.4316
  - Modelled as **empirical_quantiles** (21-point quantile table in spec).

## 4. Phase 2 — steady state (10 releases)

### 4.1 Phase-level IAT (n=9)
799.957, 317.875, 2.359, 139.110, 0.687, 93.406, 5.531, 2.000, 280.906 s
- mean **182.43 s**, std 261.84, min 0.6875, max 799.957, median 93.406, CV 1.4353
- Modelled as **empirical_quantiles** (21-point quantile table in spec).

### 4.2 Burst structure within the steady state
Steady-state IATs clearly separate into two regimes (intra-burst ≤ 5.53 s vs inter-burst gaps ≥ 93.4 s; a 10 s threshold classifies all 9 IATs unambiguously):

- **Bursts (6):** sizes [1, 1, 2, 2, 3, 1] → categorical probs {1: 0.5, 2: 0.3333, 3: 0.1667}, mean 1.6667.
  - 15:19:08 (1), 15:32:28 (1), 15:37:46+15:37:48 (2), 15:40:07+15:40:08 (2), 15:41:41+15:41:47+15:41:49 (3), 15:46:30 (1)
- **Intra-burst IAT (n=4):** 2.359, 0.6875, 5.5312, 2.0001 s → mean 2.6444, std 2.0542, min 0.6875, max 5.5312, median 2.1795 → empirical_quantiles.
- **Inter-burst gap (n=5):** 799.957, 317.875, 139.110, 93.406, 280.906 s → mean **326.25 s**, std 280.96, min 93.406, max 799.957, median 280.906, CV 0.8612 → empirical_quantiles.
  - A triang fit on support [93.41, 799.96] was rejected: the observed mean (326.25 s) is below the minimum possible triang mean on that support (328.92 s), i.e. no valid c exists.

## 5. Chosen model

`arrivals.model = "two_regime_bursts"` with a two-phase structure in the spec:

1. **Initial burst:** fixed size 8, within-burst spacing from empirical quantiles (n=7).
2. **Steady state:** bursty releases — `burst_size` (categorical, n=6), `intra_burst_iat` (empirical quantiles, n=4), `inter_burst_gap` (empirical quantiles, n=5); the phase-level IAT (n=9) is also provided for the modeling stage.

Why not the tool's default `recommended` block: it pools all 17 IATs into one mixed distribution (mean 134.25 s) and its burst decomposition spans both phases (burst_size includes the initial 8-burst, n=7). The binding T2 rule forbids a single mixed IAT and fixes the split at 8/10, so the phase-resolved parameters above were written to the spec instead.

## 6. Uncertainty flags (for the modeling stage)

1. **Small base:** only 18 releases in one ~53-min window — all arrival parameters carry wide uncertainty.
2. **Sparse sub-samples:** steady-state inter-burst gap (n=5) and intra-burst IAT (n=4) are too small for parametric fits; empirical quantiles used, and the upper tail is poorly estimated (p90 = 607.1 s vs max = 799.96 s from 9 samples).
3. **Initial burst size 8** is a single observation — modelled as a fixed initial condition (8 simultaneous releases at t=0), not a distribution.
4. **Steady-state mean IAT (182.43 s)** is dominated by the single 799.96 s gap; treat the mean as low-confidence.
5. **Transition gap (633.50 s)** between the initial burst and the first steady-state release is one observation; not modelled as a distribution.
6. Release control is open (no WIP cap), consistent with `control_policies.release_rule = "open (bursty releases)"`; max WIP observed 12, time-avg 7.09 (from topology phase).

## 7. Recorded assumptions

- Arrival time = first observed event per case (first request), per T2; the 4 incomplete cases are retained for arrival extraction.
- Phase split at the first 8 cases is fixed by the extraction plan (T2), not inferred from a regime-change test.
- Steady-state intra/gap classification threshold = 10 s; all 9 steady-state IATs classify unambiguously (next-smallest gap is 93.4 s).
- Empirical quantiles (21 points) chosen over parametric families because the samples are small (n ≤ 9) and the gap distribution is non-monotone (triang infeasible).
