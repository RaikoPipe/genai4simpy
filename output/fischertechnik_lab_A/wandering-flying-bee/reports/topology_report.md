# Topology & Control-Logic Report — Fischertechnik Lab A

**Window:** 2021-07-06T15:08:27.914751Z → 2021-07-06T16:01:31.117000Z (horizon 3183.2 s ≈ 53 min)
**Volume:** 18 cases, 192 activity instances, 9 variants, 20 activities, 15 resources
**Terminal activity:** `/hbw/store` · **First activity:** `/hbw/unload`

---

## 1. System Topology (two-line layout)

The plant is a **two-line** system. Transport `start_position`/`end_position` parameters confirm the physical layout:

| Line | Warehouse | Transporter | Machines |
|------|-----------|-------------|----------|
| **Line 1 (intake)** | `hbw_2` | `vgr_2` | `ov_1`, `ov_2`, `mm_1`, `mm_2`, `wt_1`, `wt_2`, `sm_1`, `sm_2`, `dm_2`, `pm_1` |
| **Line 2 (return)** | `hbw_1` | `vgr_1` | `hw_1` (human review) |

**Warehouse semantics**
- `hbw_2` = **intake warehouse**: `/hbw/unload` (workpiece out) + `/hbw/store_empty_bucket` (empty bucket in).
- `hbw_1` = **return warehouse**: `/hbw/get_empty_bucket` (empty bucket out) + `/hbw/store` (finished workpiece in).

**Resource table (15 concrete resources)**

| Resource | Class | Capacity | Role |
|----------|-------|----------|------|
| `hbw_1` | hbw | 1 | return warehouse |
| `hbw_2` | hbw | 1 | intake warehouse |
| `vgr_1` | vgr | 1 | line-2 transporter (return + mid-route) |
| `vgr_2` | vgr | 1 | line-1 transporter (first transport) |
| `mm_1` | mm | 1 | mill / deburr / drill |
| `mm_2` | mm | 1 | mill / drill / transport_from_to |
| `ov_1` | ov | 1 | burn / temper |
| `ov_2` | ov | 1 | burn |
| `wt_1` | wt | 1 | transport |
| `wt_2` | wt | 1 | transport |
| `sm_1` | sm | 1 | sort / transport |
| `sm_2` | sm | 1 | sort / transport |
| `dm_2` | dm | 1 | lower / cylindrical_drill |
| `pm_1` | pm | 1 | punch (recesses / gill / ribbing) |
| `hw_1` | hw | 1 | human review |

---

## 2. Variant Routing (9 variants)

All variants share the **canonical return tail** after `/hw/human_review`:
`vgr_1/pick_up_and_transport → hbw_1/get_empty_bucket → vgr_1/pick_up_and_transport → hbw_1/store`.
Per the authoritative context, any absence of this tail in the log is **time-window truncation, not optionality**, so it is modelled for every variant.

| Variant | Prob. | Cases | Key routing (before return tail) |
|---------|-------|-------|----------------------------------|
| WF_101 | 0.1111 | 2 | unload → vgr_2 → store_empty_bucket → vgr_1 → burn(ov_1) → temper(ov_1) → mill(mm_1) → deburr(mm_1) → sort(sm_1) → vgr_1 → human_review |
| WF_102 | 0.1111 | 2 | unload → vgr_2 → wt_2 → drill(mm_2) → sm_2 → dm_2/lower → store_empty_bucket → vgr_1 → human_review |
| WF_103 | 0.1111 | 2 | unload → vgr_2 → store_empty_bucket → vgr_1 → burn(ov_1) → temper(ov_1) → wt_1 → mill(mm_1) → deburr(mm_1) → sm_1 → pm_1/punch_recesses → vgr_1 → human_review |
| WF_104 | 0.1111 | 1 | **cross-line**: vgr_2 → store_empty_bucket → burn(ov_2) → wt_2 → mill(mm_2) → sort(sm_2) → vgr_2 → vgr_1 → wt_1 → deburr(mm_1) → sm_1 → pm_1/punch_gill → vgr_1 → human_review |
| WF_105 | 0.1111 | 2 | unload → vgr_2 → store_empty_bucket → vgr_1 → burn(ov_1) → wt_1 → deburr(mm_1) → sort(sm_1) → vgr_1 → human_review |
| WF_108 | 0.1111 | 1 | unload → vgr_2 → store_empty_bucket → burn(ov_2) → wt_2 → drill(mm_2) → deburr(mm_2) → sort(sm_2) → vgr_2 → vgr_1 → human_review |
| WF_109 | 0.1111 | 1 | unload → vgr_2 → store_empty_bucket → vgr_1 → burn(ov_1) → temper(ov_1) → wt_1 → mill(mm_1) → deburr(mm_1) → sm_1 → pm_1/punch_ribbing → vgr_1 → human_review |
| WF_1106 | 0.1111 | 2 | unload → vgr_2 → burn(ov_2) → wt_2 → **get_empty_bucket(hbw_1)** → mm_2/transport_from_to → sm_2 → dm_2/cylindrical_drill → vgr_1 → human_review |
| WF_1107 | 0.1111 | 2 | unload → vgr_2 → store_empty_bucket → vgr_1 → burn(ov_1) → wt_1 → drill(mm_1) → sm_1 → pm_1/punch_ribbing → vgr_1 → human_review |

**Variant-specific notes**
- **WF_104** is the only **cross-line** variant (intentional two-stage design): it starts on `vgr_2` (no `/hbw/unload`), uses line-1 machines (`ov_2`, `mm_2`, `sm_2`), then crosses to line-2 (`vgr_1`, `wt_1`, `mm_1`, `sm_1`, `pm_1`) and back. Cross-line routing is allowed for this variant only.
- **WF_1106** does **not** use `/hbw/store_empty_bucket`; instead it performs `/hbw/get_empty_bucket` on `hbw_1` mid-route (step 5), a variant-specific bucket flow.
- **Role-based VGR assignment** (authoritative): `vgr_2` performs the first transport of each case; `vgr_1` performs the rest. Documented exceptions honoured: WF_104 (vgr_2 re-used at step 7) and WF_108 (vgr_2 re-used at step 9).
- **Stochastic sorting ejection**: `/sm/sort` ejection position modelled as uniform over {1,2,3}.

---

## 3. Censoring & Window Edges

- **Right-censored (cut at window end):** 3 cases — WF_104_21, WF_108_18, WF_109_16. The authoritative context additionally lists **WF_1107_17** as incomplete → **4 cases total** excluded from *routing inference only* (retained for service-time / arrival estimation).
- **Left-censored / initial WIP:** 0 — no cases in progress at window start (`wip_at_start = 0`).
- **Interior "early exits":** the discovery tool flagged 12 of 18 cases as stopping mid-process without the terminal activity. Per the authoritative context these are **window truncation** (missing canonical return tail), **not** scrap/abandonment. Therefore `early_exit_probability = 0` for all variants. This is the sole spec-vs-evidence deviation, justified by the context file and logged in `assumptions`.

---

## 4. Control Logic

### 4.1 Queue discipline (test_dispatching_rules, 44 decision points)

| Resource class | Best rule | Agreement | FIFO | Decision |
|----------------|-----------|-----------|------|----------|
| **hbw** | **activity_priority** | **97.1%** | 55.9% | **priority** (FIFO rejected) |
| **vgr** | FIFO | 100% | 100% | fifo |
| mm, ov, wt, sm, pm, dm, hw | FIFO | ~100% | ~100% | fifo (no overtaking observed) |

**HBW priority order** (learned, leave-one-out): `/hbw/store` → `/hbw/store_empty_bucket` → `/hbw/get_empty_bucket` → `/hbw/unload`.
Interpretation: warehouse **returns (store)** and **bucket handling (store_empty_bucket)** preempt new **unload** requests — the warehouse prioritises clearing finished work / empty buckets over admitting new workpieces.

### 4.2 Waiting-time decomposition (decompose_waiting_times)

- Overall mean wait: **79.1 s**.
- **hbw** mean wait **289.0 s**, dominated by **extraneous (64.3%)** — the warehouse is idle while a case waits (hand-off / release-control delay), not queueing contention.
- **vgr** wait is **contention-dominated (45.6%)** — genuine FIFO queueing for the single transporter.
- No material **prioritization (overtaking)** share on vgr → confirms FIFO there.

### 4.3 Release control (detect_release_control)

- **Verdict: open (bursty releases)** — no WIP cap, no completion trigger.
- 18 releases; max WIP 12; time-averaged WIP 7.09; WIP-at-release mean 5.5 (range 0–11).
- **Two-regime inter-arrival process:**
  - **Burst regime:** IAT mean 1.59 s (n=11) — cases released in rapid clusters.
  - **Gap regime:** IAT mean 377.5 s (n=6) — long idle stretches.
  - Burst size mean 2.57 (values: 8,1,1,2,2,3,1).
- **Modelling implication:** model the gap process and burst size separately; do **not** use the mixed mean IAT.

### 4.4 Intra-case concurrency (detect_intra_case_concurrency)

Material overlap pairs (next step requested before previous releases its resource):

| Previous | Next | Cases |
|----------|------|-------|
| `/hbw/store_empty_bucket` | `/ov/burn` | 4 |
| `/hbw/store_empty_bucket` | `/vgr/pick_up_and_transport` | 3 |
| `/vgr/pick_up_and_transport` | `/hbw/get_empty_bucket` | 2 |

Interpretation: **bucket operations overlap with workpiece steps** (the bucket is stored/retrieved while the workpiece is being burned or transported). Physically plausible → modelled as concurrent SimPy processes (`concurrent_with_previous: true` on the relevant steps).

---

## 5. Failure Handling

8 failure events (7× HTTP 418 precondition, 1× HTTP 401 auth). Per the authoritative context these are **retryable**: the operation retries and eventually succeeds; the workpiece continues. The failed attempt's service time is not counted as a completed operation.

---

## 6. Deviations & Decisions (logged in spec `assumptions`)

1. **No early exits** — overrides the tool's "early_exit_probability" heuristic; the return tail is canonical for every variant (authoritative context). *Sole spec-vs-evidence deviation.*
2. **4 incomplete cases** (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) excluded from routing inference only; retained for service-time/arrival estimation.
3. **Canonical return tail** appended to every variant's routing.
4. **Role-based VGR** (vgr_2 first, vgr_1 rest) + documented exceptions (WF_104, WF_108).
5. **Cross-line routing** allowed for WF_104 only.
6. **Stochastic sort ejection** uniform {1,2,3}.
7. **Retryable failures** (418/401).
8. **HBW activity-priority** queue; vgr FIFO; all others FIFO.
9. **Open, bursty release** with two-regime IAT.
10. **Intra-case concurrency** on bucket↔workstep pairs.

---

## 7. Open Questions

None — all findings that contradict default assumptions (FIFO, open release, sequential steps, every-case-completes) are resolved by the authoritative context provided with this task.
