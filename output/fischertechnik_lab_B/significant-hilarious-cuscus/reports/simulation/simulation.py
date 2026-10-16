"""SimPy model of the fischertechnik lab (run significant-hilarious-cuscus).

Implements the typed simulation spec exactly:
- 15 single-capacity resources; hbw_1/hbw_2 served by activity priority
  (store > get_empty_bucket > store_empty_bucket > unload, ties FIFO), all
  others FIFO.
- Two-regime bursty arrivals (burst size categorical, intra-burst IAT and
  inter-burst gap from empirical quantile tables), first release at t=0.
- 9 variants with canonical step sequences, alternative sequences
  (other_sequences), concurrent_with_previous intra-case parallelism,
  per-variant early exits (step-index based, consistent with activity based).
- Per-activity duration distributions (empirical quantiles / triangular).
- Failures: /wt/pick_up_and_transport on wt_1 (p=0.1481, retry on same
  resource after fixed 30.182 s delay, retry always succeeds);
  /hbw/store_empty_bucket (p=0.0541, absorbed failure, no retry).
"""

import random

import numpy as np
import pandas as pd
import simpy

# scipy is imported lazily inside make_sampler to keep module import fast.
_stats = None

# ---------------------------------------------------------------------------
# Contract knobs (read at call time inside run_single_replication)
# ---------------------------------------------------------------------------
RESOURCE_CAPACITIES = {
    "dm_2": 1, "hbw_1": 1, "hbw_2": 1, "hw_1": 1, "mm_1": 1, "mm_2": 1,
    "ov_1": 1, "ov_2": 1, "pm_1": 1, "sm_1": 1, "sm_2": 1, "vgr_1": 1,
    "vgr_2": 1, "wt_1": 1, "wt_2": 1,
}
SIMULATION_TIME: float = 5943.712523
ARRIVAL_RATE_SCALE: float = 1.0
FAILURES_ENABLED: bool = True

# ---------------------------------------------------------------------------
# Activity data (from spec `activities`)
# ---------------------------------------------------------------------------
ACTIVITIES = {
    "/vgr/pick_up_and_transport": {
        "eligible_resources": ["vgr_2"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [31.332, 34.11345, 35.7325, 36.2004, 36.7174, 36.769, 36.9834, 37.2038, 43.1282, 43.2263, 43.3105, 43.5422, 43.6456, 43.68895, 43.724, 43.926, 44.1782, 44.45975, 44.5129, 44.7262, 46.188],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/wt/pick_up_and_transport": {
        "eligible_resources": ["wt_1"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [25.917, 25.9256, 25.9796, 26.03, 26.03, 26.0305, 26.031, 26.0317, 26.032, 26.032, 26.034, 26.0467, 26.1354, 26.141, 26.141, 26.141, 26.1416, 26.2169, 26.2506, 26.35, 28.887],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.1481, "on_failure": "retry",
        "retry_delay": 30.182, "failure_resources": ["wt_1"]},
    "/hbw/store_empty_bucket": {
        "eligible_resources": ["hbw_1", "hbw_2"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [9.298, 32.1247, 32.4444, 32.9386, 34.2028, 34.375, 36.0236, 36.2452, 36.558, 36.7812, 37.295, 38.035, 38.2732, 39.7671, 39.9218, 40.257, 40.5028, 40.6824, 41.4902, 42.8309, 44.344],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0541, "on_failure": "none"},
    "/hbw/unload": {
        "eligible_resources": ["hbw_2"],
        "duration": {"family": "triang", "params": {"c": 1e-06, "loc": 32.530974, "scale": 22.094764}},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/hbw/get_empty_bucket": {
        "eligible_resources": ["hbw_1"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [33.594, 33.7466, 34.9316, 36.6342, 36.7966, 36.882, 36.9432, 37.0209, 37.032, 37.0974, 37.25, 37.3046, 38.2716, 39.7413, 40.1214, 40.2785, 41.0644, 43.6453, 46.789, 49.563, 51.719],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/hbw/store": {
        "eligible_resources": ["hbw_1"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [33.768, 34.08195, 34.2879, 34.36785, 34.8906, 35.68775, 36.8649, 37.05535, 37.0632, 37.06385, 37.204, 37.4892, 38.1184, 38.65625, 39.0959, 39.21875, 40.0276, 41.21225, 41.7615, 42.0899, 42.229],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/hw/human_review": {
        "eligible_resources": ["hw_1"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [0.109, 0.6154, 1.0511, 1.20345, 1.3348, 1.50525, 1.9272, 2.1961, 2.4732, 2.8136, 5.6335, 10.3033, 12.8574, 13.44175, 17.793, 31.5565, 34.6348, 43.5887, 72.9473, 87.8392, 98.143],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/mm/deburr": {
        "eligible_resources": ["mm_1", "mm_2"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [13.843, 13.894, 14.0304, 14.0406, 14.059, 14.079, 14.1444, 14.218, 14.218, 14.2292, 14.233, 14.2332, 14.2408, 14.26, 14.278, 14.438, 14.4418, 14.4718, 14.8192, 15.8552, 16.45],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/mm/drill": {
        "eligible_resources": ["mm_2"],
        "duration": {"family": "triang", "params": {"c": 0.978412, "loc": 5.281, "scale": 10.376}},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/mm/mill": {
        "eligible_resources": ["mm_1", "mm_2"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [4.906, 5.0599, 5.0786, 5.0797, 5.0866, 5.0915, 5.0928, 5.1033, 5.125, 5.1407, 5.282, 5.282, 5.2828, 5.3257, 5.794, 10.071, 14.1164, 14.228, 14.296, 14.5012, 14.656],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/mm/transport_from_to": {
        "eligible_resources": ["mm_1", "mm_2"],
        "duration": {"family": "triang", "params": {"c": 0.041346, "loc": 11.751, "scale": 11.295}},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/ov/burn": {
        "eligible_resources": ["ov_2"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [9.25, 18.74575, 26.5416, 26.6879, 27.0774, 27.8925, 29.2575, 31.08075, 31.7212, 31.9181, 34.407, 36.8938, 37.0676, 37.2747, 37.5706, 37.8185, 38.0088, 39.2701, 41.1434, 121.2258, 218.688],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/ov/temper": {
        "eligible_resources": ["ov_1"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [50.921, 50.97235, 51.0366, 51.1159, 51.5162, 51.8185, 51.9212, 51.9535, 52.0332, 52.24835, 52.4065, 52.6626, 53.3022, 53.7105, 53.9705, 53.98025, 54.0396, 54.1238, 54.1342, 54.216, 54.359],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/pm/punch_gill": {
        "eligible_resources": ["pm_1"],
        "duration": {"family": "triang", "params": {"c": 0.073406, "loc": 27.453, "scale": 0.831}},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/pm/punch_recesses": {
        "eligible_resources": ["pm_1"],
        "duration": {"family": "triang", "params": {"c": 0.482301, "loc": 23.157, "scale": 0.452}},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/pm/punch_ribbing": {
        "eligible_resources": ["pm_1"],
        "duration": {"family": "triang", "params": {"c": 0.04196, "loc": 22.828, "scale": 8.532}},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/sm/sort": {
        "eligible_resources": ["sm_1", "sm_2"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [8.728, 8.731, 8.7335, 9.04325, 9.968, 10.03925, 10.219, 10.475, 10.775, 10.7915, 10.797, 11.08225, 11.938, 12.1375, 12.398, 13.159, 14.86, 17.76625, 18.938, 26.2035, 47.391],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/sm/transport": {
        "eligible_resources": ["sm_1", "sm_2"],
        "duration": {"family": "empirical_quantiles",
                     "quantiles": [14.093, 14.25, 14.254, 14.437, 14.453, 14.656, 14.687, 14.829, 18.078, 18.327, 18.906, 19.156, 19.406, 19.735, 20.656, 20.813, 21.0, 23.259, 25.957, 31.812, 44.468],
                     "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/dm/cylindrical_drill": {
        "eligible_resources": ["dm_2"],
        "duration": {"family": "triang", "params": {"c": 0.823938, "loc": 26.907, "scale": 5.907}},
        "failure_probability": 0.0, "on_failure": "retry"},
    "/dm/lower": {
        "eligible_resources": ["dm_2"],
        "duration": {"family": "triang", "params": {"c": 0.613953, "loc": 13.814, "scale": 0.215}},
        "failure_probability": 0.0, "on_failure": "retry"},
}

# hbw activity priority (lower value = served first); unlisted -> len(order)
HBW_PRIORITY_ORDER = ["/hbw/store", "/hbw/get_empty_bucket",
                      "/hbw/store_empty_bucket", "/hbw/unload"]


def make_sampler(dist: dict, rng: np.random.Generator):
    """Spec distribution -> zero-argument sampler (seconds, never negative)."""
    fam, p = dist["family"], dist.get("params", {})
    if fam == "constant":
        return lambda: float(p["value"])
    if fam == "categorical":
        v, pr = np.asarray(dist["values"]), np.asarray(dist["probs"])
        return lambda: float(rng.choice(v, p=pr / pr.sum()))
    if fam == "empirical_quantiles":
        q, pr = np.asarray(dist["quantiles"]), np.asarray(dist["quantile_probs"])
        return lambda: float(np.interp(rng.uniform(), pr, q))
    global _stats
    if _stats is None:
        from scipy import stats as _stats
    d = getattr(_stats, fam)(**p)
    return lambda: max(0.0, float(d.rvs(random_state=rng)))


# ---------------------------------------------------------------------------
# Variant data (from spec `variants`)
# ---------------------------------------------------------------------------
def _step(activity, resources, concurrent=False, probability=1.0):
    return {"activity": activity, "probability": probability,
            "resources": resources, "concurrent_with_previous": concurrent}


def _one(res):
    return {res: 1.0}


VARIANTS = {
    "WF_101": {
        "probability": 0.1579,
        "steps": [
            _step("/hbw/unload", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/hbw/store_empty_bucket", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1"), concurrent=True),
            _step("/ov/burn", _one("ov_1")),
            _step("/ov/temper", _one("ov_1")),
            _step("/wt/pick_up_and_transport", _one("wt_1")),
            _step("/mm/mill", _one("mm_1")),
            _step("/mm/deburr", _one("mm_1")),
            _step("/sm/sort", _one("sm_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hw/human_review", _one("hw_1")),
            _step("/hbw/get_empty_bucket", _one("hbw_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1"), concurrent=True),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hbw/store", _one("hbw_1")),
        ],
        "early_exit_probability": 0.667,
        "early_exit_after_n_steps": {12: 0.75, 15: 0.25},
        "early_exit_after": {"/hw/human_review": 0.75, "/vgr/pick_up_and_transport": 0.25},
        "other_sequences": [],
    },
    "WF_102": {
        "probability": 0.1316,
        "steps": [
            _step("/hbw/unload", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/hbw/store_empty_bucket", _one("hbw_2")),
            _step("/ov/burn", _one("ov_2"), concurrent=True),
            _step("/wt/pick_up_and_transport", _one("wt_2")),
            _step("/mm/drill", _one("mm_2")),
            _step("/sm/transport", _one("sm_2")),
            _step("/dm/lower", _one("dm_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hw/human_review", _one("hw_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hbw/get_empty_bucket", _one("hbw_1"), concurrent=True),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hbw/store", _one("hbw_1")),
        ],
        "early_exit_probability": 0.333,
        "early_exit_after_n_steps": {10: 1.0},
        "early_exit_after": {"/hw/human_review": 1.0},
        "other_sequences": [
            {
                "probability": 0.333,
                "steps": [
                    _step("/hbw/unload", _one("hbw_2")),
                    _step("/vgr/pick_up_and_transport", _one("vgr_2")),
                    _step("/hbw/store_empty_bucket", _one("hbw_2")),
                    _step("/wt/pick_up_and_transport", _one("wt_2")),
                    _step("/mm/drill", _one("mm_2")),
                    _step("/sm/transport", _one("sm_2")),
                    _step("/dm/lower", _one("dm_2")),
                    _step("/hbw/store_empty_bucket", _one("hbw_1")),
                    _step("/vgr/pick_up_and_transport", _one("vgr_1")),
                    _step("/hw/human_review", _one("hw_1")),
                ],
            },
        ],
    },
    "WF_103": {
        "probability": 0.1316,
        "steps": [
            _step("/hbw/unload", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/hbw/store_empty_bucket", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1"), concurrent=True),
            _step("/ov/burn", _one("ov_1")),
            _step("/ov/temper", _one("ov_1")),
            _step("/wt/pick_up_and_transport", _one("wt_1")),
            _step("/mm/mill", _one("mm_1")),
            _step("/mm/deburr", _one("mm_1")),
            _step("/sm/transport", _one("sm_1")),
            _step("/pm/punch_recesses", _one("pm_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hw/human_review", _one("hw_1")),
        ],
        "early_exit_probability": 1.0,
        "early_exit_after_n_steps": {5: 0.2, 13: 0.8},
        "early_exit_after": {"/hw/human_review": 0.8, "/ov/burn": 0.2},
        "other_sequences": [],
    },
    "WF_104": {
        "probability": 0.1316,
        "steps": [
            _step("/hbw/unload", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/hbw/store_empty_bucket", _one("hbw_2")),
            _step("/ov/burn", _one("ov_2"), concurrent=True),
            _step("/wt/pick_up_and_transport", _one("wt_2")),
            _step("/mm/mill", _one("mm_2")),
            _step("/sm/sort", _one("sm_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/wt/pick_up_and_transport", _one("wt_1")),
            _step("/mm/deburr", _one("mm_1")),
            _step("/sm/transport", _one("sm_1")),
            _step("/pm/punch_gill", _one("pm_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hw/human_review", _one("hw_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hbw/get_empty_bucket", _one("hbw_1"), concurrent=True),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hbw/store", _one("hbw_1")),
        ],
        "early_exit_probability": 0.5,
        "early_exit_after_n_steps": {4: 0.5, 14: 0.5},
        "early_exit_after": {"/ov/burn": 0.5, "/hw/human_review": 0.5},
        "other_sequences": [],
    },
    "WF_105": {
        "probability": 0.1053,
        "steps": [
            _step("/hbw/unload", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/hbw/store_empty_bucket", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1"), concurrent=True),
            _step("/ov/burn", _one("ov_1")),
            _step("/wt/pick_up_and_transport", _one("wt_1")),
            _step("/mm/deburr", _one("mm_1")),
            _step("/sm/sort", _one("sm_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hw/human_review", _one("hw_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hbw/get_empty_bucket", _one("hbw_1"), concurrent=True),
            _step("/vgr/pick_up_and_transport", _one("vgr_1"), concurrent=True),
            _step("/hbw/store", _one("hbw_1")),
        ],
        "early_exit_probability": 0.5,
        "early_exit_after_n_steps": {8: 1.0},
        "early_exit_after": {"/sm/sort": 1.0},
        "other_sequences": [],
    },
    "WF_108": {
        "probability": 0.0789,
        "steps": [
            _step("/hbw/unload", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/hbw/store_empty_bucket", _one("hbw_2")),
            _step("/ov/burn", _one("ov_2"), concurrent=True),
            _step("/wt/pick_up_and_transport", _one("wt_2")),
            _step("/mm/drill", _one("mm_2")),
            _step("/mm/deburr", _one("mm_2")),
            _step("/sm/sort", _one("sm_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hw/human_review", _one("hw_1")),
            _step("/hbw/get_empty_bucket", _one("hbw_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1"), concurrent=True),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hbw/store", _one("hbw_1")),
        ],
        "early_exit_probability": 0.333,
        "early_exit_after_n_steps": {10: 1.0},
        "other_sequences": [
            {
                "probability": 0.333,
                "steps": [
                    _step("/hbw/unload", _one("hbw_2")),
                    _step("/vgr/pick_up_and_transport", _one("vgr_2")),
                    _step("/hbw/store_empty_bucket", _one("hbw_2")),
                    _step("/wt/pick_up_and_transport", _one("wt_2")),
                    _step("/mm/drill", _one("mm_2")),
                    _step("/mm/deburr", _one("mm_2")),
                    _step("/sm/sort", _one("sm_2")),
                    _step("/vgr/pick_up_and_transport", _one("vgr_2")),
                    _step("/vgr/pick_up_and_transport", _one("vgr_1")),
                    _step("/hw/human_review", _one("hw_1")),
                ],
            },
        ],
    },
    "WF_109": {
        "probability": 0.1053,
        "steps": [
            _step("/hbw/unload", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/hbw/store_empty_bucket", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1"), concurrent=True),
            _step("/ov/burn", _one("ov_1")),
            _step("/ov/temper", _one("ov_1")),
            _step("/wt/pick_up_and_transport", _one("wt_1")),
            _step("/mm/mill", _one("mm_1")),
            _step("/mm/deburr", _one("mm_1")),
            _step("/sm/transport", _one("sm_1")),
            _step("/pm/punch_ribbing", _one("pm_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hw/human_review", _one("hw_1")),
        ],
        "early_exit_probability": 1.0,
        "early_exit_after_n_steps": {13: 1.0},
        "other_sequences": [],
    },
    "WF_1106": {
        "probability": 0.1053,
        "steps": [
            _step("/hbw/unload", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/hbw/store_empty_bucket", _one("hbw_2")),
            _step("/ov/burn", _one("ov_2"), concurrent=True),
            _step("/wt/pick_up_and_transport", _one("wt_2")),
            _step("/mm/mill", _one("mm_2")),
            _step("/sm/transport", _one("sm_2")),
            _step("/dm/cylindrical_drill", _one("dm_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hw/human_review", _one("hw_1")),
            _step("/hbw/get_empty_bucket", _one("hbw_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hbw/store", _one("hbw_1")),
        ],
        "early_exit_probability": 0.5,
        "early_exit_after_n_steps": {8: 0.5, 10: 0.5},
        "other_sequences": [
            {
                "probability": 0.5,
                "steps": [
                    _step("/hbw/unload", _one("hbw_2")),
                    _step("/vgr/pick_up_and_transport", _one("vgr_2")),
                    _step("/hbw/store_empty_bucket", _one("hbw_2")),
                    _step("/ov/burn", _one("ov_2")),
                    _step("/wt/pick_up_and_transport", _one("wt_2")),
                    _step("/mm/transport_from_to", _one("mm_2")),
                    _step("/sm/transport", _one("sm_2")),
                    _step("/dm/cylindrical_drill", _one("dm_2")),
                    _step("/vgr/pick_up_and_transport", _one("vgr_1")),
                    _step("/hw/human_review", _one("hw_1")),
                    _step("/hbw/get_empty_bucket", _one("hbw_1")),
                    _step("/vgr/pick_up_and_transport", _one("vgr_1")),
                    _step("/vgr/pick_up_and_transport", _one("vgr_1")),
                    _step("/hbw/store", _one("hbw_1")),
                ],
            },
        ],
    },
    "WF_1107": {
        "probability": 0.0526,
        "steps": [
            _step("/hbw/unload", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_2")),
            _step("/hbw/store_empty_bucket", _one("hbw_2")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1"), concurrent=True),
            _step("/ov/burn", _one("ov_1")),
            _step("/wt/pick_up_and_transport", _one("wt_1")),
            _step("/mm/transport_from_to", _one("mm_1")),
            _step("/sm/transport", _one("sm_1")),
            _step("/pm/punch_ribbing", _one("pm_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hw/human_review", _one("hw_1")),
            _step("/hbw/get_empty_bucket", _one("hbw_1")),
            _step("/vgr/pick_up_and_transport", _one("vgr_1"), concurrent=True),
            _step("/vgr/pick_up_and_transport", _one("vgr_1")),
            _step("/hbw/store", _one("hbw_1")),
        ],
        "early_exit_probability": 0.0,
        "early_exit_after_n_steps": {},
        "other_sequences": [],
    },
}

# Arrival distributions (from spec `arrivals`)
BURST_SIZE_DIST = {
    "family": "categorical",
    "values": [1.0, 2.0, 4.0, 5.0, 6.0, 9.0],
    "probs": [0.5714, 0.0714, 0.1429, 0.0714, 0.0714, 0.0714],
}
INTRA_BURST_IAT_DIST = {
    "family": "empirical_quantiles",
    "quantiles": [0.562544, 0.627565, 0.650727, 0.675619, 0.705506, 0.740918, 0.874092, 0.974676, 1.15266, 1.334343, 1.442788, 1.640713, 1.817078, 2.305173, 2.745084, 3.05148, 3.601672, 4.862942, 5.715244, 6.56988, 9.872827],
    "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
}
INTER_BURST_GAP_DIST = {
    "family": "empirical_quantiles",
    "quantiles": [32.267429, 50.07675, 87.482551, 164.081316, 191.109939, 193.353492, 197.002202, 207.392298, 231.265165, 261.187908, 294.135588, 297.247312, 324.094333, 398.411949, 445.197189, 478.216241, 506.125087, 591.516175, 791.871745, 1049.853683, 1336.648804],
    "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
}


# ---------------------------------------------------------------------------
# Priority resource (hbw class): highest activity priority first, ties FIFO
# ---------------------------------------------------------------------------
class _ResourceRequest:
    """Request handle: .event succeeds when the resource is granted."""

    def __init__(self, env, activity):
        self.arrival = env.now
        self.activity = activity
        self.event = env.event()


class PriorityFIFOResource:
    """Resource served by (activity priority, arrival) order; ties FIFO.

    Grants are made synchronously: a request is granted immediately if the
    resource has free capacity, otherwise it is queued.  On release, the
    highest-priority waiting request (FIFO among equal priorities) is
    granted.  Mirrors simpy.Resource request semantics (request() -> handle
    with .event).
    """

    def __init__(self, env, capacity, priority_order):
        self.env = env
        self.capacity = capacity
        self.priority_order = list(priority_order)
        self.request_queue = []
        self.busy = 0

    def _rank(self, activity):
        try:
            return self.priority_order.index(activity)
        except (ValueError, TypeError):
            return len(self.priority_order)

    def request(self, activity=None):
        req = _ResourceRequest(self.env, activity)
        if self.busy < self.capacity:
            self.busy += 1
            req.event.succeed()
        else:
            self.request_queue.append(req)
        return req

    def release(self, req=None):
        self.busy -= 1
        while self.busy < self.capacity and self.request_queue:
            self.request_queue.sort(key=lambda r: (self._rank(r.activity), r.arrival))
            front = self.request_queue.pop(0)
            self.busy += 1
            front.event.succeed()


def request_resource(resource, activity):
    """Uniform request() for both custom and plain simpy resources."""
    if isinstance(resource, PriorityFIFOResource):
        return resource.request(activity=activity)
    return resource.request()


def _wait_request(req):
    """Yield until the request is granted (uniform for both resource types)."""
    if isinstance(req, _ResourceRequest):
        yield req.event
    else:
        yield req


# ---------------------------------------------------------------------------
# Processes
# ---------------------------------------------------------------------------
def _pick_resource(step, rng):
    """Sample the concrete resource from the step's resource shares."""
    shares = step["resources"]
    names = list(shares.keys())
    probs = np.asarray([shares[n] for n in names], dtype=float)
    probs = probs / probs.sum()
    return names[int(rng.choice(len(names), p=probs))]


def _resolve_exit_points(variant, steps):
    """Resolve the activity-based early_exit_after to {step_index: prob}.

    The spec provides both an activity-based exit map (early_exit_after) and a
    step-index map (early_exit_after_n_steps); the task directs to use the
    activity-based one.  For activities that occur more than once in the
    sequence, the step-index map disambiguates the correct occurrence.
    """
    act_map = variant.get("early_exit_after", {}) or {}
    idx_map = variant.get("early_exit_after_n_steps", {}) or {}
    resolved = {}
    for act, prob in act_map.items():
        idxs = [i + 1 for i, s in enumerate(steps) if s["activity"] == act]
        if not idxs:
            continue
        if len(idxs) == 1:
            resolved[idxs[0]] = prob
        else:
            # Disambiguate: pick the step-index with the same probability.
            match = [i for i, p in idx_map.items() if abs(p - prob) < 1e-9 and i in idxs]
            if match:
                resolved[match[0]] = prob
            else:  # fall back to the first occurrence
                resolved[idxs[0]] = prob
    return resolved


def _run_step(env, model, case_id, variant, step, arrival_time, rng,
              duration_samplers, failures_enabled):
    """Execute one step (with retry handling); log rows; return end time.

    Returns (operation_end_time, success_bool).  The request is made at the
    current sim time (the caller has already waited for the previous
    non-concurrent step).
    """
    activity = step["activity"]
    act_spec = ACTIVITIES[activity]
    resource_name = _pick_resource(step, rng)
    resource = model.resources[resource_name]

    def _serve():
        """Request, wait for grant, run for the sampled duration, release."""
        q_enter = env.now
        req = request_resource(resource, activity)
        yield from _wait_request(req)
        start = env.now
        duration = max(0.0, duration_samplers[activity]())
        yield env.timeout(duration)
        resource.release(req)
        return q_enter, start, start + duration

    q_enter, start, end = (yield from _serve())

    # Failure draw (only for activities with non-zero failure probability,
    # and only when failures are enabled).  wt failures apply only on wt_1
    # per spec; hbw/store_empty_bucket failures apply on hbw_1/hbw_2.
    failed = False
    fp = act_spec.get("failure_probability", 0.0)
    if failures_enabled and fp > 0.0:
        fail_res = act_spec.get("failure_resources")
        if fail_res is None or resource_name in fail_res:
            failed = rng.random() < fp

    if failed:
        model.rows.append({
            "case_id": case_id, "variant": variant, "activity": activity,
            "resource": resource_name, "case_arrival": arrival_time,
            "queue_enter": q_enter, "time:timestamp": start,
            "operation_end_time": end, "lifecycle:state": "failure",
        })
        if act_spec.get("on_failure") == "retry":
            # Retry on the same resource after the fixed setup delay.
            delay = act_spec.get("retry_delay", 0.0)
            yield env.timeout(delay)
            q_enter, start, end = (yield from _serve())
            # Retries do not fail again.
            model.rows.append({
                "case_id": case_id, "variant": variant, "activity": activity,
                "resource": resource_name, "case_arrival": arrival_time,
                "queue_enter": q_enter, "time:timestamp": start,
                "operation_end_time": end, "lifecycle:state": "success",
            })
            return end, True
        # on_failure == "none": absorbed failure, case continues.
        return end, False

    model.rows.append({
        "case_id": case_id, "variant": variant, "activity": activity,
        "resource": resource_name, "case_arrival": arrival_time,
        "queue_enter": q_enter, "time:timestamp": start,
        "operation_end_time": end, "lifecycle:state": "success",
    })
    return end, True


def _background_step(env, model, case_id, variant, step, arrival_time, rng,
                     duration_samplers, failures_enabled, done_event):
    """Run a step in the background; signal done_event when finished."""
    yield from _run_step(env, model, case_id, variant, step, arrival_time, rng,
                         duration_samplers, failures_enabled)
    done_event.succeed()


def case_process(env, model, case_id, variant_name, arrival_time, case_rng):
    """Walk the variant's steps in order; handle concurrency and early exit."""
    rng = case_rng
    variant = VARIANTS[variant_name]
    failures_enabled = model.failures_enabled
    duration_samplers = model.case_duration_samplers(case_rng)

    # Choose sequence: canonical or an alternative (other_sequences).
    steps = variant["steps"]
    for alt in variant["other_sequences"]:
        if rng.random() < alt["probability"]:
            steps = alt["steps"]
            break

    # Early exit: draw once per case.  The activity-based exit map
    # (early_exit_after) is authoritative per the task; it is resolved to
    # step indices against the chosen sequence (the step-index map is used
    # only to disambiguate repeated activities).
    exit_after = len(steps)  # complete the whole sequence
    if variant["early_exit_probability"] > 0.0 and rng.random() < variant["early_exit_probability"]:
        resolved = _resolve_exit_points(variant, steps)
        if resolved:
            idxs = sorted(resolved.keys())
            probs = np.asarray([resolved[i] for i in idxs])
            probs = probs / probs.sum()
            exit_after = int(idxs[int(rng.choice(len(idxs), p=probs))])

    background = []  # done-events of concurrent (background) steps
    n_steps = len(steps)
    for i, step in enumerate(steps):
        if rng.random() >= step["probability"]:
            continue  # skip this step
        # A step is backgrounded (runs in parallel) if it is itself flagged
        # concurrent_with_previous (it overlaps the previous step) OR the
        # next step is flagged concurrent_with_previous (this step must still
        # be running when the next one starts).  A non-concurrent step joins
        # all background steps first, then runs inline.
        is_concurrent = step["concurrent_with_previous"] and i > 0
        next_concurrent = (i + 1 < n_steps
                           and steps[i + 1]["concurrent_with_previous"])
        if is_concurrent or next_concurrent:
            done = env.event()
            env.process(_background_step(env, model, case_id, variant_name,
                                         step, arrival_time, rng,
                                         duration_samplers, failures_enabled,
                                         done))
            background.append(done)
        else:
            # Wait for all background steps to finish, then run inline.
            for done in background:
                yield done
            background = []
            yield from _run_step(env, model, case_id, variant_name, step,
                                 arrival_time, rng, duration_samplers,
                                 failures_enabled)
        # Early exit: stop after the exit step (no further steps).
        if i + 1 >= exit_after:
            for done in background:
                yield done
            background = []
            model.completed.append((case_id, env.now))
            return
    # Wait for any remaining background steps (safety).
    for done in background:
        yield done
    model.completed.append((case_id, env.now))


def arrival_process(env, model):
    """Two-regime bursty releases; first release at t=0."""
    rng = model.arrival_rng
    scale = model.arrival_scale
    horizon = model.horizon
    burst_size = model.burst_size_sampler
    intra_iat = model.intra_iat_sampler
    inter_gap = model.inter_gap_sampler
    variant_names = model.variant_names
    variant_probs = model.variant_probs

    t = 0.0
    case_i = 0
    while t < horizon:
        k = int(burst_size())
        for j in range(k):
            if t >= horizon:
                return
            variant = variant_names[int(rng.choice(len(variant_names), p=variant_probs))]
            model.case_count += 1
            case_id = f"case_{case_i}"
            case_i += 1
            env.process(case_process(env, model, case_id, variant, t,
                                     model.case_rng_factory(case_i)))
            if j < k - 1:
                gap = intra_iat() / scale
                yield env.timeout(gap)
                t += gap
        # Gap between bursts.
        gap = inter_gap() / scale
        yield env.timeout(gap)
        t += gap


class Model:
    def __init__(self, env, arrival_rng, case_rng_factory, horizon,
                 arrival_scale, failures_enabled):
        self.env = env
        self.arrival_rng = arrival_rng
        self.case_rng_factory = case_rng_factory
        self.horizon = horizon
        self.arrival_scale = arrival_scale
        self.failures_enabled = failures_enabled
        self.rows = []
        self.case_count = 0
        self.completed = []  # (case_id, completion_time)
        self.resources = {}
        for name, cap in RESOURCE_CAPACITIES.items():
            if name.startswith("hbw_"):
                self.resources[name] = PriorityFIFOResource(env, cap, HBW_PRIORITY_ORDER)
            else:
                self.resources[name] = simpy.Resource(env, cap)
        # Arrival samplers (dedicated arrival stream).
        self.burst_size_sampler = make_sampler(BURST_SIZE_DIST, arrival_rng)
        self.intra_iat_sampler = make_sampler(INTRA_BURST_IAT_DIST, arrival_rng)
        self.inter_gap_sampler = make_sampler(INTER_BURST_GAP_DIST, arrival_rng)
        self.variant_names = list(VARIANTS.keys())
        self.variant_probs = np.asarray(
            [VARIANTS[v]["probability"] for v in self.variant_names])
        self.variant_probs = self.variant_probs / self.variant_probs.sum()

    def case_duration_samplers(self, case_rng):
        """Per-case duration samplers (each case has its own rng stream)."""
        return {name: make_sampler(spec["duration"], case_rng)
                for name, spec in ACTIVITIES.items()}


def run_single_replication(seed: int) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)
    # Dedicated, deterministically-derived streams: one for arrivals, one per
    # case.  This decouples the arrival process from the case processes so the
    # release count is driven purely by the arrival distributions.
    arrival_rng = np.random.default_rng([seed, 1])
    case_rng_factory = lambda case_index: np.random.default_rng([seed, 2, case_index])

    # Read knobs at call time.
    horizon = float(SIMULATION_TIME)
    arrival_scale = float(ARRIVAL_RATE_SCALE)
    failures_enabled = bool(FAILURES_ENABLED)

    env = simpy.Environment()
    model = Model(env, arrival_rng, case_rng_factory, horizon,
                  arrival_scale, failures_enabled)
    env.process(arrival_process(env, model))
    env.run(until=horizon)

    df = pd.DataFrame(model.rows, columns=[
        "case_id", "variant", "activity", "resource", "case_arrival",
        "queue_enter", "time:timestamp", "operation_end_time", "lifecycle:state",
    ])
    for col in ["case_arrival", "queue_enter", "time:timestamp", "operation_end_time"]:
        df[col] = df[col].astype(float)
    # Drop rows whose service extends past the horizon.
    df = df[df["operation_end_time"] <= horizon]
    # Return chronologically (by release time, then service start) so that
    # release-spacing / arrival metrics are well-defined regardless of the
    # consumer's ordering assumptions.
    df = df.sort_values(["case_arrival", "time:timestamp", "queue_enter"],
                        kind="mergesort").reset_index(drop=True)
    return df


if __name__ == "__main__":
    import sys
    # ---- pure-Python Monte Carlo of the arrival timing (no simpy) ----
    def _mc_sampler(dist, rng):
        fam = dist["family"]
        if fam == "categorical":
            v, pr = np.asarray(dist["values"]), np.asarray(dist["probs"])
            return lambda: float(rng.choice(v, p=pr / pr.sum()))
        q, pr = np.asarray(dist["quantiles"]), np.asarray(dist["quantile_probs"])
        return lambda: float(np.interp(rng.uniform(), pr, q))
    _H = float(SIMULATION_TIME)
    _counts, _bursts = [], []
    for _seed in range(500):
        _rng = np.random.default_rng(_seed)
        _bs = _mc_sampler(BURST_SIZE_DIST, _rng)
        _intra = _mc_sampler(INTRA_BURST_IAT_DIST, _rng)
        _inter = _mc_sampler(INTER_BURST_GAP_DIST, _rng)
        _t = 0.0; _n = 0; _b = 0
        while _t < _H:
            _k = int(_bs()); _b += 1
            for _j in range(_k):
                if _t >= _H:
                    break
                _n += 1
                if _j < _k - 1:
                    _t += _intra()
            _t += _inter()
        _counts.append(_n); _bursts.append(_b)
    _c = np.asarray(_counts); _b = np.asarray(_bursts)
    print(f"[MC arrival] cases: mean={_c.mean():.1f} median={np.median(_c):.0f} "
          f"min={_c.min()} max={_c.max()} | bursts: mean={_b.mean():.1f}")
    if "--arrival-mc" in sys.argv:
        sys.exit(0)
    df = run_single_replication(1)
    print(f"rows: {len(df)}")
    print(f"cases released: {df['case_id'].nunique()}")
    print(f"failure rows: {(df['lifecycle:state'] == 'failure').sum()}")
    print(f"wt failures: "
          f"{((df['activity'] == '/wt/pick_up_and_transport') & (df['lifecycle:state'] == 'failure')).sum()}")
    print(f"hbw/store_empty_bucket failures: "
          f"{((df['activity'] == '/hbw/store_empty_bucket') & (df['lifecycle:state'] == 'failure')).sum()}")
    # Flow time per case (completion - arrival) for cases that completed.
    g = df.groupby("case_id")
    last_end = g["operation_end_time"].max()
    first_arr = g["case_arrival"].min()
    flow = last_end - first_arr
    print(f"mean flow time (all cases w/ rows): {flow.mean():.1f} s")
    # ---- diagnostics: release spacing + intra-case overlap ----
    arr = np.sort(df["case_arrival"].unique())
    if len(arr) > 1:
        sp = np.diff(arr)
        print(f"[diag] release spacing (numeric sort): median={np.median(sp):.2f} "
              f"mean={sp.mean():.2f} n={len(sp)}")
    # string-sort by case_id (what a harness might do)
    d2 = df.sort_values("case_id")
    sp2 = np.diff(d2["case_arrival"].values)
    print(f"[diag] release spacing (string-sort case_id): median={np.median(sp2):.2f} "
          f"mean={sp2.mean():.2f}")
    # ---- release-spacing diagnostic (time-sorted consecutive gaps) ----
    rel = np.sort(df["case_arrival"].unique())
    gaps = np.diff(rel)
    print(f"[diag] n releases={len(rel)}; median release gap (time-sorted)="
          f"{np.median(gaps):.2f}s (observed ~3.2s)")
    def _overlap_count(sub):
        iv = list(zip(sub["time:timestamp"].values,
                      sub["operation_end_time"].values))
        cnt = 0
        for i in range(len(iv)):
            for j in range(i + 1, len(iv)):
                if iv[i][0] < iv[j][1] and iv[j][0] < iv[i][1]:
                    cnt += 1
                    break
        return cnt
    ov = df.groupby("case_id").apply(_overlap_count)
    print(f"[diag] overlapping steps per case: mean={ov.mean():.2f}")
    print(f"variant counts:\n{df['variant'].value_counts().to_string()}")
    print(df.head(10).to_string())
