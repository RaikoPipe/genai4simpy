# Inter-Arrival Times Report — Fischertechnik Lab A (wandering-flying-bee)

**Data:** `work_files/eventlog_cleaned.parquet` (576 rows, 192 instances, 18 cases, 9 variants).
**Case arrival time:** `time:timestamp` of the `scheduled` row of the case's first activity (works for WF_104, whose first activity is `/vgr/pick_up_and_transport`). All 18 cases used, including the 4 incomplete ones (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) — retained for arrival estimation per confirmed decision. No censored cases excluded (no case is left-censored at window start; initial WIP = 0).

## 1. Case arrival times (relative to first arrival)

| # | Case | Variant | t_rel (s) |
|---|------|---------|-----------|
| 1 | WF_101_30 | WF_101 | 0.000 |
| 2 | WF_102_31 | WF_102 | 0.906 |
| 3 | WF_103_29 | WF_103 | 2.562 |
| 4 | WF_105_21 | WF_105 | 4.046 |
| 5 | WF_1106_21 | WF_1106 | 4.687 |
| 6 | WF_1107_16 | WF_1107 | 5.500 |
| 7 | WF_108_17 | WF_108 | 6.010 |
| 8 | WF_109_15 | WF_109 | 6.906 |
| 9 | WF_104_20 | WF_104 | 640.403 |
| 10 | WF_1106_22 | WF_1106 | 1440.359 |
| 11 | WF_103_30 | WF_103 | 1758.234 |
| 12 | WF_105_22 | WF_105 | 1760.593 |
| 13 | WF_101_31 | WF_101 | 1899.703 |
| 14 | WF_102_32 | WF_102 | 1900.390 |
| 15 | WF_1107_17 | WF_1107 | 1993.797 |
| 16 | WF_104_21 | WF_104 | 1999.328 |
| 17 | WF_108_18 | WF_108 | 2001.328 |
| 18 | WF_109_16 | WF_109 | 2282.234 |

## 2. Overall IAT statistics (no gaps removed)

17 IATs over a 2282.23 s span:

| Statistic | Value (s) |
|---|---|
| Mean | 134.249 |
| Std | 242.763 |
| CV | 1.808 |
| Median | 2.000 |
| Min | 0.510 |
| Max | 799.957 |

The mixed mean (134.25 s) is **not** used as a model parameter — it blends the two regimes (per confirmed decision).

## 3. Regime decomposition (tool: `extract_inter_arrival_times`)

- **Regime: two_regime** — threshold 22.73 s, log-separation 0.932, gap-to-burst ratio 237.5.
- Tool's auto-decomposition (for reference): burst IATs n=11, mean 1.589 s (std 1.440); gap IATs n=6, mean 377.458 s (std 280.866); burst sizes [8, 1, 1, 2, 2, 3, 1] (mean 2.571).
- Note: the tool's auto-decomposition pools the case-8→case-9 boundary IAT (633.50 s) into the gap sample and the initial 8-case burst into the burst-size sample. Per the confirmed decision, both are handled explicitly below.

## 4. Confirmed two-phase split

### Phase 1 — initial near-simultaneous burst (cases 1–8)
Within-burst IATs (n = 7): [0.906, 1.656, 1.485, 0.641, 0.813, 0.510, 0.896] s

| Statistic | Value (s) |
|---|---|
| Mean | 0.987 |
| Std | 0.426 |
| Median | 0.896 |
| Min | 0.510 |
| Max | 1.656 |

The 8 cases arrive within a 6.91 s window — effectively a simultaneous release with a small spread. The fit degenerates to near-simultaneous arrival with a small jitter, as anticipated by the data.

### Regime boundary (EXCLUDED from both samples)
Case 8 → case 9 IAT = **633.497 s** — the transition between the initial burst and steady state; excluded per confirmed decision.

### Phase 2 — steady-state arrivals (cases 9–18)
IATs (n = 9): [799.957, 317.875, 2.359, 139.110, 0.687, 93.406, 5.531, 2.000, 280.906] s

| Statistic | Value (s) |
|---|---|
| Mean | 182.426 |
| Std | 261.842 |
| CV | 1.435 |
| Median | 93.406 |
| Min | 0.687 |
| Max | 799.957 |

Observation (not used as a separate model layer, per the confirmed decision to fit one distribution over the 9 IATs): with the 22.73 s threshold, Phase 2 contains 5 "gaps" (mean 326.25 s) and 4 short intra-burst IATs (mean 2.64 s), i.e. steady-state bursts of size [1, 1, 2, 2, 3, 1] (mean 1.67).

## 5. Chosen model

**`two_regime_bursts`** (spec section `arrivals`):

- `initial_burst`: constant **8** — the first 8 cases released as one near-simultaneous burst.
- `intra_burst_iat`: **empirical_quantiles** of the 7 Phase-1 IATs (mean 0.987 s) — characterises the initial-burst spread (small jitter around simultaneity).
- `burst_size`: categorical **[1]** with prob 1.0 — in the steady state each arrival is its own burst (the 9 Phase-2 IATs are modelled directly as gaps).
- `inter_burst_gap`: **empirical_quantiles** of the 9 Phase-2 IATs (mean 182.43 s) — steady-state arrival process.

**Why:**
1. Two-regime evidence is unambiguous (CV 1.81 overall; gap/burst ratio ~237; the 8-case initial burst spans only 6.9 s).
2. The confirmed decision mandates the two-phase structure with the boundary IAT excluded, which the tool's auto-decomposition does not implement — hence the spec was written manually with phase-specific samples (numbers copied verbatim from the computed IATs).
3. Release rule is **open** (`control_policies.release_rule`: "open (bursty releases)", `completion_triggered: false`) → no WIP cap, no `wip_controlled` model.
4. Empirical quantiles (rather than parametric fits) are used because the samples are tiny (n = 7 and n = 9); parametric fits (e.g. lognormal on the gaps) are unstable at these sizes, and per policy no smoothing is applied.

## 6. Confidence flags

- **Phase 1 (n = 7):** low confidence — jitter mean 0.99 s ± 0.43 s; the degenerate "simultaneous + small jitter" reading is robust (all 7 IATs < 1.7 s), but the exact jitter distribution is not.
- **Phase 2 (n = 9):** low confidence — mean 182.4 s with std 261.8 s (CV 1.44); the empirical quantile distribution is the only honest representation of 9 samples. The single 799.96 s IAT dominates the upper tail.
- **Boundary IAT (633.50 s):** single observation, excluded from estimation; if the initial burst is re-run in simulation, the steady state will start after one gap drawn from the Phase-2 distribution, not after 633.5 s.
- No outliers removed; no gaps trimmed (long gaps are part of the arrival process).
