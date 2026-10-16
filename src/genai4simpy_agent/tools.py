import json
import os
import resource
import subprocess
import sys
from datetime import datetime, timezone

from langchain_core.tools import tool

# --- Report path constants ---
REPORTS_DIR = "output/generated_reports"
COLUMN_MAPPING_REPORT = "column_mapping_report"
TOPOLOGY_REPORT = "topology_report"
EXTRACTION_PLAN_REPORT = "extraction_plan_report"

# Extraction sub-agent report names
DURATIONS_PROCESSING_TIMES_REPORT = "durations_processing_times_report"
INTER_ARRIVAL_TIMES_REPORT = "inter_arrival_times_report"
QUANTITIES_QUALITY_REPORT = "quantities_quality_report"
DISTRIBUTION_FITTING_REPORT = "distribution_fitting_report"
TODO_LIST_REPORT = "todo_list"

# Evaluator agent report names
EXECUTION_RESULTS_REPORT = "execution_results"
EVALUATION_REPORT = "evaluation_report"

EXTRACTION_SUB_REPORTS = [
    DURATIONS_PROCESSING_TIMES_REPORT,
    INTER_ARRIVAL_TIMES_REPORT,
    QUANTITIES_QUALITY_REPORT,
    DISTRIBUTION_FITTING_REPORT,
]

# Resource limits for code the model writes and runs (run_python).
_RUN_PYTHON_MEM_BYTES = 8 * 1024**3
_SAFE_ENV_KEYS = ("PATH", "LD_LIBRARY_PATH", "LANG", "LC_ALL", "TZ", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")


def _limit_child(cpu_seconds: int):
    """preexec_fn: cap CPU time and address space, no core dumps, own process group."""
    def _apply():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        resource.setrlimit(resource.RLIMIT_AS, (_RUN_PYTHON_MEM_BYTES, _RUN_PYTHON_MEM_BYTES))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    return _apply


def make_run_python(timeout: int = 360, work_dir: str = "work_dir"):
    """Factory for a restricted, stateless Python runner.

    The code runs with the same interpreter as the pipeline (``sys.executable``,
    so the environment matches), in isolated mode (``-I``: no user site, no
    PYTHONPATH, script dir not on sys.path), with a scrubbed environment
    (no API keys), CPU-time / memory limits, and ``work_dir`` as the current
    directory. This is a guard-rail, not a security boundary: for untrusted
    deployments run the pipeline inside a container with a read-only data mount.
    """
    _cwd = os.getcwd()
    _work = os.path.join(_cwd, work_dir)
    _dataset_path = os.path.join(_work, "eventlog.parquet")
    _cleaned_path = os.path.join(_work, "eventlog_cleaned.parquet")
    _env = {k: os.environ[k] for k in _SAFE_ENV_KEYS if k in os.environ}
    _env.update(HOME=_work, MPLBACKEND="Agg", PYTHONHASHSEED="0")

    @tool(description=(
        f"Execute Python code and return the combined stdout and stderr. "
        f"Use only when no dedicated tool covers the need. "
        f"The raw dataset is at: {_dataset_path}. "
        f"A cleaned version may exist at {_cleaned_path} — prefer it when it exists "
        f"(check with os.path.exists). Load with pd.read_parquet(<path>). "
        f"Each call runs in a fresh, resource-limited subprocess with no shared state and the "
        f"run's work_files directory as current directory; store intermediate results there."
    ))
    def run_python(code: str) -> str:
        os.makedirs(_work, exist_ok=True)
        try:
            result = subprocess.run(
                [sys.executable, "-I", "-c", code],
                capture_output=True, text=True, timeout=timeout, cwd=_work, env=_env,
                preexec_fn=_limit_child(timeout),
            )
        except subprocess.TimeoutExpired:
            return (
                f"ERROR: Script timed out after {timeout} seconds. "
                "The code likely has an infinite loop or the workload is too large."
            )
        out = (result.stdout + result.stderr) or "(no output)"
        if len(out) > 20000:
            out = out[:10000] + f"\n... [{len(out) - 20000} chars truncated] ...\n" + out[-10000:]
        return out

    return run_python


def make_log_decision_tool(log_path: str, agent_name: str):
    """Factory for the HITL decision log (questions, answers and their source).

    In autonomous mode the orchestrator answers sub-agent questions itself; without
    a log those decisions are invisible. Every question/answer pair is appended to
    a JSONL file so that RQ3 (what needs human input?) can be measured.
    """
    _path = os.path.join(os.getcwd(), log_path)

    @tool(description=(
        "Log a question that would normally go to the user, together with the answer used and "
        "where it came from. Call this for EVERY question you answer without the user "
        "(autonomous mode), and for every user answer you receive. "
        "source: 'user' | 'context_file' | 'self_answered' | 'tool_evidence'. "
        "category: 'data_semantics' (what a column/value means) | 'modelling_decision' "
        "(how to represent something) | 'parameter' (a number) | 'scope'."
    ))
    def log_decision(question: str, answer: str, source: str, category: str,
                     evidence: str | None = None) -> str:
        os.makedirs(os.path.dirname(_path), exist_ok=True)
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "agent": agent_name, "question": question,
               "answer": answer, "source": source, "category": category, "evidence": evidence}
        with open(_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        return "logged"

    return log_decision


def make_write_report(report_name: str, output_dir: str = REPORTS_DIR):
    """Factory returning a write tool scoped to a single report file."""

    _output_dir = os.path.join(os.getcwd(), output_dir)
    os.makedirs(_output_dir, exist_ok=True)
    _filepath = os.path.join(_output_dir, f"{report_name}.md")

    @tool(description=(
        f"Write the finalized '{report_name}' report. "
        f"Use ONLY after the report content has been confirmed. "
        f"Saves to: {_filepath}"
    ))
    def write_report(content: str) -> str:
        """Write content to the report file.

        Args:
            content: Full Markdown body of the report.
        """
        with open(_filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Report written to {_filepath}"

    write_report.name = f"write_{report_name}"
    return write_report


def make_read_report(report_name: str, output_dir: str = REPORTS_DIR):
    """Factory returning a read tool scoped to a single report file."""

    _output_dir = os.path.join(os.getcwd(), output_dir)
    _filepath = os.path.join(_output_dir, f"{report_name}.md")

    @tool(description=(
        f"Read the '{report_name}' report. "
        f"Returns the full Markdown content or a message if the report does not exist yet. "
        f"File location: {_filepath}"
    ))
    def read_report() -> str:
        """Read and return the report content."""
        if not os.path.exists(_filepath):
            return f"Report '{report_name}' does not exist yet at {_filepath}."
        with open(_filepath, "r", encoding="utf-8") as f:
            return f.read()

    read_report.name = f"read_{report_name}"
    return read_report


def make_read_simulation_code(sim_dir: str = "output/generated_simpy_models"):
    """Factory returning a scoped read tool for simulation.py with optional line-range pagination."""

    _filepath = os.path.join(os.getcwd(), sim_dir, "simulation.py")

    @tool(description=(
        "Read the current simulation.py code. "
        "Returns the full source by default, or a specific line range via offset/limit. "
        "Use offset+limit to inspect large files without loading the full content. "
        "Lines in the output are prefixed with their 1-based line number for reference. "
        "Returns a message if the file does not exist yet. "
        f"File location: {_filepath}"
    ))
    def read_simulation_code(
        offset: int = 1,
        limit: int | None = None,
    ) -> str:
        """Read and return simulation.py content, optionally paginated.

        Args:
            offset: 1-based line number to start reading from. Default 1 (beginning).
            limit:  Maximum number of lines to return. Default None (read to end).
        """
        if not os.path.exists(_filepath):
            return f"simulation.py does not exist yet at {_filepath}."

        with open(_filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total = len(lines)
        start = max(0, offset - 1)          # convert to 0-based
        end = total if limit is None else min(start + limit, total)
        selected = lines[start:end]

        header = f"// simulation.py — lines {start + 1}–{end} of {total}\n"
        numbered = "".join(
            f"{start + i + 1:>6}\t{line}"
            for i, line in enumerate(selected)
        )
        return header + numbered

    return read_simulation_code


def make_write_simulation_code(sim_dir: str = "output/generated_simpy_models"):
    """Factory returning a write tool that creates simulation.py from scratch."""

    _dirpath = os.path.join(os.getcwd(), sim_dir)
    _filepath = os.path.join(_dirpath, "simulation.py")

    @tool(description=(
        "Write the complete SimPy simulation code to simulation.py. "
        "Use ONLY for initial creation or full rewrites (>50% of file changed). "
        "For targeted fixes, use edit_simulation_code instead. "
        f"File location: {_filepath}"
    ))
    def write_simulation_code(code: str) -> str:
        """Write Python source code to simulation.py.

        Args:
            code: Complete Python source of the SimPy simulation.
        """
        os.makedirs(_dirpath, exist_ok=True)
        with open(_filepath, "w", encoding="utf-8") as f:
            f.write(code)
        return f"simulation.py written to {_filepath}"

    return write_simulation_code


def make_edit_simulation_code(sim_dir: str = "output/generated_simpy_models"):
    """Factory returning a targeted string-replacement edit tool for simulation.py.

    Uses Python str.replace internally — no whitespace/tab ambiguity.
    Fails explicitly on zero or multiple matches so the agent gets clear feedback.
    """

    _filepath = os.path.join(os.getcwd(), sim_dir, "simulation.py")

    @tool(description=(
        "Apply a targeted string replacement to simulation.py. "
        "old_str must match exactly once in the file — include enough surrounding "
        "lines (2–3) to make it unique. "
        "Use read_simulation_code first to obtain the exact current content. "
        "For initial creation or rewrites touching >50% of the file, "
        "use write_simulation_code instead. "
        f"File location: {_filepath}"
    ))
    def edit_simulation_code(old_str: str, new_str: str) -> str:
        """Replace old_str with new_str in simulation.py.

        Args:
            old_str: Exact substring to replace. Must appear exactly once.
            new_str: Replacement text.
        """
        if not os.path.exists(_filepath):
            return f"Error: simulation.py does not exist at {_filepath}. Use write_simulation_code first."

        with open(_filepath, "r", encoding="utf-8") as f:
            source = f.read()

        count = source.count(old_str)
        if count == 0:
            # Provide a small diagnostic: find the closest matching line
            lines = source.splitlines()
            first_line = old_str.splitlines()[0].strip() if old_str.strip() else ""
            candidates = [
                f"  line {i+1}: {l}"
                for i, l in enumerate(lines)
                if first_line and first_line[:30] in l
            ]
            hint = (
                "\nClosest matching lines:\n" + "\n".join(candidates[:5])
                if candidates
                else "\nNo lines contain the start of old_str."
            )
            return (
                f"Error: old_str not found in simulation.py. "
                f"Read the file again and copy old_str verbatim from its content.{hint}"
            )
        if count > 1:
            return (
                f"Error: old_str appears {count} times in simulation.py. "
                f"Add more surrounding lines to make it unique."
            )

        updated = source.replace(old_str, new_str, 1)
        with open(_filepath, "w", encoding="utf-8") as f:
            f.write(updated)
        return "simulation.py updated successfully."

    return edit_simulation_code

def make_execute_simulation(sim_dir: str = "output/generated_simpy_models", timeout: int = 600):
    """Factory returning a tool that executes the run's simulation.py."""

    _sim_path = os.path.join(os.getcwd(), sim_dir, "simulation.py")

    @tool(description=(
        "Execute simulation.py as a script (its __main__ block) and return stdout/stderr. "
        "Use it to catch runtime errors; use run_contract_test / run_behavioural_check to "
        "verify the model itself. "
        f"Script location: {_sim_path}"
    ))
    def execute_simulation() -> str:
        """Run simulation.py and return its output."""
        if not os.path.exists(_sim_path):
            return f"simulation.py does not exist yet at {_sim_path}."
        try:
            result = subprocess.run(
                [sys.executable, _sim_path],
                capture_output=True, text=True, timeout=timeout,
                cwd=os.getcwd(),
            )
            return result.stdout + result.stderr or "(no output)"
        except subprocess.TimeoutExpired:
            return (
                f"ERROR: Simulation timed out after {timeout} seconds. "
                "The simulation is either stuck in an infinite loop or the duration "
                "is too long. Reduce SIM_DURATION, check for infinite retry loops, "
                "or add a maximum iteration guard."
            )

    return execute_simulation


def make_check_reports_tool(output_dir: str = REPORTS_DIR):
    _output_dir = os.path.join(os.getcwd(), output_dir)

    @tool(description=(
        "Check which phase reports already exist on disk. "
        "Call this at the start of a session to determine which phases can be skipped."
    ))
    def check_existing_reports() -> dict:
        """Return a dict mapping report names to whether they exist."""
        return {
            name: os.path.exists(os.path.join(_output_dir, f"{name}.md"))
            for name in (
                TODO_LIST_REPORT,          # ← new
                COLUMN_MAPPING_REPORT,
                TOPOLOGY_REPORT,
                EXTRACTION_PLAN_REPORT,
                *EXTRACTION_SUB_REPORTS,
                EXECUTION_RESULTS_REPORT,
                EVALUATION_REPORT,
            )
        }

    return check_existing_reports

def make_write_todo_list(output_dir: str = REPORTS_DIR):
    """Factory returning a tool that persists the orchestrator's todo list to disk."""

    _output_dir = os.path.join(os.getcwd(), output_dir)
    os.makedirs(_output_dir, exist_ok=True)
    _filepath = os.path.join(_output_dir, "todo_list.md")

    @tool(description=(
        "Persist the current todo list to disk so progress survives process restarts. "
        "Call this at startup and after every phase transition. "
        "Pass the full todo list as a Markdown checklist. "
        f"File location: {_filepath}"
    ))
    def write_todo_list(content: str) -> str:
        """Write the todo list to disk.

        Args:
            content: Full Markdown checklist, e.g.:
                - [x] Phase 1: Data analysis
                - [ ] Phase 2: Topology analysis
        """
        with open(_filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Todo list written to {_filepath}"

    return write_todo_list


def make_read_todo_list(output_dir: str = REPORTS_DIR):
    """Factory returning a tool that reads the persisted todo list from disk."""

    _filepath = os.path.join(os.getcwd(), output_dir, "todo_list.md")

    @tool(description=(
        "Read the persisted todo list from disk. "
        "Call this during Phase 0 resume to restore progress state. "
        f"File location: {_filepath}"
    ))
    def read_todo_list() -> str:
        """Read and return the todo list."""
        if not os.path.exists(_filepath):
            return "No todo list found — this is a fresh run."
        with open(_filepath, "r", encoding="utf-8") as f:
            return f.read()

    return read_todo_list