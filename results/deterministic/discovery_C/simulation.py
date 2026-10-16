"""SimPy model compiled from the simulation spec by src/genai4simpy_agent/compiler.py.

Implements output contract v2. All parameters live in SPEC (generated, do not edit by hand).
"""
import json
import random

import numpy as np
import pandas as pd
import scipy.stats
import simpy

SPEC = json.loads(r"""{
 "window": {
  "t0": "2021-07-01T18:48:23.227456+00:00",
  "horizon_s": 5461.506544,
  "terminal_activity": "/hbw/store"
 },
 "resources": [
  {
   "name": "dm_2",
   "resource_class": "dm",
   "capacity": 1
  },
  {
   "name": "hbw_1",
   "resource_class": "hbw",
   "capacity": 1
  },
  {
   "name": "hbw_2",
   "resource_class": "hbw",
   "capacity": 1
  },
  {
   "name": "hw_1",
   "resource_class": "hw",
   "capacity": 1
  },
  {
   "name": "mm_1",
   "resource_class": "mm",
   "capacity": 1
  },
  {
   "name": "mm_2",
   "resource_class": "mm",
   "capacity": 1
  },
  {
   "name": "ov_1",
   "resource_class": "ov",
   "capacity": 1
  },
  {
   "name": "ov_2",
   "resource_class": "ov",
   "capacity": 1
  },
  {
   "name": "pm_1",
   "resource_class": "pm",
   "capacity": 1
  },
  {
   "name": "sm_1",
   "resource_class": "sm",
   "capacity": 1
  },
  {
   "name": "sm_2",
   "resource_class": "sm",
   "capacity": 1
  },
  {
   "name": "vgr_1",
   "resource_class": "vgr",
   "capacity": 1
  },
  {
   "name": "vgr_2",
   "resource_class": "vgr",
   "capacity": 1
  },
  {
   "name": "wt_1",
   "resource_class": "wt",
   "capacity": 1
  },
  {
   "name": "wt_2",
   "resource_class": "wt",
   "capacity": 1
  }
 ],
 "activities": [
  {
   "name": "/dm/cylindrical_drill",
   "eligible_resources": [
    "dm_2"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.5,
     "loc": 39.078,
     "scale": 7.75
    },
    "mean": 42.953,
    "n": 2,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/dm/drill",
   "eligible_resources": [
    "dm_2"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.36581,
     "loc": 15.812,
     "scale": 26.142
    },
    "mean": 27.129,
    "n": 4,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/dm/lower",
   "eligible_resources": [
    "dm_2"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.96875,
     "loc": 13.828,
     "scale": 0.016
    },
    "mean": 13.8398,
    "n": 4,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/hbw/get_empty_bucket",
   "eligible_resources": [
    "hbw_1"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 38.3806,
    "n": 14,
    "source": "fit_activity_durations",
    "quantiles": [
     32.953,
     33.4613,
     33.8661,
     34.15015,
     35.3246,
     36.09725,
     36.1083,
     36.27335,
     36.4506,
     36.5923,
     36.7265,
     37.27095,
     39.1904,
     39.8305,
     40.0519,
     41.09775,
     41.85,
     42.39375,
     42.6375,
     44.62565,
     48.109
    ],
    "quantile_probs": [
     0.0,
     0.05,
     0.1,
     0.15,
     0.2,
     0.25,
     0.3,
     0.35,
     0.4,
     0.45,
     0.5,
     0.55,
     0.6,
     0.65,
     0.7,
     0.75,
     0.8,
     0.85,
     0.9,
     0.95,
     1.0
    ]
   },
   "failure_probability": 0.0
  },
  {
   "name": "/hbw/store",
   "eligible_resources": [
    "hbw_1"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 37.1995,
    "n": 13,
    "source": "fit_activity_durations",
    "quantiles": [
     30.734,
     31.2122,
     32.103,
     33.819,
     34.5154,
     34.702,
     34.9558,
     35.8468,
     38.0122,
     38.9592,
     39.297,
     39.3156,
     39.3782,
     39.5288,
     39.7038,
     39.891,
     39.9096,
     39.972,
     40.122,
     40.1784,
     40.188
    ],
    "quantile_probs": [
     0.0,
     0.05,
     0.1,
     0.15,
     0.2,
     0.25,
     0.3,
     0.35,
     0.4,
     0.45,
     0.5,
     0.55,
     0.6,
     0.65,
     0.7,
     0.75,
     0.8,
     0.85,
     0.9,
     0.95,
     1.0
    ]
   },
   "failure_probability": 0.0
  },
  {
   "name": "/hbw/store_empty_bucket",
   "eligible_resources": [
    "hbw_2"
   ],
   "duration": {
    "family": "uniform",
    "params": {
     "loc": 31.734,
     "scale": 12.297
    },
    "mean": 37.0133,
    "n": 34,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/hbw/unload",
   "eligible_resources": [
    "hbw_2"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 1e-06,
     "loc": 31.592982,
     "scale": 21.134166
    },
    "mean": 38.2486,
    "n": 35,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0541
  },
  {
   "name": "/hw/human_review",
   "eligible_resources": [
    "hw_1"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 46.8095,
    "n": 15,
    "source": "fit_activity_durations",
    "quantiles": [
     0.328,
     0.6339,
     0.809,
     1.3581,
     4.7398,
     5.806,
     7.3716,
     12.5012,
     15.8026,
     20.398,
     27.125,
     32.4842,
     43.575,
     57.216,
     60.366,
     62.25,
     73.3592,
     108.7974,
     114.9754,
     136.5222,
     185.063
    ],
    "quantile_probs": [
     0.0,
     0.05,
     0.1,
     0.15,
     0.2,
     0.25,
     0.3,
     0.35,
     0.4,
     0.45,
     0.5,
     0.55,
     0.6,
     0.65,
     0.7,
     0.75,
     0.8,
     0.85,
     0.9,
     0.95,
     1.0
    ]
   },
   "failure_probability": 0.0
  },
  {
   "name": "/mm/deburr",
   "eligible_resources": [
    "mm_1",
    "mm_2"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 17.0527,
    "n": 19,
    "source": "fit_activity_durations",
    "quantiles": [
     13.843,
     13.8574,
     13.8718,
     13.875,
     13.9596,
     14.0315,
     14.0534,
     14.072,
     14.0932,
     14.1081,
     14.235,
     14.2485,
     14.2628,
     14.266,
     14.3878,
     14.547,
     14.7126,
     14.9094,
     15.181,
     20.7475,
     66.562
    ],
    "quantile_probs": [
     0.0,
     0.05,
     0.1,
     0.15,
     0.2,
     0.25,
     0.3,
     0.35,
     0.4,
     0.45,
     0.5,
     0.55,
     0.6,
     0.65,
     0.7,
     0.75,
     0.8,
     0.85,
     0.9,
     0.95,
     1.0
    ]
   },
   "failure_probability": 0.0
  },
  {
   "name": "/mm/drill",
   "eligible_resources": [
    "mm_2"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.356553,
     "loc": 5.078,
     "scale": 27.125
    },
    "mean": 13.7109,
    "n": 8,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/mm/mill",
   "eligible_resources": [
    "mm_1",
    "mm_2"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 8.7129,
    "n": 11,
    "source": "fit_activity_durations",
    "quantiles": [
     5.078,
     5.179,
     5.28,
     5.2805,
     5.281,
     5.281,
     5.281,
     5.2815,
     5.282,
     5.6955,
     6.109,
     6.2105,
     6.312,
     10.164,
     14.016,
     14.1565,
     14.297,
     14.375,
     14.453,
     14.453,
     14.453
    ],
    "quantile_probs": [
     0.0,
     0.05,
     0.1,
     0.15,
     0.2,
     0.25,
     0.3,
     0.35,
     0.4,
     0.45,
     0.5,
     0.55,
     0.6,
     0.65,
     0.7,
     0.75,
     0.8,
     0.85,
     0.9,
     0.95,
     1.0
    ]
   },
   "failure_probability": 0.0
  },
  {
   "name": "/mm/transport_from_to",
   "eligible_resources": [
    "mm_1",
    "mm_2"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.752,
     "loc": 12.203,
     "scale": 0.25
    },
    "mean": 12.349,
    "n": 3,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/ov/burn",
   "eligible_resources": [
    "ov_1",
    "ov_2"
   ],
   "duration": {
    "family": "uniform",
    "params": {
     "loc": 21.421,
     "scale": 20.111
    },
    "mean": 30.4531,
    "n": 32,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/ov/temper",
   "eligible_resources": [
    "ov_1"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.070377,
     "loc": 51.437,
     "scale": 1.563
    },
    "mean": 51.7167,
    "n": 8,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/pm/punch_gill",
   "eligible_resources": [
    "pm_1"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.910159,
     "loc": 23.859,
     "scale": 3.829
    },
    "mean": 26.5588,
    "n": 4,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/pm/punch_recesses",
   "eligible_resources": [
    "pm_1"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.5,
     "loc": 23.672,
     "scale": 0.157
    },
    "mean": 23.7505,
    "n": 2,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/pm/punch_ribbing",
   "eligible_resources": [
    "pm_1"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.5,
     "loc": 23.344,
     "scale": 0.453
    },
    "mean": 23.5705,
    "n": 2,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/sm/sort",
   "eligible_resources": [
    "sm_1",
    "sm_2"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 11.7752,
    "n": 13,
    "source": "fit_activity_durations",
    "quantiles": [
     8.578,
     8.6062,
     8.6564,
     8.7506,
     9.3316,
     10.156,
     10.1746,
     10.2246,
     10.3374,
     10.5374,
     10.781,
     11.6342,
     12.2406,
     12.3534,
     12.6346,
     13.0,
     13.1872,
     13.334,
     13.4,
     16.5596,
     21.266
    ],
    "quantile_probs": [
     0.0,
     0.05,
     0.1,
     0.15,
     0.2,
     0.25,
     0.3,
     0.35,
     0.4,
     0.45,
     0.5,
     0.55,
     0.6,
     0.65,
     0.7,
     0.75,
     0.8,
     0.85,
     0.9,
     0.95,
     1.0
    ]
   },
   "failure_probability": 0.0
  },
  {
   "name": "/sm/transport",
   "eligible_resources": [
    "sm_1",
    "sm_2"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 18.9202,
    "n": 19,
    "source": "fit_activity_durations",
    "quantiles": [
     14.219,
     14.3036,
     14.4626,
     14.6092,
     14.6842,
     14.742,
     14.8062,
     14.8626,
     14.9186,
     14.969,
     14.969,
     18.5267,
     18.9596,
     18.9795,
     18.9936,
     19.0155,
     19.0438,
     19.2829,
     19.943,
     24.3107,
     58.328
    ],
    "quantile_probs": [
     0.0,
     0.05,
     0.1,
     0.15,
     0.2,
     0.25,
     0.3,
     0.35,
     0.4,
     0.45,
     0.5,
     0.55,
     0.6,
     0.65,
     0.7,
     0.75,
     0.8,
     0.85,
     0.9,
     0.95,
     1.0
    ]
   },
   "failure_probability": 0.0
  },
  {
   "name": "/vgr/pick_up_and_transport",
   "eligible_resources": [
    "vgr_1",
    "vgr_2"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.976708,
     "loc": 4.832668,
     "scale": 47.71674
    },
    "mean": 36.2701,
    "n": 101,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0288
  },
  {
   "name": "/wt/pick_up_and_transport",
   "eligible_resources": [
    "wt_1",
    "wt_2"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 27.715,
    "n": 29,
    "source": "fit_activity_durations",
    "quantiles": [
     25.812,
     25.922,
     25.9348,
     25.9582,
     26.031,
     26.031,
     26.031,
     26.0318,
     26.0492,
     26.1094,
     29.094,
     29.203,
     29.203,
     29.207,
     29.2748,
     29.313,
     29.3562,
     29.4218,
     29.437,
     29.4466,
     29.531
    ],
    "quantile_probs": [
     0.0,
     0.05,
     0.1,
     0.15,
     0.2,
     0.25,
     0.3,
     0.35,
     0.4,
     0.45,
     0.5,
     0.55,
     0.6,
     0.65,
     0.7,
     0.75,
     0.8,
     0.85,
     0.9,
     0.95,
     1.0
    ]
   },
   "failure_probability": 0.0
  }
 ],
 "variants": [
  {
   "name": "WF_101",
   "probability": 0.1081,
   "steps": [
    {
     "activity": "/hbw/unload",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/ov/burn",
     "resources": {
      "ov_1": 1.0
     }
    },
    {
     "activity": "/ov/temper",
     "resources": {
      "ov_1": 1.0
     }
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_1": 1.0
     }
    },
    {
     "activity": "/mm/mill",
     "resources": {
      "mm_1": 1.0
     }
    },
    {
     "activity": "/mm/deburr",
     "resources": {
      "mm_1": 1.0
     }
    },
    {
     "activity": "/sm/sort",
     "resources": {
      "sm_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hw/human_review",
     "resources": {
      "hw_1": 1.0
     }
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "resources": {
      "hbw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/store",
     "resources": {
      "hbw_1": 1.0
     }
    }
   ],
   "early_exit_probability": 0.5,
   "early_exit_after_n_steps": {
    "0": 1.0
   }
  },
  {
   "name": "WF_102",
   "probability": 0.1351,
   "steps": [
    {
     "activity": "/hbw/unload",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 0.6,
      "vgr_1": 0.4
     }
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/ov/burn",
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_2": 1.0
     }
    },
    {
     "activity": "/mm/drill",
     "resources": {
      "mm_2": 1.0
     }
    },
    {
     "activity": "/sm/transport",
     "resources": {
      "sm_2": 1.0
     }
    },
    {
     "activity": "/dm/lower",
     "resources": {
      "dm_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hw/human_review",
     "resources": {
      "hw_1": 1.0
     }
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "resources": {
      "hbw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/store",
     "resources": {
      "hbw_1": 1.0
     }
    }
   ],
   "early_exit_probability": 0.6,
   "early_exit_after_n_steps": {
    "6": 0.333,
    "8": 0.333,
    "12": 0.333
   }
  },
  {
   "name": "WF_103",
   "probability": 0.1351,
   "steps": [
    {
     "activity": "/hbw/unload",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/ov/burn",
     "resources": {
      "ov_1": 1.0
     }
    },
    {
     "activity": "/ov/temper",
     "resources": {
      "ov_1": 1.0
     }
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_1": 1.0
     }
    },
    {
     "activity": "/mm/mill",
     "resources": {
      "mm_1": 1.0
     }
    },
    {
     "activity": "/mm/deburr",
     "resources": {
      "mm_1": 1.0
     }
    },
    {
     "activity": "/sm/transport",
     "resources": {
      "sm_1": 1.0
     }
    },
    {
     "activity": "/pm/punch_recesses",
     "resources": {
      "pm_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hw/human_review",
     "resources": {
      "hw_1": 1.0
     }
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "resources": {
      "hbw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/store",
     "resources": {
      "hbw_1": 1.0
     }
    }
   ],
   "early_exit_probability": 0.6,
   "early_exit_after_n_steps": {
    "3": 0.333,
    "4": 0.333,
    "12": 0.333
   }
  },
  {
   "name": "WF_104",
   "probability": 0.0811,
   "steps": [
    {
     "activity": "/hbw/unload",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/ov/burn",
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_2": 1.0
     }
    },
    {
     "activity": "/sm/sort",
     "resources": {
      "sm_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 0.5,
      "vgr_2": 0.5
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_1": 1.0
     }
    },
    {
     "activity": "/mm/deburr",
     "resources": {
      "mm_1": 1.0
     }
    },
    {
     "activity": "/sm/transport",
     "resources": {
      "sm_1": 1.0
     }
    },
    {
     "activity": "/pm/punch_gill",
     "resources": {
      "pm_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hw/human_review",
     "resources": {
      "hw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/ov/burn",
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_2": 1.0
     }
    },
    {
     "activity": "/mm/mill",
     "resources": {
      "mm_2": 1.0
     }
    },
    {
     "activity": "/sm/sort",
     "resources": {
      "sm_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    }
   ],
   "early_exit_probability": 1.0,
   "early_exit_after_n_steps": {
    "6": 0.333,
    "15": 0.333,
    "23": 0.333
   }
  },
  {
   "name": "WF_105",
   "probability": 0.1081,
   "steps": [
    {
     "activity": "/hbw/unload",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/ov/burn",
     "resources": {
      "ov_1": 1.0
     }
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_1": 1.0
     }
    },
    {
     "activity": "/mm/deburr",
     "resources": {
      "mm_1": 1.0
     }
    },
    {
     "activity": "/sm/sort",
     "resources": {
      "sm_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hw/human_review",
     "resources": {
      "hw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "resources": {
      "hbw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/store",
     "resources": {
      "hbw_1": 1.0
     }
    }
   ],
   "early_exit_probability": 0.5,
   "early_exit_after_n_steps": {
    "8": 1.0
   }
  },
  {
   "name": "WF_108",
   "probability": 0.0811,
   "steps": [
    {
     "activity": "/hbw/unload",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/ov/burn",
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_2": 1.0
     }
    },
    {
     "activity": "/mm/drill",
     "resources": {
      "mm_2": 1.0
     }
    },
    {
     "activity": "/mm/deburr",
     "resources": {
      "mm_2": 1.0
     }
    },
    {
     "activity": "/sm/sort",
     "resources": {
      "sm_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hw/human_review",
     "resources": {
      "hw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "resources": {
      "hbw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/store",
     "resources": {
      "hbw_1": 1.0
     }
    }
   ],
   "early_exit_probability": 0.667,
   "early_exit_after_n_steps": {
    "7": 0.5,
    "9": 0.5
   }
  },
  {
   "name": "WF_109",
   "probability": 0.0811,
   "steps": [
    {
     "activity": "/hbw/unload",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/ov/burn",
     "resources": {
      "ov_1": 1.0
     }
    },
    {
     "activity": "/ov/temper",
     "resources": {
      "ov_1": 1.0
     }
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_1": 1.0
     }
    },
    {
     "activity": "/mm/mill",
     "resources": {
      "mm_1": 1.0
     }
    },
    {
     "activity": "/mm/deburr",
     "resources": {
      "mm_1": 1.0
     }
    },
    {
     "activity": "/sm/transport",
     "resources": {
      "sm_1": 1.0
     }
    },
    {
     "activity": "/pm/punch_ribbing",
     "resources": {
      "pm_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hw/human_review",
     "resources": {
      "hw_1": 1.0
     }
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "resources": {
      "hbw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/store",
     "resources": {
      "hbw_1": 1.0
     }
    }
   ],
   "early_exit_probability": 0.333,
   "early_exit_after_n_steps": {
    "8": 1.0
   }
  },
  {
   "name": "WF_1106",
   "probability": 0.1622,
   "steps": [
    {
     "activity": "/hbw/unload",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/ov/burn",
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_2": 1.0
     }
    },
    {
     "activity": "/mm/transport_from_to",
     "resources": {
      "mm_2": 1.0
     }
    },
    {
     "activity": "/sm/transport",
     "resources": {
      "sm_2": 1.0
     }
    },
    {
     "activity": "/dm/drill",
     "resources": {
      "dm_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hw/human_review",
     "resources": {
      "hw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "resources": {
      "hbw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/store",
     "resources": {
      "hbw_1": 1.0
     }
    }
   ],
   "early_exit_probability": 0.833,
   "early_exit_after_n_steps": {
    "7": 0.4,
    "8": 0.6
   }
  },
  {
   "name": "WF_1107",
   "probability": 0.1081,
   "steps": [
    {
     "activity": "/hbw/unload",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_2": 1.0
     }
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/ov/burn",
     "resources": {
      "ov_1": 1.0
     }
    },
    {
     "activity": "/mm/transport_from_to",
     "resources": {
      "mm_1": 1.0
     }
    },
    {
     "activity": "/sm/transport",
     "resources": {
      "sm_1": 1.0
     }
    },
    {
     "activity": "/pm/punch_gill",
     "resources": {
      "pm_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hw/human_review",
     "resources": {
      "hw_1": 1.0
     }
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "resources": {
      "hbw_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "resources": {
      "vgr_1": 1.0
     }
    },
    {
     "activity": "/hbw/store",
     "resources": {
      "hbw_1": 1.0
     }
    }
   ],
   "early_exit_probability": 0.75,
   "early_exit_after_n_steps": {
    "1": 0.333,
    "3": 0.333,
    "8": 0.333
   }
  }
 ],
 "arrivals": {
  "model": "two_regime_bursts",
  "burst_size": {
   "family": "categorical",
   "values": [
    1,
    2,
    3,
    5,
    9
   ],
   "probs": [
    0.3333,
    0.25,
    0.0833,
    0.25,
    0.0833
   ],
   "mean": 3.083,
   "n": 12,
   "source": "extract_inter_arrival_times"
  },
  "intra_burst_iat": {
   "family": "empirical_quantiles",
   "params": {},
   "mean": 1.9737,
   "n": 25,
   "source": "extract_inter_arrival_times",
   "quantiles": [
    0.51015,
    0.532127,
    0.59641,
    0.655471,
    0.73077,
    0.890128,
    0.923098,
    0.931512,
    0.937978,
    1.024814,
    1.078298,
    1.130432,
    1.312155,
    1.40851,
    1.520662,
    1.73453,
    1.829138,
    2.550752,
    3.471896,
    3.548565,
    16.249838
   ],
   "quantile_probs": [
    0.0,
    0.05,
    0.1,
    0.15,
    0.2,
    0.25,
    0.3,
    0.35,
    0.4,
    0.45,
    0.5,
    0.55,
    0.6,
    0.65,
    0.7,
    0.75,
    0.8,
    0.85,
    0.9,
    0.95,
    1.0
   ]
  },
  "inter_burst_gap": {
   "family": "empirical_quantiles",
   "params": {},
   "mean": 418.8268,
   "n": 11,
   "source": "extract_inter_arrival_times",
   "quantiles": [
    33.296625,
    49.234199,
    65.171773,
    75.656213,
    86.140653,
    110.453448,
    134.766243,
    210.649177,
    286.532111,
    351.674994,
    416.817876,
    454.74979,
    492.681704,
    507.082923,
    521.484143,
    608.328046,
    695.17195,
    790.464149,
    885.756347,
    937.516099,
    989.275852
   ],
   "quantile_probs": [
    0.0,
    0.05,
    0.1,
    0.15,
    0.2,
    0.25,
    0.3,
    0.35,
    0.4,
    0.45,
    0.5,
    0.55,
    0.6,
    0.65,
    0.7,
    0.75,
    0.8,
    0.85,
    0.9,
    0.95,
    1.0
   ]
  }
 },
 "control_policies": {
  "queue_discipline": {
   "hbw": "priority"
  },
  "priority_order": {
   "hbw": [
    "/hbw/store_empty_bucket",
    "/hbw/unload"
   ]
  }
 },
 "initial_state": {
  "wip_at_start": 0
 }
}""")

RESOURCE_CAPACITIES = {r["name"]: int(r.get("capacity", 1)) for r in SPEC["resources"]}
SIMULATION_TIME = float(SPEC.get("window", {}).get("horizon_s", 3600.0))
ARRIVAL_RATE_SCALE = 1.0
FAILURES_ENABLED = True
MAX_ATTEMPTS = 20

COLUMNS = ["case_id", "variant", "activity", "resource", "case_arrival", "queue_enter",
           "time:timestamp", "operation_end_time", "lifecycle:state"]


def make_sampler(dist, rng):
    """Spec distribution -> zero-argument sampler (never negative)."""
    fam, p = dist["family"], dist.get("params", {})
    if fam == "constant":
        return lambda: float(p["value"])
    if fam == "categorical":
        v, pr = np.asarray(dist["values"], float), np.asarray(dist["probs"], float)
        return lambda: float(rng.choice(v, p=pr / pr.sum()))
    if fam == "empirical_quantiles":
        q, pr = np.asarray(dist["quantiles"], float), np.asarray(dist["quantile_probs"], float)
        return lambda: float(np.interp(rng.uniform(), pr, q))
    d = getattr(scipy.stats, fam)(**p)
    return lambda: max(0.0, float(d.rvs(random_state=rng)))


def run_single_replication(seed):
    random.seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    log = []

    cls_of = {r["name"]: r.get("resource_class", r["name"]) for r in SPEC["resources"]}
    cp = SPEC.get("control_policies", {}) or {}
    disc, prio = cp.get("queue_discipline", {}) or {}, cp.get("priority_order", {}) or {}
    res = {}
    for name, cap in RESOURCE_CAPACITIES.items():
        if disc.get(cls_of.get(name, name)) == "priority":
            res[name] = simpy.PriorityResource(env, capacity=int(cap))
        else:
            res[name] = simpy.Resource(env, capacity=int(cap))

    acts = {a["name"]: a for a in SPEC["activities"]}
    dur = {n: make_sampler(a["duration"], rng) for n, a in acts.items()}
    variants = SPEC["variants"]
    vprob = np.array([max(v.get("probability", 0.0), 0.0) for v in variants], float)
    vprob = vprob / vprob.sum() if vprob.sum() > 0 else np.full(len(variants), 1 / len(variants))

    def priority_of(resource, activity):
        order = prio.get(cls_of.get(resource, resource), [])
        return order.index(activity) if activity in order else len(order)

    def pick_resource(step, act):
        shares = {r: w for r, w in (step.get("resources") or {}).items() if r in res and w > 0}
        if shares:
            names = list(shares)
            w = np.array([shares[n] for n in names], float)
            return names[int(rng.choice(len(names), p=w / w.sum()))]
        elig = [r for r in act.get("eligible_resources", []) if r in res] or list(res)
        return min(elig, key=lambda r: (res[r].count + len(res[r].queue), rng.uniform()))

    def do_step(case, step):
        act = acts[step["activity"]]
        p_fail = float(act.get("failure_probability", 0.0)) if FAILURES_ENABLED else 0.0
        for _ in range(MAX_ATTEMPTS):
            r = pick_resource(step, act)
            q = env.now
            req = (res[r].request(priority=priority_of(r, act["name"]))
                   if isinstance(res[r], simpy.PriorityResource) else res[r].request())
            with req:
                yield req
                s = env.now
                yield env.timeout(dur[act["name"]]())
                e = env.now
            failed = rng.uniform() < p_fail
            log.append((case["id"], case["variant"], act["name"], r, case["arrival"], q, s, e,
                        "failure" if failed else "success"))
            if not failed:
                return True
            if act.get("on_failure", "retry") != "retry":
                return False
        return False

    def case_process(case, v, start_index=0):
        steps = v["steps"]
        exit_after = None
        if rng.uniform() < float(v.get("early_exit_probability", 0.0)):
            opts = v.get("early_exit_after_n_steps") or {}
            if opts:
                ks = list(opts)
                w = np.array([opts[k] for k in ks], float)
                exit_after = int(ks[int(rng.choice(len(ks), p=w / w.sum()))])
        background, done = [], 0
        for i in range(start_index, len(steps)):
            step = steps[i]
            if exit_after is not None and done >= exit_after:
                return
            if float(step.get("probability", 1.0)) < 1.0 and rng.uniform() > float(step["probability"]):
                continue
            if i == len(steps) - 1 and background:
                yield simpy.AllOf(env, background)
            nxt_concurrent = i + 1 < len(steps) and steps[i + 1].get("concurrent_with_previous", False)
            if nxt_concurrent:
                background.append(env.process(do_step(case, step)))
                ok = True
            else:
                ok = yield env.process(do_step(case, step))
            if not ok:
                return
            done += 1

    counter = [0]

    def release(v=None, start_index=0):
        if v is None:
            v = variants[int(rng.choice(len(variants), p=vprob))]
        counter[0] += 1
        case = {"id": f"case_{counter[0]}", "variant": v["name"], "arrival": env.now}
        env.process(case_process(case, v, start_index))

    arr = SPEC.get("arrivals", {}) or {}
    model = arr.get("model", "renewal")

    def arrivals():
        scale = float(ARRIVAL_RATE_SCALE)
        if model == "two_regime_bursts":
            size, intra, gap = (make_sampler(arr["burst_size"], rng), make_sampler(arr["intra_burst_iat"], rng),
                                make_sampler(arr["inter_burst_gap"], rng))
            while True:
                k = max(1, int(round(size())))
                for j in range(k):
                    release()
                    if j < k - 1:
                        yield env.timeout(intra() / scale)
                yield env.timeout(gap() / scale)
        else:
            iat = make_sampler(arr["interarrival"], rng)
            while True:
                release()
                yield env.timeout(iat() / scale)

    # initial work in progress (no observed case ids are used)
    for c in (SPEC.get("initial_state", {}) or {}).get("cases_in_progress", []):
        v = next((x for x in variants if x["name"] == c.get("variant")), None)
        if v is None:
            continue
        idx = next((i for i, s in enumerate(v["steps"]) if s["activity"] == c.get("current_activity")), 0)
        release(v, idx)

    env.process(arrivals())
    env.run(until=SIMULATION_TIME)
    return pd.DataFrame(log, columns=COLUMNS)


if __name__ == "__main__":
    df = run_single_replication(1)
    print(df.groupby("activity").size().to_string())
    print("cases:", df["case_id"].nunique(), "rows:", len(df))
