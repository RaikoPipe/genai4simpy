# GenAI4SimPy — Deep Agents

> **Automatically generate executable [SimPy](https://simpy.readthedocs.io/) discrete-event simulation models from manufacturing event logs using a multi-agent LLM pipeline.**

---

## Overview

`genai4simpy-deepagents` orchestrates a pipeline of specialised AI agents that take a raw production event log (CSV) and — through data analysis, topology analysis, parameter extraction, and code generation — produce a validated, runnable SimPy simulation.

The system is built on the **[DeepAgents](https://github.com/RaikoPipe/deepagents)** framework for hierarchical agent orchestration and **LangGraph** for the SimPy code-generation workflow. Inference is designed to run against local, open-weight models served via **Ollama** (no cloud API keys / no proprietary model dependency required).

---

## Provenance & Research Context

GenAI4SimPy originated as the reference implementation for a peer-reviewed research project on GenAI-driven, privacy-preserving discrete-event simulation generation for small and medium-sized enterprises (SMEs). It is developed at Otto von Guericke University Magdeburg (OVGU) — AI Applications in Production and Logistics (AIPAL) group — together with Hochschule Bielefeld (HSBI) and Anhalt University of Applied Sciences.

**Primary publication:**

> R. Reider, L. Döring, S. Lang, T. Reggelin, S. Trojahn, and P. Reusch. "From Manufacturing Event Logs to Simulation: Enabling SMEs with Agentic AI for SimPy Simulation Generation." *Proceedings of the 2026 Winter Simulation Conference (WSC)*, V. Ramamohan, A. Djanatliev, M. Fakhimi, C. Krejci, C. Ruiz Martin, B. S. Onggo, and N. Mustafee, eds.

The paper introduces GenAI4SimPy as a multi-agent framework — powered by a local, open-weight LLM (Qwen 3.6, 27B, served via Ollama) — that automates end-to-end DES generation from raw manufacturing event logs to executable SimPy models, using tool-augmented reasoning and human-in-the-loop (HITL) validation gates. It was evaluated on three execution blocks of the public Fischertechnik Smart Factory event log (Malburg, Grüger, & Bergmann, 2022), achieving a mean activity-duration MAPE of 7.9% and coverage of failure-rate ground truth across all three blocks. The study also identifies a **"fidelity paradox"**: accurate process-level (activity-level) parameter extraction does not guarantee system-level behavioral fidelity (throughput, flow time), because emergent queueing dynamics amplify small structural errors (e.g. observation-window truncation misread as routing optionality) beyond what activity-level validation can catch. This motivates the evaluation harness in this repository (see [Experiments & Evaluation](#experiments--evaluation) below), which separates activity-level from system-level KPI scoring.

Design goals carried through into this codebase:

- **Data sovereignty** — the pipeline is built to run entirely on local, open-weight models (no mandatory proprietary cloud API), avoiding the data-privacy risks of sending manufacturing event logs to third-party LLM providers.
- **Expertise reduction** — HITL validation gates request only domain knowledge (e.g. "does this column mapping look right?"), not simulation-modeling expertise.
- **Pipeline autonomy** — beyond an initial calibration/context pass, the framework is designed to resolve structural and modeling decisions autonomously.

This repository predates and underlies the WSC paper; related, earlier work by the same group includes Reider & Lang (2025), *"GenAI for simulation modeling: A synergistic approach,"* and Kute et al. (2025), *"Generative AI for Automatic Simulation Model Generation in Factory Planning: A Framework and Prototype,"* Procedia Computer Science, 274, 1024–1033.

If you use this framework in academic work, please cite the WSC paper:

```bibtex
@inproceedings{reider2026genai4simpy,
  title     = {From Manufacturing Event Logs to Simulation: Enabling SMEs with Agentic AI for SimPy Simulation Generation},
  author    = {Reider, Richard and D{\"o}ring, Lina and Lang, Sebastian and Reggelin, Tobias and Trojahn, Sebastian and Reusch, Pascal},
  booktitle = {Proceedings of the 2026 Winter Simulation Conference (WSC)},
  editor    = {Ramamohan, V. and Djanatliev, A. and Fakhimi, M. and Krejci, C. and Ruiz Martin, C. and Onggo, B. S. and Mustafee, N.},
  year      = {2026}
}
```

**Acknowledgments:** The work of R. Reider was supported by the German Federal Ministry of Research, Technology and Space (BMFTR) under project *GenAI4FFD* (grant no. 01MK25003E), with support from the German Aerospace Center (DLR), Fraunhofer IFF, and industrial partners. The work of L. Döring was supported by the German Federal Ministry of Education and Research (BMBF) through the FH Kooperativ program (*KiMaC*, grant no. 13FH555KX1).

---

## Architecture

### Three-Agent Pipeline

```
┌─────────────────────────────────────────────────────────┐
│              Workflow Orchestrator (Master)              │
│   Coordinates phases · Full report access · Resumption  │
└──────────────┬──────────────────┬───────────────────────┘
               │                  │                   │
    ┌──────────▼──────┐  ┌────────▼──────┐  ┌────────▼──────────┐
    │  Phase 1        │  │  Phase 2      │  │  Phase 3          │
    │  Data Analysis  │  │  Parameter    │  │  SimPy Code       │
    │  Sub-Agent      │  │  Extraction   │  │  Agent (LangGraph)│
    └─────────────────┘  └───────────────┘  └───────────────────┘
    Output:              Reads Phase 1,     Reads Phase 2,
    column_mapping       outputs param      generates & validates
    _report.md           _extraction_       simulation code
                         report.md
```

Each sub-agent has **role-based report access** — it can only read the reports it needs and write the report it owns. The orchestrator checks for existing reports on startup and **skips completed phases**, allowing interrupted runs to resume.

### SimPy Code Agent Workflow (LangGraph)

![SimPy Code Agent Workflow](simpy_code_agent_workflow.png)

The code agent runs an iterative generate → validate → repair loop (max 5 iterations):

| Node | Description |
|---|---|
| `knowledge_retrieval` | Fetches relevant SimPy docs from embedded Chroma vectorstore |
| `reasoning_step` | Analyses the manufacturing system structure |
| `code_generation` | Generates initial SimPy code from parameters |
| `determine_editing_steps` | Plans structured `str_replace` edits on existing code |
| `code_editing` | Applies planned edits |
| `code_validation` | Executes the code in a subprocess; routes to repair on failure |

---

## Features

- **End-to-end automation** — from raw CSV to validated simulation code
- **Phase resumption** — skip already-completed analysis phases
- **Statistical distribution fitting** — tests 7 scipy distributions and picks the best fit (KS test)
- **Embedded SimPy knowledge** — API reference always loaded; examples/guides retrieved via semantic search
- **Self-hosted LLM** — runs fully locally via Ollama (no API keys required)
- **Role-based agent access control** — prevents agents from accessing or overwriting irrelevant reports
- **Structured code editing** — LLM produces `str_replace` diffs rather than full rewrites

---

## Project Structure

```
genai4simpy-deepagents/
├── agent.py                            # Entry point — orchestrator setup
├── pyproject.toml
├── langgraph.json                      # LangServe deployment config
├── simpy_code_agent_workflow.png       # Workflow diagram
│
├── data/
│   └── production_data/
│       └── Production_Data.csv         # Input event log
│
├── reports/                            # Agent outputs (auto-generated)
│   ├── column_mapping_report.md
│   └── parameter_extraction_report.md
│
└── src/
    ├── genai4simpy_agent/
    │   ├── prompts.py                  # System instructions for all agents
    │   └── tools.py                   # Report read/write/check tools
    │
    ├── data_extraction_tools/
    │   └── tools.py                   # Dataset exploration & statistics tools
    │
    └── simpy_code_workflow/
        ├── graph.py                   # LangGraph code-generation workflow
        ├── tool.py                    # Tool wrapper for orchestrator
        ├── prompts/                   # Prompt files (Markdown)
        ├── context_engineering/       # Vectorstore + SimPy docs
        └── data_models/
            └── simple_model.py        # Pydantic schemas for simulation config
```

---

## Requirements

- Python **3.11+**
- [Ollama](https://ollama.com/) running locally with `qwen3.5:27b` pulled

```bash
ollama pull qwen3.5:27b
```

---

## Installation

```bash
git clone <repo-url>
cd genai4simpy-deepagents

# Standard install
pip install -e .

# With dev tools (mypy, ruff, pytest)
pip install -e ".[dev]"
```

---

## Usage

### Run the full pipeline

```bash
python agent.py
```

The pipeline will:
1. Convert `data/production_data/Production_Data.csv` → `data/eventlog.parquet`
2. Check for existing phase reports and skip completed phases
3. **Phase 1** — Analyse the dataset, detect column roles, ask for user confirmation, write `reports/column_mapping_report.md`
4. **Phase 2** — Extract processing times, inter-arrival distributions, routing patterns, write `reports/parameter_extraction_report.md`
5. **Phase 3** — Generate, validate, and repair a SimPy simulation and return the code

### Deploy via LangServe

```bash
langgraph up
```

Exposes two endpoints:
- `http://localhost:8000/agent/` — Full orchestrator
- `http://localhost:8000/simpy_code_agent/` — SimPy code agent only

---

## Experiments & Evaluation

This repository ships the full experimental harness used in the WSC paper: an **experiment runner** that drives the agent pipeline end-to-end and archives every artifact, and a **standalone evaluation harness** that scores any resulting model against ground truth over multiple stochastic replications.

> **Before running:** In `agent.py` (`create_run_agent`), point `base_url` at your local Ollama server (default `http://localhost:11434`) and set `model` to a locally pulled model tag. Use **Python 3.11–3.13** — 3.14 currently crashes the SimPy code agent.

### 1. Run an experiment (`experiment.py`)

`experiment.py` wraps the orchestrator for reproducible, unattended runs: it loads a CSV event log plus a fixed manufacturing-system context, drives the pipeline to completion (or until the phase-recovery budget is exhausted), and writes every intermediate report, generated model, and timing metric to a uniquely named run directory under `output/<dataset-name>/<run-name>/`.

```bash
python experiment.py \
  -d data/fischertechnik_lab_A/block-A.csv \
  -n 1 \
  -m qwen3.6:27b-bf16 \
  --context-file data/fischertechnik_lab_A/user_context.md
```

| Flag | Description |
|---|---|
| `-d`, `--data-path` | Path to the input event-log CSV |
| `-n`, `--num-replications` | Number of end-to-end pipeline runs to execute |
| `-m`, `--model-name` | Ollama/OpenAI-compatible model tag to use for orchestration |
| `--context-file` | File whose contents seed the manufacturing-system context (see below); mutually exclusive with `--context` |

The three Fischertechnik blocks evaluated in the paper can be reproduced with:

```bash
python experiment.py -d data/fischertechnik_lab_A/block-A.csv -n 1 -m qwen3.6:27b-bf16 --context-file data/fischertechnik_lab_A/user_context.md
python experiment.py -d data/fischertechnik_lab_B/block-B.csv -n 1 -m qwen3.6:27b-bf16 --context-file data/fischertechnik_lab_B/user_context.md
python experiment.py -d data/fischertechnik_lab_C/block-C.csv -n 1 -m qwen3.6:27b-bf16 --context-file data/fischertechnik_lab_C/user_context.md
```

Each run produces:

```
output/<dataset-name>/<run-name>/
├── reports/                          # Phase reports (column mapping, topology, extraction, evaluation, ...)
│   └── simulation/simulation.py      # Generated SimPy model (evaluate.py --model target)
├── work_files/                       # Intermediate parquet/CSV artifacts (cleaned log, fitted params, KDE tables)
└── experiment_results/
    ├── run_info.json                 # Status, timing, model name, run metadata
    └── terminal.log                  # Full mirrored console log
```

Every replication is additionally appended to `results/runs.jsonl` as a single-line JSON record, so multiple experiment invocations accumulate into one cross-run log.

**`data/<dataset>/`** holds the three benchmark blocks (`block-A.csv` / `block-B.csv` / `block-C.csv`, drawn from the public Fischertechnik Smart Factory event log; Malburg et al., 2022), each paired with:
- `user_context.md` — the fixed calibration context compiled from an initial HITL pilot run (data-interpretation clarifications only; see paper Sec. 4), reused for the reproducible autonomous run
- `ground_truth_block_*.py` — empirical ground-truth KPIs and distributions extracted independently from the raw log, consumed by `evaluate.py`
- `og_conversation.md` — the original HITL pilot transcript the context file was distilled from

### 2. Score a generated model (`evaluate.py`)

`evaluate.py` is a model-agnostic evaluation harness (Stage 2 of the paper's methodology). It takes **any** generated SimPy module satisfying the [Model Output Contract](#model-output-contract) below plus a ground-truth file, runs `m` independent stochastic replications, and reports KPI point estimates, confidence intervals, coverage/threshold verdicts, and an aggregated quality score.

```bash
python evaluate.py \
  --model output/fischertechnik_lab_A/<run-name>/reports/simulation/simulation.py \
  --ground-truth data/fischertechnik_lab_A/ground_truth_block_A.py \
  -n 30
```

| Flag | Description |
|---|---|
| `--model` | Path to the generated model `.py` (must satisfy the output contract) |
| `--ground-truth` | Path to the corresponding `ground_truth_block_*.py` (or `.json`) |
| `-n`, `--replications` | Number of independent replications (paper uses `m = 30`) |
| `--seed` | Base seed for reproducible replications (default `42`) |
| `--sim-time` | Override simulation horizon in seconds (defaults to the ground truth's observation window) |
| `-o`, `--output` | Output directory (default `output/evaluation`) |

KPIs are split into two families, matching Figure 2 of the paper:
- **Coverage-based** (throughput, mean flow time, failure rate) — pass when the KPI's 95% CI crosses zero deviation from ground truth.
- **Threshold-based** (activity-duration MAPE ≤ 20%, variant-routing Jensen–Shannon divergence ≤ 0.05) — pass when the CI stays under the threshold.

Results are written to `<output>/evaluation_results.json` (full KPI/CI/verdict/quality-score breakdown) and `<output>/replication_kpis.csv` (one row per replication).

### 3. Reproduce the paper's forest plots (`forest_plot.py`)

```bash
python forest_plot.py
```

Renders the per-block confidence-interval forest plots (coverage KPIs and threshold KPIs) shown as Figure 2 in the WSC paper, saved to `forest_plot_v3.png` / `forest_plot_v3.pdf`. The per-block KPI values are currently hardcoded from the paper's results at the top of the script — update them there to plot a new evaluation run.

---

## Configuration

| Location | Parameter | Description |
|---|---|---|
| `agent.py` (`create_run_agent`) | `model_name` | Model tag for orchestration (pass via `experiment.py -m`, e.g. `qwen3.6:27b-bf16`) |
| `agent.py` (`create_run_agent`) | `base_url` | Inference server URL (point at your local Ollama instance, e.g. `http://localhost:11434`) |
| `agent.py` | `max_output_tokens=64000` | Token budget for code generation |
| `graph.py` | `max_iterations = 5` | Max code repair loop iterations |
| `tools.py` | `REPORTS_DIR = "reports"` | Output directory for phase reports |

---

## How It Works — In Detail

### Phase 1: Data Analysis

The data-analysis sub-agent uses a set of inspection tools to:
- Summarise dataset shape, dtypes, missing values, and duplicates
- Heuristically classify columns as timestamps, case IDs, resource identifiers, product types, or durations
- Output a structured column-mapping report which the user confirms before Phase 2 begins

### Phase 2: Parameter Extraction

The extraction sub-agent reads the confirmed column mapping and:
- Computes **processing times** per resource (mean, std, percentiles)
- Computes **inter-arrival times** per job type (coefficient of variation, mean IAT)
- **Fits statistical distributions** (normal, exponential, lognormal, gamma, Weibull, uniform, triangular) using the KS test and selects the best fit
- Identifies routing patterns and system structure

### Phase 3: SimPy Code Generation

The LangGraph workflow:
1. Retrieves relevant SimPy documentation from an embedded vectorstore (HuggingFace `all-MiniLM-L6-v2` + Chroma)
2. Reasons about the manufacturing system structure
3. Generates initial code using the extracted parameters
4. Validates the code by executing it in a subprocess
5. On failure, plans structured `str_replace` edits and re-validates (up to 5 attempts)

---

## Tech Stack

| Category | Library |
|---|---|
| Agent orchestration | `deepagents`, `langchain`, `langgraph` |
| LLM backend | `langchain-ollama` (Qwen 3.5 27B) |
| Data processing | `pandas`, `numpy`, `scipy` |
| Vector search | `chromadb`, `sentence-transformers` |
| Data validation | `pydantic` |
| Logging | `loguru` |
| Linting | `ruff` |

---

## License

MIT — see [LICENSE](LICENSE).

---

## Author

Richard Reider — richard@reider.io

---

## Model Output Contract

You generate a single, self-contained, importable Python module. It MUST expose
exactly the following interface and MUST NOT execute simulation work on import
(guard any demo run behind `if __name__ == '__main__':`).

### Required module symbols

1. `run_single_replication(seed: int) -> pandas.DataFrame`
   - Seeds BOTH `random.seed(seed)` and `np.random.seed(seed)` as the first
     action, so replications are reproducible and statistically independent.
   - Returns ONE standard event log per call (schema below).
   - Returns a DataFrame (a `(DataFrame, ...)` tuple is also accepted; element 0
     is used). No file I/O, no printing, no global mutation across calls.

2. `RESOURCE_CAPACITIES: dict[str, int]`
   - Maps each CONCRETE resource name (e.g. `vgr_1`, not the pool `vgr_pool`) to
     its capacity. Resource pools are expanded to their individual machines.

3. `SIMULATION_TIME: int`
   - Default horizon in seconds. The harness overrides this to the ground-truth
     observation window, so read this constant wherever you bound the run
     (`env.run(until=SIMULATION_TIME)`); do not hard-code the number elsewhere.

### Standard event-log schema (exact column names)

One row per executed activity instance. On a failure that is reworked, emit
TWO rows: the failed attempt (`failure`) then the successful retry (`success`).

| column                 | type     | semantics                                   |
|------------------------|----------|---------------------------------------------|
| `case_id`              | hashable | workpiece / case id                         |
| `variant`              | str      | variant label; MUST match a GT variant key  |
| `activity`             | str      | activity name; MUST match a GT activity key |
| `resource`             | str      | concrete resource that executed the step    |
| `time:timestamp`       | float    | execution start, sim-seconds from 0         |
| `operation_end_time`   | float    | execution end,   sim-seconds from 0         |
| `lifecycle:state`      | str      | `'success'` or `'failure'` only             |
| `response_status_code` | int      | optional (e.g. 200 / 418 / 401)             |

### Hard rules

- Time is numeric seconds relative to sim start = 0 (NOT datetimes).
- `operation_end_time >= time:timestamp` for every row.
- `variant` and `activity` string values MUST be drawn from the same vocabulary
  as the ground-truth file (`variant_distribution` / `activity_mean_durations_s`
  keys). Mismatched labels silently zero out JSD / MAPE — never invent names.
- Do not emit lifecycle rows other than the executed-instance rows above
  (no separate `scheduled` / `start` rows); the log is one row per execution.
- Module must import cleanly with only: `simpy`, `numpy`, `pandas`, `random`,
  and stdlib.

### Self-check before returning the model

- [ ] `run_single_replication(1)` and `run_single_replication(2)` return
      DataFrames with all 7 required columns and differing content.
- [ ] No NaN in `time:timestamp` / `operation_end_time` / `lifecycle:state`.
- [ ] Every `resource` value appears as a key in `RESOURCE_CAPACITIES`.
- [ ] Every `variant` / `activity` value matches the ground-truth vocabulary.