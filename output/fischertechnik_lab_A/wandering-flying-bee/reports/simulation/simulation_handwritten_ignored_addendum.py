"""SimPy model of the Fischertechnik Lab A two-line manufacturing system.

Two-line layout:
  Line 1: hbw_2 (intake warehouse) -> vgr_2 -> machines (ov/mm/wt/sm/dm/pm)
  Line 2: hbw_1 (return warehouse) -> vgr_1 -> hw_1 (human review) + return path

Implements OUTPUT CONTRACT v2:
  - run_single_replication(seed) -> pandas.DataFrame (event log)
  - RESOURCE_CAPACITIES, SIMULATION_TIME, ARRIVAL_RATE_SCALE, FAILURES_ENABLED
    (knobs read at call time)

Arrivals: two-phase process - initial near-simultaneous burst of 8 cases
(intra_burst_iat) followed by steady-state bursts separated by
inter_burst_gap (burst_size categorical = 1). No WIP cap.

Failures: retryable, per-activity failure_probability, gated on
FAILURES_ENABLED. A failed attempt occupies the resource for a service time
drawn from the same distribution and is logged as its own 'failure' row; the
step then retries until success.

Concurrency: steps flagged concurrent_with_previous run in a background
process in parallel with the previous step's service; the next non-concurrent
step waits for both.
"""

import random

import numpy as np
import pandas as pd
import simpy
import scipy.stats

# ---------------------------------------------------------------------------
# Contract symbols
# ---------------------------------------------------------------------------

RESOURCE_CAPACITIES = {
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

EVENT_LOG_COLUMNS = [
    "case_id",
    "variant",
    "activity",
    "resource",
    "case_arrival",
    "queue_enter",
    "time:timestamp",
    "operation_end_time",
    "lifecycle:state",
]

# ---------------------------------------------------------------------------
# Spec data (durations, variants, arrivals) - embedded verbatim from spec
# ---------------------------------------------------------------------------

ACTIVITIES = {
    "/dm/cylindrical_drill": {
        "eligible_resources": ["dm_2"],
        "duration": {"family": "triang", "params": {"c": 0.5, "loc": 21.969, "scale": 4.046}},
        "failure_probability": 0.0,
    },
    "/dm/lower": {
        "eligible_resources": ["dm_2"],
        "duration": {"family": "triang", "params": {"c": 0.5, "loc": 13.875, "scale": 0.266}},
        "failure_probability": 0.0,
    },
    "/hbw/get_empty_bucket": {
        "eligible_resources": ["hbw_1"],
        "duration": {
            "family": "empirical_quantiles",
            "quantiles": [30.797, 31.1795, 31.562, 33.2655, 34.969, 35.3985, 35.828,
                          35.9115, 35.995, 36.107, 36.219, 36.3285, 36.438, 36.6095,
                          36.781, 36.8275, 36.874, 40.249, 43.624, 46.109, 48.594],
            "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
                               0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
        },
        "failure_probability": 0.0,
    },
    "/hbw/store": {
        "eligible_resources": ["hbw_1"],
        "duration": {"family": "triang", "params": {"c": 0.30222, "loc": 34.641, "scale": 7.703}},
        "failure_probability": 0.0,
    },
    "/hbw/store_empty_bucket": {
        "eligible_resources": ["hbw_2"],
        "duration": {
            "family": "empirical_quantiles",
            "quantiles": [32.641, 33.7936, 34.9214, 35.9996, 36.4718, 36.641, 36.7658,
                          37.1636, 38.1074, 39.3156, 40.656, 40.7124, 40.7844, 40.8876,
                          41.572, 42.547, 42.556, 43.009, 44.35, 44.825, 44.867],
            "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
                               0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
        },
        "failure_probability": 0.1333,
    },
    "/hbw/unload": {
        "eligible_resources": ["hbw_2"],
        "duration": {
            "family": "empirical_quantiles",
            "quantiles": [32.735, 32.8865, 33.078, 33.676, 35.047, 35.96125, 36.3705,
                          36.48125, 36.5, 37.88975, 38.4265, 38.51175, 38.547, 38.664,
                          39.0705, 40.69575, 44.469, 45.60525, 47.6165, 49.99875, 52.248],
            "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
                               0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
        },
        "failure_probability": 0.0588,
    },
    "/hw/human_review": {
        "eligible_resources": ["hw_1"],
        "duration": {
            "family": "empirical_quantiles",
            "quantiles": [0.438, 1.2297, 1.6596, 1.6674, 1.7832, 1.86775, 1.8879,
                          2.0538, 2.4278, 3.2104, 3.75, 5.0822, 9.2994, 11.75575,
                          13.6515, 16.76825, 21.5766, 28.02975, 41.5335, 52.8354, 62.25],
            "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
                               0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
        },
        "failure_probability": 0.0,
    },
    "/mm/deburr": {
        "eligible_resources": ["mm_1", "mm_2"],
        "duration": {"family": "triang", "params": {"c": 0.35964, "loc": 14.046, "scale": 1.001}},
        "failure_probability": 0.0,
    },
    "/mm/drill": {
        "eligible_resources": ["mm_1", "mm_2"],
        "duration": {"family": "triang", "params": {"c": 0.672512, "loc": 5.281, "scale": 15.625}},
        "failure_probability": 0.0,
    },
    "/mm/mill": {
        "eligible_resources": ["mm_1", "mm_2"],
        "duration": {"family": "triang", "params": {"c": 0.005911, "loc": 5.047, "scale": 9.39}},
        "failure_probability": 0.0,
    },
    "/mm/transport_from_to": {
        "eligible_resources": ["mm_2"],
        "duration": {"family": "triang", "params": {"c": 0.5, "loc": 12.594, "scale": 0.547}},
        "failure_probability": 0.0,
    },
    "/ov/burn": {
        "eligible_resources": ["ov_1", "ov_2"],
        "duration": {
            "family": "empirical_quantiles",
            "quantiles": [21.422, 21.5528, 21.6402, 21.6408, 23.5722, 26.469, 26.5254,
                          26.6292, 26.8278, 28.7612, 31.562, 31.6268, 31.7048, 31.8092,
                          33.7752, 36.672, 36.7842, 36.8592, 36.8598, 38.8288, 41.782],
            "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
                               0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
        },
        "failure_probability": 0.0,
    },
    "/ov/temper": {
        "eligible_resources": ["ov_1"],
        "duration": {"family": "triang", "params": {"c": 0.592357, "loc": 51.453, "scale": 0.157}},
        "failure_probability": 0.0,
    },
    "/pm/punch_gill": {
        "eligible_resources": ["pm_1"],
        "duration": {"family": "constant", "params": {"value": 27.484}},
        "failure_probability": 0.0,
    },
    "/pm/punch_recesses": {
        "eligible_resources": ["pm_1"],
        "duration": {"family": "triang", "params": {"c": 0.5, "loc": 23.453, "scale": 0.375}},
        "failure_probability": 0.0,
    },
    "/pm/punch_ribbing": {
        "eligible_resources": ["pm_1"],
        "duration": {"family": "triang", "params": {"c": 0.5, "loc": 23.562, "scale": 7.657}},
        "failure_probability": 0.0,
    },
    "/sm/sort": {
        "eligible_resources": ["sm_1", "sm_2"],
        "duration": {"family": "triang", "params": {"c": 0.015929, "loc": 8.36, "scale": 237.34}},
        "failure_probability": 0.0,
    },
    "/sm/transport": {
        "eligible_resources": ["sm_1", "sm_2"],
        "duration": {"family": "triang", "params": {"c": 0.537006, "loc": 14.39, "scale": 7.188}},
        "failure_probability": 0.0,
    },
    "/vgr/pick_up_and_transport": {
        "eligible_resources": ["vgr_1", "vgr_2"],
        "duration": {
            "family": "empirical_quantiles",
            "quantiles": [13.109, 19.69005, 24.3436, 35.9146, 36.4466, 36.69925,
                          37.1669, 38.23905, 40.6844, 42.0459, 42.7875, 43.28035,
                          43.5968, 43.9038, 44.2546, 46.1175, 48.8516, 51.1126,
                          53.1308, 59.9139, 88.375],
            "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
                               0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
        },
        "failure_probability": 0.0909,
    },
    "/wt/pick_up_and_transport": {
        "eligible_resources": ["wt_1", "wt_2"],
        "duration": {
            "family": "empirical_quantiles",
            "quantiles": [25.906, 25.9268, 25.9425, 25.95225, 25.9716, 26.0155, 26.0974,
                          26.12705, 26.1846, 26.3263, 26.362, 26.7415, 28.373, 28.8822,
                          28.9118, 29.047, 29.1406, 29.20375, 29.2135, 29.22395, 29.235],
            "quantile_probs": [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
                               0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
        },
        "failure_probability": 0.0,
    },
}

# HBW activity-priority queue: lower value = served first.
HBW_PRIORITY_ORDER = ["/hbw/store", "/hbw/store_empty_bucket", "/hbw/get_empty_bucket", "/hbw/unload"]

# Variants: name -> (probability, steps). Each step:
#   (activity, resource, probability, concurrent_with_previous)
VARIANTS = {
    "WF_101": (0.1111, [
        ("/hbw/unload", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/hbw/store_empty_bucket", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, True),
        ("/ov/burn", "ov_1", 1.0, False),
        ("/ov/temper", "ov_1", 1.0, False),
        ("/mm/mill", "mm_1", 1.0, False),
        ("/mm/deburr", "mm_1", 1.0, False),
        ("/sm/sort", "sm_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hw/human_review", "hw_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/get_empty_bucket", "hbw_1", 1.0, True),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/store", "hbw_1", 1.0, False),
    ]),
    "WF_102": (0.1111, [
        ("/hbw/unload", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/wt/pick_up_and_transport", "wt_2", 1.0, False),
        ("/mm/drill", "mm_2", 1.0, False),
        ("/sm/transport", "sm_2", 1.0, False),
        ("/dm/lower", "dm_2", 1.0, False),
        ("/hbw/store_empty_bucket", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, True),
        ("/hw/human_review", "hw_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/get_empty_bucket", "hbw_1", 1.0, True),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/store", "hbw_1", 1.0, False),
    ]),
    "WF_103": (0.1111, [
        ("/hbw/unload", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/hbw/store_empty_bucket", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, True),
        ("/ov/burn", "ov_1", 1.0, False),
        ("/ov/temper", "ov_1", 1.0, False),
        ("/wt/pick_up_and_transport", "wt_1", 1.0, False),
        ("/mm/mill", "mm_1", 1.0, False),
        ("/mm/deburr", "mm_1", 1.0, False),
        ("/sm/transport", "sm_1", 1.0, False),
        ("/pm/punch_recesses", "pm_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hw/human_review", "hw_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/get_empty_bucket", "hbw_1", 1.0, True),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/store", "hbw_1", 1.0, False),
    ]),
    "WF_104": (0.1111, [
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/hbw/store_empty_bucket", "hbw_2", 1.0, False),
        ("/ov/burn", "ov_2", 1.0, True),
        ("/wt/pick_up_and_transport", "wt_2", 1.0, False),
        ("/mm/mill", "mm_2", 1.0, False),
        ("/sm/sort", "sm_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/wt/pick_up_and_transport", "wt_1", 1.0, False),
        ("/mm/deburr", "mm_1", 1.0, False),
        ("/sm/transport", "sm_1", 1.0, False),
        ("/pm/punch_gill", "pm_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hw/human_review", "hw_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/get_empty_bucket", "hbw_1", 1.0, True),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/store", "hbw_1", 1.0, False),
    ]),
    "WF_105": (0.1111, [
        ("/hbw/unload", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/hbw/store_empty_bucket", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, True),
        ("/ov/burn", "ov_1", 1.0, False),
        ("/wt/pick_up_and_transport", "wt_1", 1.0, False),
        ("/mm/deburr", "mm_1", 1.0, False),
        ("/sm/sort", "sm_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hw/human_review", "hw_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/get_empty_bucket", "hbw_1", 1.0, True),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/store", "hbw_1", 1.0, False),
    ]),
    "WF_108": (0.1111, [
        ("/hbw/unload", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/hbw/store_empty_bucket", "hbw_2", 1.0, False),
        ("/ov/burn", "ov_2", 1.0, True),
        ("/wt/pick_up_and_transport", "wt_2", 1.0, False),
        ("/mm/drill", "mm_2", 1.0, False),
        ("/mm/deburr", "mm_2", 1.0, False),
        ("/sm/sort", "sm_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hw/human_review", "hw_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/get_empty_bucket", "hbw_1", 1.0, True),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/store", "hbw_1", 1.0, False),
    ]),
    "WF_109": (0.1111, [
        ("/hbw/unload", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/hbw/store_empty_bucket", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, True),
        ("/ov/burn", "ov_1", 1.0, False),
        ("/ov/temper", "ov_1", 1.0, False),
        ("/wt/pick_up_and_transport", "wt_1", 1.0, False),
        ("/mm/mill", "mm_1", 1.0, False),
        ("/mm/deburr", "mm_1", 1.0, False),
        ("/sm/transport", "sm_1", 1.0, False),
        ("/pm/punch_ribbing", "pm_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hw/human_review", "hw_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/get_empty_bucket", "hbw_1", 1.0, True),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/store", "hbw_1", 1.0, False),
    ]),
    "WF_1106": (0.1111, [
        ("/hbw/unload", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/ov/burn", "ov_2", 1.0, False),
        ("/wt/pick_up_and_transport", "wt_2", 1.0, False),
        ("/hbw/get_empty_bucket", "hbw_1", 1.0, False),
        ("/mm/transport_from_to", "mm_2", 1.0, False),
        ("/sm/transport", "sm_2", 1.0, False),
        ("/dm/cylindrical_drill", "dm_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hw/human_review", "hw_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/get_empty_bucket", "hbw_1", 1.0, True),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/store", "hbw_1", 1.0, False),
    ]),
    "WF_1107": (0.1111, [
        ("/hbw/unload", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_2", 1.0, False),
        ("/hbw/store_empty_bucket", "hbw_2", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, True),
        ("/ov/burn", "ov_1", 1.0, False),
        ("/wt/pick_up_and_transport", "wt_1", 1.0, False),
        ("/mm/drill", "mm_1", 1.0, False),
        ("/sm/transport", "sm_1", 1.0, False),
        ("/pm/punch_ribbing", "pm_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hw/human_review", "hw_1", 1.0, False),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/get_empty_bucket", "hbw_1", 1.0, True),
        ("/vgr/pick_up_and_transport", "vgr_1", 1.0, False),
        ("/hbw/store", "hbw_1", 1.0, False),
    ]),
}

VARIANT_NAMES = list(VARIANTS.keys())
VARIANT_PROBS = np.array([VARIANTS[n][0] for n in VARIANT_NAMES], dtype=float)
VARIANT_PROBS = VARIANT_PROBS / VARIANT_PROBS.sum()

# Arrival process (two_regime_bursts)
BURST_SIZE_DIST = {"family": "categorical", "values": [1.0], "probs": [1.0]}
INTRA_BURST_IAT_DIST = {
    "family": "empirical_quantiles",
    "quantiles": [0.509594, 0.588207, 0.675077, 0.778461, 0.846248, 0.896236,
                  0.902036, 1.021675, 1.36899, 1.553163, 1.655765],
    "quantile_probs": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
}
INTER_BURST_GAP_DIST = {
    "family": "empirical_quantiles",
    "quantiles": [0.687498, 1.737551, 2.215419, 3.62787, 23.106189, 93.406176,
                  129.969146, 224.187508, 295.69344, 414.291098, 799.956625],
    "quantile_probs": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
}
INITIAL_BURST_SIZE = 8.0  # constant, from spec arrivals.initial_burst


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


# ---------------------------------------------------------------------------
# Model implementation (filled in below)
# ---------------------------------------------------------------------------

def _hbw_priority(activity: str) -> int:
    """Priority value for hbw requests (lower = served first)."""
    try:
        return HBW_PRIORITY_ORDER.index(activity)
    except ValueError:
        return len(HBW_PRIORITY_ORDER)


def run_single_replication(seed: int) -> pd.DataFrame:
    """Run one full replication; return the event log as a DataFrame.

    Seeds the RNGs, builds the SimPy environment and all resources from
    RESOURCE_CAPACITIES, runs until SIMULATION_TIME, and returns one event log.
    Knobs (SIMULATION_TIME, ARRIVAL_RATE_SCALE, FAILURES_ENABLED) are read at
    call time. No file I/O, no state across calls.
    """
    random.seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)

    # Read knobs at call time (harness may override the module globals).
    horizon = float(SIMULATION_TIME)
    arrival_scale = float(ARRIVAL_RATE_SCALE) if ARRIVAL_RATE_SCALE else 1.0
    failures_enabled = bool(FAILURES_ENABLED)

    env = simpy.Environment()

    # One simpy.Resource per concrete resource (capacity from RESOURCE_CAPACITIES).
    resources = {name: simpy.Resource(env, cap) for name, cap in RESOURCE_CAPACITIES.items()}

    # Duration samplers (one per activity) + arrival samplers.
    duration_samplers = {act: make_sampler(meta["duration"], rng)
                         for act, meta in ACTIVITIES.items()}
    intra_iat_sampler = make_sampler(INTRA_BURST_IAT_DIST, rng)
    inter_gap_sampler = make_sampler(INTER_BURST_GAP_DIST, rng)
    burst_size_sampler = make_sampler(BURST_SIZE_DIST, rng)

    rows = []

    def sample_variant() -> str:
        return str(rng.choice(VARIANT_NAMES, p=VARIANT_PROBS))

    def run_step(case_id, variant, activity, resource_name, arrival_time):
        """Generator: request resource, serve (with retryable failure), log row."""
        res = resources[resource_name]
        is_hbw = resource_name.startswith("hbw")
        dur_sampler = duration_samplers[activity]
        fail_prob = ACTIVITIES[activity]["failure_probability"]
        while True:
            queue_enter = env.now
            if is_hbw:
                req = res.request(priority=_hbw_priority(activity))
            else:
                req = res.request()
            yield req  # blocks until granted
            start = env.now
            try:
                duration = dur_sampler()
                failed = bool(failures_enabled and (fail_prob > 0.0)
                              and (rng.random() < fail_prob))
                yield env.timeout(duration)
                end = env.now
                rows.append({
                    "case_id": case_id,
                    "variant": variant,
                    "activity": activity,
                    "resource": resource_name,
                    "case_arrival": float(arrival_time),
                    "queue_enter": float(queue_enter),
                    "time:timestamp": float(start),
                    "operation_end_time": float(end),
                    "lifecycle:state": "failure" if failed else "success",
                })
                if not failed:
                    return
            finally:
                res.release(req)

    def case_process(case_id, variant, arrival_time):
        """Walk the variant route; run concurrent steps in background processes."""
        steps = VARIANTS[variant][1]
        pending = []
        for i, (activity, resource_name, prob, conc) in enumerate(steps):
            if rng.random() > prob:
                continue  # step skipped (probability < 1); not used here (all 1.0)
            if i + 1 < len(steps) and steps[i + 1][3]:
                # Next step is concurrent_with_previous -> run this step in the
                # background so the next step starts in parallel with it.
                pending.append(env.process(
                    run_step(case_id, variant, activity, resource_name, arrival_time)))
            else:
                yield from run_step(case_id, variant, activity, resource_name, arrival_time)
                # A non-concurrent step must wait for any in-flight background
                # step (the first element of the concurrent pair) to finish.
                if pending:
                    for bg in pending:
                        yield bg
                    pending = []
        if pending:
            for bg in pending:
                yield bg

    def arrival_process():
        """Two-phase arrivals: initial 8-case burst + steady-state bursts."""
        case_counter = 0

        def release_case(now):
            nonlocal case_counter
            case_counter += 1
            variant = sample_variant()
            env.process(case_process(f"case_{case_counter}", variant, now))

        # Phase 1: initial near-simultaneous burst of 8 cases.
        n_initial = int(INITIAL_BURST_SIZE)
        for j in range(n_initial):
            release_case(env.now)
            if j < n_initial - 1:
                yield env.timeout(intra_iat_sampler() / arrival_scale)

        # Phase 2: steady-state bursts separated by inter_burst_gap.
        while True:
            yield env.timeout(inter_gap_sampler() / arrival_scale)
            k = int(burst_size_sampler())
            for j in range(k):
                release_case(env.now)
                if j < k - 1:
                    yield env.timeout(intra_iat_sampler() / arrival_scale)

    env.process(arrival_process())
    env.run(until=horizon)

    df = pd.DataFrame(rows, columns=EVENT_LOG_COLUMNS)
    return df


if __name__ == "__main__":
    df = run_single_replication(1)
    print(df)
    print(f"rows={len(df)}")
