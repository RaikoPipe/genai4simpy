# Column Mapping Report — Fischertechnik Lab A (wandering-flying-bee)

## 1. Dataset Summary

| Property | Value |
|---|---|
| Raw file | `work_files/eventlog.parquet` |
| Cleaned file | `work_files/eventlog_cleaned.parquet` (canonical for all later agents) |
| Rows (raw / cleaned) | 576 / 576 (no rows removed) |
| Columns (raw / cleaned) | 20 / 19 |
| Activity instances | 192 (3 lifecycle rows each: `scheduled`, `start`, `complete`) |
| Cases (workpieces) | 18 |
| Process variants | 9 (`WF_101` … `WF_1107`) |
| Activities | 20 (e.g. `/hbw/unload`, `/mm/mill`, `/ov/burn`) |
| Resources | 15 (`hbw_1/2`, `vgr_1/2`, `mm_1/2`, `wt_1/2`, `sm_1`, `ov_1`, `hw_1`, …) |
| Time span | 2021-07-06 15:08:27.91 → 16:01:31.12 UTC (~53 min) |
| Outcomes | 184 success, 8 failure (7 × HTTP 418 precondition, 1 × HTTP 401 auth) |
| Duplicates | 0 full duplicate rows |

## 2. Column Inventory & Mapping

| Column | Type | Meaning | Simulation Role | Sim-Relevant | Action |
|---|---|---|---|---|---|
| `time:timestamp` | str (ISO-8601 UTC) | Timestamp of the lifecycle transition row. On `start` rows = service start; on `scheduled` rows = request/queue entry; on `complete` rows = completion record time | Primary event clock; service-start and request timestamps | Yes | Keep — log schema `start_col` |
| `operation_end_time` | str (ISO-8601 UTC) | Per-row end-of-operation timestamp. On `start` rows it is the **planned service end** (start + planned duration, ±234 s drift from `planned_operation_time`); on `complete` rows it equals the completion time and `complete_service_time` = `operation_end_time(complete)` − `time:timestamp(scheduled)` exactly | Service-end timestamp for duration computation | Yes | Keep — log schema `end_col` |
| `lifecycle:transition` | str | Lifecycle stage: `scheduled` / `start` / `complete` (192 each) | Lifecycle column | Yes | Keep — log schema `lifecycle_col` |
| `lifecycle:state` | str | `assigned` (scheduled), `inProgress` (start), `success` (184) / `failure` (8) | Outcome column | Yes | Keep — log schema `state_col` |
| `event_id` | int64 | Activity-instance id (192 unique, 3 rows each) | Instance key linking the 3 lifecycle rows | Yes | Keep — log schema `instance_col` |
| `identifier:id` | str | Activity-instance id (`a_31551` …), 1:1 with `event_id` | Redundant instance key | No | Keep (harmless, redundant) |
| `process_model_id` | str | Product variant / process model (9 values, e.g. `WF_103`, `WF_1106`) | Variant column | Yes | Keep — log schema `variant_col` |
| `case` | str | Workpiece id (18 values, e.g. `WF_103_29`); 1:1 with `process_model_id` | Case column | Yes | Keep — log schema `case_col` |
| `concept:name` | str | Activity name (20 values, e.g. `/mm/mill`, `/hbw/unload`) | Activity column | Yes | Keep — log schema `activity_col` |
| `requested_service_url` | str | REST URL of the requested service incl. `resource=`, `start=`, `end=`, `business_key=` query params | Redundant with `org:resource` + parsed parameters | No | Keep (reference) |
| `org:resource` | str | Executing resource (15 values) | Resource column | Yes | Keep — log schema `resource_col` |
| `planned_operation_time` | str (timedelta) | Planned service duration (24 distinct values, 14 s – 3 min 42 s) | Reference only — actual duration supersedes it | Low priority | Keep for reference (per confirmed decision) |
| `parameters` | str (Python-dict repr) | Service parameters: `start_position` (18 values), `end_position` (15), `quantity` (4: 4/6/8/10), `workpiece_size` (8: regular/middle/large/maxi/30/40/50/60), plus activity-specific extras (`use_nfc`, `hbw_slot`, `burn_workpiece_thickness`, `sorting_machine_ejection_position`, `temper_intensity`) | Parsed into separate columns | Yes | Parse → `start_position`, `end_position`, `quantity`, `workpiece_size` (per confirmed decision); extras stay in raw `parameters` |
| `case:concept:name` | str | Identical to `case` (verified equal on all rows) | Redundant case key | No | Keep (harmless, redundant) |
| `SubProcessID` | str (UUID) | Subprocess execution id; populated only on `start` rows (191/192) | Internal workflow-engine detail | No | Keep (harmless) |
| `current_task` | str | Natural-language task description; populated only on `start` rows (186/192) | Human-readable detail | No | Keep (harmless) |
| `response_status_code` | float64 | HTTP status on `complete` rows: 200 (184), 418 (7), 401 (1) | Failure-type detail beyond `lifecycle:state` | Yes | Keep (per confirmed decision) |
| `complete_service_time` | str (timedelta) | Full scheduled→complete span incl. queueing delay (4 s – 21 min 27 s); equals `operation_end_time(complete)` − `time:timestamp(scheduled)` exactly | NOT service time — do not use for duration | No | Keep (reference only; actual duration must be computed from start-transition events) |
| `human_workstation_green_button_pressed` | float64 | Green-button press flag; sparse (14/576 rows, human-review only) | Out of scope | No | **Drop** (per confirmed decision) |
| `unsatisfied_condition_description` | str | Precondition-failure detail on the 8 failed instances (light-barrier interrupted, NFC business_key mismatch, HBW not ready, ValueError: workpiece not in HBW) | Failure-cause detail | Yes | Keep (reference) |

## 3. Log Schema (spec section `log_schema`)

```yaml
log_schema:
  layout: lifecycle            # 3 rows per activity instance: scheduled → start → complete
  case_col: case               # workpiece id (18)
  activity_col: concept:name   # activity name (20)
  resource_col: org:resource   # executing resource (15)
  variant_col: process_model_id# product variant / process model (9)
  lifecycle_col: lifecycle:transition
  instance_col: event_id       # links the 3 rows of one activity instance (192 instances)
  enabled_value: scheduled     # request / queue entry
  start_value: start           # service start
  complete_value: complete     # completion
  start_col: time:timestamp    # row timestamp; on 'start' rows = service start
  end_col: operation_end_time  # on 'start' rows = planned service end; on 'complete' rows = completion time
  state_col: lifecycle:state
  success_values: [success]
  failure_values: [failure]
  duration_rule: >
    actual_duration = operation_end_time − time:timestamp evaluated on the
    'start'-transition row only. Do NOT use complete_service_time — it is the
    full scheduled→complete span including queueing delay.
  notes:
    - Waiting times are observable: request time = time:timestamp of the 'scheduled' row
      (observed queue wait 1.6 s – 20.9 min, median 5.2 s).
    - Outcomes: 184 success / 8 failure; failure type detail in response_status_code
      (418 precondition ×7, 401 auth ×1) and unsatisfied_condition_description.
    - planned_operation_time retained for reference; actual duration supersedes it.
    - parameters parsed into start_position, end_position, quantity, workpiece_size.
```

## 4. Excluded Columns

| Column | Reason |
|---|---|
| `human_workstation_green_button_pressed` | Sparse (14/576 rows), out of scope — dropped per confirmed decision |

No other columns dropped. `complete_service_time`, `planned_operation_time`, `identifier:id`, `case:concept:name`, `requested_service_url`, `SubProcessID`, `current_task` are retained as reference/redundant columns.

## 5. Cleaning Summary

| Operation | Detail | Rows before → after |
|---|---|---|
| Drop column | `human_workstation_green_button_pressed` | 576 → 576 |
| Drop missing in key columns | None (no missing values in any schema key column) | 576 → 576 |
| Drop duplicates | None (0 full duplicate rows) | 576 → 576 |

Cleaned log saved to `work_files/eventlog_cleaned.parquet` (576 rows × 19 columns). No row or duplicate removal, per confirmed decision.

## 6. Remaining Ambiguities

- `operation_end_time` on `start` rows is the *planned* service end and drifts up to ~234 s from `start + planned_operation_time`; the authoritative actual duration is `operation_end_time − time:timestamp` on the `start` row per the confirmed rule.
- `workpiece_size` mixes categorical (`regular`, `middle`, `large`, `maxi`) and numeric (`30`–`60`) encodings across variants; kept as raw string.
- `parameters` contains activity-specific extras (`use_nfc`, `hbw_slot`, `burn_workpiece_thickness`, `sorting_machine_ejection_position`, `temper_intensity`) not parsed into dedicated columns — available in the raw `parameters` string if needed.
- `complete_service_time` is retained but must never be used as service time (it includes queueing delay).
