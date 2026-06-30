import subprocess
from langchain_core.tools import tool
import os, sys

from src.simpy_code_workflow.context_engineering.docs_knowledge_retriever import SimPyKnowledgeRetriever

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

KDE_QUANTILES_DIR = "output/generated_reports/kde_quantiles"


def make_run_python(timeout: int = 360, work_dir: str = "work_dir"):

    _cwd = os.getcwd()
    _dataset_path = os.path.join(_cwd, work_dir, "eventlog.parquet")
    _cleaned_path = os.path.join(_cwd, work_dir, "eventlog_cleaned.parquet")

    @tool(description=(
        f"Execute Python code locally and return the combined stdout and stderr. "
        f"Use this to explore the dataset, compute statistics, test logic, or run simulation code. "
        f"The raw dataset is at: {_dataset_path}. "
        f"If the data analyst has already cleaned the dataset, a cleaned version is available at: "
        f"{_cleaned_path} — prefer this over the raw file when it exists "
        f"(check with os.path.exists). Load with pd.read_parquet(<path>). "
        f"Each call runs in a fresh subprocess with no shared state. "
        f"Store intermediate results to files if they need to persist across calls."
    ))
    def run_python(code: str) -> str:
        try:
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True, text=True, timeout=timeout
            )
            return result.stdout + result.stderr or "(no output)"
        except subprocess.TimeoutExpired:
            return (
                f"ERROR: Script timed out after {timeout} seconds. "
                "The code likely has an infinite loop or the workload is too large. "
                "Reduce the simulation duration or add a progress check."
            )

    return run_python


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


def make_read_merged_extraction_report(output_dir: str = REPORTS_DIR):
    """Factory returning a read tool that merges all extraction sub-generated_reports."""

    _output_dir = os.path.join(os.getcwd(), output_dir)

    @tool(description=(
        "Read the merged parameter extraction report. "
        "Automatically combines all extraction sub-agent generated_reports "
        "(durations/processing times, inter-arrival times, quantities/quality, "
        "distribution fitting) into a single document."
    ))
    def read_parameter_extraction_report() -> str:
        sections = []
        for report_name in EXTRACTION_SUB_REPORTS:
            filepath = os.path.join(_output_dir, f"{report_name}.md")
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    sections.append(f.read())
            else:
                sections.append(f"<!-- {report_name}: not yet available -->")
        return "\n\n---\n\n".join(sections)

    read_parameter_extraction_report.name = "read_parameter_extraction_report"
    return read_parameter_extraction_report


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


def make_simpy_knowledge_tool():
    """Factory returning a tool that retrieves SimPy documentation via semantic search."""

    # Building the retriever downloads HuggingFace embeddings and constructs a
    # Chroma vectorstore. This runs at agent-construction time (outside the agent
    # loop), so a network/embedding failure here aborts the whole run with no
    # chance for the model to self-heal. Surface a clear, actionable message.
    try:
        retriever = SimPyKnowledgeRetriever()
    except Exception as exc:
        raise RuntimeError(
            f"Failed to build the SimPy knowledge retriever "
            f"({type(exc).__name__}: {exc}). This requires downloading the HuggingFace "
            f"embedding model and building a Chroma vectorstore — check network access "
            f"and that 'sentence-transformers' and 'chromadb' are installed."
        ) from exc

    @tool(description=(
        "Retrieve SimPy documentation and examples relevant to a query. "
        "Always includes the full API reference. Additionally retrieves "
        "guides and examples via semantic search. "
        "Use this before writing simulation code to understand SimPy patterns."
    ))
    def retrieve_simpy_docs(query: str) -> str:
        """Search SimPy docs for relevant API reference, guides, and examples.

        Args:
            query: Natural language description of what you need
                   (e.g. 'how to create a Resource with limited capacity').
        """
        return retriever.retrieve(query)

    return retrieve_simpy_docs

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
    """Factory returning a tool that executes generated_simpy_models/simulation.py."""

    _sim_path = os.path.join(os.getcwd(), sim_dir, "simulation.py")

    @tool(description=(
        "Execute the generated SimPy simulation at generated_simpy_models/simulation.py "
        "and return the combined stdout and stderr. "
        "Use this to run the simulation and observe its output or catch runtime errors. "
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