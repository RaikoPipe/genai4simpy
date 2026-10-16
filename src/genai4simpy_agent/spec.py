"""Typed simulation specification — the intermediate representation (IR).

Extraction agents write typed JSON sections into ``reports/simulation_spec.json``
instead of passing numbers through Markdown. The coding agent reads only the
sections it needs, and the verifier diff-checks the generated code against it.

Every numeric parameter carries provenance (``source``: the deterministic tool
that produced it, plus N), so transcription errors between tool output, spec
and code are traceable.
"""
from __future__ import annotations

import fcntl
import json
import os
import tempfile
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Literal

from langchain_core.tools import tool
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from src.data_extraction_tools.eventlog import LogSchema

SPEC_FILE = "simulation_spec.json"


class _Lenient(BaseModel):
    model_config = ConfigDict(extra="allow")


class Distribution(_Lenient):
    """A sampling recipe. ``family`` is a scipy.stats name, 'empirical_quantiles', or 'constant'."""

    family: str = Field(description="scipy.stats name (e.g. 'lognorm'), 'empirical_quantiles', 'categorical' or 'constant'.")
    params: dict[str, float] = Field(default_factory=dict, description="scipy keyword params, e.g. {'s':..,'loc':..,'scale':..}; {'value': x} for constant.")
    quantiles: list[float] | None = Field(None, description="Empirical quantile values (for 'empirical_quantiles').")
    quantile_probs: list[float] | None = Field(None, description="Probabilities matching `quantiles`.")
    values: list[float] | None = Field(None, description="Support of a 'categorical' distribution.")
    probs: list[float] | None = Field(None, description="Probabilities matching `values`.")
    mean: float | None = Field(None, description="Empirical mean of the sample (seconds).")
    n: int | None = Field(None, description="Sample size behind the estimate.")
    source: str | None = Field(None, description="Tool that produced the numbers, e.g. 'fit_activity_durations'.")

    @model_validator(mode="after")
    def _check(self):
        if self.family == "empirical_quantiles":
            if not self.quantiles or not self.quantile_probs or len(self.quantiles) != len(self.quantile_probs):
                raise ValueError("empirical_quantiles needs equally long `quantiles` and `quantile_probs`")
        elif self.family == "categorical":
            if not self.values or not self.probs or len(self.values) != len(self.probs):
                raise ValueError("categorical needs equally long `values` and `probs`")
            if abs(sum(self.probs) - 1) > 0.01:
                raise ValueError("categorical probs must sum to 1")
        elif self.family == "constant":
            if "value" not in self.params:
                raise ValueError("constant needs params.value")
        else:
            from scipy import stats as sp_stats
            if not hasattr(sp_stats, self.family):
                raise ValueError(f"unknown scipy.stats distribution '{self.family}'")
        return self


class Resource(_Lenient):
    name: str = Field(description="Concrete resource name as in the log, e.g. 'hbw_1'.")
    resource_class: str = Field(description="Class / pool name, e.g. 'hbw'.")
    capacity: int = Field(1, ge=1)


class Activity(_Lenient):
    name: str = Field(description="Activity label exactly as in the log.")
    eligible_resources: list[str] = Field(description="Concrete resources observed executing it.")
    duration: Distribution
    failure_probability: float = Field(0.0, ge=0, le=1, description="P(attempt fails) — estimated on all attempts.")
    on_failure: Literal["retry", "scrap", "rework", "none"] = "retry"


class Step(_Lenient):
    activity: str
    probability: float = Field(1.0, ge=0, le=1, description="P(step executed); estimate on COMPLETE cases only.")
    resources: dict[str, float] | None = Field(None, description="Concrete resource -> share for this step position (from resources_by_step).")
    resource_rule: str | None = Field(None, description="Free-text rule when shares are not enough, e.g. 'same floor as previous'.")
    concurrent_with_previous: bool = Field(False, description="Step may start before the previous step ends (intra-case parallelism).")


class Variant(_Lenient):
    name: str
    probability: float = Field(ge=0, le=1, description="Share of released cases (uncensored cases).")
    steps: list[Step] = Field(description="Main sequence, from complete cases.")
    early_exit_probability: float = Field(0.0, ge=0, le=1, description="P(case stops before the terminal activity) — real abandonment, not truncation.")
    early_exit_after_n_steps: dict[str, float] = Field(default_factory=dict, description="Number of completed steps after which an exiting case stops -> share among exits (sums to 1).")
    early_exit_after: dict[str, float] = Field(default_factory=dict, description="Descriptive: activity at which exiting cases stopped -> share.")


class Arrivals(_Lenient):
    model: Literal["poisson", "two_regime_bursts", "renewal", "batch", "wip_controlled"] = Field(
        description="Arrival / release model. Never a replay of observed case ids or timestamps.")
    interarrival: Distribution | None = Field(None, description="IAT distribution (poisson / renewal), seconds.")
    burst_size: Distribution | None = Field(None, description="Cases per burst (two_regime_bursts / batch).")
    intra_burst_iat: Distribution | None = None
    inter_burst_gap: Distribution | None = None
    wip_cap: int | None = Field(None, description="Max cases in system (wip_controlled / CONWIP).")
    initial_burst: Distribution | None = Field(
        None, description="Optional: number of cases released together at t=0 (categorical), spaced by intra_burst_iat "
                          "(or 1 s), before the regular arrival process starts.")
    notes: str | None = None

    @model_validator(mode="after")
    def _required_for_model(self):
        need = {"two_regime_bursts": ["burst_size", "intra_burst_iat", "inter_burst_gap"],
                "batch": ["burst_size", "inter_burst_gap"],
                "poisson": ["interarrival"], "renewal": ["interarrival"],
                "wip_controlled": ["interarrival", "wip_cap"]}[self.model]
        missing = [f for f in need if getattr(self, f) is None]
        if missing:
            raise ValueError(f"arrivals.model='{self.model}' requires top-level fields {missing}")
        return self


class ControlPolicies(_Lenient):
    queue_discipline: dict[str, Literal["fifo", "priority"]] = Field(
        default_factory=dict, description="Per resource class.")
    priority_order: dict[str, list[str]] = Field(
        default_factory=dict, description="Per resource class: activities from highest to lowest priority.")
    release_rule: str | None = Field(None, description="e.g. 'open', 'wip_cap(4)', 'completion_triggered'.")
    intra_case_concurrency: str | None = Field(None, description="Which steps overlap within a case, if any.")
    evidence: dict[str, Any] = Field(default_factory=dict, description="Key numbers from the discovery tools.")


class InitialState(_Lenient):
    wip_at_start: int = 0
    cases_in_progress: list[dict[str, Any]] = Field(
        default_factory=list, description="[{'variant':..,'current_activity':..}] — no case ids.")
    excluded_from_estimation: list[str] = Field(default_factory=list, description="Censored case ids excluded from routing/variant estimation (never used in code).")


class Window(_Lenient):
    t0: str
    horizon_s: float
    terminal_activity: str | None = None
    first_activity: str | None = None


SECTION_MODELS: dict[str, Any] = {
    "log_schema": LogSchema,
    "window": Window,
    "resources": list[Resource],
    "activities": list[Activity],
    "variants": list[Variant],
    "arrivals": Arrivals,
    "control_policies": ControlPolicies,
    "initial_state": InitialState,
    "assumptions": list[str],
}

# Compact shape examples, shown in the write tool's description and on validation errors.
SECTION_EXAMPLES: dict[str, str] = {
    "window": '{"t0": "2021-07-01T18:48:23+00:00", "horizon_s": 5461.5, "terminal_activity": "/x/store", "first_activity": "/x/unload"}',
    "resources": '[{"name": "hbw_1", "resource_class": "hbw", "capacity": 1}, ...]  (a LIST, one entry per concrete resource)',
    "activities": '[{"name": "/ov/burn", "eligible_resources": ["ov_1", "ov_2"], "duration": {"family": "lognorm", "params": {"s": 0.2, "loc": 0, "scale": 30}, "mean": 30.5, "n": 32, "source": "fit_activity_durations"}, "failure_probability": 0.0, "on_failure": "retry"}, ...]',
    "variants": '[{"name": "WF_101", "probability": 0.11, "steps": [{"activity": "/hbw/unload", "resources": {"hbw_2": 1.0}}, {"activity": "/ov/burn", "resources": {"ov_1": 1.0}, "concurrent_with_previous": true}], "early_exit_probability": 0.5, "early_exit_after_n_steps": {"12": 1.0}}, ...]',
    "arrivals": '{"model": "two_regime_bursts", "burst_size": {"family": "categorical", "values": [1, 2], "probs": [0.5, 0.5], "source": "..."}, "intra_burst_iat": {...}, "inter_burst_gap": {...}, "initial_burst": {"family": "constant", "params": {"value": 8}} (optional)}  or  {"model": "renewal", "interarrival": {...}}  or  {"model": "wip_controlled", "interarrival": {...}, "wip_cap": 4}',
    "control_policies": '{"queue_discipline": {"hbw": "priority", "vgr": "fifo"}, "priority_order": {"hbw": ["/hbw/store_empty_bucket", "/hbw/unload"]}, "release_rule": "open", "intra_case_concurrency": "...", "evidence": {"hbw_fifo_agreement": 0.51}}',
    "initial_state": '{"wip_at_start": 0, "cases_in_progress": [], "excluded_from_estimation": ["<case id>", ...]}',
    "assumptions": '["text", ...]  (a LIST of strings)',
}

# Which phase owns which section (write permission).
SECTION_OWNERS: dict[str, list[str]] = {
    "data-analysis-agent": ["log_schema", "window"],
    "topology-analysis-agent": ["window", "resources", "variants", "control_policies", "initial_state", "assumptions"],
    "durations-processing-times-agent": ["activities", "assumptions"],
    "inter-arrival-times-agent": ["arrivals", "assumptions"],
    "quantities-quality-agent": ["assumptions"],
    "distribution-fitting-agent": ["activities", "arrivals", "assumptions"],
    # Only used in CODEGEN_MODE=compiler (see agent.py): spec corrections backed by evidence.
    "simulation-evaluator-agent": ["variants", "arrivals", "control_policies", "activities", "assumptions"],
}


class SpecStore:
    """JSON-file backed spec with per-section validation and history."""

    _thread_lock = threading.RLock()

    def __init__(self, reports_dir: str):
        self.path = os.path.join(os.getcwd(), reports_dir, SPEC_FILE)
        self.rel_path = os.path.join(reports_dir, SPEC_FILE)

    @contextmanager
    def _locked(self):
        """Serialise read-modify-write: agents issue parallel tool calls."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with self._thread_lock, open(self.path + ".lock", "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)

    def load(self) -> dict[str, Any]:
        if not os.path.exists(self.path):
            return {}
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def save(self, spec: dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.path), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2, default=str)
        os.replace(tmp, self.path)
        with open(self.path[:-5] + ".md", "w", encoding="utf-8") as f:
            f.write(render_spec_markdown(spec))

    def get(self, section: str) -> Any:
        return self.load().get(section)

    def put(self, section: str, value: Any, author: str) -> Any:
        from pydantic import TypeAdapter

        if section not in SECTION_MODELS:
            raise KeyError(f"unknown section '{section}'. Valid: {sorted(SECTION_MODELS)}")
        validated = TypeAdapter(SECTION_MODELS[section]).validate_python(value)
        dumped = TypeAdapter(SECTION_MODELS[section]).dump_python(validated, mode="json", exclude_none=True)
        with self._locked():
            spec = self.load()
            spec[section] = dumped
            spec.setdefault("_provenance", {})[section] = {
                "author": author, "written_at": datetime.now(timezone.utc).isoformat()}
            self.save(spec)
        return dumped

    def completeness(self) -> dict[str, bool]:
        spec = self.load()
        return {s: s in spec for s in SECTION_MODELS}


def _cross_check(spec: dict[str, Any]) -> list[str]:
    """Referential-integrity warnings across sections (activities ↔ steps ↔ resources)."""
    warns = []
    acts = {a["name"] for a in spec.get("activities", [])}
    res = {r["name"] for r in spec.get("resources", [])}
    for v in spec.get("variants", []):
        for s in v.get("steps", []):
            if acts and s["activity"] not in acts:
                warns.append(f"variant {v['name']}: step '{s['activity']}' has no entry in activities")
    for a in spec.get("activities", []):
        for r in a.get("eligible_resources", []):
            if res and r not in res:
                warns.append(f"activity {a['name']}: resource '{r}' not in resources")
    if spec.get("variants"):
        tot = sum(v["probability"] for v in spec["variants"])
        if abs(tot - 1) > 0.02:
            warns.append(f"variant probabilities sum to {tot:.3f}, not 1")
    return warns[:20]


def make_spec_tools(store: SpecStore, agent_name: str, writable: list[str] | None = None) -> list:
    """Return ``read_spec`` (always) and ``write_spec_section`` (if the agent owns sections)."""
    writable = SECTION_OWNERS.get(agent_name, []) if writable is None else writable

    @tool(description=(
        "Read sections of the typed simulation spec (JSON). Pass only the sections you need "
        f"to keep context small. Sections: {', '.join(SECTION_MODELS)}. "
        "Returns {section: content}; missing sections are listed under 'missing'."
    ))
    def read_spec(sections: list[str] | None = None) -> dict[str, Any]:
        spec = store.load()
        wanted = sections or [s for s in SECTION_MODELS if s != "log_schema"]
        out = {s: spec[s] for s in wanted if s in spec}
        miss = [s for s in wanted if s not in spec]
        if miss:
            out["missing"] = miss
        return out

    tools = [read_spec]
    if not writable:
        return tools

    schemas = {s: SECTION_MODELS[s] for s in writable}

    @tool(description=(
        "Write (replace) one section of the typed simulation spec. The content is validated "
        "against the section schema; on error nothing is written and the validation message "
        "is returned. merge=True updates instead of replacing: list sections are merged by "
        "`name` (same name replaced, new names appended), dict sections key by key. Prefer the "
        "draft_* tools for whole sections; use this tool for corrections. Otherwise the "
        "validation message "
        f"is returned. You may write: {', '.join(writable)}. Copy numbers verbatim from tool "
        "results and set `source` on every distribution. Never include observed case ids or "
        "timestamps as model inputs (no trace replay). Shapes:\n"
        + "\n".join(f"- {s}: {SECTION_EXAMPLES[s]}" for s in writable)
    ))
    def write_spec_section(section: str, content: dict | list | str, merge: bool = False) -> str:
        if section not in schemas:
            return f"Error: you may only write sections {writable}; '{section}' is owned by another phase."
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError as exc:
                return f"Error: content is not valid JSON ({exc}). Pass the section as a JSON object or array."
        if isinstance(content, dict) and set(content) == {section}:
            content = content[section]  # tolerate {"<section>": ...} wrapping
        if merge:
            current = store.get(section)
            if isinstance(current, list) and isinstance(content, list) and all(isinstance(x, str) for x in current + content):
                content = current + [x for x in content if x not in current]  # e.g. assumptions
            elif isinstance(current, list) and isinstance(content, list):
                by_name = {x.get("name"): x for x in current if isinstance(x, dict)}
                for x in content:  # replace entries with the same name, append new ones
                    by_name[x.get("name")] = x
                content = list(by_name.values())
            elif isinstance(current, dict) and isinstance(content, dict):
                content = {**current, **content}
        try:
            store.put(section, content, author=agent_name)
        except ValidationError as exc:
            errs = "\n".join(f"- {'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()[:10])
            return (f"Validation error in section '{section}' — nothing written:\n{errs}\n"
                    f"Expected shape: {SECTION_EXAMPLES[section]}")
        except Exception as exc:
            return f"Error writing section '{section}': {type(exc).__name__}: {exc}"
        warns = _cross_check(store.load())
        return (f"Section '{section}' written to {store.rel_path}."
                + (("\nCross-section warnings:\n- " + "\n- ".join(warns)) if warns else ""))

    tools.append(write_spec_section)
    return tools


def make_spec_status_tool(store: SpecStore):
    """Orchestrator-facing: which spec sections exist (no content)."""

    @tool(description="Report which sections of the simulation spec exist, plus cross-section consistency warnings.")
    def check_spec_status() -> dict[str, Any]:
        return {"sections_present": store.completeness(), "warnings": _cross_check(store.load())}

    return check_spec_status


def _fmt_dist(d: dict | None) -> str:
    if not d:
        return "—"
    fam, p = d.get("family"), d.get("params", {})
    if fam == "empirical_quantiles":
        q = d.get("quantiles") or []
        core = f"empirical quantiles [{q[0]:.3g} … {q[len(q) // 2]:.3g} … {q[-1]:.3g}]" if q else fam
    elif fam == "categorical":
        core = "categorical " + ", ".join(f"{v:g}:{pr:.2f}" for v, pr in zip(d.get("values", []), d.get("probs", [])))
    else:
        core = f"{fam}(" + ", ".join(f"{k}={v:.4g}" for k, v in p.items()) + ")"
    extra = []
    if d.get("mean") is not None:
        extra.append(f"mean {d['mean']:.4g}")
    if d.get("n") is not None:
        extra.append(f"n={d['n']}")
    if d.get("source"):
        extra.append(f"src {d['source']}")
    return core + (f" ({'; '.join(extra)})" if extra else "")


def render_spec_markdown(spec: dict[str, Any]) -> str:
    """Human-readable view of the spec for HITL review (generated, never hand-edited)."""
    L = ["# Simulation specification (generated from simulation_spec.json — do not edit)", ""]
    w = spec.get("window")
    if w:
        L += ["## Window", f"t0 {w.get('t0')} · horizon {w.get('horizon_s', 0):.0f} s · "
              f"first {w.get('first_activity')} · terminal {w.get('terminal_activity')}", ""]
    if spec.get("resources"):
        L += ["## Resources", "| Resource | Class | Capacity |", "|---|---|---|"]
        L += [f"| {r['name']} | {r.get('resource_class')} | {r.get('capacity', 1)} |" for r in spec["resources"]]
        L.append("")
    if spec.get("activities"):
        L += ["## Activities", "| Activity | Resources | Service time | P(failure) |", "|---|---|---|---|"]
        L += [f"| {a['name']} | {', '.join(a.get('eligible_resources', []))} | {_fmt_dist(a.get('duration'))} | "
              f"{a.get('failure_probability', 0):.3f} |" for a in spec["activities"]]
        L.append("")
    if spec.get("variants"):
        L += ["## Variants"]
        for v in spec["variants"]:
            L.append(f"### {v['name']} — p={v.get('probability', 0):.3f}, early exit p={v.get('early_exit_probability', 0):.2f}")
            for i, st in enumerate(v.get("steps", [])):
                res = ", ".join(f"{k} {x:.0%}" for k, x in (st.get("resources") or {}).items())
                flags = (" ∥ concurrent with previous" if st.get("concurrent_with_previous") else "") + \
                        (f" (p={st['probability']:.2f})" if st.get("probability", 1) < 1 else "")
                L.append(f"{i + 1}. {st['activity']} [{res}]{flags}")
            L.append("")
    a = spec.get("arrivals")
    if a:
        L += ["## Arrivals", f"model: **{a.get('model')}**"]
        for k in ("interarrival", "burst_size", "intra_burst_iat", "inter_burst_gap"):
            if a.get(k):
                L.append(f"- {k}: {_fmt_dist(a[k])}")
        if a.get("wip_cap"):
            L.append(f"- wip_cap: {a['wip_cap']}")
        L.append("")
    cp = spec.get("control_policies")
    if cp:
        L += ["## Control policies", f"- queue discipline: {cp.get('queue_discipline')}",
              f"- priority order: {cp.get('priority_order')}", f"- release rule: {cp.get('release_rule')}",
              f"- intra-case concurrency: {cp.get('intra_case_concurrency')}", ""]
    if spec.get("assumptions"):
        L += ["## Assumptions"] + [f"- {x}" for x in spec["assumptions"]] + [""]
    prov = spec.get("_provenance", {})
    if prov:
        L += ["## Provenance", "| Section | Author | Written |", "|---|---|---|"]
        L += [f"| {k} | {v.get('author')} | {v.get('written_at')} |" for k, v in prov.items()]
    return "\n".join(L) + "\n"


def section_json_schema(section: str) -> dict:
    """JSON schema of a section (used in prompts so the agents see the exact shape)."""
    from pydantic import TypeAdapter
    return TypeAdapter(SECTION_MODELS[section]).json_schema()
