Here is the context on how to interpret the data from the manufacturing event logs:

Phase 1 — Data Analysis

- Compute actual duration from start-transition events only: actual_duration is operation_end_time − time:timestamp
  where lifecycle transition is 'start'. Do not use complete_service_time - it measures the full scheduled-to-complete span which includes queueing delay, not service time.
- Retain planned_operation_time even though actual complete service time supersedes it (low priority, keep for reference).
- Parse the parameters string-dict into separate columns: start_position, end_position, quantity, workpiece_size.
- Keep response_status_code — it provides failure-type detail (401 auth, 418 precondition) beyond lifecycle:state.
- Drop human_workstation_green_button_pressed (sparse, out of scope).
- Proceed with cleaning and save the cleaned event log to parquet. No row/duplicate removal.

Phase 2 — Topology Analysis

- Treat the end-of-process warehouse-return sequence (hbw_1/get_empty_bucket, hbw_1/store, associated vgr transports) as canonical for every variant. Any absence is time-window truncation, not optionality.
- WF_104 cross-line routing is intentional (two-stage design). Allow cross-line routing for this variant only.
- Enforce role-based VGR assignment: vgr_2 performs the first transport, vgr_1 the rest (honor the documented exceptions in source data).
- Model sorting ejection position as stochastic (uniform over {1,2,3}).
- Exclude the 4 incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) from routing inference only; retain them elsewhere.
- Model the 8 failure events (418/401) as retryable: operation retries and eventually succeeds; workpiece continues.

Phase 3 — Extraction Planning

- Model inter-arrivals as two-phase: initial near-simultaneous burst (first 8 cases) followed by steady-state arrivals, as reflected in the data.
- For sparse processing times, pool only machine pairs performing the same activity. Never pool across different activities.
- Use a single transport-time distribution per VGR resource (pool identical hardware); flag this for revisit at the modeling stage.
- Model failures with per-activity rates. Treat 418 and 401 as a single unified retry mechanism that triggers a re-attempt.
- burn_workpiece_size is context-dependent — separate by activity: at /ov/burn it is categorical and deterministic per variant; at drill steps it is numeric.
- Event semantics: one event_id = one attempt; the complete row is terminal. A retry appears as a new event_id and simply repeats the same process.