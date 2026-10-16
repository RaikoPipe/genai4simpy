# Evaluation Report — fischertechnik_lab_C Digital Twin (Phase 5 follow-up: refined MR1)

**Model:** `reports/simulation/simulation.py` (537 lines, **unchanged** this round — confirmed by line count and exact reproduction of the original `__main__` output: 205 rows, 20 entered / 7 completed at seed 1)
**Contract:** OUTPUT CONTRACT v2
**Iteration count:** 1 (this round: oracle refinement only, no model change per confirmed user decision)

## Final verdict: **PASS**

All contract checks pass (26/26); every behavioural KPI with ground truth lies inside the 95% prediction interval; all metamorphic relations pass under the refined oracle (MR1a + MR1b; MR2–MR4 unchanged). The strict system-wide-wait formulation of MR1 is retained as a **documented, non-gating accepted exception** (see below).

---

## 1. Contract test (`run_contract_test`)

| Check | Result |
|---|---|
| Importable without side effects; required symbols (`run_single_replication`, `RESOURCE_CAPACITIES`, `SIMULATION_TIME`, `ARRIVAL_RATE_SCALE`, `FAILURES_ENABLED`) | ✅ |
| Event-log columns incl. `case_arrival`, `queue_enter`; numeric times; `end ≥ start ≥ queue_enter` | ✅ |
| Reproducibility per seed (seeds 1, 1, 2) | ✅ |
| Resources in `RESOURCE_CAPACITIES`; activity/variant vocabulary and capacities vs spec | ✅ |
| No hard-coded observed case ids (no trace replay); no file I/O; knobs read at call time | ✅ |
| **Total** | **✅ PASS 26/26** |

Warnings (expected, non-blocking): spec activities never emitted in seed 1: `/dm/cylindrical_drill` (alternate WF_1106 route, not in the linear main sequence), `/dm/lower`, `/pm/punch_recesses` (low-proportion variants; may be absent in a single seed).

## 2. Behavioural check vs observed log (30 replications, deterministic)

| KPI | Ground truth | Sim mean | 95% PI | Bias | Covered |
|---|---|---|---|---|---|
| completed_cases | 13 | 12.03 | [6.73, 18.83] | −7.4% | ✅ |
| cases_entered | 37 | 41.47 | [23.45, 60.38] | +12.1% | ✅ |
| WIP at end | 24 | 29.43 | [13.45, 47.55] | +22.6% | ✅ |
| flow_time (s) | 597.5 | 794.7 | [560.3, 1170.6] | +33.0% | ✅ |
| time_in_system (s) | 430.6 | 539.0 | [375.2, 802.9] | +25.2% | ✅ |
| failure_rate | 0.013 | 0.014 | [0.005, 0.026] | +3.2% | ✅ |
| overlapping_steps/case | 1.46 | 0.90 | [0.32, 1.68] | −38.1% | ✅ |
| mean_WIP | 6.07 | 5.32 | [2.12, 11.85] | −12.3% | ✅ |
| activity-duration MAPE | — | 9.9% | [7.1, 16.6] | — | ✅ |
| variant JSD | — | 0.049 | [0.01, 0.11] | — | ✅ |
| utilisation MAE (pp) | — | 4.5 | [1.7, 10.4] | — | ✅ |

All 12 KPIs with observed ground truth fall inside the 95% PI. Results are identical to the previous round (deterministic, same seeds), confirming the model was not altered.

Waiting by resource class (s): hbw 177.9 obs / 92.1 sim; vgr 19.4 / 32.7; hw 3.1 / 10.3; wt 6.5 / 0.2; ov 5.0 / 5.1; others small. Release-spacing median 1.6 obs / 4.8 sim. BPS distances: cycle-time EMD 239.4 s, arrival EMD 364.4 s, 2-gram JSD 0.161.

## 3. Metamorphic relations (10 replications, common random numbers)

### Refined MR1 (bottleneck-migration-tolerant) — **PASS**

Per the confirmed user decision, MR1 is refined to two gating sub-checks; the strict version is retained as a documented, non-gating accepted exception.

| Sub-check | Criterion | Baseline | +1 cap (vgr_1) | Result |
|---|---|---|---|---|
| **MR1a** | Mean wait **at the augmented resource** strictly decreases | wait@vgr_1 = 34.0 s | 2.4 s | ✅ PASS |
| **MR1b** | End-to-end flow time (paired completed cases) not increased (ε = 0.1 s) | 844.6 s | 727.6 s | ✅ PASS |
| STRICT-MR1 (accepted exception, non-gating) | System-wide mean wait not increased | 30.8 s | 27.9 s | holds in this seed set |

**Accepted-exception diagnosis (why strict MR1 is not a model defect):** the capacity knob is correctly applied — wait at the augmented resource `vgr_1` collapses (64.5 s → 4.3 s in the original harness seed set; 34.0 s → 2.4 s in the refined oracle's seed set). The system-wide wait increase seen by the strict oracle is a **legitimate bottleneck-migration effect**: `hbw_2` wait rose 138 s → 264 s (original harness) / 124.8 s → 138.7 s (refined oracle) as the bottleneck migrates to the next most-constrained resource. End-to-end flow time **improves** in both formulations (578.9 s → 523.8 s original harness; 844.6 s → 727.6 s refined oracle, paired cases). The strict assertion therefore fails on a semantic that the system does not satisfy by design, not on a wiring or knob error; it is documented, reported, and non-gating.

**Harness note:** the environment's metamorphic harness is a fixed tool with no editable source in the tree, so the refined oracle was implemented as a standalone, self-contained, deterministic script `metamorphic_mr1_refined.py` (10 replications, seeds 1..10, common random numbers, imports `simulation` unmodified, paired flow comparison). The coding agent's toolset could not write the file to disk; the **complete source is preserved in `execution_results.md`** (section "Run command and output") and can be saved to `reports/simulation/metamorphic_mr1_refined.py` and run with `python metamorphic_mr1_refined.py`. The identical logic was executed to produce the numbers above.

### Unchanged relations — **PASS**

| Relation | Result | Evidence |
|---|---|---|
| MR2: ARRIVAL_RATE_SCALE=1.5 must not decrease cases entered or mean WIP | ✅ PASS | entered 39.5 → 57.9; WIP 5.24 → 10.75 |
| MR3: FAILURES_ENABLED=False → failure rate 0, flow not increased | ✅ PASS | fail 0.013 → 0.0; flow 578.9 → 506.1 |
| MR4: SIMULATION_TIME ×2 → cases entered roughly scales (≥1.5×) | ✅ PASS | 39.5 → 76.2 (1.93×) |

The built-in harness still reports the *strict* MR1 as "fail" (wait 35.5 → 45.7, flow 578.9 → 523.8) because its source is not editable; that result is superseded by the refined MR1a/MR1b above per the user's confirmed decision.

## 4. Spec ↔ code findings

- **Arrivals:** `two_regime_bursts` implemented exactly (burst-size categorical [1,2,3,5,9] with spec probabilities; intra-burst IAT and inter-burst gaps from the spec empirical-quantile tables; first burst at t=0; all gaps divided by `ARRIVAL_RATE_SCALE` read at call time). No trace replay.
- **Variants:** all 9 variants with exact per-step resource probabilities, concurrency flags, and spec duration distributions (incl. `/ov/burn` uniform 21.421+20.111 s — actual behaviour, not the planned 222 s).
- **Concurrency:** concurrent step-groups spawn as parallel SimPy processes starting together with the preceding step; the main process waits for all before the next sequential step — matches the spec's 4 intra-case concurrency pairs.
- **Queue discipline:** `hbw_1`/`hbw_2` priority queues with spec priority order (`/hbw/store_empty_bucket` > `/hbw/unload`, FIFO tie-break); all other resources FIFO — matches `control_policies`.
- **Failures/retry:** `/hbw/unload` (0.0541) and `/vgr/pick_up_and_transport` (0.0288) fail and retry on the same resource, logging a `failure` row then a `success` row; gated by `FAILURES_ENABLED` (verified by MR3).
- **Handoff delay:** `vgr_to_hbw_handoff_delay` (empirical quantiles, mean 3.55 s) on `hbw_1` at the verified per-variant insertion points — not folded into vgr service time, per spec.
- **Early-exit semantics:** per-case draw using the spec's `early_exit_probability` + `early_exit_after_n_steps` (the spec-authoritative interpretation; yields 35.2% completion vs observed 35% = 13/37, whereas a per-step roll would give ~7% and contradict the data).
- **Knobs:** `SIMULATION_TIME`, `ARRIVAL_RATE_SCALE`, `FAILURES_ENABLED`, and `RESOURCE_CAPACITIES` all read inside `run_single_replication`; single `np.random.default_rng(seed)` plus `random.seed`/`np.random.seed` for contract compliance; no file I/O, no cross-call state.

## 5. Remaining discrepancies (all within the 95% PI; structural, not fixable without deviating from spec numbers)

1. **flow_time +33% / time_in_system +25%:** driven by elevated utilisation of the shared exchange-point resources (vgr_1 +12 pp, hbw_2 +10 pp) and the serial handoff-delay steps at hbw_1. Structural consequence of the spec's exact distributions and the shared hbw/vgr topology.
2. **overlapping_steps/case −38% (0.90 vs 1.46):** early exits terminate cases before their later concurrent step-pairs, reducing observed overlap.
3. **Per-class waiting skew:** sim under-waits at hbw (92 vs 178 s) and over-waits at vgr (33 vs 19 s) and hw (10 vs 3 s); under-waits at wt (0.2 vs 6.5 s). Net effect stays within PI; reflects the pooled per-activity service-time fits (spec assumption: pooled values used as planned) and the bursty arrival structure.
4. **release_spacing_median 4.8 s vs 1.6 s:** the burst structure (inter-burst gaps mean 419 s) makes the median over all release spacings higher than the intra-burst-only observed median.
5. **`/dm/cylindrical_drill` never simulated:** alternate WF_1106 route, not part of the linear main sequence (expected contract warning).

## 6. Reproducibility

`run_single_replication(seed)` is fully deterministic per seed (single `np.random.default_rng(seed)`); results are identical across repeated calls with the same seed, and this round's behavioural/contract results match the previous round exactly, confirming the model was not modified.
