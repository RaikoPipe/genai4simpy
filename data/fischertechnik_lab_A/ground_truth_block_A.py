"""
Ground-Truth Metrics — Fischertechnik Model Factory, Block-A (2021-07-06)
==========================================================================

Empirical ground-truth values extracted from block-A.csv for use in the
Stage-2 quantitative evaluation (see Evaluation Methodology, sections 2.2-2.5).
This module contains ONLY ground-truth constants — no simulation model.

Source slice characteristics:
  - Observation window : 3183 s (~53 min) on 2021-07-06
  - Cases (workpieces) : 18 (2 per variant, balanced)
  - Activity instances : 192 (complete-transition events)
  - Variants           : 9
  - Completed cases    : 3 (reached /hbw/store)

CAVEAT — partial block: block-A is a short slice. Most traces are truncated by
the window edge (only 3/18 cases reach /hbw/store), so per-variant
routings are the LONGEST OBSERVED trace per variant, not guaranteed-complete
end-to-end sequences. Throughput / flow-time ground truth are window-bounded
and should be interpreted accordingly (cf. methodology 2.2 "Ground Truth").

Conventions match simulation_multi_rep.py:
  - Durations from start events: operation_end_time - time:timestamp.
  - Failure rate = failure-state completes / total completes.
"""

# ============================================================================
# DATASET-LEVEL GROUND TRUTH
# ============================================================================

GROUND_TRUTH = {
    'date': '2021-07-06',
    'throughput': 18,                 # workpieces observed in window
    'completed_cases': 3,              # reached /hbw/store
    'activity_instances': 192,
    'observation_period_s': 3183.2,
    'mean_flow_time_s': 1261.31,        # window-bounded (truncated traces)
    'failure_rate': 8/192,               # 4.17%
    'iat_mean_s': 134.25,
    'iat_median_s': 2.0,
    'variant_distribution': {        # empirical case proportions
        'WF_101': 2/18,
        'WF_102': 2/18,
        'WF_103': 2/18,
        'WF_104': 2/18,
        'WF_105': 2/18,
        'WF_108': 2/18,
        'WF_109': 2/18,
        'WF_1106': 2/18,
        'WF_1107': 2/18,
    },
    'terminal_activity': '/hbw/store',   # case completion marker (methodology 2.2 throughput)
    'iat_values_s': [0.91, 1.66, 1.48, 0.64, 0.81, 0.51, 0.9, 633.5, 799.96, 317.87,
                     2.36, 139.11, 0.69, 93.41, 5.53, 2.0, 280.91],  # observed IATs for KS test
    'resource_utilization': None,        # not extracted for block-A; set to enable util scoring
    'activity_mean_durations_s': {   # from start-event durations
        '/dm/cylindrical_drill'       : 23.99,
        '/dm/lower'                   : 14.01,
        '/hbw/get_empty_bucket'       : 37.06,
        '/hbw/store'                  : 37.98,
        '/hbw/store_empty_bucket'     : 41.09,
        '/hbw/unload'                 : 36.98,
        '/hw/human_review'            : 14.0,
        '/mm/deburr'                  : 14.46,
        '/mm/drill'                   : 14.44,
        '/mm/mill'                    : 6.67,
        '/mm/transport_from_to'       : 12.87,
        '/ov/burn'                    : 30.14,
        '/ov/temper'                  : 51.54,
        '/pm/punch_gill'              : 27.48,
        '/pm/punch_recesses'          : 23.64,
        '/pm/punch_ribbing'           : 27.39,
        '/sm/sort'                    : 50.15,
        '/sm/transport'               : 17.52,
        '/vgr/pick_up_and_transport'  : 40.39,
        '/wt/pick_up_and_transport'   : 27.38,
    },
}

# ============================================================================
# PER-ACTIVITY DURATION STATS  (mean_s, std_s, n)
# ============================================================================

PROCESSING_TIMES = {
    '/dm/cylindrical_drill'       : (23.99, 2.86),   # n=2
    '/dm/lower'                   : (14.01, 0.19),   # n=2
    '/hbw/get_empty_bucket'       : (37.06, 5.04),   # n=11
    '/hbw/store'                  : (37.98, 3.95),   # n=3
    '/hbw/store_empty_bucket'     : (41.09, 7.55),   # n=15
    '/hbw/unload'                 : (36.98, 11.06),   # n=17
    '/hw/human_review'            : (14.0, 19.21),   # n=14
    '/mm/deburr'                  : (14.46, 0.36),   # n=9
    '/mm/drill'                   : (14.44, 6.57),   # n=4
    '/mm/mill'                    : (6.67, 3.8),   # n=6
    '/mm/transport_from_to'       : (12.87, 0.39),   # n=2
    '/ov/burn'                    : (30.14, 6.67),   # n=13
    '/ov/temper'                  : (51.54, 0.06),   # n=5
    '/pm/punch_gill'              : (27.48, 0.0),   # n=1
    '/pm/punch_recesses'          : (23.64, 0.27),   # n=2
    '/pm/punch_ribbing'           : (27.39, 5.41),   # n=2
    '/sm/sort'                    : (50.15, 95.83),   # n=6
    '/sm/transport'               : (17.52, 3.01),   # n=9
    '/vgr/pick_up_and_transport'  : (40.39, 13.4),   # n=55
    '/wt/pick_up_and_transport'   : (27.38, 1.55),   # n=14
}

# ============================================================================
# FAILURE RATES  (per-activity: n_failures / n_instances)
# ============================================================================

FAILURE_RATES = {
    '/hbw/store_empty_bucket'     : 2/15,   # 13.33%
    '/hbw/unload'                 : 1/17,   # 5.88%
    '/vgr/pick_up_and_transport'  : 5/55,   # 9.09%
}

OVERALL_FAILURE_RATE = 8/192  # 4.17%

FAILURE_STATUS_CODES = {   # empirical proportion among failures
    418: 7/8,   # 87.5%
    401: 1/8,   # 12.5%
}

# ============================================================================
# VARIANT WEIGHTS  (sampling proportions)
# ============================================================================

VARIANT_WEIGHTS = {
    'WF_101': 2/18,
    'WF_102': 2/18,
    'WF_103': 2/18,
    'WF_104': 2/18,
    'WF_105': 2/18,
    'WF_108': 2/18,
    'WF_109': 2/18,
    'WF_1106': 2/18,
    'WF_1107': 2/18,
}

# ============================================================================
# VARIANT ROUTING  (longest observed (activity, resource) trace per variant)
# NOTE: truncated by window edge — see module caveat.
# ============================================================================

VARIANT_ROUTING = {
    'WF_101': [
        ('/hbw/unload'                   , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/hbw/store_empty_bucket'       , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/ov/burn'                      , 'ov_1'),
        ('/ov/temper'                    , 'ov_1'),
        ('/mm/mill'                      , 'mm_1'),
        ('/mm/deburr'                    , 'mm_1'),
        ('/sm/sort'                      , 'sm_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hw/human_review'              , 'hw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hbw/get_empty_bucket'         , 'hbw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hbw/store'                    , 'hbw_1'),
    ],
    'WF_102': [
        ('/hbw/unload'                   , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/wt/pick_up_and_transport'     , 'wt_2'),
        ('/mm/drill'                     , 'mm_2'),
        ('/sm/transport'                 , 'sm_2'),
        ('/dm/lower'                     , 'dm_2'),
        ('/hbw/store_empty_bucket'       , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hw/human_review'              , 'hw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hbw/get_empty_bucket'         , 'hbw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hbw/store'                    , 'hbw_1'),
    ],
    'WF_103': [
        ('/hbw/unload'                   , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/hbw/store_empty_bucket'       , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/ov/burn'                      , 'ov_1'),
        ('/ov/temper'                    , 'ov_1'),
        ('/wt/pick_up_and_transport'     , 'wt_1'),
        ('/mm/mill'                      , 'mm_1'),
        ('/mm/deburr'                    , 'mm_1'),
        ('/sm/transport'                 , 'sm_1'),
        ('/pm/punch_recesses'            , 'pm_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hw/human_review'              , 'hw_1'),
        ('/hbw/get_empty_bucket'         , 'hbw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
    ],
    'WF_104': [
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/hbw/store_empty_bucket'       , 'hbw_2'),
        ('/ov/burn'                      , 'ov_2'),
        ('/wt/pick_up_and_transport'     , 'wt_2'),
        ('/mm/mill'                      , 'mm_2'),
        ('/sm/sort'                      , 'sm_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/wt/pick_up_and_transport'     , 'wt_1'),
        ('/mm/deburr'                    , 'mm_1'),
        ('/sm/transport'                 , 'sm_1'),
        ('/pm/punch_gill'                , 'pm_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hw/human_review'              , 'hw_1'),
        ('/hbw/get_empty_bucket'         , 'hbw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
    ],
    'WF_105': [
        ('/hbw/unload'                   , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/hbw/store_empty_bucket'       , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/ov/burn'                      , 'ov_1'),
        ('/wt/pick_up_and_transport'     , 'wt_1'),
        ('/mm/deburr'                    , 'mm_1'),
        ('/sm/sort'                      , 'sm_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hw/human_review'              , 'hw_1'),
        ('/hbw/get_empty_bucket'         , 'hbw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
    ],
    'WF_108': [
        ('/hbw/unload'                   , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/hbw/store_empty_bucket'       , 'hbw_2'),
        ('/ov/burn'                      , 'ov_2'),
        ('/wt/pick_up_and_transport'     , 'wt_2'),
        ('/mm/drill'                     , 'mm_2'),
        ('/mm/deburr'                    , 'mm_2'),
        ('/sm/sort'                      , 'sm_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hw/human_review'              , 'hw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hbw/get_empty_bucket'         , 'hbw_1'),
    ],
    'WF_109': [
        ('/hbw/unload'                   , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/hbw/store_empty_bucket'       , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/ov/burn'                      , 'ov_1'),
        ('/ov/temper'                    , 'ov_1'),
        ('/wt/pick_up_and_transport'     , 'wt_1'),
        ('/mm/mill'                      , 'mm_1'),
        ('/mm/deburr'                    , 'mm_1'),
        ('/sm/transport'                 , 'sm_1'),
        ('/pm/punch_ribbing'             , 'pm_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hw/human_review'              , 'hw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hbw/get_empty_bucket'         , 'hbw_1'),
    ],
    'WF_1106': [
        ('/hbw/unload'                   , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/ov/burn'                      , 'ov_2'),
        ('/wt/pick_up_and_transport'     , 'wt_2'),
        ('/hbw/get_empty_bucket'         , 'hbw_1'),
        ('/mm/transport_from_to'         , 'mm_2'),
        ('/sm/transport'                 , 'sm_2'),
        ('/dm/cylindrical_drill'         , 'dm_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hw/human_review'              , 'hw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hbw/get_empty_bucket'         , 'hbw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hbw/store'                    , 'hbw_1'),
    ],
    'WF_1107': [
        ('/hbw/unload'                   , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_2'),
        ('/hbw/store_empty_bucket'       , 'hbw_2'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/ov/burn'                      , 'ov_1'),
        ('/wt/pick_up_and_transport'     , 'wt_1'),
        ('/mm/drill'                     , 'mm_1'),
        ('/sm/transport'                 , 'sm_1'),
        ('/pm/punch_ribbing'             , 'pm_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hw/human_review'              , 'hw_1'),
        ('/vgr/pick_up_and_transport'    , 'vgr_1'),
        ('/hbw/get_empty_bucket'         , 'hbw_1'),
    ],
}

POOL_MEMBERS = {
    'vgr_pool': ['vgr_1', 'vgr_2'],
    'mm_pool': ['mm_1', 'mm_2'],
    'ov_pool': ['ov_1', 'ov_2'],
    'sm_pool': ['sm_1', 'sm_2'],
    'wt_pool': ['wt_1', 'wt_2'],
}

# Resource capacities observed (dedicated unless pooled above)
RESOURCE_CAPACITIES = {
    'vgr_pool': 2, 'mm_pool': 2, 'ov_pool': 2, 'sm_pool': 2, 'wt_pool': 2,
    'hbw_1': 1, 'hbw_2': 1, 'pm_1': 1, 'dm_2': 1, 'hw_1': 1, 'ov_1': 1, 'mm_2': 1,
}