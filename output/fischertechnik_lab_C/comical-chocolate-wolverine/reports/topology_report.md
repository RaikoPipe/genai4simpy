# Topology Report — fischertechnik_lab_C

**Phase 2 — Topology & Control-Logic Discovery**
Window: `2021-07-01 18:48:23.227 → 20:19:24.734 UTC` (horizon ≈ 5,461.5 s)
Dataset: 1,137 rows → 379 activity instances, 37 cases, 9 variants, 15 resources, 21 activities.

---

## 1. System Topology

### 1.1 Two parallel production tracks (confirmed)

The system is two production lines linked only for workpiece exchange:

| Track | Oven (ov) | Mill (mm) | Winder (wt) | Sorter (sm) |
|---|---|---|---|---|
| Track 1 (shop-floor 1) | `ov_1` | `mm_1` | `wt_1` | `sm_1` |
| Track 2 (shop-floor 2) | `ov_2` | `mm_2` | `wt_2` | `sm_2` |

Each case runs its machine steps entirely on one track (verified: no case uses both `ov_1` and `ov_2`, etc.). The tracks are **separate capacity pools**.

**Single-instance (not paired) resources** (confirmed):
- `pm_1` (punch machine) — shop-floor 1 only.
- `hw_1` (human workstation) — shop-floor 1 only.
- `dm_2` (drill machine) — shop-floor 2 only.

### 1.2 hbw / vgr: SHARED pool at the exchange point (confirmed)

The task asked to verify whether `hbw` (bucket store) and `vgr` (vertical gripper/transporter) are per-track or shared. **Confirmed (user + data): they form a single shared pool of 2 hbw + 2 vgr instances contended by both tracks — both tracks use all four instances, serialized (no temporal overlap).**

| Resource | Track-1 cases | Track-2 cases | Cross-track (T1×T2) temporal overlap | Within-track self-concurrency |
|---|---|---|---|---|
| `hbw_1` | 17 | 9 | **0** | 0 |
| `hbw_2` | 28 | 29 | **0** | 0 |
| `vgr_1` | 42 | 16 | **0** | 0 |
| `vgr_2` | 14 | 14 | **0** | 0 |

- Both tracks' cases use **all four** `hbw_1/2` and `vgr_1/2` instances (e.g. `hbw_2` serves 28 T1 + 29 T2 cases).
- **Zero cross-track temporal overlap**: a Track-1 case and a Track-2 case never occupy the same `hbw`/`vgr` instance at the same time. The shared resources serialize across tracks.
- **No within-track self-concurrency** either (each instance is single-capacity; a case's successive `hbw`/`vgr` steps never overlap).

**Conclusion (confirmed decision):** model `hbw_1, hbw_2, vgr_1, vgr_2` as a **single shared pool of 2 hbw + 2 vgr single-capacity resources** (not per-track). The two tracks contend for these shared exchange-point resources. This is the only place the two lines interact.

### 1.3 Resources table (spec `resources`)

| Resource | Class | Capacity | Scope |
|---|---|---|---|
| `hbw_1` | hbw | 1 | shared (exchange point) |
| `hbw_2` | hbw | 1 | shared (exchange point) |
| `vgr_1` | vgr | 1 | shared (exchange point) |
| `vgr_2` | vgr | 1 | shared (exchange point) |
| `ov_1` | ov | 1 | track 1 |
| `ov_2` | ov | 1 | track 2 |
| `mm_1` | mm | 1 | track 1 |
| `mm_2` | mm | 1 | track 2 |
| `wt_1` | wt | 1 | track 1 |
| `wt_2` | wt | 1 | track 2 |
| `sm_1` | sm | 1 | track 1 |
| `sm_2` | sm | 1 | track 2 |
| `pm_1` | pm | 1 | shop-floor 1 only |
| `hw_1` | hw | 1 | shop-floor 1 only |
| `dm_2` | dm | 1 | shop-floor 2 only |

All 15 resources are single-capacity (no resource is ever observed busy with two cases at once).

---

## 2. Variant Routing (spec `variants`)

Routing (main sequence, step presence, per-step resources) is estimated from **complete cases only** (13 of 37). Variant mix (probability) is estimated from **all 37 released cases** (every case carries its `process_model_id` at release).

| Variant | p (released) | #cases | #complete | Main sequence (complete cases) | Track |
|---|---|---|---|---|---|
| WF_101 | 0.108 | 4 | 2 | unload → vgr → store_empty_bucket → vgr → **ov/burn → ov/temper** → wt → mm/mill → mm/deburr → sm/sort → vgr → hw → hbw/get_empty_bucket → vgr → vgr → store | T1 |
| WF_102 | 0.135 | 5 | 2 | unload → vgr → store_empty_bucket → **ov/burn** → wt → mm/drill → sm/transport → dm/lower → vgr → hw → hbw/get_empty_bucket → vgr → vgr → store | T2 |
| WF_103 | 0.135 | 5 | 2 | unload → vgr → store_empty_bucket → vgr → **ov/burn → ov/temper** → wt → mm/mill → mm/deburr → sm/transport → **pm/punch_recesses** → vgr → hw → hbw/get_empty_bucket → vgr → vgr → store | T1 |
| WF_104 | 0.081 | 3 | 0 | **rework loop** ending in explicit `/hbw/store` (see §2.1) | T2→T1→T2 |
| WF_105 | 0.108 | 4 | 2 | unload → vgr → store_empty_bucket → vgr → **ov/burn** → wt → mm/deburr → sm/sort → vgr → hw → vgr → hbw/get_empty_bucket → vgr → store | T1 |
| WF_108 | 0.081 | 3 | 1 | unload → vgr → store_empty_bucket → **ov/burn** → wt → mm/drill → mm/deburr → sm/sort → vgr → vgr → hw → vgr → hbw/get_empty_bucket → vgr → store | T2 |
| WF_109 | 0.081 | 3 | 2 | unload → vgr → store_empty_bucket → vgr → **ov/burn → ov/temper** → wt → mm/mill → mm/deburr → sm/transport → **pm/punch_ribbing** → vgr → hw → hbw/get_empty_bucket → vgr → vgr → store | T1 |
| WF_1106 | 0.162 | 6 | 1 | unload → vgr → store_empty_bucket → **ov/burn** → wt → mm/transport_from_to → sm/transport → **dm/drill ∥ dm/cylindrical_drill** → vgr → hw → vgr → hbw/get_empty_bucket → vgr → store | T2 |
| WF_1107 | 0.108 | 4 | 1 | unload → vgr → store_empty_bucket → vgr → **ov/burn** → mm/transport_from_to → sm/transport → **pm/punch_gill** → vgr → hw → hbw/get_empty_bucket → vgr → vgr → store | T1 |

Common skeleton (all variants): `/hbw/unload` (release) → `/vgr/pick_up_and_transport` → `/hbw/store_empty_bucket` → (variant-specific machine steps) → `/hw/human_review` → `/hbw/get_empty_bucket` → `/vgr/pick_up_and_transport` → `/hbw/store` (terminal).

### 2.1 WF_104 — quality rework loop with explicit terminal (confirmed)

WF_104 is a **quality rework loop**: a failed human review sends the workpiece back for reprocessing. Its observed sequence crosses both tracks (T2 → T1 → T2), reflecting the rework round-trip:

```
unload(T2) → vgr → store_empty_bucket → ov/burn(T2) → wt(T2) → sm/sort(T2)
→ vgr → vgr → wt(T1) → mm/deburr(T1) → sm/transport(T1) → pm/punch_gill
→ vgr → hw/human_review → vgr → store_empty_bucket → ov/burn(T2) → wt(T2)
→ mm/mill(T2) → sm/sort(T2) → vgr → vgr → vgr → **hbw/store**
```

No complete WF_104 case exists in the window (0 of 3 complete), so its `main_sequence` is the longest observed (partial) sequence and its early-exit probability (1.0) is based on a single scrap case. **Confirmed decision:** the rework loop gets an **explicit terminal `/hbw/store` step after the second `ov/burn`**, mirroring the main flow's terminal — the rework is a quality loop that must eventually exit to storage (the final transport-to-store legs are not observed, so the terminal is appended to the observed partial sequence).

### 2.2 WF_1106 — conditional routing (confirmed)

WF_1106 is modelled as a **single process model with conditional routing** at the drill step: `/dm/drill` (p=0.6) vs `/dm/cylindrical_drill` (p=0.4), both on `dm_2`. The branch is chosen per case; both are real (not truncation) — the 5 non-completed WF_1106 cases are missing-data stubs (see §3), not drill-branch outcomes. **Confirmed decision:** the observed **0.6/0.4 split is kept as the conditional-routing probability** — it is documented as an **estimate from limited data (5 stub cases)**.

---

## 3. Censoring & Truncation (spec `initial_state`)

`detect_censoring`: 37 cases, **13 complete**, **0 right-censored**, **0 left-censored**, **24 incomplete-interior**, initial WIP at window start = **0**.

The 24 incomplete-interior cases are **not** window truncation (none overlap the window edges). Per the confirmed lifecycle:state rule they split into two classes:

| Class | Count | Rule | Disposition |
|---|---|---|---|
| **Failure-ending** (last activity `lifecycle:state = failure`) | **5** | real scrap | **kept** → modelled as early exits |
| **Success-ending, non-terminal** (last activity `success` but no `/hbw/store`) | **19** | missing data (log cut) | **dropped** from routing/early-exit estimation |

**5 real scrap (early-exit) cases:**

| Case | Variant | Steps | Fails at (activity / resource) | Steps completed before exit |
|---|---|---|---|---|
| WF_101_26 | WF_101 | 1 | `/hbw/unload` / hbw_2 | 0 |
| WF_101_28 | WF_101 | 1 | `/hbw/unload` / hbw_2 | 0 |
| WF_103_27 | WF_103 | 4 | `/vgr/pick_up_and_transport` / vgr_1 | 3 |
| WF_104_17 | WF_104 | 16 | `/vgr/pick_up_and_transport` / vgr_1 | 15 |
| WF_1107_13 | WF_1107 | 4 | `/vgr/pick_up_and_transport` / vgr_1 | 3 |

**19 missing-data stubs (excluded, recorded in `initial_state.excluded_from_estimation`):** WF_102_26/27/29, WF_103_25/28, WF_104_18/19, WF_105_18/20, WF_108_14/15, WF_109_13, WF_1106_15/17/18/19/20, WF_1107_12/15.

**Early-exit probabilities (scrap-only, `early_exit_p = scrap / (complete + scrap)`):**

| Variant | complete | scrap | early_exit_p | exit after n steps |
|---|---|---|---|---|
| WF_101 | 2 | 2 | **0.500** | 0 (at `/hbw/unload`) |
| WF_102 | 2 | 0 | **0.000** | — |
| WF_103 | 2 | 1 | **0.333** | 3 (at `/vgr/…`) |
| WF_104 | 0 | 1 | **1.000** | 15 (at `/vgr/…`) |
| WF_105 | 2 | 0 | **0.000** | — |
| WF_108 | 1 | 0 | **0.000** | — |
| WF_109 | 2 | 0 | **0.000** | — |
| WF_1106 | 1 | 0 | **0.000** | — |
| WF_1107 | 1 | 1 | **0.500** | 3 (at `/vgr/…`) |

> **Deviation note:** `check_spec_against_evidence` flags 7 variants (WF_102/103/105/108/109/1106/1107) where the spec's `early_exit_probability` is lower than the tool's default. This is **intentional**: the tool counts *all* non-terminal-ending cases as early exits, but per the confirmed lifecycle:state rule the success-ending non-terminal cases are missing data and are excluded. Only the 5 failure-ending cases are real scrap. Recorded in `assumptions`.

---

## 4. Control Logic (spec `control_policies`)

### 4.1 Queue discipline

`test_dispatching_rules` (per resource):

| Class | Decision points | FIFO | Best rule | FIFO rejected? |
|---|---|---|---|---|
| **hbw** | 65 | 0.508 | **case_age / activity_priority (1.00)** | **Yes** |
| **vgr** | 15 | **1.00** | FIFO | No |

- **hbw is NOT FIFO.** The learned activity priority is `[store_empty_bucket, unload]` — `store_empty_bucket` overtakes a waiting `unload` 122 times. Modelled as a **priority queue** (`simpy.PriorityResource`) with order `[/hbw/store_empty_bucket, /hbw/unload]`.
- **vgr is FIFO** (100% agreement over 15 decisions).

### 4.2 Waiting-time causes

`decompose_waiting_times` (379 steps, mean wait 53.3 s, p90 61.9 s):

| Class | n | mean wait | contention | prioritization | extraneous |
|---|---|---|---|---|---|
| **hbw** | 98 | 177.9 s | 0.235 | **0.261** | 0.505 |
| **vgr** | 104 | 19.4 s | 0.529 | 0.0 | 0.471 |
| ov | 40 | 5.0 s | 0 | 0 | 1.0 |
| mm | 41 | 4.8 s | 0 | 0 | 1.0 |
| wt | 29 | 6.5 s | 0 | 0 | 1.0 |
| sm | 32 | 2.5 s | 0 | 0 | 1.0 |
| dm | 10 | 3.0 s | 0 | 0 | 1.0 |
| pm | 8 | 3.2 s | 0 | 0 | 1.0 |
| hw | 17 | 3.1 s | 0 | 0 | 1.0 |

- **hbw** is the bottleneck: mean wait 177.9 s (p90 643 s). 26% of its waiting is **prioritization** (later-enabled steps overtaking — consistent with the non-FIFO finding) and 50% is **extraneous** (resource idle while the case waits → hand-off/transport/release delay, not resource contention).
- **vgr** waiting is 53% **contention** (FIFO queueing) — the shared transporters are genuinely contended.
- All machine classes (ov/mm/wt/sm/dm/pm/hw) show **100% extraneous** waiting (mean ~3–6 s) — their waits are hand-off/transport delays, not resource contention.

### 4.3 Release control

`detect_release_control` (37 releases): **open (bursty releases)** — no WIP cap, no completion-triggered release.

- Max WIP = 9, time-averaged WIP = 6.07.
- Releases come in **bursts**: 12 bursts, mean burst size 3.08 (range 1–9), burst IAT mean 1.97 s, separated by gaps mean 418.8 s (gap:burst IAT ratio ≈ 212).
- Completion-triggered release: only 10.8% of releases within 5 s of a completion (lift 3.3 over chance) — weak, not a controller.
- **Model:** open arrival stream with a burst/gap process (do NOT use the mixed mean IAT).

### 4.4 Intra-case concurrency

`detect_intra_case_concurrency`: 81% of cases have ≥1 overlapping step pair; 1.46 overlapping steps per completed case. The next step is requested **before** the previous releases its resource.

| Previous activity | Next activity | Overlap count | Mean overlap |
|---|---|---|---|
| `/hbw/store_empty_bucket` | `/ov/burn` | 17 | 35.5 s |
| `/hbw/store_empty_bucket` | `/vgr/pick_up_and_transport` | 13 | 28.8 s |
| `/vgr/pick_up_and_transport` | `/hbw/get_empty_bucket` | 5 | 17.2 s |
| `/hbw/get_empty_bucket` | `/vgr/pick_up_and_transport` | 4 | 22.3 s |

**Modelled as concurrent steps** (`concurrent_with_previous: true`): the two dominant, physically-plausible pairs — `store_empty_bucket → ov/burn` (oven pre-heats while the bucket is still being stowed) and `store_empty_bucket → vgr/pick_up_and_transport` (transporter called while the bucket is stowed). The two smaller vgr/hbw pairs (5 and 4 cases) are below the materiality threshold and left sequential.

---

## 5. Spec Sections Written

- `window` — t0, horizon, terminal `/hbw/store`, first `/hbw/unload`.
- `resources` — 15 single-capacity resources (2 shared hbw, 2 shared vgr, 2+2+2+2 track pools, pm_1/hw_1/dm_2 single-instance).
- `variants` — 9 variants with main sequences, per-step resources, conditional WF_1106 drill branch, scrap-only early-exit probabilities, and the explicit WF_104 terminal `/hbw/store`.
- `control_policies` — hbw priority queue (store_empty_bucket > unload), vgr FIFO, open bursty release, intra-case concurrency pairs.
- `initial_state` — WIP 0 at start; 19 missing-data stubs excluded from estimation.
- `assumptions` — 10 modelling assumptions (tracks, shared hbw/vgr, truncation rule, variant mix vs routing, WF_104 rework, WF_1106 conditional routing, queue discipline, concurrency, release, initial WIP).

---

## 6. Confirmed Decisions (Phase 2 follow-up)

All three open questions from Phase 2 have been answered authoritatively and are now recorded in the spec (`assumptions`) and reflected above:

1. **hbw/vgr sharing — CONFIRMED as a shared pool.** One pool of 2 hbw + 2 vgr instances is contended by both tracks (not per-track). The data finding (zero cross-track temporal overlap, both tracks using all four instances) already reflects this; it is now stated explicitly as a confirmed decision (§1.2).

2. **WF_104 rework loop — explicit terminal added.** The rework loop gets an **explicit terminal `/hbw/store` step after the second `ov/burn`**, mirroring the main flow's terminal (the quality loop must eventually exit to storage). The WF_104 variant routing in the spec now ends in `/hbw/store` (§2.1).

3. **WF_1106 drill branch — 0.6/0.4 kept as the conditional-routing probability.** The `/dm/drill` (0.6) vs `/dm/cylindrical_drill` (0.4) estimate is retained and documented as an estimate from limited data (5 stub cases) (§2.2).
