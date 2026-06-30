"""
SimPy simulation of the Fischertechnik Lab C manufacturing system.
Based on extraction reports from eventlog_cleaned.parquet.
"""

import random
import numpy as np
import pandas as pd
import simpy
from scipy import stats


# =============================================================================
# Constants
# =============================================================================

RESOURCE_CAPACITIES = {
    'ov_1': 1, 'ov_2': 1, 'mm_1': 1, 'mm_2': 1,
    'wt_1': 1, 'wt_2': 1, 'sm_1': 1, 'sm_2': 1,
    'pm_1': 1, 'hw_1': 1, 'dm_2': 1,
    'hbw_1': 1, 'hbw_2': 1, 'vgr_1': 1, 'vgr_2': 1,
}

SIMULATION_TIME = 5461  # seconds (matching observation window)

# Process model mix (categorical distribution)
PROCESS_MODELS = [
    'WF_101', 'WF_102', 'WF_103', 'WF_104', 'WF_105',
    'WF_108', 'WF_109', 'WF_1106', 'WF_1107',
]
MODEL_WEIGHTS = [
    0.1081, 0.1351, 0.1351, 0.0811, 0.1081,
    0.0811, 0.0811, 0.1622, 0.1081,
]

# Human review probabilities per process model
HUMAN_REVIEW_PROBS = {
    'WF_101': 0.50, 'WF_102': 0.60, 'WF_103': 0.60, 'WF_104': 0.67,
    'WF_105': 0.50, 'WF_108': 0.33, 'WF_109': 0.67,
    'WF_1106': 0.17, 'WF_1107': 0.25,
}

# Failure rates per activity
FAILURE_RATES = {
    '/hbw/unload': 0.054,
    '/vgr/pick_up_and_transport': 0.029,
}

# Burst sizes (empirical from data: 11 bursts, 37 cases)
BURST_SIZES = [1, 1, 1, 2, 2, 2, 3, 5, 5, 6, 9]

# Constant processing times (empirical means for N < 30)
CONSTANT_TIMES = {
    ('/hbw/get_empty_bucket', 'hbw_1'): 38.38,
    ('/hbw/store', 'hbw_1'): 37.20,
    ('/ov/burn', 'ov_1'): 27.29,
    ('/ov/temper', 'ov_1'): 51.55,
    ('/ov/burn', 'ov_2'): 32.92,
    ('/mm/mill', 'mm_1'): 5.52,
    ('/mm/deburr', 'mm_1'): 14.35,
    ('/mm/transport_from_to', 'mm_1'): 12.39,
    ('/mm/mill', 'mm_2'): 14.30,
    ('/mm/deburr', 'mm_2'): 14.19,
    ('/mm/drill', 'mm_2'): 11.07,
    ('/mm/transport_from_to', 'mm_2'): 12.33,
    ('/sm/sort', 'sm_1'): 12.52,
    ('/sm/transport', 'sm_1'): 19.29,
    ('/sm/sort', 'sm_2'): 9.45,
    ('/sm/transport', 'sm_2'): 14.69,
    ('/wt/pick_up_and_transport', 'wt_1'): 26.00,
    ('/wt/pick_up_and_transport', 'wt_2'): 29.32,
    ('/pm/punch_gill', 'pm_1'): 27.46,
    ('/pm/punch_recesses', 'pm_1'): 23.75,
    ('/pm/punch_ribbing', 'pm_1'): 23.57,
    ('/dm/cylindrical_drill', 'dm_2'): 42.95,
    ('/dm/drill', 'dm_2'): 27.13,
    ('/dm/lower', 'dm_2'): 13.84,
}


# =============================================================================
# Sampling functions
# =============================================================================

def sample_duration(activity, resource):
    """Sample processing duration for an activity-resource pair."""
    key = (activity, resource)

    if key == ('/hbw/unload', 'hbw_2'):
        # Triangular: a=31.59, mode=36.05, b=51.20
        c_param = (36.05 - 31.59) / (51.20 - 31.59)  # ~0.2274
        return stats.triang.rvs(c_param, loc=31.59, scale=19.61)

    elif key == ('/hbw/store_empty_bucket', 'hbw_2'):
        # Uniform[31.73, 44.03]
        return np.random.uniform(31.73, 44.03)

    elif key == ('/hw/human_review', 'hw_1'):
        # Exponential with mean 46.83
        return max(1.0, np.random.exponential(46.83))

    elif key == ('/vgr/pick_up_and_transport', 'vgr_1'):
        # Normal(mean=34.47, std=14.24), floor at 1s
        return max(1.0, np.random.normal(34.47, 14.24))

    elif key == ('/vgr/pick_up_and_transport', 'vgr_2'):
        # Normal(mean=39.96, std=4.18), floor at 1s
        return max(1.0, np.random.normal(39.96, 4.18))

    else:
        # Constant (empirical mean for N < 30)
        return CONSTANT_TIMES.get(key, 30.0)


def check_failure(activity):
    """Check if an activity fails based on failure rates."""
    rate = FAILURE_RATES.get(activity, 0.0)
    return random.random() < rate


# =============================================================================
# Activity execution helper
# =============================================================================

def do_activity(env, res, case_id, variant, activity, resource_name, log):
    """Execute an activity on a resource.

    Yields SimPy events for resource request and processing timeout.
    Appends one row to the event log.
    Returns True if successful, False if failed.
    """
    duration = sample_duration(activity, resource_name)

    with res.request() as req:
        yield req
        t_start = env.now
        yield env.timeout(duration)
        t_end = env.now

        failed = check_failure(activity)

        log.append({
            'case_id': case_id,
            'variant': variant,
            'activity': activity,
            'resource': resource_name,
            'time:timestamp': t_start,
            'operation_end_time': t_end,
            'lifecycle:state': 'failure' if failed else 'success',
            'response_status_code': 418 if failed else 200,
        })

    return not failed


# =============================================================================
# Shared routing helpers
# =============================================================================

def _entry_phase(env, case_id, variant, R, log):
    """Common entry: hbw_2(unload) -> vgr_2(transport) -> hbw_2(store_empty_bucket)."""
    if not (yield from do_activity(env, R['hbw_2'], case_id, variant,
                                   '/hbw/unload', 'hbw_2', log)):
        return False
    if not (yield from do_activity(env, R['vgr_2'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_2', log)):
        return False
    if not (yield from do_activity(env, R['hbw_2'], case_id, variant,
                                   '/hbw/store_empty_bucket', 'hbw_2', log)):
        return False
    return True


def _storage_phase(env, case_id, variant, R, log):
    """Common storage: hbw_1(get_empty_bucket) -> vgr_1 x2 -> hbw_1(store)."""
    if not (yield from do_activity(env, R['hbw_1'], case_id, variant,
                                   '/hbw/get_empty_bucket', 'hbw_1', log)):
        return False
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return False
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return False
    if not (yield from do_activity(env, R['hbw_1'], case_id, variant,
                                   '/hbw/store', 'hbw_1', log)):
        return False
    return True


def _human_review_and_store(env, case_id, variant, R, log, cross_track_vgr=None):
    """Conditional human review followed by storage.
    If cross_track_vgr is set, use it before vgr_1 for review transport."""
    if cross_track_vgr and cross_track_vgr in R:
        if not (yield from do_activity(env, R[cross_track_vgr], case_id, variant,
                                       '/vgr/pick_up_and_transport', cross_track_vgr, log)):
            return False
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return False
    if not (yield from do_activity(env, R['hw_1'], case_id, variant,
                                   '/hw/human_review', 'hw_1', log)):
        return False
    if not (yield from _storage_phase(env, case_id, variant, R, log)):
        return False
    return True


# =============================================================================
# Process model routing functions
# =============================================================================

def process_wf_101(env, case_id, R, log):
    """WF_101: Track 1, burn+temper -> mill+deburr -> sort -> [human_review] -> [store]"""
    variant = 'WF_101'

    if not (yield from _entry_phase(env, case_id, variant, R, log)):
        return

    # Cross to Track 1
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return

    # Track 1 processing
    if not (yield from do_activity(env, R['ov_1'], case_id, variant,
                                   '/ov/burn', 'ov_1', log)):
        return
    if not (yield from do_activity(env, R['ov_1'], case_id, variant,
                                   '/ov/temper', 'ov_1', log)):
        return
    if not (yield from do_activity(env, R['wt_1'], case_id, variant,
                                   '/wt/pick_up_and_transport', 'wt_1', log)):
        return
    if not (yield from do_activity(env, R['mm_1'], case_id, variant,
                                   '/mm/mill', 'mm_1', log)):
        return
    if not (yield from do_activity(env, R['mm_1'], case_id, variant,
                                   '/mm/deburr', 'mm_1', log)):
        return

    # Sort
    if not (yield from do_activity(env, R['sm_1'], case_id, variant,
                                   '/sm/sort', 'sm_1', log)):
        return

    # Conditional human review + storage (50%)
    if random.random() < HUMAN_REVIEW_PROBS[variant]:
        if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                       '/vgr/pick_up_and_transport', 'vgr_1', log)):
            return
        if not (yield from do_activity(env, R['hw_1'], case_id, variant,
                                       '/hw/human_review', 'hw_1', log)):
            return
        if not (yield from _storage_phase(env, case_id, variant, R, log)):
            return


def process_wf_102(env, case_id, R, log):
    """WF_102: Track 2, burn -> drill -> transport -> lower -> [human_review] -> [store]"""
    variant = 'WF_102'

    # Entry (optional vgr_2 transport between unload and store_empty_bucket)
    if not (yield from do_activity(env, R['hbw_2'], case_id, variant,
                                   '/hbw/unload', 'hbw_2', log)):
        return
    if random.random() < 0.5:
        if not (yield from do_activity(env, R['vgr_2'], case_id, variant,
                                       '/vgr/pick_up_and_transport', 'vgr_2', log)):
            return
    if not (yield from do_activity(env, R['hbw_2'], case_id, variant,
                                   '/hbw/store_empty_bucket', 'hbw_2', log)):
        return

    # Track 2 processing
    if not (yield from do_activity(env, R['ov_2'], case_id, variant,
                                   '/ov/burn', 'ov_2', log)):
        return
    if not (yield from do_activity(env, R['wt_2'], case_id, variant,
                                   '/wt/pick_up_and_transport', 'wt_2', log)):
        return
    if not (yield from do_activity(env, R['mm_2'], case_id, variant,
                                   '/mm/drill', 'mm_2', log)):
        return
    if not (yield from do_activity(env, R['sm_2'], case_id, variant,
                                   '/sm/transport', 'sm_2', log)):
        return
    if not (yield from do_activity(env, R['dm_2'], case_id, variant,
                                   '/dm/lower', 'dm_2', log)):
        return

    # Conditional human review + storage (60%)
    if random.random() < HUMAN_REVIEW_PROBS[variant]:
        if not (yield from _human_review_and_store(env, case_id, variant, R, log)):
            return


def process_wf_103(env, case_id, R, log):
    """WF_103: Track 1, burn+temper -> mill+deburr -> transport -> punch_recesses -> [review] -> [store]"""
    variant = 'WF_103'

    if not (yield from _entry_phase(env, case_id, variant, R, log)):
        return

    # Cross to Track 1
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return

    # Track 1 processing
    if not (yield from do_activity(env, R['ov_1'], case_id, variant,
                                   '/ov/burn', 'ov_1', log)):
        return
    if not (yield from do_activity(env, R['ov_1'], case_id, variant,
                                   '/ov/temper', 'ov_1', log)):
        return
    # Optional wt_1 transport
    if random.random() < 0.5:
        if not (yield from do_activity(env, R['wt_1'], case_id, variant,
                                       '/wt/pick_up_and_transport', 'wt_1', log)):
            return
    if not (yield from do_activity(env, R['mm_1'], case_id, variant,
                                   '/mm/mill', 'mm_1', log)):
        return
    if not (yield from do_activity(env, R['mm_1'], case_id, variant,
                                   '/mm/deburr', 'mm_1', log)):
        return

    # Transport to punch
    if not (yield from do_activity(env, R['sm_1'], case_id, variant,
                                   '/sm/transport', 'sm_1', log)):
        return
    if not (yield from do_activity(env, R['pm_1'], case_id, variant,
                                   '/pm/punch_recesses', 'pm_1', log)):
        return

    # Conditional human review + storage (60%)
    if random.random() < HUMAN_REVIEW_PROBS[variant]:
        if not (yield from _human_review_and_store(env, case_id, variant, R, log)):
            return


def process_wf_104(env, case_id, R, log):
    """WF_104: Cross-track with deterministic rework loop (always 1 cycle)."""
    variant = 'WF_104'

    # Entry
    if not (yield from _entry_phase(env, case_id, variant, R, log)):
        return

    # ---- Phase 1 (Track 2) ----
    if not (yield from do_activity(env, R['ov_2'], case_id, variant,
                                   '/ov/burn', 'ov_2', log)):
        return
    if not (yield from do_activity(env, R['wt_2'], case_id, variant,
                                   '/wt/pick_up_and_transport', 'wt_2', log)):
        return
    # Optional mm_2(mill) in Phase 1
    if random.random() < 0.5:
        if not (yield from do_activity(env, R['mm_2'], case_id, variant,
                                       '/mm/mill', 'mm_2', log)):
            return
    if not (yield from do_activity(env, R['sm_2'], case_id, variant,
                                   '/sm/sort', 'sm_2', log)):
        return
    # Cross-track transport
    if not (yield from do_activity(env, R['vgr_2'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_2', log)):
        return
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return

    # ---- Phase 2 (Track 1) ----
    if not (yield from do_activity(env, R['wt_1'], case_id, variant,
                                   '/wt/pick_up_and_transport', 'wt_1', log)):
        return
    if not (yield from do_activity(env, R['mm_1'], case_id, variant,
                                   '/mm/deburr', 'mm_1', log)):
        return
    if not (yield from do_activity(env, R['sm_1'], case_id, variant,
                                   '/sm/transport', 'sm_1', log)):
        return
    if not (yield from do_activity(env, R['pm_1'], case_id, variant,
                                   '/pm/punch_gill', 'pm_1', log)):
        return
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return
    if not (yield from do_activity(env, R['hw_1'], case_id, variant,
                                   '/hw/human_review', 'hw_1', log)):
        return

    # ---- Rework Loop (deterministic, 1 cycle) ----
    if not (yield from do_activity(env, R['vgr_2'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_2', log)):
        return
    if not (yield from do_activity(env, R['hbw_2'], case_id, variant,
                                   '/hbw/store_empty_bucket', 'hbw_2', log)):
        return
    if not (yield from do_activity(env, R['ov_2'], case_id, variant,
                                   '/ov/burn', 'ov_2', log)):
        return
    if not (yield from do_activity(env, R['wt_2'], case_id, variant,
                                   '/wt/pick_up_and_transport', 'wt_2', log)):
        return
    if not (yield from do_activity(env, R['mm_2'], case_id, variant,
                                   '/mm/mill', 'mm_2', log)):
        return
    if not (yield from do_activity(env, R['sm_2'], case_id, variant,
                                   '/sm/sort', 'sm_2', log)):
        return
    if not (yield from do_activity(env, R['vgr_2'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_2', log)):
        return
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return

    # ---- Phase 2 again ----
    if not (yield from do_activity(env, R['wt_1'], case_id, variant,
                                   '/wt/pick_up_and_transport', 'wt_1', log)):
        return
    if not (yield from do_activity(env, R['mm_1'], case_id, variant,
                                   '/mm/deburr', 'mm_1', log)):
        return
    if not (yield from do_activity(env, R['sm_1'], case_id, variant,
                                   '/sm/transport', 'sm_1', log)):
        return
    if not (yield from do_activity(env, R['pm_1'], case_id, variant,
                                   '/pm/punch_gill', 'pm_1', log)):
        return
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return
    if not (yield from do_activity(env, R['hw_1'], case_id, variant,
                                   '/hw/human_review', 'hw_1', log)):
        return


def process_wf_105(env, case_id, R, log):
    """WF_105: Track 1, burn -> deburr -> sort -> [human_review] -> [store]"""
    variant = 'WF_105'

    if not (yield from _entry_phase(env, case_id, variant, R, log)):
        return

    # Cross to Track 1
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return

    # Track 1 processing
    if not (yield from do_activity(env, R['ov_1'], case_id, variant,
                                   '/ov/burn', 'ov_1', log)):
        return
    if not (yield from do_activity(env, R['wt_1'], case_id, variant,
                                   '/wt/pick_up_and_transport', 'wt_1', log)):
        return
    if not (yield from do_activity(env, R['mm_1'], case_id, variant,
                                   '/mm/deburr', 'mm_1', log)):
        return
    if not (yield from do_activity(env, R['sm_1'], case_id, variant,
                                   '/sm/sort', 'sm_1', log)):
        return

    # Conditional human review + storage (50%)
    if random.random() < HUMAN_REVIEW_PROBS[variant]:
        if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                       '/vgr/pick_up_and_transport', 'vgr_1', log)):
            return
        if not (yield from do_activity(env, R['hw_1'], case_id, variant,
                                       '/hw/human_review', 'hw_1', log)):
            return
        if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                       '/vgr/pick_up_and_transport', 'vgr_1', log)):
            return
        if not (yield from do_activity(env, R['hbw_1'], case_id, variant,
                                       '/hbw/get_empty_bucket', 'hbw_1', log)):
            return
        if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                       '/vgr/pick_up_and_transport', 'vgr_1', log)):
            return
        if not (yield from do_activity(env, R['hbw_1'], case_id, variant,
                                       '/hbw/store', 'hbw_1', log)):
            return


def process_wf_108(env, case_id, R, log):
    """WF_108: Track 2, burn -> drill+deburr -> sort -> [human_review] -> [store]"""
    variant = 'WF_108'

    # Entry (optional vgr_2 transport)
    if not (yield from do_activity(env, R['hbw_2'], case_id, variant,
                                   '/hbw/unload', 'hbw_2', log)):
        return
    if random.random() < 0.5:
        if not (yield from do_activity(env, R['vgr_2'], case_id, variant,
                                       '/vgr/pick_up_and_transport', 'vgr_2', log)):
            return
    if not (yield from do_activity(env, R['hbw_2'], case_id, variant,
                                   '/hbw/store_empty_bucket', 'hbw_2', log)):
        return

    # Track 2 processing
    if not (yield from do_activity(env, R['ov_2'], case_id, variant,
                                   '/ov/burn', 'ov_2', log)):
        return
    if not (yield from do_activity(env, R['wt_2'], case_id, variant,
                                   '/wt/pick_up_and_transport', 'wt_2', log)):
        return
    if not (yield from do_activity(env, R['mm_2'], case_id, variant,
                                   '/mm/drill', 'mm_2', log)):
        return
    if not (yield from do_activity(env, R['mm_2'], case_id, variant,
                                   '/mm/deburr', 'mm_2', log)):
        return
    if not (yield from do_activity(env, R['sm_2'], case_id, variant,
                                   '/sm/sort', 'sm_2', log)):
        return

    # Conditional human review + storage (33%)
    if random.random() < HUMAN_REVIEW_PROBS[variant]:
        if not (yield from do_activity(env, R['vgr_2'], case_id, variant,
                                       '/vgr/pick_up_and_transport', 'vgr_2', log)):
            return
        if not (yield from _human_review_and_store(env, case_id, variant, R, log)):
            return


def process_wf_109(env, case_id, R, log):
    """WF_109: Track 1, burn+temper -> mill+deburr -> transport -> punch_ribbing -> [review] -> [store]"""
    variant = 'WF_109'

    if not (yield from _entry_phase(env, case_id, variant, R, log)):
        return

    # Cross to Track 1
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return

    # Track 1 processing
    if not (yield from do_activity(env, R['ov_1'], case_id, variant,
                                   '/ov/burn', 'ov_1', log)):
        return
    if not (yield from do_activity(env, R['ov_1'], case_id, variant,
                                   '/ov/temper', 'ov_1', log)):
        return
    if not (yield from do_activity(env, R['wt_1'], case_id, variant,
                                   '/wt/pick_up_and_transport', 'wt_1', log)):
        return
    if not (yield from do_activity(env, R['mm_1'], case_id, variant,
                                   '/mm/mill', 'mm_1', log)):
        return
    if not (yield from do_activity(env, R['mm_1'], case_id, variant,
                                   '/mm/deburr', 'mm_1', log)):
        return

    # Transport to punch
    if not (yield from do_activity(env, R['sm_1'], case_id, variant,
                                   '/sm/transport', 'sm_1', log)):
        return
    if not (yield from do_activity(env, R['pm_1'], case_id, variant,
                                   '/pm/punch_ribbing', 'pm_1', log)):
        return

    # Conditional human review + storage (67%)
    if random.random() < HUMAN_REVIEW_PROBS[variant]:
        if not (yield from _human_review_and_store(env, case_id, variant, R, log)):
            return


def process_wf_1106(env, case_id, R, log):
    """WF_1106: Track 2, burn -> variable mm_2 -> transport -> variable dm_2 -> [review] -> [store]"""
    variant = 'WF_1106'

    if not (yield from _entry_phase(env, case_id, variant, R, log)):
        return

    # Track 2 processing
    if not (yield from do_activity(env, R['ov_2'], case_id, variant,
                                   '/ov/burn', 'ov_2', log)):
        return

    # Optional wt_2 transport
    if random.random() < 0.5:
        if not (yield from do_activity(env, R['wt_2'], case_id, variant,
                                       '/wt/pick_up_and_transport', 'wt_2', log)):
            return

    # Variable mm_2 activity (deburr, drill, mill, transport_from_to)
    mm_activity = random.choice(['/mm/deburr', '/mm/drill', '/mm/mill',
                                 '/mm/transport_from_to'])
    if not (yield from do_activity(env, R['mm_2'], case_id, variant,
                                   mm_activity, 'mm_2', log)):
        return

    # Transport to dm
    if not (yield from do_activity(env, R['sm_2'], case_id, variant,
                                   '/sm/transport', 'sm_2', log)):
        return

    # Variable dm_2 activity (drill, cylindrical_drill)
    dm_activity = random.choice(['/dm/drill', '/dm/cylindrical_drill'])
    if not (yield from do_activity(env, R['dm_2'], case_id, variant,
                                   dm_activity, 'dm_2', log)):
        return

    # Conditional human review + storage (17%)
    if random.random() < HUMAN_REVIEW_PROBS[variant]:
        if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                       '/vgr/pick_up_and_transport', 'vgr_1', log)):
            return
        if not (yield from do_activity(env, R['hw_1'], case_id, variant,
                                       '/hw/human_review', 'hw_1', log)):
            return
        if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                       '/vgr/pick_up_and_transport', 'vgr_1', log)):
            return
        if not (yield from do_activity(env, R['hbw_1'], case_id, variant,
                                       '/hbw/get_empty_bucket', 'hbw_1', log)):
            return
        if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                       '/vgr/pick_up_and_transport', 'vgr_1', log)):
            return
        if not (yield from do_activity(env, R['hbw_1'], case_id, variant,
                                       '/hbw/store', 'hbw_1', log)):
            return


def process_wf_1107(env, case_id, R, log):
    """WF_1107: Track 1, burn -> [transport] -> sm_1(transport) -> punch_gill -> [review] -> [store]"""
    variant = 'WF_1107'

    if not (yield from _entry_phase(env, case_id, variant, R, log)):
        return

    # Cross to Track 1
    if not (yield from do_activity(env, R['vgr_1'], case_id, variant,
                                   '/vgr/pick_up_and_transport', 'vgr_1', log)):
        return

    # Track 1 processing
    if not (yield from do_activity(env, R['ov_1'], case_id, variant,
                                   '/ov/burn', 'ov_1', log)):
        return

    # Optional wt_1 transport
    if random.random() < 0.5:
        if not (yield from do_activity(env, R['wt_1'], case_id, variant,
                                       '/wt/pick_up_and_transport', 'wt_1', log)):
            return

    # sm_1 transport -> pm_1 punch_gill
    if not (yield from do_activity(env, R['sm_1'], case_id, variant,
                                   '/sm/transport', 'sm_1', log)):
        return
    if not (yield from do_activity(env, R['pm_1'], case_id, variant,
                                   '/pm/punch_gill', 'pm_1', log)):
        return

    # Conditional human review + storage (25%)
    if random.random() < HUMAN_REVIEW_PROBS[variant]:
        if not (yield from _human_review_and_store(env, case_id, variant, R, log)):
            return


# =============================================================================
# Arrival process
# =============================================================================

def arrival_process(env, R, log):
    """Bursty two-stage arrival process.

    Stage 1: Inter-burst gaps ~ Exponential(mean=457s)
    Stage 2: Within bursts, cases arrive with constant 13s IAT.
    """
    case_counter = 0

    while True:
        # Inter-burst gap (exponential, mean 457s = 7.6 min)
        gap = np.random.exponential(457)
        yield env.timeout(gap)

        if env.now >= SIMULATION_TIME:
            break

        # Burst size from empirical distribution
        burst_size = random.choice(BURST_SIZES)

        for i in range(burst_size):
            case_counter += 1
            case_id = f"case_{case_counter}"

            # Assign process model from categorical distribution
            variant = np.random.choice(PROCESS_MODELS, p=MODEL_WEIGHTS)

            # Start process model as concurrent SimPy process
            process_map = {
                'WF_101': process_wf_101,
                'WF_102': process_wf_102,
                'WF_103': process_wf_103,
                'WF_104': process_wf_104,
                'WF_105': process_wf_105,
                'WF_108': process_wf_108,
                'WF_109': process_wf_109,
                'WF_1106': process_wf_1106,
                'WF_1107': process_wf_1107,
            }
            env.process(process_map[variant](env, case_id, R, log))

            # Intra-burst IAT (constant 13s, except last in burst)
            if i < burst_size - 1:
                yield env.timeout(13)


# =============================================================================
# Main simulation function
# =============================================================================

def run_single_replication(seed):
    """Run a single replication of the simulation.

    Args:
        seed: Random seed for reproducibility.

    Returns:
        pandas.DataFrame with standard event log schema.
    """
    random.seed(seed)
    np.random.seed(seed)

    env = simpy.Environment()
    log = []

    # Create SimPy resources
    R = {name: simpy.Resource(env, capacity=cap)
         for name, cap in RESOURCE_CAPACITIES.items()}

    # Start arrival process
    env.process(arrival_process(env, R, log))

    # Run simulation
    env.run(until=SIMULATION_TIME)

    return pd.DataFrame(log)


# =============================================================================
# Demo / standalone execution
# =============================================================================

if __name__ == "__main__":
    df = run_single_replication(42)

    warmup = SIMULATION_TIME * 0.1

    print(f"Simulation complete. Total events: {len(df)}")
    print(f"Simulation time: {SIMULATION_TIME}s")
    print(f"Warm-up period: {warmup:.0f}s")
    print()

    if len(df) > 0:
        print("Variant distribution:")
        print(df['variant'].value_counts().to_string())
        print()

        print("Resource utilization (event count):")
        print(df['resource'].value_counts().to_string())
        print()

        print("Lifecycle states:")
        print(df['lifecycle:state'].value_counts().to_string())
        print()

        print("Activity distribution:")
        print(df['activity'].value_counts().to_string())
        print()

        # Post-warmup stats
        post_warmup = df[df['time:timestamp'] >= warmup]
        print(f"Post-warmup events: {len(post_warmup)}")

        if len(post_warmup) > 0:
            avg_duration = (post_warmup['operation_end_time'] -
                            post_warmup['time:timestamp']).mean()
            print(f"Average processing time: {avg_duration:.2f}s")

    print()
    print("First 20 events:")
    print(df.head(20).to_string())
