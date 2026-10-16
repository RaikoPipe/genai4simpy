# Extraction Plan — fischertechnik_lab_A (run: eager-nice-cow)

## 1. Data Basis

- Source: `work_files/eventlog_cleaned.parquet` — 576 rows, 192 activity instances × 3 lifecycle transitions (`scheduled` → `start` → `complete`), 18 cases, 9 variants, 20 activities, 15 resources.
- Window: 2021-07-06 15:08:27.91 → 16:01:31.12 UTC (~53 min).
- Outcomes: 184 success / 8 failure (418 ×7 precondition, 401 ×1 auth).
- **Duration rule (binding):** actual service time = `operation_end_time` − `time:timestamp` on **`start` lifecycle rows only**. `complete_service_time` includes queueing and is never used as service time.
- **Attempt semantics (binding):** one `event_id` = one attempt; a `complete` row is terminal for that attempt; a retry is a new `event_id` repeating the same activity on the same resource. 418 and 401 are a **single unified retry mechanism** (operation retries and eventually succeeds; workpiece continues; no scrap).

## 2. Extraction Tasks

### T1 — Service (processing) times per activity
- Extract actual durations for all 192 instances using the duration rule above.
- **Grouping:** per activity, pooling machine pairs of the same class that perform the *same* activity (e.g., `ov_1`+`ov_2` for `/ov/burn`; `mm_1`+`mm_2` for `/mm/mill`). **Never pool across different activities** (`/mm/mill` ≠ `/mm/deburr` ≠ `/mm/drill`; `/ov/burn` ≠ `/ov/temper`; `/hbw/unload` ≠ `/hbw/store`, etc.).
- **Exception — VGR transports:** one transport-time distribution **per VGR resource** (`vgr_1`, `vgr_2` separately), pooling identical hardware within each resource. *Flag for revisit at the modeling stage* (vgr_2 serves early transports, vgr_1 the back half + terminal tail; distance profiles may differ).
- **Failure handling:** failed attempts (418/401) are **excluded from service-time samples** (they are short precondition/auth failures, not full service); they are used only for T4 (per-activity failure rates).
- **`workpiece_size` dependence:**
  - `/ov/burn`: `burn_workpiece_size` is **categorical and deterministic per variant** (regular/middle/large/maxi). Check duration by size class; if duration is (near-)constant within a class, model deterministic per class; otherwise fit a distribution per class.
  - Drill steps (`/mm/drill`, `/dm/cylindrical_drill`): `burn_workpiece_size` is **numeric** (30–60). Test correlation with duration; if material, group by size band; otherwise pool.

### T2 — Arrival process (two-phase)
- Model as **two phases**, as reflected in the data:
  1. **Initial burst:** first 8 cases arrive near-simultaneously at window start (extract burst size and within-burst spacing).
  2. **Steady-state arrivals:** remaining 10 releases; extract inter-arrival times for the steady-state process.
- Do **not** fit a single mixed IAT across both phases.
- Note: 18 releases in one ~53-min window is a small base; flag parameter uncertainty for the modeling stage.

### T3 — Quantities (quality: skipped)
- Extract the `quantity` column (workpiece count, 3–10, present in 33/576 rows) and summarize its distribution (sparse → simple discrete fit, e.g., discrete uniform over the observed range, flagged).
- **Quality extraction skipped:** no scrap/rework/quality columns exist; all 8 failures are retryable with eventual success, so there is no quality yield to extract.

### T4 — Failure / retry rates
- Compute **per-activity failure rates** treating 418 and 401 as one unified retry mechanism (pooled per activity): failed attempts / total attempts per activity.
- Observed failures concentrate in `/hbw/store_empty_bucket`, `/vgr/pick_up_and_transport`, `/hbw/unload` (8 failures total). Activities with zero observed failures get rate 0 (flag: small-sample).
- These rates drive the retry loop in the simulation (failed attempt → re-enqueue same activity as a new attempt).

### T5 — Distribution fitting & review
- Fit candidate distributions to every extracted sample (service times per activity, per-VGR transport times, burst + steady-state IATs, quantity, size-class burn durations).
- Review fit quality per sample; flag all samples with n < 5 for conservative treatment at the modeling stage.
- `planned_operation_time` may be used as a sanity reference only (actuals supersede).

## 3. Agent Deployment Recommendation

| Sub-Agent | Deploy? | Reason |
|---|---|---|
| durations-processing-times-agent | **Yes** | Start/end times exist for all 192 instances. Extracts: per-activity service times (same-activity machine-pair pooling), per-VGR-resource transport times (vgr_1, vgr_2), size-class-dependent `/ov/burn` durations, numeric-size check at drill steps, per-activity failure rates (418+401 unified). |
| inter-arrival-times-agent | **Yes** | Always required. Extracts: two-phase arrival process — initial near-simultaneous burst (first 8 cases: size + spacing) and steady-state IAT distribution (remaining 10 releases). |
| quantities-quality-agent | **Yes (quantity only)** | `quantity` column exists (33 rows, 3–10) → extract its distribution. Quality extraction skipped: no quality/scrap columns; failures are retryable with eventual success. |
| distribution-fitting-agent | **Yes** | Always required. Fits and reviews all extracted samples; flags sparse samples (n < 5) and small-sample failure rates for the modeling stage. |

## 4. Grouping / Pooling Decisions (summary)

1. **Service times:** per activity; pool only machine pairs of the same class performing the *same* activity (ov_1/ov_2, mm_1/mm_2, sm_1/sm_2, wt_1/wt_2; hbw activities are already resource-exclusive per activity). Never pool across activities.
2. **VGR transports:** one distribution per VGR resource (`vgr_1`, `vgr_2`); flagged for revisit at the modeling stage.
3. **`/ov/burn`:** separate by categorical size class (deterministic per variant); verify constancy within class.
4. **Drill steps:** numeric size — correlation test before deciding on size-band grouping.
5. **Arrivals:** two-phase split (initial 8-case burst vs steady state); no pooled single IAT.
6. **Failures:** 418 + 401 pooled into one per-activity retry rate; failed attempts excluded from service-time samples.

## 5. Exclusions & Censoring

- **Failed attempts (8):** excluded from service-time samples; retained for failure-rate estimation.
- **4 incomplete cases** (`WF_104_21`, `WF_108_18`, `WF_109_16`, `WF_1107_17`): excluded from **routing inference only** (already handled in the topology phase); **retained** for duration, arrival, quantity, and failure-rate extraction — their observed steps are complete service observations.
- **`complete_service_time`:** never used as service time (includes queueing).
- **`human_workstation_green_button_pressed`:** dropped in cleaning; out of scope.
- **WF_104_20:** `missing_first_activity` (unload predates window); its observed steps are used normally.

## 6. Data Sufficiency Notes

- 192 instances over 20 activities ≈ 9.6 samples/activity on average. Class-level instance counts: vgr 55, hbw 46, mm 21, ov 18, sm 15, wt 14, hw 14, pm 5, dm 4.
- **Sparse (flag for modeling stage):**
  - `dm` class: only 4 instances across 2 activities (~2 each: `/dm/lower`, `/dm/cylindrical_drill`).
  - `pm` class: 5 instances across 3 activities (~1–2 each: `/pm/punch_recesses`, `/pm/punch_gill`, `/pm/punch_ribbing`).
  - `/hbw/store`: only ~3 observed instances (terminal activity, present only in the 3 complete cases).
  - `/mm/transport_from_to`: ~2 instances (WF_1106 only).
  - For n < 5: fit with wide confidence, fall back to `planned_operation_time`-informed reference values, and flag.
- **Quantity:** only 33 observations → simple discrete fit, flagged.
- **Failure rates:** 8 failures total → per-activity rates are small-sample; the unified 418/401 pooling helps; consider a global fallback rate for activities with zero observed failures.
- **Arrivals:** 18 releases in one window → burst/gap parameters carry wide uncertainty; flagged.
- **Window truncation:** 15 of 18 cases are window-truncated (not scrap); this does not bias service-time extraction (all observed steps are complete attempts) but limits terminal-activity and full-case observations.

## 7. Recorded Assumptions (autonomous-mode resolutions)

1. Failed attempts are excluded from service-time samples because they are short precondition/auth failures, not full service; the retry cost is captured by the per-activity failure rate + re-attempt loop.
2. `wt` transports are pooled across `wt_1`/`wt_2` per activity (no resource-specific behaviour observed; the per-resource rule was specified for VGR only).
3. `hbw` activities need no cross-resource pooling because each hbw activity is served by exactly one resource in the observed routings (hbw_2: unload/store_empty_bucket; hbw_1: get_empty_bucket/store).
4. The two-phase arrival split point is the first 8 cases (per ground truth), not a data-driven regime change.
5. Quality yield is not extracted (no scrap exists in this log); if rework quality is needed later, it is out of scope for this run.
