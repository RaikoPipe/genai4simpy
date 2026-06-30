# Column Mapping Report — Fischertechnik Lab C Event Log

## Dataset Summary

| Property | Value |
|---|---|
| Source file | `eventlog.parquet` |
| Cleaned file | `eventlog_cleaned.parquet` |
| Rows (original) | 1,137 |
| Rows (cleaned) | 1,137 |
| Columns (original) | 20 |
| Columns (cleaned) | 13 |
| Duplicate rows | 0 |
| Entities (unique event_id) | 379 |
| Lifecycle transitions per entity | 3 (scheduled → start → complete) |
| Time span | 2021-07-01 |

## Column Mapping Table

| Column | Meaning | DES Role | Sim-Relevant | Action |
|---|---|---|---|---|
| `time:timestamp` | Event occurrence timestamp (ISO8601) | **Timestamp** | ✅ Yes | **Keep** — arrival/start time for events |
| `operation_end_time` | When the operation completed | **Timestamp** | ✅ Yes | **Keep** — used to compute processing duration |
| `lifecycle:transition` | Event phase: scheduled, start, complete | **Event Type** | ✅ Yes | **Keep** — distinguishes event phases |
| `event_id` | Unique operation instance identifier | **Entity ID** | ✅ Yes | **Keep** — groups the 3 lifecycle events per operation |
| `process_model_id` | Workflow template (WF_101–WF_1107) | **Activity Category** | ✅ Yes | **Keep** — identifies the workflow/routing pattern |
| `case` | Case instance (e.g., WF_103_24) | **Entity (Case)** | ✅ Yes | **Keep** — groups operations belonging to the same workpiece case |
| `concept:name` | Operation name (e.g., /vgr/pick_up_and_transport) | **Activity** | ✅ Yes | **Keep** — identifies the process step/activity |
| `org:resource` | Resource performing the operation (e.g., hbw_2, vgr_1) | **Resource** | ✅ Yes | **Keep** — identifies the machine/station |
| `planned_operation_time` | Target processing duration (timedelta string) | **Duration (Target)** | ✅ Yes | **Keep** — planned/standard processing time |
| `complete_service_time` | Full response time from scheduled to complete | **Duration (Actual Total)** | ✅ Yes | **Keep** — includes queueing + processing |
| `actual_processing_duration` | Computed: operation_end_time − time:timestamp | **Duration (Computed)** | ✅ Yes | **Added** — processing time per event phase |
| `planned_operation_time_seconds` | Computed: planned_operation_time in seconds | **Duration (Target)** | ✅ Yes | **Added** — numeric version for analysis |
| `complete_service_time_seconds` | Computed: complete_service_time in seconds | **Duration (Actual Total)** | ✅ Yes | **Added** — numeric version for analysis |

## Excluded Columns

| Column | Reason for Exclusion |
|---|---|
| `case:concept:name` | Exact duplicate of `case` column |
| `identifier:id` | Internal activity ID (a_XXXXX), redundant with `event_id` |
| `parameters` | Context-only JSON (positions, NFC flags); not used for routing |
| `requested_service_url` | Contains resource info already captured in `org:resource`; URL structure not needed for DES |
| `SubProcessID` | 760/1137 missing (67%); UUIDs with no simulation meaning |
| `current_task` | 765/1137 missing (67%); verbose human-readable descriptions |
| `response_status_code` | 758/1137 missing (67%); HTTP status codes (200/401/418) |
| `human_workstation_green_button_pressed` | 1086/1137 missing (95%); binary flag for human review only |
| `unsatisfied_condition_description` | 1122/1137 missing (99%); error/debug descriptions |
| `lifecycle:state` | Derived from `lifecycle:transition` (assigned→inProgress→success/failure) |

## Cleaning Summary

- **Columns dropped**: 10 non-simulation-relevant columns removed
- **Columns added**: 3 computed duration columns (`actual_processing_duration`, `planned_operation_time_seconds`, `complete_service_time_seconds`)
- **Rows dropped**: 0 (no duplicates, no missing values in key columns)
- **Duplicates removed**: 0 (no duplicate rows in original data)
- **Saved path**: `/home/rreider/PycharmProjects/genai4simpy-deepagents/output/fischertechnik_lab_C/elated-shellfish-of-attraction/work_files/eventlog_cleaned.parquet`

## Duration Interpretation

| Duration Column | Computation | Meaning |
|---|---|---|
| `actual_processing_duration` (start events) | `operation_end_time − time:timestamp` where `lifecycle:transition == 'start'` | **Processing time** — actual time the resource spent working on the operation |
| `complete_service_time` (complete events) | Provided in data | **Total response time** — from scheduled to complete, includes queueing delay |
| `planned_operation_time` | Provided in data | **Target/standard time** — expected processing duration |

**Key insight**: The `start` transition events have `actual_processing_duration` ≈ 31s mean (processing time), while `complete_service_time` ≈ 87s mean (total response time including queueing). The `scheduled` events show the queueing delay before processing begins.

## Resource Inventory (15 resources)

| Resource | Count | Likely Type |
|---|---|---|
| hbw_1, hbw_2 | 294 | High Bay Warehouse |
| vgr_1, vgr_2 | 312 | Vacuum Gripper |
| ov_1, ov_2 | 120 | Oven |
| mm_1, mm_2 | 123 | Milling Machine |
| sm_1, sm_2 | 102 | Sorting Machine |
| hw_1 | 51 | Human Workstation |
| wt_1, wt_2 | 87 | Wheel Transporter |
| dm_2 | 30 | Drill Machine |
| pm_1 | 24 | Punch Machine |

## Remaining Ambiguities

- None. All columns have been classified and the mapping is complete.
