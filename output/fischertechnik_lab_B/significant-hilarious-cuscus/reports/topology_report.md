# Topology Report — fischertechnik_lab_B (significant-hilarious-cuscus)

## 1. Scope & Data Basis

- **Source**: `work_files/eventlog_cleaned.parquet` (1,383 rows × 12 cols; lifecycle layout, 3 rows per instance).
- **Volume**: 461 activity instances, 38 cases (workpieces), 20 activities, 15 resources, 9 process-model variants.
- **Window**: t0 = 2021-06-30T15:24:34Z, horizon ≈ 5,943.7 s (~99 min).
- **Outcomes**: 452 success, 9 failure (real factory behavior, retained).

## 2. Censoring & Case Classification (detect_censoring)

| Category | Count | Cases |
|---|---|---|
| Complete (end with `/hbw/store`) | 14 | WF_101_14, WF_101_18, WF_102_15, WF_102_18, WF_104_11, WF_104_8, WF_105_8, WF_105_9, WF_108_7, WF_108_9, WF_1106_7, WF_1106_8, WF_1107_6, WF_1107_7 |
| Right-censored (cut at window end) | 0 | — |
| Left-censored / initial WIP | 0 | — |
| Incomplete interior (early exit) | 24 | see §7 |

- No case overlaps the window edges (edge_tol 72.2 s); **no window truncation** — all 24 incomplete cases are genuine mid-process stops (early exits / scrap / abandonment), not truncation.
- Initial WIP at window start = 0 → simulation starts empty.
- **Excluded as truncation artifacts** (terminate immediately after a failure, no recovery): **WF_102_16** (ends in failed `/vgr/pick_up_and_transport`), **WF_102_17** (single failed `/hbw/unload`), **WF_104_9** (single failed `/hbw/unload`). Per project decision, only these are excluded; all other failed steps are real retry behavior.
- Estimation basis: main sequences & step presence from **complete cases**; early-exit statistics from non-excluded cases; variant mix from all 38 released cases.

## 3. Resources (15, all capacity 1 — verified, max concurrent service per resource = 1)

| Resource | Class | Capacity | Instances | Role |
|---|---|---|---|---|
| hbw_1 | hbw | 1 | 30 | warehouse: get_empty_bucket, store |
| hbw_2 | hbw | 1 | 74 | warehouse: unload, store_empty_bucket |
| vgr_1 | vgr | 1 | 85 | vertical gripper (in-process transport) |
| vgr_2 | vgr | 1 | 42 | vertical gripper (initial pick-up) |
| wt_1 | wt | 1 | 27 | workpiece transport |
| wt_2 | wt | 1 | 14 | workpiece transport |
| mm_1 | mm | 1 | 37 | milling (mill, deburr, transport_from_to) |
| mm_2 | mm | 1 | 17 | milling (mill, drill, deburr) |
| ov_1 | ov | 1 | 35 | oven (burn, temper) |
| ov_2 | ov | 1 | 12 | oven (burn) |
| sm_1 | sm | 1 | 23 | sorting/transport |
| sm_2 | sm | 1 | 14 | sorting/transport |
| pm_1 | pm | 1 | 13 | press (punch_gill, punch_recesses, punch_ribbing) |
| dm_2 | dm | 1 | 8 | deep milling (lower, cylindrical_drill) |
| hw_1 | hw | 1 | 30 | human review workstation |

## 4. Variant Routing (9 variants; all observed sub-types captured)

Variant mix (share of 38 released cases): WF_101 0.158, WF_102 0.132, WF_103 0.132, WF_104 0.132, WF_105 0.105, WF_108 0.079, WF_109 0.105, WF_1106 0.105, WF_1107 0.053.

All variants share the skeleton: `/hbw/unload` (hbw_2) → `/vgr/pick_up_and_transport` (vgr_2) → [optional `/hbw/store_empty_bucket` (hbw_2)] → process steps → `/hw/human_review` (hw_1) → [optional `/hbw/get_empty_bucket` (hbw_1) → `/vgr/pick_up_and_transport` (vgr_1) → `/hbw/store` (hbw_1)].

| Variant | n cases | completed | Main sequence (complete cases) | Early exit P | Early-exit points |
|---|---|---|---|---|---|
| WF_101 | 6 | 2 | U → V2 → SEB → V1 → B(ov_1) → T(ov_1) → W1 → M1 → D1 → SO1 → V1 → H → GEB → V1 → V1 → S | 0.667 | after H (0.75), after V1 (0.25) |
| WF_102 | 5 | 2 | U → V2 → SEB → B(ov_2) → W2 → DR2 → ST2 → L2 → V1 → H → V1 → GEB → V1 → S | 0.333 | after H (1.0, of non-excluded) |
| WF_103 | 5 | 0 | U → V2 → SEB → V1 → B(ov_1) → T(ov_1) → W1 → M1 → D1 → ST1 → PR1 → V1 → H (partial, no complete case) | 1.0 | after B (0.2), after H (0.8) |
| WF_104 | 5 | 2 | U → V2 → SEB → B(ov_2) → W2 → M2 → SO2 → V2 → V1 → W1 → D1 → ST1 → PG1 → V1 → H → V1 → GEB → V1 → S | 0.5 | after B (0.5), after H (0.5) |
| WF_105 | 4 | 2 | U → V2 → SEB → V1 → B(ov_1) → W1 → D1 → SO1 → V1 → H → V1 → GEB → V1 → S | 0.5 | after SO1 (1.0) |
| WF_108 | 3 | 2 | U → V2 → SEB → B(ov_2) → W2 → DR2 → D2 → SO2 → V2 → V1 → H → GEB → V1 → V1 → S | 0.333 | after H (1.0) |
| WF_109 | 4 | 0 | U → V2 → SEB → V1 → B(ov_1) → T(ov_1) → W1 → M1 → D1 → ST1 → PB1 → V1 → H (partial, no complete case) | 1.0 | after H (1.0) |
| WF_1106 | 4 | 2 | U → V2 → SEB → B(ov_2) → W2 → M2/MT2 → ST2 → CD2 → V1 → H → GEB → V1 → V1 → S | 0.5 | after H (0.5), after CD2 (0.5) |
| WF_1107 | 2 | 2 | U → V2 → SEB → V1 → B(ov_1) → W1 → MT1/PB1 → ST1 → PB1/PR1 → V1 → H → GEB → V1 → V1 → S | 0.0 | — |

(U=unload, V=vgr/pick_up_and_transport, SEB=store_empty_bucket, GEB=get_empty_bucket, S=store, B=burn, T=temper, W=wt/pick_up_and_transport, M=mill, D=deburr, DR=drill, MT=mm/transport_from_to, SO=sort, ST=sm/transport, PR=punch_recesses, PB=punch_ribbing, PG=punch_gill, L=dm/lower, CD=dm/cylindrical_drill, H=human_review; suffix = resource index.)

**Non-canonical sub-sequences captured** (per decision: capture ALL observed variants):
- **WF_102**: WF_102_14 (early exit after H) ran without `/ov/burn` and with an extra `/hbw/store_empty_bucket` on **hbw_1** (concurrent with vgr_1 transport) before human review — captured as `other_sequences` (p=0.333 over non-excluded cases).
- **WF_108**: WF_108_8 (early exit after H) ran without `/ov/burn` — captured as `other_sequences` (p=0.333).
- **WF_1106**: WF_1106_8 used `/mm/transport_from_to` (mm_2) instead of `/mm/mill` — captured as `other_sequences` (p=0.5).
- **WF_1107**: WF_1107_7 used `/mm/mill` + `/pm/punch_recesses` instead of `/mm/transport_from_to` + `/pm/punch_ribbing` — captured as `other_sequences` (p=0.5).

**Storage steps** (`store_empty_bucket` at start; `get_empty_bucket` → `store` at end): conditional/optional but present in **all complete cases** of their variants — captured in the canonical sequence; the absence in incomplete cases is truncation bias, not optionality (step_presence_complete_cases = 1.0).

## 5. Queue Disciplines (test_dispatching_rules, 87 decision points)

| Class | n decisions | FIFO | LIFO | case_age | activity_priority | Best | FIFO rejected? |
|---|---|---|---|---|---|---|---|
| hbw | 66 | 0.50 | 0.50 | **0.985** | 0.97 | case_age | **yes** |
| vgr | 21 | **1.00** | 0.00 | 0.476 | 1.00 | FIFO | no |
| all others | — | — | — | — | — | — | no contention at all (100% extraneous waiting) |

- **hbw**: NOT FIFO. Learned activity priority: `/hbw/store` > `/hbw/get_empty_bucket` > `/hbw/store_empty_bucket` > `/hbw/unload`. Dominant overtaking: `store_empty_bucket` chosen over waiting `unload` (110 overtakes). → Model with `simpy.PriorityResource`.
- **vgr**: FIFO consistent (100%).
- All other classes (dm, hw, mm, ov, pm, sm, wt): zero contention waiting — effectively no queue; FIFO.

## 6. Waiting-Time Causes (decompose_waiting_times, 461 steps)

Overall mean wait 41.0 s (p90 66.6 s); shares: contention 29.5%, prioritization 22.6%, extraneous 47.9%.

- **hbw** (104 steps, mean 144.8 s, p90 525.3 s): 28.3% of waiting is overtaking by later-enabled steps → confirms non-FIFO priority queue; `/hbw/unload` alone has mean wait 385.6 s (p90 700 s) because it has the lowest priority.
- **vgr** (127 steps, mean 23.0 s): 49.5% contention (FIFO queueing), 50.5% extraneous (hand-off/transport delay).
- **ov, wt, mm, sm, pm, dm, hw**: 100% extraneous — waiting happens while the resource is idle (hand-off/release delay, not resource capacity).

## 7. Early Exits (24 interior incomplete cases — real scrap/abandonment, not truncation)

| Variant | Exits | After (success) | After (failure) |
|---|---|---|---|
| WF_101 | 4 | /hw/human_review ×3, /vgr/pick_up_and_transport ×1 | — |
| WF_102 | 2 (of 5; 2 excluded) | /hw/human_review ×1 | /vgr/pick_up_and_transport ×1 (WF_102_16, excluded), /hbw/unload ×1 (WF_102_17, excluded) |
| WF_103 | 5 | /ov/burn ×1, /hw/human_review ×4 | — |
| WF_104 | 3 (of 5; 1 excluded) | /ov/burn ×1, /hw/human_review ×1 | /hbw/unload ×1 (WF_104_9, excluded) |
| WF_105 | 2 | /sm/sort ×2 | — |
| WF_108 | 1 | /hw/human_review ×1 | — |
| WF_109 | 4 | /hw/human_review ×4 | — |
| WF_1106 | 2 | /hw/human_review ×1, /dm/cylindrical_drill ×1 | — |
| WF_1107 | 0 | — | — |

Most exits occur at/after `/hw/human_review` (workpiece rejected at inspection) — consistent with scrap at the quality gate.

## 8. Release Control (detect_release_control, 38 releases)

- **Verdict: open (bursty releases)** — no WIP cap (WIP at release: mean 5.0, max 8, no ceiling pattern) and no completion trigger (within-5s lift 0.86 < 1; within-30s lift 1.39, weak).
- Max WIP 9, time-averaged WIP 5.91 (15.2% of time at max).
- **Two-regime arrival process**: 14 bursts (mean size 2.7, up to 9) spaced by burst IAT (mean 2.44 s, median 1.44 s), separated by gaps (mean 394.7 s, median 294.1 s; gap:burst IAT ratio 161.5). Model with a gap process + burst size — never the mixed mean IAT (140.3 s, cv 2.0).

## 9. Intra-Case Concurrency (detect_intra_case_concurrency)

0.974 overlapping steps per case; 68.4% of cases have overlap; 1.571 per completed case → **the process is not a strictly sequential chain**. Material overlapping (previous → next) pairs, physically plausible (transporter fetched / bucket handled while machine still works):

| Pair | n | mean overlap |
|---|---|---|
| /hbw/store_empty_bucket → /ov/burn | 12 | 34.5 s |
| /hbw/store_empty_bucket → /vgr/pick_up_and_transport | 11 | 25.3 s |
| /hbw/get_empty_bucket → /vgr/pick_up_and_transport | 6 | 31.4 s |
| /vgr/pick_up_and_transport → /hbw/get_empty_bucket | 5 | 20.7 s |
| /hbw/store_empty_bucket → /wt/pick_up_and_transport | 3 | 21.7 s |

Modeled via `concurrent_with_previous: true` flags per variant step (e.g. burn starts while store_empty_bucket still runs; vgr fetch starts while get_empty_bucket still runs).

## 10. Failure / Rework Behavior (9 failed instances)

- **Retries on same resource (model as retry-on-same-resource with delay)**: `/wt/pick_up_and_transport` on wt_1 in WF_104_8 (2 consecutive failures → success), WF_109_6, WF_1107_7; `/hbw/store_empty_bucket` on hbw_2 in WF_102_15 and WF_104_8 (failed, case continued — no retry instance, treated as a transient fault absorbed by the process).
- **Terminal failures (truncation artifacts, excluded)**: WF_102_16 (vgr), WF_102_17 (hbw unload), WF_104_9 (hbw unload) — no subsequent activity for the case.

## 11. Control-Logic Summary (written to spec `control_policies`)

- `queue_discipline`: hbw = **priority** (order: store > get_empty_bucket > store_empty_bucket > unload); vgr = fifo; all others fifo (no contention).
- `release_rule`: open (bursty releases) — two-regime burst/gap arrival process.
- `intra_case_concurrency`: the five pairs above.
- `evidence`: hbw FIFO agreement 0.50 (case_age 0.985, activity_priority 0.97 over 66 decisions); vgr FIFO 1.00 (21 decisions); 1.571 overlapping steps per completed case (68.4% of cases).

## 12. Spec Corrections Made During Verification

1. **WF_102 main_sequence** corrected: `/hbw/store_empty_bucket` (hbw_2) is present in **all** WF_102 cases (including both complete cases) — it was missing from the previous main sequence; added as step 3 with `/ov/burn` concurrent.
2. **WF_102 / WF_104 early-exit statistics** recomputed excluding the 3 failure-terminated truncation artifacts (WF_102_16, WF_102_17, WF_104_9) per project decision; their "early exit after step 0 / unload-failure" entries were truncation, not real exits.
3. **WF_102 / WF_108 `other_sequences`** added (non-canonical sub-types: no-burn routing with extra hbw_1 store_empty_bucket; no-burn routing).
4. **`concurrent_with_previous` flags** corrected from raw overlap check: WF_102 `get_empty_bucket`→`vgr` = false (no overlap observed); WF_104 `get_empty_bucket`→`vgr` = false; WF_108 `get_empty_bucket`→`vgr` = true (6.5 s overlap); WF_101 `get_empty_bucket` = false and WF_1106 `get_empty_bucket` = false (the observed overlap is with the *following* vgr step, not the preceding one); WF_1106 `other_sequences` resource for `/mm/transport_from_to` corrected to mm_2 (observed on mm_2, not mm_1).
5. **`initial_state.excluded_from_estimation`** populated with the 3 truncation-artifact case ids (exclusion list only — not used as model inputs).
6. **`assumptions`** section written (10 entries) recording all modelling decisions and their evidence.
7. **`control_policies.evidence`** completed with case_age/activity_priority agreement rates and overlap statistics.

## 13. Open Questions

See QUESTIONS FOR USER in the final message.
