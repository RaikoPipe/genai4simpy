# Column Mapping Report — fischertechnik_lab_A (eager-nice-cow)

## 1. Dataset Summary

- **Source:** `work_files/eventlog.parquet` (raw), `work_files/eventlog_cleaned.parquet` (cleaned)
- **Shape:** 576 rows × 20 columns (raw) → 576 rows × 22 columns (cleaned)
- **Structure:** lifecycle layout — 192 activity instances × 3 transitions each (`scheduled` → `start` → `complete`), rows linked by `identifier:id`
- **Domain:** 18 cases (workpieces), 9 process variants, 20 activities, 15 resources
- **Time span:** 2021-07-06 15:08:27.91 → 16:01:31.12 UTC (≈ 53 min)
- **Outcomes:** 184 success / 8 failure (418 ×7 precondition, 401 ×1 auth)
- **Data quality:** 2,629 missing cells (22.8%), all in non-key detail columns; 0 duplicate rows

## 2. Column Mapping

| Column | Meaning | Simulation Role | Sim-Relevant | Action |
|---|---|---|---|---|
| `time:timestamp` | Timestamp of the lifecycle transition | Event time: queue entry (scheduled), service start (start), completion (complete) | Yes | Keep |
| `operation_end_time` | Service end time (per row; on start rows = true service end) | Service end ⇒ actual_duration = end − start (start rows only) | Yes | Keep |
| `lifecycle:transition` | `scheduled` / `start` / `complete` | Lifecycle transition marker | Yes | Keep |
| `lifecycle:state` | `assigned` / `inProgress` / `success` / `failure` | Outcome of completion | Yes | Keep |
| `event_id` | Numeric instance id (1:1 with `identifier:id`) | Instance identifier (redundant) | No | Keep (harmless id) |
| `identifier:id` | Activity-instance id (e.g. `a_32642`) | Instance key linking the 3 lifecycle rows | Yes | Keep |
| `process_model_id` | Product variant / process model (`WF_101` … `WF_1107`) | Case variant | Yes | Keep |
| `case` | Work-piece id (e.g. `WF_101_30`) | Case id | Yes | Keep |
| `concept:name` | Activity name (e.g. `/vgr/pick_up_and_transport`) | Activity | Yes | Keep |
| `requested_service_url` | REST URL incl. resource + parameter query string | Redundant with `org:resource` + `parameters` | No | Keep (reference) |
| `org:resource` | Executing resource (e.g. `vgr_1`, `hbw_2`) | Resource | Yes | Keep |
| `planned_operation_time` | Nominal/planned service duration | Reference only — actual duration supersedes (confirmed: keep, low priority) | Low | Keep |
| `parameters` | Raw parameter dict (`{'value': None, 'children': [...]}`) | Parsed into 4 columns below | Yes | Keep raw + parse |
| `case:concept:name` | Copy of `case` (verified 100% equal) | Redundant | No | **Drop** |
| `SubProcessID` | UUID of executing subprocess (start rows only, 191/192) | Diagnostic detail | No | Keep |
| `current_task` | Free-text task description (mostly start rows) | Diagnostic detail | No | Keep |
| `response_status_code` | HTTP status on complete rows: 200 / 418 / 401 | Failure-type detail beyond `lifecycle:state` (confirmed: keep) | Yes | Keep |
| `complete_service_time` | Full scheduled→complete span incl. queueing | NOT service time; reference only | No | Keep (reference) |
| `human_workstation_green_button_pressed` | Human green-button flag (42/576 rows) | Sparse, out of scope (confirmed: drop) | No | **Drop** |
| `unsatisfied_condition_description` | Precondition-check detail for the 8 failures | Failure diagnostics | Yes | Keep |
| `start_position` | *(new)* parsed from `parameters.parameter_start_position` | Transport source position | Yes | Add (342/576) |
| `end_position` | *(new)* parsed from `parameters.parameter_end_position` | Transport target position | Yes | Add (342/576) |
| `quantity` | *(new)* parsed from `parameters.parameter_quantity` | Workpiece count (3–10, Int64) | Yes | Add (33/576) |
| `workpiece_size` | *(new)* parsed from `parameters.parameter_burn_workpiece_size` | Workpiece size; mixed domain (categorical `regular/middle/large/maxi` + numeric `30`–`60`) → kept as string | Yes | Add (57/576) |

## 3. Log Schema (confirmed via `set_log_schema`)

- **Layout:** lifecycle (one row per transition)
- case_col: `case` · activity_col: `concept:name` · resource_col: `org:resource` · variant_col: `process_model_id`
- lifecycle_col: `lifecycle:transition` · instance_col: `identifier:id`
- enabled_value: `scheduled` · start_value: `start` · complete_value: `complete`
- start_col: `time:timestamp` · end_col: `operation_end_time`
- state_col: `lifecycle:state` · success: `success` · failure: `failure`

Validation: 192 instances, 18 cases, 20 activities, 15 resources, 184 success / 8 failure, enabled observed for 100% of instances, 0 missing end times, no warnings. Sample instance `WF_101_30 / /hbw/unload @ hbw_2`: enabled 0.0 s → start 3.52 s → end 55.77 s (success).

**Duration rule (confirmed):** actual_duration = `operation_end_time` − `time:timestamp` on `start` rows only. `complete_service_time` measures scheduled→complete (includes queueing) and is not used as service time.

## 4. Excluded Columns

| Column | Reason |
|---|---|
| `human_workstation_green_button_pressed` | Sparse (42/576), out of scope (confirmed decision) |
| `case:concept:name` | Exact duplicate of `case` |

## 5. Cleaning Summary

- Rows: 576 → 576 (no row or duplicate removal, per confirmed decision)
- Columns: 20 → 18 (2 dropped) + 4 parsed parameter columns = 22
- No missing values in any schema-relevant key column
- Output: `work_files/eventlog_cleaned.parquet`

## 6. Remaining Ambiguities

- `workpiece_size` mixes categorical labels (`regular`, `middle`, `large`, `maxi`) with numeric sizes (`30`–`60`) for `/ov/burn`; kept as raw string — a size-class mapping may be needed in later phases.
- `event_id` and `identifier:id` are 1:1 redundant; `identifier:id` is the instance key.
- `SubProcessID` has 1 missing value (start row) and `current_task` 6 — both diagnostic only, no impact.
