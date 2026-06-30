"""
Ground-Truth Metrics — Fischertechnik Model Factory, Block-B (2021-06-30)
=========================================================================

Empirical ground-truth values extracted from block-B.csv for use in the
Stage-2 quantitative evaluation (see Evaluation Methodology, sections 2.2-2.5).
This module contains ONLY ground-truth constants — no simulation model.

Source slice characteristics:
  - Observation window : 5943.7 s (~99 min) on 2021-06-30
  - Cases (workpieces) : 38 (unbalanced across variants)
  - Activity instances : 461 (complete-transition events)
  - Variants           : 9
  - Completed cases    : 14 (reached /hbw/store)

CAVEAT — partial block: block-B is a short slice. Many traces are truncated by
the window edge (only 14/38 cases reach /hbw/store), so per-variant
routings are the LONGEST OBSERVED trace per variant, not guaranteed-complete
end-to-end sequences. Throughput / flow-time ground truth are window-bounded
and should be interpreted accordingly (cf. methodology 2.2 "Ground Truth").

Conventions match simulation_multi_rep.py / ground_truth_block_A.py:
  - Durations from start events: operation_end_time - time:timestamp.
  - Failure rate = failure-state completes / total completes.

Alignment with evaluate.py (flag-free):
  - terminal_activity = '/hbw/store' lets the harness measure throughput as
    COMPLETED cases (methodology 2.2) and compare against completed_cases (14),
    rather than the weaker 'observed' (entered) basis.
  - iat_values_s carries the raw inter-arrival samples so the harness can run
    the two-sample KS test (2.2) instead of skipping it. mean/median of this
    list reproduce iat_mean_s / iat_median_s exactly.
"""

# ============================================================================
# DATASET-LEVEL GROUND TRUTH
# ============================================================================

GROUND_TRUTH = {
    'date': '2021-06-30',
    'throughput': 38,
    'completed_cases': 14,
    'terminal_activity': '/hbw/store',
    'activity_instances': 461,
    'observation_period_s': 5943.7,
    'mean_flow_time_s': 927.0,
    'failure_rate': 9/461,
    'iat_mean_s': 140.25,
    'iat_median_s': 3.19,
    'iat_values_s': [
        1.371, 1.112, 1.315, 858.657, 0.888, 0.967, 0.563, 0.704, 0.706,
        1.844, 0.752, 6.696, 1336.649, 1.708, 2.329, 1.515, 478.216, 5.856,
        0.652, 5.388, 9.873, 61.95, 193.353, 239.223, 189.614, 524.731, 4.222,
        0.624, 0.65, 3.006, 2.716, 32.267, 294.136, 199.435, 423.184, 3.188,
        299.322,
    ],
    'variant_distribution': {
        'WF_101': 6/38,
        'WF_102': 5/38,
        'WF_103': 5/38,
        'WF_104': 5/38,
        'WF_105': 4/38,
        'WF_108': 3/38,
        'WF_109': 4/38,
        'WF_1106': 4/38,
        'WF_1107': 2/38,
    },
    'activity_mean_durations_s': {
        '/dm/cylindrical_drill'         : 30.82,
        '/dm/lower'                     : 13.93,
        '/hbw/get_empty_bucket'         : 39.4,
        '/hbw/store'                    : 37.73,
        '/hbw/store_empty_bucket'       : 36.95,
        '/hbw/unload'                   : 37.78,
        '/hw/human_review'              : 16.74,
        '/mm/deburr'                    : 14.39,
        '/mm/drill'                     : 11.13,
        '/mm/mill'                      : 7.61,
        '/mm/transport_from_to'         : 15.67,
        '/ov/burn'                      : 34.15,
        '/ov/temper'                    : 52.69,
        '/pm/punch_gill'                : 27.75,
        '/pm/punch_recesses'            : 23.35,
        '/pm/punch_ribbing'             : 24.75,
        '/sm/sort'                      : 14.11,
        '/sm/transport'                 : 19.87,
        '/vgr/pick_up_and_transport'    : 38.01,
        '/wt/pick_up_and_transport'     : 27.32,
    },
}

# ============================================================================
# PER-ACTIVITY DURATION STATS  (mean_s, std_s, n)
# ============================================================================

PROCESSING_TIMES = {
    '/dm/cylindrical_drill'         : (30.82, 2.65),   # n=4
    '/dm/lower'                     : (13.93, 0.11),   # n=4
    '/hbw/get_empty_bucket'         : (39.4, 5.11),   # n=15
    '/hbw/store'                    : (37.73, 2.8),   # n=14
    '/hbw/store_empty_bucket'       : (36.95, 5.77),   # n=37
    '/hbw/unload'                   : (37.78, 10.61),   # n=38
    '/hw/human_review'              : (16.74, 27.99),   # n=30
    '/mm/deburr'                    : (14.39, 0.61),   # n=25
    '/mm/drill'                     : (11.13, 5.46),   # n=7
    '/mm/mill'                      : (7.61, 4.13),   # n=19
    '/mm/transport_from_to'         : (15.67, 6.39),   # n=3
    '/ov/burn'                      : (34.15, 33.83),   # n=33
    '/ov/temper'                    : (52.69, 1.28),   # n=14
    '/pm/punch_gill'                : (27.75, 0.46),   # n=3
    '/pm/punch_recesses'            : (23.35, 0.18),   # n=5
    '/pm/punch_ribbing'             : (24.75, 3.7),   # n=5
    '/sm/sort'                      : (14.11, 9.43),   # n=16
    '/sm/transport'                 : (19.87, 7.21),   # n=21
    '/vgr/pick_up_and_transport'    : (38.01, 11.68),   # n=127
    '/wt/pick_up_and_transport'     : (27.32, 1.65),   # n=41
}

# ============================================================================
# FAILURE RATES  (per-activity: n_failures / n_instances)
# ============================================================================

FAILURE_RATES = {
    '/hbw/store_empty_bucket'       : 2/37,   # 5.41%
    '/hbw/unload'                   : 2/38,   # 5.26%
    '/vgr/pick_up_and_transport'    : 1/127,   # 0.79%
    '/wt/pick_up_and_transport'     : 4/41,   # 9.76%
}

OVERALL_FAILURE_RATE = 9/461  # 1.95%

FAILURE_STATUS_CODES = {   # empirical proportion among failures
    418: 7/9,   # 77.8%
    401: 2/9,   # 22.2%
}

# ============================================================================
# VARIANT WEIGHTS  (sampling proportions)
# ============================================================================

VARIANT_WEIGHTS = {
    'WF_101': 6/38,
    'WF_102': 5/38,
    'WF_103': 5/38,
    'WF_104': 5/38,
    'WF_105': 4/38,
    'WF_108': 3/38,
    'WF_109': 4/38,
    'WF_1106': 4/38,
    'WF_1107': 2/38,
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
    ],
    'WF_104': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/ov/burn'                       , 'ov_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/wt/pick_up_and_transport'      , 'wt_2'),
        ('/mm/mill'                       , 'mm_2'),
        ('/sm/sort'                       , 'sm_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/mm/deburr'                     , 'mm_1'),
        ('/sm/transport'                  , 'sm_1'),
        ('/pm/punch_gill'                 , 'pm_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/store'                     , 'hbw_1'),
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
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
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
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/mm/mill'                       , 'mm_1'),
        ('/mm/deburr'                     , 'mm_1'),
        ('/sm/transport'                  , 'sm_1'),
        ('/pm/punch_ribbing'              , 'pm_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
    ],
    'WF_1106': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/ov/burn'                       , 'ov_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/wt/pick_up_and_transport'      , 'wt_2'),
        ('/mm/mill'                       , 'mm_2'),
        ('/sm/transport'                  , 'sm_2'),
        ('/dm/cylindrical_drill'          , 'dm_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hw/human_review'               , 'hw_1'),
        ('/hbw/get_empty_bucket'          , 'hbw_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/hbw/store'                     , 'hbw_1'),
    ],
    'WF_1107': [
        ('/hbw/unload'                    , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_2'),
        ('/hbw/store_empty_bucket'        , 'hbw_2'),
        ('/vgr/pick_up_and_transport'     , 'vgr_1'),
        ('/ov/burn'                       , 'ov_1'),
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/wt/pick_up_and_transport'      , 'wt_1'),
        ('/mm/mill'                       , 'mm_1'),
        ('/sm/transport'                  , 'sm_1'),
        ('/pm/punch_recesses'             , 'pm_1'),
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
    'hbw_1': 1, 'hbw_2': 1, 'dm_2': 1, 'hw_1': 1, 'pm_1': 1,
}