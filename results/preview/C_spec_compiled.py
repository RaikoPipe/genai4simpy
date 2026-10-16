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
  "terminal_activity": "/hbw/store",
  "first_activity": "/hbw/unload"
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
 "variants": [
  {
   "name": "WF_101",
   "probability": 0.1081,
   "steps": [
    {
     "activity": "/hbw/unload",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/ov/temper",
     "probability": 1.0,
     "resources": {
      "ov_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "wt_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/mill",
     "probability": 1.0,
     "resources": {
      "mm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/deburr",
     "probability": 1.0,
     "resources": {
      "mm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/sort",
     "probability": 1.0,
     "resources": {
      "sm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hw/human_review",
     "probability": 1.0,
     "resources": {
      "hw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    }
   ],
   "early_exit_probability": 0.5,
   "early_exit_after_n_steps": {
    "0": 1.0
   },
   "early_exit_after": {
    "/hbw/unload": 1.0
   }
  },
  {
   "name": "WF_102",
   "probability": 0.1351,
   "steps": [
    {
     "activity": "/hbw/unload",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 0.6,
      "vgr_1": 0.4
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "wt_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/drill",
     "probability": 1.0,
     "resources": {
      "mm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/transport",
     "probability": 1.0,
     "resources": {
      "sm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/dm/lower",
     "probability": 1.0,
     "resources": {
      "dm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hw/human_review",
     "probability": 1.0,
     "resources": {
      "hw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    }
   ],
   "early_exit_probability": 0.6,
   "early_exit_after_n_steps": {
    "6": 0.333,
    "8": 0.333,
    "12": 0.333
   },
   "early_exit_after": {
    "/vgr/pick_up_and_transport": 0.667,
    "/mm/drill": 0.333
   }
  },
  {
   "name": "WF_103",
   "probability": 0.1351,
   "steps": [
    {
     "activity": "/hbw/unload",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/ov/temper",
     "probability": 1.0,
     "resources": {
      "ov_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "wt_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/mill",
     "probability": 1.0,
     "resources": {
      "mm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/deburr",
     "probability": 1.0,
     "resources": {
      "mm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/transport",
     "probability": 1.0,
     "resources": {
      "sm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/pm/punch_recesses",
     "probability": 1.0,
     "resources": {
      "pm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hw/human_review",
     "probability": 1.0,
     "resources": {
      "hw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    }
   ],
   "early_exit_probability": 0.6,
   "early_exit_after_n_steps": {
    "3": 0.333,
    "4": 0.333,
    "12": 0.333
   },
   "early_exit_after": {
    "/hw/human_review": 0.333,
    "/vgr/pick_up_and_transport": 0.667
   }
  },
  {
   "name": "WF_104",
   "probability": 0.0811,
   "steps": [
    {
     "activity": "/hbw/unload",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "wt_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/sort",
     "probability": 1.0,
     "resources": {
      "sm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 0.5,
      "vgr_2": 0.5
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "wt_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/deburr",
     "probability": 1.0,
     "resources": {
      "mm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/transport",
     "probability": 1.0,
     "resources": {
      "sm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/pm/punch_gill",
     "probability": 1.0,
     "resources": {
      "pm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hw/human_review",
     "probability": 1.0,
     "resources": {
      "hw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "wt_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/mill",
     "probability": 1.0,
     "resources": {
      "mm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/sort",
     "probability": 1.0,
     "resources": {
      "sm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    }
   ],
   "early_exit_probability": 1.0,
   "early_exit_after_n_steps": {
    "6": 0.333,
    "15": 0.333,
    "23": 0.333
   },
   "early_exit_after": {
    "/vgr/pick_up_and_transport": 0.667,
    "/sm/sort": 0.333
   }
  },
  {
   "name": "WF_105",
   "probability": 0.1081,
   "steps": [
    {
     "activity": "/hbw/unload",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "wt_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/deburr",
     "probability": 1.0,
     "resources": {
      "mm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/sort",
     "probability": 1.0,
     "resources": {
      "sm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hw/human_review",
     "probability": 1.0,
     "resources": {
      "hw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/hbw/store",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    }
   ],
   "early_exit_probability": 0.5,
   "early_exit_after_n_steps": {
    "8": 1.0
   },
   "early_exit_after": {
    "/sm/sort": 1.0
   }
  },
  {
   "name": "WF_108",
   "probability": 0.0811,
   "steps": [
    {
     "activity": "/hbw/unload",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "wt_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/drill",
     "probability": 1.0,
     "resources": {
      "mm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/deburr",
     "probability": 1.0,
     "resources": {
      "mm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/sort",
     "probability": 1.0,
     "resources": {
      "sm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hw/human_review",
     "probability": 1.0,
     "resources": {
      "hw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/hbw/store",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    }
   ],
   "early_exit_probability": 0.667,
   "early_exit_after_n_steps": {
    "7": 0.5,
    "9": 0.5
   },
   "early_exit_after": {
    "/vgr/pick_up_and_transport": 0.5,
    "/sm/sort": 0.5
   }
  },
  {
   "name": "WF_109",
   "probability": 0.0811,
   "steps": [
    {
     "activity": "/hbw/unload",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/ov/temper",
     "probability": 1.0,
     "resources": {
      "ov_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "wt_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/mill",
     "probability": 1.0,
     "resources": {
      "mm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/deburr",
     "probability": 1.0,
     "resources": {
      "mm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/transport",
     "probability": 1.0,
     "resources": {
      "sm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/pm/punch_ribbing",
     "probability": 1.0,
     "resources": {
      "pm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hw/human_review",
     "probability": 1.0,
     "resources": {
      "hw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    }
   ],
   "early_exit_probability": 0.333,
   "early_exit_after_n_steps": {
    "8": 1.0
   },
   "early_exit_after": {
    "/mm/deburr": 1.0
   }
  },
  {
   "name": "WF_1106",
   "probability": 0.1622,
   "steps": [
    {
     "activity": "/hbw/unload",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/wt/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "wt_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/transport_from_to",
     "probability": 1.0,
     "resources": {
      "mm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/transport",
     "probability": 1.0,
     "resources": {
      "sm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/dm/drill",
     "probability": 1.0,
     "resources": {
      "dm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hw/human_review",
     "probability": 1.0,
     "resources": {
      "hw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/hbw/store",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    }
   ],
   "early_exit_probability": 0.833,
   "early_exit_after_n_steps": {
    "7": 0.4,
    "8": 0.6
   },
   "early_exit_after": {
    "/dm/drill": 0.6,
    "/dm/cylindrical_drill": 0.4
   }
  },
  {
   "name": "WF_1107",
   "probability": 0.1081,
   "steps": [
    {
     "activity": "/hbw/unload",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/mm/transport_from_to",
     "probability": 1.0,
     "resources": {
      "mm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/sm/transport",
     "probability": 1.0,
     "resources": {
      "sm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/pm/punch_gill",
     "probability": 1.0,
     "resources": {
      "pm_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hw/human_review",
     "probability": 1.0,
     "resources": {
      "hw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/get_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": true
    },
    {
     "activity": "/vgr/pick_up_and_transport",
     "probability": 1.0,
     "resources": {
      "vgr_1": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/hbw/store",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
     },
     "concurrent_with_previous": false
    }
   ],
   "early_exit_probability": 0.75,
   "early_exit_after_n_steps": {
    "1": 0.333,
    "3": 0.333,
    "8": 0.333
   },
   "early_exit_after": {
    "/hbw/unload": 0.333,
    "/vgr/pick_up_and_transport": 0.333,
    "/pm/punch_gill": 0.333
   }
  }
 ],
 "control_policies": {
  "queue_discipline": {
   "hbw": "priority",
   "vgr": "fifo"
  },
  "priority_order": {
   "hbw": [
    "/hbw/store_empty_bucket",
    "/hbw/unload"
   ]
  },
  "release_rule": "exogenous batch release (operator-driven): single global arrival process into hbw with bursty batch structure (12 bursts, mean size 3.08, burst IAT mean 1.97 s, gap mean 418.8 s), then split by process-model proportions",
  "intra_case_concurrency": "/hbw/get_empty_bucket || /vgr/pick_up_and_transport; /hbw/store_empty_bucket || /ov/burn; /hbw/store_empty_bucket || /vgr/pick_up_and_transport; /vgr/pick_up_and_transport || /hbw/get_empty_bucket",
  "evidence": {
   "hbw_fifo_agreement": 0.508,
   "vgr_fifo_agreement": 1.0,
   "hbw_best_rule": "case_age",
   "vgr_best_rule": "FIFO",
   "overlapping_steps_per_completed_case": null
  },
  "handoff_delay": {
   "between": [
    "vgr",
    "hbw"
   ],
   "model": "explicit transfer/hand-off delay between vgr and hbw; NOT folded into vgr service time",
   "evidence": "50.5% of hbw waiting time is extraneous (resource idle while the case waited)"
  }
 },
 "initial_state": {
  "wip_at_start": 0,
  "cases_in_progress": []
 },
 "assumptions": [
  "Two parallel tracks (production lines) confirmed: Track 1 (shop floor 1) = ov_1, mm_1, wt_1, sm_1, pm_1, hw_1; Track 2 (shop floor 2) = ov_2, mm_2, wt_2, sm_2, dm_2. pm and hw are shop-floor-1 only (single-instance); dm is shop-floor-2 only (single-instance).",
  "hbw and vgr are shared at the exchange point (not track-specific). Evidence: hbw_1, hbw_2, vgr_1, vgr_2 are used by all variants (both track 1 and track 2). hbw_2 is the infeed bucket station, hbw_1 is the outfeed bucket station, vgr_2 is the infeed transporter, vgr_1 is the outfeed/general transporter.",
  "WF_104 rework loop is a real quality rework loop (failed human review \u2192 reprocessed). The spec models it as a linear sequence (the spec schema does not support conditional routing or loops). The 23-step sequence is the longest observed partial sequence (no complete cases for WF_104).",
  "WF_1106 variability is modeled as a single process model with conditional routing (different drill types: /dm/drill vs /dm/cylindrical_drill). The spec models it as a linear sequence (the spec schema does not support conditional routing). The main sequence uses /dm/drill; /dm/cylindrical_drill is an alternative.",
  "The release rule is open (bursty releases), not completion-triggered or WIP-capped. Evidence: 37 releases, max WIP 9, time-avg WIP 6.07, 12 bursts with mean size 3.08, gap mean 418.8s, burst IAT mean 1.97s.",
  "The queue discipline for hbw is priority (not FIFO), with priority order: /hbw/store_empty_bucket > /hbw/unload. Evidence: FIFO agreement 50.8%, case_age agreement 100%, activity_priority agreement 100%.",
  "The queue discipline for vgr is FIFO. Evidence: FIFO agreement 100% over 15 decision points.",
  "Intra-case concurrency is modeled for 4 pairs: /hbw/store_empty_bucket \u2192 /ov/burn (17 cases, mean overlap 35.5s), /hbw/store_empty_bucket \u2192 /vgr/pick_up_and_transport (13 cases, mean overlap 28.8s), /vgr/pick_up_and_transport \u2192 /hbw/get_empty_bucket (5 cases, mean overlap 17.2s), /hbw/get_empty_bucket \u2192 /vgr/pick_up_and_transport (4 cases, mean overlap 22.3s).",
  "Cases ending on a failure state are real scrap (early exits), not missing data. 5 such cases identified: WF_101_26, WF_101_28, WF_103_27, WF_104_17, WF_1107_13.",
  "Cases ending on a non-terminal activity with success state are real abandonment (early exits), except for 1-2 activity stubs which are missing data. WF_1107_15 (1-step stub) is missing data and should be excluded per user decision, but the tool included it as an early exit (impact is minor: 1 case out of 37).",
  "The 18 longer success-ending incomplete cases (4-12 steps) are real abandonment (early exits), not missing data. This is consistent with the tool's classification and the user's decision to only discard 1-2 activity stubs as missing data.",
  "Service times are extracted from start-row durations (operation_end_time - timestamp on lifecycle 'start'), pooled per activity across resources per the extraction plan. Per-resource breakdowns show real differences that track the per-resource planned times: /mm/mill mm_1 5.5 s vs mm_2 14.3 s (planned 5 vs 14), /wt wt_1 26.0 s vs wt_2 29.3 s (planned 22 vs 27), /sm/transport sm_1 23.6 s vs sm_2 14.7 s (planned 18 vs 15), /vgr vgr_1 34.2 s (CV 0.42) vs vgr_2 40.0 s (CV 0.10), /ov/burn ov_1 27.3 s vs ov_2 32.9 s. Pooled values are used as the plan directs; the distribution-fitting/calibration phase may split these if needed.",
  "/ov/burn service time uses the observed actual durations (n=32, mean 30.45 s, uniform 21.4-41.5 s), NOT the planned 222 s - the twin models actual behaviour.",
  "The vgr -> hbw hand-off delay is modelled as an explicit transfer delay (spec activity 'vgr_to_hbw_handoff_delay', empirical quantiles, mean 3.55 s, n=13) and is NOT folded into vgr service times. It was estimated from the 13 /hbw/store idle gaps (2.35-6.66 s, a consistent physical transfer). The 9 /hbw/get_empty_bucket idle gaps (5.5-122 s, mean 26.5 s) contain additional operator/bucket-availability waiting and are excluded from the base transfer delay.",
  "Small-sample activities (n < 5: /dm/cylindrical_drill, /dm/drill, /dm/lower, /pm/punch_gill, /pm/punch_recesses, /pm/punch_ribbing, /mm/transport_from_to) use the tool's triangular/constant fallback (min/median/max) with wide uncertainty; the distribution-fitting-agent will review these fits.",
  "Data-defect exclusions from service-time statistics: (1) the 0.031 s /hbw/unload instance WF_101_28 (confirmed NFC 418 failure, data error per plan); (2) the 0.047 s /hbw/unload instance WF_101_26 (same failure mode, also a failed attempt); (3) the two zero-duration /hw/human_review start rows (WF_1106_16, WF_102_28) where the recorded end timestamp equals the start timestamp (logging artifact; actual review took ~1-3 s per complete_service_time). Failed attempts are excluded from duration fits (include_failures=False) but count toward failure probabilities: /hbw/unload p=0.0541 (2/37), /vgr/pick_up_and_transport p=0.0288 (3/104).",
  "Five /hw/human_review instances have unreliable start-row end timestamps (recorded 0.0-0.875 s vs actual 1.3-2.8 s per complete_service_time); the empirical quantile table keeps the recorded values, so the lower tail of human_review may be slightly compressed. Median (27.1 s) and upper tail are reliable."
 ],
 "arrivals": {
  "model": "two_regime_bursts",
  "burst_size": {
   "family": "categorical",
   "params": {},
   "values": [
    1.0,
    2.0,
    3.0,
    5.0,
    9.0
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
   ],
   "mean": 1.9737,
   "n": 25,
   "source": "extract_inter_arrival_times"
  },
  "inter_burst_gap": {
   "family": "empirical_quantiles",
   "params": {},
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
   ],
   "mean": 418.8268,
   "n": 11,
   "source": "extract_inter_arrival_times"
  },
  "variant_split": {
   "method": "interleaved categorical draw per arriving case",
   "source": "spec.variants (process-model proportions, Phase 3)",
   "proportions": {
    "WF_101": 0.1081,
    "WF_102": 0.1351,
    "WF_103": 0.1351,
    "WF_104": 0.0811,
    "WF_105": 0.1081,
    "WF_108": 0.0811,
    "WF_109": 0.0811,
    "WF_1106": 0.1622,
    "WF_1107": 0.1081
   }
  }
 },
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
  },
  {
   "name": "/hbw/get_empty_bucket",
   "eligible_resources": [
    "hbw_1"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
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
    ],
    "mean": 38.3806,
    "n": 14,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "retry"
  },
  {
   "name": "/hbw/store",
   "eligible_resources": [
    "hbw_1"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
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
    ],
    "mean": 37.1995,
    "n": 13,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0541,
   "on_failure": "retry"
  },
  {
   "name": "/hw/human_review",
   "eligible_resources": [
    "hw_1"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
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
    ],
    "mean": 46.8095,
    "n": 15,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "retry"
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
    ],
    "mean": 17.0527,
    "n": 19,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
    ],
    "mean": 8.7129,
    "n": 11,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
    ],
    "mean": 11.7752,
    "n": 13,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "retry"
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
    ],
    "mean": 18.9202,
    "n": 19,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0288,
   "on_failure": "retry"
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
    ],
    "mean": 27.715,
    "n": 29,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "retry"
  },
  {
   "name": "vgr_to_hbw_handoff_delay",
   "eligible_resources": [
    "hbw_1"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "quantiles": [
     2.353,
     2.3998,
     2.5372,
     2.8558,
     3.0184,
     3.103,
     3.1312,
     3.1592,
     3.1868,
     3.2712,
     3.384,
     3.3846,
     3.4098,
     3.4842,
     3.509,
     3.509,
     3.5558,
     3.8434,
     4.6126,
     5.5837,
     6.6558
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
    ],
    "mean": 3.5457,
    "n": 13,
    "source": "run_python hand-off delay analysis (vgr completion -> hbw start where hbw_1 idle; /hbw/store population)"
   },
   "failure_probability": 0.0,
   "on_failure": "retry",
   "note": "Explicit transfer delay between vgr and hbw; NOT folded into vgr service time. Estimated from the 13 /hbw/store idle gaps (consistent physical transfer, 2.35-6.66 s). The 9 /hbw/get_empty_bucket idle gaps (5.5-122 s, mean 26.5 s) reflect additional operator/bucket-availability waiting and are excluded from this base transfer delay."
  }
 ]
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
