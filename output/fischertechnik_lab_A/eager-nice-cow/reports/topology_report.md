# Topology Report — fischertechnik_lab_A (run: eager-nice-cow)

## 1. Scope & Data Basis

- **Source:** `work_files/eventlog_cleaned.parquet` — 576 rows × 22 columns; 192 activity instances × 3 lifecycle transitions (`scheduled` → `start` → `complete`); **18 cases**, **9 variants**, **20 activities**, **15 resources**.
- **Window:** 2021-07-06 15:08:27.91 → 16:01:31.12 UTC (≈ 53 min, horizon 3183.2 s). First activity `/hbw/unload`, terminal activity `/hbw/store`.
- **Outcomes:** 184 success / 8 failure (418 ×7 precondition, 401 ×1 auth).
- **Censoring:** 3 of 18 cases complete (WF_101_30, WF_102_31, WF_1106_22); 3 right-censored at window end (WF_104_21, WF_108_18, WF_109_16); 12 stop inside the window without the terminal activity. **Initial WIP at window start = 0** (no left-censored cases).

> **Spec correction applied during this pass:** the previously written `variants` section left 6 variants (WF_103, WF_104, WF_105, WF_108, WF_109, WF_1107) ending at `/hbw/get_empty_bucket` — a routing that can never reach the terminal activity `/hbw/store`. This was an artifact of window truncation (no complete case of those variants was observed), not a real early exit. All 6 were completed with the **standard terminal tail** (verified identical on all 3 complete cases, after `/hw/human_review`):
> `/vgr/pick_up_and_transport @ vgr_1` → `/hbw/get_empty_bucket @ hbw_1` (concurrent) → `/vgr/pick_up_and_transport @ vgr_1` → `/hbw/store @ hbw_1`.
> The `assumptions` section records this. All 9 variants now terminate at `/hbw/store`.

## 2. Resources

15 concrete resources, each a **single-server queue (capacity 1)**. Paired resources of the same class are independent (e.g. `hbw_1` and `hbw_2` are separate queues).

| Class | Resources | Role (activities) |
|---|---|---|
| `hbw` | hbw_1, hbw_2 | Bucket warehouse / handling: `/hbw/unload`, `/hbw/store_empty_bucket`, `/hbw/get_empty_bucket`, `/hbw/store` |
| `vgr` | vgr_1, vgr_2 | VGR transporter: `/vgr/pick_up_and_transport` |
| `wt` | wt_1, wt_2 | Workpiece transporter: `/wt/pick_up_and_transport` |
| `ov` | ov_1, ov_2 | Oven: `/ov/burn`, `/ov/temper` |
| `mm` | mm_1, mm_2 | Milling machine: `/mm/mill`, `/mm/deburr`, `/mm/drill`, `/mm/transport_from_to` |
| `sm` | sm_1, sm_2 | Sorter / transport: `/sm/sort`, `/sm/transport` |
| `pm` | pm_1 | Punch machine: `/pm/punch_recesses`, `/pm/punch_gill`, `/pm/punch_ribbing` |
| `dm` | dm_2 | Drilling machine: `/dm/lower`, `/dm/cylindrical_drill` |
| `hw` | hw_1 | Human workstation: `/hw/human_review` |

Notes:
- `hbw_2` handles the early bucket operations (unload / store_empty_bucket); `hbw_1` handles the terminal operations (get_empty_bucket / store).
- `vgr_2` is used for the early transports; `vgr_1` carries the workpiece through the back half (after the oven) and the terminal tail.
- `ov_1` is used by most variants; `ov_2` by WF_104 / WF_108 / WF_1106.
- `mm_1` and `mm_2` are split by variant (front vs back milling path).

## 3. Variant Routings

9 variants. Variant-mix probabilities are the **share of released cases over all 18 cases** (the complete-case mix of 3 cases is too thin to be representative). All variants terminate at `/hbw/store`. No true early exits are modelled (`early_exit_probability = 0` for all).

| Variant | Prob. | n cases | Steps | Terminal tail |
|---|---|---|---|---|
| WF_101 | 0.1333 | 2 | 15 | yes (complete) |
| WF_102 | 0.1333 | 2 | 13 | yes (complete) |
| WF_103 | 0.1333 | 2 | 16 | added (window-truncated) |
| WF_104 | 0.0667 | 1 | 17 | added (window-truncated) |
| WF_105 | 0.1333 | 2 | 13 | added (window-truncated) |
| WF_108 | 0.0667 | 1 | 15 | added (window-truncated) |
| WF_109 | 0.0667 | 1 | 16 | added (window-truncated) |
| WF_1106 | 0.1333 | 2 | 14 | yes (complete) |
| WF_1107 | 0.1333 | 2 | 15 | added (window-truncated) |

**Common structure.** Every variant (except WF_104) opens with `/hbw/unload @ hbw_2` → `/vgr/pick_up_and_transport @ vgr_2`, then diverges through a variant-specific machine path (oven burn/temper, milling, drilling, punching, sorting), passes through `/hw/human_review @ hw_1`, and closes with the standard terminal tail on `vgr_1` / `hbw_1` ending at `/hbw/store @ hbw_1`.

**WF_104** is the only variant that does **not** start with `/hbw/unload`: its first observed step is `/vgr/pick_up_and_transport @ vgr_2` (its unload predates the window — case WF_104_20 has `missing_first_activity`). It also uses `ov_2` and a double-transport (`vgr_2` then `vgr_1`) mid-route.

**Early exits.** None modelled. `discover_variant_routings` reported "early exits" for the 6 variants without a complete case, but those are window-truncation artifacts (the case simply had not finished by 16:01:31), not scrap/abandonment. Because 418/401 failures are retryable and the workpiece continues, no permanent early exit is modelled.

## 4. Dispatching Rules / Priorities & Queue Discipline

From `test_dispatching_rules` (per concrete resource, 44 decision points total):

| Class | n decision pts | FIFO | LIFO | case_age | most_progressed | activity_priority | Best rule | FIFO rejected? |
|---|---|---|---|---|---|---|---|---|
| `hbw` | 34 (15 mixed-activity) | 0.559 | 0.441 | 0.824 | 0.583 | **0.971** | activity_priority | **Yes** |
| `vgr` | 10 (0 mixed-activity) | **1.0** | 0.0 | 0.7 | 0.6 | 1.0 | FIFO | No |

- **`hbw` → priority queue** (`simpy.PriorityResource`), learned activity order:
  **`/hbw/store` > `/hbw/store_empty_bucket` > `/hbw/get_empty_bucket` > `/hbw/unload`**.
  Evidence: activity_priority 97.1% vs FIFO 55.9% over 34 decision points. Dominant overtaking: `/hbw/store_empty_bucket` chosen over waiting `/hbw/unload` (55 times) — i.e. finishing a bucket store pre-empts a new unload.
- **`vgr` → FIFO** (100% agreement over 10 decision points; no mixed-activity contention observed).
- All other classes (`ov`, `mm`, `sm`, `wt`, `pm`, `dm`, `hw`) have no mixed-activity contention and are modelled as **FIFO** single servers.

## 5. Waiting-Time Decomposition

From `decompose_waiting_times` (192 steps; overall mean wait 79.1 s, p90 139.4 s):

| Class | n | mean wait (s) | contention | prioritization | extraneous |
|---|---|---|---|---|---|
| `hbw` | 46 | 289.0 | 0.181 | 0.176 | **0.643** |
| `vgr` | 55 | 26.4 | **0.456** | 0.0 | 0.544 |
| `ov` | 18 | 6.2 | 0.0 | 0.0 | 1.0 |
| `mm` | 21 | 6.2 | 0.0 | 0.0 | 1.0 |
| `sm` | 15 | 2.7 | 0.0 | 0.0 | 1.0 |
| `wt` | 14 | 5.5 | 0.0 | 0.0 | 1.0 |
| `pm` | 5 | 3.2 | 0.0 | 0.0 | 1.0 |
| `dm` | 4 | 4.1 | 0.0 | 0.0 | 1.0 |
| `hw` | 14 | 3.9 | 0.0 | 0.0 | 1.0 |

- **64% of all waiting is "extraneous"** (resource idle while the case waits) — hand-off / transport / release delays, not machine contention. This is concentrated in `hbw` (64.3% of 46 waits, mean 289 s; `/hbw/unload` alone averages 609 s wait).
- **`vgr` is the only class with material contention** (45.6% of vgr waits) — genuine queueing at the transporters.
- The `hbw` prioritization share (17.6%) reflects the non-FIFO priority discipline in §4.

## 6. Release Control

From `detect_release_control` (18 releases): **open, bursty arrivals** — no WIP cap, no completion trigger.

- **WIP:** max 12, time-avg 7.09 (only 4.1% of time at max WIP). WIP at release: mean 5.5, median 5.5, min 0, max 11.
- **Burst/gap regime (two-regime):** 7 bursts of mean size **2.57** (max 8); burst IAT mean **1.59 s**; gap IAT mean **377.5 s** (gap-to-burst ratio ≈ 237).
- **Completion-triggered release: none** — 0% of releases fall within 5 s / 30 s of a completion (chance 2.8% / 15.6%, lift 0.0).

**Modelling implication:** use a **burst/gap arrival process** (gap process between bursts + `burst_size` arrivals per burst spaced by `burst_iat`), not the mixed mean IAT.

## 7. Intra-Case Concurrency

From `detect_intra_case_concurrency` (1.667 overlapping steps per completed case; 50% of cases have overlap). The next step is requested **before** the previous one releases its resource (e.g. the bucket store / next transport is called while the machine still works). Modelled concurrent pairs:

| Previous | Next | Cases | Mean overlap (s) |
|---|---|---|---|
| `/hbw/store_empty_bucket` | `/ov/burn` | 4 | 38.7 |
| `/hbw/store_empty_bucket` | `/vgr/pick_up_and_transport` | 3 | 35.1 |
| `/vgr/pick_up_and_transport` | `/hbw/get_empty_bucket` | 2 | 26.5 |

These are encoded in the spec as `concurrent_with_previous: true` on the affected steps (the terminal-tail `get_empty_bucket` is concurrent in WF_101/102/1106/108/1107; the `store_empty_bucket → burn` / `store_empty_bucket → vgr` overlaps in the oven variants). Physically plausible: a transporter is dispatched / the oven is loaded while the bucket handling still holds its resource.

## 8. Failure / Retry Handling

8 failed completions: **418 ×7 (precondition)** and **401 ×1 (auth)**, across `/hbw/store_empty_bucket`, `/vgr/pick_up_and_transport`, and `/hbw/unload`.

**Semantics (confirmed):** 418/401 events are **retryable**.
- **One `event_id` = one attempt.** A `complete` row is terminal for that attempt.
- **A retry is a new `event_id`** repeating the same activity on the same resource.
- The operation **retries and eventually succeeds**; the **workpiece continues** along its routing.
- **No permanent scrap** is modelled — a failed attempt does not terminate the case.

In the simulation, a failed attempt should re-enqueue the same activity (new attempt) rather than ending the case; the case only completes when the terminal activity `/hbw/store` succeeds.

## 9. Assumptions (recorded in spec `assumptions`)

1. **Window truncation, not scrap:** the short (~53 min) window leaves only 3 of 18 cases complete; the 15 non-censored cases are treated as window-truncated, not abandoned, because 418/401 are retryable and the workpiece continues.
2. **No true early exits:** `early_exit_probability = 0` for all variants; the tool-reported "early exits" for variants without a complete case are truncation artifacts.
3. **Standard terminal tail** (verified on all 3 complete cases) applied to the 6 window-truncated variants: `vgr_1 transport → hbw_1 get_empty_bucket (concurrent) → vgr_1 transport → hbw_1 store`.
4. **Variant mix** = share of released cases over all 18 (complete-case mix of 3 is too thin).
5. **hbw = priority** (store > store_empty_bucket > get_empty_bucket > unload); **vgr = FIFO**; all other classes FIFO.
6. **Release = open, bursty** (no WIP cap, no completion trigger); model with burst/gap process.
7. **Concurrency** for the three pairs in §7.
8. **Initial WIP = 0** (no left-censored cases).
9. **All resources capacity 1**; each concrete resource is a separate single-server queue.
10. **WF_104** starts at `/vgr/pick_up_and_transport` (its unload predates the window).
11. **64% of waiting is extraneous** (hand-off/transport/release), dominated by `hbw`; `vgr` is the only class with material contention.
12. **`workpiece_size`** for `/ov/burn` mixes categorical (`regular/middle/large/maxi`) and numeric (`30`–`60`) labels; kept as raw string, no size-class mapping applied in this phase.

## 10. Open Questions / Notes

- The 6 window-truncated variants have **no complete case**, so their mid-route machine sequences are the *longest observed partial* sequences; the terminal tail is inferred from the 3 complete cases. If a variant-specific terminal deviation exists, it is not observable in this window.
- `workpiece_size` needs a size-class mapping in a later phase (categorical vs numeric) if burn duration depends on it.
- The burst/gap arrival parameters (burst_size ≈ 2.57, burst_iat ≈ 1.59 s, gap_iat ≈ 377.5 s) are estimates from 18 releases in one window; a longer observation would tighten them.
