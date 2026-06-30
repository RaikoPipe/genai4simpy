# Topology Report — Fischertechnik Lab B Manufacturing System

## 1. Dataset Characteristics

| Property | Value |
|---|---|
| Source file | `eventlog_cleaned.parquet` |
| Total events | 1,383 (461 entities × 3 transitions each) |
| Unique entities (workpieces) | 461 |
| Unique workflow instances (cases) | 38 |
| Workflow templates | 9 (WF_101, WF_102, WF_103, WF_104, WF_105, WF_108, WF_109, WF_1106, WF_1107) |
| Distinct operations | 20 |
| Distinct resources | 15 |
| Time span | 2021-06-30 16:04:34 — 2021-06-30 18:03:37 UTC (~2 hours) |
| Failure events | 9 (1.96% of entities) |

**Grain model:** Each entity (`identifier:id`) represents a single atomic operation on a workpiece (3 events: scheduled → start → complete). A *case* (workflow instance) groups sequential operations that together process one workpiece through its full manufacturing route. Operations within a case are ordered by timestamp.

---

## 2. Resource Inventory

### 2.1 Resource Classes and Entities

| Resource Class | Entities | Count | Description |
|---|---|---|---|
| `hbw` (High Bay Warehouse) | `hbw_1`, `hbw_2` | 2 | Storage/retrieval; hbw_2 handles unloading, hbw_1 handles bucket management |
| `vgr` (Vertical Guide Rail / AGV) | `vgr_1`, `vgr_2` | 2 | Primary transport between stations |
| `wt` (Work Transporter) | `wt_1`, `wt_2` | 2 | Secondary transport (oven-to-mill lane) |
| `mm` (Milling Machine) | `mm_1`, `mm_2` | 2 | Milling, deburring, drilling, transport |
| `ov` (Oven) | `ov_1`, `ov_2` | 2 | Heat treatment (burn/temper) |
| `sm` (Sorting Machine) | `sm_1`, `sm_2` | 2 | Sorting and transport |
| `pm` (Punching Machine) | `pm_1` | 1 | Punching (recesses, gill, ribbing) |
| `dm` (Drilling Machine) | `dm_2` | 1 | Drilling (lower, cylindrical) |
| `hw` (Human Workstation) | `hw_1` | 1 | Manual quality review |

### 2.2 Resource–Activity Mapping

| Resource | Activities |
|---|---|
| `hbw_1` | `/hbw/get_empty_bucket`, `/hbw/store`, `/hbw/store_empty_bucket` |
| `hbw_2` | `/hbw/unload`, `/hbw/store_empty_bucket` |
| `vgr_1` | `/vgr/pick_up_and_transport` |
| `vgr_2` | `/vgr/pick_up_and_transport` |
| `wt_1` | `/wt/pick_up_and_transport` |
| `wt_2` | `/wt/pick_up_and_transport` |
| `mm_1` | `/mm/mill`, `/mm/deburr`, `/mm/transport_from_to` |
| `mm_2` | `/mm/mill`, `/mm/deburr`, `/mm/drill`, `/mm/transport_from_to` |
| `ov_1` | `/ov/burn`, `/ov/temper` |
| `ov_2` | `/ov/burn` |
| `sm_1` | `/sm/sort`, `/sm/transport` |
| `sm_2` | `/sm/sort`, `/sm/transport` |
| `pm_1` | `/pm/punch_recesses`, `/pm/punch_gill`, `/pm/punch_ribbing` |
| `dm_2` | `/dm/lower`, `/dm/cylindrical_drill` |
| `hw_1` | `/hw/human_review` |

### 2.3 Resource Pooling Analysis

| Activity | Pool Members | Pooling Type |
|---|---|---|
| `/vgr/pick_up_and_transport` | `vgr_1`, `vgr_2` | Full pool (interchangeable) |
| `/wt/pick_up_and_transport` | `wt_1`, `wt_2` | Full pool (interchangeable) |
| `/mm/mill` | `mm_1`, `mm_2` | Full pool |
| `/mm/deburr` | `mm_1`, `mm_2` | Full pool |
| `/mm/transport_from_to` | `mm_1`, `mm_2` | Full pool |
| `/ov/burn` | `ov_1`, `ov_2` | Full pool |
| `/sm/sort` | `sm_1`, `sm_2` | Full pool |
| `/sm/transport` | `sm_1`, `sm_2` | Full pool |
| `/hbw/store_empty_bucket` | `hbw_1`, `hbw_2` | Partial pool (also dedicated on each) |

**Dedicated resources** (single instance, no pooling):
- `pm_1` — all punching operations
- `dm_2` — all drilling operations
- `hw_1` — human review
- `ov_1` — tempering (only ov_1 can temper)
- `mm_2` — drilling (`/mm/drill` only on mm_2)

**Usage imbalance:** vgr_1 handles 85 operations vs vgr_2 at 42; hbw_2 handles 74 vs hbw_1 at 30. This reflects lane-based routing: vgr_2 primarily serves the hbw_2 → ov_2 → mm_2 lane, while vgr_1 serves the mm_1 → pm_1 → hw_1 lane.

---

## 3. Routing Topology

### 3.1 Common Pattern Structure

All workflows share a common backbone:

```
[hbw_2: unload] → [vgr_2: transport] → [hbw_2: store_empty_bucket] → [processing lane] → [hw_1: human_review] → [optional: hbw_1 storage]
```

The **processing lane** differs per workflow type. Two parallel lanes exist:
- **Lane 1 (mm_1 lane):** ov_1 → wt_1 → mm_1 → sm_1 → pm_1
- **Lane 2 (mm_2 lane):** ov_2 → wt_2 → mm_2 → sm_2 → dm_2

### 3.2 Workflow Routing Sequences

#### WF_101 — Mill + Deburr + Sort (Oven Lane 1)
**Instances:** 6 cases, 83 entities | **Canonical length:** 12–16 steps

```
1.  /hbw/unload              @ hbw_2
2.  /vgr/pick_up_and_transport @ vgr_2
3.  /hbw/store_empty_bucket  @ hbw_2
4.  /vgr/pick_up_and_transport @ vgr_1
5.  /ov/burn                 @ ov_1
6.  /ov/temper               @ ov_1
7.  /wt/pick_up_and_transport @ wt_1
8.  /mm/mill                 @ mm_1
9.  /mm/deburr               @ mm_1
10. /sm/sort                 @ sm_1
11. /vgr/pick_up_and_transport @ vgr_1
12. /hw/human_review         @ hw_1
[13. /hbw/get_empty_bucket   @ hbw_1]   ← conditional (83% of cases)
[14. /vgr/pick_up_and_transport @ vgr_1]
[15. /vgr/pick_up_and_transport @ vgr_1]
[16. /hbw/store              @ hbw_1]
```

**Confidence:** High — deterministic routing, consistent across all 6 cases.

---

#### WF_102 — Drill + Lower (Oven Lane 2)
**Instances:** 5 cases, 48 entities | **Canonical length:** 10–14 steps

```
1.  /hbw/unload              @ hbw_2
2.  /vgr/pick_up_and_transport @ vgr_2
3.  /hbw/store_empty_bucket  @ hbw_2
4.  /ov/burn                 @ ov_2          ← conditional (60% of cases)
5.  /wt/pick_up_and_transport @ wt_2
6.  /mm/drill                @ mm_2
7.  /sm/transport            @ sm_2
8.  /dm/lower                @ dm_2
9.  /vgr/pick_up_and_transport @ vgr_1
10. /hw/human_review         @ hw_1
[11. /vgr/pick_up_and_transport @ vgr_1]
[12. /hbw/get_empty_bucket   @ hbw_1]       ← conditional (60% of cases)
[13. /vgr/pick_up_and_transport @ vgr_1]
[14. /hbw/store              @ hbw_1]
```

**Truncated cases:** WF_102_17 (1 step, failure at hbw/unload), WF_102_16 (9 steps, failure at vgr transport after dm/lower).

**Confidence:** High — deterministic core; ov_2 burn is conditional.

---

#### WF_103 — Mill + Deburr + Punch Recesses (Oven Lane 1)
**Instances:** 5 cases, 57 entities | **Canonical length:** 13 steps

```
1.  /hbw/unload              @ hbw_2
2.  /vgr/pick_up_and_transport @ vgr_2
3.  /hbw/store_empty_bucket  @ hbw_2
4.  /vgr/pick_up_and_transport @ vgr_1
5.  /ov/burn                 @ ov_1
6.  /ov/temper               @ ov_1
7.  /wt/pick_up_and_transport @ wt_1
8.  /mm/mill                 @ mm_1
9.  /mm/deburr               @ mm_1
10. /sm/transport            @ sm_1
11. /pm/punch_recesses       @ pm_1
12. /vgr/pick_up_and_transport @ vgr_1
13. /hw/human_review         @ hw_1
```

**Truncated case:** WF_103_14 (5 steps, stopped after ov/burn — all events succeeded, likely data truncation).

**Confidence:** High — fully deterministic, no storage tail.

---

#### WF_104 — Mill + Sort + Punch Gill (Dual-Lane)
**Instances:** 5 cases, 59 entities | **Canonical length:** 14–21 steps

```
1.  /hbw/unload              @ hbw_2
2.  /vgr/pick_up_and_transport @ vgr_2
3.  /hbw/store_empty_bucket  @ hbw_2
4.  /ov/burn                 @ ov_2          ← conditional (80% of cases)
5.  /wt/pick_up_and_transport @ wt_2
6.  /mm/mill                 @ mm_2
7.  /sm/sort                 @ sm_2
8.  /vgr/pick_up_and_transport @ vgr_2
9.  /vgr/pick_up_and_transport @ vgr_1
10. /wt/pick_up_and_transport @ wt_1
11. /mm/deburr               @ mm_1
12. /sm/transport            @ sm_1
13. /pm/punch_gill           @ pm_1
14. /vgr/pick_up_and_transport @ vgr_1
15. /hw/human_review         @ hw_1
[16. /vgr/pick_up_and_transport @ vgr_1]
[17. /hbw/get_empty_bucket   @ hbw_1]       ← conditional (60% of cases)
[18. /vgr/pick_up_and_transport @ vgr_1]
[19. /hbw/store              @ hbw_1]
```

**Non-deterministic element:** WF_104_8 had 3 consecutive wt_1 transport steps (2 failed, 1 succeeded) between steps 10–12, indicating a retry pattern.

**Truncated cases:** WF_104_9 (1 step, failure at hbw/unload), WF_104_7 (4 steps, stopped after ov/burn).

**Confidence:** Medium — dual-lane routing with conditional oven step and retry behavior.

---

#### WF_105 — Deburr + Sort (Oven Lane 1, no milling)
**Instances:** 4 cases, 44 entities | **Canonical length:** 8–14 steps

```
1.  /hbw/unload              @ hbw_2
2.  /vgr/pick_up_and_transport @ vgr_2
3.  /hbw/store_empty_bucket  @ hbw_2
4.  /vgr/pick_up_and_transport @ vgr_1
5.  /ov/burn                 @ ov_1
6.  /wt/pick_up_and_transport @ wt_1
7.  /mm/deburr               @ mm_1
8.  /sm/sort                 @ sm_1
[9.  /vgr/pick_up_and_transport @ vgr_1]
[10. /hw/human_review        @ hw_1]        ← conditional (50% of cases)
[11. /vgr/pick_up_and_transport @ vgr_1]
[12. /hbw/get_empty_bucket   @ hbw_1]
[13. /vgr/pick_up_and_transport @ vgr_1]
[14. /hbw/store              @ hbw_1]
```

**Confidence:** High — deterministic core; human review and storage are conditional.

---

#### WF_108 — Drill + Deburr + Sort (Lane 2)
**Instances:** 3 cases, 40 entities | **Canonical length:** 10–15 steps

```
1.  /hbw/unload              @ hbw_2
2.  /vgr/pick_up_and_transport @ vgr_2
3.  /hbw/store_empty_bucket  @ hbw_2
4.  /ov/burn                 @ ov_2          ← conditional (67% of cases)
5.  /wt/pick_up_and_transport @ wt_2
6.  /mm/drill                @ mm_2
7.  /mm/deburr               @ mm_2
8.  /sm/sort                 @ sm_2
9.  /vgr/pick_up_and_transport @ vgr_2
10. /vgr/pick_up_and_transport @ vgr_1
11. /hw/human_review         @ hw_1
[12. /hbw/get_empty_bucket   @ hbw_1]       ← conditional (67% of cases)
[13. /vgr/pick_up_and_transport @ vgr_1]
[14. /vgr/pick_up_and_transport @ vgr_1]
[15. /hbw/store              @ hbw_1]
```

**Confidence:** High — deterministic core; oven and storage are conditional.

---

#### WF_109 — Mill + Deburr + Punch Ribbing (Oven Lane 1)
**Instances:** 4 cases, 53 entities | **Canonical length:** 13 steps

```
1.  /hbw/unload              @ hbw_2
2.  /vgr/pick_up_and_transport @ vgr_2
3.  /hbw/store_empty_bucket  @ hbw_2
4.  /vgr/pick_up_and_transport @ vgr_1
5.  /ov/burn                 @ ov_1
6.  /ov/temper               @ ov_1
7.  /wt/pick_up_and_transport @ wt_1
8.  /mm/mill                 @ mm_1
9.  /mm/deburr               @ mm_1
10. /sm/transport            @ sm_1
11. /pm/punch_ribbing        @ pm_1
12. /vgr/pick_up_and_transport @ vgr_1
13. /hw/human_review         @ hw_1
```

**Confidence:** High — fully deterministic, no storage tail.

---

#### WF_1106 — Cylindrical Drill (Lane 2, variable milling)
**Instances:** 4 cases, 46 entities | **Canonical length:** 8–14 steps

```
1.  /hbw/unload              @ hbw_2
2.  /vgr/pick_up_and_transport @ vgr_2
3.  /hbw/store_empty_bucket  @ hbw_2
4.  /ov/burn                 @ ov_2
5.  /wt/pick_up_and_transport @ wt_2
6.  /mm/{deburr|mill|transport_from_to} @ mm_2   ← VARIABLE
7.  /sm/transport            @ sm_2
8.  /dm/cylindrical_drill    @ dm_2
9.  /vgr/pick_up_and_transport @ vgr_1
10. /hw/human_review         @ hw_1
[11. /hbw/get_empty_bucket   @ hbw_1]       ← conditional (50% of cases)
[12. /vgr/pick_up_and_transport @ vgr_1]
[13. /vgr/pick_up_and_transport @ vgr_1]
[14. /hbw/store              @ hbw_1]
```

**Non-deterministic element:** Step 6 varies:
- `/mm/deburr` (WF_1106_6)
- `/mm/mill` (WF_1106_7)
- `/mm/transport_from_to` (WF_1106_8, WF_1106_9)

**Truncated case:** WF_1106_9 (8 steps, stopped after dm/cylindrical_drill — all events succeeded).

**Confidence:** Medium — step 6 is non-deterministic (3 variants observed).

---

#### WF_1107 — Punch Ribbing/Recesses (Lane 1, variable milling)
**Instances:** 2 cases, 31 entities | **Canonical length:** 15–16 steps

```
1.  /hbw/unload              @ hbw_2
2.  /vgr/pick_up_and_transport @ vgr_2
3.  /hbw/store_empty_bucket  @ hbw_2
4.  /vgr/pick_up_and_transport @ vgr_1
5.  /ov/burn                 @ ov_1
6.  /wt/pick_up_and_transport @ wt_1
7.  /mm/{transport_from_to|mill} @ mm_1     ← VARIABLE
8.  /sm/transport            @ sm_1
9.  /pm/{punch_ribbing|punch_recesses} @ pm_1  ← VARIABLE
10. /vgr/pick_up_and_transport @ vgr_1
11. /hw/human_review         @ hw_1
[12. /hbw/get_empty_bucket   @ hbw_1]
[13. /vgr/pick_up_and_transport @ vgr_1]
[14. /vgr/pick_up_and_transport @ vgr_1]
[15. /hbw/store              @ hbw_1]
```

**Non-deterministic elements:**
- Step 7: `/mm/transport_from_to` (WF_1107_6) vs `/mm/mill` (WF_1107_7)
- Step 9: `/pm/punch_ribbing` (WF_1107_6) vs `/pm/punch_recesses` (WF_1107_7)

**Confidence:** Medium — 2 variants observed across 2 cases; step 7 and step 9 vary.

---

### 3.3 Routing Summary Table

| Workflow | Lane | Core Operations | Length | Deterministic? | Storage Tail? |
|---|---|---|---|---|---|
| WF_101 | 1 (mm_1) | burn → temper → mill → deburr → sort | 12–16 | Yes | Conditional (83%) |
| WF_102 | 2 (mm_2) | [burn] → drill → lower | 10–14 | Yes (burn optional) | Conditional (60%) |
| WF_103 | 1 (mm_1) | burn → temper → mill → deburr → punch_recesses | 13 | Yes | No |
| WF_104 | 2→1 (dual) | [burn] → mill → sort → deburr → punch_gill | 14–21 | Partial (retries) | Conditional (60%) |
| WF_105 | 1 (mm_1) | burn → deburr → sort | 8–14 | Yes | Conditional (50%) |
| WF_108 | 2 (mm_2) | [burn] → drill → deburr → sort | 10–15 | Yes (burn optional) | Conditional (67%) |
| WF_109 | 1 (mm_1) | burn → temper → mill → deburr → punch_ribbing | 13 | Yes | No |
| WF_1106 | 2 (mm_2) | burn → {deburr/mill/transport} → cyl_drill | 8–14 | No (step 6 varies) | Conditional (50%) |
| WF_1107 | 1 (mm_1) | burn → {transport/mill} → {ribbing/recesses} | 15–16 | No (steps 7,9 vary) | Yes (100%) |

---

## 4. Special Conditions

### 4.1 Failure Events (9 total)

| Entity | Case | Operation | Resource | Impact |
|---|---|---|---|---|
| a_13354 | WF_102_15 | /hbw/store_empty_bucket | hbw_2 | Terminal — no retry |
| a_13611 | WF_104_8 | /hbw/store_empty_bucket | hbw_2 | Terminal — no retry |
| a_14015 | WF_104_8 | /wt/pick_up_and_transport | wt_1 | Terminal — retried (a_14055) |
| a_14055 | WF_104_8 | /wt/pick_up_and_transport | wt_1 | Terminal — retried (a_14239) |
| a_14239 | WF_104_8 | /wt/pick_up_and_transport | wt_1 | Success (3rd attempt) |
| a_15150 | WF_104_9 | /hbw/unload | hbw_2 | Terminal — case truncated |
| a_15339 | WF_102_16 | /vgr/pick_up_and_transport | vgr_1 | Terminal — case truncated |
| a_16268 | WF_102_17 | /hbw/unload | hbw_2 | Terminal — case truncated |
| a_16539 | WF_109_6 | /wt/pick_up_and_transport | wt_1 | Non-terminal — workflow continued |
| a_17498 | WF_1107_7 | /wt/pick_up_and_transport | wt_1 | Non-terminal — workflow continued |

**Failure modeling guidance:**
- Most failures are terminal (entity removed from workflow).
- WF_104_8 shows a retry pattern: 2 failed wt_1 transports followed by a successful retry. Model as retry-on-same-resource with delay.
- WF_109_6 and WF_1107_7 had wt_1 failures but the workflow continued (subsequent entities succeeded). These may represent transient errors absorbed by the system.

### 4.2 Truncated Cases

| Case | Steps Observed | Expected | Cause |
|---|---|---|---|
| WF_102_17 | 1 | 10–14 | Failure at first step (hbw/unload) |
| WF_104_9 | 1 | 14–19 | Failure at first step (hbw/unload) |
| WF_104_7 | 4 | 14–19 | Stopped after ov/burn (data truncation) |
| WF_103_14 | 5 | 13 | Stopped after ov/burn (data truncation) |
| WF_1106_9 | 8 | 10–14 | Stopped after dm/cylindrical_drill (data truncation) |

### 4.3 Conditional Storage Tail

A **storage tail** appears at the end of some completed workflows:
```
/hbw/get_empty_bucket @ hbw_1 → /vgr/pick_up_and_transport @ vgr_1 → /vgr/pick_up_and_transport @ vgr_1 → /hbw/store @ hbw_1
```

This tail is present in ~60% of completed cases across WF_101, WF_102, WF_104, WF_105, WF_108, WF_1106, WF_1107. It is absent in WF_103 and WF_109 (which always end at hw/human_review).

**Modeling guidance:** Treat as optional post-processing step. The storage tail always uses hbw_1 (not hbw_2) and involves 2 vgr_1 transport events.

### 4.4 Dual-Lane Routing (WF_104)

WF_104 is the only workflow that uses **both lanes**: it starts on Lane 2 (ov_2 → wt_2 → mm_2 → sm_2) then transitions to Lane 1 (vgr_1 → wt_1 → mm_1 → sm_1 → pm_1). The transition is mediated by vgr transports (vgr_2 → vgr_1).

### 4.5 Non-Deterministic Routing

Two workflows exhibit non-deterministic step selection:

1. **WF_1106 Step 6:** The mm_2 operation varies between `/mm/deburr`, `/mm/mill`, and `/mm/transport_from_to`. This may reflect workpiece-specific requirements.

2. **WF_1107 Steps 7 & 9:** The mm_1 operation varies (`/mm/transport_from_to` vs `/mm/mill`) and the pm_1 operation varies (`/pm/punch_ribbing` vs `/pm/punch_recesses`). These two variants may be correlated (ribbing with transport_from_to, recesses with mill).

---

## 5. Resource Pooling Notes

### 5.1 Pool Assignment by Lane

The system exhibits **lane-based resource assignment** rather than true dynamic pooling:

| Lane | Resources | Workflows |
|---|---|---|
| Lane 1 (mm_1) | ov_1, wt_1, mm_1, sm_1, vgr_1 | WF_101, WF_103, WF_105, WF_109, WF_1107 |
| Lane 2 (mm_2) | ov_2, wt_2, mm_2, sm_2, vgr_2 | WF_102, WF_108, WF_1106 |
| Shared | hbw_1, hbw_2, pm_1, dm_2, hw_1 | All workflows |

Within a lane, resources are dedicated (e.g., WF_101 always uses ov_1, wt_1, mm_1, sm_1). Cross-lane pooling is limited to WF_104 (dual-lane) and the shared resources.

### 5.2 Simulation Modeling Recommendations

1. **Model each resource class as a pool** of capacity 2 (or 1 for dedicated resources), but constrain routing to lane-specific resources per workflow type.
2. **vgr_1 and vgr_2** are the most heavily loaded resources (85 and 42 operations respectively). They serve as the primary interconnect between all stations.
3. **hbw_2** is the universal entry point (all workflows start with `/hbw/unload @ hbw_2`).
4. **hw_1** is the universal exit point (all completed workflows end with `/hw/human_review @ hw_1`).
5. **pm_1** is a potential bottleneck — it serves 3 different punching operations across 4 workflow types with no parallel instance.

---

## 6. Topology Diagram (Textual)

```
                    ┌─────────────────────────────────────────────────────┐
                    │                    ENTRY POINT                       │
                    │              hbw_2: /hbw/unload                      │
                    └──────────────────────┬──────────────────────────────┘
                                           │
                                    vgr_2: transport
                                           │
                                    hbw_2: store_empty_bucket
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                             │
            ┌───────▼──────┐                             ┌───────▼──────┐
            │   LANE 1     │                             │   LANE 2     │
            │              │                             │              │
            │  vgr_1       │                             │  ov_2        │
            │  ov_1        │                             │  wt_2        │
            │  ov_1(temper)│                             │  mm_2        │
            │  wt_1        │                             │  sm_2        │
            │  mm_1        │                             │              │
            │  sm_1        │                             │  dm_2        │
            │  pm_1        │                             │              │
            │              │                             │              │
            └───────┬──────┘                             └───────┬──────┘
                    │                                             │
                    └──────────────────────┬──────────────────────┘
                                           │
                                    vgr_1: transport
                                           │
                                    hw_1: human_review
                                           │
                              ┌────────────▼─────────────┐
                              │   OPTIONAL STORAGE TAIL  │
                              │                          │
                              │  hbw_1: get_empty_bucket │
                              │  vgr_1: transport ×2     │
                              │  hbw_1: store            │
                              └──────────────────────────┘
```

---

*Report generated from `eventlog_cleaned.parquet` (1,383 events, 461 entities, 38 cases, 9 workflow types).*
