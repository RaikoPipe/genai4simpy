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
   "probability": 0.1111,
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
   "early_exit_probability": 0.0,
   "early_exit_after_n_steps": {},
   "early_exit_after": {}
  },
  {
   "name": "WF_102",
   "probability": 0.1111,
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
   "early_exit_probability": 0.0,
   "early_exit_after_n_steps": {},
   "early_exit_after": {}
  },
  {
   "name": "WF_103",
   "probability": 0.1111,
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
   "early_exit_probability": 0.0,
   "early_exit_after_n_steps": {},
   "early_exit_after": {}
  },
  {
   "name": "WF_104",
   "probability": 0.1111,
   "steps": [
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
   "early_exit_probability": 0.0,
   "early_exit_after_n_steps": {},
   "early_exit_after": {}
  },
  {
   "name": "WF_105",
   "probability": 0.1111,
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
   "early_exit_probability": 0.0,
   "early_exit_after_n_steps": {},
   "early_exit_after": {}
  },
  {
   "name": "WF_108",
   "probability": 0.1111,
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
   "early_exit_probability": 0.0,
   "early_exit_after_n_steps": {},
   "early_exit_after": {}
  },
  {
   "name": "WF_109",
   "probability": 0.1111,
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
   "early_exit_probability": 0.0,
   "early_exit_after_n_steps": {},
   "early_exit_after": {}
  },
  {
   "name": "WF_1106",
   "probability": 0.1111,
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
     "activity": "/ov/burn",
     "probability": 1.0,
     "resources": {
      "ov_2": 1.0
     },
     "concurrent_with_previous": false
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
     "activity": "/hbw/get_empty_bucket",
     "probability": 1.0,
     "resources": {
      "hbw_1": 1.0
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
     "activity": "/dm/cylindrical_drill",
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
   "early_exit_probability": 0.0,
   "early_exit_after_n_steps": {},
   "early_exit_after": {}
  },
  {
   "name": "WF_1107",
   "probability": 0.1111,
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
     "activity": "/mm/drill",
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
   "early_exit_probability": 0.0,
   "early_exit_after_n_steps": {},
   "early_exit_after": {}
  }
 ],
 "control_policies": {
  "queue_discipline": {
   "hbw": "priority",
   "vgr": "fifo",
   "mm": "fifo",
   "ov": "fifo",
   "wt": "fifo",
   "sm": "fifo",
   "pm": "fifo",
   "dm": "fifo",
   "hw": "fifo"
  },
  "priority_order": {
   "hbw": [
    "/hbw/store",
    "/hbw/store_empty_bucket",
    "/hbw/get_empty_bucket",
    "/hbw/unload"
   ]
  },
  "release_rule": "open (bursty releases)",
  "intra_case_concurrency": "/hbw/store_empty_bucket || /ov/burn; /hbw/store_empty_bucket || /vgr/pick_up_and_transport; /vgr/pick_up_and_transport || /hbw/get_empty_bucket",
  "evidence": {
   "hbw_fifo_agreement": 0.559,
   "hbw_activity_priority_agreement": 0.971,
   "vgr_fifo_agreement": 1.0,
   "hbw_best_rule": "activity_priority",
   "vgr_best_rule": "FIFO",
   "n_decision_points": 44,
   "overlapping_steps_per_completed_case": 1.667,
   "share_cases_with_overlap": 0.5,
   "share_steps_overlapping": 0.068,
   "overall_mean_wait_s": 79.1,
   "hbw_mean_wait_s": 289.0,
   "hbw_share_extraneous": 0.643,
   "vgr_share_contention": 0.456
  },
  "release_bursts": {
   "n_releases": 18,
   "max_wip": 12,
   "time_avg_wip": 7.09,
   "wip_at_release": {
    "mean": 5.5,
    "std": 2.995,
    "median": 5.5,
    "min": 0.0,
    "max": 11.0
   },
   "regime": "two_regime",
   "burst_iat_s": {
    "mean": 1.589,
    "std": 1.44,
    "median": 0.906,
    "min": 0.51,
    "max": 5.531,
    "n": 11
   },
   "gap_iat_s": {
    "mean": 377.458,
    "std": 280.866,
    "median": 299.39,
    "min": 93.406,
    "max": 799.957,
    "n": 6
   },
   "burst_size": {
    "mean": 2.571,
    "values": [
     8,
     1,
     1,
     2,
     2,
     3,
     1
    ],
    "n_bursts": 7
   },
   "completion_triggered": false
  }
 },
 "initial_state": {
  "wip_at_start": 0,
  "cases_in_progress": [],
  "exclusion_note": "Per authoritative context: the 4 incomplete cases are excluded from ROUTING inference only (they are cut before the canonical return tail); they are RETAINED for service-time and arrival-rate estimation. detect_censoring right-censored only 3 (WF_104_21, WF_108_18, WF_109_16); WF_1107_17 is added per the context's explicit list."
 },
 "assumptions": [
  "Canonical return tail: the end-of-process warehouse-return sequence (hbw_1/get_empty_bucket -> vgr_1/pick_up_and_transport -> hbw_1/store) is canonical for EVERY variant. Any absence in the log is time-window truncation, not optionality (authoritative context).",
  "No real early exits: discover_variant_routings flagged 'early_exit_probability' for 6 variants, but those are window truncation (cases cut before the return tail), not scrap/abandonment. early_exit_probability=0 for all variants (authoritative context).",
  "Routing inference excludes the 4 incomplete cases WF_104_21, WF_108_18, WF_109_16, WF_1107_17 (right-censored at window end); they are retained for service-time / arrival estimation (authoritative context).",
  "Retryable failures: the 8 failure events (7x HTTP 418 precondition, 1x HTTP 401 auth) are modelled as retryable - the operation retries and eventually succeeds; the workpiece continues (authoritative context).",
  "Role-based VGR assignment: vgr_2 performs the first transport of each case (hbw_2 -> first machine), vgr_1 performs all subsequent transports (authoritative context). Documented exceptions honored: WF_104 (cross-line, vgr_2 also used mid-route at step 7) and WF_108 (vgr_2 re-used at step 9).",
  "Cross-line routing: WF_104 is intentionally two-stage and is the ONLY variant allowed to route across lines (line-1 hbw_2/vgr_2 -> line-2 hbw_1/vgr_1 and back) (authoritative context).",
  "Stochastic sorting ejection: /sm/sort ejection position is modelled as uniform over {1,2,3} (authoritative context).",
  "Two-line physical layout (from transport start/end positions): Line 1 = hbw_2 (intake warehouse) -> vgr_2 -> machines (ov_1/ov_2, mm_1/mm_2, wt_1/wt_2, sm_1/sm_2, dm_2, pm_1); Line 2 = hbw_1 (return warehouse) -> vgr_1 -> hw_1 (human review) and the return path.",
  "HBW semantics: hbw_2 = intake warehouse (workpiece unload + empty-bucket store); hbw_1 = return warehouse (empty-bucket get + finished workpiece store). /hbw/store_empty_bucket and /hbw/unload are on hbw_2; /hbw/get_empty_bucket and /hbw/store are on hbw_1.",
  "Queue discipline: hbw uses activity priority (97.1% agreement vs 56% FIFO over 34 decision points) with order [store, store_empty_bucket, get_empty_bucket, unload]; vgr is FIFO (100% over 10 decision points); all other resource classes (mm, ov, wt, sm, pm, dm, hw) default to FIFO - no overtaking observed (contention share ~0).",
  "Release rule: open (no WIP cap, no completion trigger). Arrivals are bursty with a two-regime inter-arrival process (burst_iat ~1.6 s, gap_iat ~377 s, burst_size mean 2.57). Model the gap process and burst size separately, not the mixed mean IAT.",
  "Intra-case concurrency: bucket operations overlap with workpiece steps - /hbw/store_empty_bucket || /ov/burn (4 cases), /hbw/store_empty_bucket || /vgr/pick_up_and_transport (3), /vgr/pick_up_and_transport || /hbw/get_empty_bucket (2). The next step is requested before the previous releases its resource; model as concurrent SimPy processes.",
  "Per-step resource assignment is taken from the longest observed case per variant (resources_by_step). Machine assignment may vary between cases (e.g. mm_1 vs mm_2, ov_1 vs ov_2, sm_1 vs sm_2); the spec pins the dominant observed resource per step.",
  "Window: t0=2021-07-06T15:08:27.914751Z, horizon 3183.2 s (~53 min), 18 cases, 192 activity instances. terminal_activity=/hbw/store, first_activity=/hbw/unload.",
  "Initial WIP at window start = 0 (no cases in progress at t0).",
  "WF_104 starts with /vgr/pick_up_and_transport on vgr_2 (no /hbw/unload) - consistent with its cross-line two-stage design where the workpiece is picked up directly by vgr_2.",
  "WF_1106 does NOT use /hbw/store_empty_bucket (it uses /hbw/get_empty_bucket on hbw_1 mid-route at step 5) - a variant-specific bucket flow distinct from the other 8 variants.",
  "Failure-retry semantics: a failed instance (418/401) is followed by a re-request of the same activity that succeeds; the failed attempt's service time is not counted as a completed operation.",
  "Quantity is a per-variant deterministic parameter, observable only at feature-processing steps (drill/punch): WF_102=6 (/mm/drill), WF_103=6 (/pm/punch_recesses), WF_104=8 (/pm/punch_gill), WF_108=4 (/mm/drill), WF_109=6 (/pm/punch_ribbing), WF_1106=4 (/dm/cylindrical_drill). WF_1107 is step-dependent (6 at /mm/drill, 10 at /pm/punch_ribbing) - flagged, model per-step not per-variant. WF_101/WF_105 have no quantity parameter (no drill/punch step) - N/A, not 1.",
  "workpiece_size at /ov/burn is CATEGORICAL and deterministic per variant: WF_101=regular, WF_102=middle, WF_103=large, WF_104=maxi, WF_105=regular, WF_108=maxi, WF_109=regular, WF_1106=middle, WF_1107=large. burn_workpiece_thickness is also deterministic per variant: thin (WF_101/102/103/104/109), thick (WF_105/108/1106/1107).",
  "workpiece_size at drill steps is NUMERIC, extracted separately from the burn encoding (not merged): /mm/drill: WF_102=30, WF_108=30, WF_1107=40 (all deterministic); /dm/cylindrical_drill WF_1106 varies across cases (50 vs 60) - flagged, not deterministic, model as discrete {50,60}.",
  "No quality/rework/scrap data exist in the log; no scrap (early_exit_probability=0 for all variants, incomplete cases are window truncation); the only quality signal is the 8 retryable failures (7x HTTP 418, 1x HTTP 401) handled by the failure-rate extraction.",
  "Routing inconsistency flagged during quantity extraction: log contains an /ov/burn instance for WF_102_32 (size middle, thin) although the spec WF_102 route has no burn; WF_1106_21 has no /ov/burn instance although the spec WF_1106 route has burn at step 3 - burn presence varies across cases within WF_102/WF_1106, verify at modeling stage.",
  "Service-time duration rule: actual service time = operation_end_time - time:timestamp on the `start` row only. complete_service_time (includes queueing) is never used; planned_operation_time is reference only.",
  "Service-time sample: successful attempts only (n=184). The 8 failed attempts (7x HTTP 418, 1x HTTP 401) are excluded from service times; a failed attempt is not a completed operation. Failure rates are computed over all 192 attempts (failed in denominator).",
  "The 4 incomplete cases (WF_104_21, WF_108_18, WF_109_16, WF_1107_17) are RETAINED for service-time estimation per confirmed decision (window truncation, not abandonment).",
  "Grouping: per activity, pooling only across machine pairs performing the same activity (mm_1+mm_2, ov_1+ov_2, wt_1+wt_2, sm_1+sm_2); never across different activities. Single pooled transport distribution for vgr_1+vgr_2 (identical hardware) per confirmed decision - flagged for revisit at the modeling stage.",
  "/ov/burn duration is size-dependent: burn_workpiece_size (regular/middle/large/maxi, deterministic per variant) shows non-overlapping duration ranges - regular 21.4-26.6 s (n=5, mean 23.55), middle 26.9-31.8 s (n=2, mean 29.37), large 31.6-36.7 s (n=3, mean 33.30), maxi 36.9-41.8 s (n=3, mean 38.50). The spec carries the single pooled per-activity distribution (n=13, mean 30.14 s); per-category distributions are recommended for the modeling stage (flagged).",
  "Sparse/low-confidence groups (n <= 5): /pm/punch_gill (n=1, constant), /dm/cylindrical_drill (n=2), /dm/lower (n=2), /mm/transport_from_to (n=2), /pm/punch_recesses (n=2), /pm/punch_ribbing (n=2), /hbw/store (n=3), /mm/drill (n=4), /ov/temper (n=5), /mm/mill (n=6), /sm/sort (n=6). Estimates flagged low confidence; no cross-activity pooling used.",
  "Outliers kept (real variability, not removed): /sm/sort max 245.7 s (WF_108_17, ~10x the other 5 values of 8.4-14.0 s); /mm/mill max 14.437 s (mm_2 vs ~5.1 s on mm_1); /vgr max 88.375 s; /hw/human_review max 62.25 s (human-paced, CV=1.37). No data-defect removals were made.",
  "/mm/mill is dominated by mm_1 at ~5.0-5.3 s; the single mm_2 observation (14.437 s) inflates the pooled mean to 6.67 s - flagged for the modeling stage.",
  "VGR pooled transport: vgr_1 (n=32, mean 42.64 s, includes 5 failed-attempt retries and the 88.4 s max) vs vgr_2 (n=18, mean 40.76 s, tighter). Pooled mean 41.97 s; the single pooled distribution is used per confirmed decision.",
  "Per-resource check (activity x resource): machine pairs are poolable within each activity - /mm/deburr mm_1 14.49 s (n=8) vs mm_2 14.24 s (n=1); /wt wt_1 26.09 s (n=8) vs wt_2 29.09 s (n=6); /ov/burn ov_1 27.20 s (n=8) vs ov_2 34.85 s (n=5) is confounded with workpiece size (ov_2 handles the larger pieces), consistent with the size-dependence flag. Exception: /sm/transport sm_1 19.92 s (n=5) vs sm_2 14.53 s (n=4) differ by ~37% - pooled distribution (mean 17.52 s) is used per the confirmed pooling decision, but a per-resource split is recommended for the modeling stage."
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
     "c": 0.5,
     "loc": 13.875,
     "scale": 0.266
    },
    "mean": 14.008,
    "n": 2,
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
    ],
    "mean": 37.0619,
    "n": 11,
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
   "failure_probability": 0.0,
   "on_failure": "retry"
  },
  {
   "name": "/hbw/store_empty_bucket",
   "eligible_resources": [
    "hbw_2"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "quantiles": [
     32.641,
     33.7936,
     34.9214,
     35.9996,
     36.4718,
     36.641,
     36.7658,
     37.1636,
     38.1074,
     39.3156,
     40.656,
     40.7124,
     40.7844,
     40.8876,
     41.572,
     42.547,
     42.556,
     43.009,
     44.35,
     44.825,
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
    ],
    "mean": 39.4288,
    "n": 13,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.1333,
   "on_failure": "retry"
  },
  {
   "name": "/hbw/unload",
   "eligible_resources": [
    "hbw_2"
   ],
   "duration": {
    "family": "empirical_quantiles",
    "params": {},
    "quantiles": [
     32.735,
     32.8865,
     33.078,
     33.676,
     35.047,
     35.96125,
     36.3705,
     36.48125,
     36.5,
     37.88975,
     38.4265,
     38.51175,
     38.547,
     38.664,
     39.0705,
     40.69575,
     44.469,
     45.60525,
     47.6165,
     49.99875,
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
    ],
    "mean": 39.2919,
    "n": 16,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0588,
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
    ],
    "mean": 13.9959,
    "n": 14,
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
   "failure_probability": 0.0,
   "on_failure": "retry"
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
    "family": "empirical_quantiles",
    "params": {},
    "quantiles": [
     21.422,
     21.5528,
     21.6402,
     21.6408,
     23.5722,
     26.469,
     26.5254,
     26.6292,
     26.8278,
     28.7612,
     31.562,
     31.6268,
     31.7048,
     31.8092,
     33.7752,
     36.672,
     36.7842,
     36.8592,
     36.8598,
     38.8288,
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
    ],
    "mean": 30.1445,
    "n": 13,
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
     "c": 0.592357,
     "loc": 51.453,
     "scale": 0.157
    },
    "mean": 51.5374,
    "n": 5,
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
    "family": "constant",
    "params": {
     "value": 27.484
    },
    "mean": 27.484,
    "n": 1,
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
     "loc": 23.453,
     "scale": 0.375
    },
    "mean": 23.6405,
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
     "loc": 23.562,
     "scale": 7.657
    },
    "mean": 27.3905,
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
    "family": "empirical_quantiles",
    "params": {},
    "quantiles": [
     13.109,
     19.69005,
     24.3436,
     35.9146,
     36.4466,
     36.69925,
     37.1669,
     38.23905,
     40.6844,
     42.0459,
     42.7875,
     43.28035,
     43.5968,
     43.9038,
     44.2546,
     46.1175,
     48.8516,
     51.1126,
     53.1308,
     59.9139,
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
    ],
    "mean": 41.965,
    "n": 50,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0909,
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
    ],
    "mean": 27.3769,
    "n": 14,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "retry"
  }
 ],
 "arrivals": {
  "model": "two_regime_bursts",
  "burst_size": {
   "family": "categorical",
   "params": {},
   "values": [
    1.0,
    2.0,
    3.0
   ],
   "probs": [
    0.5,
    0.3333,
    0.1667
   ],
   "n": 6,
   "source": "control_policies.release_bursts.burst_size values [8,1,1,2,2,3,1] minus initial burst 8 -> 6 bursts [1,1,2,2,3,1]: P(1)=3/6, P(2)=2/6, P(3)=1/6, mean 1.667"
  },
  "intra_burst_iat": {
   "family": "lognorm",
   "params": {
    "s": 0.774,
    "loc": 0.0,
    "scale": 1.178
   },
   "mean": 1.589,
   "n": 11,
   "source": "control_policies.release_bursts.burst_iat_s (mean 1.589, std 1.44, n 11); lognormal fitted to mean+std: s=sqrt(ln(1+(1.44/1.589)^2))=0.774, scale=1.589/exp(s^2/2)=1.178. (A triangular was infeasible: min 0.51/max 5.531 with mean 1.589 implies mode -1.27 s.)"
  },
  "inter_burst_gap": {
   "family": "triang",
   "params": {
    "c": 0.2061,
    "loc": 93.406,
    "scale": 706.551
   },
   "mean": 377.458,
   "n": 6,
   "source": "control_policies.release_bursts.gap_iat_s (mean 377.458, min 93.406, max 799.957, n 6); mode m=3*mean-min-max=239.01, c=(m-min)/(max-min)=0.2061 so (min+max+mode)/3=377.458. Infinite two-regime process (no max_bursts): long-run rate = burst_mean/gap_mean = 1.667/377.458 = 1 release per 226 s, matching the observed 10 post-initial-burst releases over ~1960 s. The observed 7 bursts / 18 releases is a censored finite-window draw (last ~911 s release-free), not a cap; an infinite process is required for MR4 (cases scale with horizon)."
  },
  "initial_burst": {
   "family": "constant",
   "params": {
    "value": 8.0
   },
   "n": 1,
   "source": "extract_inter_arrival_times / control_policies.release_bursts.burst_size values[0]=8"
  }
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

    def gated(case, v, start_index):
        with wip_gate.request() as token:
            yield token
            case["arrival"] = env.now
            yield env.process(case_process(case, v, start_index))

    def release(v=None, start_index=0):
        if v is None:
            v = variants[int(rng.choice(len(variants), p=vprob))]
        counter[0] += 1
        case = {"id": f"case_{counter[0]}", "variant": v["name"], "arrival": env.now}
        env.process(gated(case, v, start_index) if wip_gate is not None else case_process(case, v, start_index))

    arr = SPEC.get("arrivals", {}) or {}
    model = arr.get("model", "renewal")

    wip_gate = (simpy.Resource(env, capacity=int(arr["wip_cap"]))
                if model == "wip_controlled" and arr.get("wip_cap") else None)

    def arrivals():
        scale = float(ARRIVAL_RATE_SCALE)
        if arr.get("initial_burst"):
            k0 = max(1, int(round(make_sampler(arr["initial_burst"], rng)())))
            gap0 = make_sampler(arr["intra_burst_iat"], rng) if arr.get("intra_burst_iat") else (lambda: 1.0)
            for j in range(k0):
                release()
                yield env.timeout(gap0() / scale)
        if model in ("two_regime_bursts", "batch"):
            size, gap = make_sampler(arr["burst_size"], rng), make_sampler(arr["inter_burst_gap"], rng)
            intra = make_sampler(arr["intra_burst_iat"], rng) if arr.get("intra_burst_iat") else (lambda: 0.0)
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
