# Inter-Arrival Times Report — fischertechnik_lab_B (significant-hilarious-cuscus)

## 1. Population & Release-Time Convention

- **Population**: all **38 released cases**, including the 3 excluded failure-only cases (WF_102_16, WF_102_17, WF_104_9) — their releases are real system inputs regardless of outcome.
- **Release time per case** = timestamp of the `scheduled` row of the first activity `/hbw/unload`.
- Verified: for all 38 cases the earliest log timestamp of the case equals the `/hbw/unload` scheduled timestamp exactly (max abs diff 0.0 s), and `/hbw/unload` is the first activity of every case — so the release-time convention and the earliest-timestamp-per-case convention coincide.
- Window: first release 2021-06-30 15:24:34.013 (t0), last release 16:51:03.396; span of releases ≈ 5189.4 s.

## 2. Overall IAT Statistics (no gaps removed)

37 inter-arrival times over 38 cases:

| Statistic | Value (s) |
|---|---|
| Mean | 140.25 |
| Std | 280.42 |
| CV | 2.00 |
| Median | 3.19 |
| Min | 0.56 |
| Max | 1336.65 |

The mixed mean IAT (140.3 s, cv 2.0) is **not** a usable arrival model: it blends two very different regimes (short within-burst intervals and long idle gaps). The regimes are well separated (log-separation 0.88, gap-to-burst ratio ≈ 162, threshold 17.85 s), so the arrival process is modeled as **two_regime_bursts**.

## 3. Regime Decomposition (two_regime_bursts)

Threshold 17.85 s splits the 37 IATs into 13 inter-burst gaps and 24 within-burst IATs, forming **14 bursts** (first burst at t0; the 13 gaps separate the 14 bursts).

### 3.1 Gaps between bursts (n = 13)

| Statistic | Value (s) |
|---|---|
| Mean | 394.67 |
| Std | 357.47 |
| CV | 0.91 |
| Median | 294.14 |
| Min | 32.27 |
| Max | 1336.65 |

Sample: [858.66, 1336.65, 478.22, 61.95, 193.35, 239.22, 189.61, 524.73, 32.27, 294.14, 199.43, 423.18, 299.32]

### 3.2 Burst sizes (n = 14 bursts)

| Statistic | Value |
|---|---|
| Mean | 2.71 |
| Min | 1 |
| Max | 9 |

Empirical categorical distribution:

| Size | 1 | 2 | 4 | 5 | 6 | 9 |
|---|---|---|---|---|---|---|
| Count | 8 | 1 | 2 | 1 | 1 | 1 |
| Prob | 0.5714 | 0.0714 | 0.1429 | 0.0714 | 0.0714 | 0.0714 |

Burst sequence: [4, 9, 4, 5, 1, 1, 1, 1, 6, 1, 1, 1, 2, 1]

### 3.3 Within-burst IAT (n = 24)

| Statistic | Value (s) |
|---|---|
| Mean | 2.44 |
| Std | 2.38 |
| CV | 0.98 |
| Median | 1.44 |
| Min | 0.56 |
| Max | 9.87 |

Sample: [1.37, 1.11, 1.31, 0.89, 0.97, 0.56, 0.70, 0.71, 1.84, 0.75, 6.70, 1.71, 2.33, 1.51, 5.86, 0.65, 5.39, 9.87, 4.22, 0.62, 0.65, 3.01, 2.72, 3.19]

## 4. Chosen Arrival Model

**`two_regime_bursts`** (per the release-control analysis in the extraction plan, §3.2; `control_policies.release_rule` = "open (bursty releases)", so no WIP cap applies):

- **Inter-burst gap**: empirical quantile distribution over the 13 observed gaps (mean 394.67 s) — the long idle periods between release batches.
- **Burst size**: empirical categorical over the 14 observed burst sizes (mean 2.71).
- **Within-burst IAT**: empirical quantile distribution over the 24 observed short intervals (mean 2.44 s) — the near-simultaneous releases inside a batch.

The overall mean IAT (140.3 s, cv 2.0) is deliberately **not** modeled; the long gaps are part of the arrival process and were never trimmed. All numbers are stored verbatim in the spec `arrivals` section (source: `extract_inter_arrival_times`, n = 13/14/24 per component).

## 5. Component Samples for the Distribution-Fitting Agent

Saved in `work_files/`:

- `arrival_gaps.csv` — 13 inter-burst gaps (s)
- `arrival_burst_sizes.csv` — 14 burst sizes
- `arrival_within_burst_iat.csv` — 24 within-burst IATs (s)
- `release_times.csv` — the 38 case release times (reference only; not a model input — no trace replay)

Suggested candidate families (for the fitting agent): gaps → exponential / lognormal / gamma; within-burst IAT → exponential (or empirical); burst sizes → geometric / Poisson / empirical categorical.

## 6. Notes & Caveats

- The 3 failure-only cases are included in arrivals (per plan) but excluded from routing/failure estimation (per `initial_state.excluded_from_estimation`).
- The first burst (size 4) starts exactly at the window start (t0 = 15:24:34.013); the observation window may therefore truncate the gap preceding the first burst. No pre-window gap is modeled.
- With n = 13 gaps and n = 24 within-burst IATs, fitted-distribution confidence is limited; the empirical quantile distributions in the spec are the safe baseline for the simulation.
