# Quantities & Quality Report — Fischertechnik Lab A (wandering-flying-bee)

**Data:** `work_files/eventlog_cleaned.parquet` — 576 rows, 192 activity instances (3 lifecycle rows each), 18 cases, 9 variants. Parameters parsed from the `parameters` column (nested `{'value': None, 'children': [(name, value), ...]}` structure): `parameter_quantity` (33 rows → 11 instances), `parameter_burn_workpiece_size` (57 rows → 19 instances), `parameter_burn_workpiece_thickness` (39 rows → 13 instances). Values are identical across the 3 lifecycle rows of every instance (verified: 0 instances with within-instance variation), so all mappings below are checked at instance level and per variant × case.

Per confirmed decision, `quantity` and `workpiece_size` are extracted as **per-variant deterministic parameters** with within-variant variation flagged. The two `workpiece_size` encodings (categorical at `/ov/burn`, numeric at drill steps) are extracted **separately and never merged**.

---

## 1. Quantity (per variant, deterministic)

`parameter_quantity` appears **only at feature-processing steps** (drill/punch) — the steps that process multiple features. Observed values: 4, 6, 8, 10.

| Variant | Step where observed | Quantity | Cases observed | Deterministic? |
|---|---|---|---|---|
| WF_102 | `/mm/drill` | 6 | 2/2 | Yes |
| WF_103 | `/pm/punch_recesses` | 6 | 2/2 | Yes |
| WF_104 | `/pm/punch_gill` | 8 | 1/2 (WF_104_21 truncated) | Yes |
| WF_108 | `/mm/drill` | 4 | 1/2 (WF_108_18 truncated) | Yes |
| WF_109 | `/pm/punch_ribbing` | 6 | 1/2 (WF_109_16 truncated) | Yes |
| WF_1106 | `/dm/cylindrical_drill` | 4 | 2/2 | Yes |
| WF_1107 | `/mm/drill` **and** `/pm/punch_ribbing` | 6 **and** 10 | 1/2 (WF_1107_17 truncated) | **No — step-dependent** |
| WF_101 | — (no drill/punch step) | — | — | N/A |
| WF_105 | — (no drill/punch step) | — | — | N/A |

**Flag (WF_1107):** quantity is not a single variant-level value — case WF_1107_16 shows 6 at `/mm/drill` and 10 at `/pm/punch_ribbing`. Model quantity per step, not per variant.

**Note:** WF_101 and WF_105 carry no quantity parameter anywhere in the log (their routes have no feature-processing step); quantity is N/A for them, not 1 (unobservable).

## 2. Workpiece size at `/ov/burn` (categorical, per variant)

Observed categories: `regular` / `middle` / `large` / `maxi`. 13 burn instances across all 9 variants.

| Variant | Size | Cases observed | Deterministic? |
|---|---|---|---|
| WF_101 | regular | 2/2 | Yes |
| WF_102 | middle | 1/2 (WF_102_31 has no burn instance — see §5 flag 3) | Yes |
| WF_103 | large | 2/2 | Yes |
| WF_104 | maxi | 2/2 | Yes |
| WF_105 | regular | 2/2 | Yes |
| WF_108 | maxi | 1/2 (WF_108_18 truncated) | Yes |
| WF_109 | regular | 1/2 (WF_109_16 truncated) | Yes |
| WF_1106 | middle | 1/2 (WF_1106_21 has no burn instance — see §5 flag 3) | Yes |
| WF_1107 | large | 1/2 (WF_1107_17 truncated) | Yes |

**Determinism check passed:** every variant maps to exactly one burn size category; no within-variant variation.

**Supplement:** `parameter_burn_workpiece_thickness` (`thin`/`thick`) is likewise deterministic per variant: thin = WF_101, WF_102, WF_103, WF_104, WF_109; thick = WF_105, WF_108, WF_1106, WF_1107.

## 3. Workpiece size at drill steps (numeric, per variant)

Observed values: 30 / 40 / 50 / 60. Two drill activities, extracted separately (not merged with the burn encoding).

| Variant | Step | Size | Cases observed | Deterministic? |
|---|---|---|---|---|
| WF_102 | `/mm/drill` | 30 | 2/2 | Yes |
| WF_108 | `/mm/drill` | 30 | 1/2 (WF_108_18 truncated) | Yes |
| WF_1107 | `/mm/drill` | 40 | 1/2 (WF_1107_17 truncated) | Yes |
| WF_1106 | `/dm/cylindrical_drill` | 50 (case _22) / 60 (case _21) | 2/2 | **No — varies across cases** |

**Flag (WF_1106):** the `/dm/cylindrical_drill` size differs between the two cases (WF_1106_21 → 60, WF_1106_22 → 50). Not deterministic per variant; recommend a discrete {50, 60} parameter (flagged for the modeling stage).

## 4. Quality / Scrap

- No quality, rework, or scrap columns exist in the log.
- **No scrap:** `early_exit_probability = 0` for all variants; the 4 incomplete cases are window truncation, not abandonment.
- The only quality signal is the 8 retryable failures (7× HTTP 418 precondition, 1× HTTP 401 auth), which are handled by the failure-rate extraction (plan §2) and are out of scope here.

## 5. Flags for the Modeling Stage

1. **WF_1107 quantity is step-dependent** (drill = 6, punch_ribbing = 10) — model per step, not per variant.
2. **WF_1106 cylindrical-drill size varies across cases** (50 vs 60) — not deterministic; model as discrete {50, 60}.
3. **Routing inconsistency observed during extraction:** the log contains an `/ov/burn` instance for WF_102_32 (size `middle`, thickness `thin`) although the spec WF_102 route has no burn step; conversely WF_1106_21 has no `/ov/burn` instance although the spec WF_1106 route has burn at step 3. Burn presence varies across cases within WF_102/WF_1106 — routing should be re-verified at the modeling stage.
4. **Quantity is observable only at feature-processing steps**; WF_101/WF_105 have no quantity parameter (N/A, not 1).
