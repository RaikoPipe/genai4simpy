# Extraction Plan Report — fischertechnik_lab_C (run: foamy-ancient-hornet), Phase 3

## 1. Data Basis

- Canonical dataset: `eventlog_cleaned.parquet` — 1,137 rows, 379 activity instances, 37 cases, 21 activities, 15 resources, horizon ≈ 5,461.5 s (~91 min).
- **Service time** = `operation_end_time` − `time:timestamp` on the **start row only** (excludes queueing).
- **`complete_service_time`** (scheduled → complete, incl. queueing) is the **actual** end-to-end response time; **`planned_operation_time`** is the **target** — used for benchmarking, not for service-time extraction.
- Censoring: 0 left-censored, 0 right-censored. The 24 incomplete-interior cases are real scrap/abandonment (early exits) and are **retained** for estimation. The only row-level exclusion is the **0.03 s `/hbw/unload` outlier** (confirmed data error).

## 2. Parameter Extractions Required

### 2.1 Service times — per activity (21 activities)
- **Grouping: per activity, pooled across resources.** The topology shows no resource-specific behaviour (mm_1/mm_2 and ov_1/ov_2 execute the same operations with no evidence of differing durations); per-activity × resource splits would leave ~9 samples per cell. Report per-resource breakdowns as a sanity check only.
- Source: start-row durations from the cleaned log, all 379 instances (no censored cases to drop).
- Caveats:
  - **`/ov/burn`: use the observed actual mean (~31 s), not the planned 222 s** — the twin models actual behaviour.
  - **`/hbw/unload`: exclude the 0.03 s outlier instance** from all statistics and fits.
  - **Small-sample activities** (e.g. `/pm/punch_gill`, `/dm/cylindrical_drill`, `/ov/temper`, `/dm/lower`, `/pm/punch_recesses`, `/pm/punch_ribbing` — n < ~5): report with wide uncertainty; fall back to mean/constant values where fitting is not statistically meaningful.
- Benchmark: per-activity comparison of actual (`complete_service_time`) vs target (`planned_operation_time`).

### 2.2 Failure / early-exit probabilities
- **Already fixed in the spec from the topology phase** — no new extraction: per-variant `early_exit_probability` and `early_exit_after` (WF_101 0.5, WF_102 0.6, WF_103 0.6, WF_104 1.0, WF_105 0.5, WF_108 0.667, WF_109 0.333, WF_1106 0.833, WF_1107 0.75), the WF_1106 drill branch (60/40), and the WF_104 rework cap (3 iterations).
- **Per-activity failure rates**: only 5 failures in 379 instances (NFC 418 on `/vgr/pick_up_and_transport`, missing-workpiece 401 on `/hbw/unload`) — too sparse to estimate per-activity failure distributions; retain as observed event rates and refine in calibration.
- **WF_104 rework pass/fail probability**: not estimable from 3 cases — deferred to the calibration phase.

### 2.3 Arrival / release process
- **Single global arrival process into hbw** (exogenous, operator-driven batch releases — confirmed not completion-triggered, no WIP cap).
- Source: `scheduled` timestamps of each case's first activity (`/hbw/unload`) — 37 releases.
- Structure to extract/fit: bursty batches — **12 bursts, mean batch size ≈ 3.08, within-burst IAT mean ≈ 1.97 s, inter-burst gap mean ≈ 418.8 s** (min 33.3 s, max 989.3 s).
- After arrival, cases are **split into variants by process-model proportions** already in the spec (WF_101 0.1081, WF_102 0.1351, WF_103 0.1351, WF_104 0.0811, WF_105 0.1081, WF_108 0.0811, WF_109 0.0811, WF_1106 0.1622, WF_1107 0.1081).

### 2.4 vgr → hbw hand-off delay
- Modelled as an **explicit transfer delay between vgr and hbw; NOT folded into vgr service time** (50.5% of hbw waiting time is extraneous — resource idle while the case waited).
- Estimate from data: for hbw instances where the resource was idle at the time of waiting, the gap between the **completion of the preceding vgr step** and the **hbw start**. Report mean and distribution; this value is the magnitude of the hand-off delay in the model.

### 2.5 Quantities / quality
- **Skipped — no meaningful quantity or quality columns exist.** `parameters.quantity` is constant (single workpiece per case); `human_workstation_green_button_pressed` is an initial-state flag, not an outcome (2 instances with flag = 0 still completed successfully).

## 3. Agent Deployment Recommendation

| Sub-Agent | Deploy? | Reason / Data & Caveats |
|---|---|---|
| durations-processing-times-agent | **Yes** | Per-activity service times from start-row durations (operation_end_time − timestamp), pooled across resources; plus complete_service_time vs planned_operation_time benchmark; plus vgr→hbw hand-off delay estimation (hbw start − preceding vgr completion where hbw was idle). Caveats: exclude the 0.03 s `/hbw/unload` outlier; `/ov/burn` uses actual (~31 s), not planned (222 s); do not fold hand-off delay into vgr times. |
| inter-arrival-times-agent | **Yes** | Single global batch arrival process into hbw from the 37 first-step scheduled timestamps; fit burst structure (12 bursts, batch size ≈ 3, within-burst IAT ≈ 1.97 s, gap ≈ 418.8 s); variant split uses the spec proportions. |
| quantities-quality-agent | **No** | No sim-relevant quantity/quality columns (quantity constant; green-button flag is context, not an outcome). |
| distribution-fitting-agent | **Yes** | Fit distributions to (a) per-activity service times, (b) the arrival process (batch size, within-burst IAT, inter-burst gap), (c) the hand-off delay. Caveats: exclude the 0.03 s outlier; small-sample activities (n < ~5) get mean/constant fallback with reported uncertainty; burn fitted to actual data only. |

## 4. Exclusions, Skips, and Deferred Items

- **Excluded from fitting**: the single 0.03 s `/hbw/unload` instance (data error).
- **No censored cases** to exclude; early-exit cases (scrap/abandonment) are retained for service-time and arrival estimation.
- **Skipped**: quantities/quality extraction (no qualifying columns); per-activity × resource service-time splits (no resource-specific behaviour in the topology; sample sizes too small).
- **Deferred to calibration**: WF_104 rework pass/fail probability (3 cases, not estimable); per-activity failure rates (5 events, too sparse).
