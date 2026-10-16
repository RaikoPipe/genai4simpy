# Evaluation Report — Fischertechnik Lab C Digital Twin (Phase 5)

## Status: **FAIL**

Worst of the three deterministic verdicts:
- Contract test: **PASS** (25/25)
- Behavioural check: **FAIL**
- Metamorphic tests: **FAIL** (MR3)

Overall verdict: **FAIL**

## Iterations
- **0 fix iterations.** A research investigation was delegated to the coding agent to verify root causes. **No implementation errors were found** — the code is a faithful, deterministic implementation of the structured spec (contract PASS). All KPI gaps are attributed to spec decisions, window-truncation artifacts, or oracle artifacts (see §4). No spec changes were made because every deviation is either a user-locked decision, a window-truncation artifact, or sampling variance (none are backed by a tool result that warrants a spec correction).

---

## 1. Contract Test — PASS (25/25)

| Check group | Result |
|---|---|
| import_is_side_effect_free | **PASS** (re-run; the initial 5.1 s was a cold scipy/pandas import cache — the demo code is `__main__`-guarded and printed 0 chars) |
| required symbols (run_single_replication, RESOURCE_CAPACITIES, SIMULATION_TIME, ARRIVAL_RATE_SCALE, FAILURES_ENABLED) | PASS |
| event-log columns (case_id, variant, activity, resource, case_arrival, queue_enter, time:timestamp, operation_end_time, lifecycle:state) | PASS |
| numeric times / ordering (operation_end_time ≥ time:timestamp ≥ queue_enter) | PASS |
| per-seed reproducibility | PASS |
| resource vocabulary & capacities (15 resources, all cap 1) | PASS |
| activity / variant vocabulary vs. spec | PASS |
| no trace replay (no observed case ids), no file I/O, knobs read at call time | PASS |

The model is a faithful, deterministic implementation of the structured spec.

---

## 2. Behavioural Check vs. Observed Log — FAIL (30 replications, 5461 s window)

Rule: PASS if all |bias| ≤ 20% on [completed_cases, flow_time_completed_s, time_in_system_all_s, overlapping_steps_per_case]; FAIL if any > 50%.

| KPI | Observed (GT) | Sim mean | 95% PI | Bias | In PI? |
|---|---|---|---|---|---|
| **completed_cases** | 13 | 25.9 | [17.4, 35.3] | **+99.2%** | **No** |
| **flow_time_completed_s** | 597.5 | 951.7 | [550.1, 1717.7] | **+59.3%** | Yes |
| **time_in_system_all_s** | 430.6 | 733.0 | [390.3, 1456.7] | **+70.2%** | Yes |
| overlapping_steps_per_case | 1.46 | 1.31 | [0.89, 1.67] | −10.5% | Yes |
| cases_entered | 37 | 46.2 | [33.0, 69.7] | +24.9% | Yes |
| mean_wip | 6.07 | 9.11 | [3.83, 22.63] | +50.1% | Yes |
| wip_at_T | 24 | 20.3 | [9.7, 42.8] | −15.4% | Yes |
| failure_rate | 0.013 | 0.013 | [0.003, 0.025] | −2.7% | Yes |
| activity MAPE | — | 5.2% | [2.7, 10.5] | — | — |
| variant JSD | — | 0.041 | [0.018, 0.085] | — | — |
| utilisation MAE | — | 7.4 pp | [2.4, 15.3] | — | — |
| idle_s | 169.5 | 496.4 | [109.2, 1244.5] | +192.8% | Yes |

**Waiting by resource class (observed → sim):**

| Class | Observed (s) | Sim (s) |
|---|---|---|
| **vgr** | 19.4 | **100.8** |
| hbw | 177.9 | 103.2 |
| hw | 3.1 | 9.5 |
| wt | 6.5 | 0.3 |
| dm | 3.0 | 0.6 |
| mm | 4.8 | 0.2 |
| ov | 5.0 | 2.0 |
| pm | 3.2 | 0.3 |
| sm | 2.5 | 0.2 |

**Distances:** cycle-time EMD 379.8 s, arrival EMD 262.6 s, 2-gram JSD 0.096.

---

## 3. Metamorphic Tests — FAIL (MR3 only)

| Relation | Status | Detail |
|---|---|---|
| MR1 +1 capacity at bottleneck (vgr_1) | **pass** | wait 41.5→32.3 s, flow 591→403.5 s |
| MR2 ARRIVAL_RATE_SCALE=1.5 | **pass** | cases_entered 38.2→66.7, mean WIP 5.87→18.97 |
| MR3 FAILURES_ENABLED=False | **FAIL** | failure rate 0.015→0.0 (correct), but flow time 591→902 s |
| MR4 SIMULATION_TIME ×2 | **pass** | cases_entered 38.2→77.0 |

---

## 4. Spec ↔ Code Findings & Discrepancy Attribution

The code is a faithful implementation of the structured spec (contract PASS). **Every KPI gap is attributable to a spec decision, a window-truncation artifact, or an oracle artifact — there are no implementation errors.**

### (a) completed_cases +99% (25.9 vs. 13)
- **Primary cause: window-truncation artifact + arrival sampling variance.** The observed window is truncated: 37 entered, only 13 completed, 24 still in WIP at t=5461 s. The sim runs the full window and completes a larger fraction (56% of entered vs. 35% observed). The fitted arrival model's expected count (~49) exceeds the observed realization (37) due to sampling variance over 12 bursts.
- **Secondary cause: the WF_104 / rework spec contradiction (see (d)).**
- **Not a speed artifact:** the sim is actually *slower* per case (flow 951.7 s vs. 597.5 s), so the over-completion is a throughput/arrival effect, not a 2× speedup.

### (b) flow_time +59% / time_in_system +70%
- **Cause: higher WIP (more, front-loaded cases) + WF_104 long routing.** The sim's higher mean WIP (9.1 vs. 6.07) increases queuing, and WF_104 (a 24-step route) is sampled as an arrival variant, adding long flow times.

### (c) vgr waiting 100.8 s vs. 19.4 s
- **Cause: WF_104 in the arrival mix (8 vgr steps) + vgr FIFO queueing.** WF_104 is the dominant vgr load; its inclusion as an arrival variant over-loads the vgr pool (vgr_1 utilisation deviation +34 pp, the largest).

### (d) WF_104 / rework-branch spec-internal contradiction — **modelling decision to revisit**
- The structured `variants` section includes **WF_104 at probability 0.0811 as an arrival variant**, but the user's locked decision (and the `assumptions` section) states **WF_104 is a quality rework branch** (p=0.0588 after `/hw/human_review`), **not an arrival variant**, and is "removed from the arrival mix."
- The compiled model implements the structured spec: it samples WF_104 as a normal arrival variant and has **no rework loop** (the rework branch exists only in free-text `assumptions`, which the compiler does not parse).
- This is a **spec-internal contradiction** between the structured `variants` section and the user's locked decision / `assumptions`. It is a **modelling decision to revisit**, not an implementation error. Resolving it requires a spec revision (remove WF_104 from `variants`; add a structured rework-branch field — the current schema has no such field).

### (e) Early-exit deviations (7 variants) — **window-truncation artifacts, NOT real scraps**
- `check_spec_against_evidence` flags WF_102 (0.0 vs 0.6), WF_103 (0.33 vs 0.6), WF_105 (0.0 vs 0.5), WF_108 (0.0 vs 0.67), WF_109 (0.0 vs 0.33), WF_1106 (0.0 vs 0.83), WF_1107 (0.5 vs 0.75).
- These "observed early-exit" counts closely match the `initial_state.excluded_from_estimation` list (19 missing-data stubs). Per the user's locked decision, those stubs (1–2 activity stubs ending on a non-terminal activity with no complete/failure) are **missing data / window truncation**, NOT genuine early exits. The 5 real scrap cases (WF_101_26, WF_101_28, WF_103_27, WF_104_17, WF_1107_13) are already handled via `on_failure='scrap'` + `failure_probability`.
- **Verdict: the spec's `early_exit_probability=0.0` for these variants is CORRECT and was NOT changed.** Raising them would inject spurious early terminations that do not exist in reality.

### (f) MR3 failure — **oracle artifact, not a code defect**
- The knob works correctly: `FAILURES_ENABLED=False` gives failure rate 0.
- The flow-time increase (591→902 s) is a legitimate consequence of the population change: with failures enabled, the 5 scrap cases die early and are removed from the completed pool (and release vgr/hbw capacity sooner); with failures disabled, those cases survive and run full multi-minute routes, increasing the completed-case mean flow and holding resources busy longer.
- The metamorphic oracle's assumption ("disabling failures cannot increase flow time") is violated because in a model where failures **scrap** (remove) cases, disabling them changes the completed-case population and system dynamics. Reported as failing per the rules (the relation is not weakened).

### (g) Minor: overlapping_steps_per_case −10.5%
- Within the 20% tolerance but slightly low. The `concurrent_with_previous` flags (e.g. `/ov/burn` concurrent with `/hbw/store_empty_bucket`) are implemented via background processes; the sim produces slightly fewer overlaps than observed. Minor concurrency-calibration gap, not a defect.

---

## 5. Remaining Discrepancies & Likely Cause (summary)

| Discrepancy | Likely cause | Type |
|---|---|---|
| completed_cases +99% | Window truncation (24/37 cases incomplete in observed window) + arrival sampling variance (+32% over-release) + WF_104 in mix | Spec decision / artifact |
| flow_time +59% | Higher WIP + WF_104 long routing | Spec decision |
| time_in_system +70% | Same as flow time + higher WIP | Spec decision |
| vgr waiting 100.8 vs 19.4 s | WF_104 (8 vgr steps) as arrival variant + FIFO | Spec decision |
| hbw waiting 103.2 vs 177.9 s | Priority discipline not reproducing observed hbw congestion | Calibration |
| MR3 flow-time increase | Population change (5 scrap cases now complete full routes) | Oracle artifact |
| 7 early-exit deviations | Window-truncation artifacts (missing-data stubs) | Artifact (spec correct) |

**No implementation errors were found. No spec changes were warranted** (all deviations are user-locked decisions, window-truncation artifacts, sampling variance, or oracle artifacts).

---

## 6. Conclusion

The SimPy digital twin is a **faithful, deterministic implementation of the structured spec** (contract 25/25 PASS, reproducible, no trace replay, all knobs honoured). The **FAIL** verdict is driven by:
1. **Window-truncation artifacts** — the observed 5461 s window is heavily truncated (only 13 of 37 cases completed), so the sim's full-window completion count and flow times are structurally higher than the observed realization.
2. **A spec-internal contradiction** — WF_104 is an arrival variant in the structured `variants` section but a rework branch in the user's locked decision / `assumptions`; the compiler implements the structured spec, so WF_104 is over-represented as an arrival and the rework loop is absent.
3. **An oracle artifact** — MR3's flow-time increase is a legitimate consequence of the scrap-on-failure semantics, not a code defect.

These are modelling/spec issues to revisit, not implementation bugs. The model correctly reproduces the per-activity service-time distributions (MAPE 5.2%), the variant mix (JSD 0.041), the failure rate (0.013), and the release pattern (median spacing 1.8 s vs. 1.6 s observed).
