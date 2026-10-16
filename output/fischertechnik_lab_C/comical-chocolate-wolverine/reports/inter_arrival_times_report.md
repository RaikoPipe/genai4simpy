# Inter-Arrival Times Report — fischertechnik_lab_C

**Phase 4 — Arrival/release process extraction**
Window: `2021-07-01 18:48:23.227 → 20:19:24.734 UTC` (horizon ≈ 5,461.5 s)
Source: `extract_inter_arrival_times` (case column `case`, timestamp `time:timestamp`, unit: seconds)

---

## 1. Release-time definition

Per the confirmed extraction plan (§3.2), the release time per case is the timestamp of the `scheduled` row of `/hbw/unload` — the first request of the case at the entry resource. All **37 cases** are included, including the 19 missing-data stubs: they are real orders released into the system and belong in the arrival stream. No censored cases exist (initial WIP at t0 = 0), so no cases were excluded.

## 2. Overall inter-arrival statistics (no gaps removed)

| Statistic | Value (s) |
|---|---|
| Arrivals | 37 |
| IATs (n) | 36 |
| Span | 4,656.44 |
| Mean | 129.35 |
| Std | 264.36 |
| CV | 2.044 |
| Min | 0.510 |
| Median | 1.641 |
| Max | 989.28 |
| Zero IATs | 0 |

The overall CV of 2.04 and the wide min–max range (0.51 s → 989.3 s) already signal that a single exponential or even a single empirical distribution would mix two very different regimes.

## 3. Regime decomposition

The tool's two-regime decomposition finds a clearly separated **two_regime** structure:

- Separation threshold: 23.26 s (log-separation 0.888)
- Gap-to-burst IAT ratio: **212.2** — the regimes are separated by more than two orders of magnitude

### 3.1 Intra-burst IAT (within a burst)

| Statistic | Value (s) |
|---|---|
| n | 25 |
| Mean | 1.974 |
| Std | 3.105 |
| CV | 1.573 |
| Median | 1.078 |
| Min / Max | 0.510 / 16.250 |

### 3.2 Inter-burst gaps (between bursts)

| Statistic | Value (s) |
|---|---|
| n | 11 |
| Mean | 418.83 |
| Std | 334.42 |
| CV | 0.798 |
| Median | 416.82 |
| Min / Max | 33.30 / 989.28 |

### 3.3 Burst sizes

| Statistic | Value |
|---|---|
| n_bursts | 12 |
| Mean size | 3.083 |
| Range | 1 – 9 |
| Observed sizes (in order) | 9, 1, 5, 5, 2, 2, 2, 1, 1, 5, 1, 3 |

Burst-size distribution (categorical): size 1 → 0.3333, size 2 → 0.25, size 3 → 0.0833, size 5 → 0.25, size 9 → 0.0833.

## 4. Chosen model: `two_regime_bursts`

**Why:** `regimes.regime == "two_regime"` with a gap:burst ratio of 212.2 — collapsing the process to a single mean IAT (129.3 s) would be qualitatively wrong: it would destroy the fast within-burst arrivals (mean ≈ 2 s) and the long idle gaps (mean ≈ 419 s) that drive queue build-up and resource utilization at `hbw`. The release rule is **open** (no WIP cap, no completion-triggered release — confirmed in `control_policies.release_rule`), so `wip_controlled` does not apply.

The spec section `arrivals` (written to `simulation_spec.json`) contains, copied verbatim from the tool's `recommended` block:

- `burst_size`: categorical over {1, 2, 3, 5, 9} with probs {0.3333, 0.25, 0.0833, 0.25, 0.0833} (n = 12)
- `intra_burst_iat`: empirical_quantiles (n = 25, mean 1.9737 s) — 21-point quantile table
- `inter_burst_gap`: empirical_quantiles (n = 11, mean 418.8268 s) — 21-point quantile table
- `initial_burst`: constant 9 — the window opens exactly at the first release, and the first burst contains 9 cases; this seeds the simulation with the observed opening burst instead of an additional random gap.

Empirical quantiles are used for both IAT regimes rather than parametric fits: samples are small (n = 25 / n = 11) and clearly non-exponential (intra-burst CV 1.57 with a mass near 0.5–1.6 s plus a 16.25 s tail; gaps are near-lognormal with CV 0.80), so quantile sampling preserves the observed shape without overfitting.

## 5. Notes

- The long gaps between bursts are part of the arrival process and were **not** trimmed or treated as outliers (statistics policy).
- The 8 process models (WF_104 removed from the mix) are interleaved draws from this single global stream; the variant mix (renormalized over the 34 non-WF_104 cases) is recorded in the extraction plan §3.2 and the spec `variants` section.
- Observed arrival times are **not** replayed: the model samples burst sizes, intra-burst IATs and inter-burst gaps from the fitted distributions above.
