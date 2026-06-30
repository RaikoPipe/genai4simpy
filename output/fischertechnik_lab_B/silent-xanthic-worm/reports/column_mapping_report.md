# Column Mapping Report — Fischertechnik Lab B Event Log

## Dataset Summary

| Property | Value |
|---|---|
| Source file | `eventlog.parquet` |
| Cleaned file | `eventlog_cleaned.parquet` |
| Rows (before cleaning) | 1,383 |
| Rows (after cleaning) | 1,383 |
| Columns (before cleaning) | 20 |
| Columns (after cleaning) | 12 |
| Duplicate rows | 0 |
| Entities (unique `identifier:id`) | 461 |
| Events per entity | 3 (scheduled → start → complete) |

## Column Inventory and Classification

### Simulation-Relevant Columns (Retained)

| Column | Type | Meaning | DES Role | Notes |
|---|---|---|---|---|
| `identifier:id` | str | Unique workpiece/job identifier (e.g., `a_15949`) | **Entity** | 461 unique entities |
| `time:timestamp` | float64 | Event creation time (seconds since epoch) | **Event Timestamp** | Arrival/scheduling time; parsed from ISO 8601 |
| `operation_end_time` | float64 | Operation completion time (seconds since epoch) | **Event Timestamp** | Preferred over `time:timestamp` for duration computation |
| `lifecycle:transition` | str | Event type: `scheduled`, `start`, `complete` | **Activity/Event Type** | 3 transitions per entity (1:1:1 ratio) |
| `lifecycle:state` | str | Outcome: `assigned`, `inProgress`, `success`, `failure` | **Quality/Outcome** | 9 failure entries retained (real factory behavior) |
| `process_model_id` | str | Workflow/route template (e.g., `WF_101`) | **Activity/Route** | 9 distinct workflow templates |
| `case` | str | Workflow instance (e.g., `WF_104_8`) | **Entity Group** | 38 case instances; links entity to workflow |
| `concept:name` | str | Operation name (e.g., `/mm/mill`, `/vgr/pick_up_and_transport`) | **Activity Name** | 20 distinct operations |
| `org:resource` | str | Resource performing the operation (e.g., `mm_1`, `vgr_1`) | **Resource** | 15 distinct resources |
| `planned_operation_time` | float64 | Planned processing duration in seconds | **Duration (Planned)** | Parsed from timedelta strings; range 5–222s |
| `complete_service_time` | float64 | Full response time (scheduled→complete) in seconds | **Duration (Observed)** | Available only on `complete` events (461/1383) |
| `actual_duration` | float64 | Computed: `operation_end_time − time:timestamp` for `start` events | **Duration (Computed)** | Available only on `start` events (461/1383); mean 30.4s |

### Excluded Columns (Dropped)

| Column | Reason for Exclusion |
|---|---|
| `event_id` | Redundant integer ID; `identifier:id` retained as entity identifier |
| `requested_service_url` | Full HTTP URL with query parameters; not useful for simulation |
| `parameters` | Complex nested JSON-like strings; 1 missing value; not needed for DES |
| `case:concept:name` | Exact duplicate of `case` column |
| `SubProcessID` | UUID identifiers with 924 missing values; no simulation relevance |
| `current_task` | Human-readable task descriptions with 937 missing values; redundant with `concept:name` |
| `response_status_code` | HTTP status codes (200, 401, 418); 922 missing values; not needed |
| `human_workstation_green_button_pressed` | Binary flag specific to one resource; 1,296 missing values |
| `unsatisfied_condition_description` | Error condition details; 1,356 missing values; not needed for DES |

## Cleaning Operations Performed

1. **Dropped 9 non-simulation-relevant columns** (listed above)
2. **Parsed `time:timestamp`** from ISO 8601 strings to float64 seconds since epoch
3. **Parsed `operation_end_time`** from ISO 8601 strings to float64 seconds since epoch
4. **Parsed `planned_operation_time`** from timedelta strings (e.g., `0 days 00:00:47`) to float64 seconds
5. **Parsed `complete_service_time`** from duration strings (e.g., `0:00:27.249969`) to float64 seconds
6. **Computed `actual_duration`** as `operation_end_time − time:timestamp` for rows where `lifecycle:transition == 'start'`
7. **Retained all 9 failure entries** in `lifecycle:state` (reflects real factory behavior)
8. **No rows dropped** — no duplicate rows found; no rows with missing values in key columns

## Final Column Mapping Table (DES Simulation)

| DES Role | Mapped Column(s) | Description |
|---|---|---|
| **Entity** | `identifier:id` | Workpiece/job flowing through the system |
| **Entity Group** | `case`, `process_model_id` | Workflow instance and route template |
| **Event Timestamp (Arrival)** | `time:timestamp` | When the event was created/scheduled |
| **Event Timestamp (Completion)** | `operation_end_time` | When the operation ended |
| **Resource** | `org:resource` | Machine/station performing the operation |
| **Activity Name** | `concept:name` | Operation type (e.g., mill, transport, sort) |
| **Event Type** | `lifecycle:transition` | `scheduled` / `start` / `complete` |
| **Outcome** | `lifecycle:state` | `assigned` / `inProgress` / `success` / `failure` |
| **Planned Duration** | `planned_operation_time` | Expected processing time in seconds |
| **Actual Duration** | `actual_duration` | Computed processing time (start events only) |
| **Total Service Time** | `complete_service_time` | Queue + processing time (complete events only) |

## Remaining Ambiguities

- **`case` vs `process_model_id`**: `process_model_id` defines the workflow route template (9 types), while `case` identifies specific instances (38 instances). Both are retained; the simulation designer should decide which to use for routing logic.
- **Duration columns**: Three duration measures are available — `planned_operation_time` (all rows), `actual_duration` (start events only), and `complete_service_time` (complete events only). The simulation should use `actual_duration` for processing time and `complete_service_time` for understanding total lead time including queueing.
- **Failure handling**: 9 out of 461 entities have `failure` states. The simulation designer should decide whether to model rework, scrap, or bypass behavior for these cases.

## Cleaned Dataset Path

```
/home/rreider/PycharmProjects/genai4simpy-deepagents/output/fischertechnik_lab_B/silent-xanthic-worm/work_files/eventlog_cleaned.parquet
```
