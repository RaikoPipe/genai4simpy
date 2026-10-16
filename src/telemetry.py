"""Run telemetry: tokens, latency, tool calls/errors, retries and guard triggers per agent.

One ``Telemetry`` object per pipeline run. ``experiment.py`` feeds it from the
``astream_events`` stream; the retry / thrash-guard middlewares report into the
module-level ``CURRENT`` instance. Full (untruncated) tool I/O goes to a JSONL
file; aggregated numbers to ``telemetry.json``.
"""
from __future__ import annotations

import json
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

CURRENT: "Telemetry | None" = None


def _agent_from_ns(metadata: dict) -> str:
    ns = metadata.get("langgraph_checkpoint_ns", "") or ""
    # Namespaces look like "tools:<uuid>|model:<uuid>"; deepagents tags sub-agent runs
    # with lc_agent_name, which is the most reliable label.
    return metadata.get("lc_agent_name") or (ns.split(":")[0] if ns else "orchestrator")


class Telemetry:
    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.tool_log = open(os.path.join(out_dir, "tool_calls.jsonl"), "a", encoding="utf-8")
        self.started = time.perf_counter()
        self.agents: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.events: list[dict[str, Any]] = []
        self._model_t0: dict[str, float] = {}
        self._tool_t0: dict[str, float] = {}
        self.peak_input_tokens: dict[str, int] = defaultdict(int)

    # ---- model calls --------------------------------------------------------
    def model_start(self, run_id: str):
        self._model_t0[run_id] = time.perf_counter()

    def model_end(self, run_id: str, agent: str, output: Any):
        a = self.agents[agent]
        a["model_calls"] += 1
        a["model_latency_s"] += time.perf_counter() - self._model_t0.pop(run_id, time.perf_counter())
        usage = getattr(output, "usage_metadata", None) or {}
        a["input_tokens"] += usage.get("input_tokens", 0)
        a["output_tokens"] += usage.get("output_tokens", 0)
        reasoning = (usage.get("output_token_details") or {}).get("reasoning", 0)
        a["reasoning_tokens"] += reasoning
        self.peak_input_tokens[agent] = max(self.peak_input_tokens[agent], usage.get("input_tokens", 0))

    # ---- tool calls -----------------------------------------------------------
    def tool_start(self, run_id: str, agent: str, name: str, tool_input: Any):
        self._tool_t0[run_id] = time.perf_counter()
        self.agents[agent]["tool_calls"] += 1
        self._write({"ev": "start", "run_id": run_id, "agent": agent, "tool": name, "input": tool_input})

    def tool_end(self, run_id: str, agent: str, name: str, output: Any, error: bool = False):
        dt = time.perf_counter() - self._tool_t0.pop(run_id, time.perf_counter())
        a = self.agents[agent]
        a["tool_latency_s"] += dt
        text = getattr(output, "content", output)
        text = text if isinstance(text, str) else str(text)
        is_err = error or text.lstrip().lower().startswith(("error", "validation error")) or '"error"' in text[:200]
        if is_err:
            a["tool_errors"] += 1
        self._write({"ev": "error" if error else "end", "run_id": run_id, "agent": agent, "tool": name,
                     "latency_s": round(dt, 3), "tool_error": bool(is_err), "output": text})

    # ---- middleware events ------------------------------------------------------
    def event(self, kind: str, **detail):
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "kind": kind, **detail}
        self.events.append(rec)
        print(f"\n[telemetry] {kind}: {detail}", flush=True)

    def _write(self, rec: dict):
        self.tool_log.write(json.dumps(rec, default=str) + "\n")
        self.tool_log.flush()

    def summary(self) -> dict[str, Any]:
        per_agent = {k: {m: round(v, 2) for m, v in d.items()} for k, d in self.agents.items()}
        tot = defaultdict(float)
        for d in self.agents.values():
            for m, v in d.items():
                tot[m] += v
        kinds = defaultdict(int)
        for e in self.events:
            kinds[e["kind"]] += 1
        return {"wall_clock_s": round(time.perf_counter() - self.started, 1),
                "totals": {m: round(v, 2) for m, v in tot.items()},
                "per_agent": per_agent,
                "peak_input_tokens": dict(self.peak_input_tokens),
                "event_counts": dict(kinds), "events": self.events[-200:]}

    def close(self):
        name, i = "telemetry.json", 1
        while os.path.exists(os.path.join(self.out_dir, name)):  # one file per (resumed) session
            i += 1
            name = f"telemetry_{i}.json"
        with open(os.path.join(self.out_dir, name), "w", encoding="utf-8") as f:
            json.dump(self.summary(), f, indent=2, default=str)
        self.tool_log.close()


def record(kind: str, **detail):
    """Report a middleware event (retry, guard trigger) to the active run, if any."""
    if CURRENT is not None:
        CURRENT.event(kind, **detail)
