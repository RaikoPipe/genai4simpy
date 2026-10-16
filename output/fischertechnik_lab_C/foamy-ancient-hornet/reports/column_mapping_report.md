# Column Mapping Report — fischertechnik_lab_C (run: foamy-ancient-hornet)

## 1. Dataset Summary

- **Source**: `work_files/eventlog.parquet` (raw), cleaned output: `work_files/eventlog_cleaned.parquet`
- **Shape**: 1,137 rows × 20 columns → 1,137 rows × 13 columns after cleaning (0 rows removed, 7 columns dropped)
- **Structure**: lifecycle layout — exactly 3 rows per activity instance (`scheduled` → `start` → `complete`), 379 instances, 37 cases, 21 activities, 15 resources
- **Time span**: t0 = 2021-07-01 18:48:23 UTC, horizon T ≈ 5,461.5 s (~91 min)
- **Outcomes**: 374 success, 5 failure (all on `complete` rows)
- **Data quality**: no fully duplicate rows; no missing values in key columns; `parameters` has 1 missing (a `start` row of `/sm/sort`, event_id 2141); `human_workstation_green_button_pressed` populated only for `/hw/human_review` rows

## 2. log_schema (spec section)

Confirmed via `set_log_schema` (verified: 379 instances, 37 cases, 21 activities, 15 resources, `enabled_observed_frac = 1.0`, no warnings).

| Schema field | Column | Value / Notes |
|---|---|---|
| `case_col` | `case` | work-piece id, e.g. `WF_101_25` (37 unique) |
| `activity_col` | `concept:name` | activity name, e.g. `/vgr/pick_up_and_transport` (21 unique) |
| `resource_col` | `org:resource` | executing resource, e.g. `vgr_1` (15 unique) |
| `variant_col` | `process_model_id` | product variant / process model, e.g. `WF_101` (9 unique); 1:1 with `case` prefix |
| `start_col` | `time:timestamp` | timestamp of the row's lifecycle transition |
| `end_col` | `operation_end_time` | end of the operation for that row |
| `lifecycle_col` | `lifecycle:transition` | `scheduled` / `start` / `complete` |
| `instance_col` | `event_id` | links the 3 rows of one activity instance (379 unique, 1:1 with dropped `identifier:id`) |
| `enabled_value` | `scheduled` | queue entry / request |
| `start_value` | `start` | service start |
| `complete_value` | `complete` | service completion |
| `state_col` | `lifecycle:state` | `assigned` (scheduled), `inProgress` (start), `success` / `failure` (complete) |
| `success_values` | — | `["success"]` |
| `failure_values` | — | `["failure"]` |

### Duration semantics (authoritative decisions, recorded)

- **Actual duration** = `operation_end_time` − `time:timestamp` on the **`start` row only** (service time, excludes queueing). Observed: min 0.0 s, mean 31.2 s, max 185.1 s.
- **`complete_service_time`** = full response time from `scheduled` to `complete` (includes queueing delay). Verified exactly: `complete_service_time` == `operation_end_time(complete row)` − `time:timestamp(scheduled row)` for all 379 instances (max abs diff 0.0 s).
- **`planned_operation_time`** = target (planned) operation time per activity (22 distinct values, e.g. 00:00:46, 00:03:42).
- Waiting time (queueing) is observable as `time:timestamp(start row)` − `time:timestamp(scheduled row)`.

### Failure observations (5 instances)

| case | activity | resource | status code | note |
|---|---|---|---|---|
| WF_104_17 | /vgr/pick_up_and_transport | vgr_1 | 418 | NFC read failed (workpiece not at expected position) |
| WF_101_26 | /hbw/unload | hbw_2 | 401 | workpiece not in HBW slot |
| WF_1107_13 | /vgr/pick_up_and_transport | vgr_1 | 418 | NFC read failed |
| WF_101_28 | /hbw/unload | hbw_2 | 401 | workpiece not in HBW slot |
| WF_103_27 | /vgr/pick_up_and_transport | vgr_1 | 418 | NFC read failed |

All 5 failures had `response_status_code` 401/418 and a populated `unsatisfied_condition_description` (dropped column; details above). Note: 2 `/hw/human_review` instances have `human_workstation_green_button_pressed = 0` but completed with state `success` — the flag marks the initial press state, not the outcome.

## 3. Column Mapping Table

| Column | Meaning | Simulation Role | Sim-Relevant | Action |
|---|---|---|---|---|
| `time:timestamp` | Timestamp of the lifecycle transition (row time) | Event time (start/end per lifecycle row) | Yes | Keep |
| `operation_end_time` | End of the operation for that row | End time; `start` row: actual duration = end − start | Yes | Keep |
| `lifecycle:transition` | `scheduled` / `start` / `complete` | Lifecycle column (queue entry / service start / completion) | Yes | Keep |
| `lifecycle:state` | `assigned` / `inProgress` / `success` / `failure` | Outcome column (success/failure) | Yes | Keep |
| `event_id` | Instance id (379, 1:1 with `identifier:id`) | Instance column linking the 3 rows of one activity | Yes | Keep |
| `identifier:id` | Activity-instance id, `a_XXXXX` (1:1 with `event_id`) | Redundant duplicate of `event_id` | No | **Drop** (redundant) |
| `process_model_id` | Product variant / process model (`WF_101`…`WF_1107`) | Variant column (routing / product type) | Yes | Keep |
| `case` | Work-piece id (`WF_xxx_n`) | Case column | Yes | Keep |
| `case:concept:name` | Identical to `case` (verified: 100% equal) | Redundant | No | **Drop** (redundant) |
| `concept:name` | Activity name (`/hbw/unload`, `/ov/burn`, …) | Activity column | Yes | Keep |
| `requested_service_url` | Full HTTP request URL incl. resource, start/end positions, business_key | Context only; resource & case already in dedicated columns; positions derivable from `parameters` | No | **Drop** (redundant/noisy) |
| `org:resource` | Executing resource (`vgr_1`, `hbw_2`, …) | Resource column | Yes | Keep |
| `planned_operation_time` | Planned (target) operation time per activity | Target duration for benchmarking | Yes | Keep |
| `parameters` | Activity parameters (start/end positions, size, thickness, quantity, NFC flag, slot) | Context only — not used directly for routing (per decision); 1 missing value | Yes | Keep |
| `SubProcessID` | UUID present only on `start` rows (377/379) | No simulation role | No | **Drop** (noisy) |
| `current_task` | Free-text task description on `start` rows (372/379) | No simulation role; duplicates activity+parameters | No | **Drop** (noisy) |
| `response_status_code` | HTTP status on `complete` rows (200/401/418) | Redundant with `lifecycle:state` (200↔success, 401/418↔failure) | No | **Drop** (redundant) |
| `complete_service_time` | Full response time scheduled→complete (incl. queueing) | Actual (end-to-end) duration; equals `operation_end_time(complete)` − `time:timestamp(scheduled)` exactly | Yes | Keep |
| `human_workstation_green_button_pressed` | 1/0 flag on `/hw/human_review` rows only (51 rows) | Human-activity context (initial press state); not an outcome indicator | Yes | Keep |
| `unsatisfied_condition_description` | Failure detail (NFC/light-barrier conditions, ValueError) on 5 failing instances | Diagnostic context only | No | **Drop** (noisy; details recorded in §2) |

## 4. Excluded Columns (decisions)

1. `identifier:id` — 1:1 duplicate of `event_id` (verified).
2. `case:concept:name` — 100% identical to `case` (verified).
3. `requested_service_url` — raw HTTP URL; all information (resource, start/end positions, business_key) is already in `org:resource`, `parameters`, `case`.
4. `SubProcessID` — UUID only on `start` rows, no simulation meaning.
5. `current_task` — free-text description, redundant with `concept:name` + `parameters`.
6. `response_status_code` — fully determined by `lifecycle:state` on `complete` rows (200↔success, 401/418↔failure).
7. `unsatisfied_condition_description` — sparse failure diagnostics (5 instances), context only.

## 5. Cleaning Summary

- **Columns dropped**: 7 (see §4).
- **Rows dropped for missing key values** (`case`, `concept:name`, `org:resource`, `time:timestamp`, `operation_end_time`, `event_id`, `lifecycle:transition`): 0.
- **Duplicate rows removed**: 0 (none present).
- **Result**: 1,137 rows × 13 columns → `eventlog_cleaned.parquet` (canonical dataset for all subsequent agents).
- No rows needed for the log schema were dropped; every instance retains all 3 lifecycle rows.

## 6. Remaining Ambiguities / Notes

- `parameters` missing on one `start` row (event_id 2141, `/sm/sort`) — harmless, values present on the other two rows of that instance.
- `human_workstation_green_button_pressed = 0` on 2 `/hw/human_review` instances that still completed successfully — treated as context (initial state), not as a failure signal.
- Resources are not 1:1 with activities (e.g. `/mm/mill` runs on `mm_1` and `mm_2`; `/ov/burn` on `ov_1`/`ov_2`) — resource selection per instance is given by `org:resource` in the log and must be modeled as dispatching in the simulation.
- Timestamps are stored as ISO-8601 strings with mixed microsecond precision (some rows lack microseconds); parsed with `format='mixed'` — all values valid, no data loss.
