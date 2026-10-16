# Execution Results — fischertechnik_lab_A / wandering-flying-bee

Regenerated `simulation.py` (2310 lines) from the current spec via the deterministic compiler. Output contract v2 intact: module-level `run_single_replication(seed)`, `RESOURCE_CAPACITIES`, `SIMULATION_TIME` (= 3183.202249 s from `window.horizon_s`), `ARRIVAL_RATE_SCALE`, `FAILURES_ENABLED`; all knobs read at call time; no file I/O; no state across calls; generated `case_{i}` ids only.

## 1. Smoke test (seed 1)

`python -c "import simulation; df = simulation.run_single_replication(1); print(len(df), df['case_id'].nunique())"` → **`344 26`** (344 event rows, 26 unique cases). Run completes within the 3183 s horizon (`env.run(until=SIMULATION_TIME)`).

Activity counts (seed 1): /vgr/pick_up_and_transport 109, /wt/pick_up_and_transport 26, /hbw/store_empty_bucket 27, /hbw/unload 25, /ov/burn 22, /hw/human_review 19, /mm/deburr 19, /hbw/get_empty_bucket 18, /hbw/store 14, /sm/transport 14, /sm/sort 13, /mm/mill 11, /ov/temper 7, /mm/drill 6, /pm/punch_gill 4, /pm/punch_recesses 4, /pm/punch_ribbing 4, /dm/lower 2.

## 2. Contract test (v2) — 25/26 passed

- **FAILED: `import_is_side_effect_free`** — import took 5.30 s (threshold ~0). No output (0 chars) and no simulation work at import time (all work is inside `run_single_replication`); the latency is scipy/numpy/simpy import cost in this environment, not a side effect.
- Warning: spec activities never emitted in seed 1: `/dm/cylindrical_drill`, `/mm/transport_from_to` (rare branches, n=2 each — expected at low probability).
- All other checks passed: required symbols (incl. `ARRIVAL_RATE_SCALE`, `FAILURES_ENABLED`), event-log columns, numeric times, ordering invariants, reproducibility per seed, resource capacities, activity/variant vocabulary, no hard-coded observed ids, no file I/O, knobs read at call time.

## 3. Behavioural check (30 replications vs observed window) — **FAIL**

Rule: PASS if all |bias| ≤ 20% on headline KPIs; FAIL if any > 50%.

| KPI | Observed | Sim mean | 95% PI | Bias |
|---|---|---|---|---|
| completed_cases | 3 | 15.03 | [12, 17] | **+401%** |
| cases_entered | 18 | 22.83 | [19.2, 27.3] | +27% |
| wip_at_T | 15 | 7.80 | [2.9, 12.6] | **−48%** |
| flow_time_completed_s | 656 | 1359 | [1001, 1630] | **+107%** |
| time_in_system_all_s | 660 | 1188 | [908, 1400] | **+80%** |
| overlapping_steps_per_case | 1.667 | 0.883 | [0.52, 1.43] | **−47%** |
| failure_rate | 0.042 | 0.047 | [0.026, 0.067] | +13% (in PI) |
| mean_wip | 7.09 | 9.72 | [6.8, 12.9] | +37% (in PI) |
| activity Mape | — | 10.2% | [5.0, 19.9] | — |
| variant JSD | — | 0.084 | [0.02, 0.21] | >0.05 |
| utilization MAE | — | 10.0 pp | [7.6, 12.4] | — |

Waiting by class (s): hbw obs 289 vs sim 54; vgr obs 26 vs sim 225; sm obs 3 vs sim 9; mm obs 6 vs sim 0.1; idle_s obs 261 vs sim 832 (+219%). Distances: cycle-time EMD 697 s, arrival EMD 255 s, 2-gram JSD 0.122.

Findings: completed_cases, cases_entered, wip_at_T, flow_time, time_in_system, overlapping_steps, idle_s all outside PI; hbw waiting under-modeled; vgr waiting over-modeled; variant mix JSD 0.084 > 0.05.

## 4. Spec elements most likely responsible (compiler implements spec exactly — these are spec decisions)

1. **`initial_state` (empty at t0) + `arrivals` (two_regime_bursts, infinite, ~1 release/226 s)** — primary driver of completed_cases (+401%), wip_at_T (−48%), time_in_system (+80%), idle_s (+219%), hbw waiting. The observed window is mid-stream: 15 of 18 observed cases are right-censored (only 3 completed in-window). A simulation starting empty at t0 fills up and completes ~15 cases by T; it also idles during the ~377 s inter-burst gaps. Fix candidates: seed `initial_state.cases_in_progress` with the in-flight cases at t0, and/or model the observed 18 releases as a finite-window draw (censoring) rather than an infinite process.
2. **`variants[].steps[].concurrent_with_previous` flags** — driver of overlapping_steps_per_case (−47%) and flow_time (+107%). The assumption text says "the next step is requested before the previous releases its resource; model as concurrent SimPy processes," but only a few steps carry the flag, so the compiled engine serializes most steps.
3. **`activities` durations — `/vgr/pick_up_and_transport` pooled distribution (mean 41.97 s incl. 88.4 s max and 5 failed-attempt retries, flagged) and `/mm/mill` (mm_2 outlier 14.4 s)** — driver of vgr waiting (sim 225 s vs obs 26 s): with fewer concurrent overlaps, the 2-vgr FIFO pool saturates. Per-resource or retry-excluded duration splits were flagged in assumptions for the modeling stage.
4. **`arrivals.intra_burst_iat` / release spacing** — release_spacing_median sim 7.5 s vs obs 2.0 s (secondary; lognorm mean 1.589 s is correct, the median gap between consecutive releases across burst boundaries inflates the sim median).

## 5. Deviations

- Contract check `import_is_side_effect_free` fails on import latency (5.30 s) — environmental (scipy import), no side effects or output; not fixable by spec change.
- Behavioural verdict FAIL — see §4 for the spec-level change requests.
