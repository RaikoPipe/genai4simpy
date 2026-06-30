# Topology Report — Fischertechnik Manufacturing System

## 1. Dataset Characteristics

| Property | Value |
|---|---|
| Source file | `eventlog_cleaned.parquet` |
| Total events | 576 (192 operations × 3 lifecycle events) |
| Operations | 192 |
| Product variants | 9 (WF_101, WF_102, WF_103, WF_104, WF_105, WF_108, WF_109, WF_1106, WF_1107) |
| Case instances | 18 (4 incomplete: WF_104_21, WF_108_18, WF_109_16, WF_1107_17) |
| Failure events | 8 (7 × HTTP 418, 1 × HTTP 401) |
| Time window | 2021-07-06 15:10 – 16:02 UTC |

---

## 2. Resource Inventory

### 2.1 Resource Classes and Entities

| Resource Class | Entity | Capacity | Activities | Line |
|---|---|---|---|---|
| **High Bay Warehouse (Input)** | `hbw_2` | 1 | `/hbw/unload`, `/hbw/store_empty_bucket` | Shared |
| **High Bay Warehouse (Output)** | `hbw_1` | 1 | `/hbw/get_empty_bucket`, `/hbw/store` | Shared |
| **Vertical Guided Robot** | `vgr_1` | 1 | `/vgr/pick_up_and_transport` | Shared |
| **Vertical Guided Robot** | `vgr_2` | 1 | `/vgr/pick_up_and_transport` | Shared |
| **Oven** | `ov_1` | 1 | `/ov/burn`, `/ov/temper` | Line 1 |
| **Oven** | `ov_2` | 1 | `/ov/burn` | Line 2 |
| **Mill Machine** | `mm_1` | 1 | `/mm/mill`, `/mm/deburr`, `/mm/drill` | Line 1 |
| **Mill Machine** | `mm_2` | 1 | `/mm/mill`, `/mm/deburr`, `/mm/drill`, `/mm/transport_from_to` | Line 2 |
| **Sorting Machine** | `sm_1` | 1 | `/sm/sort`, `/sm/transport` | Line 1 |
| **Sorting Machine** | `sm_2` | 1 | `/sm/sort`, `/sm/transport` | Line 2 |
| **Work Transport** | `wt_1` | 1 | `/wt/pick_up_and_transport` | Line 1 |
| **Work Transport** | `wt_2` | 1 | `/wt/pick_up_and_transport` | Line 2 |
| **Punch Machine** | `pm_1` | 1 | `/pm/punch_recesses`, `/pm/punch_ribbing`, `/pm/punch_gill` | Shared |
| **Drill Machine** | `dm_2` | 1 | `/dm/lower`, `/dm/cylindrical_drill` | Line 2 |
| **Human Workstation** | `hw_1` | 1 | `/hw/human_review` | Shared |

### 2.2 Resource Pooling Notes

- **VGRs (`vgr_1`, `vgr_2`)**: Shared across all variants. Role-based assignment (see §5.1).
- **Mill Machines (`mm_1`, `mm_2`)**: Same activity set (`mill`, `deburr`, `drill`), but each variant uses only one. `mm_1` is primary (higher utilization: 42 ops vs 21 ops).
- **Sorting Machines (`sm_1`, `sm_2`)**: Same activity set (`sort`, `transport`), but each variant uses only one. `sm_1` is primary (27 ops vs 18 ops).
- **Ovens (`ov_1`, `ov_2`)**: `ov_1` supports both `burn` and `temper`; `ov_2` supports `burn` only. Variants are partitioned: Line 1 variants use `ov_1`, Line 2 variants use `ov_2`.
- **Work Transports (`wt_1`, `wt_2`)**: Each variant uses only one. `wt_1` serves Line 1, `wt_2` serves Line 2.
- **`pm_1`**: Single punch machine, shared by all variants that require punching.
- **`dm_2`**: Single drill machine, used only by Line 2 variants.
- **`hw_1`**: Single human workstation, shared by all variants.
- **`hbw_1` / `hbw_2`**: Shared warehouses — `hbw_2` is input (raw materials), `hbw_1` is output (finished goods).

---

## 3. Product Variant Routing

### 3.1 WF_101 — Burn → Temper → Mill → Deburr → Sort → Review → Store
**Line 1 only. 2 cases (WF_101_30: 15 ops, WF_101_31: 12 ops).**

| Step | Activity | Resource | Notes |
|---|---|---|---|
| 1 | `/hbw/unload` | hbw_2 | Retrieve workpiece from input warehouse |
| 2 | `/vgr/pick_up_and_transport` | vgr_2 | hbw_2_pos → dm_2_sink_pos |
| 3 | `/hbw/store_empty_bucket` | hbw_2 | Return empty bucket |
| 4 | `/vgr/pick_up_and_transport` | vgr_1 | dm_2_sink_pos → ov_1_pos |
| 5 | `/ov/burn` | ov_1 | Burn (size/thickness per case) |
| 6 | `/ov/temper` | ov_1 | Temper (high intensity) |
| 7 | `/mm/mill` | mm_1 | Mill operation |
| 8 | `/mm/deburr` | mm_1 | Deburr → sm_1_lb_1_pos |
| 9 | `/sm/sort` | sm_1 | Sort → sm_1_automatic_pos |
| 10 | `/vgr/pick_up_and_transport` | vgr_1 | sm_1_sink_N_pos → hw_1_pos |
| 11 | `/hw/human_review` | hw_1 | Quality review |
| 12 | `/vgr/pick_up_and_transport` | vgr_1 | hw_1_pos → hbw_1_waiting_platform_pos |
| 13 | `/hbw/get_empty_bucket` | hbw_1 | Get empty bucket |
| 14 | `/vgr/pick_up_and_transport` | vgr_1 | hbw_1_waiting_platform_pos → hbw_1_pos |
| 15 | `/hbw/store` | hbw_1 | Store finished workpiece |

### 3.2 WF_102 — Burn (ov_2) → Drill → Sort → Lower → Review → Store
**Line 2 only. 2 cases (WF_102_31: 13 ops, WF_102_32: 10 ops).**

| Step | Activity | Resource | Notes |
|---|---|---|---|
| 1 | `/hbw/unload` | hbw_2 | Retrieve workpiece |
| 2 | `/vgr/pick_up_and_transport` | vgr_2 | hbw_2_pos → ov_2_pos |
| 3 | `/wt/pick_up_and_transport` | wt_2 | ov_2_pos → mm_2_initial_pos |
| 4 | `/mm/drill` | mm_2 | Drill (quantity=6, size=30) → sm_2_lb_1_pos |
| 5 | `/sm/transport` | sm_2 | sm_2_lb_1_pos → sm_2_corner_pos |
| 6 | `/dm/lower` | dm_2 | sm_2_corner_pos → dm_2_sink_pos |
| 7 | `/hbw/store_empty_bucket` | hbw_2 | Return empty bucket |
| 8 | `/vgr/pick_up_and_transport` | vgr_1 | dm_2_sink_pos → hw_1_pos |
| 9 | `/hw/human_review` | hw_1 | Quality review |
| 10 | `/vgr/pick_up_and_transport` | vgr_1 | hw_1_pos → hbw_1_waiting_platform_pos |
| 11 | `/hbw/get_empty_bucket` | hbw_1 | Get empty bucket |
| 12 | `/vgr/pick_up_and_transport` | vgr_1 | hbw_1_waiting_platform_pos → hbw_1_pos |
| 13 | `/hbw/store` | hbw_1 | Store finished workpiece |

### 3.3 WF_103 — Burn → Temper → Mill → Deburr → Transport → Punch Recesses → Review → Store
**Line 1 only. 2 cases (WF_103_29: 15 ops, WF_103_30: 15 ops).**

| Step | Activity | Resource | Notes |
|---|---|---|---|
| 1 | `/hbw/unload` | hbw_2 | Retrieve workpiece |
| 2 | `/vgr/pick_up_and_transport` | vgr_2 | hbw_2_pos → dm_2_sink_pos |
| 3 | `/hbw/store_empty_bucket` | hbw_2 | Return empty bucket |
| 4 | `/vgr/pick_up_and_transport` | vgr_1 | dm_2_sink_pos → ov_1_pos |
| 5 | `/ov/burn` | ov_1 | Burn (large/thin) |
| 6 | `/ov/temper` | ov_1 | Temper (high intensity) |
| 7 | `/wt/pick_up_and_transport` | wt_1 | ov_1_pos → mm_1_initial_pos |
| 8 | `/mm/mill` | mm_1 | Mill operation |
| 9 | `/mm/deburr` | mm_1 | Deburr → sm_1_lb_1_pos |
| 10 | `/sm/transport` | sm_1 | sm_1_lb_1_pos → sm_1_corner_pos |
| 11 | `/pm/punch_recesses` | pm_1 | sm_1_corner_pos → pm_1_sink_pos (qty=6) |
| 12 | `/vgr/pick_up_and_transport` | vgr_1 | pm_1_sink_pos → hw_1_pos |
| 13 | `/hw/human_review` | hw_1 | Quality review |
| 14 | `/hbw/get_empty_bucket` | hbw_1 | Get empty bucket |
| 15 | `/vgr/pick_up_and_transport` | vgr_1 | hw_1_pos → hbw_1_waiting_platform_pos |
| 16 | `/vgr/pick_up_and_transport` | vgr_1 | hbw_1_waiting_platform_pos → hbw_1_pos |
| 17 | `/hbw/store` | hbw_1 | Store finished workpiece |

### 3.4 WF_104 — Cross-Line: Burn (ov_2) → Mill (mm_2) → Sort (sm_2) → Deburr (mm_1) → Transport (sm_1) → Punch Gill (pm_1) → Review → Store
**Two-stage design: Line 2 first, then Line 1. 1 complete case (WF_104_20: 16 ops).**

| Step | Activity | Resource | Line | Notes |
|---|---|---|---|---|
| 1 | `/vgr/pick_up_and_transport` | vgr_2 | L2 | hbw_2_pos → ov_2_pos |
| 2 | `/hbw/store_empty_bucket` | hbw_2 | — | Return empty bucket |
| 3 | `/ov/burn` | ov_2 | L2 | Burn (maxi/thin) |
| 4 | `/wt/pick_up_and_transport` | wt_2 | L2 | ov_2_pos → mm_2_initial_pos |
| 5 | `/mm/mill` | mm_2 | L2 | Mill → sm_2_lb_1_pos |
| 6 | `/sm/sort` | sm_2 | L2 | Sort → sm_2_automatic_pos |
| 7 | `/vgr/pick_up_and_transport` | vgr_2 | L2→L1 | sm_2_sink_2_pos → dm_2_sink_pos |
| 8 | `/vgr/pick_up_and_transport` | vgr_1 | L1 | dm_2_sink_pos → ov_1_pos |
| 9 | `/wt/pick_up_and_transport` | wt_1 | L1 | ov_1_pos → mm_1_initial_pos |
| 10 | `/mm/deburr` | mm_1 | L1 | Deburr → sm_1_lb_1_pos |
| 11 | `/sm/transport` | sm_1 | L1 | sm_1_lb_1_pos → sm_1_corner_pos |
| 12 | `/pm/punch_gill` | pm_1 | — | sm_1_corner_pos → pm_1_sink_pos (qty=8) |
| 13 | `/vgr/pick_up_and_transport` | vgr_1 | — | pm_1_sink_pos → hw_1_pos |
| 14 | `/hw/human_review` | hw_1 | — | Quality review |
| 15 | `/hbw/get_empty_bucket` | hbw_1 | — | Get empty bucket |
| 16 | `/vgr/pick_up_and_transport` | vgr_1 | — | hw_1_pos → hbw_1_waiting_platform_pos |
| 17 | `/vgr/pick_up_and_transport` | vgr_1 | — | hbw_1_waiting_platform_pos → hbw_1_pos |
| 18 | `/hbw/store` | hbw_1 | — | Store finished workpiece |

**Note:** WF_104 is the only variant with intentional cross-line routing. It starts on Line 2 (ov_2, mm_2, sm_2) and transitions to Line 1 (mm_1, sm_1, pm_1). `vgr_2` performs two transports (steps 1 and 7) — an exception to the standard role-based assignment.

### 3.5 WF_105 — Burn → Deburr → Sort → Review → Store
**Line 1 only. 2 cases (WF_105_21: 12 ops, WF_105_22: 10 ops).**

| Step | Activity | Resource | Notes |
|---|---|---|---|
| 1 | `/hbw/unload` | hbw_2 | Retrieve workpiece |
| 2 | `/vgr/pick_up_and_transport` | vgr_2 | hbw_2_pos → dm_2_sink_pos |
| 3 | `/hbw/store_empty_bucket` | hbw_2 | Return empty bucket |
| 4 | `/vgr/pick_up_and_transport` | vgr_1 | dm_2_sink_pos → ov_1_pos |
| 5 | `/ov/burn` | ov_1 | Burn (regular/thick) |
| 6 | `/wt/pick_up_and_transport` | wt_1 | ov_1_pos → mm_1_initial_pos |
| 7 | `/mm/deburr` | mm_1 | Deburr → sm_1_lb_1_pos |
| 8 | `/sm/sort` | sm_1 | Sort → sm_1_automatic_pos |
| 9 | `/vgr/pick_up_and_transport` | vgr_1 | sm_1_sink_N_pos → hw_1_pos |
| 10 | `/hw/human_review` | hw_1 | Quality review |
| 11 | `/hbw/get_empty_bucket` | hbw_1 | Get empty bucket |
| 12 | `/vgr/pick_up_and_transport` | vgr_1 | hw_1_pos → hbw_1_waiting_platform_pos |
| 13 | `/vgr/pick_up_and_transport` | vgr_1 | hbw_1_waiting_platform_pos → hbw_1_pos |
| 14 | `/hbw/store` | hbw_1 | Store finished workpiece |

### 3.6 WF_108 — Burn (ov_2) → Drill (mm_2) → Deburr (mm_2) → Sort (sm_2) → Review → Store
**Line 2 only. 1 complete case (WF_108_17: 13 ops).**

| Step | Activity | Resource | Notes |
|---|---|---|---|
| 1 | `/hbw/unload` | hbw_2 | Retrieve workpiece |
| 2 | `/vgr/pick_up_and_transport` | vgr_2 | hbw_2_pos → ov_2_pos |
| 3 | `/hbw/store_empty_bucket` | hbw_2 | Return empty bucket |
| 4 | `/ov/burn` | ov_2 | Burn (maxi/thick) |
| 5 | `/wt/pick_up_and_transport` | wt_2 | ov_2_pos → mm_2_initial_pos |
| 6 | `/mm/drill` | mm_2 | Drill (qty=4, size=30) → mm_2_initial_pos |
| 7 | `/mm/deburr` | mm_2 | Deburr → sm_2_lb_1_pos |
| 8 | `/sm/sort` | sm_2 | Sort → sm_2_automatic_pos |
| 9 | `/vgr/pick_up_and_transport` | vgr_2 | sm_2_sink_1_pos → dm_2_sink_pos |
| 10 | `/vgr/pick_up_and_transport` | vgr_1 | dm_2_sink_pos → hw_1_pos |
| 11 | `/hw/human_review` | hw_1 | Quality review |
| 12 | `/vgr/pick_up_and_transport` | vgr_1 | hw_1_pos → hbw_1_waiting_platform_pos |
| 13 | `/hbw/get_empty_bucket` | hbw_1 | Get empty bucket |
| 14 | `/vgr/pick_up_and_transport` | vgr_1 | hbw_1_waiting_platform_pos → hbw_1_pos |
| 15 | `/hbw/store` | hbw_1 | Store finished workpiece |

### 3.7 WF_109 — Burn → Temper → Mill → Deburr → Transport → Punch Ribbing → Review → Store
**Line 1 only. 1 complete case (WF_109_15: 15 ops).**

| Step | Activity | Resource | Notes |
|---|---|---|---|
| 1 | `/hbw/unload` | hbw_2 | Retrieve workpiece |
| 2 | `/vgr/pick_up_and_transport` | vgr_2 | hbw_2_pos → dm_2_sink_pos |
| 3 | `/hbw/store_empty_bucket` | hbw_2 | Return empty bucket |
| 4 | `/vgr/pick_up_and_transport` | vgr_1 | dm_2_sink_pos → ov_1_pos |
| 5 | `/ov/burn` | ov_1 | Burn (regular/thin) |
| 6 | `/ov/temper` | ov_1 | Temper (high intensity) |
| 7 | `/wt/pick_up_and_transport` | wt_1 | ov_1_pos → mm_1_initial_pos |
| 8 | `/mm/mill` | mm_1 | Mill operation |
| 9 | `/mm/deburr` | mm_1 | Deburr → sm_1_lb_1_pos |
| 10 | `/sm/transport` | sm_1 | sm_1_lb_1_pos → sm_1_corner_pos |
| 11 | `/pm/punch_ribbing` | pm_1 | sm_1_corner_pos → pm_1_sink_pos (qty=6) |
| 12 | `/vgr/pick_up_and_transport` | vgr_1 | pm_1_sink_pos → hw_1_pos |
| 13 | `/hw/human_review` | hw_1 | Quality review |
| 14 | `/vgr/pick_up_and_transport` | vgr_1 | hw_1_pos → hbw_1_waiting_platform_pos |
| 15 | `/hbw/get_empty_bucket` | hbw_1 | Get empty bucket |
| 16 | `/vgr/pick_up_and_transport` | vgr_1 | hbw_1_waiting_platform_pos → hbw_1_pos |
| 17 | `/hbw/store` | hbw_1 | Store finished workpiece |

### 3.8 WF_1106 — Transport (mm_2) → Transport (sm_2) → Cylindrical Drill → Review → Store
**Line 2 only. 2 cases (WF_1106_21: 10 ops, WF_1106_22: 14 ops).**

| Step | Activity | Resource | Notes |
|---|---|---|---|
| 1 | `/hbw/unload` | hbw_2 | Retrieve workpiece |
| 2 | `/vgr/pick_up_and_transport` | vgr_2 | hbw_2_pos → ov_2_pos |
| 3 | `/hbw/store_empty_bucket` | hbw_2 | Return empty bucket |
| 4 | `/wt/pick_up_and_transport` | wt_2 | ov_2_pos → mm_2_initial_pos |
| 5 | `/mm/transport_from_to` | mm_2 | mm_2_initial_pos → sm_2_lb_1_pos |
| 6 | `/sm/transport` | sm_2 | sm_2_lb_1_pos → sm_2_corner_pos |
| 7 | `/dm/cylindrical_drill` | dm_2 | sm_2_corner_pos → dm_2_sink_pos (qty=4) |
| 8 | `/vgr/pick_up_and_transport` | vgr_1 | dm_2_sink_pos → hw_1_pos |
| 9 | `/hw/human_review` | hw_1 | Quality review |
| 10 | `/vgr/pick_up_and_transport` | vgr_1 | hw_1_pos → hbw_1_waiting_platform_pos |
| 11 | `/hbw/get_empty_bucket` | hbw_1 | Get empty bucket |
| 12 | `/vgr/pick_up_and_transport` | vgr_1 | hbw_1_waiting_platform_pos → hbw_1_pos |
| 13 | `/hbw/store` | hbw_1 | Store finished workpiece |

### 3.9 WF_1107 — Burn → Drill (mm_1) → Transport → Punch Ribbing → Review → Store
**Line 1 only. 1 complete case (WF_1107_16: 13 ops).**

| Step | Activity | Resource | Notes |
|---|---|---|---|
| 1 | `/hbw/unload` | hbw_2 | Retrieve workpiece |
| 2 | `/vgr/pick_up_and_transport` | vgr_2 | hbw_2_pos → dm_2_sink_pos |
| 3 | `/hbw/store_empty_bucket` | hbw_2 | Return empty bucket |
| 4 | `/vgr/pick_up_and_transport` | vgr_1 | dm_2_sink_pos → ov_1_pos |
| 5 | `/ov/burn` | ov_1 | Burn (large/thick) |
| 6 | `/wt/pick_up_and_transport` | wt_1 | ov_1_pos → mm_1_initial_pos |
| 7 | `/mm/drill` | mm_1 | Drill (qty=6, size=40) → sm_1_lb_1_pos |
| 8 | `/sm/transport` | sm_1 | sm_1_lb_1_pos → sm_1_corner_pos |
| 9 | `/pm/punch_ribbing` | pm_1 | sm_1_corner_pos → pm_1_sink_pos (qty=10) |
| 10 | `/vgr/pick_up_and_transport` | vgr_1 | pm_1_sink_pos → hw_1_pos |
| 11 | `/hw/human_review` | hw_1 | Quality review |
| 12 | `/vgr/pick_up_and_transport` | vgr_1 | hw_1_pos → hbw_1_waiting_platform_pos |
| 13 | `/hbw/get_empty_bucket` | hbw_1 | Get empty bucket |
| 14 | `/vgr/pick_up_and_transport` | vgr_1 | hbw_1_waiting_platform_pos → hbw_1_pos |
| 15 | `/hbw/store` | hbw_1 | Store finished workpiece |

---

## 4. Routing Summary Matrix

| Variant | Line | Burn | Temper | Mill | Deburr | Drill | Sort | Transport | Punch | Lower | CylDrill | Review | Store |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WF_101 | L1 | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | — | — | — | ✓ | ✓ |
| WF_102 | L2 | ✓ | — | — | — | ✓ | — | ✓ | — | ✓ | — | ✓ | ✓ |
| WF_103 | L1 | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | Recess | — | — | ✓ | ✓ |
| WF_104 | L2→L1 | ✓ | — | ✓ | ✓ | — | ✓ | ✓ | Gill | — | — | ✓ | ✓ |
| WF_105 | L1 | ✓ | — | — | ✓ | — | ✓ | — | — | — | — | ✓ | ✓ |
| WF_108 | L2 | ✓ | — | — | ✓ | ✓ | ✓ | — | — | — | — | ✓ | ✓ |
| WF_109 | L1 | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | Ribbing | — | — | ✓ | ✓ |
| WF_1106 | L2 | — | — | — | — | — | — | ✓ | — | — | ✓ | ✓ | ✓ |
| WF_1107 | L1 | ✓ | — | — | — | ✓ | — | ✓ | Ribbing | — | — | ✓ | ✓ |

---

## 5. Special Conditions

### 5.1 VGR Role-Based Assignment

**Rule:** `vgr_2` performs the **first** transport (always from `hbw_2_pos` to the first processing station). `vgr_1` performs **all subsequent** transports.

**Exceptions (documented in source data):**
- **WF_104**: `vgr_2` performs two transports (step 1: hbw_2→ov_2, step 7: sm_2_sink→dm_2_sink) because of cross-line routing.
- **WF_108**: `vgr_2` performs two transports (step 2: hbw_2→ov_2, step 9: sm_2_sink→dm_2_sink) for the same cross-line pattern.

**Simulation modeling:** Implement as a priority rule — `vgr_2` is assigned to the first transport of each workpiece; `vgr_1` handles all remaining transports. For WF_104 and WF_108, `vgr_2` also handles the mid-route cross-line transport.

### 5.2 Cross-Line Routing (WF_104)

WF_104 is the **only** variant with intentional cross-line routing:
- **Stage 1 (Line 2):** Burn on `ov_2`, Mill on `mm_2`, Sort on `sm_2`
- **Transition:** `vgr_2` transports from `sm_2_sink_2_pos` to `dm_2_sink_pos`
- **Stage 2 (Line 1):** Deburr on `mm_1`, Transport on `sm_1`, Punch Gill on `pm_1`

This is a two-stage design, not an error. No other variant crosses lines.

### 5.3 Failure Handling (Retryable Events)

**8 failure events** observed (7 × HTTP 418, 1 × HTTP 401):

| Event ID | Case | Activity | Resource | Status | Outcome |
|---|---|---|---|---|---|
| 2473 | WF_103_29 | /hbw/store_empty_bucket | hbw_2 | 418 | Workpiece continued |
| 2513 | WF_103_29 | /vgr/pick_up_and_transport | vgr_1 | 418 | Workpiece continued |
| 2536 | WF_104_20 | /vgr/pick_up_and_transport | vgr_1 | 418 | Workpiece continued |
| 2541 | WF_1106_21 | /vgr/pick_up_and_transport | vgr_1 | 418 | Workpiece continued |
| 2575 | WF_105_22 | /hbw/store_empty_bucket | hbw_2 | 418 | Workpiece continued |
| 2587 | WF_109_15 | /vgr/pick_up_and_transport | vgr_1 | 418 | Workpiece continued |
| 2604 | WF_103_30 | /vgr/pick_up_and_transport | vgr_1 | 418 | Workpiece continued |
| 2645 | WF_108_18 | /hbw/unload | hbw_2 | 401 | Case incomplete (truncated) |

**Modeling approach:** Treat failures as **retryable** — the operation retries and eventually succeeds; the workpiece continues its route. In simulation, model as a stochastic retry mechanism with a small probability of failure per attempt.

### 5.4 Warehouse Return Sequence (Canonical End-of-Process)

Every complete variant follows this canonical warehouse-return sequence:

1. `/vgr/pick_up_and_transport` — `hw_1_pos` → `hbw_1_waiting_platform_pos` (vgr_1)
2. `/hbw/get_empty_bucket` — `hbw_1` (get empty bucket)
3. `/vgr/pick_up_and_transport` — `hbw_1_waiting_platform_pos` → `hbw_1_pos` (vgr_1)
4. `/hbw/store` — `hbw_1` (store finished workpiece)

**Note:** Some cases in the dataset are missing steps 3–4 due to time-window truncation. In simulation, this sequence is **mandatory** for every variant.

### 5.5 Sorting Machine Ejection Position

The sorting machine ejection position is **stochastic** — uniformly distributed over {1, 2, 3}:

| Position | Count | Percentage |
|---|---|---|
| 1 | 6 | 33.3% |
| 2 | 6 | 33.3% |
| 3 | 6 | 33.3% |

**Modeling approach:** Sample uniformly from {1, 2, 3} at each sort operation. The ejection position determines the VGR pickup location (`sm_N_sink_1_pos`, `sm_N_sink_2_pos`, or `sm_N_sink_3_pos`).

### 5.6 Incomplete Cases

Four cases are incomplete (time-window truncation):

| Case | Variant | Operations | Status |
|---|---|---|---|
| WF_104_21 | WF_104 | 4 | Incomplete — excluded from routing inference |
| WF_108_18 | WF_108 | 1 | Failed at first step (HTTP 401) |
| WF_109_16 | WF_109 | 1 | Incomplete — excluded from routing inference |
| WF_1107_17 | WF_1107 | 3 | Incomplete — excluded from routing inference |

These cases are **retained** in the dataset but **excluded** from routing inference.

---

## 6. Structural Observations for Simulation Modeling

### 6.1 Two-Line Architecture

The system comprises two parallel processing lines:

- **Line 1:** `ov_1` → `wt_1` → `mm_1` → `sm_1`
- **Line 2:** `ov_2` → `wt_2` → `mm_2` → `sm_2` → `dm_2`

Shared resources bridge both lines: `vgr_1`, `vgr_2`, `pm_1`, `hw_1`, `hbw_1`, `hbw_2`.

### 6.2 Bottleneck Candidates

- **`hw_1` (Human Workstation):** Every variant requires human review. Single resource, shared by all variants.
- **`pm_1` (Punch Machine):** Shared by 4 variants (WF_103, WF_104, WF_109, WF_1107). Single resource.
- **`vgr_1`:** Handles the majority of transport operations (111 of 165 total VGR ops).
- **`hbw_2`:** All variants start with unload from `hbw_2`.

### 6.3 Variant Line Assignment

| Line 1 Variants | Line 2 Variants | Cross-Line |
|---|---|---|
| WF_101, WF_103, WF_105, WF_109, WF_1107 | WF_102, WF_108, WF_1106 | WF_104 (L2→L1) |

### 6.4 Process Parameter Variability

- **Burn size/thickness:** Varies per case (regular/large/maxi/middle × thin/thick). Does not affect routing, only processing time.
- **Drill quantity:** Varies (4–10 holes). Affects processing time.
- **Punch quantity:** Varies (6–10 punches). Affects processing time.
- **Temper intensity:** Always `ov_1_temper_high` (no variability observed).

### 6.5 Activity Duration Notes

- `actual_duration` is computed as `operation_end_time − time:timestamp` for `start` transitions.
- Mean actual duration across all start transitions: ~31.95 seconds.
- Duration varies significantly by activity type (e.g., burn/temper are longer, VGR transport is shorter).

---

## 7. Confidence Assessment

| Finding | Confidence | Rationale |
|---|---|---|
| Resource inventory (15 entities) | **High** | Directly observed in `org:resource` column |
| Variant routing (9 variants) | **High** | Consistent across multiple cases per variant |
| VGR role-based assignment | **High** | 100% consistent across all 18 cases |
| Cross-line routing (WF_104 only) | **High** | Explicitly documented; only variant with L2→L1 transition |
| Sorting ejection stochasticity | **High** | Perfect uniform distribution (6/6/6) across 3 positions |
| Failure retry behavior | **High** | All failed operations' workpieces continued successfully |
| Warehouse return canonical sequence | **High** | Present in all complete cases; absences are truncation |
| Two-line architecture | **High** | Clear resource partitioning (mm_1 vs mm_2, sm_1 vs sm_2, etc.) |
| Bottleneck identification | **Medium** | Based on single production run; needs validation with more data |
| Processing time distributions | **Medium** | Limited sample size (192 operations); distributions need more data |
