# Topology Report — Fischertechnik Lab C Manufacturing System

## 1. Dataset Characteristics

| Property | Value |
|---|---|
| Source file | `eventlog.parquet` (raw), `eventlog_cleaned.parquet` (cleaned) |
| Total rows (raw) | 1,137 (379 operations × 3 lifecycle transitions) |
| Total rows (cleaned) | 1,137 |
| Unique operations (event_id) | 379 |
| Unique cases (workpieces) | 37 |
| Unique process models | 9 (WF_101–WF_1107) |
| Unique activities (concept:name) | 21 |
| Unique resources (org:resource) | 15 |
| Time span | 2021-07-01 (single simulated day) |
| Lifecycle transitions | scheduled → start → complete |
| Failure events | 5 (out of 379 operations) |

## 2. Resource Classes & Entities

### 2.1 Resource Class Table

| Resource Class | Prefix | Entities | Count | Location | Pooling |
|---|---|---|---|---|---|
| High Bay Warehouse | `hbw` | hbw_1, hbw_2 | 2 | hbw_1: Shop Floor 1; hbw_2: Shop Floor 2 | Separate instances (not pooled) |
| Vacuum Gripper | `vgr` | vgr_1, vgr_2 | 2 | vgr_1: Shop Floor 1; vgr_2: Shop Floor 2 | Separate instances (not pooled) |
| Oven | `ov` | ov_1, ov_2 | 2 | ov_1: Track 1; ov_2: Track 2 | Parallel capacity pools |
| Milling Machine | `mm` | mm_1, mm_2 | 2 | mm_1: Track 1; mm_2: Track 2 | Parallel capacity pools |
| Sorting Machine | `sm` | sm_1, sm_2 | 2 | sm_1: Track 1; sm_2: Track 2 | Parallel capacity pools |
| Wheel Transporter | `wt` | wt_1, wt_2 | 2 | wt_1: Track 1; wt_2: Track 2 | Parallel capacity pools |
| Human Workstation | `hw` | hw_1 | 1 | Shop Floor 1 | Single instance |
| Punch Machine | `pm` | pm_1 | 1 | Shop Floor 1 | Single instance |
| Drill Machine | `dm` | dm_2 | 1 | Shop Floor 2 | Single instance |

### 2.2 Resource Pooling Architecture

The system has **two parallel production tracks** (Shop Floor 1 and Shop Floor 2), linked by workpiece exchange via vacuum grippers:

**Track 1 (Shop Floor 1):** ov_1 → mm_1 → wt_1 → sm_1
**Track 2 (Shop Floor 2):** ov_2 → mm_2 → wt_2 → sm_2

**Shared/Cross-Track Resources:**
- `hbw_1` and `hbw_2`: Separate warehouses per floor (not pooled)
- `vgr_1` and `vgr_2`: Separate grippers per floor (not pooled)
- `hw_1`: Single human workstation (Shop Floor 1) — bottleneck for all variants requiring review
- `pm_1`: Single punch machine (Shop Floor 1) — bottleneck for all variants requiring punching
- `dm_2`: Single drill machine (Shop Floor 2) — bottleneck for all variants requiring drilling

**Key pooling insight:** The two tracks operate as independent capacity pools for ov/mm/wt/sm. However, pm_1, hw_1, and dm_2 are single-instance resources that create cross-track contention. Workpiece exchange between tracks occurs via vgr_1/vgr_2 transport operations.

## 3. Product Variants & Routing Sequences

### 3.1 Process Model Summary

| Process Model | Track | Cases | Avg Steps | Key Activities | Human Review | Terminal Activity |
|---|---|---|---|---|---|---|
| WF_101 | Track 1 | 4 | 16 | burn+temper → mill+deburr → sort | Yes | store |
| WF_102 | Track 2 | 5 | 10 | burn → drill → transport → lower | Conditional | store / in-progress |
| WF_103 | Track 1 | 5 | 14 | burn+temper → mill+deburr → transport → punch_recesses | Conditional | store / in-progress |
| WF_104 | Cross-track | 3 | 15 | burn → mill/sort → deburr → punch_gill | Yes | in-progress (rework) |
| WF_105 | Track 1 | 4 | 11 | burn → deburr → sort | Conditional | store / in-progress |
| WF_108 | Track 2 | 3 | 10 | burn → drill+deburr → sort | Conditional | store / in-progress |
| WF_109 | Track 1 | 3 | 14 | burn+temper → mill+deburr → transport → punch_ribbing | Conditional | store / in-progress |
| WF_1106 | Track 2 | 6 | 9 | burn → variable_mm → transport → drill | Conditional | store / in-progress |
| WF_1107 | Track 1 | 4 | 9 | burn → transport → punch_gill | Conditional | store / in-progress |

### 3.2 Detailed Routing Per Process Model

#### WF_101 (Track 1 — Full Process with Temper)
```
hbw_2(unload) → vgr_2(transport) → hbw_2(store_empty_bucket) → vgr_1(transport)
→ ov_1(burn) → ov_1(temper) → wt_1(transport) → mm_1(mill) → mm_1(deburr)
→ sm_1(sort) → vgr_1(transport) → hw_1(human_review) → hbw_1(get_empty_bucket)
→ vgr_1(transport) → vgr_1(transport) → hbw_1(store)
```
- **Confidence:** High — consistent across 2 complete cases
- **Truncated cases:** WF_101_26, WF_101_28 (1 step each, failure at hbw_2/unload)

#### WF_102 (Track 2 — Drill & Lower)
```
hbw_2(unload) → [vgr_2(transport)] → hbw_2(store_empty_bucket) → ov_2(burn)
→ wt_2(transport) → mm_2(drill) → sm_2(transport) → dm_2(lower)
→ [vgr_1(transport) → hw_1(human_review) → hbw_1(get_empty_bucket)
→ vgr_1(transport) → vgr_1(transport) → hbw_1(store)]
```
- **Confidence:** High — core routing consistent; human review is conditional
- **Variability:** vgr_2 transport sometimes omitted; human review present in ~60% of cases

#### WF_103 (Track 1 — Punch Recesses)
```
hbw_2(unload) → vgr_2(transport) → hbw_2(store_empty_bucket) → vgr_1(transport)
→ ov_1(burn) → ov_1(temper) → [wt_1(transport)] → mm_1(mill) → mm_1(deburr)
→ sm_1(transport) → pm_1(punch_recesses) → vgr_1(transport) → hw_1(human_review)
→ [hbw_1(get_empty_bucket) → vgr_1(transport) → vgr_1(transport) → hbw_1(store)]
```
- **Confidence:** High — core routing consistent
- **Variability:** wt_1 transport sometimes omitted; human review and storage conditional
- **Truncated cases:** WF_103_27 (failure at vgr_1), WF_103_28 (success but incomplete)

#### WF_104 (Cross-Track — Rework Loop)
```
Phase 1 (Track 2):
hbw_2(unload) → vgr_2(transport) → hbw_2(store_empty_bucket) → ov_2(burn)
→ wt_2(transport) → [mm_2(mill)] → sm_2(sort) → vgr_2(transport) → vgr_1(transport)

Phase 2 (Track 1):
→ wt_1(transport) → mm_1(deburr) → sm_1(transport) → pm_1(punch_gill)
→ vgr_1(transport) → hw_1(human_review)

Rework Loop (if review fails):
→ vgr_2(transport) → hbw_2(store_empty_bucket) → ov_2(burn) → wt_2(transport)
→ mm_2(mill) → sm_2(sort) → vgr_2(transport) → vgr_1(transport)
→ [repeat Phase 2]
```
- **Confidence:** High — rework loop confirmed in WF_104_18 (23 steps, two full cycles)
- **Special condition:** Quality rework loop — failed human review triggers reprocessing through Track 2
- **Cross-track:** Only process model that uses both tracks in a single case
- **Truncated case:** WF_104_19 (6 steps, incomplete at sm_2/sort)

#### WF_105 (Track 1 — Simple Deburr)
```
hbw_2(unload) → vgr_2(transport) → hbw_2(store_empty_bucket) → vgr_1(transport)
→ ov_1(burn) → wt_1(transport) → mm_1(deburr) → sm_1(sort)
→ [vgr_1(transport) → hw_1(human_review) → vgr_1(transport)
→ hbw_1(get_empty_bucket) → vgr_1(transport) → hbw_1(store)]
```
- **Confidence:** High — core routing consistent
- **Variability:** Human review and storage conditional (~50% of cases)

#### WF_108 (Track 2 — Drill & Deburr)
```
hbw_2(unload) → [vgr_2(transport)] → hbw_2(store_empty_bucket) → ov_2(burn)
→ wt_2(transport) → mm_2(drill) → mm_2(deburr) → sm_2(sort)
→ [vgr_2(transport) → vgr_1(transport) → hw_1(human_review)
→ vgr_1(transport) → hbw_1(get_empty_bucket) → vgr_1(transport) → hbw_1(store)]
```
- **Confidence:** High — core routing consistent
- **Variability:** vgr_2 transport sometimes omitted; human review conditional (~33% of cases)

#### WF_109 (Track 1 — Punch Ribbing)
```
hbw_2(unload) → vgr_2(transport) → hbw_2(store_empty_bucket) → vgr_1(transport)
→ ov_1(burn) → ov_1(temper) → wt_1(transport) → mm_1(mill) → mm_1(deburr)
→ sm_1(transport) → pm_1(punch_ribbing) → vgr_1(transport) → hw_1(human_review)
→ [hbw_1(get_empty_bucket) → vgr_1(transport) → vgr_1(transport) → hbw_1(store)]
```
- **Confidence:** High — core routing consistent
- **Truncated case:** WF_109_13 (8 steps, incomplete at mm_1/deburr)

#### WF_1106 (Track 2 — Variable Milling & Drilling)
```
hbw_2(unload) → vgr_2(transport) → hbw_2(store_empty_bucket) → ov_2(burn)
→ [wt_2(transport)] → mm_2({deburr|drill|mill|transport_from_to})
→ sm_2(transport) → dm_2({drill|cylindrical_drill})
→ [vgr_1(transport) → hw_1(human_review) → vgr_1(transport)
→ hbw_1(get_empty_bucket) → vgr_1(transport) → hbw_1(store)]
```
- **Confidence:** Medium — single process model with conditional routing
- **Variability:** High — mm_2 activity varies (deburr, drill, mill, transport_from_to); dm_2 activity varies (drill, cylindrical_drill); wt_2 transport sometimes omitted
- **Routing variability table:**

| Case | mm_2 activity | dm_2 activity | wt_2 present | human_review |
|---|---|---|---|---|
| WF_1106_15 | deburr | cylindrical_drill | No | No |
| WF_1106_16 | transport_from_to | drill | Yes | Yes |
| WF_1106_17 | transport_from_to | drill | Yes | No |
| WF_1106_18 | drill | cylindrical_drill | Yes | No |
| WF_1106_19 | mill | drill | No | No |
| WF_1106_20 | deburr | drill | Yes | No |

#### WF_1107 (Track 1 — Punch Gill)
```
hbw_2(unload) → vgr_2(transport) → hbw_2(store_empty_bucket) → vgr_1(transport)
→ ov_1(burn) → [wt_1(transport)] → sm_1(transport) → pm_1(punch_gill)
→ [vgr_1(transport) → hw_1(human_review) → hbw_1(get_empty_bucket)
→ vgr_1(transport) → vgr_1(transport) → hbw_1(store)]
```
- **Confidence:** High — core routing consistent
- **Variability:** wt_1 transport sometimes omitted; mm_1 activity varies (transport_from_to vs absent); human review conditional
- **Truncated cases:** WF_1107_13 (failure at vgr_1), WF_1107_15 (1 step, success at hbw_2/unload)

### 3.3 Non-Deterministic Routing Summary

| Process Model | Non-Deterministic Elements |
|---|---|
| WF_102 | Optional vgr_2 transport; conditional human review + storage |
| WF_103 | Optional wt_1 transport; conditional human review + storage |
| WF_104 | Rework loop (conditional on human review outcome); optional mm_2/mill |
| WF_105 | Conditional human review + storage |
| WF_108 | Optional vgr_2 transport; conditional human review + storage |
| WF_109 | Conditional human review + storage |
| WF_1106 | Variable mm_2 activity (4 types); variable dm_2 activity (2 types); optional wt_2; conditional human review |
| WF_1107 | Optional wt_1 transport; variable mm_1 activity; conditional human review |

## 4. Special Conditions

### 4.1 Quality Rework Loop (WF_104)
- **Confidence:** High
- **Mechanism:** After human review at hw_1, failed cases are routed back through Track 2 (ov_2 → mm_2 → sm_2) for reprocessing, then return to Track 1 for deburr → punch_gill → human review
- **Evidence:** WF_104_18 shows 23 steps with two complete processing cycles
- **DES implication:** Implement a feedback loop from hw_1 back to ov_2 for WF_104 cases

### 4.2 Failure Events (5 total)
- **Confidence:** High
- **Cases with failures:**
  - WF_101_26: Failure at hbw_2/unload (scrap at entry)
  - WF_101_28: Failure at hbw_2/unload (scrap at entry)
  - WF_103_27: Failure at vgr_1/pick_up_and_transport (transport failure)
  - WF_104_17: Failure at vgr_1/pick_up_and_transport (transport failure after human review)
  - WF_1107_13: Failure at vgr_1/pick_up_and_transport (transport failure)
- **DES implication:** Model failure rates per activity; failed cases terminate (scrap)

### 4.3 Truncated/Incomplete Cases
- **Confidence:** High
- **Cases ending on non-terminal activity with no complete/failure (missing data):**
  - WF_101_26, WF_101_28: 1 step each (failure at hbw_2/unload — real scrap)
  - WF_103_28: 4 steps (success at vgr_1, but no further events — missing data)
  - WF_104_19: 6 steps (ends at sm_2/sort — missing data)
  - WF_105_18, WF_105_20: 8 steps each (ends at sm_1/sort — missing data)
  - WF_108_14, WF_108_15: 7-9 steps (ends at sm_2/sort or vgr_2 — missing data)
  - WF_109_13: 8 steps (ends at mm_1/deburr — missing data)
  - WF_1106_15, WF_1106_17, WF_1106_18, WF_1106_19, WF_1106_20: 7-8 steps (ends at dm_2 — missing data)
  - WF_1107_12, WF_1107_15: 1-8 steps (missing data)
- **DES implication:** Distinguish real scrap (failure state) from missing data (success state but incomplete sequence)

### 4.4 Conditional Human Review
- **Confidence:** High
- **Mechanism:** Human review at hw_1 is conditional — present in some cases but not others within the same process model
- **Process models with conditional review:** WF_102, WF_103, WF_105, WF_108, WF_109, WF_1106, WF_1107
- **Process models with mandatory review:** WF_101, WF_104
- **DES implication:** Model human review as a conditional gate (probability-based or rule-based)

### 4.5 Batch Processing Indicators
- **Confidence:** Medium
- **Evidence:** Parameters contain `parameter_quantity` for dm and pm operations:
  - dm/cylindrical_drill: quantity=8
  - dm/drill: quantity=6
  - mm/drill: quantity=4
  - pm/punch_gill: quantity=8
  - pm/punch_recesses: quantity=6
  - pm/punch_ribbing: quantity=6
- **DES implication:** These may represent batch sizes; processing times should be validated against batch quantities

### 4.6 Workpiece Size Variability
- **Confidence:** High
- **Evidence:** ov/burn parameters contain `parameter_burn_workpiece_size` and `parameter_burn_workpiece_thickness`:
  - Sizes: regular, middle, large, maxi
  - Thickness: thin (all observed cases)
- **DES implication:** Workpiece size may affect processing times; consider size-dependent processing time distributions

## 5. Resource-Activity Mapping

### 5.1 Activities Per Resource

| Resource | Activities | Process Models |
|---|---|---|
| hbw_1 | get_empty_bucket, store | All (storage phase) |
| hbw_2 | unload, store_empty_bucket | All (entry phase) |
| vgr_1 | pick_up_and_transport | All (Track 1 transport + cross-track) |
| vgr_2 | pick_up_and_transport | All (Track 2 transport + cross-track) |
| ov_1 | burn, temper | WF_101, WF_103, WF_105, WF_109, WF_1107 |
| ov_2 | burn | WF_102, WF_104, WF_108, WF_1106 |
| mm_1 | mill, deburr, transport_from_to | WF_101, WF_103, WF_104, WF_105, WF_109, WF_1107 |
| mm_2 | mill, deburr, drill, transport_from_to | WF_102, WF_104, WF_108, WF_1106 |
| sm_1 | sort, transport | WF_101, WF_103, WF_104, WF_105, WF_109, WF_1107 |
| sm_2 | sort, transport | WF_102, WF_104, WF_108, WF_1106 |
| wt_1 | pick_up_and_transport | WF_101, WF_103, WF_104, WF_105, WF_109, WF_1107 |
| wt_2 | pick_up_and_transport | WF_102, WF_104, WF_108, WF_1106 |
| hw_1 | human_review | WF_101, WF_102, WF_103, WF_104, WF_105, WF_108, WF_109, WF_1106, WF_1107 |
| pm_1 | punch_gill, punch_recesses, punch_ribbing | WF_103, WF_104, WF_109, WF_1107 |
| dm_2 | lower, drill, cylindrical_drill | WF_102, WF_1106 |

### 5.2 Resource Utilization (Operation Count)

| Resource | Operations | % of Total |
|---|---|---|
| vgr_1 | 204 | 53.8% |
| hbw_2 | 213 | 56.2% |
| vgr_2 | 108 | 28.5% |
| hbw_1 | 81 | 21.4% |
| ov_1 | 66 | 17.4% |
| mm_1 | 66 | 17.4% |
| mm_2 | 57 | 15.0% |
| ov_2 | 54 | 14.2% |
| hw_1 | 51 | 13.5% |
| sm_2 | 51 | 13.5% |
| sm_1 | 45 | 11.9% |
| wt_2 | 45 | 11.9% |
| wt_1 | 42 | 11.1% |
| dm_2 | 30 | 7.9% |
| pm_1 | 24 | 6.3% |

## 6. Topology Diagram (Text Representation)

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    SHOP FLOOR 2                          │
                    │                                                         │
  Raw Material ──►  │  hbw_2 ──► vgr_2 ──► ov_2 ──► wt_2 ──► mm_2 ──► sm_2  │
                    │                              │                    │     │
                    │                              │                    └──► dm_2
                    │                              │                         │
                    └──────────────────────────────┼─────────────────────────┘
                                                   │
                    ┌──────────────────────────────┼─────────────────────────┐
                    │                              ▼                         │
                    │                    SHOP FLOOR 1                          │
                    │                                                         │
                    │  hbw_1 ◄────────────────────────────────────────────┐   │
                    │  ▲                                                 │   │
                    │  │    vgr_1 ──► ov_1 ──► wt_1 ──► mm_1 ──► sm_1  │   │
                    │  │                              │                    │   │
                    │  │                              │                    └──► pm_1
                    │  │                              │                         │
                    │  └──────────────────────────────┼─────────────────────────┘
                    │                                 │
                    └─────────────────────────────────┼─────────────────────────┘
                                                      │
                                                   hw_1 (shared)
                                                      │
                                               [human_review]
                                                      │
                                               ┌──────┴──────┐
                                               │             │
                                            Pass        Fail (WF_104 only)
                                               │             │
                                            Store ◄──┐       │
                                               │     │       │
                                               └─────┴───────┘
                                                  (rework loop)
```

## 7. DES Simulation Implications

1. **Two parallel tracks** with independent ov/mm/wt/sm resources, but shared pm_1, hw_1, and dm_2 create cross-track contention
2. **Conditional routing** is pervasive — human review, storage, and some transport steps are optional
3. **Rework loop** in WF_104 requires feedback routing from hw_1 back to Track 2
4. **Failure handling** — 5 failure events across 379 operations (~1.3% failure rate); failures result in scrap
5. **Batch processing** — dm and pm operations may process multiple workpieces per operation
6. **Workpiece size** — 4 size categories (regular, middle, large, maxi) may affect processing times
7. **Truncated cases** — distinguish real scrap (failure state) from missing data (success state but incomplete)

## 8. Confidence Assessment

| Finding | Confidence | Rationale |
|---|---|---|
| Resource class identification | High | Clear prefix pattern (ov, mm, sm, wt, hbw, vgr, hw, pm, dm) |
| Two-track architecture | High | Consistent resource assignment per track across all process models |
| WF_104 rework loop | High | Directly observable in WF_104_18 (23 steps, two cycles) |
| Conditional human review | High | Present in some cases, absent in others within same process model |
| WF_1106 variability | Medium | Single process model with 4 different mm_2 activities; needs validation |
| Batch processing | Medium | Parameter quantities observed but need confirmation of actual batch behavior |
| Failure rates | Low | Only 5 failures in 379 operations; insufficient for statistical estimation |
| Workpiece size impact | Medium | Size parameters observed but processing time correlation not yet tested |

---

*Report generated from analysis of `eventlog_cleaned.parquet` (1,137 rows, 379 operations, 37 cases, 9 process models)*