# Extraction Plan Report — Fischertechnik Manufacturing System

## 1. Dataset Characteristics

| Property | Value |
|---|---|
| Source file | `eventlog_cleaned.parquet` |
| Total events | 576 (192 operations × 3 lifecycle events per operation) |
| Operations | 192 |
| Product variants | 9 (WF_101, WF_102, WF_103, WF_104, WF_105, WF_108, WF_109, WF_1106, WF_1107) |
| Case instances | 18 (4 incomplete due to time-window truncation) |
| Failure events | 8 (7 × HTTP 418, 1 × HTTP 401) — all retryable |
| Time window | 2021-07-06 15:10 – 16:02 UTC (~52 minutes) |
| Architecture | Two parallel processing lines (Line 1 and Line 2) with shared resources |

### Routing Sequences

The system processes 9 product variants across two parallel lines:

- **Line 1 variants:** WF_101, WF_103, WF_105, WF_109, WF_1107
- **Line 2 variants:** WF_102, WF_108, WF_1106
- **Cross-line variant:** WF_104 (Line 2 → Line 1)

All variants follow a canonical warehouse-return sequence at completion: VGR transport from human workstation to output warehouse, empty bucket retrieval, final VGR transport, and storage.

### Key Structural Notes

- **VGR role-based assignment:** `vgr_2` performs the first transport per workpiece; `vgr_1` handles all subsequent transports.
- **Sorting machine ejection:** Uniformly distributed over positions {1, 2, 3}.
- **Failure handling:** 8 failures observed; all are retryable (workpiece continues after retry). Treat HTTP 418 and 401 as a unified retry mechanism.

---

## 2. Extraction Steps

### Step 1 — Extract Processing Times (Activity × Resource Pairs)

**Source:** `actual_duration` column on `start` lifecycle transitions.

**Grouping strategy:**
- Group by `(concept:name, org:resource)` to get per-activity processing times.
- For machines performing the same activity on different lines (e.g., `mm_1` and `mm_2` both perform `/mm/mill`), pool observations **only when the activity is identical**. Never pool across different activities.
- Pooling pairs:
  - `/mm/mill`: pool `mm_1` and `mm_2` observations
  - `/mm/deburr`: pool `mm_1` and `mm_2` observations
  - `/mm/drill`: pool `mm_1` and `mm_2` observations
  - `/ov/burn`: pool `ov_1` and `ov_2` observations
  - `/sm/sort`: pool `sm_1` and `sm_2` observations
  - `/sm/transport`: pool `sm_1` and `sm_2` observations
- Do NOT pool `/ov/temper` (only `ov_1`), `/dm/lower` (only `dm_2`), `/dm/cylindrical_drill` (only `dm_2`), or any punch activities (only `pm_1`).

**Exclusions:**
- Exclude `scheduled` and `complete` lifecycle transitions — use only `start` rows.
- Exclude incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) from processing time extraction if their operations are truncated.

**Failure handling:**
- Include failed attempts in processing time extraction (they represent actual service time consumed).
- Model failure rates separately per activity (see Step 4).

**Expected output:** One processing time sample list per unique `(concept:name, org:resource)` pair, with pooled samples where applicable.

---

### Step 2 — Extract Transport Times (VGR and Work Transport)

**Source:** `actual_duration` on `start` transitions for transport activities.

**Grouping strategy:**
- **VGR transport (`/vgr/pick_up_and_transport`):** Use a single transport-time distribution per VGR resource. Pool `vgr_1` and `vgr_2` observations because they are identical hardware performing the same activity. Flag this pooling decision for revisit at the modeling stage — route-dependent distance differences may warrant separate distributions.
- **Work Transport (`/wt/pick_up_and_transport`):** Pool `wt_1` and `wt_2` observations (identical hardware, same activity).

**Exclusions:**
- Exclude `/mm/transport_from_to` from VGR pooling — it is a mill-machine internal transport, not a VGR operation.

**Expected output:** Two transport-time distributions (VGR pooled, Work Transport pooled).

---

### Step 3 — Extract Inter-Arrival Times

**Source:** `time:timestamp` on `scheduled` lifecycle transitions, grouped by `case`.

**Grouping strategy:**
- Model inter-arrivals as **two-phase**:
  1. **Initial burst phase:** The first 8 cases arrive in near-simultaneous bursts. Extract timestamps of the first 8 case arrivals and characterize the burst pattern (near-zero inter-arrival times).
  2. **Steady-state phase:** After the initial burst, extract inter-arrival times between subsequent case arrivals. Compute the time difference between consecutive case first-scheduled timestamps.

**Entity definition:** A "case arrival" is the timestamp of the first `scheduled` event for each `case` value.

**Expected output:**
- Burst phase: list of first 8 case arrival timestamps
- Steady-state phase: list of inter-arrival time samples between consecutive cases after the burst

---

### Step 4 — Extract Failure Rates (Per Activity)

**Source:** `response_status_code` column on `complete` lifecycle transitions, and `lifecycle:state` column.

**Grouping strategy:**
- Group by `concept:name` to compute per-activity failure rates.
- Treat HTTP 418 (precondition failed) and HTTP 401 (authentication failed) as a single unified failure category — both trigger a retry.
- Compute failure rate as: (number of failed attempts) / (total attempts) per activity.
- 8 failures observed across 192 operations. Most failures occur on `/vgr/pick_up_and_transport` (5 of 8) and `/hbw/store_empty_bucket` (2 of 8), with 1 on `/hbw/unload`.

**Expected output:** Failure rate per activity, with total attempt counts and failure counts.

---

### Step 5 — Extract Process Parameters (Quantities and Variants)

**Source:** Parsed parameter columns (`quantity`, `burn_workpiece_size`, `burn_workpiece_thickness`, `sorting_machine_ejection_position`).

**Grouping strategy:**
- **`burn_workpiece_size`:** Context-dependent — separate by activity:
  - At `/ov/burn`: categorical and deterministic per variant (e.g., WF_101 uses specific size/thickness). Extract as a lookup table: variant → (size, thickness).
  - At drill steps (`/mm/drill`): numeric values (30, 40, 50, 60). Extract as numeric parameter per case.
- **`quantity`:** Extract per activity where applicable (`/mm/drill`, `/pm/punch_*`, `/dm/cylindrical_drill`). Map to variant-activity pairs.
- **`sorting_machine_ejection_position`:** Uniform over {1, 2, 3}. Confirm uniformity and extract as a discrete uniform distribution parameter.
- **`burn_workpiece_thickness`:** Categorical (thin/thick). Extract as part of the variant lookup table.

**Expected output:**
- Variant parameter lookup table (variant → burn size, burn thickness)
- Quantity values per activity-variant pair
- Confirmation of uniform ejection position distribution

---

### Step 6 — Statistical Distribution Fitting

**Source:** All extracted samples from Steps 1–3.

**Fitting strategy:**
- Fit candidate distributions (exponential, Weibull, lognormal, normal, gamma) to each processing time sample set.
- Fit candidate distributions to inter-arrival times (steady-state phase only).
- Fit candidate distributions to transport times.
- Use goodness-of-fit tests (Kolmogorov-Smirnov, Anderson-Darling, AIC/BIC) to select the best-fitting distribution for each parameter.
- Flag any parameter with insufficient samples (< 5 observations) for manual review — these may require fixed-value modeling or expert estimation.

**Expected output:** Best-fitting distribution name and parameters for each extracted time parameter, with goodness-of-fit statistics.

---

## 3. What to Skip and Why

| Parameter | Decision | Reason |
|---|---|---|
| `planned_operation_time` | **Skip** | Scheduled/planned duration; not reflective of actual processing behavior. Use `actual_duration` instead. |
| `complete_service_time` | **Skip** | Includes queueing delay; not a pure service time metric. Use `actual_duration` on `start` transitions. |
| `SubProcessID` | **Skip** | 67% missing; no simulation relevance. |
| `current_task` | **Skip** | 68% missing; verbose human-readable descriptions with no simulation value. |
| `unsatisfied_condition_description` | **Skip** | 96% missing; only populated on failures. Failure rates are captured via `response_status_code`. |
| `human_workstation_green_button_pressed` | **Already dropped** | 93% missing; out of scope for DES simulation. |
| `temper_intensity` | **Skip as variable** | Always `ov_1_temper_high` — no variability. Model as a fixed parameter, not a stochastic one. |
| `use_nfc` | **Skip** | Binary flag with no observed impact on processing times or routing. |
| `hbw_slot` | **Skip** | Deterministic location parameter; no variability affecting simulation timing. |

---

## 4. Sub-Agent Deployment Table

| Sub-Agent | Deploy? | Reason |
|---|---|---|
| **durations-processing-times-agent** | ✅ **Yes** | `actual_duration` exists for all `start` transitions. Need per-activity processing times with pooling rules for identical hardware. |
| **inter-arrival-times-agent** | ✅ **Yes** | Timestamps exist for all events. Two-phase arrival pattern (burst + steady-state) requires extraction. |
| **quantities-quality-agent** | ✅ **Yes** | `quantity`, `burn_workpiece_size`, `burn_workpiece_thickness`, and `response_status_code` columns contain extractable parameters. Failure rates per activity needed. |
| **distribution-fitting-agent** | ✅ **Yes** | Required to fit statistical distributions to all extracted processing times, transport times, and inter-arrival times. |

---

## 5. Extraction Execution Order

1. **durations-processing-times-agent** — Extract processing times per activity-resource pair (Step 1) and transport times (Step 2).
2. **inter-arrival-times-agent** — Extract two-phase inter-arrival times (Step 3).
3. **quantities-quality-agent** — Extract process parameters and failure rates (Steps 4–5).
4. **distribution-fitting-agent** — Fit distributions to all extracted samples (Step 6).

Steps 1–3 are independent and can run in parallel. Step 4 (distribution fitting) depends on completion of Steps 1–3.

---

## 6. Data Quality Notes

- **Sample size warning:** With only 192 operations across 20 unique activities, many activity-resource pairs will have fewer than 10 observations. Distribution fitting results for sparse groups should be flagged for manual review.
- **Incomplete cases:** 4 cases are truncated. Their partial operations should be excluded from processing time extraction to avoid biasing duration estimates.
- **Pooling assumptions:** Pooling identical hardware (e.g., `mm_1`/`mm_2`) assumes distance-independent processing times. This should be validated at the modeling stage.
- **Failure sample size:** Only 8 failures observed. Per-activity failure rates will have wide confidence intervals. Consider modeling a single system-wide failure rate if per-activity rates are too sparse.
