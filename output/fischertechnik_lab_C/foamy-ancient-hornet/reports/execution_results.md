# Execution Results — Refined MR1 Metamorphic Oracle

## Scope
Refinement of the **MR1** metamorphic oracle to a **bottleneck-migration-tolerant**
formulation. `simulation.py` (the digital twin) was **NOT** modified — it remains
byte-identical (537 lines; original `__main__` output reproduced exactly: 205 rows,
20 entered, 7 completed for seed 1).

## Why the strict MR1 failed (diagnosis, embedded in the harness)
The strict MR1 ("+1 capacity at the busiest resource must reduce **system-wide**
waiting") failed in the previous verification round. Diagnosis:

- The capacity knob **is** correctly applied. Mean wait at the augmented resource
  `vgr_1` dropped **64.5s → 4.3s**.
- The system-wide wait increase is a **legitimate bottleneck-migration effect**:
  `hbw_2` wait rose **138s → 264s** (the bottleneck migrated to the next
  most-constrained resource).
- End-to-end **flow time IMPROVED**: **578.9s → 523.8s**.

Therefore the strict system-wide-wait assertion is an **accepted exception**
(documented below, reported, but **non-gating**).

## New MR1 pass criteria (as implemented)
Both sub-checks must pass:
- **MR1a** — mean wait time **at the augmented resource** (`vgr_1`, the specific
  resource whose capacity was increased by +1) must **strictly decrease**
  (baseline run vs +1-capacity run).
- **MR1b** — end-to-end **flow time** (mean over completed cases) must **not
  increase**: `flow_augmented <= flow_baseline + epsilon` (epsilon = 0.1 s).

Documented, **non-gating** accepted-exception check (computed and reported, never
fails the overall result):
- **STRICT-MR1** — system-wide mean waiting must not increase
  (`sys_wait_augmented <= sys_wait_baseline`).

**MR2 / MR3 / MR4 are unchanged** (ARRIVAL_RATE_SCALE=1.5; FAILURES_ENABLED=False;
doubling SIMULATION_TIME).

## Method (deterministic)
- 10 replications, seeds 1..10, **common random numbers**: for each seed the
  baseline (vgr_1 cap 1) and augmented (vgr_1 cap 2) runs use the same seed, so
  the arrival process and case_ids are identical across the two runs.
- Flow time is compared on **paired** cases (those completing in **both** runs),
  which is robust to the completed-set shifting when capacity changes.
- `run_single_replication(seed)` is imported from `simulation.py` **unmodified**.

## Run output (baseline vs +1 capacity at the busiest resource `vgr_1`)
```
=== Refined MR1 oracle (10 replications, common random numbers, paired) ===
Augmented resource: vgr_1 (cap 1 -> 2)   [bottleneck per original MR1 / diagnosis]
Paired completed cases (complete in both runs): 40
Baseline : wait@vgr_1=34.0s  sys_wait=30.8s  paired_flow=844.6s
Augmented: wait@vgr_1=2.4s  sys_wait=27.9s  paired_flow=727.6s
MR1a (wait@vgr_1 strictly decreases): 2.4 < 34.0 -> PASS
MR1b (end-to-end flow not increased, eps=0.1): 727.6 <= 844.6+0.1 -> PASS
STRICT-MR1 (system-wide wait not increased) [ACCEPTED EXCEPTION, non-gating]: 27.9 <= 30.8 -> holds
OVERALL (MR1a AND MR1b): PASS

Per-resource mean wait (baseline -> augmented):
  dm_2    :    15.3 ->    15.3
  hbw_1   :     1.2 ->     1.2
  hbw_2   :   124.8 ->   138.7
  hw_1    :     3.3 ->     3.3
  mm_1    :    16.0 ->    16.0
  mm_2    :    18.5 ->    18.5
  ov_1    :     3.7 ->     3.7
  ov_2    :     3.1 ->     3.1
  pm_1    :     1.5 ->     1.5
  sm_1    :     8.6 ->     8.6
  sm_2    :     7.2 ->     7.2
  vgr_1   :    34.0 ->     2.4
  vgr_2   :    18.2 ->    18.2
  wt_1    :     7.4 ->     7.4
  wt_2    :     6.9 ->     6.9
```

## Interpretation
- **MR1a PASS**: the augmented resource `vgr_1` wait collapses (34.0s → 2.4s),
  confirming the capacity knob is correctly applied and the local bottleneck is
  relieved.
- **MR1b PASS**: end-to-end flow time **improves** (844.6s → 727.6s), consistent
  with the diagnosis (578.9s → 523.8s).
- **Bottleneck migration is visible and expected**: `hbw_2` wait rises
  (124.8s → 138.7s) — the next most-constrained resource absorbs the load.
- **STRICT-MR1 holds** in this run (30.8s → 27.9s); where it does not hold it is
  reported as an accepted exception and does **not** gate the overall result.

## Files
- `simulation.py` — **unchanged** (537 lines; original output reproduced).
- `metamorphic_mr1_refined.py` — standalone, self-contained refined-MR1 oracle
  (imports `simulation` unmodified; 10 replications; common random numbers;
  deterministic seeds 1..10). See final report for the run command and output.
