"""Tests for the deterministic verification tools (proposal P5)."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.data_extraction_tools.eventlog import LogSchema  # noqa: E402
from src.genai4simpy_agent.verification import (  # noqa: E402
    behavioural_check, contract_test, make_verification_tools, metamorphic_tests, static_scan,
)

FIX = os.path.join(ROOT, "tests", "fixtures")
TOY = os.path.join(FIX, "toy_v2_model.py")
BROKEN = os.path.join(FIX, "toy_broken_model.py")
FT_SCHEMA = LogSchema(case_col="case", activity_col="concept:name", resource_col="org:resource",
                      start_col="time:timestamp", end_col="operation_end_time", variant_col="process_model_id",
                      lifecycle_col="lifecycle:transition", instance_col="identifier:id", enabled_value="scheduled",
                      start_value="start", complete_value="complete", state_col="lifecycle:state")
PRIOR = {"A": "colossal-unyielding-flounder", "B": "silent-xanthic-worm", "C": "elated-shellfish-of-attraction"}
V2_ONLY = {"symbol:ARRIVAL_RATE_SCALE", "symbol:FAILURES_ENABLED", "v2_columns", "knobs_read_at_runtime",
           "no_trace_replay"}  # trace replay is the documented O5 defect of the block-A model


def _prior(b):
    return os.path.join(ROOT, f"output/fischertechnik_lab_{b}/{PRIOR[b]}/reports/simulation/simulation.py")


def _block(b):
    return pd.read_csv(os.path.join(ROOT, f"data/fischertechnik_lab_{b}/block-{b}.csv"))


@pytest.mark.parametrize("b", list(PRIOR))
def test_prior_models_pass_v1_checks(b):
    df = _block(b)
    r = contract_test(_prior(b), None, set(df["case"].astype(str)))
    failed = {c["name"] for c in r["checks"] if not c["passed"]}
    assert failed - V2_ONLY == set(), r
    assert {"symbol:ARRIVAL_RATE_SCALE", "v2_columns"} <= failed      # contract v1 models lack v2 symbols
    if b == "A":
        assert "no_trace_replay" in failed                             # block-A model replays observed case ids


def test_toy_v2_model_passes_all():
    spec = {"activities": [{"name": "/cut"}, {"name": "/paint"}], "variants": [{"name": "A"}, {"name": "B"}],
            "resources": [{"name": "m_1", "capacity": 1}, {"name": "m_2", "capacity": 1}]}
    r = contract_test(TOY, spec, {"WF_101_30"})
    assert r["passed"], [c for c in r["checks"] if not c["passed"]]


def test_spec_mismatch_detected():
    spec = {"activities": [{"name": "/cut"}], "resources": [{"name": "m_1", "capacity": 2}, {"name": "m_2", "capacity": 1}]}
    failed = {c["name"] for c in contract_test(TOY, spec)["checks"] if not c["passed"]}
    assert {"vocabulary:activity", "capacities_match_spec"} <= failed


def test_broken_model_fails_static_and_import_checks():
    r = contract_test(BROKEN, None, {"WF_101_30", "WF_999_1"})
    failed = {c["name"] for c in r["checks"] if not c["passed"]}
    assert {"no_trace_replay", "no_file_io", "import_is_side_effect_free"} <= failed
    assert not r["passed"]


def test_static_scan_ignores_main_block():
    src = "import pandas as pd\nX=1\nif __name__ == '__main__':\n    pd.read_csv('x.csv')\n"
    assert next(c for c in static_scan(src) if c["name"] == "no_file_io")["passed"]


def test_behavioural_check_block_c_finite():
    r = behavioural_check(_prior("C"), _block("C"), FT_SCHEMA, m=10)
    assert r["ok"] and r["terminal_activity"] == "/hbw/store"
    for k in ("completed_cases", "flow_time_completed_s", "failure_rate"):
        assert np.isfinite(r["kpis"][k]["mean"]) and np.isfinite(r["kpis"][k]["gt"])
    assert np.isfinite(r["kpis"]["activity_mape"]["mean"])
    assert np.isfinite(r["distances"]["cycle_time_emd_s"]) and np.isfinite(r["distances"]["bigram_jsd"])
    assert any("parallelism" in f for f in r["findings"])          # documented mechanism finding


def test_metamorphic_toy():
    r = metamorphic_tests(TOY, m=5)
    rel = {x["relation"][:3]: x["status"] for x in r["relations"]}
    assert r["ok"] and r["passed"]
    assert rel["MR3"] == "pass" and rel["MR2"] == "pass" and rel["MR1"] == "pass"


def test_tool_factory(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    sim_dir = os.path.relpath(tmp_path, ROOT)
    import shutil
    shutil.copy(TOY, tmp_path / "simulation.py")
    tools = make_verification_tools(sim_dir, pd.DataFrame({"case": ["x"]}), lambda: {"case_col": "case"},
                                    lambda: None, os.path.join(sim_dir, "evidence"))
    assert [t.name for t in tools] == ["run_contract_test", "run_behavioural_check", "run_metamorphic_tests"]
    out = tools[0].invoke({})
    assert out["passed"] and os.path.exists(os.path.join(ROOT, out["evidence_file"]))
