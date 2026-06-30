# Column Mapping Report

## Dataset Summary

| Property | Value |
|---|---|
| Source file | `eventlog.parquet` |
| Cleaned file | `eventlog_cleaned.parquet` |
| Rows | 576 (no rows removed) |
| Original columns | 20 |
| Cleaned columns | 29 |
| Duplicate rows | 0 |
| Structure | 192 operations × 3 lifecycle events (scheduled, start, complete) |

---

## Column Inventory & Classification

### Core Simulation-Relevant Columns

| Column | Meaning | DES Role | Type | Notes |
|---|---|---|---|---|
| `time:timestamp` | Event occurrence timestamp | **Timestamp** | datetime | Primary event time; parseable ISO-8601 |
| `operation_end_time` | Scheduled operation completion time | **Timestamp** | datetime | Used with `time:timestamp` to compute `actual_duration` |
| `lifecycle:transition` | Event type: scheduled/start/complete | **Event Type** | categorical | 3 values, 192 each; `start` rows used for actual_duration |
| `lifecycle:state` | Operation outcome: assigned/inProgress/success/failure | **Event Outcome** | categorical | 184 success, 8 failure |
| `event_id` | Unique event identifier | **Entity ID** | int64 | 192 unique values; shared across 3 lifecycle events per operation |
| `identifier:id` | Activity/operation instance ID | **Entity ID** | string | 192 unique values (e.g., `a_32823`) |
| `process_model_id` | Workflow/process template ID | **Activity Group** | categorical | 9 unique values (WF_101–WF_1107) |
| `case` | Case/workpiece instance ID | **Entity** | categorical | 18 unique values (e.g., `WF_104_20`) |
| `concept:name` | Operation/activity name | **Activity** | categorical | 20 unique values (e.g., `/vgr/pick_up_and_transport`) |
| `org:resource` | Resource/machine performing operation | **Resource** | categorical | 15 unique values (vgr_1, hbw_2, mm_1, etc.) |
| `planned_operation_time` | Scheduled/planned duration | **Duration (planned)** | string | 24 unique values; kept for reference |
| `actual_duration` | Computed: `operation_end_time − time:timestamp` | **Duration (actual)** | float64 | **Mean 31.95s for `start` transitions**; computed per instructions |
| `complete_service_time` | Full scheduled-to-complete span | **Duration (reference)** | string | Includes queueing delay; 67% missing (only on `complete` events) |
| `response_status_code` | HTTP response code for operation | **Quality/Failure** | float64 | 200 (success), 418 (precondition), 401 (auth); 67% missing |

### Parsed Parameter Columns (from `parameters`)

| Column | Meaning | DES Role | Type | Non-null |
|---|---|---|---|---|
| `start_position` | Starting position for transport/movement | **Location** | string | 342/576 |
| `end_position` | Ending position for transport/movement | **Location** | string | 342/576 |
| `quantity` | Number of items/workpieces | **Quantity** | string | 33/576 |
| `burn_workpiece_size` | Workpiece size for burn operations | **Category** | string | 57/576 |
| `burn_workpiece_thickness` | Workpiece thickness for burn operations | **Category** | string | 39/576 |
| `hbw_slot` | High Bay Warehouse slot identifier | **Location** | string | 138/576 |
| `use_nfc` | NFC usage flag (true/false) | **Category** | string | 156/576 |
| `sorting_machine_ejection_position` | Ejection position on sorting machine | **Location** | float64 | 18/576 |
| `temper_intensity` | Tempering intensity setting | **Category** | string | 15/576 |

### Reference Columns (Retained, Low Priority)

| Column | Meaning | DES Role | Type | Notes |
|---|---|---|---|---|
| `requested_service_url` | Full REST API URL for the operation | Reference | string | Contains resource, positions, business_key embedded in URL |
| `SubProcessID` | Sub-process UUID identifier | Reference | string | 385 missing (67%); only present for some operations |
| `current_task` | Human-readable task description | Reference | string | 390 missing (68%); verbose descriptions |
| `unsatisfied_condition_description` | Failure condition details | Reference | string | 552 missing (96%); only populated on failures |

### Dropped Columns

| Column | Reason |
|---|---|
| `human_workstation_green_button_pressed` | Sparse (93% missing), out of scope for DES simulation |
| `case:concept:name` | Exact duplicate of `case` column |
| `parameters` | Parsed into 9 separate columns; raw string dict no longer needed |

---

## Parameter Parsing Results

The `parameters` column contained Python string-dict representations with a `children` list of key-value pairs. Parsing extracted **9 distinct parameter keys**:

| Parameter Key | Values | Frequency |
|---|---|---|
| `start_position` | 20 distinct positions | 342 rows |
| `end_position` | 20 distinct positions | 342 rows |
| `hbw_slot` | `hbw_1_automatic_pos`, `hbw_2_automatic_pos` | 138 rows |
| `use_nfc` | `true`, `false` | 156 rows |
| `burn_workpiece_size` | `regular`, `large`, `maxi`, `middle`, `30`, `40`, `50`, `60` | 57 rows |
| `burn_workpiece_thickness` | `thin`, `thick` | 39 rows |
| `quantity` | `4`, `6`, `8`, `10` | 33 rows |
| `sorting_machine_ejection_position` | `1.0`, `2.0`, `3.0` | 18 rows |
| `temper_intensity` | `ov_1_temper_high` | 15 rows |

---

## Cleaning Operations Performed

| Operation | Details |
|---|---|
| **Dropped columns** | `human_workstation_green_button_pressed` (sparse, out of scope), `case:concept:name` (duplicate of `case`), `parameters` (parsed into separate columns) |
| **Added columns** | 9 parsed parameter columns + `actual_duration` |
| **Computed `actual_duration`** | `operation_end_time − time:timestamp` for all rows; meaningful for `start` transitions (mean 31.95s) |
| **Row removal** | None (per instructions) |
| **Duplicate removal** | None (0 duplicates found) |

---

## Final Cleaned Dataset Schema

| # | Column | Type | Non-null | DES Role |
|---|---|---|---|---|
| 1 | `time:timestamp` | datetime64 | 576 | Timestamp |
| 2 | `operation_end_time` | datetime64 | 576 | Timestamp |
| 3 | `lifecycle:transition` | string | 576 | Event Type |
| 4 | `lifecycle:state` | string | 576 | Event Outcome |
| 5 | `event_id` | int64 | 576 | Entity ID |
| 6 | `identifier:id` | string | 576 | Entity ID |
| 7 | `process_model_id` | string | 576 | Activity Group |
| 8 | `case` | string | 576 | Entity |
| 9 | `concept:name` | string | 576 | Activity |
| 10 | `requested_service_url` | string | 576 | Reference |
| 11 | `org:resource` | string | 576 | Resource |
| 12 | `planned_operation_time` | string | 576 | Duration (planned) |
| 13 | `case:concept:name` | — | — | **DROPPED** (duplicate) |
| 14 | `SubProcessID` | string | 191 | Reference |
| 15 | `current_task` | string | 186 | Reference |
| 16 | `response_status_code` | float64 | 192 | Quality/Failure |
| 17 | `complete_service_time` | string | 192 | Duration (reference) |
| 18 | `unsatisfied_condition_description` | string | 24 | Reference |
| 19 | `use_nfc` | string | 156 | Parsed Parameter |
| 20 | `burn_workpiece_size` | string | 57 | Parsed Parameter |
| 21 | `temper_intensity` | string | 15 | Parsed Parameter |
| 22 | `sorting_machine_ejection_position` | float64 | 18 | Parsed Parameter |
| 23 | `quantity` | string | 33 | Parsed Parameter |
| 24 | `start_position` | string | 342 | Parsed Parameter |
| 25 | `end_position` | string | 342 | Parsed Parameter |
| 26 | `hbw_slot` | string | 138 | Parsed Parameter |
| 27 | `burn_workpiece_thickness` | string | 39 | Parsed Parameter |
| 28 | `actual_duration` | float64 | 576 | Duration (actual) |
| 29 | `human_workstation_green_button_pressed` | — | — | **DROPPED** |
| — | `parameters` | — | — | **DROPPED** (parsed) |

---

## Remaining Ambiguities

1. **`complete_service_time` vs `actual_duration`**: `complete_service_time` measures the full scheduled-to-complete span (includes queueing). `actual_duration` (computed from `start` transitions) measures actual service time. For DES, `actual_duration` on `start` rows is the correct service time metric.
2. **`case` vs `process_model_id`**: `case` encodes both workflow type and instance number (e.g., `WF_104_20`). `process_model_id` is the workflow template alone (e.g., `WF_104`). Both are retained; `case` is the entity/workpiece identifier, `process_model_id` groups by workflow type.
3. **`SubProcessID` and `current_task`**: High missingness (67–68%). Retained as reference but not recommended for core simulation logic.
4. **`response_status_code`**: Only populated on `complete` events. Values 418 (precondition failed) and 401 (auth failed) indicate failure modes beyond `lifecycle:state`.

---

## Cleaned Dataset Path

```
/home/rreider/PycharmProjects/genai4simpy-deepagents/output/fischertechnik_lab_A/colossal-unyielding-flounder/work_files/eventlog_cleaned.parquet
```
