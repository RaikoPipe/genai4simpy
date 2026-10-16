# Distribution Fitting Report — Fischertechnik Lab A (wandering-flying-bee)

**Data:** `work_files/eventlog_cleaned.parquet` — 576 rows, 192 activity instances (3 lifecycle rows each), 18 cases, 9 variants. Window 2021-07-06 15:08:27.91 → 16:01:31.12 UTC (~53 min).
**Scope:** review and finalisation of ALL distributions in spec sections `activities` (20 service-time distributions) and `arrivals` (2-phase burst model), plus per-activity failure probabilities.

---

## 1. Method & sample definition (verified against raw data)

- **Duration rule:** service time = `operation_end_time − time:timestamp` on the `start` row only; `complete_service_time` never used (recomputed from the cleaned log: 184 successes / 8 failures — matches spec).
- **Sample:** successful attempts only (n = 184). The 8 failed attempts (7× HTTP 418, 1× HTTP 401) are excluded from service times but **included in failure-rate denominators** (192 attempts total).
- **Incomplete cases** WF_104_21, WF_108_18, WF_109_16, WF_1107_17 are **retained** for estimation (window truncation, not abandonment).
- **Pooling:** only within same-activity machine pairs; single pooled vgr_1+vgr_2 transport distribution (confirmed decision, kept).
- **Outliers kept** (real variability, no data-defect removals): /sm/sort 245.7 s, /mm/mill 14.437 s (mm_2), /vgr 88.375 s, /hw/human_review 62.25 s.

### Fitting gate (enforced by `fit_activity_durations`; restated)

A parametric family is used **only if** all hold: N ≥ 30; theoretical mean within 15 % and std within 25 % of the empirical moments; p99 ≤ 2 × observed max; non-degenerate parameters; and the parametric-bootstrap KS test (Lilliefors-type, parameters re-estimated in every bootstrap sample) does not reject at 5 %. Otherwise the **empirical quantile table** (inverse-CDF sampling) is used, or **triangular(min, median, max)** / **constant** for N < 10. No rejected parametric fit is substituted, and no distribution is replaced by its mean — variability is preserved.

**Result: no parametric fit passed the gate.** Only /vgr (N = 50) reached the parametric branch; its best candidates (norm, lognorm, gamma, all p = 0.01 in the bootstrap KS test; triang failed the moment gate with mean error 10.8 % / std error 30 %) were all rejected → empirical quantiles. All other groups have N < 30 → bounded empirical fallbacks.

---

## 2. Activity service-time distributions (final)

All 20 spec entries were re-verified against a fresh `fit_activity_durations` run and against direct recomputation from the raw log (means, stds, min/max, quantile tables, n, failure rates — all match verbatim). **No spec changes were required.**

| Parameter | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| /dm/cylindrical_drill | ⚠️ 2 | ⚠️ triang (min, med, max) | 23.992 | 23.992 | 2.861 | 2.861 | — | N<30 → fallback |
| /dm/lower | ⚠️ 2 | ⚠️ triang | 14.008 | 14.008 | 0.188 | 0.188 | — | N<30 → fallback |
| /hbw/get_empty_bucket | ⚠️ 11 | ⚠️ empirical_quantiles | 37.062 | 37.062 | 5.038 | 5.038 | — (in-sample CDF) | N<30 → fallback |
| /hbw/store | ⚠️ 3 | ⚠️ triang | 37.985 | 37.985 | 3.951 | 3.951 | — | N<30 → fallback |
| /hbw/store_empty_bucket | ⚠️ 13 | ⚠️ empirical_quantiles | 39.429 | 39.429 | 3.852 | 3.852 | — (in-sample CDF) | N<30 → fallback |
| /hbw/unload | ⚠️ 16 | ⚠️ empirical_quantiles | 39.292 | 39.292 | 5.798 | 5.798 | — (in-sample CDF) | N<30 → fallback |
| /hw/human_review | ⚠️ 14 | ⚠️ empirical_quantiles | 13.996 | 13.996 | 19.210 | 19.210 | — (in-sample CDF) | N<30 → fallback |
| /mm/deburr | ⚠️ 9 | ⚠️ triang | 14.463 | 14.500 | 0.361 | 0.361 | — | N<30 → fallback |
| /mm/drill | ⚠️ 4 | ⚠️ triang | 14.441 | 13.992 | 6.570 | 6.570 | — | N<30 → fallback |
| /mm/mill | ⚠️ 6 | ⚠️ triang | 6.672 | 8.196 | 3.805 | 3.805 | — | N<30 → fallback (mean gap 22.8 %, see §5) |
| /mm/transport_from_to | ⚠️ 2 | ⚠️ triang | 12.868 | 12.868 | 0.387 | 0.387 | — | N<30 → fallback |
| /ov/burn | ⚠️ 13 | ⚠️ empirical_quantiles | 30.144 | 30.144 | 6.665 | 6.665 | — (in-sample CDF) | N<30 → fallback (size effect, §4) |
| /ov/temper | ⚠️ 5 | ⚠️ triang | 51.537 | 51.536 | 0.056 | 0.056 | — | N<30 → fallback (near-constant) |
| /pm/punch_gill | ⚠️ 1 | ⚠️ constant 27.484 s | 27.484 | 27.484 | 0.000 | 0.000 | — | N=1 → constant |
| /pm/punch_recesses | ⚠️ 2 | ⚠️ triang | 23.641 | 23.641 | 0.265 | 0.265 | — | N<30 → fallback |
| /pm/punch_ribbing | ⚠️ 2 | ⚠️ triang | 27.391 | 27.391 | 5.414 | 5.414 | — | N<30 → fallback |
| /sm/sort | ⚠️ 6 | ⚠️ triang | 50.146 | 88.734 | 95.827 | 95.827 | — | N<30 → fallback (outlier 245.7 s, see §5) |
| /sm/transport | ⚠️ 9 | ⚠️ triang | 17.523 | 18.073 | 3.011 | 3.011 | — | N<30 → fallback (per-resource flag, §5) |
| /vgr/pick_up_and_transport | 50 | ⚠️ empirical_quantiles | 41.965 | 41.965 | 12.795 | 12.795 | 0.01 (best of norm/lognorm/gamma) | parametric rejected → fallback |
| /wt/pick_up_and_transport | ⚠️ 14 | ⚠️ empirical_quantiles | 27.377 | 27.377 | 1.546 | 1.546 | — (in-sample CDF) | N<30 → fallback |

Notes:
- "Fit mean/std" for `empirical_quantiles` equals the empirical moments by construction (the table is the sample's own CDF; no in-sample goodness-of-fit test is meaningful, hence "—").
- For the `triang` fallbacks the fit moments are the triangular moments of (min, median, max); they equal the empirical moments except where the data is strongly skewed by an outlier (/mm/mill, /sm/sort) or the 3-point bound is coarse (/mm/deburr +0.3 %, /mm/drill −3.1 %, /sm/transport +3.1 %). These are inherent to the bounded fallback, not fitting errors; the fallbacks are the gate-mandated representation and are kept.
- ⚠️ = fallback distribution and/or N < 30 (low confidence, no smoothing applied).

### Failure probabilities (Bernoulli per activity, over all 192 attempts)

| Activity | Failed/Total | p | 95 % rule-of-three upper bound (if 0 failures) |
|---|---|---|---|
| /hbw/store_empty_bucket | 2/15 | 0.1333 | — |
| /hbw/unload | 1/17 | 0.0588 | — |
| /vgr/pick_up_and_transport | 5/55 | 0.0909 | — |
| all other 17 activities | 0/n | 0.0 | 3/n (e.g. /ov/burn 0/13 → ≤ 0.23; /hw/human_review 0/14 → ≤ 0.21; /hbw/get_empty_bucket 0/11 → ≤ 0.27) |

All `on_failure: retry` (unified retryable class, HTTP 418/401). Verified against raw log: the 8 failed attempts are exactly the 2 hbw/store_empty_bucket + 1 hbw/unload + 5 vgr above.

---

## 3. Arrivals (two-phase, final)

Recomputed from the raw log: case arrival = `time:timestamp` of the `scheduled` row of each case's first activity; all 18 cases used (incl. the 4 incomplete). 17 IATs over a 2282.23 s span; mixed mean 134.25 s **not** used. Two-regime evidence: overall CV 1.81, gap/burst ratio ≈ 237, initial 8 cases span only 6.91 s.

| Parameter | N | Recommended | Emp. mean | Fit mean | Emp. std | Fit std | KS p (bootstrap) | Gate |
|---|---|---|---|---|---|---|---|---|
| initial_burst | 1 (observed burst) | constant 8 | — | 8 | — | 0 | — | confirmed decision |
| intra_burst_iat (phase 1, cases 1–8) | ⚠️ 7 | ⚠️ empirical_quantiles | 0.987 | 0.987 | 0.426 | 0.426 | — (in-sample CDF) | N<30 → fallback |
| inter_burst_gap (phase 2, cases 9–18) | ⚠️ 9 | ⚠️ empirical_quantiles | 182.426 | 182.426 | 261.842 | 261.842 | — (in-sample CDF) | N<30 → fallback |
| burst_size (steady state) | ⚠️ 9 | categorical [1] p=1.0 | — | 1 | — | 0 | — | each steady-state arrival is its own burst |

- Phase-1 IATs (n=7): [0.906, 1.656, 1.485, 0.641, 0.813, 0.510, 0.896] s — near-simultaneous release with small jitter; the 11-point quantile table in the spec matches the recomputed quantiles verbatim.
- Phase-2 IATs (n=9): [799.957, 317.875, 2.359, 139.110, 0.687, 93.406, 5.531, 2.000, 280.906] s; quantile table matches verbatim. The 799.96 s IAT (case 9→10) is retained — only the **case 8→9 boundary IAT (633.497 s) is excluded**, per the confirmed decision.
- Release rule is **open** (no WIP cap, `completion_triggered: false`) → `two_regime_bursts` without `wip_cap`, consistent with `control_policies`.
- Parametric fits (e.g. lognormal on the 9 gaps) are unstable at n = 7/9; per policy no smoothing is applied — the empirical quantile tables are the honest representation. Both phases are **low confidence** (⚠️): phase-1 jitter 0.99 ± 0.43 s; phase-2 mean 182.4 s with CV 1.44, upper tail dominated by the single 799.96 s IAT.

---

## 4. Burn size-dependence decision (/ov/burn)

`burn_workpiece_size` is categorical and deterministic per variant (verified in quantities report). Burn duration is **strongly and monotonically size-dependent** with non-overlapping ranges:

| size | n | mean (s) | std (s) | min–max (s) |
|---|---|---|---|---|
| regular | 5 | 23.547 | 2.712 | 21.422–26.563 |
| middle | 2 | 29.369 | 3.500 | 26.894–31.844 |
| large | 3 | 33.301 | 2.920 | 31.562–36.672 |
| maxi | 3 | 38.500 | 2.842 | 36.859–41.782 |

**Decision: keep the single pooled per-activity distribution (n = 13, empirical quantiles, mean 30.14 s) in the spec.** Rationale:
1. Per-category samples are n = 2–5 — below every parametric threshold and too small for reliable quantile tables; splitting would force exactly the silent smoothing the policy forbids.
2. The pooled empirical quantile table already spans the full 21.4–41.8 s range and contains the four non-overlapping size blocks, so a simulation drawing from it reproduces the size-driven spread (a workpiece of a given size will land in its block only if the size is also modelled — see flag below).
3. The confirmed decision requires the spec to stay consistent with this choice; it does (single `/ov/burn` entry, no per-category entries).

**Flag for the modeling stage:** to make the size effect *exact* rather than statistical, the model should condition burn duration on the (deterministic per-variant) size category — e.g. per-category constants/means (23.5 / 29.4 / 33.3 / 38.5 s) or per-category mini-distributions once more data exists. Thickness (thin/thick) adds a secondary within-size effect but has too few points to model separately. The ov_1 (27.2 s, n=8) vs ov_2 (34.9 s, n=5) per-resource gap is **confounded with size** (ov_2 handles the larger pieces), not a machine difference — pooling ov_1+ov_2 is correct.

---

## 5. Consistency checks & flags carried forward

1. **/sm/transport per-resource difference (exception to pooling):** sm_1 19.92 s (n=5) vs sm_2 14.53 s (n=4), ≈ 37 % apart. The pooled triang (mean 17.52 s) is kept per the confirmed pooling decision; a per-resource split is recommended at the modeling stage.
2. **/mm/mill mm_2 outlier:** mm_1 ≈ 5.0–5.3 s (n=5) vs a single mm_2 observation of 14.437 s; the pooled mean (6.67 s) and the triang fit mean (8.20 s) are both inflated. Kept per outlier policy; flagged for the modeling stage.
3. **/sm/sort outlier:** 245.7 s (WF_108_17) ≈ 10× the other five (8.4–14.0 s). Kept; the bounded triang captures the long tail (fit mean 88.7 s vs empirical 50.1 s — a known consequence of the 3-point bound with an extreme max; flagged, not "fixed").
4. **VGR pooled transport (confirmed decision, kept):** vgr_1 n=32 mean 42.64 s (std 15.8, range 13.1–88.4, includes 5 failed-attempt retries) vs vgr_2 n=18 mean 40.76 s (std 3.7, tighter). Single pooled empirical-quantile distribution (n=50) retained; revisit at the modeling stage.
5. **Machine-pair poolability verified:** /mm/deburr mm_1 14.49 (n=8) vs mm_2 14.24 (n=1) — consistent; /wt wt_1 26.09 (n=8) vs wt_2 29.09 (n=6) — consistent; /ov/burn — see §4.
6. **/ov/temper** is near-constant (CV 0.001, 51.45–51.61 s) — triang fallback is effectively a tight constant; fine as-is.
7. **/hw/human_review** is human-paced (CV 1.37, 0.44–62.25 s); empirical quantiles preserve the heavy right tail.
8. **Arrival boundary:** in simulation the steady state starts after one gap drawn from the phase-2 distribution (which includes 799.96 s), not after the observed 633.5 s boundary IAT — documented, accepted.
9. **Spec consistency:** `activities` (20 entries), `arrivals`, `control_policies.release_rule` ("open"), `initial_state` (WIP 0, 4 incomplete cases retained for estimation), and `assumptions` (duration rule, sample definition, pooling, burn size-dependence, outlier policy) are all mutually consistent. No case ids or timestamps appear as model inputs.

---

## 6. Finalisation

- **Spec `activities`:** verified verbatim against `fit_activity_durations` and raw-data recomputation — **no changes made** (all families, params, quantile tables, means, n, sources, failure probabilities correct).
- **Spec `arrivals`:** verified verbatim against recomputed phase-1/phase-2 IATs — **no changes made**.
- All distributions are gate-compliant bounded empirical fallbacks (no parametric fit passed the gate); variability is preserved; no outliers removed; no smoothing applied. Low-confidence groups (N < 30, all of them) are flagged above rather than silently smoothed.
