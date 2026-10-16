# Column Mapping Report — fischertechnik_lab_B (significant-hilarious-cuscus)

## 1. Dataset Summary

- **Source**: `work_files/eventlog.parquet` → cleaned: `work_files/eventlog_cleaned.parquet`
- **Shape**: 1,383 rows × 20 columns (raw); 1,383 rows × 12 columns (cleaned)
- **Structure**: lifecycle layout — exactly 3 rows per activity instance (`scheduled` → `start` → `complete`), 461 instances, 38 cases (workpieces), 20 activities, 15 resources, 9 process-model variants.
- **Time span**: t0 = 2021-06-30T15:24:34Z, horizon T ≈ 5,943.7 s (~99 min).
- **Outcomes**: 452 success, 9 failure (kept — real factory behavior; HTTP 418/401 on the `complete` row).
- **No duplicate rows**; no missing values in key columns.

## 2. Column Mapping

| Column | Meaning | Simulation Role | Sim-Relevant | Action |
|---|---|---|---|---|
| `time:timestamp` | Timestamp of the lifecycle transition (ISO8601, mixed precision) | Request time on `scheduled` row; **service start** on `start` row | Yes | Keep; parse to seconds. Actual duration = `operation_end_time` − `time:timestamp` on `start` rows only |
| `operation_end_time` | Operation end timestamp (ISO8601) | **Service end** (preferred over `time:timestamp` of the `complete` row) | Yes | Keep; parse to seconds |
| `lifecycle:transition` | Transition type: `scheduled` / `start` / `complete` | Lifecycle column | Yes | Keep |
| `lifecycle:state` | `assigned` (scheduled) / `inProgress` (start) / `success` / `failure` (complete) | Outcome column; 9 failures retained | Yes | Keep |
| `event_id` | Integer id shared by the 3 rows of an instance (1002–1483) | Redundant instance key | No | **Drop** (keep `identifier:id`) |
| `identifier:id` | Activity-instance id (e.g. `a_15513`), unique per instance | Instance column linking the 3 lifecycle rows | Yes | Keep |
| `process_model_id` | Process-model / product variant (WF_101…WF_1107), 9 values | Variant column | Yes | Keep |
| `case` | Workpiece id, e.g. `WF_101_13` (prefix = process model, 100% consistent) | Case column | Yes | Keep |
| `concept:name` | Activity name (e.g. `/ov/burn`, `/vgr/pick_up_and_transport`), 20 values | Activity column | Yes | Keep |
| `requested_service_url` | REST URL of the service call; resource query param matches `org:resource` 100% | Redundant (resource already mapped); carries size/thickness for burn | No | **Drop** (parameters carry the same info) |
| `org:resource` | Executing resource (vgr_1/2, hbw_1/2, mm_1/2, ov_1, hw_1, wt_1/2, sm_1, …), 15 values | Resource column | Yes | Keep |
| `planned_operation_time` | Planned duration, timedelta string (e.g. `0 days 00:00:47`) | Planned processing time | Yes | Keep; **parse to seconds** (22 distinct values, 5–222 s) |
| `parameters` | Dict string of activity parameters (positions, hbw slot, burn size/thickness, NFC flag); 1 missing on a `complete` row | Activity parameters (routing/variant detail) | Yes | Keep |
| `case:concept:name` | Identical to `case` (100%) | Redundant | No | **Drop** |
| `SubProcessID` | UUID present only on `start` rows (459/461) | Redundant instance detail | No | **Drop** |
| `current_task` | Free-text task description, only on `start` rows | Redundant narrative | No | **Drop** |
| `response_status_code` | HTTP code on `complete` rows (200 / 418×7 / 401×2) | Redundant with `lifecycle:state` (success↔200, failure↔418/401, 100% consistent) | No | **Drop** |
| `complete_service_time` | Full response time scheduled→complete incl. queueing (timedelta string), only on `complete` rows | Reference metric (mean 73.6 s vs 30.4 s actual service) | Yes | Keep (do not use as service duration) |
| `human_workstation_green_button_pressed` | 1/0 flag, only on `/hw/human_review` instances (87 rows) | Human-intervention detail; not needed for core simulation | No | **Drop** |
| `unsatisfied_condition_description` | Precondition-failure detail (NFC/light-barrier/warehouse errors), only on the 9 failed instances | Diagnostic detail of failures | No | **Drop** |

## 3. Log Schema (confirmed via `set_log_schema`)

- **Layout**: lifecycle — one row per transition; 3 rows per instance.
- **case_col**: `case` | **activity_col**: `concept:name` | **resource_col**: `org:resource` | **variant_col**: `process_model_id`
- **start_col**: `time:timestamp` | **end_col**: `operation_end_time` (preferred over `complete`-row timestamp)
- **lifecycle_col**: `lifecycle:transition` | **instance_col**: `identifier:id`
- **enabled_value**: `scheduled` (queue entry / request) | **start_value**: `start` | **complete_value**: `complete`
- **state_col**: `lifecycle:state` | success: `success` | failure: `failure`
- **Validation**: 461 instances, 38 cases, 20 activities, 15 resources; `enabled_observed_frac = 1.0` (waiting times fully observable); `end_missing = 0`; no warnings. Sample verified: e.g. `/hbw/unload` on `hbw_2`: enabled 0.0 s → start 3.56 s → end 55.91 s (≈ start + 52 s planned).
- **Duration convention**: actual service duration = `operation_end_time − time:timestamp` on `start` rows only (mean 30.4 s, min 0.0, max 218.7 s, no negatives). `complete_service_time` records the full response time (scheduled → complete, incl. queueing; mean 73.6 s, max 1,079 s) and is kept only as a reference metric.

## 4. Excluded Columns

`event_id`, `case:concept:name`, `SubProcessID`, `current_task`, `response_status_code`, `requested_service_url`, `unsatisfied_condition_description`, `human_workstation_green_button_pressed` (8 columns; all redundant or diagnostic-only).

## 5. Cleaning Summary

- Dropped 8 columns (above).
- Drop rows with missing values in key columns (`identifier:id`, `case`, `concept:name`, `org:resource`, `time:timestamp`, `operation_end_time`, `lifecycle:transition`, `lifecycle:state`): **0 rows removed** (no missing values in these columns).
- Duplicate rows: none.
- Result: 1,383 rows × 12 columns → `eventlog_cleaned.parquet`.
- All 9 `failure` entries in `lifecycle:state` retained (real factory behavior).

## 6. Remaining Ambiguities

- `operation_end_time` differs across the 3 rows of an instance (per-row operation end, not a constant); the schema uses the value on the relevant row, which is consistent with the duration convention above.
- `parameters` has 1 missing value (on a `complete` row); kept as-is since it is not a key column.
- 2 instances have only 2 distinct `operation_end_time` values across their rows (negligible; no action taken).
