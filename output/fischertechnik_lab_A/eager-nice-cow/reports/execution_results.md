# Execution Results — fischertechnik_lab_A / eager-nice-cow

Simulation file: `reports/simulation/simulation.py` (SimPy, output contract v2).

## Verification summary

| Check | Result |
|---|---|
| `execute_simulation` (seed 1) | PASS — 300 rows × 9 cols, 22 cases, 12 failure rows, 19 terminal `/hbw/store` completions; all sanity asserts (column set, time monotonicity `end ≥ start ≥ queue_enter ≥ arrival ≥ 0`, resource/variant/activity vocabulary, no observed case ids, every failure followed by a success on same case/activity/resource, occurrence-based routing-order check incl. concurrent joins) pass |
| `run_contract_test` (25 checks) | PASS — importable without side effects; required symbols incl. `ARRIVAL_RATE_SCALE`, `FAILURES_ENABLED`; event-log columns incl. `case_arrival`, `queue_enter`; numeric times; reproducibility per seed; resources in `RESOURCE_CAPACITIES`; activity/variant vocabulary; no hard-coded observed ids, no file I/O |
| `run_behavioural_check` (30 reps) | Partial match — see below |
| `run_metamorphic_tests` (10 reps) | PASS — MR1 (+1 vgr_1 capacity reduces wait 41.1→13.6 s), MR2 (ARRIVAL_RATE_SCALE=1.5: cases 24.4→30.9, WIP 7.35→11.31), MR3 (FAILURES_ENABLED=False: failure rate 0, flow 864→810 s), MR4 (2× horizon: cases 24.4→42.4) |

## Behavioural check (30 replications vs observed window)

| KPI | Observed | Sim mean (95% PI) | Notes |
|---|---|---|---|
| completed cases | 3 | 16.9 (13.9–19.3) | Observed window is heavily truncated: 12/18 cases stop mid-window without the terminal activity (spec assumption: window truncation, not scrap). A full-horizon simulation of the same routing completes most cases. |
| cases entered | 18 | 23.8 (17.0–31.4) | PI covers observed; steady-state burst process draws gaps until the horizon, so counts vary with sampled gap tail (n=5 base). |
| WIP at end | 15 | 6.9 (0–17.5) | PI covers; observed end-WIP is inflated by truncation. |
| flow time (completed) | 656 s | 1018 s (695–1395) | Observed completed cases are the 3 that finished early; sim flow includes full routing (≈15 steps) for all completed cases. |
| failure rate | 0.042 | 0.037 (0.02–0.057) | PI covers. |
| overlapping steps/case | 1.67 | 0.91 (0.69–1.33) | Sim has one concurrent pair per case (the spec's 3 pairs only materialize on specific variants); observed value counts overlaps across the 3 complete cases. |
| mean WIP | 7.09 | 7.36 (4.6–11.8) | Close (bias +3.8%). |
| activity MAPE | — | 8.9% (4.1–15.6) | Good. |
| variant JSD | — | 0.085 | Small-sample mix noise (9 variants, 18 observed cases). |
| hbw waiting | 289 s | 31 s | Spec attributes 64% of observed hbw waiting to "extraneous" hand-off/transport/release delays with no machine contention — no distribution for these delays exists in the spec, so the sim cannot reproduce them. |
| vgr waiting | 26 s | 114 s | Sim vgr_1 utilization ~0.89 (bottleneck per MR1); observed window had fewer in-flight cases. |
| release spacing median | 2.0 s | 4.6 s | Phase-1 intra-burst IATs (median 0.90 s) are diluted by the 633 s transition gap and steady-state gaps in the pooled spacing. |
| cycle-time EMD | — | 374 s | Driven by the completed-cases flow-time gap above. |
| arrival EMD | — | 287 s | Driven by the transition gap / burst-tail sampling. |
| bigram JSD | — | 0.048 | Good routing match. |

No implementation errors were found in the behavioural check; the residual gaps are explained by (a) window truncation of the observed log (15/18 cases never reach the terminal activity in the observation), (b) the spec's documented "extraneous" hbw waiting with no modelable distribution, and (c) small-sample arrival parameters (n=5 gaps, n=4 intra-burst IATs). No spec numbers were tuned to hit KPIs.

## Binding constraints — implementation

1. **Service times** — all 19 activities sampled via `make_sampler` from the spec's finalized distributions (triang / norm / empirical_quantiles / constant), full distributions, never means.
2. **Per-resource conditioning** — `/sm/transport` (sm_1/sm_2 triang), `/wt/pick_up_and_transport` (wt_1/wt_2 triang), `/vgr/pick_up_and_transport` (vgr_1 norm, vgr_2 empirical quantiles) sampled from the split matching the resource actually used (`RESOURCE_DURATIONS` lookup in `sample_duration`).
3. **/sm/sort** — pooled triang kept AS-IS (c=0.015929, loc=8.36, scale=237.34); no cap, no slow-sort mode.
4. **Arrivals** — `two_regime_bursts` as two separate phases in one release process: Phase 1 = 8 cases, first at t=0, intra-burst IATs from the spec empirical quantiles; fixed transition gap 633.4968 s; Phase 2 = steady-state burst loop (burst_size categorical {1:0.5, 2:0.3333, 3:0.1667}, intra-burst IATs and inter-burst gaps from their empirical quantiles) drawing until the horizon. All IATs/gaps divided by `ARRIVAL_RATE_SCALE`.
5. **Variant mix** — each released case sampled from spec probabilities (0.1333 ×6, 0.0667 ×3), normalized.
6. **Routing** — per-variant step sequences transcribed exactly from spec `variants`, including the canonical terminal tail (… /hw/human_review → vgr_1 → /hbw/get_empty_bucket @ hbw_1 (concurrent) → vgr_1 → /hbw/store @ hbw_1) on every variant; WF_104 starts at /vgr/pick_up_and_transport; fixed resource per step; no early exits (early_exit_probability=0); in-progress cases truncated at horizon (no rows for unstarted steps).
7. **Intra-case concurrency** — `concurrent_with_previous` steps are spawned as a background process at the moment the previous step's service **starts** (spec evidence: "requested while the previous step still holds its resource", observed overlaps 26–39 s); the case joins (waits for the background process to finish) before the next sequential step. Pairs: /hbw/store_empty_bucket || /vgr/pick_up_and_transport, /hbw/store_empty_bucket || /ov/burn, /vgr/pick_up_and_transport || /hbw/get_empty_bucket.
8. **Queue discipline** — hbw_1/hbw_2 are `simpy.PriorityResource` with priority `HBW_PRIORITY_ORDER.index(activity)` (store 0 > store_empty_bucket 1 > get_empty_bucket 2 > unload 3); all other resources plain FIFO `simpy.Resource`.
9. **Failures** — per-activity `failure_probability` (store_empty_bucket 0.1333, unload 0.0588, vgr 0.0909 applied on vgr_1 attempts only, 0 on vgr_2 per per-resource evidence), gated by `FAILURES_ENABLED`; a failed attempt holds the resource for 0.1× the sampled service time, logs a 'failure' row, and the case immediately re-requests the same resource (geometric retries until success); no scrap.
10. **Quantity** — empirical PMF {4:0.273, 6:0.545, 8:0.091, 10:0.091} sampled for material-removal steps; stored as a case-state attribute only, no duration conditioning (not required).
11. **Initial state** — WIP at start = 0; system starts empty.

## Assumptions made where the spec was ambiguous

- **Concurrency trigger**: the spec text said "as soon as the previous step's resource is released" but the spec's own evidence says the concurrent step is "requested while the previous step still holds its resource" with measured 26–39 s overlaps. The evidence (binding, with actual overlap magnitudes) was followed: the concurrent step requests its resource at the previous step's service **start**.
- **Failed-attempt duration**: spec allows a short service; used 0.1× the sampled service time (deterministic rule, no new parameters).
- **Phase-2 continuation**: spec allows continuing the steady-state burst process beyond the 10 observed releases until the horizon; implemented that (draw bursts until `env.now ≥ horizon`), deterministic per seed.
- **Truncated retries**: if a case is still retrying at the horizon, the in-flight retry emits no row (only completed attempts are logged), consistent with "do not emit rows for steps not started".
- **Step probabilities**: all spec steps have probability 1.0; the skip-draw code path is present but never triggers.

## Sanity-check output (seed 1)

```
(300, 9)
  case_id  variant  ... operation_end_time lifecycle:state
0  case_2   WF_104  ...          45.101190         success
1  case_1   WF_105  ...          49.934403         success
2  case_2   WF_104  ...          85.197929         success
3  case_2   WF_104  ...          86.666280         success
4  case_3  WF_1106  ...          90.041994         failure
5  case_1   WF_105  ...          94.760014         success
6  case_2   WF_104  ...         115.754914         success
7  case_2   WF_104  ...         126.445645         success
8  case_4  WF_1106  ...         128.685702         success
9  case_1   WF_105  ...         132.169958         failure

rows: 300 | failures: 12 | cases: 22 | completed: 19
SANITY OK
```
