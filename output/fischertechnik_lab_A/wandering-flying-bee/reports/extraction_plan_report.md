# Extraction Plan — Fischertechnik Lab A (wandering-flying-bee)

**Data:** `work_files/eventlog_cleaned.parquet` — 576 rows, 192 activity instances (3 lifecycle rows each: scheduled/start/complete), 18 cases, 9 variants, 20 activities, 15 resources. Window: 2021-07-06 15:08:27.91 → 16:01:31.12 UTC (~53 min). Outcomes: 184 success / 8 failure (7× HTTP 418, 1× HTTP 401).

---

## 1. Service Times (Processing Times)

**Duration rule (authoritative):** actual service time = `operation_end_time − time:timestamp` evaluated on the **`start` row only**. `complete_service_time` is never used (it includes queueing delay); `planned_operation_time` is reference only.

**Sample:** successful attempts only (`complete` rows with `lifecycle:state = success`, n = 184). The 8 failed attempts are **excluded** from the service-time sample — a failed attempt is not a completed operation. Each `event_id` is one attempt; a retry is a new `event_id` repeating the same process, so retries are already represented as separate instances.

**Grouping strategy:** per activity, pooling **only across machine pairs performing the same activity** — never across different activities. The topology shows no within-activity resource-specific behaviour beyond the pooling below.

| Activity group | Resources pooled | Notes |
|---|---|---|
| `/hbw/unload` | hbw_2 | single resource |
| `/hbw/store_empty_bucket` | hbw_2 | single resource |
| `/hbw/get_empty_bucket` | hbw_1 | single resource |
| `/hbw/store` | hbw_1 | single resource |
| `/vgr/pick_up_and_transport` | vgr_1 + vgr_2 | **single pooled transport distribution** (identical hardware) per confirmed decision — flagged for revisit at the modeling stage |
| `/ov/burn` | ov_1 + ov_2 | size-dependence check below |
| `/ov/temper` | ov_1 | single resource |
| `/mm/mill` | mm_1 + mm_2 | |
| `/mm/deburr` | mm_1 + mm_2 | |
| `/mm/drill` | mm_1 + mm_2 | |
| `/mm/transport_from_to` | mm_2 | single resource |
| `/wt/pick_up_and_transport` | wt_1 + wt_2 | |
| `/sm/sort` | sm_1 + sm_2 | |
| `/sm/transport` | sm_1 + sm_2 | |
| `/pm/punch_recesses`, `/pm/punch_gill`, `/pm/punch_ribbing` | pm_1 | three distinct activities — never pooled with each other |
| `/dm/lower`, `/dm/cylindrical_drill` | dm_2 | two distinct activities — never pooled with each other |
| `/hw/human_review` | hw_1 | single resource |

**Burn size-dependence check:** at `/ov/burn`, `burn_workpiece_size` is categorical and deterministic per variant (per confirmed decision). Test whether burn duration varies systematically by size category (pooling variants that share a size). If the data supports it, provide per-category distributions; otherwise fall back to the single per-activity distribution and flag the result.

**Sparsity handling:** report sample size n per group. Groups with very small n (punch activities, `/dm/lower`, `/dm/cylindrical_drill`, `/ov/temper`) get flagged, low-confidence estimates (wide CIs). No cross-activity pooling is permitted to compensate.

## 2. Failure Probabilities

- **Unified retry mechanism:** HTTP 418 (precondition) and HTTP 401 (auth) are treated as a **single** retryable failure class that triggers a re-attempt; the workpiece continues.
- **Per-activity failure rate** = failed attempts at activity / total attempts at activity (Bernoulli parameter per activity), computed over all 192 attempts (failed attempts included in the denominator, excluded from service times per §1).
- Activities with zero observed failures: rate 0, reported with a small-sample confidence bound (e.g., rule of three) rather than asserted as exactly zero.

## 3. Arrival Process (two-phase)

Per confirmed decision, model inter-arrivals as **two-phase**: an initial near-simultaneous burst followed by steady-state arrivals, as reflected in the data (two-regime IAT evidence: burst mean 1.59 s, gap mean 377.5 s).

- **Phase 1 — initial burst:** the **first 8 cases** arrive near-simultaneously. Extract the within-burst IATs (n = 7) to characterise the spread; the fit may degenerate to simultaneous arrival with a small fixed jitter, per the data.
- **Phase 2 — steady state:** IATs between cases 9–18 (n = 9). Fit a distribution.
- The case 8 → case 9 transition IAT is **excluded from both samples** (regime boundary).
- **Case arrival time** = `time:timestamp` of the `scheduled` row of the case's first activity (works for WF_104, which starts with a vgr transport rather than `/hbw/unload`).
- **All 18 cases are used**, including the 4 incomplete ones — they are retained for arrival estimation.
- Do **not** use the mixed mean IAT; do **not** model a WIP cap (release is open/bursty, no completion trigger).

## 4. Quantities / Quality

`quantity` and `workpiece_size` columns exist → extract as **per-variant deterministic parameters** (verify each variant maps to exactly one value; flag any variation within a variant):

- **quantity** (observed values 4/6/8/10): variant → quantity mapping.
- **workpiece_size** — context-dependent per confirmed decision:
  - at `/ov/burn`: **categorical** (regular/middle/large/maxi), deterministic per variant;
  - at drill steps: **numeric** (30/40/50/60).
  - Extract variant → size for each context separately; do not merge the two encodings.
- No quality/rework data beyond the retryable failures (covered in §2); no scrap (early_exit_probability = 0 for all variants).

## 5. Exclusions & Skips

| Item | Treatment | Reason |
|---|---|---|
| 8 failed attempts (418/401) | Excluded from service-time sample; used in failure-rate denominators | Failed attempt ≠ completed operation; unified retry mechanism |
| 4 incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) | **Retained** for service-time and arrival estimation; excluded from routing only | Per confirmed decision — truncation is window cut, not abandonment |
| Censored service times | None to exclude | All 192 instances have a `complete` row; no right-censored durations |
| `complete_service_time` | Skipped | Includes queueing delay — not a service time |
| `planned_operation_time` | Skipped (reference only) | Actual duration supersedes it |
| `human_workstation_green_button_pressed` | Already dropped in cleaning | Out of scope |
| Per-activity × resource splits beyond §1 pooling | Skipped | Topology shows no resource-specific behaviour within an activity; vgr handled by the single pooled distribution |

## 6. Distribution Fitting

Fit and validate (goodness-of-fit statistics + confidence intervals) for:

1. Per-activity service-time distributions (17 groups in §1).
2. Burst IAT sample (n = 7) — may degenerate to a fixed small offset / simultaneity.
3. Steady-state IAT distribution (n = 9).
4. Per-activity failure probabilities (Bernoulli, with small-sample intervals per §2).

All fits with n < 5 are flagged low-confidence in the output.

## 7. Agent Deployment Recommendation

| Sub-Agent | Deploy? | Reason |
|---|---|---|
| durations-processing-times-agent | **Yes** | Service times needed for all 20 activities; per-activity grouping with machine-pair pooling (mm/ov/wt/sm pairs, single pooled vgr distribution); failed attempts excluded; burn size-dependence check. |
| inter-arrival-times-agent | **Yes** | Two-phase arrival process: initial near-simultaneous burst (first 8 cases) + steady-state IATs (cases 9–18); small samples (n = 7 / n = 9) need careful handling; boundary IAT excluded. |
| quantities-quality-agent | **Yes** | `quantity` and `workpiece_size` columns exist; extract per-variant deterministic mappings (categorical size at `/ov/burn`, numeric at drill steps); verify within-variant determinism. |
| distribution-fitting-agent | **Yes** | Fit distributions for all 17 service-time groups, both IAT samples, and per-activity failure rates; goodness-of-fit plus small-sample confidence intervals. |

## 8. Flags for the Modeling Stage

1. **Single pooled VGR transport distribution** (vgr_1 + vgr_2) — revisit at the modeling stage (per confirmed decision).
2. **Burn duration size-dependence** — resolved by the data check in §1; per-category distributions only if supported.
3. **Small samples** — steady-state IAT (n = 9), burst IAT (n = 7), and several activity groups with n ≤ 3: low-confidence fits are flagged, not silently smoothed.
