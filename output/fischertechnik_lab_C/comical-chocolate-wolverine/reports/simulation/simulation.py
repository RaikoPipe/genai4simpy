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
   "probability": 0.1176,
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
   },
   "rework_branches": [
    {
     "name": "quality_rework",
     "trigger_activity": "/hw/human_review",
     "probability": 0.0588,
     "terminal": true,
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
     ]
    }
   ]
  },
  {
   "name": "WF_102",
   "probability": 0.1471,
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
   "early_exit_after": {},
   "rework_branches": [
    {
     "name": "quality_rework",
     "trigger_activity": "/hw/human_review",
     "probability": 0.0588,
     "terminal": true,
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
     ]
    }
   ]
  },
  {
   "name": "WF_103",
   "probability": 0.1471,
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
    "3": 1.0
   },
   "early_exit_after": {
    "/vgr/pick_up_and_transport": 1.0
   },
   "rework_branches": [
    {
     "name": "quality_rework",
     "trigger_activity": "/hw/human_review",
     "probability": 0.0588,
     "terminal": true,
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
     ]
    }
   ]
  },
  {
   "name": "WF_105",
   "probability": 0.1176,
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
   "early_exit_after": {},
   "rework_branches": [
    {
     "name": "quality_rework",
     "trigger_activity": "/hw/human_review",
     "probability": 0.0588,
     "terminal": true,
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
     ]
    }
   ]
  },
  {
   "name": "WF_108",
   "probability": 0.0882,
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
   "early_exit_after": {},
   "rework_branches": [
    {
     "name": "quality_rework",
     "trigger_activity": "/hw/human_review",
     "probability": 0.0588,
     "terminal": true,
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
     ]
    }
   ]
  },
  {
   "name": "WF_109",
   "probability": 0.0882,
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
   "early_exit_after": {},
   "rework_branches": [
    {
     "name": "quality_rework",
     "trigger_activity": "/hw/human_review",
     "probability": 0.0588,
     "terminal": true,
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
     ]
    }
   ]
  },
  {
   "name": "WF_1106",
   "probability": 0.1765,
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
     "probability": 0.6,
     "resources": {
      "dm_2": 1.0
     },
     "concurrent_with_previous": false
    },
    {
     "activity": "/dm/cylindrical_drill",
     "probability": 0.4,
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
   "early_exit_after": {},
   "rework_branches": [
    {
     "name": "quality_rework",
     "trigger_activity": "/hw/human_review",
     "probability": 0.0588,
     "terminal": true,
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
     ]
    }
   ]
  },
  {
   "name": "WF_1107",
   "probability": 0.1176,
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
    "3": 1.0
   },
   "early_exit_after": {
    "/vgr/pick_up_and_transport": 1.0
   },
   "rework_branches": [
    {
     "name": "quality_rework",
     "trigger_activity": "/hw/human_review",
     "probability": 0.0588,
     "terminal": true,
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
     ]
    }
   ]
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
  "release_rule": "open (bursty releases)",
  "intra_case_concurrency": "/hbw/store_empty_bucket || /ov/burn; /hbw/store_empty_bucket || /vgr/pick_up_and_transport",
  "evidence": {
   "hbw_fifo_agreement": 0.508,
   "vgr_fifo_agreement": 1.0,
   "hbw_best_rule": "case_age",
   "vgr_best_rule": "FIFO",
   "overlapping_steps_per_completed_case": null
  }
 },
 "initial_state": {
  "wip_at_start": 0,
  "cases_in_progress": []
 },
 "assumptions": [
  "Service times are measured on the 'start' lifecycle row only: duration = operation_end_time - time:timestamp (complete rows have logging drift; complete_service_time includes queueing and was not used).",
  "All 379 start rows are used for duration fits, including completed steps of the 19 missing-data stub cases and the 5 real scrap cases (confirmed decision).",
  "Grouping is per activity only (21 activities), pooling across track instances (ov_1/ov_2, mm_1/mm_2, wt_1/wt_2, sm_1/sm_2) and shared hbw_1/hbw_2, vgr_1/vgr_2 pools; no per-activity x resource splits (no resource-specific service-time behaviour in the topology).",
  "/hbw/unload: the 0.031 s outlier (WF_101_28) and the 0.047 s near-zero (WF_101_26) are the two scrap cases' failed unload attempts (transport/NFC errors) and are excluded from the duration fit; the 35 successful unloads are fitted (n=35).",
  "/ov/burn is fitted to observed values (mean 30.45 s, max 41.53 s, uniform(21.421, 41.532)); the planned 222 s is NOT used (digital twin of actual behaviour, confirmed decision).",
  "/hw/human_review: 2 zero-duration starts (WF_1106_16, WF_102_28) are kept as-is (instant hand-off events) and included in the empirical quantile table (n=17, min=0.000); the activity has high CV (1.285) and a long tail up to 185 s.",
  "Low-confidence estimates (small samples): /dm/cylindrical_drill (n=2), /pm/punch_recesses (n=2), /pm/punch_ribbing (n=2), /mm/transport_from_to (n=3), /dm/drill (n=4), /dm/lower (n=4), /pm/punch_gill (n=4), /mm/drill (n=8), /ov/temper (n=8). Triangular fallbacks (min/median/max) are used for n<10; empirical quantile tables for 10<=n<30; parametric fits only where the moment/tail gate and bootstrap KS passed (n>=30).",
  "Failure probabilities are transport/NFC errors, not quality defects: /hbw/unload p=2/37=0.0541 (WF_101_26, WF_101_28), /vgr/pick_up_and_transport p=3/104=0.0288 (WF_103_27, WF_104_17, WF_1107_13); all other activities p=0 (no observed failures).",
  "on_failure='scrap' for all activities (corrected from the 'retry' placeholder): in the log the 5 failed attempts (2x /hbw/unload, 3x /vgr/pick_up_and_transport) terminate the case (early exit / scrap) rather than retry \u2014 confirmed decision.",
  "The 5 real scrap cases (WF_101_26, WF_101_28, WF_103_27, WF_104_17, WF_1107_13) end in failure states; their completed steps are valid service observations and are included in the fits.",
  "Rework branch (structured field variants[].rework_branches; fixed probability, no fit \u2014 small-sample estimate): p_rework = 1/17 = 0.0588 of /hw/human_review completions enters the quality-rework loop (the WF_104 sequence: /vgr/pick_up_and_transport, /hbw/store_empty_bucket, /ov/burn, /wt/pick_up_and_transport, /mm/mill, /sm/sort, 3x /vgr/pick_up_and_transport, /hbw/store), terminated by /hbw/store; applies to every variant with a human-review step (all 8 arrival variants). WF_104 itself is removed from the arrival mix: its 0.0811 share in the log is internal rework flow, not an arrival stream (authorized fix #1).",
  "Arrivals: single global stream into hbw, two_regime_bursts model (12 bursts, mean size 3.08, range 1-9; intra-burst IAT mean 1.97 s, n=25; inter-burst gaps mean 418.8 s, n=11, scaled x1.42182 -> mean 595.5 s so the expected number of releases over the 5461.5 s window is 37, matching the observed 37 releases; initial burst constant 9). Long gaps are part of the arrival process and were not trimmed. Variant mix (renormalized over 34 non-WF_104 cases): WF_101 0.1176, WF_102 0.1471, WF_103 0.1471, WF_105 0.1176, WF_108 0.0882, WF_109 0.0882, WF_1106 0.1765, WF_1107 0.1176."
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
    47.3418,
    69.0022,
    92.6625,
    107.5695,
    122.4765,
    157.0449,
    191.6133,
    299.5052,
    407.3971,
    500.0185,
    592.6399,
    646.5723,
    700.5047,
    720.9806,
    741.4566,
    864.933,
    988.4094,
    1123.8977,
    1259.3861,
    1332.9791,
    1406.5722
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
   "mean": 595.496,
   "n": 11,
   "source": "extract_inter_arrival_times, recalibrated x1.42182 so expected releases over the 5461.5 s window = 37 (observed release count; authorized fix #2)"
  },
  "initial_burst": {
   "family": "constant",
   "params": {
    "value": 9.0
   },
   "source": "extract_inter_arrival_times"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
    "mean": 13.84,
    "n": 4,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
     "loc": 31.593,
     "scale": 21.134
    },
    "mean": 38.2486,
    "n": 35,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0541,
   "on_failure": "scrap"
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
     0.0,
     0.0,
     0.1968,
     0.5028,
     0.787,
     0.875,
     4.7398,
     5.826,
     8.8372,
     14.0902,
     17.515,
     25.203,
     31.7186,
     43.575,
     57.666,
     61.266,
     62.8404,
     93.6096,
     114.6036,
     129.5878,
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
    "mean": 41.3025,
    "n": 17,
    "source": "fit_activity_durations"
   },
   "failure_probability": 0.0,
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
   "on_failure": "scrap"
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
