# Execution Results — fischertechnik_lab_C digital twin

Model: `simulation.py` (compiled deterministically from the typed simulation spec by the
SimPy compiler). Output contract v2. Window 2021-07-01 18:48:23 → 20:19:24 UTC (≈5,461.5 s).

## 1. Smoke run (execute_simulation, seed 1)
- Status: **OK** — ran without error, returned a non-empty DataFrame.
- Rows: **582**, distinct cases: **52**.
- Activity row counts (seed 1):
  /vgr/pick_up_and_transport 171, /wt/pick_up_and_transport 42, /ov/burn 41,
  /hbw/store_empty_bucket 49, /hbw/unload 52, /hbw/get_empty_bucket 30, /hbw/store 26,
  /hw/human_review 34, /sm/transport 31, /mm/deburr 20, /mm/drill 12, /mm/transport_from_to 12,
  /ov/temper 10, /mm/mill 10, /dm/lower 9, /dm/drill 6, /sm/sort 13, /pm/punch_gill 5,
  /pm/punch_recesses 4, /pm/punch_ribbing 3, /dm/cylindrical_drill 2.
- Columns present (exact contract v2): case_id, variant, activity, resource, case_arrival,
  queue_enter, time:timestamp, operation_end_time, lifecycle:state.

## 2. Output contract v2 (run_contract_test)
- **PASS** — 25/25 checks. (A first run reported `import_is_side_effect_free` at 5.12 s due to a
  cold scipy/pandas import cache; the re-run passed with no side effects and no printed output.)
- Required symbols present: run_single_replication, RESOURCE_CAPACITIES (15 resources, all cap 1),
  SIMULATION_TIME, ARRIVAL_RATE_SCALE, FAILURES_ENABLED, MAX_ATTEMPTS.
- Event-log columns, numeric times, ordering (operation_end_time ≥ time:timestamp ≥ queue_enter),
  per-seed reproducibility, resource vocabulary/capacities, activity/variant vocabulary all verified.
- No hard-coded observed case ids, no file I/O, knobs read at call time.

## 3. Behavioural check vs observed training log (30 replications)
- **Verdict: FAIL** (rule: PASS if all |bias| ≤ 20% on completed_cases, flow_time_completed_s,
  time_in_system_all_s, overlapping_steps_per_case; FAIL if any > 50%).
- Headline biases:
  - completed_cases: sim 25.9 vs observed 13 → **+99.2%** (outside 95% PI [17.4, 35.3])
  - flow_time_completed_s: sim 951.7 vs observed 597.5 → **+59.3%**
  - time_in_system_all_s: sim 733.0 vs observed 430.6 → **+70.2%**
  - overlapping_steps_per_case: sim 1.31 vs observed 1.46 → **−10.5%** (within tolerance)
  - cases_entered: sim 46.2 vs observed 37 → +24.9%
  - mean_wip: sim 9.11 vs observed 6.07 → +50.1%
  - wip_at_T: sim 20.3 vs observed 24 → −15.4%
  - failure_rate: sim 0.013 vs observed 0.013 → −2.7% (good)
  - activity MAPE 5.2%, variant JSD 0.041, utilisation MAE 7.4 pp (good)
- Waiting by resource class (observed → sim): vgr 19.4 → **100.8 s** (large), hbw 177.9 → 103.2 s,
  hw 3.1 → 9.5 s, wt 6.5 → 0.3 s, dm 3.0 → 0.6 s, mm 4.8 → 0.2 s, ov 5.0 → 2.0 s, pm 3.2 → 0.3 s, sm 2.5 → 0.2 s.
- Distances: cycle-time EMD 379.8 s, arrival EMD 262.6 s, 2-gram JSD 0.096.
- Findings: sim over-produces completed cases (+99%) and over-states flow/time-in-system (+59/+70%);
  vgr is a severe bottleneck in the sim (101 s vs 19 s observed); release spacing is close
  (median 1.8 s vs 1.6 s observed).

## 4. Most-likely spec elements responsible for out-of-tolerance KPIs
The compiler implements the **structured** spec exactly. The two largest structural gaps are in the
free-text `assumptions`, which the compiler does not parse into code:

1. **Rework branch NOT implemented** (`assumptions`, second-to-last bullet: p_rework = 1/17 after
   every /hw/human_review → WF_104 rework sequence). The compiled `case_process` walks the variant
   step list linearly with no rework loop. Because rework adds ~10 extra steps (incl. several vgr
   steps) and delay, its absence makes cases flow faster and complete sooner → contributes to
   **completed_cases** and **flow_time** mismatches and under-loads vgr.
2. **Renormalized variant mix / WF_104 exclusion NOT implemented** (`assumptions`, last bullet).
   The compiled model uses the raw `variants[].probability` (which sums to 1.0 and **includes
   WF_104 at 0.0811**), so WF_104 — a long 24-step variant — is an arrival variant. This inflates
   **cases_entered**, **completed_cases**, **flow_time**, **time_in_system**, **mean_wip**, and
   vgr waiting (WF_104 has 8 vgr steps).

Per-KPI attribution:
- **completed_cases (+99%)** → `arrivals` (two_regime_bursts volume: 46 vs 37 entered) + `variants`
  (WF_104 included) + `assumptions` (rework branch missing).
- **flow_time_completed_s (+59%)** → `variants` (WF_104 long routing) + `activities`
  (/vgr/pick_up_and_transport, triang mean 36.3 s / max 52.5 s) + `control_policies` (vgr FIFO queueing).
- **time_in_system_all_s (+70%)** → same as flow time + `arrivals` (higher WIP).
- **mean_wip (+50%)** → `arrivals` (more cases) + slower flow (`variants`/`activities`).
- **vgr waiting (101 s vs 19 s)** → `activities` (/vgr/pick_up_and_transport duration) + `variants`
  routing (many vgr steps per case, WF_104 included) + `control_policies` (vgr FIFO).
- **overlapping_steps_per_case (−10%, in tolerance)** → `control_policies.intra_case_concurrency`
  (concurrency slightly under-represented).

## 5. Interpretation decisions (as compiled)
- **Priority values (hbw)**: `PriorityResource` for hbw_1/hbw_2; priority = index in
  `control_policies.priority_order.hbw` → /hbw/store_empty_bucket = 0 (highest), /hbw/unload = 1,
  all other hbw activities (/hbw/store, /hbw/get_empty_bucket) = 2 (neutral). vgr_1/vgr_2 = plain
  FIFO `Resource`.
- **Early-exit coin timing**: rolled **once per case at case start** (before step 0). If triggered,
  `exit_after` = key of `early_exit_after_n_steps`; the case returns when `done >= exit_after`.
  Note: for WF_101 the spec key is "0", so the compiled model exits **before executing any step**
  (0 logged rows for those cases). This differs from the task's prose "after step index 0 (after
  /hbw/unload completes)" — a spec-field vs prose ambiguity in `variants.WF_101.early_exit_after_n_steps`.
- **Failures**: on failure one row is logged (lifecycle:state='failure', service time still drawn and
  consumed) and the case is **scraped immediately** (no retry), gated on FAILURES_ENABLED.
- **Concurrency**: a step with `concurrent_with_previous: true` is spawned as a background process as
  soon as its resource is free; the next non-concurrent step waits for both the previous and any
  concurrent step to finish.
- **Service times**: sampled per activity (pooled across resource instances) from the fitted
  distributions (triang / uniform / empirical_quantiles).
- **Arrivals**: generated from the fitted two_regime_bursts model (initial burst 9; then categorical
  burst sizes; intra-burst IAT and inter-burst gaps from empirical quantiles), all divided by
  ARRIVAL_RATE_SCALE. No replay of observed timestamps.

## 6. Note on scope
Per the build procedure the model is compiler-generated from the structured spec and is not hand-edited;
the spec is not modified. The two `assumptions`-only features (rework branch, renormalized mix / WF_104
exclusion) are not represented in the compiled code and are the primary drivers of the behavioural FAIL.
If those are required, the spec must be changed (e.g., move the rework branch and the renormalized
arrival mix into structured fields) and steps 1–4 re-run.