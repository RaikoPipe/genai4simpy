# Extraction Plan Report — fischertechnik_lab_B (significant-hilarious-cuscus)

## 1. Scope & Data Basis

- **Data**: cleaned event log — 1,383 rows, 461 activity instances, 38 cases (workpieces), 20 activities, 15 resources (all capacity 1), 9 process-model variants, window ≈ 5,944 s (~99 min).
- **Duration convention**: actual service duration = end − start taken on the `start` row only (mean 30.4 s, min 0.0 s, max 218.7 s). `complete_service_time` (scheduled→complete, incl. queueing; mean 73.6 s) is a reference metric only — **never** used as service duration.
- **Censoring**: none for durations (end_missing = 0; every instance has a complete row). The 24 early-exit cases stop *after* a completed activity, so no censored service times.
- **Excluded cases** (truncation artifacts — terminal failure, no recovery): WF_102_16, WF_102_17, WF_104_9. Excluded from failure-probability and routing estimation; **included in arrival estimation** (their releases are real system inputs).

## 2. Agent Deployment Recommendation

| Sub-Agent | Deploy? | Reason |
|---|---|---|
| durations-processing-times-agent | **Yes** | 461 instances with full start/end pairs; service times per activity-resource, planned durations, and failure/retry parameters all extractable. |
| inter-arrival-times-agent | **Yes** | 38 releases under open (bursty) release control; two-regime gap/burst process must be extracted and fit. |
| quantities-quality-agent | **No** | No quantity or quality columns exist in the log (no batch sizes, defect counts, or inspection-result columns). Scrap/quality-gate behavior is already captured by the topology's early-exit statistics. |
| distribution-fitting-agent | **Yes** | Distribution review is always required: service times, arrival gaps, burst sizes, within-burst IAT, and retry delays all need fitted distributions with goodness-of-fit checks. |

## 3. Extraction Plan per Agent

### 3.1 durations-processing-times-agent

**A. Actual service times**
- Source: `start` rows only; duration = end − start.
- **Grouping strategy**: start at **activity × resource** level. For high-volume activities, test whether duration genuinely differs across resources and **split only where the difference is real and measurable**; otherwise pool to activity level. High-volume activities to check:
  - `/vgr/pick_up_and_transport` (127 instances; vgr_1 = in-process transport vs vgr_2 = initial pick-up — different roles, likely different durations),
  - `/ov/burn` (ov_1 vs ov_2 — different ovens; burn size/thickness parameters differ),
  - `/mm/mill` (mm_1 vs mm_2),
  - `/wt/pick_up_and_transport` (wt_1 vs wt_2),
  - `/hbw/store_empty_bucket` (hbw_2 only — no split possible).
- **Low-sample combos (n < 10)**: pool within resource class (e.g. mm_1+mm_2, ov_1+ov_2, wt_1+wt_2, sm_1+sm_2, vgr_1+vgr_2, hbw_1+hbw_2) rather than estimating per-resource.
- **Successful vs. failed instances**: build the service-time distribution from the 452 successful instances; record the 9 failed attempts' durations separately (failed attempts may run differently and feed the failure/retry model, not the nominal service distribution).
- **Data notes**: min duration is 0.0 s — flag zero/near-zero instances (possible instantaneous hand-off steps) before fitting; `/hw/human_review` (30 instances) is human-driven and expected to be high-variance.

**B. Planned durations (separate set)**
- Parse `planned_operation_time` (22 distinct values, 5–222 s) per activity as a **separate planned-duration set** for comparison/validation against actuals (ratio actual/planned per activity; flag activities where actuals systematically deviate from plan).

**C. Failure & retry parameters (explicit — do not defer to manual modeling)**
- **Failure probability per activity × resource**: failed instances / total instances, estimated from the 6 retryable failures only (the 3 excluded terminal failures are truncation artifacts and are **not** used for failure-rate estimation):
  - `/wt/pick_up_and_transport` on wt_1: 4 failed attempts (WF_104_8 ×2 consecutive, WF_109_6, WF_1107_7),
  - `/hbw/store_empty_bucket` on hbw_2: 2 failed attempts (WF_102_15, WF_104_8) — **no retry instance** (transient fault absorbed; case continued) → model as failure-without-retry.
- **Retry delay**: for each retryable failure, delay = start of the retry instance − complete of the failed instance (wt_1: 3 retry events, incl. one double-retry chain in WF_104_8).
- All other activity × resource combos: failure probability = 0 (no failures observed).

### 3.2 inter-arrival-times-agent

- **Population**: all **38 released cases, including the 3 excluded failure-only cases** — arrivals are real system inputs regardless of outcome.
- Release time per case = timestamp of the `scheduled` row of the first activity (`/hbw/unload`).
- **Two-regime process** (per release-control analysis — do **not** model the mixed mean IAT of 140.3 s, cv 2.0):
  - **Gaps** between bursts: 13 gaps (mean 394.7 s, median 294.1 s) — extract the gap process,
  - **Burst sizes**: 14 bursts (size 1–9, mean 2.7) — extract the discrete size distribution,
  - **Within-burst IAT**: burst IATs (mean 2.44 s, median 1.44 s) — extract the short-interval process.
- Output: the three component samples (gaps, burst sizes, within-burst IAT) for the distribution-fitting agent.

### 3.3 quantities-quality-agent — skipped

No quantity or quality columns exist in the log (verified against the column mapping: no batch/quantity fields, no defect or inspection-result columns; `parameters` carries only routing detail such as positions, hbw slot, burn size/thickness). Scrap at the quality gate is already quantified by the topology (24 early exits, mostly at/after `/hw/human_review`, with per-variant `early_exit_after` probabilities in the spec) — no further extraction is needed.

### 3.4 distribution-fitting-agent

Fit and validate distributions for every extracted parameter:
1. **Service times** — per activity (or per split activity × resource where the durations agent confirmed a real difference); candidate families to review (e.g. lognormal, gamma, Weibull, constant); report recommended distribution + parameters + goodness-of-fit.
2. **Arrival gaps** — candidate families for the long inter-burst gaps (e.g. exponential, lognormal, gamma).
3. **Burst sizes** — discrete distribution (e.g. geometric/Poisson/empirical).
4. **Within-burst IAT** — short-interval process (e.g. exponential).
5. **Retry delays** — small sample (3 events); report empirical values; fit only if a distribution is defensible, otherwise recommend fixed/empirical values.
6. **Planned vs. actual comparison** — per-activity ratio and deviation statistics for validation (planned set from 3.1-B).

## 4. Exclusions & Skips (summary)

| Item | Decision | Why |
|---|---|---|
| WF_102_16, WF_102_17, WF_104_9 | Excluded from failure-probability estimation; **included** in arrivals | Terminal failures with no recovery = truncation artifacts; releases are still real inputs. |
| 9 failed instances | Kept; durations recorded separately from the 452 successful ones | Real factory behavior; feed failure/retry model, not nominal service distribution. |
| `complete_service_time` | Not used as service duration | Includes queueing (mean 73.6 s vs 30.4 s actual service). |
| Quantities/quality extraction | Skipped | No such columns in the log; early-exit statistics already in spec. |
| Censored durations | None to handle | end_missing = 0; early exits occur after completed activities. |

## 5. Data Notes for Sub-Agents

1. Duration convention is start-row-based (end − start on `start` rows); do not use `complete`-row timestamps or `complete_service_time` for service times.
2. One missing value in `parameters` (on a `complete` row) — irrelevant to extraction.
3. Two instances have 2 distinct end values across their rows — negligible, no action.
4. `/hbw/store_empty_bucket` failures (hbw_2) have **no** retry instance — model as failure-without-retry (process absorbs the fault), distinct from wt_1 retry-on-same-resource.
5. hbw queue is priority-based (store > get_empty_bucket > store_empty_bucket > unload) and vgr is FIFO — relevant context for interpreting waiting times, but queue discipline is already in the spec and needs no extraction.
