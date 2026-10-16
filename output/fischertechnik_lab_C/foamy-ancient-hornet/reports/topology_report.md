# Topology Report — fischertechnik_lab_C (run: foamy-ancient-hornet)

## 1. System Overview

Two parallel production lines (shop floors) linked only for workpiece exchange, plus a shared infeed/outfeed bucket area. 37 cases, 379 activity instances, 9 variants, 21 activities, 15 resources, observation window 2021-07-01 18:48:23 UTC, horizon 5,461.5 s (~91 min).

## 2. Resources

| Resource | Class | Track / Role | Capacity |
|---|---|---|---|
| hbw_2 | hbw | Shared — infeed bucket station (unload, store_empty_bucket) | 1 |
| hbw_1 | hbw | Shared — outfeed bucket station (get_empty_bucket, store) | 1 |
| vgr_2 | vgr | Shared — infeed transporter | 1 |
| vgr_1 | vgr | Shared — outfeed/general transporter | 1 |
| ov_1 / ov_2 | ov | Track 1 / Track 2 — burn, temper | 1 each |
| mm_1 / mm_2 | mm | Track 1 / Track 2 — mill, deburr, drill, transport_from_to | 1 each |
| wt_1 / wt_2 | wt | Track 1 / Track 2 — pick_up_and_transport | 1 each |
| sm_1 / sm_2 | sm | Track 1 / Track 2 — sort, transport | 1 each |
| pm_1 | pm | Track 1 only — punch_gill, punch_recesses, punch_ribbing | 1 |
| hw_1 | hw | Track 1 only — human_review | 1 |
| dm_2 | dm | Track 2 only — drill, cylindrical_drill, lower | 1 |

**Track assignment (from data):** Track 1 (ov_1/mm_1/wt_1/sm_1) carries WF_101, WF_103, WF_105, WF_109, WF_1107; Track 2 (ov_2/mm_2/wt_2/sm_2) carries WF_102, WF_108, WF_1106. WF_104 uses both tracks (rework crosses the exchange). **hbw and vgr are shared, not track-specific** — every variant uses both hbw_1 and hbw_2 (hbw_2: 71 instances, hbw_1: 27) and both vgr_1 and vgr_2 (vgr_1: 68, vgr_2: 36). Decision logged in assumptions.

## 3. Variant Routing (main sequences from complete cases)

| Variant | Share (released) | Complete | Main sequence (track) | Early exit |
|---|---|---|---|---|
| WF_101 | 0.108 | 2/4 | unload → vgr → store_empty_bucket → vgr → burn → temper → wt → mill → deburr → sort → vgr → human_review → get_empty_bucket → vgr → vgr → store (T1) | 0.5 after step 0 (unload failure, scrap) |
| WF_102 | 0.135 | 2/5 | unload → vgr → store_empty_bucket → burn → wt → drill → sm/transport → dm/lower → vgr → human_review → get_empty_bucket → vgr → vgr → store (T2) | 0.6 (after steps 6/8/12) |
| WF_103 | 0.135 | 2/5 | unload → vgr → store_empty_bucket → vgr → burn → temper → wt → mill → deburr → sm/transport → **pm/punch_recesses** → vgr → human_review → get_empty_bucket → vgr → vgr → store (T1) | 0.6 (after steps 3/4/12) |
| WF_104 | 0.081 | 0/3 | 23-step sequence incl. rework loop: … human_review → vgr → store_empty_bucket → burn → wt → mill → sort → vgr → vgr → vgr (T2→T1→T2) | 1.0 (no complete case; longest partial sequence used) |
| WF_105 | 0.108 | 2/4 | unload → vgr → store_empty_bucket → vgr → burn → wt → deburr → sort → vgr → human_review → vgr → get_empty_bucket → vgr → store (T1) | 0.5 after step 8 (sort) |
| WF_108 | 0.081 | 1/3 | unload → vgr → store_empty_bucket → burn → wt → drill → deburr → sort → vgr → vgr → human_review → vgr → get_empty_bucket → vgr → store (T2) | 0.667 (after steps 7/9) |
| WF_109 | 0.081 | 2/3 | unload → vgr → store_empty_bucket → vgr → burn → temper → wt → mill → deburr → sm/transport → **pm/punch_ribbing** → vgr → human_review → get_empty_bucket → vgr → vgr → store (T1) | 0.333 after step 8 (deburr) |
| WF_1106 | 0.162 | 1/6 | unload → vgr → store_empty_bucket → burn → wt → mm/transport_from_to → sm/transport → **drill (60%) / cylindrical_drill (40%)** → vgr → human_review → vgr → get_empty_bucket → vgr → store (T2) | 0.833 (after steps 7/8) |
| WF_1107 | 0.108 | 1/4 | unload → vgr → store_empty_bucket → vgr → burn → mm/transport_from_to → sm/transport → **pm/punch_gill** → vgr → human_review → get_empty_bucket → vgr → vgr → store (T1) | 0.75 (after steps 1/3/8) |

Common skeleton: `hbw_2/unload → vgr → hbw_2/store_empty_bucket → [track processing] → vgr → hw_1/human_review → hbw_1/get_empty_bucket → vgr → hbw_1/store`. Differences are the track-1 vs track-2 machine block and the punch/drill/sort variant-specific steps.

**Special structures (confirmed decisions, Phase 2 follow-up):**
- **WF_104 rework loop**: probabilistic branch after `/hw/human_review`. On failure the case repeats the rework cycle (steps 15–23: vgr → store_empty_bucket → burn → wt → mill → sort → vgr → vgr → vgr) **until pass, capped at 3 rework iterations** to avoid infinite loops. The cap of 3 is a modeling choice (not data-derived); the pass/fail probability is not estimable from the 3 observed WF_104 cases and must be set in a later calibration phase.
- **WF_1106 drill choice**: probabilistic branch **60/40** (`/dm/drill` vs `/dm/cylindrical_drill`) within the single WF_1106 process model, encoded as two mutually exclusive steps at the same sequence position (step 8).
- **Early exits**: treated as **real scrap/abandonment** in the model — cases probabilistically exit at the observed points and rates (WF_101 0.5 after unload; WF_102 0.6 after steps 6/8/12; WF_103 0.6 after steps 3/4/12; WF_104 1.0 after steps 6/15/23; WF_105 0.5 after sort; WF_108 0.667 after steps 7/9; WF_109 0.333 after deburr; WF_1106 0.833 after steps 7/8; WF_1107 0.75 after steps 1/3/8). 5 failure-ending cases are real scrap (NFC 418 / missing-workpiece 401); success-ending interior stops are abandonment, not window truncation. Only 1–2-step stubs on non-terminal activities count as missing data — the only such stub is WF_1107_15 (1 step), which the tool retained as an early exit (1/37 ≈ 2.7% effect on WF_1107's exit probability; accepted).

## 4. Censoring Summary

- 37 cases, 13 complete (ending in `/hbw/store`), 0 left-censored, 0 right-censored, 24 incomplete-interior.
- Initial WIP at window start: **0** → simulation starts empty.
- 5 of the 24 end in `failure` (real scrap, kept as early exits); 19 end in `success` mid-process (abandonment, kept as early exits); 1 is a 1-step stub (WF_1107_15, missing data per decision, negligible effect).
- Routing and variant-mix estimates use complete cases only (tool default); arrival/service estimates may use all cases.

## 5. Control Logic

### 5.1 Queue discipline (test_dispatching_rules, per resource)
- **hbw: FIFO rejected** (agreement 0.508 over 65 decision points, 32 mixed-activity). Best rules: case_age (1.0), activity_priority (1.0). Learned priority order: **`/hbw/store_empty_bucket` > `/hbw/unload`** (122 overtakes of unload by store_empty_bucket). **Confirmed rule: activity-based priority** (store_empty_bucket > unload) — kept as the modelled rule.
- **vgr: FIFO confirmed** (agreement 1.0 over 15 decision points).
- All other classes (ov, mm, wt, sm, pm, hw, dm): negligible waiting (mean ≤ 6.5 s), no contention — single-user queues, discipline irrelevant.

### 5.2 Waiting-time decomposition (379 steps)
- Overall: mean wait 53.3 s, p90 61.9 s; contention 25.5%, prioritization 22.5%, extraneous 52.0%.
- **hbw dominates**: 98 steps, mean wait 177.9 s, p90 643.4 s; 26.1% prioritization (later-enabled steps overtake → non-FIFO, consistent with 5.1), **50.5% extraneous (resource idle while waiting) → modelled as an explicit transfer/hand-off delay between vgr and hbw, NOT folded into vgr service time** (confirmed decision).
- **vgr**: 104 steps, mean 19.4 s; 52.9% contention (pure FIFO queueing), 0% prioritization.
- `/hbw/unload` is the single worst activity: mean 465.1 s, p90 832.1 s — new cases queue behind in-process bucket traffic (store_empty_bucket priority) plus hand-off delay.

### 5.3 Release control
- **Confirmed: exogenous operator-driven batch releases** — not completion-triggered, not WIP-capped. Modelled as a **single global arrival process into hbw** reproducing the bursty batch structure (12 bursts, mean size 3.08, burst IAT mean 1.97 s, gap mean 418.8 s, min 33.3 s, max 989.3 s), then split by process-model (variant) proportions.
- Evidence: 37 releases, max WIP 9, time-avg WIP 6.07 (10.8% of time at max). Completion-triggered release not supported: only 10.8% of releases within 5 s of a completion (lift 3.34), 13.5% within 30 s (lift 0.75 < 1). No WIP cap observed (WIP at release 0–8, no ceiling at 9).

### 5.4 Intra-case concurrency
- 81.1% of cases have overlapping steps; 1.05 overlapping steps/case (1.46 for completed cases) → model as concurrent processes, not a strict chain.
- Material pairs (previous → next):
  1. `/hbw/store_empty_bucket` → `/ov/burn`: 17 cases, mean overlap 35.5 s (workpiece released to track while bucket operation still finishing)
  2. `/hbw/store_empty_bucket` → `/vgr/pick_up_and_transport`: 13 cases, 28.8 s (transporter called before bucket released)
  3. `/vgr/pick_up_and_transport` → `/hbw/get_empty_bucket`: 5 cases, 17.2 s
  4. `/hbw/get_empty_bucket` → `/vgr/pick_up_and_transport`: 4 cases, 22.3 s
- All four pairs are physically plausible (transporter/hand-off overlap with bucket operations) and are marked `concurrent_with_previous` in the spec.

## 6. Initial State

- WIP at window start: 0; no cases in progress; no cases excluded from estimation (the 1 stub is retained per §3 note).

## 7. Confirmed Decisions (Phase 2 follow-up — all open questions resolved)

1. **hbw queue rule**: activity-based priority (`/hbw/store_empty_bucket` > `/hbw/unload`) is the modelled rule (not case_age).
2. **hbw idle-waiting**: modelled as an explicit transfer/hand-off delay between vgr and hbw; not folded into vgr service time.
3. **Releases**: exogenous operator-driven batch releases; single global arrival process into hbw with bursty batch structure (12 bursts, mean size ~3, gaps ~418.8 s), then split by process-model proportions.
4. **WF_104 rework**: probabilistic branch after human review; rework repeats until pass, capped at 3 iterations to avoid infinite loops.
5. **WF_1106 drill choice**: probabilistic branch 60/40 (drill vs cylindrical_drill) within the single WF_1106 process model.
6. **Early exits**: real scrap/abandonment in the model — cases probabilistically exit at the observed points and rates (WF_1106 ~83%, WF_1107 ~75%, WF_104 100% of observed cases, others per §3).

No open questions remain. Remaining calibration items (out of scope for topology): pass/fail probability of the WF_104 rework branch, and the magnitude of the vgr→hbw hand-off delay.
