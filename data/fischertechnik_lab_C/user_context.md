Here is the context on how to interpret the data from the manufacturing event logs:

Phase 1 — Data Analysis (column cleaning)

- Compute actual duration from start-transition events only: actual_duration is operation_end_time − time:timestamp
  where lifecycle transition is 'start'. complete_service_time records the full response time (scheduled to complete, including queueing delay).
- Confirmed dropping the listed columns.
- Treat planned_operation_time as the target, complete_service_time as the actual.
- Use parameters for context only, not directly for routing.

Phase 2 — Topology Analysis (process structure)

- WF_104 rework loop: treat as a quality rework loop (failed human review → reprocessed).
- Truncated cases: drop 1–2 activity stubs ending on non-terminal activity with no complete/failure (missing data); keep short sequences ending on a failure state (real scrap). Use lifecycle:state to disambiguate.
- WF_1106 variability: single process model with conditional routing.
- Resource class prefixes: confirmed correct.
- Two parallel tracks confirmed: ov_1/mm_1/wt_1/sm_1 vs ov_2/mm_2/wt_2/sm_2 are separate capacity pools (two production lines linked only for workpiece exchange). Exceptions: pm and hw are shop-floor-1 only, dm is shop-floor-2 only — single-instance, not paired. hbw and vgr: must check whether each track has its own or they're shared at the exchange point.

Phase 3 — Extraction Planning (parameter fitting)

- /ov/burn time: use actual observed mean (~31s), not planned (222s) — building a digital twin of actual behavior.
- Inter-arrival: single global arrival process (one order stream into hbw), then split by process-model proportions; 9 models are interleaved draws.
- WF_104 rework: treat as probabilistic branch after human review.
- /hbw/unload 0.03s outlier: data error.