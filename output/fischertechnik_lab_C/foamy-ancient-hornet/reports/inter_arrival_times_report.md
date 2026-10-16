# Inter-Arrival Times Report — fischertechnik_lab_C (run: foamy-ancient-hornet)

## 1. Data Basis

- Source: `eventlog_cleaned.parquet` — arrival (release) time per case = earliest `time:timestamp` of the case's first activity (`/hbw/unload`), i.e. the `scheduled` timestamp.
- 37 cases, 36 inter-arrival times (IATs), span 4,656.44 s within a horizon of 5,461.51 s.
- No censored cases to exclude (`initial_state.excluded_from_estimation` is empty; 0 left-/right-censored per extraction plan).
- No gaps removed: the long gaps between bursts are part of the arrival process.

## 2. Overall IAT Statistics (no gaps removed)

| Statistic | Value (s) |
|---|---|
| n | 36 |
| Mean | 129.3455 |
| Std | 264.3586 |
| CV | 2.0438 |
| Min | 0.5101 |
| Median | 1.6406 |
| Max | 989.2759 |

The very high CV (2.04) and the huge min/max spread indicate a non-renewal, bursty arrival process — a single exponential (or any single-regime renewal fit) would be inappropriate.

## 3. Regime Decomposition

The tool's two-regime decomposition (threshold 23.26 s, log-separation 0.888, gap-to-burst ratio 212.2) finds a clear **two_regime** structure:

- **12 bursts** of batch releases (operator-driven, exogenous — confirmed not completion-triggered and not WIP-capped).
- **Burst sizes**: values [9, 1, 5, 5, 2, 2, 2, 1, 1, 5, 1, 3], mean 3.083.
- **Within-burst IAT** (25 observations): mean 1.974 s, std 3.105, CV 1.573, median 1.078 s, range 0.51–16.25 s.
- **Inter-burst gaps** (11 observations): mean 418.827 s, std 334.421, CV 0.798, median 416.818 s, range 33.30–989.28 s.

The two regimes are well separated (gap mean ≈ 212× burst-IAT mean), so arrivals must be modelled as batches, not as a single exponential with the overall mean.

## 4. Chosen Model

**`two_regime_bursts`** (written to spec `arrivals` via `draft_arrivals_spec`, numbers copied verbatim from `extract_inter_arrival_times`):

| Component | Family | Parameters | n |
|---|---|---|---|
| `burst_size` | categorical | values [1, 2, 3, 5, 9], probs [0.3333, 0.25, 0.0833, 0.25, 0.0833], mean 3.083 | 12 |
| `intra_burst_iat` | empirical_quantiles | 21 quantiles, 0.51–16.25 s, mean 1.9737 | 25 |
| `inter_burst_gap` | empirical_quantiles | 21 quantiles, 33.30–989.28 s, mean 418.8268 | 11 |

Rationale:
1. `regimes.regime == "two_regime"` with a 212× gap/burst separation — the textbook case for the two-regime burst model.
2. Control policy confirms exogenous, operator-driven batch releases with no WIP cap, so `wip_controlled` is not applicable.
3. Small samples (n = 11 gaps, n = 25 intra-burst IATs) make parametric fits unreliable; empirical quantile distributions preserve the observed variability (including the 16.25 s intra-burst outlier and the 33.3 s short gap) without trimming.

## 5. Variant Split

After arrival, each case is assigned a process model by interleaved categorical draw using the spec's process-model proportions (already in `spec.variants`, copied into `arrivals.variant_split`):

WF_101 0.1081, WF_102 0.1351, WF_103 0.1351, WF_104 0.0811, WF_105 0.1081, WF_108 0.0811, WF_109 0.0811, WF_1106 0.1622, WF_1107 0.1081.

## 6. Caveats

- n = 11 inter-burst gaps is a small sample; the empirical gap distribution should be revisited if more data becomes available (calibration phase).
- The single 9-case burst and the 33.3 s minimum gap are retained as real observations (no documented data defect), per the statistics policy.
- Observed case IDs and timestamps are not replayed; the model is fully distributional.
