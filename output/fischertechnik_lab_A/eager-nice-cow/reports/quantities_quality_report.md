# Quantities & Quality Report — fischertechnik_lab_A (run: eager-nice-cow)

## 1. Scope

- **Task T3 (binding):** extract the `quantity` column (workpiece count) and summarize its distribution; sparse → simple discrete fit, flagged.
- **Quality extraction: SKIPPED** (rationale in §5).
- Data: `work_files/eventlog_cleaned.parquet` (576 rows, 192 instances, 18 cases).
- The 4 incomplete cases (`WF_104_21`, `WF_108_18`, `WF_109_16`, `WF_1107_17`) are **retained** for this extraction per the binding rule; none of their observed activities carries the `quantity` parameter, so they contribute 0 observations.

## 2. Quantity Distribution

### 2.1 Observed sample

- **33 rows** of 576 carry `quantity` — these are **11 activity instances × 3 lifecycle rows** (`scheduled`/`start`/`complete` carry the identical value per instance). Distinct instances: 11; distinct cases: 10 of 18.
- **Range: 4–10** (note: the extraction plan stated 3–10, but no value 3 occurs in the data; observed range 4–10 is used).
- Values are even integers only: {4, 6, 8, 10}.

| quantity | count | share |
|---|---|---|
| 4 | 9 | 0.2727 |
| 6 | 18 | 0.5455 |
| 8 | 3 | 0.0909 |
| 10 | 3 | 0.0909 |
| **total** | **33** | 1.0 |

- Mean 6.00, std 1.73, median 6.0, Q25 4.0, Q75 6.0.
- No outliers flagged (IQR method, k=3); nothing removed.

### 2.2 Where quantity appears (per activity / resource)

| Activity | Resource | Instances | Quantity |
|---|---|---|---|
| `/mm/drill` | mm_2 (3), mm_1 (1) | 4 | 4 or 6 (WF_108→4, WF_102/WF_109-class→6, WF_1107→6) |
| `/pm/punch_recesses` | pm_1 | 2 | 6 (WF_103) |
| `/pm/punch_gill` | pm_1 | 1 | 8 (WF_104) |
| `/pm/punch_ribbing` | pm_1 | 2 | 6 (WF_109), 10 (WF_1107) |
| `/dm/cylindrical_drill` | dm_2 | 2 | 4 (WF_1106) |

Quantity is attached only to **material-removal steps** (drill / punch / cylindrical_drill) — not to transports, burn, temper, sort, review, or bucket handling.

### 2.3 Key structural finding: quantity is deterministic per variant/step

Within every variant (and within every case, except WF_1107_16 which legitimately has two different quantities on two different steps: 6 at `/mm/drill`, 10 at `/pm/punch_ribbing`), the quantity is **constant**:

| Variant | Step(s) with quantity | Quantity |
|---|---|---|
| WF_102 | `/mm/drill` | 6 |
| WF_103 | `/pm/punch_recesses` | 6 |
| WF_104 | `/pm/punch_gill` | 8 |
| WF_108 | `/mm/drill` | 4 |
| WF_109 | `/pm/punch_ribbing` | 6 |
| WF_1106 | `/dm/cylindrical_drill` | 4 |
| WF_1107 | `/mm/drill` / `/pm/punch_ribbing` | 6 / 10 |

No stochastic variation is observed at all — the "distribution" is a degenerate per-variant constant.

## 3. Candidate Discrete Fit

Per the binding rule (sparse → simple discrete fit, flagged):

1. **Recommended (deterministic per-variant step attribute):** model quantity as a fixed parameter of the variant/step as in the table above. This matches the data exactly (zero unexplained variance) and is the most defensible given 11 instances.
2. **Fallback (if a single pooled discrete distribution is required):** empirical PMF over the observed support {4, 6, 8, 10}: **P(4)=0.273, P(6)=0.545, P(8)=0.091, P(10)=0.091**.
3. **Discrete uniform over observed range {4,6,8,10}: rejected.** Chi-square = 18.27 (df=3, p ≈ 0.0005); value 6 dominates (18/33) far above the uniform expectation of 8.25. A uniform over 4..10 (7 values) is even worse (chi2 = 56.73, df=6).

**Sparsity flag:** n = 33 rows / 11 instances total, and **n < 5 per variant** (1–2 instances each). Any pooled fit carries wide uncertainty; the deterministic per-variant assignment is strongly preferred.

## 4. Quality Extraction — SKIPPED (explicit rationale)

Quality extraction is **skipped** for this run:

- **No quality columns exist** in the log: there are no scrap, rework, defect, or inspection-outcome columns (verified against the column mapping report and the cleaned schema — 22 columns, none quality-related).
- **All 8 failures are retryable with eventual success** (418 ×7 precondition, 401 ×1 auth; unified retry mechanism per the extraction plan). Every failed attempt is re-queued as a new attempt on the same activity/resource and the workpiece continues along its routing.
- Consequently **there is no quality yield to extract**: no workpiece is ever scrapped or reworked, and the 15 window-truncated cases are truncation artifacts, not scrap. No scrap/rework/quality parameters are modelled.

## 5. Assumptions Recorded (autonomous-mode resolutions)

1. The 33 quantity rows are 11 instances × 3 lifecycle rows (value identical per instance); instances, not rows, are the sampling unit for the distribution.
2. The extraction plan's stated range 3–10 is corrected to the observed 4–10 (no 3 present).
3. Quantity is attached only to material-removal steps (drill/punch/cylindrical_drill); steps without the parameter are not treated as quantity=1 or quantity=0 — the parameter is simply absent for those steps.
4. Deterministic per-variant/step quantity is the recommended model; the empirical discrete PMF over {4,6,8,10} is the flagged fallback.
5. The 4 incomplete cases were retained but contribute no quantity observations (their observed steps carry no quantity parameter).
6. Quality yield is not extracted (no scrap exists in this log); if rework quality is needed later, it is out of scope for this run.
