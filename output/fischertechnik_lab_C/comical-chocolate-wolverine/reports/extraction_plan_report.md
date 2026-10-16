# Extraction Plan — fischertechnik_lab_C

**Phase 3 — Parameter Extraction Plan**
Window: `2021-07-01 18:48:23.227 → 20:19:24.734 UTC` (horizon ≈ 5,461.5 s)
Data: 1,137 rows → 379 activity instances, 37 cases, 9 variants, 21 activities, 15 resources (lifecycle layout: `scheduled` → `start` → `complete`).

---

## 1. Confirmed Decisions (inputs to this plan)

1. **`/ov/burn`**: use the ACTUAL observed mean (~31 s), NOT the planned value (222 s) — digital twin of actual behavior.
2. **Arrivals**: a SINGLE GLOBAL arrival process (one order stream into `hbw`); the process models are interleaved draws from that one stream, split by process-model proportions.
3. **Rework (general quality mechanism)**: a probabilistic branch after human review for every variant that includes a human-review step. `WF_104` is REMOVED from the arrival mix and modeled as the post-review rework branch (failed review → rework loop → terminal `/hbw/store`).
4. **Rework branch probability**: `p_rework = 1/17 ≈ 0.059` of human-review completions — documented as a small-sample estimate.
5. **`/hbw/unload` 0.03 s outlier**: data error — excluded from the fit.
6. **Truncated cases**: the 19 missing-data stubs (non-terminal, no complete/failure) are excluded from the process model, but their completed steps are kept for duration fits; the 5 real scrap cases (ending in failure state) are kept as early exits.

---

## 2. Agent Deployment Recommendation

| Sub-Agent | Deploy? | Reason |
|---|---|---|
| durations-processing-times-agent | **Yes** | Start/end timestamps exist for all 379 instances (100% coverage, `end_missing = 0`); service times are needed for all 21 activities. |
| inter-arrival-times-agent | **Yes** | A single global arrival stream into `hbw` must be extracted from the 37 release timestamps; the release process is open and bursty (12 bursts), so the burst/gap structure must be fitted rather than a single mean IAT. |
| quantities-quality-agent | **No** | No quantity or quality columns exist in the log (one workpiece per case; no defect/quantity flags — the 5 failures are transport/NFC errors, not quality defects). The only quality parameter (rework probability) is already fixed by confirmed decision (`p_rework = 1/17`); there is nothing to extract. |
| distribution-fitting-agent | **Yes** | Always required: fit and review distributions for per-activity service times, the burst/gap inter-arrival process, and the rework branch; handle outliers, zero durations, and small-sample activities. |

---

## 3. Extraction Plan

### 3.1 Service times (per activity)

- **Measure**: duration = `operation_end_time` − start-row timestamp, evaluated on the **`start` row only** (authoritative; the <30 s per-row drift on 2 late `complete` rows is logging noise).
- **Grouping strategy: per activity only (21 activities).** Pool across track instances (`ov_1/ov_2`, `mm_1/mm_2`, `wt_1/wt_2`, `sm_1/sm_2`) and across the shared `hbw_1/2`, `vgr_1/2` instances. No per-activity × resource split is justified: the topology shows no resource-specific service-time behaviour — all machine classes (ov/mm/wt/sm/dm/pm/hw) show 100% extraneous waiting (no resource contention), and `hbw`/`vgr` form a single shared pool. The hbw priority-queue behaviour affects *waiting*, not service duration, and is captured by the control policy, not by duration fits.
- **Included**: all 379 start rows — including completed steps from the 19 missing-data stubs and the 5 scrap cases (valid service observations).
- **Excluded**: the `/hbw/unload` 0.03 s outlier (data error).
- **Special handling**:
  - `/ov/burn`: fit to observed values (mean ≈ 31 s, max ≈ 41.5 s); the planned 222 s is NOT used (digital twin of actual behavior).
  - 2 zero-duration `/hw/human_review` starts: kept as-is (instant hand-off events), flagged for the distribution review.
- **Small-sample caveat**: several activities have few observations (e.g. `/ov/temper`, `/pm/punch_recesses`, `/pm/punch_ribbing`, `/dm/lower`, `/dm/drill`, `/dm/cylindrical_drill`) — their fits must be reported as low-confidence estimates.

### 3.2 Arrival process (single global stream)

- **Release time per case** = timestamp of the `scheduled` row of `/hbw/unload` (37 releases; all cases including the 19 stubs — they are real orders released into the system, so they belong in the arrival stream).
- **Structure**: open, bursty releases — 12 bursts (mean size 3.08, range 1–9), within-burst IAT mean ≈ 1.97 s, between-burst gaps mean ≈ 418.8 s (gap:burst IAT ratio ≈ 212). Fit the **burst/gap (two-phase) process**; do not collapse to a single mean IAT.
- **Variant mix** (interleaved draws from the single stream): `WF_104` removed; proportions renormalized over the 34 non-WF_104 cases:

| Variant | Proportion |
|---|---|
| WF_101 | 0.1176 |
| WF_102 | 0.1471 |
| WF_103 | 0.1471 |
| WF_105 | 0.1176 |
| WF_108 | 0.0882 |
| WF_109 | 0.0882 |
| WF_1106 | 0.1765 |
| WF_1107 | 0.1176 |

### 3.3 Quality / rework (no extraction — fixed by confirmed decision)

- `p_rework = 1/17 ≈ 0.059` of `/hw/human_review` completions → rework branch (documented as a small-sample estimate).
- Applies to **every variant with a human-review step** (all 8 arrival variants).
- **Rework loop** = the observed WF_104 rework sequence (T2 → T1 → T2 round-trip: `ov/burn → wt → mm/deburr → sm/transport → pm/punch_gill → vgr → human_review → vgr → store_empty_bucket → ov/burn → wt → mm/mill → sm/sort → vgr ×3`), terminated by an explicit `/hbw/store` (mirroring the main-flow terminal).
- WF_104 case data (the 16-step scrap case + 2 stubs) contributes to duration fits of the rework-loop activities; it is **not** used in the arrival mix.

### 3.4 Distribution review

- Fit candidate distributions to: (a) per-activity service times, (b) within-burst IAT and between-burst gaps, (c) report `p_rework` as a fixed probability (no fit — small-sample estimate).
- Review and document: the `/hbw/unload` 0.03 s outlier (excluded), the 2 zero-duration `human_review` starts, the `/ov/burn` observed-vs-planned gap (222 s planned vs ≤ 41.5 s observed), and the small-sample activities listed in §3.1.
- Report fit quality and confidence per parameter.

---

## 4. What is skipped, and why

- **quantities-quality-agent**: no quantity/quality columns exist in the log, and the rework probability is already fixed by confirmed decision — nothing to extract.
- **Per-activity × resource duration grouping**: no evidence of resource-specific service-time behaviour in the topology (no machine contention; single shared hbw/vgr pool) — per-activity grouping suffices.
- **Planned operation times**: used only as a calibration cross-check, not as parameters (observed data exists for every activity).
- **`complete_service_time`**: not used for service durations (it includes queueing); queueing is represented by the queue disciplines (hbw priority: `store_empty_bucket` > `unload`; vgr FIFO) and the burst/gap arrival process.
