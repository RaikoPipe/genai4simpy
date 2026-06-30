import os

# Must be set before importing agent so that the module-level default
# initialization (directory creation + dataset loading) is skipped.
os.environ["GENAI_SKIP_DEFAULT_INIT"] = "1"

import asyncio
import glob
import time
import json
from datetime import timedelta, datetime, timezone
from pathlib import Path
import traceback

import pandas as pd
from langchain_core.messages import HumanMessage
from langgraph.errors import GraphRecursionError

from agent import create_run_agent, _generate_run_name

import sys
import io

# Force UTF-8 on Windows so emoji/box-drawing chars don't hit cp1252 charmap errors
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import sys

class _Tee:
    """Mirror writes to multiple streams (e.g. console + log file)."""
    def __init__(self, *streams):
        self._streams = streams

    def write(self, data):
        for s in self._streams:
            s.write(data)
            s.flush()

    def flush(self):
        for s in self._streams:
            s.flush()

# --- Setup & Configuration ---
# Resolves the project root dynamically based on the script's location
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

# --- Experiment Configuration ---
DATA_PATH = "data/fischertechnik_lab/operational_day_2021_07_01.csv"
NUM_REPLICATIONS = 1  # Edit in place to change how many runs to execute

# Dataset name derived from parent directory of DATA_PATH
DATASET_NAME = os.path.basename(os.path.dirname(DATA_PATH))

# Unified cross-run log (one entry per replication)
UNIFIED_LOG_PATH = "results/runs.jsonl"

# --- Manufacturing System Context ---
# The following is a summary from a QA style conversation with the LLM assistant. Recommendations on the interpretation of the
# data and were drawn from the LLM's analysis of the dataset.
USER_CONTEXT = """\
Here is the context on how to interpret the data from the manufacturing event logs:

Phase 1 — Data Analysis

- Retain planned_operation_time even though actual complete service time supersedes it (low priority, keep for reference).
- Parse the parameters string-dict into separate columns: start_position, end_position, quantity, workpiece_size.
- Keep response_status_code — it provides failure-type detail (401 auth, 418 precondition) beyond lifecycle:state.
- Drop human_workstation_green_button_pressed (sparse, out of scope).
Proceed with cleaning and save the cleaned event log to parquet. No row/duplicate removal.

Phase 2 — Topology Analysis

- Treat the end-of-process warehouse-return sequence (hbw_1/get_empty_bucket, hbw_1/store, associated vgr transports) as canonical for every variant. Any absence is time-window truncation, not optionality.
- WF_104 cross-line routing is intentional (two-stage design). Allow cross-line routing for this variant only.
- Enforce role-based VGR assignment: vgr_2 performs the first transport, vgr_1 the rest (honor the documented exceptions in source data).
- Model sorting ejection position as stochastic (uniform over {1,2,3}).
- Exclude the 4 incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) from routing inference only; retain them elsewhere.
- Model the 8 failure events (418/401) as retryable: operation retries and eventually succeeds; workpiece continues.

Phase 3 — Extraction Planning

- Model inter-arrivals as two-phase: initial near-simultaneous burst (first 8 cases) followed by steady-state arrivals, as reflected in the data.
- For sparse processing times, pool only machine pairs performing the same activity. Never pool across different activities.
- Use a single transport-time distribution per VGR resource (pool identical hardware); flag this for revisit at the modeling stage.
- Model failures with per-activity rates. Treat 418 and 401 as a single unified retry mechanism that triggers a re-attempt.
- burn_workpiece_size is context-dependent — separate by activity: at /ov/burn it is categorical and deterministic per variant; at drill steps it is numeric.
- Event semantics: one event_id = one attempt; the complete row is terminal. A retry appears as a new event_id and simply repeats the same process.
"""

# --- Autonomous Execution Preamble ---
NO_QUESTIONS_PREAMBLE = """
=== AUTONOMOUS EXECUTION MODE ===
You are running in fully automated experiment mode. Adhere to the following rules strictly
for this entire run — they override any contrary instructions in your system prompt:

1. DO NOT ask the user any questions at any point.
2. DO NOT pause for confirmations on reports, routing proposals, or data cleaning operations.
3. DO NOT produce any "QUESTIONS FOR USER" section — omit it entirely from all responses.
4. For every sub-agent delegation: when the agent returns findings or a draft report,
   immediately treat it as confirmed and instruct the agent to write the report to disk.
   Do not relay the report to the user for approval first.
5. When a sub-agent asks a question, answer it yourself using the context provided below
   or make the best possible assumption based on available data.
6. Proceed autonomously through all 5 phases from start to finish without stopping.

=== MANUFACTURING SYSTEM CONTEXT ===
Use the following context as authoritative background knowledge when making decisions
or answering questions that would otherwise require user input:

{context}

=== TASK ===
Execute the complete pipeline:
- Phase 0: Check existing reports and resume from the earliest incomplete phase.
- Phase 1: Data analysis — column mapping.
- Phase 2: Topology analysis — resources, routing, special conditions.
- Phase 3: Extraction planning — determine which extraction agents to deploy.
- Phase 4: Parameter extraction — durations, inter-arrival times, quantities, distributions.
- Phase 5: SimPy code generation, iterative validation, and evaluation.

Complete all phases and produce a fully validated SimPy simulation.
"""


# --- Notification ---
def _notify(title: str, message: str) -> None:
    """Send a desktop notification cross-platform (Linux/macOS/Windows)."""
    import sys
    try:
        if sys.platform == "linux":
            os.system(f'notify-send "{title}" "{message}"')
        elif sys.platform == "darwin":
            os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
    except Exception as e:
        print(f"[Notification failed: {e}]")


# --- Pipeline Execution ---
async def run_pipeline(agent, context: str, log_path: Path | None = None) -> tuple[float, str]:
    """Run the full pipeline in autonomous mode and stream all outputs to console (and log file)."""
    user_message = NO_QUESTIONS_PREAMBLE.format(context=context)
    input_data = {"messages": [HumanMessage(content=user_message)]}
    config = {"recursion_limit": 1000}

    log_file = None
    original_stdout = sys.stdout
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = open(log_path, "w", encoding="utf-8")
        sys.stdout = _Tee(original_stdout, log_file)

    try:
        print("\n" + "━" * 80)
        print(f"🚀 LAUNCHING AUTONOMOUS PIPELINE")
        print("━" * 80)

        t_start = time.perf_counter()

        async for event in agent.astream_events(input_data, config=config, version="v2"):
            kind = event.get("event", "")
            name = event.get("name", "")
            metadata = event.get("metadata", {})

            ns = metadata.get("langgraph_checkpoint_ns", "")
            agent_label = ns.split(":")[0] if ns else "orchestrator"
            prefix = f"[{agent_label.upper():<12}]"

            if kind == "on_chat_model_start":
                print(f"\n{prefix} 🤖 Thinking...", flush=True)

            elif kind == "on_chat_model_stream":
                chunk = event["data"].get("chunk")
                if chunk and chunk.content:
                    print(chunk.content, end="", flush=True)

            elif kind == "on_tool_start":
                tool_input = event["data"].get("input", {})
                input_preview = str(tool_input)[:150].replace('\n', ' ')
                print(f"\n{prefix} 🛠️  Tool: {name} | Input: {input_preview}...", flush=True)

            elif kind == "on_tool_end":
                tool_output = str(event["data"].get("output", "")).replace('\n', ' ')
                preview = (tool_output[:200] + "...") if len(tool_output) > 200 else tool_output
                print(f"\n{prefix} ✅ Result: {preview}", flush=True)

        elapsed = time.perf_counter() - t_start
        elapsed_str = str(timedelta(seconds=int(elapsed)))

        print("\n\n" + "━" * 80)
        print(f"🏁 RUN COMPLETE | Total Time: {elapsed_str}")
        print("━" * 80)
    finally:
        if log_file is not None:
            sys.stdout = original_stdout
            log_file.close()

    _notify(title="GenAI4FFD Pipeline Complete", message=f"Finished in {elapsed_str}")

    return elapsed, elapsed_str


# --- Display Results ---
def display_results_for(run_dir: Path) -> None:
    """List all generated reports in the run's reports directory."""
    reports_path = run_dir / "reports"
    report_files = sorted(glob.glob(str(reports_path / "*.md")))

    if not report_files:
        print(f"\n⚠️  No reports found in {reports_path}. Did the pipeline complete successfully?")
        return

    print("\n📜 GENERATED ARTIFACTS SUMMARY")
    print("─" * 60)
    for path in report_files:
        file_name = os.path.basename(path)
        size_kb = os.path.getsize(path) / 1024
        print(f"  • {file_name:<40} ({size_kb:.1f} KB)")
    print("─" * 60)
    print(f"Artifacts saved to: {reports_path}\n")


# --- Unified log ---
def _append_unified_log(entry: dict) -> None:
    """Append a single JSON record to the cross-run unified log."""
    os.makedirs(os.path.dirname(UNIFIED_LOG_PATH), exist_ok=True)
    with open(UNIFIED_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _write_budget_exhausted_report(run_dir: Path, run_name: str, error: str) -> None:
    """Write a stub evaluation report when a run hits the recursion/step ceiling.

    Ensures downstream artifact tooling still finds an ``evaluation_report.md``
    and that the run is diagnosable as "stuck" rather than silently missing an
    evaluation. Never overwrites an existing report.
    """
    reports_dir = run_dir / "reports"
    report_path = reports_dir / "evaluation_report.md"
    if report_path.exists():
        return
    try:
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            f"# Evaluation Report — INCOMPLETE (step budget exhausted)\n\n"
            f"Run `{run_name}` reached the agent's recursion/step limit before "
            f"completing all phases. No valid simulation was produced.\n\n"
            f"This usually means the agent got stuck repeating an action it could "
            f"not complete (e.g. a tool that kept failing the same way) rather "
            f"than a one-off crash. Inspect `experiment_results/terminal.log` and "
            f"the partial reports in this directory to find the blocking step.\n\n"
            f"**Termination cause:** {error}\n",
            encoding="utf-8",
        )
    except Exception as exc:  # never let reporting failure mask the original outcome
        print(f"[Could not write budget-exhausted stub report: {exc}]")


# --- Experiment Driver ---
def run_experiment(data_path: str, num_replications: int, context: str, model_name:str) -> None:
    """Run ``num_replications`` replications back-to-back."""
    dataset_name = os.path.basename(os.path.dirname(data_path))


    # --- PRE-FLIGHT DASHBOARD ---
    print("\n" + "═" * 60)
    print("                 EXPERIMENT DASHBOARD")
    print("═" * 60)
    print(f"📂 Dataset:      {dataset_name}")
    print(f"📊 Replications: {num_replications}")
    print(f"📍 Data Path:    {data_path}")
    print(f"🏠 Work Dir:     {os.getcwd()}")
    print("═" * 60 + "\n")

    for i in range(1, num_replications + 1):
        run_name = _generate_run_name()
        started_at = datetime.now(timezone.utc).isoformat()
        status: str = "success"
        error: str | None = None
        tb: str | None = None
        elapsed: float = 0.0
        elapsed_str: str = "0:00:00"

        print("\n" + "💎" * 30)
        print(f"💎 REPLICATION {i}/{num_replications} | ID: {run_name.upper()}")
        print("💎" * 30)

        run_artifacts = create_run_agent(dataset_name, run_name, data_path, model_name)
        agent = run_artifacts["agent"]
        run_dir = Path(run_artifacts["run_dir"])
        experiment_results_dir = Path(run_artifacts["experiment_results_dir"])

        print(f"📁 Run directory: {run_dir}")

        log_path = experiment_results_dir / "terminal.log"

        try:
            elapsed, elapsed_str = asyncio.run(run_pipeline(agent, context, log_path=log_path))
        except GraphRecursionError as exc:
            # The agent exhausted its step budget (recursion_limit). This is a
            # recognized "stuck / budget exhausted" outcome rather than an opaque
            # crash — label it distinctly and still emit a diagnosable artifact so
            # downstream tooling finds an evaluation report.
            status = "budget_exhausted"
            tb = traceback.format_exc()
            error = f"{type(exc).__name__}: {exc}"
            print(f"\n⏱️ [Replication {i} HIT STEP LIMIT] {error}")
            _write_budget_exhausted_report(run_dir, run_name, error)
            if log_path and log_path.exists():
                with open(log_path, "a") as f:
                    f.write(f"\n⏱️ BUDGET EXHAUSTED: {error}\n{tb}")
        except Exception as exc:
            status = "failed"
            tb = traceback.format_exc()
            error = f"{type(exc).__name__}: {exc}"
            print(f"\n❌ [Replication {i} FAILED] {error}\n{tb}")
            # Also write to log file
            if log_path and log_path.exists():
                with open(log_path, "a") as f:
                    f.write(f"\n❌ FAILED: {error}\n{tb}")

        finished_at = datetime.now(timezone.utc).isoformat()

        run_info = {
            "run_name": run_name,
            "dataset": dataset_name,
            "replication_index": i,
            "total_replications": num_replications,
            "data_path": data_path,
            "status": status,
            "error": error,
            "traceback": tb,
            "started_at": started_at,
            "finished_at": finished_at,
            "elapsed_seconds": round(elapsed),
            "elapsed_str": elapsed_str,
            "run_dir": str(run_dir),
            "model": model_name
        }

        with open(experiment_results_dir / "run_info.json", "w") as f:
            json.dump(run_info, f, indent=2)

        _append_unified_log(run_info)

        if status == "success":
            display_results_for(run_dir)
        else:
            print(f"\n⚠️  Partial artifacts at {run_dir}")


# --- CLI ---
def _parse_args():
    import argparse

    p = argparse.ArgumentParser(
        description="Run the GenAI4SimPy autonomous pipeline experiment."
    )
    p.add_argument(
        "-d", "--data-path", default=DATA_PATH,
        help=f"Path to the input event-log CSV (default: {DATA_PATH}).",
    )
    p.add_argument(
        "-n", "--num-replications", type=int, default=NUM_REPLICATIONS,
        help=f"Number of replications to run (default: {NUM_REPLICATIONS}).",
    )
    p.add_argument(
        "-m", "--model-name", default=None, type=str,
        help="Name of the model to run.",
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--context", default=None,
        help="Manufacturing-system context string passed to the agent. "
             "Overrides the built-in default.",
    )
    g.add_argument(
        "--context-file", default=None,
        help="Path to a file whose contents are used as the context string.",
    )
    return p.parse_args()


# --- Entry Point ---
if __name__ == "__main__":
    args = _parse_args()

    if args.context_file:
        context = Path(args.context_file).read_text()
    elif args.context is not None:
        context = args.context
    else:
        context = USER_CONTEXT

    run_experiment(
        data_path=args.data_path,
        num_replications=args.num_replications,
        context=context,
        model_name=args.model_name
    )

# todo
# - currently pipeline deals with floating point numbers in report, which is a bad idea and can lead to untracked hallucination
# - instead, the agent should write all intermediate numbers to a json file, and then read from that file when writing the final report. This way we have a single source of truth for all extracted parameters and can easily track any hallucination or drift in the report writing phase.
