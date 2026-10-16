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

import json
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
from langchain.agents.middleware import (TodoListMiddleware, AgentMiddleware, ContextEditingMiddleware,
                                        ClearToolUsesEdit, ToolCallLimitMiddleware)
from deepagents.middleware.subagents import SubAgentMiddleware
from deepagents import CompiledSubAgent, create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.filesystem import FilesystemMiddleware

from src import telemetry
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
    SIMPY_COMPILER_AGENT_INSTRUCTIONS,
    EVALUATOR_COMPILER_MODE_ADDENDUM,
    FRAMEWORK_TOOLS,
    render,
    assert_prompt_tools,
)
from src.data_extraction_tools.tools import (
    make_exploration_tools,
    make_compute_duration,
    make_extract_processing_times,
    make_extract_inter_arrival_times,
    make_compute_grouped_statistics,
    make_fit_distribution,
    make_fit_activity_durations,
    make_apply_cleaning_and_save,
)
from src.data_extraction_tools.discovery import make_discovery_tools, make_set_log_schema_tool
from src.data_extraction_tools.routing import make_routing_tool
from src.genai4simpy_agent.spec import SpecStore, make_spec_tools, make_spec_status_tool
from src.genai4simpy_agent.verification import make_verification_tools
from src.genai4simpy_agent.compiler import make_compile_tool
from src.genai4simpy_agent.spec_drafting import make_drafting_tools, make_deviation_tool
from src.genai4simpy_agent.tools import (
    make_run_python,
    make_write_report,
    make_read_report,
    make_check_reports_tool,
    make_write_simulation_code,
    make_edit_simulation_code,
    make_read_simulation_code,
    make_execute_simulation,
    make_log_decision_tool,
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
)
from dotenv import load_dotenv
load_dotenv()

max_concurrent_extraction_units = 3
RECURSION_LIMIT = 1000
# 'compiler' (default): the coding agent compiles the spec (proposal P3a); 'llm': it writes simulation.py.
CODEGEN_MODE = os.getenv("CODEGEN_MODE", "compiler")

# ---------------------------------------------------------------------------
# Model endpoint
#
# The model is served by an OpenAI-compatible server (vLLM; Ollama's /v1 also
# works). Endpoint resolution: LLM_BASE_URL / LLM_API_KEY env vars, else the
# endpoint file written by scripts/vllm_qwen38.sbatch once the server is up.
# ---------------------------------------------------------------------------

VLLM_ENDPOINT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "vllm_endpoint.env")


def resolve_endpoint() -> dict:
    """Return {'base_url', 'api_key', 'model'(optional), ...} for the inference server."""
    ep = {}
    if os.path.exists(VLLM_ENDPOINT_FILE):
        with open(VLLM_ENDPOINT_FILE) as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    ep[k] = v
    base_url = os.getenv("LLM_BASE_URL") or ep.get("VLLM_BASE_URL")
    if not base_url:
        raise RuntimeError(f"No inference endpoint: set LLM_BASE_URL or start the vLLM job ({VLLM_ENDPOINT_FILE} missing).")
    key = os.getenv("LLM_API_KEY") or os.getenv("OLLAMA_API_KEY") or "EMPTY"
    return {"base_url": base_url, "api_key": key.removeprefix("Bearer "),
            "model": ep.get("VLLM_MODEL"), "model_repo": ep.get("VLLM_MODEL_REPO"), "job": ep.get("VLLM_JOB")}


def describe_model(base_url: str, api_key: str, model_name: str) -> dict:
    """Pin what is actually served (issue V5): model root/checkpoint and context length."""
    try:
        r = httpx.get(base_url.rstrip("/") + "/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
        for m in r.json().get("data", []):
            if m.get("id") == model_name:
                return {k: m.get(k) for k in ("id", "root", "max_model_len", "owned_by", "created")}
        return {"error": f"model '{model_name}' not served", "served": [m.get("id") for m in r.json().get("data", [])]}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def make_model(model_name: str, base_url: str, api_key: str):
    """Chat model with the generation settings recorded in run_info.json."""
    settings = {
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.6")),
        "top_p": float(os.getenv("LLM_TOP_P", "0.95")),
        "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "49152")),
        # thinking_token_budget (vLLM): caps reasoning per call so a single turn cannot think
        # past the output limit (which silently drops the tool call) or stall a run for minutes.
        "extra_body": {"top_k": int(os.getenv("LLM_TOP_K", "20")),
                       "thinking_token_budget": int(os.getenv("LLM_THINKING_BUDGET", "8192")),
                       "chat_template_kwargs": {"enable_thinking": os.getenv("LLM_THINKING", "1") == "1"}},
    }
    # stream_chunk_timeout=None: vLLM's tool parser buffers a tool call until it is complete, so a
    # large tool argument (spec section, model code) legitimately produces no chunk for minutes.
    model = init_chat_model(model=model_name, model_provider="openai", base_url=base_url, api_key=api_key,
                            timeout=float(os.getenv("LLM_TIMEOUT", "1800")), max_retries=0,
                            stream_chunk_timeout=None, stream_usage=True, **settings)
    return model, settings


# ---------------------------------------------------------------------------
# Transient model-call resilience
#
# Malformed tool calls from the model (server-side parser errors) and transport
# faults (timeouts, 5xx, connection resets) are resampled with backoff instead
# of aborting a multi-hour unattended run.
# ---------------------------------------------------------------------------

try:
    import openai as _openai
    _OPENAI_TRANSIENT = (_openai.APIConnectionError, _openai.APITimeoutError,
                         _openai.InternalServerError, _openai.RateLimitError)
except Exception:  # pragma: no cover
    _OPENAI_TRANSIENT = ()

try:
    from langchain_openai.chat_models._client_utils import StreamChunkTimeoutError as _StreamChunkTimeout
    _OPENAI_TRANSIENT = (*_OPENAI_TRANSIENT, _StreamChunkTimeout)
except Exception:  # pragma: no cover
    pass

try:  # optional: Ollama's native client
    from ollama import ResponseError as _OllamaResponseError
except Exception:  # pragma: no cover
    _OllamaResponseError = None

_TRANSIENT_MODEL_ERRORS = tuple(
    exc for exc in (_OllamaResponseError, httpx.HTTPError, *_OPENAI_TRANSIENT) if isinstance(exc, type)
)


class ModelRetryMiddleware(AgentMiddleware):
    """Retry model-call failures from the inference backend.

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
        max_attempts: int = 12,
        base_delay: float = 2.0,
        broad_max_attempts: int = 3,
        max_delay: float = 120.0,
    ) -> None:
        super().__init__()
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.broad_max_attempts = broad_max_attempts
        self.max_delay = max_delay

    def _backoff(self, attempt: int) -> float:
        # Capped exponential backoff: 12 transient attempts span ~15 min, enough to ride out
        # an inference-server restart without losing the run.
        return min(self.max_delay, self.base_delay * (2 ** attempt)) + random.uniform(0, 1)

    def _is_transient(self, exc: BaseException) -> bool:
        return bool(_TRANSIENT_MODEL_ERRORS) and isinstance(exc, _TRANSIENT_MODEL_ERRORS)

    _TRUNCATION_NOTE = (
        "[orchestration note] Your previous response was cut off at the output-token limit, so "
        "its tool call was lost. Think less and produce SMALLER pieces: e.g. write a short file "
        "skeleton first and add the remaining functions with separate edit calls, or write one "
        "spec section / one list chunk per call (merge=True).")

    @staticmethod
    def _truncated(response) -> bool:
        msgs = getattr(response, "result", None) or []
        meta = getattr(msgs[-1], "response_metadata", {}) if msgs else {}
        return meta.get("finish_reason") == "length"

    def _with_note(self, request):
        from langchain_core.messages import HumanMessage
        return request.override(messages=[*request.messages, HumanMessage(content=self._TRUNCATION_NOTE)])

    def wrap_model_call(self, request, handler):
        response = self._wrap_model_call(request, handler)
        if self._truncated(response):  # one re-issue with a steering note
            telemetry.record("output_truncated", retried=True)
            response = self._wrap_model_call(self._with_note(request), handler)
        return response

    async def awrap_model_call(self, request, handler):
        response = await self._awrap_model_call(request, handler)
        if self._truncated(response):
            telemetry.record("output_truncated", retried=True)
            response = await self._awrap_model_call(self._with_note(request), handler)
        return response

    def _wrap_model_call(self, request, handler):
        for attempt in range(max(self.max_attempts, self.broad_max_attempts)):
            try:
                return handler(request)
            except Exception as exc:
                transient = self._is_transient(exc)
                budget = self.max_attempts if transient else self.broad_max_attempts
                if attempt >= budget - 1:
                    raise
                telemetry.record("model_retry", error=type(exc).__name__, transient=transient,
                                 attempt=attempt + 1, budget=budget, detail=str(exc)[:300])
                time.sleep(self._backoff(attempt))

    async def _awrap_model_call(self, request, handler):
        for attempt in range(max(self.max_attempts, self.broad_max_attempts)):
            try:
                return await handler(request)
            except Exception as exc:
                transient = self._is_transient(exc)
                budget = self.max_attempts if transient else self.broad_max_attempts
                if attempt >= budget - 1:
                    raise
                telemetry.record("model_retry", error=type(exc).__name__, transient=transient,
                                 attempt=attempt + 1, budget=budget, detail=str(exc)[:300])
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

        telemetry.record("thrash_guard", tool=name, repeats=self._repeat_count)
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

    def _error_result(self, request, exc: Exception):
        """Turn an unexpected tool exception into feedback instead of aborting the run."""
        from langchain_core.messages import ToolMessage

        tc = getattr(request, "tool_call", None) or {}
        tc_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
        name = self._tool_name(request)
        telemetry.record("tool_exception", tool=name, error=f"{type(exc).__name__}: {exc}"[:300])
        return ToolMessage(content=f"Error: tool '{name}' raised {type(exc).__name__}: {exc}. "
                                   f"Check the arguments against the tool description and retry differently.",
                           tool_call_id=tc_id or "unknown", name=name, status="error")

    def wrap_tool_call(self, request, handler):
        try:
            result = handler(request)
        except Exception as exc:  # GraphInterrupt etc. derive from BaseException-safe types below
            if type(exc).__name__ in ("GraphInterrupt", "ParentCommand", "GraphBubbleUp"):
                raise
            result = self._error_result(request, exc)
        return self._steer(request, result)

    async def awrap_tool_call(self, request, handler):
        try:
            result = await handler(request)
        except Exception as exc:
            if type(exc).__name__ in ("GraphInterrupt", "ParentCommand", "GraphBubbleUp"):
                raise
            result = self._error_result(request, exc)
        return self._steer(request, result)


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
                ├── reports/            ← markdown reports, simulation_spec.json, hitl_log.jsonl
                │   ├── evidence/       ← full JSON results of the deterministic tools
                │   └── simulation/     ← generated SimPy models
                ├── work_files/         ← temp files (eventlog.parquet, cleaned)
                └── experiment_results/ ← run metadata (run_info.json)
    """
    run_dir = os.path.join("output", dataset_name, run_name)
    reports_dir = os.path.join(run_dir, "reports")
    sim_dir = os.path.join(run_dir, "reports", "simulation")
    work_dir = os.path.join(run_dir, "work_files")
    evidence_dir = os.path.join(run_dir, "reports", "evidence")
    experiment_results_dir = os.path.join(run_dir, "experiment_results")

    for d in (reports_dir, sim_dir, work_dir, evidence_dir, experiment_results_dir):
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
        "evidence_dir": evidence_dir,
        "experiment_results_dir": experiment_results_dir,
        "df": df,
    }




# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def create_run_agent(dataset_name: str, run_name: str, data_path: str, model_name: str | None = None) -> dict:
    """
    Build all agents for a specific run, scoped to that run's directory.

    Creates the directory structure, loads the dataset, and wires every tool
    factory to the run-specific paths. Prompts are rendered from the same paths
    and checked against each agent's tool list (no prompt may name a tool the
    agent lacks).

    Returns a dict with keys ``agent`` (orchestrator), ``subagents`` (name ->
    compiled graph, for standalone testing), ``run_dir``,
    ``experiment_results_dir`` and ``model_info``.
    """
    ctx = setup_run_dirs(dataset_name, run_name, data_path)
    df = ctx["df"]
    reports_dir, sim_dir, work_dir = ctx["reports_dir"], ctx["sim_dir"], ctx["work_dir"]
    evidence_dir, run_dir = ctx["evidence_dir"], ctx["run_dir"]

    endpoint = resolve_endpoint()
    model_name = model_name or endpoint.get("model")
    model, gen_settings = make_model(model_name, endpoint["base_url"], endpoint["api_key"])
    model_info = {"name": model_name, "base_url": endpoint["base_url"], "checkpoint": endpoint.get("model_repo"),
                  "codegen_mode": CODEGEN_MODE,
                  "context_clear_trigger_tokens": int(os.getenv("CONTEXT_CLEAR_TRIGGER", "40000")),
                  "run_python_limit_per_subagent_call": int(os.getenv("RUN_PYTHON_LIMIT", "8")),
                  "server_job": endpoint.get("job"), "generation": gen_settings,
                  "served": describe_model(endpoint["base_url"], endpoint["api_key"], model_name)}

    # virtual_mode: file tools see only this run directory (paths are rooted at it).
    _backend = FilesystemBackend(root_dir=os.path.join(os.getcwd(), run_dir), virtual_mode=True)

    # ---- shared state: spec store and providers for the deterministic tools ----
    store = SpecStore(reports_dir)
    schema_provider = lambda: store.get("log_schema")

    def censoring_provider():
        path = os.path.join(os.getcwd(), evidence_dir, "detect_censoring.json")
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _on_schema(schema: dict, meta: dict) -> None:
        store.put("log_schema", schema, author="data-analysis-agent")
        store.put("window", {"t0": meta["t0"], "horizon_s": meta["T"]}, author="data-analysis-agent")

    discovery = {t.name: t for t in make_discovery_tools(df, schema_provider, evidence_dir)}
    verification = make_verification_tools(sim_dir, df, schema_provider, store.load, evidence_dir)
    hitl_log = os.path.join(reports_dir, "hitl_log.jsonl")
    paths = {"SIM_FILE": os.path.join(sim_dir, "simulation.py"),
             "MAX_CONCURRENT": str(max_concurrent_extraction_units)}

    # Context engineering (P7): sub-agents accumulate large tool results (fit tables, run_python
    # dumps); above the trigger, older results are replaced by a placeholder. Everything cleared
    # can be re-read from the spec or the evidence files.
    ctx_trigger = int(os.getenv("CONTEXT_CLEAR_TRIGGER", "40000"))

    def _middleware(filesystem: bool = True, extra: list | None = None) -> list:
        mw = [ModelRetryMiddleware(), ToolThrashGuardMiddleware(), TodoListMiddleware(),
              ContextEditingMiddleware(edits=[ClearToolUsesEdit(
                  trigger=ctx_trigger, keep=4,
                  placeholder="[older tool result cleared to save context — re-run the tool or read_spec if needed]")])]
        # Over-exploration guard: agents tended to re-derive deterministic tool results in
        # run_python. After the budget, further run_python calls are refused (with a message)
        # and the agent continues with the dedicated tools.
        mw.append(ToolCallLimitMiddleware(tool_name="run_python",
                                          run_limit=int(os.getenv("RUN_PYTHON_LIMIT", "8")), exit_behavior="continue"))
        if filesystem:
            mw.append(FilesystemMiddleware(backend=_backend))
        return mw + (extra or [])

    built: dict[str, CompiledSubAgent] = {}

    def _build(name: str, description: str, prompt: str, tools: list, filesystem: bool = True,
               extra_mw: list | None = None) -> CompiledSubAgent:
        prompt = render(prompt, **paths)
        framework = {"write_todos"} | ({"read_file", "write_file", "edit_file", "ls", "glob", "grep"} if filesystem else set()) \
            | ({"task"} if extra_mw else set())
        assert_prompt_tools(name, prompt, {t.name for t in tools}, framework)
        graph = create_agent(model=model, tools=tools, system_prompt=prompt, name=name,
                             middleware=_middleware(filesystem, extra_mw)).with_config({"recursion_limit": RECURSION_LIMIT})
        built[name] = CompiledSubAgent(name=name, description=description, runnable=graph)
        return built[name]

    rr = lambda r: make_read_report(r, output_dir=reports_dir)
    wr = lambda r: make_write_report(r, output_dir=reports_dir)
    spec_tools = lambda agent: [*make_spec_tools(store, agent),
                                *make_drafting_tools(df, store, schema_provider, agent)]

    # ------------------------------------------------------------------
    # Phase 1-4 sub-agents
    # ------------------------------------------------------------------

    _build("data-analysis-agent",
           "Delegate dataset exploration, column meaning and relevance classification, the log "
           "schema (set_log_schema), data cleaning, and the column mapping report.",
           DATA_ANALYSIS_INSTRUCTIONS,
           [*make_exploration_tools(df), make_set_log_schema_tool(df, _on_schema), make_run_python(work_dir=work_dir),
            make_apply_cleaning_and_save(df, work_dir=work_dir), rr(COLUMN_MAPPING_REPORT), wr(COLUMN_MAPPING_REPORT)])

    _build("topology-analysis-agent",
           "Delegate topology and control-logic discovery: censoring, resources, variant routings "
           "with early exits, dispatching rules / priorities, release control and intra-case "
           "concurrency. Writes the spec sections and the topology report.",
           TOPOLOGY_ANALYSIS_INSTRUCTIONS,
           [*make_exploration_tools(df), *discovery.values(),
            make_routing_tool(df, schema_provider, censoring_provider, evidence_dir),
            make_run_python(work_dir=work_dir), *spec_tools("topology-analysis-agent"),
            make_deviation_tool(store, evidence_dir),
            rr(COLUMN_MAPPING_REPORT), rr(TOPOLOGY_REPORT), wr(TOPOLOGY_REPORT)])

    _build("extraction-planning-agent",
           "Delegate extraction planning: which parameter extractions are needed and which "
           "extraction sub-agents to deploy.",
           EXTRACTION_PLANNING_INSTRUCTIONS,
           [*spec_tools("extraction-planning-agent"), rr(COLUMN_MAPPING_REPORT), rr(TOPOLOGY_REPORT),
            rr(EXTRACTION_PLAN_REPORT), wr(EXTRACTION_PLAN_REPORT)])

    _build("durations-processing-times-agent",
           "Delegate service-time and failure-probability extraction per activity (spec "
           "section 'activities'). Reads its context from disk.",
           DURATIONS_PROCESSING_TIMES_INSTRUCTIONS,
           [make_fit_activity_durations(df, schema_provider), make_compute_duration(df),
            make_extract_processing_times(df), make_run_python(work_dir=work_dir),
            *spec_tools("durations-processing-times-agent"), rr(EXTRACTION_PLAN_REPORT),
            rr(DURATIONS_PROCESSING_TIMES_REPORT), wr(DURATIONS_PROCESSING_TIMES_REPORT)])

    _build("inter-arrival-times-agent",
           "Delegate arrival / release process extraction (spec section 'arrivals'). Reads its "
           "context from disk.",
           INTER_ARRIVAL_TIMES_INSTRUCTIONS,
           [make_extract_inter_arrival_times(df), make_run_python(work_dir=work_dir),
            *spec_tools("inter-arrival-times-agent"), rr(EXTRACTION_PLAN_REPORT),
            rr(INTER_ARRIVAL_TIMES_REPORT), wr(INTER_ARRIVAL_TIMES_REPORT)])

    _build("quantities-quality-agent",
           "Delegate quantity and quality statistics extraction. Reads its context from disk.",
           QUANTITIES_QUALITY_INSTRUCTIONS,
           [make_compute_grouped_statistics(df), make_run_python(work_dir=work_dir),
            *spec_tools("quantities-quality-agent"), rr(EXTRACTION_PLAN_REPORT), rr(COLUMN_MAPPING_REPORT),
            rr(QUANTITIES_QUALITY_REPORT), wr(QUANTITIES_QUALITY_REPORT)])

    _build("distribution-fitting-agent",
           "Delegate the review and finalisation of all distributions in the spec ('activities', "
           "'arrivals'). Runs after the other extraction agents.",
           DISTRIBUTION_FITTING_INSTRUCTIONS,
           [make_fit_activity_durations(df, schema_provider), make_fit_distribution(df),
            make_run_python(work_dir=work_dir), *spec_tools("distribution-fitting-agent"),
            rr(EXTRACTION_PLAN_REPORT), rr(DURATIONS_PROCESSING_TIMES_REPORT), rr(INTER_ARRIVAL_TIMES_REPORT),
            rr(DISTRIBUTION_FITTING_REPORT), wr(DISTRIBUTION_FITTING_REPORT)])

    # ------------------------------------------------------------------
    # Phase 5: coding agent (nested inside the evaluator)
    # ------------------------------------------------------------------

    code_tools = [make_read_simulation_code(sim_dir=sim_dir), make_execute_simulation(sim_dir=sim_dir),
                  *verification, wr(EXECUTION_RESULTS_REPORT)]
    if CODEGEN_MODE == "compiler":
        coder_prompt = SIMPY_COMPILER_AGENT_INSTRUCTIONS
        code_tools = [make_compile_tool(store.load, sim_dir), *code_tools]
    else:
        coder_prompt = SIMPY_DEEP_CODING_AGENT_INSTRUCTIONS
        code_tools = [make_write_simulation_code(sim_dir=sim_dir), make_edit_simulation_code(sim_dir=sim_dir),
                      *code_tools]
    coder = _build("simpy-deep-coding-agent",
                   "Delegate SimPy model generation from the simulation spec, and change requests. "
                   "Produces simulation.py (compiled from the spec or written), executes and verifies it.",
                   coder_prompt,
                   [*spec_tools("simpy-deep-coding-agent"), *code_tools],
                   filesystem=False)

    compiler_mode = CODEGEN_MODE == "compiler"
    _build("simulation-evaluator-agent",
           "Delegate SimPy simulation generation, deterministic verification (contract, behaviour "
           "vs the observed log, metamorphic relations) and evaluation. Coordinates the coding "
           "agent internally and writes the evaluation report.",
           SIMULATION_EVALUATOR_INSTRUCTIONS + (EVALUATOR_COMPILER_MODE_ADDENDUM if compiler_mode else ""),
           [*(spec_tools("simulation-evaluator-agent") if compiler_mode
              else make_spec_tools(store, "simulation-evaluator-agent", writable=[])), make_read_simulation_code(sim_dir=sim_dir), *verification,
            make_deviation_tool(store, evidence_dir),
            rr(EXECUTION_RESULTS_REPORT), wr(EVALUATION_REPORT)],
           filesystem=False,
           extra_mw=[SubAgentMiddleware(backend=_backend, subagents=[coder])])

    # ------------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------------

    orchestrator_prompt = render(
        WORKFLOW_INSTRUCTIONS + "\n\n" + "=" * 80 + "\n\n" + EXTRACTION_DELEGATION_INSTRUCTIONS, **paths)
    orchestrator_tools = [
        make_check_reports_tool(output_dir=reports_dir),
        make_spec_status_tool(store),
        make_deviation_tool(store, evidence_dir),
        rr(EXTRACTION_PLAN_REPORT),
        make_write_todo_list(output_dir=reports_dir),
        make_read_todo_list(output_dir=reports_dir),
        make_log_decision_tool(hitl_log, "orchestrator"),
    ]
    assert_prompt_tools("orchestrator", orchestrator_prompt, {t.name for t in orchestrator_tools}, FRAMEWORK_TOOLS)
    phase_agents = [n for n in built if n != "simpy-deep-coding-agent"]
    main_agent = create_deep_agent(
        model=model,
        tools=orchestrator_tools,
        system_prompt=orchestrator_prompt,
        subagents=[built[n] for n in phase_agents],
        middleware=[ModelRetryMiddleware(), ToolThrashGuardMiddleware()],
    ).with_config({"recursion_limit": RECURSION_LIMIT})

    return {
        "agent": main_agent,
        "subagents": {n: sa["runnable"] for n, sa in built.items()},
        "spec_store": store,
        "run_dir": run_dir,
        "experiment_results_dir": ctx["experiment_results_dir"],
        "model_info": model_info,
    }


# ---------------------------------------------------------------------------
# Module-level exports for LangGraph Studio
#
# Skipped when GENAI_SKIP_DEFAULT_INIT is set (e.g. by experiment.py) so that
# importing this module does not trigger folder creation or dataset loading.
# ---------------------------------------------------------------------------

if not os.environ.get("GENAI_SKIP_DEFAULT_INIT"):
    _default = create_run_agent(_DEFAULT_DATASET_NAME, _generate_run_name(), _DEFAULT_DATA_PATH,
                                model_name=os.getenv("HUMAN_MODE_MODEL"))
    agent = _default["agent"]
    data_analysis_graph = _default["subagents"]["data-analysis-agent"]
    topology_analysis_graph = _default["subagents"]["topology-analysis-agent"]
    extraction_planning_graph = _default["subagents"]["extraction-planning-agent"]
    simpy_deep_coding_graph = _default["subagents"]["simpy-deep-coding-agent"]
    simulation_evaluator_graph = _default["subagents"]["simulation-evaluator-agent"]
