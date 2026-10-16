"""SimPy digital twin of the Fischertechnik lab manufacturing system (fischertechnik_lab_C).

Two parallel production-line tracks (Track1: ov_1/mm_1/wt_1/sm_1 + pm_1/hw_1;
Track2: ov_2/mm_2/wt_2/sm_2 + dm_2) with shared exchange-point resources
(hbw_1 outfeed, hbw_2 infeed, vgr_1 outfeed/general, vgr_2 infeed), driven by a
single global bursty arrival stream into hbw.
"""

import random

import numpy as np
import pandas as pd
import simpy
import scipy.stats

# ---------------------------------------------------------------------------
# Contract knobs (read at call time inside run_single_replication)
# ---------------------------------------------------------------------------
RESOURCE_CAPACITIES = {
    "dm_2": 1, "hbw_1": 1, "hbw_2": 1, "hw_1": 1, "mm_1": 1, "mm_2": 1,
    "ov_1": 1, "ov_2": 1, "pm_1": 1, "sm_1": 1, "sm_2": 1, "vgr_1": 1,
    "vgr_2": 1, "wt_1": 1, "wt_2": 1,
}
SIMULATION_TIME: float = 5461.506544
ARRIVAL_RATE_SCALE: float = 1.0
FAILURES_ENABLED: bool = True

# ---------------------------------------------------------------------------
# Activity duration distributions (spec.activities, used exactly)
# ---------------------------------------------------------------------------
ACTIVITY_DURATIONS = {
    "/dm/cylindrical_drill": {"family": "triang", "params": {"c": 0.5, "loc": 39.078, "scale": 7.75}},
    "/dm/drill": {"family": "triang", "params": {"c": 0.36581, "loc": 15.812, "scale": 26.142}},
    "/dm/lower": {"family": "triang", "params": {"c": 0.96875, "loc": 13.828, "scale": 0.016}},
    "/hbw/get_empty_bucket": {"family": "empirical_quantiles",
        "quantiles": [32.953, 33.4613, 33.8661, 34.15015, 35.3246, 36.09725, 36.1083, 36.27335, 36.4506, 36.5923, 36.7265, 37.27095, 39.1904, 39.8305, 40.0519, 41.09775, 41.85, 42.39375, 42.6375, 44.62565, 48.109],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
    "/hbw/store": {"family": "empirical_quantiles",
        "quantiles": [30.734, 31.2122, 32.103, 33.819, 34.5154, 34.702, 34.9558, 35.8468, 38.0122, 38.9592, 39.297, 39.3156, 39.3782, 39.5288, 39.7038, 39.891, 39.9096, 39.972, 40.122, 40.1784, 40.188],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
    "/hbw/store_empty_bucket": {"family": "uniform", "params": {"loc": 31.734, "scale": 12.297}},
    "/hbw/unload": {"family": "triang", "params": {"c": 1e-06, "loc": 31.592982, "scale": 21.134166}},
    "/hw/human_review": {"family": "empirical_quantiles",
        "quantiles": [0.328, 0.6339, 0.809, 1.3581, 4.7398, 5.806, 7.3716, 12.5012, 15.8026, 20.398, 27.125, 32.4842, 43.575, 57.216, 60.366, 62.25, 73.3592, 108.7974, 114.9754, 136.5222, 185.063],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
    "/mm/deburr": {"family": "empirical_quantiles",
        "quantiles": [13.843, 13.8574, 13.8718, 13.875, 13.9596, 14.0315, 14.0534, 14.072, 14.0932, 14.1081, 14.235, 14.2485, 14.2628, 14.266, 14.3878, 14.547, 14.7126, 14.9094, 15.181, 20.7475, 66.562],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
    "/mm/drill": {"family": "empirical_quantiles",
        "quantiles": [5.078, 5.1494, 5.2208, 5.2835, 5.294, 5.3045, 6.187, 9.2495, 12.312, 14.2683, 14.7495, 15.2308, 15.4402, 15.4458, 15.4514, 15.8047, 16.2972, 16.7897, 21.4629, 26.833, 32.203],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
    "/mm/mill": {"family": "empirical_quantiles",
        "quantiles": [5.078, 5.179, 5.28, 5.2805, 5.281, 5.281, 5.281, 5.2815, 5.282, 5.6955, 6.109, 6.2105, 6.312, 10.164, 14.016, 14.1565, 14.297, 14.375, 14.453, 14.453, 14.453],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
    "/mm/transport_from_to": {"family": "triang", "params": {"c": 0.752, "loc": 12.203, "scale": 0.25}},
    "/ov/burn": {"family": "uniform", "params": {"loc": 21.421, "scale": 20.111}},
    "/ov/temper": {"family": "triang", "params": {"c": 0.070377, "loc": 51.437, "scale": 1.563}},
    "/pm/punch_gill": {"family": "triang", "params": {"c": 0.910159, "loc": 23.859, "scale": 3.829}},
    "/pm/punch_recesses": {"family": "triang", "params": {"c": 0.5, "loc": 23.672, "scale": 0.157}},
    "/pm/punch_ribbing": {"family": "triang", "params": {"c": 0.5, "loc": 23.344, "scale": 0.453}},
    "/sm/sort": {"family": "empirical_quantiles",
        "quantiles": [8.578, 8.6062, 8.6564, 8.7506, 9.3316, 10.156, 10.1746, 10.2246, 10.3374, 10.5374, 10.781, 11.6342, 12.2406, 12.3534, 12.6346, 13.0, 13.1872, 13.334, 13.4, 16.5596, 21.266],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
    "/sm/transport": {"family": "empirical_quantiles",
        "quantiles": [14.219, 14.3036, 14.4626, 14.6092, 14.6842, 14.742, 14.8062, 14.8626, 14.9186, 14.969, 14.969, 18.5267, 18.9596, 18.9795, 18.9936, 19.0155, 19.0438, 19.2829, 19.943, 24.3107, 58.328],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
    "/vgr/pick_up_and_transport": {"family": "triang", "params": {"c": 0.976708, "loc": 4.832668, "scale": 47.71674}},
    "/wt/pick_up_and_transport": {"family": "empirical_quantiles",
        "quantiles": [25.812, 25.922, 25.9348, 25.9582, 26.031, 26.031, 26.031, 26.0318, 26.0492, 26.1094, 29.094, 29.203, 29.203, 29.207, 29.2748, 29.313, 29.3562, 29.4218, 29.437, 29.4466, 29.531],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
    "vgr_to_hbw_handoff_delay": {"family": "empirical_quantiles",
        "quantiles": [2.353, 2.3998, 2.5372, 2.8558, 3.0184, 3.103, 3.1312, 3.1592, 3.1868, 3.2712, 3.384, 3.3846, 3.4098, 3.4842, 3.509, 3.509, 3.5558, 3.8434, 4.6126, 5.5837, 6.6558],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]},
}

# Failure probabilities per activity (spec.activities)
ACTIVITY_FAILURES = {
    "/hbw/unload": 0.0541,
    "/vgr/pick_up_and_transport": 0.0288,
}

# hbw_1 priority order (lower index = served first)
HBW_1_PRIORITY = {"/hbw/store_empty_bucket": 0, "/hbw/unload": 1}
HBW_1_DEFAULT_PRIORITY = len(HBW_1_PRIORITY)

# ---------------------------------------------------------------------------
# Arrival process (two_regime_bursts)
# ---------------------------------------------------------------------------
BURST_SIZE_DIST = {"family": "categorical",
                   "values": [1.0, 2.0, 3.0, 5.0, 9.0],
                   "probs": [0.3333, 0.25, 0.0833, 0.25, 0.0833]}
INTRA_BURST_IAT = {"family": "empirical_quantiles",
    "quantiles": [0.51015, 0.532127, 0.59641, 0.655471, 0.73077, 0.890128, 0.923098, 0.931512, 0.937978, 1.024814, 1.078298, 1.130432, 1.312155, 1.40851, 1.520662, 1.73453, 1.829138, 2.550752, 3.471896, 3.548565, 16.249838],
    "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]}
INTER_BURST_GAP = {"family": "empirical_quantiles",
    "quantiles": [33.296625, 49.234199, 65.171773, 75.656213, 86.140653, 110.453448, 134.766243, 210.649177, 286.532111, 351.674994, 416.817876, 454.74979, 492.681704, 507.082923, 521.484143, 608.328046, 695.17195, 790.464149, 885.756347, 937.516099, 989.275852],
    "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]}

VARIANT_SPLIT = {
    "WF_101": 0.1081, "WF_102": 0.1351, "WF_103": 0.1351, "WF_104": 0.0811,
    "WF_105": 0.1081, "WF_108": 0.0811, "WF_109": 0.0811, "WF_1106": 0.1622,
    "WF_1107": 0.1081,
}


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
    d = getattr(scipy.stats, fam)(**p)
    return lambda: max(0.0, float(d.rvs(random_state=rng)))


class PriorityResource(simpy.Resource):
    """Capacity-1 resource with (priority, arrival-time) queue discipline."""

    def request(self, priority=0):
        req = super().request()
        req.priority = priority
        return req

    def _filter(self, reqs):
        return sorted(reqs, key=lambda r: (getattr(r, "priority", 0), r.arrival))


# ---------------------------------------------------------------------------
# Variant step tables (spec.variants). Each step:
#   (activity, {resource: prob}, concurrent_with_previous)
# ---------------------------------------------------------------------------
def _S(activity, resources, concurrent=False):
    return {"activity": activity, "resources": resources, "concurrent": concurrent}


VARIANTS = {
    "WF_101": {
        "steps": [
            _S("/hbw/unload", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/hbw/store_empty_bucket", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/ov/burn", {"ov_1": 1.0}),
            _S("/ov/temper", {"ov_1": 1.0}),
            _S("/wt/pick_up_and_transport", {"wt_1": 1.0}),
            _S("/mm/mill", {"mm_1": 1.0}),
            _S("/mm/deburr", {"mm_1": 1.0}),
            _S("/sm/sort", {"sm_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hw/human_review", {"hw_1": 1.0}),
            _S("/hbw/get_empty_bucket", {"hbw_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hbw/store", {"hbw_1": 1.0}),
        ],
        "early_exit_probability": 0.5,
        "early_exit_after_n_steps": {"0": 1.0},
        "early_exit_after": {"/hbw/unload": 1.0},
    },
    "WF_102": {
        "steps": [
            _S("/hbw/unload", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 0.6, "vgr_1": 0.4}),
            _S("/hbw/store_empty_bucket", {"hbw_2": 1.0}),
            _S("/ov/burn", {"ov_2": 1.0}, True),
            _S("/wt/pick_up_and_transport", {"wt_2": 1.0}),
            _S("/mm/drill", {"mm_2": 1.0}),
            _S("/sm/transport", {"sm_2": 1.0}),
            _S("/dm/lower", {"dm_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hw/human_review", {"hw_1": 1.0}),
            _S("/hbw/get_empty_bucket", {"hbw_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hbw/store", {"hbw_1": 1.0}),
        ],
        "early_exit_probability": 0.6,
        "early_exit_after_n_steps": {"6": 0.333, "8": 0.333, "12": 0.333},
        "early_exit_after": {"/vgr/pick_up_and_transport": 0.667, "/mm/drill": 0.333},
    },
    "WF_103": {
        "steps": [
            _S("/hbw/unload", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/hbw/store_empty_bucket", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/ov/burn", {"ov_1": 1.0}),
            _S("/ov/temper", {"ov_1": 1.0}),
            _S("/wt/pick_up_and_transport", {"wt_1": 1.0}),
            _S("/mm/mill", {"mm_1": 1.0}),
            _S("/mm/deburr", {"mm_1": 1.0}),
            _S("/sm/transport", {"sm_1": 1.0}),
            _S("/pm/punch_recesses", {"pm_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hw/human_review", {"hw_1": 1.0}),
            _S("/hbw/get_empty_bucket", {"hbw_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hbw/store", {"hbw_1": 1.0}),
        ],
        "early_exit_probability": 0.6,
        "early_exit_after_n_steps": {"3": 0.333, "4": 0.333, "12": 0.333},
        "early_exit_after": {"/hw/human_review": 0.333, "/vgr/pick_up_and_transport": 0.667},
    },
    "WF_104": {
        "steps": [
            _S("/hbw/unload", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/hbw/store_empty_bucket", {"hbw_2": 1.0}),
            _S("/ov/burn", {"ov_2": 1.0}, True),
            _S("/wt/pick_up_and_transport", {"wt_2": 1.0}),
            _S("/sm/sort", {"sm_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 0.5, "vgr_2": 0.5}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/wt/pick_up_and_transport", {"wt_1": 1.0}),
            _S("/mm/deburr", {"mm_1": 1.0}),
            _S("/sm/transport", {"sm_1": 1.0}),
            _S("/pm/punch_gill", {"pm_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hw/human_review", {"hw_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/hbw/store_empty_bucket", {"hbw_2": 1.0}),
            _S("/ov/burn", {"ov_2": 1.0}, True),
            _S("/wt/pick_up_and_transport", {"wt_2": 1.0}),
            _S("/mm/mill", {"mm_2": 1.0}),
            _S("/sm/sort", {"sm_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
        ],
        "early_exit_probability": 1.0,
        "early_exit_after_n_steps": {"6": 0.333, "15": 0.333, "23": 0.333},
        "early_exit_after": {"/vgr/pick_up_and_transport": 0.667, "/sm/sort": 0.333},
    },
    "WF_105": {
        "steps": [
            _S("/hbw/unload", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/hbw/store_empty_bucket", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/ov/burn", {"ov_1": 1.0}),
            _S("/wt/pick_up_and_transport", {"wt_1": 1.0}),
            _S("/mm/deburr", {"mm_1": 1.0}),
            _S("/sm/sort", {"sm_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hw/human_review", {"hw_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hbw/get_empty_bucket", {"hbw_1": 1.0}, True),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/hbw/store", {"hbw_1": 1.0}),
        ],
        "early_exit_probability": 0.5,
        "early_exit_after_n_steps": {"8": 1.0},
        "early_exit_after": {"/sm/sort": 1.0},
    },
    "WF_108": {
        "steps": [
            _S("/hbw/unload", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/hbw/store_empty_bucket", {"hbw_2": 1.0}),
            _S("/ov/burn", {"ov_2": 1.0}, True),
            _S("/wt/pick_up_and_transport", {"wt_2": 1.0}),
            _S("/mm/drill", {"mm_2": 1.0}),
            _S("/mm/deburr", {"mm_2": 1.0}),
            _S("/sm/sort", {"sm_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hw/human_review", {"hw_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hbw/get_empty_bucket", {"hbw_1": 1.0}, True),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/hbw/store", {"hbw_1": 1.0}),
        ],
        "early_exit_probability": 0.667,
        "early_exit_after_n_steps": {"7": 0.5, "9": 0.5},
        "early_exit_after": {"/vgr/pick_up_and_transport": 0.5, "/sm/sort": 0.5},
    },
    "WF_109": {
        "steps": [
            _S("/hbw/unload", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/hbw/store_empty_bucket", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/ov/burn", {"ov_1": 1.0}),
            _S("/ov/temper", {"ov_1": 1.0}),
            _S("/wt/pick_up_and_transport", {"wt_1": 1.0}),
            _S("/mm/mill", {"mm_1": 1.0}),
            _S("/mm/deburr", {"mm_1": 1.0}),
            _S("/sm/transport", {"sm_1": 1.0}),
            _S("/pm/punch_ribbing", {"pm_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hw/human_review", {"hw_1": 1.0}),
            _S("/hbw/get_empty_bucket", {"hbw_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hbw/store", {"hbw_1": 1.0}),
        ],
        "early_exit_probability": 0.333,
        "early_exit_after_n_steps": {"8": 1.0},
        "early_exit_after": {"/mm/deburr": 1.0},
    },
    "WF_1106": {
        "steps": [
            _S("/hbw/unload", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/hbw/store_empty_bucket", {"hbw_2": 1.0}),
            _S("/ov/burn", {"ov_2": 1.0}, True),
            _S("/wt/pick_up_and_transport", {"wt_2": 1.0}),
            _S("/mm/transport_from_to", {"mm_2": 1.0}),
            _S("/sm/transport", {"sm_2": 1.0}),
            _S("/dm/drill", {"dm_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hw/human_review", {"hw_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hbw/get_empty_bucket", {"hbw_1": 1.0}, True),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/hbw/store", {"hbw_1": 1.0}),
        ],
        "early_exit_probability": 0.833,
        "early_exit_after_n_steps": {"7": 0.4, "8": 0.6},
        "early_exit_after": {"/dm/drill": 0.6, "/dm/cylindrical_drill": 0.4},
    },
    "WF_1107": {
        "steps": [
            _S("/hbw/unload", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_2": 1.0}),
            _S("/hbw/store_empty_bucket", {"hbw_2": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/ov/burn", {"ov_1": 1.0}),
            _S("/mm/transport_from_to", {"mm_1": 1.0}),
            _S("/sm/transport", {"sm_1": 1.0}),
            _S("/pm/punch_gill", {"pm_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hw/human_review", {"hw_1": 1.0}),
            _S("/hbw/get_empty_bucket", {"hbw_1": 1.0}),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}, True),
            _S("/vgr/pick_up_and_transport", {"vgr_1": 1.0}),
            _S("/hbw/store", {"hbw_1": 1.0}),
        ],
        "early_exit_probability": 0.75,
        "early_exit_after_n_steps": {"1": 0.333, "7": 0.333, "12": 0.333},
        "early_exit_after": {"/hbw/unload": 0.333, "/vgr/pick_up_and_transport": 0.333, "/pm/punch_gill": 0.333},
    },
}

HBW_1_ACTIVITIES = {"/hbw/get_empty_bucket", "/hbw/store"}
HANDOFF_ACTIVITY = "vgr_to_hbw_handoff_delay"

# Verified vgr->hbw_1 handoff insertion points: variant -> list of original
# step indices after which a handoff-delay step is inserted (per the spec's
# verified per-variant enumeration).
HANDOFF_AFTER = {
    "WF_101": [14],
    "WF_102": [12],
    "WF_103": [15],
    "WF_104": [22],
    "WF_105": [10, 12],
    "WF_108": [11, 13],
    "WF_109": [15],
    "WF_1106": [10, 12],
    "WF_1107": [12],
}


def build_case_steps(variant_name: str):
    """Return the executable step list for a variant, with the vgr->hbw_1
    handoff-delay step inserted at the verified per-variant points.

    Returns a list of (original_index, step_dict, is_concurrent) tuples where
    is_concurrent marks steps that run in parallel with the preceding step."""
    steps = [dict(s) for s in VARIANTS[variant_name]["steps"]]
    insert_after = set(HANDOFF_AFTER.get(variant_name, []))
    out = []
    for i, s in enumerate(steps):
        out.append((i, s, s["concurrent"]))
        if i in insert_after:
            out.append((None, _S(HANDOFF_ACTIVITY, {"hbw_1": 1.0}), False))
    return out


def run_single_replication(seed: int) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)

    horizon = float(SIMULATION_TIME)
    rate_scale = float(ARRIVAL_RATE_SCALE)
    failures_enabled = bool(FAILURES_ENABLED)

    env = simpy.Environment()
    resources = {name: simpy.Resource(env, cap) for name, cap in RESOURCE_CAPACITIES.items()}
    resources["hbw_1"] = PriorityResource(env, RESOURCE_CAPACITIES["hbw_1"])
    resources["hbw_2"] = PriorityResource(env, RESOURCE_CAPACITIES["hbw_2"])

    duration_samplers = {name: make_sampler(dist, rng) for name, dist in ACTIVITY_DURATIONS.items()}
    burst_size_sampler = make_sampler(BURST_SIZE_DIST, rng)
    intra_iat_sampler = make_sampler(INTRA_BURST_IAT, rng)
    inter_gap_sampler = make_sampler(INTER_BURST_GAP, rng)
    variant_names = np.array(list(VARIANT_SPLIT.keys()))
    variant_probs = np.array([VARIANT_SPLIT[v] for v in variant_names])
    variant_probs = variant_probs / variant_probs.sum()

    rows = []

    def log_row(case_id, variant, activity, resource, case_arrival, queue_enter, start, end, state):
        rows.append({
            "case_id": case_id,
            "variant": variant,
            "activity": activity,
            "resource": resource,
            "case_arrival": float(case_arrival),
            "queue_enter": float(queue_enter),
            "time:timestamp": float(start),
            "operation_end_time": float(end),
            "lifecycle:state": state,
        })

    def pick_resource(probs: dict) -> str:
        names = np.array(list(probs.keys()))
        p = np.array([probs[n] for n in names], dtype=float)
        return str(rng.choice(names, p=p / p.sum()))

    def hbw_priority(activity: str) -> int:
        return HBW_1_PRIORITY.get(activity, HBW_1_DEFAULT_PRIORITY)

    def run_step(case_id, variant, case_arrival, activity, res_name, duration, state="success"):
        """Execute one attempt on a resource; log the row; return end time."""
        res = resources[res_name]
        queue_enter = env.now
        if res_name in ("hbw_1", "hbw_2"):
            req = res.request(priority=hbw_priority(activity))
        else:
            req = res.request()
        yield req
        start = env.now
        yield env.timeout(max(0.0, duration))
        end = env.now
        res.release(req)
        log_row(case_id, variant, activity, res_name, case_arrival, queue_enter, start, end, state)
        return end

    def attempt_step(case_id, variant, case_arrival, activity, res_name):
        """Run an activity with failure/retry semantics until success."""
        p_fail = ACTIVITY_FAILURES.get(activity, 0.0) if failures_enabled else 0.0
        while True:
            duration = duration_samplers[activity]()
            failed = p_fail > 0.0 and rng.random() < p_fail
            end = yield from run_step(case_id, variant, case_arrival, activity, res_name,
                                       duration, "failure" if failed else "success")
            if not failed:
                return end

    def case_process(case_id, variant, case_arrival):
        entries = build_case_steps(variant)
        # Per-case early exit: draw ONCE whether the case abandons (scrap),
        # and if so, after which step (original index). This matches the
        # observed ~35% completion rate (the per-step early_exit_after rolls
        # would give only ~7%, inconsistent with the data).
        vinfo = VARIANTS[variant]
        exit_flag = rng.random() < vinfo.get("early_exit_probability", 0.0)
        exit_step = None
        if exit_flag:
            n_steps = vinfo.get("early_exit_after_n_steps", {})
            if n_steps:
                keys = [int(k) for k in n_steps.keys()]
                probs = np.array([n_steps[str(k)] for k in keys], dtype=float)
                exit_step = int(rng.choice(keys, p=probs / probs.sum()))
        i = 0
        n = len(entries)
        while i < n:
            # Group a step with any following steps that are concurrent with it
            # (they all start together, in parallel).
            group = [entries[i]]
            j = i + 1
            while j < n and entries[j][2]:
                group.append(entries[j])
                j += 1
            # Skip draws for the group (in step order) before any of them start.
            executed = []
            for _, s, _ in group:
                if rng.random() < s.get("probability", 1.0):
                    executed.append(s)
            # Spawn all executed steps as background processes (parallel start).
            procs = []
            for s in executed:
                res_name = pick_resource(s["resources"])
                procs.append(env.process(attempt_step(case_id, variant, case_arrival,
                                                      s["activity"], res_name)))
            for p in procs:
                yield p
            # Per-case early exit: if this case was drawn to abandon, stop it
            # once the step at the drawn original index has completed.
            if exit_step is not None:
                last_orig = max((e[0] for e in group if e[0] is not None), default=None)
                if last_orig is not None and last_orig >= exit_step:
                    return
            i = j

    def arrivals():
        case_idx = 0
        first = True
        while True:
            if not first:
                yield env.timeout(inter_gap_sampler() / rate_scale)
            first = False
            burst = int(burst_size_sampler())
            for k in range(burst):
                if k > 0:
                    yield env.timeout(intra_iat_sampler() / rate_scale)
                if env.now > horizon:
                    return
                variant = str(rng.choice(variant_names, p=variant_probs))
                case_idx += 1
                env.process(case_process(f"case_{case_idx}", variant, env.now))

    env.process(arrivals())
    env.run(until=horizon)

    df = pd.DataFrame(rows, columns=[
        "case_id", "variant", "activity", "resource", "case_arrival",
        "queue_enter", "time:timestamp", "operation_end_time", "lifecycle:state",
    ])
    return df


if __name__ == "__main__":
    df = run_single_replication(1)
    print(df.head())
    print(len(df), "rows")
    entered = df.drop_duplicates("case_id")
    completed = df[df["activity"] == "/hbw/store"].drop_duplicates("case_id")
    print(f"entered: {len(entered)}, completed: {len(completed)}")