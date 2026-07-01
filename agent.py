"""GenAI4SimPy Agent - LangGraph deployment script.

Multi-agent architecture:
  - Workflow Orchestrator (top-level): coordinates phases, relays user input
  - Data Analysis Sub-Agent: explores dataset, produces column mapping
  - Extraction Planning Sub-Agent: analyzes special conditions, routing, produces extraction plan
  - Extraction Sub-Agents (4): extract simulation parameters in parallel/sequential groups
  - SimPy Deep Coding Agent: reads generated_reports, writes/edits/executes SimPy code iteratively

Note: All sub-agents are created as CompiledSubAgent instances with explicit
recursion_limit to work around deepagents#1698.
"""

import os
import uuid
import time
import random
import asyncio
import logging
import pandas as pd

import httpx

logger = logging.getLogger(__name__)

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware, AgentMiddleware
from deepagents.middleware.subagents import SubAgentMiddleware
from deepagents import CompiledSubAgent, create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.filesystem import FilesystemMiddleware

from src.genai4simpy_agent.prompts import (
    WORKFLOW_INSTRUCTIONS,
    DATA_ANALYSIS_INSTRUCTIONS,
    TOPOLOGY_ANALYSIS_INSTRUCTIONS,
    EXTRACTION_PLANNING_INSTRUCTIONS,
    EXTRACTION_DELEGATION_INSTRUCTIONS,
    DURATIONS_PROCESSING_TIMES_INSTRUCTIONS,
    INTER_ARRIVAL_TIMES_INSTRUCTIONS,
    QUANTITIES_QUALITY_INSTRUCTIONS,
    DISTRIBUTION_FITTING_INSTRUCTIONS,
    SIMPY_DEEP_CODING_AGENT_INSTRUCTIONS,
    SIMULATION_EVALUATOR_INSTRUCTIONS,
)
from src.data_extraction_tools.tools import (
    make_exploration_tools,
    make_compute_duration,
    make_extract_processing_times,
    make_extract_inter_arrival_times,
    make_compute_grouped_statistics,
    make_fit_distribution,
    make_export_kde_quantiles,
    make_apply_cleaning_and_save,
)
from src.genai4simpy_agent.tools import (
    make_run_python,
    make_write_report,
    make_read_report,
    make_check_reports_tool,
    make_simpy_knowledge_tool,
    make_write_simulation_code,
    make_edit_simulation_code,
    make_read_simulation_code,
    make_execute_simulation,
    COLUMN_MAPPING_REPORT,
    TOPOLOGY_REPORT,
    EXTRACTION_PLAN_REPORT,
    DURATIONS_PROCESSING_TIMES_REPORT,
    INTER_ARRIVAL_TIMES_REPORT,
    QUANTITIES_QUALITY_REPORT,
    DISTRIBUTION_FITTING_REPORT,
    EXECUTION_RESULTS_REPORT,
    EVALUATION_REPORT,
    make_write_todo_list,
    make_read_todo_list,
    TODO_LIST_REPORT,
)
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# Model (module-level — expensive to initialize, shared across all runs)
# ---------------------------------------------------------------------------
header_auth_key = os.getenv("OLLAMA_API_KEY")
auth_value = header_auth_key if header_auth_key.startswith("Bearer ") else f"Bearer {header_auth_key}"
kwargs = {"client_kwargs": {"headers": {"Authorization": auth_value}}}

max_concurrent_extraction_units = 3
RECURSION_LIMIT = 1000

# ---------------------------------------------------------------------------
# Transient model-call resilience
#
# The remote Ollama server parses tool calls server-side with a strict XML
# parser. The Qwen model occasionally emits a malformed/truncated tool call
# (e.g. ``element <function> closed by </parameter>`` or ``unexpected EOF``),
# which Ollama returns as a hard ``ResponseError`` (status code -1). Because
# nothing downstream retries it, a single bad sample aborts an entire
# multi-phase run. The same applies to transient transport faults seen in the
# run log (504 Gateway Time-out, ConnectError, RemoteProtocolError, llama-server
# start timeouts). Since sampling is stochastic (temperature > 0), simply
# re-issuing the model call almost always recovers.
# ---------------------------------------------------------------------------

try:  # ollama is the backend client used by langchain-ollama
    from ollama import ResponseError as _OllamaResponseError
except Exception:  # pragma: no cover - fallback if export path changes
    try:
        from ollama._types import ResponseError as _OllamaResponseError
    except Exception:
        _OllamaResponseError = None

if _OllamaResponseError is None:
    # The middleware exists primarily to retry Ollama's server-side malformed
    # tool-call XML errors. If the import path ever changes and this resolves to
    # None, those errors silently stop being retried and a single bad sample
    # aborts an entire multi-phase run. Make that degradation visible instead of
    # failing silently.
    logger.warning(
        "Could not import ollama.ResponseError; ModelRetryMiddleware will rely on "
        "its broad retry tier for malformed-tool-call recovery. Check the installed "
        "ollama package version."
    )

_TRANSIENT_MODEL_ERRORS = tuple(
    exc for exc in (_OllamaResponseError, httpx.HTTPError) if isinstance(exc, type)
)


class ModelRetryMiddleware(AgentMiddleware):
    """Retry model-call failures from the Ollama backend.

    Wraps the model invocation (sync and async) and re-issues it on failure,
    using exponential backoff with jitter. Re-running the call re-samples the
    model, which resolves the intermittent malformed-tool-call XML errors raised
    by Ollama's server-side parser.

    Two retry tiers, because a single model-call failure aborts an entire
    unattended multi-phase run if it propagates:

    * Known transient classes (``_TRANSIENT_MODEL_ERRORS``) are retried up to
      ``max_attempts`` times. These are the documented Ollama/transport faults.
    * Any *other* exception raised by the model call is retried up to
      ``broad_max_attempts`` times. The Ollama adapter surfaces malformed
      tool-call XML inconsistently (sometimes ResponseError, sometimes a plain
      ``ValueError``/``KeyError`` or a JSON/validation error), and since sampling
      is stochastic a resample usually recovers. This tier keeps such cases from
      being terminal while still re-raising once the budget is exhausted.
    """

    def __init__(
        self,
        max_attempts: int = 4,
        base_delay: float = 2.0,
        broad_max_attempts: int = 3,
    ) -> None:
        super().__init__()
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.broad_max_attempts = broad_max_attempts

    def _backoff(self, attempt: int) -> float:
        return self.base_delay * (2 ** attempt) + random.uniform(0, 1)

    def _is_transient(self, exc: BaseException) -> bool:
        return bool(_TRANSIENT_MODEL_ERRORS) and isinstance(exc, _TRANSIENT_MODEL_ERRORS)

    def wrap_model_call(self, request, handler):
        for attempt in range(max(self.max_attempts, self.broad_max_attempts)):
            try:
                return handler(request)
            except Exception as exc:
                transient = self._is_transient(exc)
                budget = self.max_attempts if transient else self.broad_max_attempts
                if attempt >= budget - 1:
                    raise
                if not transient:
                    logger.warning(
                        "Retrying model call after non-transient %s (attempt %d/%d): %s",
                        type(exc).__name__, attempt + 1, budget, exc,
                    )
                time.sleep(self._backoff(attempt))

    async def awrap_model_call(self, request, handler):
        for attempt in range(max(self.max_attempts, self.broad_max_attempts)):
            try:
                return await handler(request)
            except Exception as exc:
                transient = self._is_transient(exc)
                budget = self.max_attempts if transient else self.broad_max_attempts
                if attempt >= budget - 1:
                    raise
                if not transient:
                    logger.warning(
                        "Retrying model call after non-transient %s (attempt %d/%d): %s",
                        type(exc).__name__, attempt + 1, budget, exc,
                    )
                await asyncio.sleep(self._backoff(attempt))


class ToolThrashGuardMiddleware(AgentMiddleware):
    """Break deterministic tool-failure loops before they exhaust the recursion budget.

    ``ToolNode`` feeds tool errors back to the model so it can self-correct, but
    nothing caps *repeated identical* failures. A persistent/deterministic
    failure (permission denied, an edit the model can never match, a report it
    keeps mis-formatting) produces feed-back -> retry -> same error, looping
    until ``recursion_limit`` raises ``GraphRecursionError`` and the whole
    unattended run dies with no graceful exit.

    This middleware tracks consecutive identical results per tool. Once the same
    tool returns the same output ``warn_after`` times in a row it appends a
    steering instruction to the tool result telling the model to change approach;
    at ``hard_after`` it escalates to "stop and summarize the blocker". The
    nudges ride back on the normal tool-result channel, so the model breaks the
    loop well before the 1000-step ceiling.

    Limitation: only *consecutive* repeats of the same tool are counted, so
    strictly-alternating thrash (A,B,A,B all failing) is not caught; the dominant
    real failure mode is the model hammering a single tool, which this covers.
    """

    def __init__(self, warn_after: int = 3, hard_after: int = 5) -> None:
        super().__init__()
        self.warn_after = warn_after
        self.hard_after = hard_after
        self._last_sig = None
        self._repeat_count = 0

    @staticmethod
    def _tool_name(request) -> str:
        tc = getattr(request, "tool_call", None)
        if isinstance(tc, dict):
            return tc.get("name", "<tool>")
        return getattr(tc, "name", "<tool>")

    def _steer(self, request, result):
        """Update repeat counters from ``result`` and append steering text if stuck."""
        from langchain_core.messages import ToolMessage

        # Only reason about plain-text ToolMessage results; pass Commands etc. through.
        if not isinstance(result, ToolMessage) or not isinstance(result.content, str):
            self._last_sig = None
            self._repeat_count = 0
            return result

        name = self._tool_name(request)
        sig = (name, result.content)
        if sig == self._last_sig:
            self._repeat_count += 1
        else:
            self._last_sig = sig
            self._repeat_count = 1

        if self._repeat_count < self.warn_after:
            return result

        if self._repeat_count >= self.hard_after:
            nudge = (
                f"\n\n[orchestration guard] Tool '{name}' has now returned the SAME "
                f"result {self._repeat_count} times in a row. Repeating it will not "
                f"help and is consuming the run's step budget. STOP calling this tool. "
                f"If you cannot make progress, write what you have, record the blocker "
                f"in the relevant report, and conclude this phase instead of retrying."
            )
        else:
            nudge = (
                f"\n\n[orchestration guard] Tool '{name}' has returned an identical "
                f"result {self._repeat_count} times. This approach is not working — "
                f"do NOT repeat the same call. Change your inputs/strategy, use a "
                f"different tool, or move on."
            )
        return result.model_copy(update={"content": result.content + nudge})

    def wrap_tool_call(self, request, handler):
        return self._steer(request, handler(request))

    async def awrap_tool_call(self, request, handler):
        return self._steer(request, await handler(request))


# ---------------------------------------------------------------------------
# Defaults for LangGraph Studio standalone use
# ---------------------------------------------------------------------------

_DEFAULT_DATASET_NAME = "fischertechnik_lab_C"
_DEFAULT_DATA_PATH = "data/fischertechnik_lab_C/block-C.csv"

# ---------------------------------------------------------------------------
# Run name generator (shared by agent.py and experiment.py)
# ---------------------------------------------------------------------------

def _generate_run_name() -> str:
    """Return a human-friendly random run identifier."""
    try:
        from coolname import generate_slug
        return generate_slug(3)
    except Exception:
        return f"run-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Directory setup
# ---------------------------------------------------------------------------

def setup_run_dirs(dataset_name: str, run_name: str, data_path: str) -> dict:
    """
    Create the per-run directory tree under ``output/`` and return a context dict.

    Layout::

        output/
        └── {dataset_name}/
            └── {run_name}/
                ├── reports/            ← markdown reports + kde_quantiles/
                │   └── simulation/     ← generated SimPy models
                ├── work_files/         ← temp files (eventlog.parquet, cleaned)
                └── experiment_results/ ← run metadata (run_info.json)
    """
    run_dir = os.path.join("output", dataset_name, run_name)
    reports_dir = os.path.join(run_dir, "reports")
    sim_dir = os.path.join(run_dir, "reports", "simulation")
    work_dir = os.path.join(run_dir, "work_files")
    kde_dir = os.path.join(run_dir, "reports", "kde_quantiles")
    experiment_results_dir = os.path.join(run_dir, "experiment_results")

    for d in (reports_dir, sim_dir, work_dir, kde_dir, experiment_results_dir):
        os.makedirs(d, exist_ok=True)

    # Construction-time I/O runs *outside* the agent loop, so the model cannot
    # self-heal from a failure here — a bad path or unreadable CSV simply aborts
    # the whole replication. Fail with a clear, actionable message instead of a
    # raw pandas/pyarrow traceback.
    if not os.path.isfile(data_path):
        raise FileNotFoundError(
            f"Input dataset not found at '{data_path}'. Check the --data-path "
            f"argument / DATA_PATH and that the file exists relative to {os.getcwd()}."
        )
    try:
        df = pd.read_csv(data_path)
    except Exception as exc:
        raise ValueError(
            f"Failed to read dataset CSV at '{data_path}': {type(exc).__name__}: {exc}. "
            f"Verify the file is a valid, readable CSV."
        ) from exc
    try:
        df.to_parquet(os.path.join(work_dir, "eventlog.parquet"))
    except Exception as exc:
        raise RuntimeError(
            f"Failed to write working parquet to '{work_dir}': {type(exc).__name__}: {exc}. "
            f"Check disk space and write permissions, and that a parquet engine "
            f"(pyarrow/fastparquet) is installed."
        ) from exc

    return {
        "run_dir": run_dir,
        "reports_dir": reports_dir,
        "sim_dir": sim_dir,
        "work_dir": work_dir,
        "kde_dir": kde_dir,
        "experiment_results_dir": experiment_results_dir,
        "df": df,
    }


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def create_run_agent(dataset_name: str, run_name: str, data_path: str, model_name:str) -> dict:
    """
    Build all agents for a specific run, scoped to that run's directory.

    Creates the directory structure, loads the dataset, and wires every tool
    factory to the run-specific paths.  Agents are restricted to the run folder
    via ``FilesystemBackend``.

    Returns a dict with keys:
        ``agent``, ``data_analysis_graph``, ``topology_analysis_graph``,
        ``extraction_planning_graph``, ``simpy_deep_coding_graph``,
        ``simulation_evaluator_graph``, ``run_dir``, ``experiment_results_dir``
    """
    ctx = setup_run_dirs(dataset_name, run_name, data_path)
    df = ctx["df"]
    reports_dir = ctx["reports_dir"]
    sim_dir = ctx["sim_dir"]
    work_dir = ctx["work_dir"]
    kde_dir = ctx["kde_dir"]
    run_dir = ctx["run_dir"]

    # Restrict filesystem access to this run's folder
    _backend = FilesystemBackend(
        root_dir=os.path.join(os.getcwd(), run_dir),
        virtual_mode=False,
    )

    model = init_chat_model(
        model=model_name,
        model_provider="openai",
        temperature=0.2,
        reasoning="high",
        base_url="http://localhost:11434",
        num_ctx=128000,
        **kwargs
    )

    ORCHESTRATOR_INSTRUCTIONS = (
        WORKFLOW_INSTRUCTIONS + "\n\n" + "=" * 80 + "\n\n"
        + EXTRACTION_DELEGATION_INSTRUCTIONS.format(
            max_concurrent_extraction_units=max_concurrent_extraction_units,
        )
    )

    def _build_subagent(name: str, description: str, system_prompt: str, tools: list) -> CompiledSubAgent:
        ag = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            middleware=[
                ModelRetryMiddleware(),
                ToolThrashGuardMiddleware(),
                TodoListMiddleware(),
                FilesystemMiddleware(backend=_backend),
            ],
        ).with_config({"recursion_limit": RECURSION_LIMIT})
        return CompiledSubAgent(name=name, description=description, runnable=ag)

    # ------------------------------------------------------------------
    # Sub-agents
    # ------------------------------------------------------------------

    data_analysis_sub_agent = _build_subagent(
        name="data-analysis-agent",
        description=(
            "Delegate dataset exploration, column meaning derivation, simulation relevance "
            "classification, data cleaning, and column mapping to the data analysis agent. "
            "It will analyze the event log, classify each column as simulation-relevant or not, "
            "confirm exclusions and cleaning operations with the user, save a cleaned dataset "
            "to data/eventlog_cleaned.parquet, and return a finalized column mapping report."
        ),
        system_prompt=DATA_ANALYSIS_INSTRUCTIONS,
        tools=[
            *make_exploration_tools(df),
            make_run_python(work_dir=work_dir),
            make_apply_cleaning_and_save(df, work_dir=work_dir),
            make_read_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
            make_write_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
        ],
    )

    topology_analysis_sub_agent = _build_subagent(
        name="topology-analysis-agent",
        description=(
            "Delegate topology analysis to identify resource classes, resource entities, "
            "routing per product variant, resource pooling, and other structural aspects "
            "of the manufacturing system. Returns findings for user validation or questions "
            "requiring clarification."
        ),
        system_prompt=TOPOLOGY_ANALYSIS_INSTRUCTIONS,
        tools=[
            *make_exploration_tools(df),
            make_run_python(work_dir=work_dir),
            make_read_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
            make_read_report(TOPOLOGY_REPORT, output_dir=reports_dir),
            make_write_report(TOPOLOGY_REPORT, output_dir=reports_dir),
        ],
    )

    extraction_planning_sub_agent = _build_subagent(
        name="extraction-planning-agent",
        description=(
            "Delegate extraction planning to determine which parameter extractions are needed "
            "based on the topology and column mapping, recommend which sub-agents to deploy, "
            "and produce a high-level extraction plan. "
            "It will return findings for user validation or questions requiring clarification."
        ),
        system_prompt=EXTRACTION_PLANNING_INSTRUCTIONS,
        tools=[
            *make_exploration_tools(df),
            make_run_python(work_dir=work_dir),
            make_read_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
            make_read_report(TOPOLOGY_REPORT, output_dir=reports_dir),
            make_read_report(EXTRACTION_PLAN_REPORT, output_dir=reports_dir),
            make_write_report(EXTRACTION_PLAN_REPORT, output_dir=reports_dir),
        ],
    )

    durations_processing_times_sub_agent = _build_subagent(
        name="durations-processing-times-agent",
        description=(
            "Delegate duration computation and processing time extraction. "
            "The agent reads its own context (column mapping, extraction plan) from disk. "
            "It writes results to durations_processing_times_report."
        ),
        system_prompt=DURATIONS_PROCESSING_TIMES_INSTRUCTIONS,
        tools=[
            make_compute_duration(df),
            make_extract_processing_times(df),
            make_run_python(work_dir=work_dir),
            make_read_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
            make_read_report(TOPOLOGY_REPORT, output_dir=reports_dir),
            make_read_report(EXTRACTION_PLAN_REPORT, output_dir=reports_dir),
            make_read_report(DURATIONS_PROCESSING_TIMES_REPORT, output_dir=reports_dir),
            make_write_report(DURATIONS_PROCESSING_TIMES_REPORT, output_dir=reports_dir),
        ],
    )

    inter_arrival_times_sub_agent = _build_subagent(
        name="inter-arrival-times-agent",
        description=(
            "Delegate inter-arrival time computation. "
            "The agent reads its own context (column mapping, extraction plan) from disk. "
            "It writes results to inter_arrival_times_report."
        ),
        system_prompt=INTER_ARRIVAL_TIMES_INSTRUCTIONS,
        tools=[
            make_extract_inter_arrival_times(df),
            make_run_python(work_dir=work_dir),
            make_read_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
            make_read_report(TOPOLOGY_REPORT, output_dir=reports_dir),
            make_read_report(EXTRACTION_PLAN_REPORT, output_dir=reports_dir),
            make_read_report(INTER_ARRIVAL_TIMES_REPORT, output_dir=reports_dir),
            make_write_report(INTER_ARRIVAL_TIMES_REPORT, output_dir=reports_dir),
        ],
    )

    quantities_quality_sub_agent = _build_subagent(
        name="quantities-quality-agent",
        description=(
            "Delegate quantity and quality statistics extraction. "
            "The agent reads its own context (column mapping, extraction plan) from disk. "
            "It writes results to quantities_quality_report."
        ),
        system_prompt=QUANTITIES_QUALITY_INSTRUCTIONS,
        tools=[
            make_compute_grouped_statistics(df),
            make_run_python(work_dir=work_dir),
            make_read_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
            make_read_report(TOPOLOGY_REPORT, output_dir=reports_dir),
            make_read_report(EXTRACTION_PLAN_REPORT, output_dir=reports_dir),
            make_read_report(QUANTITIES_QUALITY_REPORT, output_dir=reports_dir),
            make_write_report(QUANTITIES_QUALITY_REPORT, output_dir=reports_dir),
        ],
    )

    distribution_fitting_sub_agent = _build_subagent(
        name="distribution-fitting-agent",
        description=(
            "Delegate distribution fitting for all key simulation parameters. "
            "The agent reads its own context (column mapping, extraction plan, and other "
            "sub-agent generated_reports) from disk. "
            "It writes results to distribution_fitting_report."
        ),
        system_prompt=DISTRIBUTION_FITTING_INSTRUCTIONS,
        tools=[
            make_compute_duration(df),
            make_fit_distribution(df),
            make_export_kde_quantiles(output_dir=kde_dir),
            make_run_python(work_dir=work_dir),
            make_read_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
            make_read_report(TOPOLOGY_REPORT, output_dir=reports_dir),
            make_read_report(EXTRACTION_PLAN_REPORT, output_dir=reports_dir),
            make_read_report(DURATIONS_PROCESSING_TIMES_REPORT, output_dir=reports_dir),
            make_read_report(INTER_ARRIVAL_TIMES_REPORT, output_dir=reports_dir),
            make_read_report(DISTRIBUTION_FITTING_REPORT, output_dir=reports_dir),
            make_write_report(DISTRIBUTION_FITTING_REPORT, output_dir=reports_dir),
        ],
    )

    # ------------------------------------------------------------------
    # SimPy Deep Coding Agent
    # ------------------------------------------------------------------

    simpy_deep_coding_tools = [
        make_read_report(TOPOLOGY_REPORT, output_dir=reports_dir),
        make_read_report(DISTRIBUTION_FITTING_REPORT, output_dir=reports_dir),
        make_read_report(DURATIONS_PROCESSING_TIMES_REPORT, output_dir=reports_dir),
        make_read_report(INTER_ARRIVAL_TIMES_REPORT, output_dir=reports_dir),
        make_read_report(QUANTITIES_QUALITY_REPORT, output_dir=reports_dir),
        make_write_simulation_code(sim_dir=sim_dir),
        make_edit_simulation_code(sim_dir=sim_dir),
        make_read_simulation_code(sim_dir=sim_dir),
        make_execute_simulation(sim_dir=sim_dir),
        make_write_report(EXECUTION_RESULTS_REPORT, output_dir=reports_dir),
    ]

    simpy_deep_coding_graph_inner = create_agent(
        model=model,
        tools=simpy_deep_coding_tools,
        system_prompt=SIMPY_DEEP_CODING_AGENT_INSTRUCTIONS,
        middleware=[ModelRetryMiddleware(), ToolThrashGuardMiddleware(), TodoListMiddleware()],
    ).with_config({"recursion_limit": RECURSION_LIMIT})

    simpy_deep_coding_agent = CompiledSubAgent(
        name="simpy-deep-coding-agent",
        description=(
            "Delegate SimPy simulation code generation and validation. "
            "It reads all extraction generated_reports, writes SimPy code to files, "
            "iteratively edits and executes until the simulation runs correctly, "
            "and returns working SimPy code or a failure report."
        ),
        runnable=simpy_deep_coding_graph_inner,
    )

    # ------------------------------------------------------------------
    # Simulation Evaluator Agent
    # ------------------------------------------------------------------

    evaluator_tools = [
        make_read_report(DISTRIBUTION_FITTING_REPORT, output_dir=reports_dir),
        make_read_report(DURATIONS_PROCESSING_TIMES_REPORT, output_dir=reports_dir),
        make_read_report(INTER_ARRIVAL_TIMES_REPORT, output_dir=reports_dir),
        make_read_report(QUANTITIES_QUALITY_REPORT, output_dir=reports_dir),
        make_read_report(EXECUTION_RESULTS_REPORT, output_dir=reports_dir),
        make_read_report(TOPOLOGY_REPORT, output_dir=reports_dir),
        make_read_simulation_code(sim_dir=sim_dir),
        make_write_report(EVALUATION_REPORT, output_dir=reports_dir),
    ]

    simulation_evaluator_graph_inner = create_agent(
        model=model,
        tools=evaluator_tools,
        system_prompt=SIMULATION_EVALUATOR_INSTRUCTIONS,
        middleware=[
            ModelRetryMiddleware(),
            ToolThrashGuardMiddleware(),
            TodoListMiddleware(),
            SubAgentMiddleware(
                backend=_backend,
                subagents=[simpy_deep_coding_agent],
            ),
        ],
    ).with_config({"recursion_limit": RECURSION_LIMIT})

    simulation_evaluator_agent = CompiledSubAgent(
        name="simulation-evaluator-agent",
        description=(
            "Delegate SimPy simulation generation, validation, and evaluation. "
            "This agent coordinates with the coding agent internally: it generates code, "
            "cross-checks generated code against extraction reports, "
            "iterates until the simulation is accurate, and writes "
            "a final evaluation report."
        ),
        runnable=simulation_evaluator_graph_inner,
    )

    # ------------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------------

    orchestrator_tools = [
        make_run_python(work_dir=work_dir),
        make_check_reports_tool(output_dir=reports_dir),
        make_write_todo_list(output_dir=reports_dir),
        make_read_todo_list(output_dir=reports_dir),
    ]

    all_subagents = [
        data_analysis_sub_agent,
        topology_analysis_sub_agent,
        extraction_planning_sub_agent,
        durations_processing_times_sub_agent,
        inter_arrival_times_sub_agent,
        quantities_quality_sub_agent,
        distribution_fitting_sub_agent,
        simulation_evaluator_agent,
    ]

    main_agent = create_deep_agent(
        model=model,
        tools=orchestrator_tools,
        system_prompt=ORCHESTRATOR_INSTRUCTIONS,
        subagents=all_subagents,
        middleware=[ModelRetryMiddleware(), ToolThrashGuardMiddleware()],
    ).with_config({"recursion_limit": RECURSION_LIMIT})

    # ------------------------------------------------------------------
    # Standalone sub-agent graphs (for independent testing via LangGraph Studio)
    # ------------------------------------------------------------------

    data_analysis_graph = create_agent(
        model=model,
        tools=[
            *make_exploration_tools(df),
            make_run_python(work_dir=work_dir),
            make_apply_cleaning_and_save(df, work_dir=work_dir),
            make_read_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
            make_write_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
        ],
        system_prompt=DATA_ANALYSIS_INSTRUCTIONS,
        middleware=[
            ModelRetryMiddleware(),
            ToolThrashGuardMiddleware(),
            TodoListMiddleware(),
            FilesystemMiddleware(backend=_backend),
        ],
    ).with_config({"recursion_limit": RECURSION_LIMIT})

    topology_analysis_graph = create_agent(
        model=model,
        tools=[
            *make_exploration_tools(df),
            make_run_python(work_dir=work_dir),
            make_read_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
            make_read_report(TOPOLOGY_REPORT, output_dir=reports_dir),
            make_write_report(TOPOLOGY_REPORT, output_dir=reports_dir),
        ],
        system_prompt=TOPOLOGY_ANALYSIS_INSTRUCTIONS,
        middleware=[
            ModelRetryMiddleware(),
            ToolThrashGuardMiddleware(),
            TodoListMiddleware(),
            FilesystemMiddleware(backend=_backend),
        ],
    ).with_config({"recursion_limit": RECURSION_LIMIT})

    extraction_planning_graph = create_agent(
        model=model,
        tools=[
            *make_exploration_tools(df),
            make_run_python(work_dir=work_dir),
            make_read_report(COLUMN_MAPPING_REPORT, output_dir=reports_dir),
            make_read_report(TOPOLOGY_REPORT, output_dir=reports_dir),
            make_read_report(EXTRACTION_PLAN_REPORT, output_dir=reports_dir),
            make_write_report(EXTRACTION_PLAN_REPORT, output_dir=reports_dir),
        ],
        system_prompt=EXTRACTION_PLANNING_INSTRUCTIONS,
        middleware=[
            ModelRetryMiddleware(),
            ToolThrashGuardMiddleware(),
            TodoListMiddleware(),
            FilesystemMiddleware(backend=_backend),
        ],
    ).with_config({"recursion_limit": RECURSION_LIMIT})

    simpy_deep_coding_graph = create_agent(
        model=model,
        tools=simpy_deep_coding_tools,
        system_prompt=SIMPY_DEEP_CODING_AGENT_INSTRUCTIONS,
        middleware=[
            ModelRetryMiddleware(),
            ToolThrashGuardMiddleware(),
            TodoListMiddleware(),
            FilesystemMiddleware(backend=_backend),
        ],
    ).with_config({"recursion_limit": RECURSION_LIMIT})

    simulation_evaluator_graph = create_agent(
        model=model,
        tools=evaluator_tools,
        system_prompt=SIMULATION_EVALUATOR_INSTRUCTIONS,
        middleware=[
            ModelRetryMiddleware(),
            ToolThrashGuardMiddleware(),
            TodoListMiddleware(),
            SubAgentMiddleware(
                backend=_backend,
                subagents=[simpy_deep_coding_agent],
            ),
        ],
    ).with_config({"recursion_limit": RECURSION_LIMIT})

    return {
        "agent": main_agent,
        "data_analysis_graph": data_analysis_graph,
        "topology_analysis_graph": topology_analysis_graph,
        "extraction_planning_graph": extraction_planning_graph,
        "simpy_deep_coding_graph": simpy_deep_coding_graph,
        "simulation_evaluator_graph": simulation_evaluator_graph,
        "run_dir": run_dir,
        "experiment_results_dir": ctx["experiment_results_dir"],
    }


# ---------------------------------------------------------------------------
# Module-level exports for LangGraph Studio
#
# Skipped when GENAI_SKIP_DEFAULT_INIT is set (e.g. by experiment.py) so that
# importing this module does not trigger folder creation or dataset loading.
# ---------------------------------------------------------------------------

if not os.environ.get("GENAI_SKIP_DEFAULT_INIT"):
    model_name = os.getenv("HUMAN_MODE_MODEL")

    _default = create_run_agent(_DEFAULT_DATASET_NAME, _generate_run_name(), _DEFAULT_DATA_PATH, model_name=model_name)
    agent = _default["agent"]
    data_analysis_graph = _default["data_analysis_graph"]
    topology_analysis_graph = _default["topology_analysis_graph"]
    extraction_planning_graph = _default["extraction_planning_graph"]
    simpy_deep_coding_graph = _default["simpy_deep_coding_graph"]
    simulation_evaluator_graph = _default["simulation_evaluator_graph"]
