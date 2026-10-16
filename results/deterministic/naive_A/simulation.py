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
  "t0": "2021-07-06T15:08:27.914751+00:00",
  "horizon_s": 3183.202249,
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
     "loc": 21.969,
     "scale": 4.046
    },
    "mean": 23.992,
    "n": 2,
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
     "c": 0.5,
     "loc": 13.875,
     "scale": 0.266
    },
    "mean": 14.008,
    "n": 2,
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
    "mean": 37.0619,
    "n": 11,
    "source": "fit_activity_durations",
    "quantiles": [
     30.797,
     31.1795,
     31.562,
     33.2655,
     34.969,
     35.3985,
     35.828,
     35.9115,
     35.995,
     36.107,
     36.219,
     36.3285,
     36.438,
     36.6095,
     36.781,
     36.8275,
     36.874,
     40.249,
     43.624,
     46.109,
     48.594
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
    "family": "triang",
    "params": {
     "c": 0.30222,
     "loc": 34.641,
     "scale": 7.703
    },
    "mean": 37.9847,
    "n": 3,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/hbw/store_empty_bucket",
   "eligible_resources": [
    "hbw_2"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 39.1677,
    "n": 12,
    "source": "fit_activity_durations",
    "quantiles": [
     32.641,
     33.69755,
     34.7417,
     35.73005,
     36.4154,
     36.5705,
     36.7034,
     36.8178,
     37.4782,
     38.34335,
     39.539,
     40.6607,
     40.7124,
     40.7758,
     40.8704,
     41.32825,
     42.222,
     43.3345,
     44.572,
     44.8285,
     44.867
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
   "failure_probability": 0.1333
  },
  {
   "name": "/hbw/unload",
   "eligible_resources": [
    "hbw_2"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 39.3485,
    "n": 14,
    "source": "fit_activity_durations",
    "quantiles": [
     32.735,
     32.8663,
     33.0216,
     33.2049,
     34.3158,
     35.35175,
     36.1441,
     36.38095,
     36.48,
     36.49625,
     37.5,
     38.50705,
     38.5376,
     38.6172,
     39.2796,
     43.0275,
     45.075,
     46.14725,
     48.2695,
     50.29865,
     52.248
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
   "failure_probability": 0.0588
  },
  {
   "name": "/hw/human_review",
   "eligible_resources": [
    "hw_1"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 13.9959,
    "n": 14,
    "source": "fit_activity_durations",
    "quantiles": [
     0.438,
     1.2297,
     1.6596,
     1.6674,
     1.7832,
     1.86775,
     1.8879,
     2.0538,
     2.4278,
     3.2104,
     3.75,
     5.0822,
     9.2994,
     11.75575,
     13.6515,
     16.76825,
     21.5766,
     28.02975,
     41.5335,
     52.8354,
     62.25
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
    "family": "triang",
    "params": {
     "c": 0.35964,
     "loc": 14.046,
     "scale": 1.001
    },
    "mean": 14.4631,
    "n": 9,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/mm/drill",
   "eligible_resources": [
    "mm_1",
    "mm_2"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.672512,
     "loc": 5.281,
     "scale": 15.625
    },
    "mean": 14.4412,
    "n": 4,
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
    "family": "triang",
    "params": {
     "c": 0.005911,
     "loc": 5.047,
     "scale": 9.39
    },
    "mean": 6.6722,
    "n": 6,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0
  },
  {
   "name": "/mm/transport_from_to",
   "eligible_resources": [
    "mm_2"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.5,
     "loc": 12.594,
     "scale": 0.547
    },
    "mean": 12.8675,
    "n": 2,
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
    "family": "empirical_quantiles",
    "params": {},
    "mean": 29.5849,
    "n": 12,
    "source": "fit_activity_durations",
    "quantiles": [
     21.422,
     21.5419,
     21.6401,
     21.64065,
     22.6066,
     25.262,
     26.4972,
     26.5489,
     26.6954,
     26.87745,
     29.228,
     31.5674,
     31.6268,
     31.6961,
     31.7918,
     33.051,
     35.7064,
     36.7378,
     36.8412,
     39.0749,
     41.782
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
   "name": "/ov/temper",
   "eligible_resources": [
    "ov_1"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.592357,
     "loc": 51.453,
     "scale": 0.157
    },
    "mean": 51.5374,
    "n": 5,
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
    "family": "constant",
    "params": {
     "value": 27.484
    },
    "mean": 27.484,
    "n": 1,
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
     "loc": 23.453,
     "scale": 0.375
    },
    "mean": 23.6405,
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
     "loc": 23.562,
     "scale": 7.657
    },
    "mean": 27.3905,
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
    "family": "triang",
    "params": {
     "c": 0.015929,
     "loc": 8.36,
     "scale": 237.34
    },
    "mean": 50.1455,
    "n": 6,
    "source": "fit_activity_durations"
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
    "family": "triang",
    "params": {
     "c": 0.537006,
     "loc": 14.39,
     "scale": 7.188
    },
    "mean": 17.5233,
    "n": 9,
    "source": "fit_activity_durations"
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
    "family": "empirical_quantiles",
    "params": {},
    "mean": 42.073,
    "n": 49,
    "source": "fit_activity_durations",
    "quantiles": [
     13.109,
     19.6846,
     24.1562,
     35.8372,
     36.4402,
     36.781,
     37.5154,
     39.0756,
     41.4502,
     42.2098,
     43.2,
     43.3508,
     43.6156,
     44.0,
     44.3062,
     46.391,
     49.2182,
     51.1312,
     53.5746,
     59.9558,
     88.375
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
   "failure_probability": 0.0909
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
    "mean": 27.3769,
    "n": 14,
    "source": "fit_activity_durations",
    "quantiles": [
     25.906,
     25.9268,
     25.9425,
     25.95225,
     25.9716,
     26.0155,
     26.0974,
     26.12705,
     26.1846,
     26.3263,
     26.362,
     26.7415,
     28.373,
     28.8822,
     28.9118,
     29.047,
     29.1406,
     29.20375,
     29.2135,
     29.22395,
     29.235
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
   "probability": 0.1333,
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
     }
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
   ]
  },
  {
   "name": "WF_102",
   "probability": 0.1333,
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
     "activity": "/hbw/store_empty_bucket",
     "resources": {
      "hbw_2": 1.0
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
   ]
  },
  {
   "name": "WF_103",
   "probability": 0.1333,
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
     }
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
    }
   ]
  },
  {
   "name": "WF_104",
   "probability": 0.0667,
   "steps": [
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
     }
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
     "activity": "/hbw/get_empty_bucket",
     "resources": {
      "hbw_1": 1.0
     }
    }
   ]
  },
  {
   "name": "WF_105",
   "probability": 0.1333,
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
     }
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
    }
   ]
  },
  {
   "name": "WF_108",
   "probability": 0.0667,
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
     }
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
    }
   ]
  },
  {
   "name": "WF_109",
   "probability": 0.0667,
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
     }
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
    }
   ]
  },
  {
   "name": "WF_1106",
   "probability": 0.1333,
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
     "activity": "/ov/burn",
     "resources": {
      "ov_2": 1.0
     }
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "resources": {
      "wt_2": 1.0
     }
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "resources": {
      "hbw_1": 1.0
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
     "activity": "/dm/cylindrical_drill",
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
   ]
  },
  {
   "name": "WF_1107",
   "probability": 0.1333,
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
     }
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
     "activity": "/mm/drill",
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
    }
   ]
  }
 ],
 "arrivals": {
  "model": "renewal",
  "interarrival": {
   "family": "empirical_quantiles",
   "params": {},
   "mean": 142.414,
   "n": 14,
   "source": "extract_inter_arrival_times",
   "quantiles": [
    0.509594,
    0.594758,
    0.65468,
    0.685154,
    0.762753,
    0.833751,
    0.887905,
    0.901553,
    1.021675,
    1.397933,
    1.570264,
    1.761249,
    2.218344,
    43.330223,
    97.976547,
    127.68396,
    210.615819,
    333.655821,
    538.810184,
    691.757747,
    799.956625
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
  "queue_discipline": {},
  "priority_order": {}
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
