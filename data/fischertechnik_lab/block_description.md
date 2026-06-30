# Dataset Description — DES Candidate Blocks (Phase 1)

Three curated event-log slices extracted from the cleaned version of the
*IoT-Enriched Event Log for Process Mining in Smart Factories* (Malburg, Grüger,
Bergmann, 2022). Each block is a temporally contiguous, high-density burst of
process executions on the Fischertechnik physical smart-factory model, selected
for suitability as input to discrete-event simulation (DES) model generation —
specifically, contention-aware models with queueing dynamics.

All three blocks share an identical 21-column schema and originate from the same
two-shop-floor factory. They differ in recording day, sample size, and load
profile.

## Provenance

- **Source dataset:** https://doi.org/10.6084/m9.figshare.20130794 (CC BY 4.0), cleaned version.
- **Origin:** `MainProcess.xes` top-level events, flattened to CSV.
- **Selection:** each block is one dense execution burst, bounded by extended idle
  gaps (no active case) on either side, so that within-block timestamps reflect
  continuous machine operation rather than diluted load.

## Blocks at a glance

| File | Recording day | Window (UTC) | Cases | Events | Wall | Max / mean concurrency | Workflows | Multifloor cases | Failure cases |
|------|--------------|--------------|-------|--------|------|------------------------|-----------|------------------|---------------|
| `block-A.csv` | 2021-07-06 | 15:08–16:01 | 18 | 576 | 53 min | 12 / 7.1 | 9 | 14 | 7 |
| `block-B.csv` | 2021-06-30 | 15:24–17:03 | 38 | 1383 | 99 min | 9 / 5.9 | 9 | 34 | 7 |
| `block-C.csv` | 2021-07-01 | 18:48–20:19 | 37 | 1137 | 91 min | 9 / 6.1 | 9 | 25 | 5 |

All three cover the same nine workflow models (`WF_101`–`WF_105`, `WF_108`,
`WF_109`, `WF_1106`, `WF_1107`), use the same 15 resource servers (7 per shop
floor, fewer on floor 2), and show a median activity service time of ~34–36 s.

## DES-relevant characteristics

Each block exhibits genuine resource contention — events wait in queue because the
requested machine is busy, observable as a positive gap between the `scheduled`
and `start` lifecycle transitions.

| File | Median wait | p90 wait | Events waiting > 5 s | Median service |
|------|-------------|----------|----------------------|----------------|
| `block-A.csv` | 5.2 s | 139 s | 51 % | 36 s |
| `block-B.csv` | 4.4 s | 67 s | 36 % | 34 s |
| `block-C.csv` | 4.3 s | 62 s | 33 % | 35 s |

- **`block-A.csv`** — highest peak (12) and mean (7.1) concurrency and the longest
  wait tail (p90 139 s), making it the most contention-intensive slice. Smallest
  sample (18 cases), so service-time distribution fitting per activity is thin.
  Best used as a peak-load stress/validation burst.
- **`block-B.csv`** — largest sample (38 cases) with strong sustained load and the
  highest share of multifloor cases (34/38), exercising inter-floor workpiece
  handoff. Moderate failure load. A robust primary or validation block.
- **`block-C.csv`** — dense sustained load (mean 6.1) with the cleanest failure
  profile (5/37) and full workflow coverage. Strongest single primary target for a
  feasibility proof where queueing must be reproduced with minimal stochastic
  routing noise.

## Schema

Each row is one lifecycle transition of one activity instance. A single activity
execution produces up to three rows (`scheduled` → `start` → `complete`),
linked by `case:concept:name` + `event_id`.

| Column | Meaning |
|--------|---------|
| `time:timestamp` | Event timestamp (UTC, ISO 8601). |
| `operation_end_time` | Expected/observed end time of the operation. |
| `lifecycle:transition` | `scheduled` (queued on resource), `start` (execution begins), `complete` (execution ends). |
| `lifecycle:state` | `assigned`, `inProgress`, `success`, or `failure`. |
| `event_id` | Activity-instance index within a case. |
| `identifier:id` | Activity identifier (e.g. `a_3`). |
| `process_model_id` | Workflow model, e.g. `WF_101`. |
| `case` | Case identifier. |
| `concept:name` | Activity name / service path, e.g. `/hbw/unload`. |
| `requested_service_url` | Full resource service call (host, resource, parameters, business key). |
| `org:resource` | Executing resource instance, e.g. `hbw_2`. Suffix `_1`/`_2` = shop floor. |
| `planned_operation_time` | Planned duration of the operation. |
| `parameters` | Structured input parameters for the activity. |
| `case:concept:name` | Case identifier (process-mining standard key). |
| `SubProcessID` | Links an `inProgress` event to its subevent file containing full IoT sensor data. |
| `current_task` | Human-readable description of the operation in progress. |
| `response_status_code` | HTTP status of the service call (e.g. 200). |
| `complete_service_time` | Total service time at completion. |
| `human_workstation_green_button_pressed` | Operator confirmation flag at the human workstation. |
| `unsatisfied_condition_description` | Reason an activity could not proceed, where applicable. |

## Key derivations for DES

- **Service time** = `complete.time:timestamp` − `start.time:timestamp` (per activity instance).
- **Queue wait** = `start.time:timestamp` − `scheduled.time:timestamp`.
- **Resources / servers** = distinct `org:resource` values; floor membership from the `_1`/`_2` suffix.
- **Control flow** = ordered `concept:name` sequence per case (by `event_id`).
- **Stochastic branches** = cases containing `lifecycle:state = failure`.
- **Inter-floor handoff** = cases whose resources span both `_1` and `_2` floors (the multifloor count above).

## Notes and caveats

- Timestamps are from the cleaned dataset; the specific cleaning measures applied
  upstream are not documented in the source distribution.
- `block-C.csv` runs late in the working day (ends 20:19). Confirm its service-time
  medians match `block-B.csv` before treating it as representative of typical
  cycle times.
- Full IoT sensor streams are **not** included here; they reside in the per-subevent
  files referenced by `SubProcessID` in the original dataset.

## License

Derived from a CC BY 4.0 dataset. Reuse under the same terms with attribution to
Malburg, Grüger, Bergmann (2022), DOI 10.6084/m9.figshare.20130794.