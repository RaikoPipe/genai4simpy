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
  "t0": "2021-06-30T15:24:34.013477+00:00",
  "horizon_s": 5943.712523,
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
     "c": 0.823938,
     "loc": 26.907,
     "scale": 5.907
    },
    "mean": 30.8172,
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
     "c": 0.613953,
     "loc": 13.814,
     "scale": 0.215
    },
    "mean": 13.9337,
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
    "mean": 39.4026,
    "n": 15,
    "source": "fit_activity_durations",
    "quantiles": [
     33.594,
     33.7466,
     34.9316,
     36.6342,
     36.7966,
     36.882,
     36.9432,
     37.0209,
     37.032,
     37.0974,
     37.25,
     37.3046,
     38.2716,
     39.7413,
     40.1214,
     40.2785,
     41.0644,
     43.6453,
     46.789,
     49.563,
     51.719
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
    "mean": 37.7296,
    "n": 14,
    "source": "fit_activity_durations",
    "quantiles": [
     33.768,
     34.08195,
     34.2879,
     34.36785,
     34.8906,
     35.68775,
     36.8649,
     37.05535,
     37.0632,
     37.06385,
     37.204,
     37.4892,
     38.1184,
     38.65625,
     39.0959,
     39.21875,
     40.0276,
     41.21225,
     41.7615,
     42.0899,
     42.229
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
    "hbw_1",
    "hbw_2"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 36.8164,
    "n": 35,
    "source": "fit_activity_durations",
    "quantiles": [
     9.298,
     32.1247,
     32.4444,
     32.9386,
     34.2028,
     34.375,
     36.0236,
     36.2452,
     36.558,
     36.7812,
     37.295,
     38.035,
     38.2732,
     39.7671,
     39.9218,
     40.257,
     40.5028,
     40.6824,
     41.4902,
     42.8309,
     44.344
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
   "failure_probability": 0.0541
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
     "loc": 32.530974,
     "scale": 22.094764
    },
    "mean": 39.8734,
    "n": 36,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0526
  },
  {
   "name": "/hw/human_review",
   "eligible_resources": [
    "hw_1"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "mean": 20.9192,
    "n": 24,
    "source": "fit_activity_durations",
    "quantiles": [
     0.109,
     0.6154,
     1.0511,
     1.20345,
     1.3348,
     1.50525,
     1.9272,
     2.1961,
     2.4732,
     2.8136,
     5.6335,
     10.3033,
     12.8574,
     13.44175,
     17.793,
     31.5565,
     34.6348,
     43.5887,
     72.9473,
     87.8392,
     98.143
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
    "mean": 14.3934,
    "n": 25,
    "source": "fit_activity_durations",
    "quantiles": [
     13.843,
     13.894,
     14.0304,
     14.0406,
     14.059,
     14.079,
     14.1444,
     14.218,
     14.218,
     14.2292,
     14.233,
     14.2332,
     14.2408,
     14.26,
     14.278,
     14.438,
     14.4418,
     14.4718,
     14.8192,
     15.8552,
     16.45
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
     "c": 0.978412,
     "loc": 5.281,
     "scale": 10.376
    },
    "mean": 11.1264,
    "n": 7,
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
    "mean": 7.6111,
    "n": 19,
    "source": "fit_activity_durations",
    "quantiles": [
     4.906,
     5.0599,
     5.0786,
     5.0797,
     5.0866,
     5.0915,
     5.0928,
     5.1033,
     5.125,
     5.1407,
     5.282,
     5.282,
     5.2828,
     5.3257,
     5.794,
     10.071,
     14.1164,
     14.228,
     14.296,
     14.5012,
     14.656
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
     "c": 0.041346,
     "loc": 11.751,
     "scale": 11.295
    },
    "mean": 15.6717,
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
    "family": "weibull_min",
    "params": {
     "c": 0.554599,
     "loc": 20.781,
     "scale": 9.52938
    },
    "mean": 34.1506,
    "n": 33,
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
    "family": "empirical_quantiles",
    "params": {},
    "mean": 52.6866,
    "n": 14,
    "source": "fit_activity_durations",
    "quantiles": [
     50.921,
     50.97235,
     51.0366,
     51.1159,
     51.5162,
     51.8185,
     51.9212,
     51.9535,
     52.0332,
     52.24835,
     52.4065,
     52.6626,
     53.3022,
     53.7105,
     53.9705,
     53.98025,
     54.0396,
     54.1238,
     54.1342,
     54.216,
     54.359
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
   "name": "/pm/punch_gill",
   "eligible_resources": [
    "pm_1"
   ],
   "duration": {
    "family": "triang",
    "params": {
     "c": 0.073406,
     "loc": 27.453,
     "scale": 0.831
    },
    "mean": 27.7503,
    "n": 3,
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
     "c": 0.482301,
     "loc": 23.157,
     "scale": 0.452
    },
    "mean": 23.347,
    "n": 5,
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
     "c": 0.04196,
     "loc": 22.828,
     "scale": 8.532
    },
    "mean": 24.7464,
    "n": 5,
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
    "mean": 14.1144,
    "n": 16,
    "source": "fit_activity_durations",
    "quantiles": [
     8.728,
     8.731,
     8.7335,
     9.04325,
     9.968,
     10.03925,
     10.219,
     10.475,
     10.775,
     10.7915,
     10.797,
     11.08225,
     11.938,
     12.1375,
     12.398,
     13.159,
     14.86,
     17.76625,
     18.938,
     26.2035,
     47.391
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
    "mean": 19.8682,
    "n": 21,
    "source": "fit_activity_durations",
    "quantiles": [
     14.093,
     14.25,
     14.254,
     14.437,
     14.453,
     14.656,
     14.687,
     14.829,
     18.078,
     18.327,
     18.906,
     19.156,
     19.406,
     19.735,
     20.656,
     20.813,
     21.0,
     23.259,
     25.957,
     31.812,
     44.468
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
    "family": "empirical_quantiles",
    "params": {},
    "mean": 37.9448,
    "n": 126,
    "source": "fit_activity_durations",
    "quantiles": [
     11.03,
     19.2185,
     19.4755,
     20.41825,
     21.391,
     32.04925,
     36.487,
     37.0955,
     38.139,
     41.56725,
     42.977,
     43.31725,
     43.69,
     44.223,
     44.7265,
     46.3715,
     48.064,
     48.38,
     49.992,
     51.3325,
     55.312
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
   "failure_probability": 0.0079
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
    "mean": 27.4511,
    "n": 37,
    "source": "fit_activity_durations",
    "quantiles": [
     25.917,
     25.9578,
     26.03,
     26.0304,
     26.0312,
     26.032,
     26.0336,
     26.0952,
     26.141,
     26.141,
     26.142,
     26.2506,
     27.8766,
     29.3494,
     29.422,
     29.423,
     29.4434,
     29.5302,
     29.5314,
     29.5488,
     29.852
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
   "failure_probability": 0.0976
  }
 ],
 "variants": [
  {
   "name": "WF_101",
   "probability": 0.1579,
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
   ]
  },
  {
   "name": "WF_102",
   "probability": 0.1316,
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
   "probability": 0.1316,
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
    }
   ]
  },
  {
   "name": "WF_104",
   "probability": 0.1316,
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
   "name": "WF_105",
   "probability": 0.1053,
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
   "name": "WF_108",
   "probability": 0.0789,
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
   ]
  },
  {
   "name": "WF_109",
   "probability": 0.1053,
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
    }
   ]
  },
  {
   "name": "WF_1106",
   "probability": 0.1053,
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
     "activity": "/mm/mill",
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
   ]
  },
  {
   "name": "WF_1107",
   "probability": 0.0526,
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
   ]
  }
 ],
 "arrivals": {
  "model": "renewal",
  "interarrival": {
   "family": "empirical_quantiles",
   "params": {},
   "mean": 140.2536,
   "n": 37,
   "source": "extract_inter_arrival_times",
   "quantiles": [
    0.562544,
    0.644757,
    0.683387,
    0.724829,
    0.903578,
    1.112139,
    1.35954,
    1.631031,
    2.038308,
    2.774059,
    3.188357,
    5.154442,
    6.359811,
    18.830668,
    87.482551,
    193.353492,
    231.265165,
    297.247312,
    445.197189,
    591.516175,
    1336.648804
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
