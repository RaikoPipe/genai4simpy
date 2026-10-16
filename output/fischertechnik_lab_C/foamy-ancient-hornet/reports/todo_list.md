# Pipeline TODO — fischertechnik_lab_C / foamy-ancient-hornet

- [x] Phase 0 — Resume check
- [x] Phase 1 — Data analysis: column mapping report + spec `log_schema`
- [x] Phase 2 — Topology & control logic: topology report + spec `resources`, `variants`, `control_policies`, `initial_state`, `assumptions`
- [x] Phase 3 — Extraction planning: extraction plan report
- [x] Phase 4 — Parameter extraction:
  - [x] durations-processing-times-agent → spec `activities` + durations report
  - [x] inter-arrival-times-agent → spec `arrivals` + inter-arrival report
  - [~] quantities-quality-agent → skipped per extraction plan (no qualifying columns)
  - [x] distribution-fitting-agent → spec `activities` + `arrivals` finalised, distribution fitting report
- [x] Phase 5 — SimPy code generation, verification & evaluation → verdict PASS (refined MR1 oracle; strict MR1 documented as accepted exception)
