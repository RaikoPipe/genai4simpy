"""SimPy discrete-event simulation of the Fischertechnik lab A line.

Run: fischertechnik_lab_A / eager-nice-cow.
Implements the typed simulation spec (window, resources, activities,
variants, arrivals, control_policies, initial_state, assumptions).

Output contract v2:
- run_single_replication(seed) -> pandas.DataFrame event log
- RESOURCE_CAPACITIES, SIMULATION_TIME, ARRIVAL_RATE_SCALE, FAILURES_ENABLED
"""

import random

import numpy as np
import pandas as pd
import scipy.stats
import simpy

# ---------------------------------------------------------------------------
# Contract symbols (read at call time inside run_single_replication)
# ---------------------------------------------------------------------------

RESOURCE_CAPACITIES: dict[str, int] = {
    "dm_2": 1,
    "hbw_1": 1,
    "hbw_2": 1,
    "hw_1": 1,
    "mm_1": 1,
    "mm_2": 1,
    "ov_1": 1,
    "ov_2": 1,
    "pm_1": 1,
    "sm_1": 1,
    "sm_2": 1,
    "vgr_1": 1,
    "vgr_2": 1,
    "wt_1": 1,
    "wt_2": 1,
}

SIMULATION_TIME: float = 3183.202249
ARRIVAL_RATE_SCALE: float = 1.0
FAILURES_ENABLED: bool = True

# hbw priority order (lower index = higher priority)
HBW_PRIORITY_ORDER = ["/hbw/store", "/hbw/store_empty_bucket",
                      "/hbw/get_empty_bucket", "/hbw/unload"]

# ---------------------------------------------------------------------------
# Spec data: activity durations (start-row service times)
# ---------------------------------------------------------------------------

ACTIVITY_DISTRIBUTIONS: dict[str, dict] = {
    "/dm/cylindrical_drill": {
        "family": "triang", "params": {"c": 0.5, "loc": 21.969, "scale": 4.046},
    },
    "/dm/lower": {
        "family": "triang", "params": {"c": 0.5, "loc": 13.875, "scale": 0.266},
    },
    "/hbw/get_empty_bucket": {
        "family": "empirical_quantiles",
        "quantiles": [30.797, 31.1795, 31.562, 33.2655, 34.969, 35.3985,
                      35.828, 35.9115, 35.995, 36.107, 36.219, 36.3285,
                      36.438, 36.6095, 36.781, 36.8275, 36.874, 40.249,
                      43.624, 46.109, 48.594],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                           0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                           0.9, 0.95, 1.0],
    },
    "/hbw/store": {
        "family": "triang", "params": {"c": 0.30222, "loc": 34.641, "scale": 7.703},
    },
    "/hbw/store_empty_bucket": {
        "family": "empirical_quantiles",
        "quantiles": [32.641, 33.7936, 34.9214, 35.9996, 36.4718, 36.641,
                      36.7658, 37.1636, 38.1074, 39.3156, 40.656, 40.7124,
                      40.7844, 40.8876, 41.572, 42.547, 42.556, 43.009,
                      44.35, 44.825, 44.867],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                           0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                           0.9, 0.95, 1.0],
    },
    "/hbw/unload": {
        "family": "empirical_quantiles",
        "quantiles": [32.735, 32.8865, 33.078, 33.676, 35.047, 35.96125,
                      36.3705, 36.48125, 36.5, 37.88975, 38.4265, 38.51175,
                      38.547, 38.664, 39.0705, 40.69575, 44.469, 45.60525,
                      47.6165, 49.99875, 52.248],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                           0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                           0.9, 0.95, 1.0],
    },
    "/hw/human_review": {
        "family": "empirical_quantiles",
        "quantiles": [0.438, 1.2297, 1.6596, 1.6674, 1.7832, 1.86775, 1.8879,
                      2.0538, 2.4278, 3.2104, 3.75, 5.0822, 9.2994, 11.75575,
                      13.6515, 16.76825, 21.5766, 28.02975, 41.5335, 52.8354,
                      62.25],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                           0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                           0.9, 0.95, 1.0],
    },
    "/mm/deburr": {
        "family": "triang", "params": {"c": 0.35964, "loc": 14.046, "scale": 1.001},
    },
    "/mm/drill": {
        "family": "triang", "params": {"c": 0.672512, "loc": 5.281, "scale": 15.625},
    },
    "/mm/mill": {
        "family": "triang", "params": {"c": 0.005911, "loc": 5.047, "scale": 9.39},
    },
    "/mm/transport_from_to": {
        "family": "triang", "params": {"c": 0.5, "loc": 12.594, "scale": 0.547},
    },
    "/ov/burn": {
        "family": "empirical_quantiles",
        "quantiles": [21.422, 21.5528, 21.6402, 21.6408, 23.5722, 26.469,
                      26.5254, 26.6292, 26.8278, 28.7612, 31.562, 31.6268,
                      31.7048, 31.8092, 33.7752, 36.672, 36.7842, 36.8592,
                      36.8598, 38.8288, 41.782],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                           0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                           0.9, 0.95, 1.0],
    },
    "/ov/temper": {
        "family": "triang", "params": {"c": 0.592357, "loc": 51.453, "scale": 0.157},
    },
    "/pm/punch_gill": {
        "family": "constant", "params": {"value": 27.484},
    },
    "/pm/punch_recesses": {
        "family": "triang", "params": {"c": 0.5, "loc": 23.453, "scale": 0.375},
    },
    "/pm/punch_ribbing": {
        "family": "triang", "params": {"c": 0.5, "loc": 23.562, "scale": 7.657},
    },
    "/sm/sort": {
        # Pooled triang kept AS-IS per spec (inflated mean from 245.7 s outlier).
        "family": "triang", "params": {"c": 0.015929, "loc": 8.36, "scale": 237.34},
    },
    "/sm/transport": {
        "family": "triang", "params": {"c": 0.537006, "loc": 14.39, "scale": 7.188},
    },
    "/vgr/pick_up_and_transport": {
        "family": "empirical_quantiles",
        "quantiles": [13.109, 19.69005, 24.3436, 35.9146, 36.4466, 36.69925,
                      37.1669, 38.23905, 40.6844, 42.0459, 42.7875, 43.28035,
                      43.5968, 43.9038, 44.2546, 46.1175, 48.8516, 51.1126,
                      53.1308, 59.9139, 88.375],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                           0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                           0.9, 0.95, 1.0],
    },
    "/wt/pick_up_and_transport": {
        "family": "empirical_quantiles",
        "quantiles": [25.906, 25.9268, 25.9425, 25.95225, 25.9716, 26.0155,
                      26.0974, 26.12705, 26.1846, 26.3263, 26.362, 26.7415,
                      28.373, 28.8822, 28.9118, 29.047, 29.1406, 29.20375,
                      29.2135, 29.22395, 29.235],
        "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                           0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                           0.9, 0.95, 1.0],
    },
}

# Per-resource conditioning (binding): /sm/transport, /wt/pick_up_and_transport,
# /vgr/pick_up_and_transport use the split matching the resource actually used.
RESOURCE_DURATIONS: dict[str, dict[str, dict]] = {
    "/sm/transport": {
        "sm_1": {"family": "triang", "params": {"c": 0.34976, "loc": 18.25, "scale": 3.328}},
        "sm_2": {"family": "triang", "params": {"c": 0.56015, "loc": 14.39, "scale": 0.266}},
    },
    "/wt/pick_up_and_transport": {
        "wt_1": {"family": "triang", "params": {"c": 0.30719, "loc": 25.906, "scale": 0.459}},
        "wt_2": {"family": "triang", "params": {"c": 0.766667, "loc": 28.875, "scale": 0.36}},
    },
    "/vgr/pick_up_and_transport": {
        "vgr_1": {"family": "norm", "params": {"loc": 42.643656, "scale": 15.557378}},
        "vgr_2": {
            "family": "empirical_quantiles",
            "quantiles": [35.734, 36.1726, 36.3697, 36.55905, 36.7156, 36.82025,
                          36.9707, 37.24865, 37.8898, 41.42795, 43.3515, 43.4974,
                          43.5874, 43.625, 43.625, 43.871, 44.094, 44.19475,
                          44.2546, 44.5133, 45.297],
            "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                               0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                               0.9, 0.95, 1.0],
        },
    },
}

# Per-activity failure probability (418/401 unified retry mechanism).
FAILURE_PROBABILITIES: dict[str, float] = {
    "/hbw/store_empty_bucket": 0.1333,
    "/hbw/unload": 0.0588,
    "/vgr/pick_up_and_transport": 0.0909,
}

# All observed vgr failures were on vgr_1 (5/37); vgr_2 0/18.
VGR_FAILURE_RESOURCE = "vgr_1"

# Quantity PMF for material-removal steps (spec assumptions).
QUANTITY_VALUES = [4, 6, 8, 10]
QUANTITY_PROBS = [0.273, 0.545, 0.091, 0.091]
QUANTITY_STEPS = {"/mm/drill", "/pm/punch_recesses", "/pm/punch_gill",
                  "/pm/punch_ribbing", "/dm/cylindrical_drill"}

# ---------------------------------------------------------------------------
# Arrivals (two_regime_bursts)
# ---------------------------------------------------------------------------

INITIAL_BURST_CASES = 8
TRANSITION_GAP_S = 633.4968
STEADY_STATE_CASES = 10

INITIAL_BURST_IAT = {
    "family": "empirical_quantiles",
    "quantiles": [0.5096, 0.5489, 0.5882, 0.6275, 0.6751, 0.7268, 0.7785,
                  0.8213, 0.8462, 0.8712, 0.8962, 0.8991, 0.902, 0.9049,
                  1.0217, 1.1953, 1.369, 1.5019, 1.5532, 1.6045, 1.6558],
    "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                       0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                       0.9, 0.95, 1.0],
}

STEADY_BURST_SIZE = {
    "family": "categorical",
    "values": [1, 2, 3],
    "probs": [0.5, 0.3333, 0.1667],
}

STEADY_INTRA_BURST_IAT = {
    "family": "empirical_quantiles",
    "quantiles": [0.6875, 0.8844, 1.0813, 1.2782, 1.475, 1.6719, 1.8688,
                  2.018, 2.0718, 2.1257, 2.1795, 2.2334, 2.2872, 2.341,
                  2.6762, 3.152, 3.6279, 4.1037, 4.5795, 5.0554, 5.5312],
    "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                       0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                       0.9, 0.95, 1.0],
}

STEADY_INTER_BURST_GAP = {
    "family": "empirical_quantiles",
    "quantiles": [93.4062, 102.5469, 111.6877, 120.8284, 129.9691, 139.1099,
                  167.4691, 195.8283, 224.1875, 252.5467, 280.9059, 288.2997,
                  295.6934, 303.0872, 310.481, 317.8747, 414.2911, 510.7075,
                  607.1239, 703.5402, 799.9566],
    "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                       0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85,
                       0.9, 0.95, 1.0],
}

# Variant mix (share of released cases over all 18 cases).
VARIANT_NAMES = ["WF_101", "WF_102", "WF_103", "WF_104", "WF_105", "WF_108",
                 "WF_109", "WF_1106", "WF_1107"]
VARIANT_PROBS = [0.1333, 0.1333, 0.1333, 0.0667, 0.1333, 0.0667, 0.0667,
                 0.1333, 0.1333]


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


def _sample_quantity(rng: np.random.Generator) -> int:
    return int(rng.choice(QUANTITY_VALUES, p=np.asarray(QUANTITY_PROBS) / sum(QUANTITY_PROBS)))


# ---------------------------------------------------------------------------
# Variant step sequences (transcribed exactly from spec `variants`).
# Each step: (activity, resource, concurrent_with_previous)
# ---------------------------------------------------------------------------

VARIANTS: dict[str, list[tuple[str, str, bool]]] = {
    "WF_101": [
        ("/hbw/unload", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/hbw/store_empty_bucket", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_1", True),
        ("/ov/burn", "ov_1", False),
        ("/ov/temper", "ov_1", False),
        ("/mm/mill", "mm_1", False),
        ("/mm/deburr", "mm_1", False),
        ("/sm/sort", "sm_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hw/human_review", "hw_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/get_empty_bucket", "hbw_1", True),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/store", "hbw_1", False),
    ],
    "WF_102": [
        ("/hbw/unload", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/wt/pick_up_and_transport", "wt_2", False),
        ("/mm/drill", "mm_2", False),
        ("/sm/transport", "sm_2", False),
        ("/dm/lower", "dm_2", False),
        ("/hbw/store_empty_bucket", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_1", True),
        ("/hw/human_review", "hw_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/get_empty_bucket", "hbw_1", True),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/store", "hbw_1", False),
    ],
    "WF_103": [
        ("/hbw/unload", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/hbw/store_empty_bucket", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_1", True),
        ("/ov/burn", "ov_1", False),
        ("/ov/temper", "ov_1", False),
        ("/wt/pick_up_and_transport", "wt_1", False),
        ("/mm/mill", "mm_1", False),
        ("/mm/deburr", "mm_1", False),
        ("/sm/transport", "sm_1", False),
        ("/pm/punch_recesses", "pm_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hw/human_review", "hw_1", False),
        ("/hbw/get_empty_bucket", "hbw_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/store", "hbw_1", False),
    ],
    "WF_104": [
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/hbw/store_empty_bucket", "hbw_2", False),
        ("/ov/burn", "ov_2", True),
        ("/wt/pick_up_and_transport", "wt_2", False),
        ("/mm/mill", "mm_2", False),
        ("/sm/sort", "sm_2", False),
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/wt/pick_up_and_transport", "wt_1", False),
        ("/mm/deburr", "mm_1", False),
        ("/sm/transport", "sm_1", False),
        ("/pm/punch_gill", "pm_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hw/human_review", "hw_1", False),
        ("/hbw/get_empty_bucket", "hbw_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/store", "hbw_1", False),
    ],
    "WF_105": [
        ("/hbw/unload", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/hbw/store_empty_bucket", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_1", True),
        ("/ov/burn", "ov_1", False),
        ("/wt/pick_up_and_transport", "wt_1", False),
        ("/mm/deburr", "mm_1", False),
        ("/sm/sort", "sm_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hw/human_review", "hw_1", False),
        ("/hbw/get_empty_bucket", "hbw_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/store", "hbw_1", False),
    ],
    "WF_108": [
        ("/hbw/unload", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/hbw/store_empty_bucket", "hbw_2", False),
        ("/ov/burn", "ov_2", True),
        ("/wt/pick_up_and_transport", "wt_2", False),
        ("/mm/drill", "mm_2", False),
        ("/mm/deburr", "mm_2", False),
        ("/sm/sort", "sm_2", False),
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hw/human_review", "hw_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/get_empty_bucket", "hbw_1", True),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/store", "hbw_1", False),
    ],
    "WF_109": [
        ("/hbw/unload", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/hbw/store_empty_bucket", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_1", True),
        ("/ov/burn", "ov_1", False),
        ("/ov/temper", "ov_1", False),
        ("/wt/pick_up_and_transport", "wt_1", False),
        ("/mm/mill", "mm_1", False),
        ("/mm/deburr", "mm_1", False),
        ("/sm/transport", "sm_1", False),
        ("/pm/punch_ribbing", "pm_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hw/human_review", "hw_1", False),
        ("/hbw/get_empty_bucket", "hbw_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/store", "hbw_1", False),
    ],
    "WF_1106": [
        ("/hbw/unload", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/ov/burn", "ov_2", False),
        ("/wt/pick_up_and_transport", "wt_2", False),
        ("/hbw/get_empty_bucket", "hbw_1", False),
        ("/mm/transport_from_to", "mm_2", False),
        ("/sm/transport", "sm_2", False),
        ("/dm/cylindrical_drill", "dm_2", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hw/human_review", "hw_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/get_empty_bucket", "hbw_1", True),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/store", "hbw_1", False),
    ],
    "WF_1107": [
        ("/hbw/unload", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_2", False),
        ("/hbw/store_empty_bucket", "hbw_2", False),
        ("/vgr/pick_up_and_transport", "vgr_1", True),
        ("/ov/burn", "ov_1", False),
        ("/wt/pick_up_and_transport", "wt_1", False),
        ("/mm/drill", "mm_1", False),
        ("/sm/transport", "sm_1", False),
        ("/pm/punch_ribbing", "pm_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hw/human_review", "hw_1", False),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/get_empty_bucket", "hbw_1", True),
        ("/vgr/pick_up_and_transport", "vgr_1", False),
        ("/hbw/store", "hbw_1", False),
    ],
}


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

EVENT_LOG_COLUMNS = [
    "case_id", "variant", "activity", "resource", "case_arrival",
    "queue_enter", "time:timestamp", "operation_end_time", "lifecycle:state",
]


def run_single_replication(seed: int) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)

    # Knobs read at call time (never copied at import).
    horizon = float(SIMULATION_TIME)
    rate_scale = float(ARRIVAL_RATE_SCALE)
    if rate_scale <= 0.0:
        rate_scale = 1.0
    failures_enabled = bool(FAILURES_ENABLED)

    env = simpy.Environment()

    # hbw class uses PriorityResource (activity priority); all others FIFO.
    resources = {}
    for name, cap in RESOURCE_CAPACITIES.items():
        if name.startswith("hbw_"):
            resources[name] = simpy.PriorityResource(env, cap)
        else:
            resources[name] = simpy.Resource(env, cap)

    # Samplers (full distributions, not means).
    duration_samplers = {act: make_sampler(d, rng)
                         for act, d in ACTIVITY_DISTRIBUTIONS.items()}
    res_samplers = {
        act: {res: make_sampler(d, rng) for res, d in splits.items()}
        for act, splits in RESOURCE_DURATIONS.items()
    }
    init_burst_iat = make_sampler(INITIAL_BURST_IAT, rng)
    steady_burst_size = make_sampler(STEADY_BURST_SIZE, rng)
    steady_intra_iat = make_sampler(STEADY_INTRA_BURST_IAT, rng)
    steady_gap = make_sampler(STEADY_INTER_BURST_GAP, rng)
    vprobs = np.asarray(VARIANT_PROBS, dtype=float)
    vprobs = vprobs / vprobs.sum()

    def pick_variant() -> str:
        return str(rng.choice(VARIANT_NAMES, p=vprobs))

    def sample_duration(activity: str, resource: str) -> float:
        # Per-resource conditioning (binding) for sm/wt/vgr transports.
        splits = res_samplers.get(activity)
        if splits is not None and resource in splits:
            return splits[resource]()
        return duration_samplers[activity]()

    def failure_probability(activity: str, resource: str) -> float:
        if not failures_enabled:
            return 0.0
        p = FAILURE_PROBABILITIES.get(activity, 0.0)
        # All observed vgr failures were on vgr_1 (5/37); vgr_2 0/18.
        if activity == "/vgr/pick_up_and_transport" and resource != VGR_FAILURE_RESOURCE:
            return 0.0
        return p

    rows: list[dict] = []

    def log_row(case_id, variant, activity, resource, case_arrival,
                queue_enter, start, end, state):
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

    def run_step(case_id, variant, case_arrival, activity, resource,
                 on_grant=None):
        """One attempt loop with geometric retries; logs one row per attempt.

        A failed attempt holds the resource for a short time (0.1x the sampled
        service time), is logged as 'failure', and the case immediately
        re-requests the same resource until success. `on_grant`, if given, is
        invoked at service start (used to spawn a concurrent step while this
        step still holds its resource).
        """
        first_grant = True
        while True:
            queue_enter = env.now
            res = resources[resource]
            if isinstance(res, simpy.PriorityResource):
                priority = HBW_PRIORITY_ORDER.index(activity)
                req = res.request(priority)
            else:
                req = res.request()
            yield req
            start = env.now
            if first_grant and on_grant is not None:
                on_grant()
            first_grant = False
            dur = sample_duration(activity, resource)
            failed = rng.random() < failure_probability(activity, resource)
            if failed:
                fail_dur = max(0.0, 0.1 * dur)
                yield env.timeout(fail_dur)
                res.release(req)
                log_row(case_id, variant, activity, resource, case_arrival,
                        queue_enter, start, env.now, "failure")
                continue
            yield env.timeout(dur)
            res.release(req)
            log_row(case_id, variant, activity, resource, case_arrival,
                    queue_enter, start, env.now, "success")
            return

    def concurrent_step(case_id, variant, case_arrival, activity, resource,
                        done):
        # Background process for a concurrent_with_previous step; it requests
        # its resource at the moment the previous step's service starts.
        yield from run_step(case_id, variant, case_arrival, activity, resource)
        done.succeed()

    def case_process(case_id, variant, case_arrival, steps):
        i = 0
        n = len(steps)
        while i < n:
            activity, resource, concurrent = steps[i]
            if rng.random() >= 1.0:  # step probability (1.0 for all spec steps)
                i += 1
                continue
            if activity in QUANTITY_STEPS:
                _sample_quantity(rng)  # case-state attribute; no conditioning
            if i + 1 < n and steps[i + 1][2]:
                # Next step is concurrent_with_previous: it requests its
                # resource while this step holds its resource (spec evidence:
                # "requested while the previous step still holds its
                # resource", observed overlaps 26-39 s).
                a2, r2, _ = steps[i + 1]
                done = simpy.Event(env)

                def spawn(a=a2, r=r2, d=done):
                    env.process(concurrent_step(case_id, variant, case_arrival,
                                                 a, r, d))

                yield from run_step(case_id, variant, case_arrival, activity,
                                    resource, on_grant=spawn)
                # Join: the case cannot proceed to the next sequential step
                # until the concurrent step has completed.
                yield done
                i += 2
            else:
                yield from run_step(case_id, variant, case_arrival,
                                    activity, resource)
                i += 1

    def arrivals():
        case_idx = 0
        # Phase 1: initial near-simultaneous burst of 8 cases, first at t=0.
        for i in range(INITIAL_BURST_CASES):
            case_idx += 1
            variant = pick_variant()
            env.process(case_process(f"case_{case_idx}", variant, env.now,
                                     VARIANTS[variant]))
            if i < INITIAL_BURST_CASES - 1:
                yield env.timeout(init_burst_iat() / rate_scale)
        # Transition gap (single observation; fixed, scaled by rate).
        yield env.timeout(TRANSITION_GAP_S / rate_scale)
        # Phase 2: steady-state bursty releases until the horizon is exhausted.
        while env.now < horizon:
            k = int(steady_burst_size())
            for j in range(k):
                if env.now >= horizon:
                    break
                case_idx += 1
                variant = pick_variant()
                env.process(case_process(f"case_{case_idx}", variant, env.now,
                                         VARIANTS[variant]))
                if j < k - 1:
                    yield env.timeout(steady_intra_iat() / rate_scale)
            if env.now < horizon:
                yield env.timeout(steady_gap() / rate_scale)

    env.process(arrivals())
    env.run(until=horizon)

    df = pd.DataFrame(rows, columns=EVENT_LOG_COLUMNS)
    return df


if __name__ == "__main__":
    df = run_single_replication(1)
    print(df.shape)
    print(df.head(10))
    # --- sanity checks ---
    req_cols = ["case_id", "variant", "activity", "resource", "case_arrival",
                "queue_enter", "time:timestamp", "operation_end_time",
                "lifecycle:state"]
    assert list(df.columns) == req_cols, df.columns
    assert (df["operation_end_time"] >= df["time:timestamp"]).all()
    assert (df["time:timestamp"] >= df["queue_enter"]).all()
    assert (df["queue_enter"] >= df["case_arrival"]).all()
    assert (df["case_arrival"] >= 0).all()
    assert df["resource"].isin(RESOURCE_CAPACITIES).all()
    assert df["variant"].isin(VARIANT_NAMES).all()
    assert df["activity"].isin(ACTIVITY_DISTRIBUTIONS).all()
    assert df["lifecycle:state"].isin(["success", "failure"]).all()
    assert not df["case_id"].str.contains(r"WF_").any()
    # every failure row is followed by a success row (same case/activity/
    # resource), unless the case was truncated at the horizon (no further rows).
    for cid, g in df.sort_values(["case_arrival", "queue_enter"]).groupby("case_id"):
        for i, r in g.iterrows():
            if r["lifecycle:state"] == "failure":
                later = g.loc[g.index > i]
                if len(later) == 0:
                    continue  # truncated at horizon: retry not started
                nxt = later[(later["activity"] == r["activity"]) &
                            (later["resource"] == r["resource"])]
                assert len(nxt) > 0 and \
                    (nxt["lifecycle:state"] == "success").any(), \
                    f"unresolved failure for {cid} {r['activity']}"
    # per-case ordering: first-success time of routing step i must be >= that
    # of step i-1, except a concurrent step may finish before its predecessor
    # (but before the following sequential step).
    for cid, g in df.groupby("case_id"):
        routing = VARIANTS[g["variant"].iloc[0]]
        # Occurrence-based greedy match of routing steps against the case's
        # successful attempts (sorted by service start).
        succ = [r for _, r in g.iterrows()
                if r["lifecycle:state"] == "success"]
        succ.sort(key=lambda r: (r["time:timestamp"], r["queue_enter"]))
        free = {a: [r for r in succ if r["activity"] == a]
                for a in {a for a, _, _ in routing}}
        prev_start = prev_end = 0.0
        for i, (a_i, _, conc_i) in enumerate(routing):
            # A concurrent step may start as soon as its predecessor starts;
            # a sequential step (including the step after a concurrent one,
            # i.e. the join) starts only after the previous step ended.
            bound = prev_start if conc_i else prev_end
            cands = [r for r in free[a_i]
                     if r["time:timestamp"] >= bound - 1e-9]
            if not cands:
                break  # truncated at horizon
            row = cands[0]
            free[a_i].remove(row)
            prev_start, prev_end = row["time:timestamp"], row["operation_end_time"]
    print("rows:", len(df), "| failures:", int((df["lifecycle:state"] == "failure").sum()),
          "| cases:", df["case_id"].nunique(),
          "| completed:", int(df[df["activity"] == "/hbw/store"].shape[0]))
    print("SANITY OK")
