"""Tests for the deterministic discovery tools on the Fischertechnik blocks."""
import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import evaluate_v2 as ev  # noqa: E402
from src.data_extraction_tools import discovery as D  # noqa: E402
from src.data_extraction_tools.eventlog import LogSchema, build_instances  # noqa: E402

SCHEMA = dict(case_col="case", activity_col="concept:name", resource_col="org:resource",
              start_col="time:timestamp", end_col="operation_end_time", variant_col="process_model_id",
              lifecycle_col="lifecycle:transition", instance_col="identifier:id", enabled_value="scheduled",
              start_value="start", complete_value="complete", state_col="lifecycle:state")


def _csv(b):
    return os.path.join(ROOT, f"data/fischertechnik_lab_{b}/block-{b}.csv")


@pytest.fixture(scope="module")
def blocks():
    out = {}
    for b in "ABC":
        df = pd.read_csv(_csv(b))
        inst, meta = build_instances(df, LogSchema(**SCHEMA))
        out[b] = (df, inst, meta)
    return out


@pytest.mark.parametrize("b", list("ABC"))
def test_build_instances_matches_evaluate_v2(blocks, b):
    _, inst, meta = blocks[b]
    real, T = ev.load_real(_csv(b))
    assert meta["T"] == pytest.approx(T)
    m = real.merge(inst, left_on=["case_id", "activity", "service_start"],
                   right_on=["case_id", "activity", "start"], how="outer", indicator=True)
    assert (m["_merge"] == "both").all()
    assert np.allclose(m["step_release"], m["enabled"])
    assert np.allclose(m["operation_end_time"], m["end"])
    assert (m["lifecycle:state"] == m["state"]).all()


def test_censoring_block_A(blocks):
    _, inst, meta = blocks["A"]
    c = D.detect_censoring(inst, meta["T"])
    assert c["inferred_first_activity"] == "/hbw/unload"
    assert c["inferred_terminal_activity"] == "/hbw/store"
    # the user context names WF_104_21, WF_108_18, WF_109_16 (and WF_1107_17) as incomplete at the window end
    assert {"WF_104_21", "WF_108_18", "WF_109_16"} <= set(c["right_censored"])
    assert c["n_complete"] == 3
    assert "WF_104_20" in c["missing_first_activity"]
    json.dumps(c)


@pytest.mark.parametrize("b", ["B", "C"])
def test_dispatching_rejects_fifo_at_hbw(blocks, b):
    _, inst, _ = blocks[b]
    r = D.test_dispatching_rules(inst)["by_resource_class"]["hbw"]
    assert r["fifo_rejected"]
    assert r["agreement"]["activity_priority"] >= r["agreement"]["FIFO"] + 0.3
    assert r["learned_activity_priority"][-1] == "/hbw/unload"      # new orders have lowest priority
    assert D.test_dispatching_rules(inst)["by_resource_class"]["vgr"]["fifo_rejected"] is False


def test_waiting_decomposition_shares(blocks):
    _, inst, _ = blocks["C"]
    w = D.decompose_waiting_times(inst)
    hbw = w["by_resource_class"]["hbw"]
    assert hbw["share_prioritization"] > 0.15
    tot = hbw["share_contention"] + hbw["share_prioritization"] + hbw["share_extraneous"]
    assert tot == pytest.approx(1.0, abs=0.01)


def test_two_regime_iat_block_C(blocks):
    _, inst, _ = blocks["C"]
    rel = np.sort(inst.groupby("case_id")["enabled"].min().to_numpy())
    r = D.two_regime_iat(np.diff(rel))
    assert r["regime"] == "two_regime"
    assert 1.0 <= r["burst_iat"]["mean"] <= 6.0           # vs. 12.7 s IQR-"clean" mean
    assert r["gap_iat"]["mean"] > 100
    assert sum(r["burst_size"]["values"]) == len(rel)


def test_two_regime_single_for_poisson():
    rng = np.random.default_rng(0)
    assert D.two_regime_iat(rng.exponential(60, 200))["regime"] == "single"


def test_release_and_concurrency(blocks):
    _, inst, meta = blocks["C"]
    r = D.detect_release_control(inst, meta["T"])
    assert r["max_wip"] == 9 and r["release_spacing"]["regime"] == "two_regime"
    real, T = ev.load_real(_csv("C"))
    gt = ev.kpis(real, T)
    done = inst.loc[(inst["activity"] == "/hbw/store") & (inst["state"] == "success"), "case_id"].unique().tolist()
    cc = D.detect_intra_case_concurrency(inst, completed_cases=done)
    assert cc["overlapping_steps_per_completed_case"] == pytest.approx(gt["overlapping_steps_per_case"], abs=1e-3)


def test_tools_write_evidence(blocks, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    df, _, _ = blocks["B"]
    store = {}
    set_schema = D.make_set_log_schema_tool(df, lambda s, m: store.update(schema=s, meta=m))
    tools = {t.name: t for t in D.make_discovery_tools(df, lambda: store.get("schema"), "reports/evidence")}
    assert "set_log_schema" in tools["detect_censoring"].invoke({})          # schema not confirmed yet
    res = set_schema.invoke(SCHEMA)
    assert res["status"].startswith("log schema confirmed") and not res["warnings"]
    for name, t in tools.items():
        out = t.invoke({})
        assert "error" not in out, (name, out)
        json.dumps(out)
        assert os.path.exists(tmp_path / out["evidence_file"])
    assert "error" in set_schema.invoke({**SCHEMA, "case_col": "nope"})
