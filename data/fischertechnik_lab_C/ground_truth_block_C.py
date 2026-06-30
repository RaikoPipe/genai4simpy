"""
Ground-Truth Metrics — Fischertechnik Model Factory, Block-C (2021-07-01)
=========================================================================

Empirical ground-truth values extracted from block-C.csv for use in the
Stage-2 quantitative evaluation (see Evaluation Methodology, sections 2.2-2.5).
This module contains ONLY ground-truth constants — no simulation model.

Source slice characteristics:
  - Observation window : 5461.5 s (~91 min) on 2021-07-01
  - Cases (workpieces) : 37 (unbalanced across variants)
  - Activity instances : 379 (complete-transition events)
  - Variants           : 9
  - Completed cases    : 13 (reached /hbw/store)

CAVEAT — partial block: block-C is a short slice. Many traces are truncated by
the window edge (only 13/37 cases reach /hbw/store), so per-variant
routings are the LONGEST OBSERVED trace per variant, not guaranteed-complete
end-to-end sequences. Throughput / flow-time ground truth are window-bounded
and should be interpreted accordingly (cf. methodology 2.2 "Ground Truth").

Conventions match simulation_multi_rep.py / ground_truth_block_A.py:
  - Durations from start events: operation_end_time - time:timestamp.
  - Failure rate = failure-state completes / total completes.
"""

# ============================================================================
# DATASET-LEVEL GROUND TRUTH
# ============================================================================

GROUND_TRUTH = {
    'date': '2021-07-01',
    'throughput': 37,
    'completed_cases': 13,
    'activity_instances': 379,
    'observation_period_s': 5461.5,
    'mean_flow_time_s': 901.01,
    'failure_rate': 5/379,
    'iat_mean_s': 129.35,
    'iat_median_s': 1.64,
    'variant_distribution': {
        'WF_101': 4/37,
        'WF_102': 5/37,
        'WF_103': 5/37,
        'WF_104': 3/37,
        'WF_105': 4/37,
        'WF_108': 3/37,
        'WF_109': 3/37,
        'WF_1106': 6/37,
        'WF_1107': 4/37,
    },
    'activity_mean_durations_s': {
        '/dm/cylindrical_drill'         : 42.95,
        '/dm/drill'                     : 27.13,
        '/dm/lower'                     : 13.84,
        '/hbw/get_empty_bucket'         : 38.38,
        '/hbw/store'                    : 37.2,
        '/hbw/store_empty_bucket'       : 37.01,
        '/hbw/unload'                   : 36.18,
        '/hw/human_review'              : 41.3,
        '/mm/deburr'                    : 17.05,
        '/mm/drill'                     : 13.71,
        '/mm/mill'                      : 8.71,
        '/mm/transport_from_to'         : 12.35,
        '/ov/burn'                      : 30.45,
        '/ov/temper'                    : 51.72,
        '/pm/punch_gill'                : 26.56,
        '/pm/punch_recesses'            : 23.75,
        '/pm/punch_ribbing'             : 23.57,
        '/sm/sort'                      : 11.78,
        '/sm/transport'                 : 18.92,
        '/vgr/pick_up_and_transport'    : 36.37,
        '/wt/pick_up_and_transport'     : 27.72,
    },
}

# ============================================================================
# PER-ACTIVITY DURATION STATS  (mean_s, std_s, n)
# ============================================================================

PROCESSING_TIMES = {
    '/dm/cylindrical_drill'         : (42.95, 5.48),   # n=2
    '/dm/drill'                     : (27.13, 10.93),   # n=4
    '/dm/lower'                     : (13.84, 0.01),   # n=4
    '/hbw/get_empty_bucket'         : (38.38, 4.23),   # n=14
    '/hbw/store'                    : (37.2, 3.44),   # n=13
    '/hbw/store_empty_bucket'       : (37.01, 3.7),   # n=34
    '/hbw/unload'                   : (36.18, 10.12),   # n=37
    '/hw/human_review'              : (41.3, 53.08),   # n=17
    '/mm/deburr'                    : (17.05, 12.0),   # n=19
    '/mm/drill'                     : (13.71, 9.06),   # n=8
    '/mm/mill'                      : (8.71, 4.45),   # n=11
    '/mm/transport_from_to'         : (12.35, 0.13),   # n=3
    '/ov/burn'                      : (30.45, 6.05),   # n=32
    '/ov/temper'                    : (51.72, 0.52),   # n=8
    '/pm/punch_gill'                : (26.56, 1.81),   # n=4
    '/pm/punch_recesses'            : (23.75, 0.11),   # n=2
    '/pm/punch_ribbing'             : (23.57, 0.32),   # n=2
    '/sm/sort'                      : (11.78, 3.35),   # n=13
    '/sm/transport'                 : (18.92, 9.82),   # n=19
    '/vgr/pick_up_and_transport'    : (36.37, 12.03),   # n=104
    '/wt/pick_up_and_transport'     : (27.72, 1.69),   # n=29
}

# ============================================================================
# FAILURE RATES  (per-activity: n_failures / n_instances)
# ============================================================================

FAILURE_RATES = {
    '/hbw/unload'                   : 2/37,   # 5.41%
    '/vgr/pick_up_and_transport'    : 3/104,   # 2.88%
}

OVERALL_FAILURE_RATE = 5/379  # 1.32%

FAILURE_STATUS_CODES = {   # empirical proportion among failures
    418: 3/5,   # 60.0%
    401: 2/5,   # 40.0%
}

# ============================================================================
# VARIANT WEIGHTS  (sampling proportions)
# ============================================================================

VARIANT_WEIGHTS = {
    'WF_101': 4/37,
    'WF_102': 5/37,
    'WF_103': 5/37,
    'WF_104': 3/37,
    'WF_105': 4/37,
    'WF_108': 3/37,
    'WF_109': 3/37,
    'WF_1106': 6/37,
    'WF_1107': 4/37,
}

# ============================================================================
# VARIANT ROUTING  (longest observed (activity, resource) trace per variant)
# NOTE: truncated by window edge — see module caveat.
# ============================================================================

VARIANT_ROUTING = {
    'WF_101': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/ov/burn'                       , 'ov_1'),
        ('/ov/temper'                     , 'ov_1'),
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/mm/mill'                       , 'mm_1'),
        ('/mm/deburr'                     , 'mm_1'),
        ('/sm/sort'                       , 'sm_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/store'                     , 'hbw_1'),
    ],
    'WF_102': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/ov/burn'                       , 'ov_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/wt/pick_up_and_transport'      , 'wt_2'),
        ('/mm/drill'                      , 'mm_2'),
        ('/sm/transport'                  , 'sm_2'),
        ('/dm/lower'                      , 'dm_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/store'                     , 'hbw_1'),
    ],
    'WF_103': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/ov/burn'                       , 'ov_1'),
        ('/ov/temper'                     , 'ov_1'),
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/mm/mill'                       , 'mm_1'),
        ('/mm/deburr'                     , 'mm_1'),
        ('/sm/transport'                  , 'sm_1'),
        ('/pm/punch_recesses'             , 'pm_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/store'                     , 'hbw_1'),
    ],
    'WF_104': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/ov/burn'                       , 'ov_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/wt/pick_up_and_transport'      , 'wt_2'),
        ('/sm/sort'                       , 'sm_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/mm/deburr'                     , 'mm_1'),
        ('/sm/transport'                  , 'sm_1'),
        ('/pm/punch_gill'                 , 'pm_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/ov/burn'                       , 'ov_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/wt/pick_up_and_transport'      , 'wt_2'),
        ('/mm/mill'                       , 'mm_2'),
        ('/sm/sort'                       , 'sm_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
    ],
    'WF_105': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/ov/burn'                       , 'ov_1'),
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/mm/deburr'                     , 'mm_1'),
        ('/sm/sort'                       , 'sm_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/store'                     , 'hbw_1'),
    ],
    'WF_108': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/ov/burn'                       , 'ov_2'),
        ('/wt/pick_up_and_transport'      , 'wt_2'),
        ('/mm/drill'                      , 'mm_2'),
        ('/mm/deburr'                     , 'mm_2'),
        ('/sm/sort'                       , 'sm_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/store'                     , 'hbw_1'),
    ],
    'WF_109': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/ov/burn'                       , 'ov_1'),
        ('/ov/temper'                     , 'ov_1'),
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/mm/mill'                       , 'mm_1'),
        ('/mm/deburr'                     , 'mm_1'),
        ('/sm/transport'                  , 'sm_1'),
        ('/pm/punch_ribbing'              , 'pm_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/store'                     , 'hbw_1'),
    ],
    'WF_1106': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/ov/burn'                       , 'ov_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/wt/pick_up_and_transport'      , 'wt_2'),
        ('/mm/transport_from_to'          , 'mm_2'),
        ('/sm/transport'                  , 'sm_2'),
        ('/dm/drill'                      , 'dm_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/store'                     , 'hbw_1'),
    ],
    'WF_1107': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/ov/burn'                       , 'ov_1'),
        ('/mm/transport_from_to'          , 'mm_1'),
        ('/sm/transport'                  , 'sm_1'),
        ('/pm/punch_gill'                 , 'pm_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/store'                     , 'hbw_1'),
    ],
}

POOL_MEMBERS = {
    'mm_pool': ['mm_1', 'mm_2'],
    'ov_pool': ['ov_1', 'ov_2'],
    'sm_pool': ['sm_1', 'sm_2'],
    'vgr_pool': ['vgr_1', 'vgr_2'],
    'wt_pool': ['wt_1', 'wt_2'],
}

# Resource capacities observed (dedicated unless pooled above)
RESOURCE_CAPACITIES = {
    'mm_pool': 2, 'ov_pool': 2, 'sm_pool': 2, 'vgr_pool': 2, 'wt_pool': 2,
    'dm_2': 1, 'hbw_1': 1, 'hbw_2': 1, 'hw_1': 1, 'pm_1': 1,
}