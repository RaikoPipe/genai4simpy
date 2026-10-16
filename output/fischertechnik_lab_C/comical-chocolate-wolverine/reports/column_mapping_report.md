# Column Mapping Report — fischertechnik_lab_C

## 1. Dataset Summary

- **Source**: `work_files/eventlog.parquet` → cleaned: `work_files/eventlog_cleaned.parquet`
- **Shape (raw)**: 1,137 rows × 20 columns; **cleaned**: 1,137 rows × 12 columns (0 rows removed)
- **Time range**: 2021-07-01 18:48:23.227 → 2021-07-01 20:19:24.734 (UTC), horizon T ≈ 5,461.5 s
- **Structure**: lifecycle layout — exactly 3 rows per activity instance (`scheduled` → `start` → `complete`), 379 instances, 37 cases, 21 activities, 15 resources, 9 product variants (process models WF_101–WF_1107).
- **Outcomes**: 374 success / 5 failure (failures: 3× HTTP 418 on `/vgr/pick_up_and_transport`, 2× HTTP 401 on `/hbw/unload`; all failures carry an `unsatisfied_condition_description` — NFC business-key mismatch or missing workpiece in HBW).
- **Duplicate rows**: none.

## 2. Column Mapping Table

| Column | Meaning | Simulation Role | Sim-Relevant | Action |
|---|---|---|---|---|
| `time:timestamp` | Timestamp of the lifecycle transition row | Row timestamp; service start = timestamp of the `start` row; request (queue entry) = timestamp of the `scheduled` row | Yes | Keep (start_col) |
| `operation_end_time` | Operation end timestamp (per row) | Service end = `operation_end_time` of the `start` row; actual_duration = `operation_end_time` − `time:timestamp` of the `start` row | Yes | Keep (end_col) |
| `lifecycle:transition` | Transition type: `scheduled` / `start` / `complete` | Lifecycle column defining the three rows of one activity instance | Yes | Keep (lifecycle_col) |
| `lifecycle:state` | State after transition: `assigned` / `inProgress` / `success` / `failure` | Outcome column (success/failure) on the `complete` row | Yes | Keep (state_col) |
| `event_id` | Numeric ID of the activity instance (1:1 with `identifier:id`) | Redundant instance identifier | No | Drop |
| `identifier:id` | Activity instance ID (e.g. `a_29396`), links the 3 lifecycle rows | Instance column | Yes | Keep (instance_col) |
| `process_model_id` | Product variant / process model (WF_101…WF_1107); 1:1 with case | Variant column (routing context) | Yes | Keep (variant_col) |
| `case` | Work-piece ID (e.g. `WF_105_18`), 37 cases | Case column | Yes | Keep (case_col) |
| `concept:name` | Activity name (e.g. `/vgr/pick_up_and_transport`, `/ov/burn`), 21 distinct | Activity column | Yes | Keep (activity_col) |
| `requested_service_url` | Full HTTP service URL incl. resource, slot, NFC flag, business_key | Redundant with resource/parameters/case | No | Drop |
| `org:resource` | Executing resource (hbw_1/2, vgr_1/2, ov_1/2, mm_1/2, sm_1/2, pm_1, hw_1, wt_1, dm_2), 15 distinct | Resource column | Yes | Keep (resource_col) |
| `planned_operation_time` | Planned (target) operation duration, e.g. `0 days 00:00:47` | Target duration for calibration | Yes | Keep |
| `parameters` | Activity parameters (positions, slot, NFC flag), 1 missing | Context only — not used directly for routing | Yes (context) | Keep |
| `case:concept:name` | Duplicate of `case` (verified identical in all rows) | Redundant | No | Drop |
| `SubProcessID` | UUID of the subprocess, only on `start` rows (377/379) | Redundant instance identifier | No | Drop |
| `current_task` | Free-text task description, only on `start` rows (372/379) | Redundant with `concept:name` | No | Drop |
| `response_status_code` | HTTP status on `complete` rows (200/401/418) | Redundant with `lifecycle:state` | No | Drop |
| `complete_service_time` | Full response time (scheduled → complete, incl. queueing) | Actual end-to-end response time (incl. waiting); NOT the service duration | Yes | Keep |
| `human_workstation_green_button_pressed` | Green-button flag on `/hw/human_review` rows (45×1, 6×0) | Context for human-workstation behaviour | No (context) | Drop |
| `unsatisfied_condition_description` | Failure reason (NFC mismatch / missing workpiece), 15 rows | Failure diagnostics only | No (context) | Drop |

## 3. Log Schema (spec section `log_schema`)

Confirmed via `set_log_schema` (no warnings; `enabled_observed_frac = 1.0`, `end_missing = 0`):

```yaml
log_schema:
  layout: lifecycle            # 3 rows per activity instance
  case_col: case               # 37 cases (work-pieces)
  activity_col: concept:name   # 21 activities
  resource_col: org:resource   # 15 resources
  variant_col: process_model_id  # 9 variants (WF_101..WF_1107)
  instance_col: identifier:id  # 379 instances, links the 3 rows
  lifecycle_col: lifecycle:transition
  enabled_value: scheduled     # request / queue entry
  start_value: start           # service start
  complete_value: complete     # completion
  start_col: time:timestamp    # row timestamp
  end_col: operation_end_time  # service end (taken from the start row)
  state_col: lifecycle:state
  success_values: [success]
  failure_values: [failure]
```

**Duration semantics (confirmed decisions):**
- **Actual service duration** = `operation_end_time` − `time:timestamp` evaluated on the **`start` row only** (mean ≈ 31.2 s, min 0, max ≈ 185 s; 2 zero-duration starts are `/hw/human_review` instances).
- **`complete_service_time`** = full response time from `scheduled` to `complete` (includes queueing delay) — used as the actual end-to-end response time, not as the service duration.
- **`planned_operation_time`** = target duration per activity (constant per activity, 2 values for a few activities).

**Observability checks:**
- Every instance has exactly one `scheduled`, one `start`, one `complete` row, in that order (379/379).
- `operation_end_time` is constant per instance (377/379; 2 instances show minor per-row drift, < 30 s, on late complete rows — start-row value is authoritative).
- Waiting times are observable: request time = timestamp of the `scheduled` row (100% coverage).
- `case` → `process_model_id` is 1:1 (each case belongs to exactly one variant).

## 4. Excluded Columns

Dropped (8): `event_id`, `case:concept:name`, `SubProcessID`, `current_task`, `requested_service_url`, `response_status_code`, `unsatisfied_condition_description`, `human_workstation_green_button_pressed` — all redundant with the retained schema columns or context-only.

## 5. Cleaning Summary

- Dropped 8 columns; **0 rows removed** (no missing values in key columns; no duplicate rows).
- Cleaned file: `work_files/eventlog_cleaned.parquet` (1,137 × 12).

## 6. Remaining Ambiguities

1. **`operation_end_time` drift**: in 2 of 379 instances the `end` value differs slightly across the 3 rows (up to ~30 s on `complete` rows). Per the confirmed decision, the `start` row's `operation_end_time` is authoritative; the drift is treated as logging noise.
2. **`/ov/burn` planned vs actual**: planned 222 s vs actual max 41.5 s — burn durations in the log are far shorter than the planned value; flagged for the parameter-extraction phase (planning target may include setup or be nominal).
3. **`parameters` has 1 missing value** (on a `/sm/sort` start row); kept as context only, no simulation use.
4. **Zero-duration starts** (2× `/hw/human_review`): kept as-is; likely instant hand-off events.
