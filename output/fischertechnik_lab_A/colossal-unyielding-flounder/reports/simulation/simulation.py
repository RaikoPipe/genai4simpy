"""
SimPy simulation of the Fischertechnik PCB manufacturing system.
Two-line manufacturing with 15 resources, 9 product variants, 18 workpieces.
"""

import random
import numpy as np
import pandas as pd
import simpy


# =============================================================================
# Constants
# =============================================================================

RESOURCE_CAPACITIES: dict[str, int] = {
    "ov_1": 1, "ov_2": 1, "wt_1": 1, "wt_2": 1,
    "mm_1": 1, "mm_2": 1, "sm_1": 1, "sm_2": 1,
    "dm_2": 1, "pm_1": 1, "hw_1": 1,
    "vgr_1": 1, "vgr_2": 1, "hbw_1": 1, "hbw_2": 1,
}

SIMULATION_TIME: int = 2280

# =============================================================================
# Processing Time Parameters (empirical means from reports, in seconds)
# =============================================================================

PROCESSING_TIMES = {
    # Machine activities
    "mm_mill_mm1": 5.08,
    "mm_mill_mm2": 14.44,
    "mm_deburr": 14.46,
    "mm_drill": 17.49,
    "mm_transport_from_to": 12.87,
    "ov_burn": 29.58,
    "ov_temper": 51.54,
    "sm_sort": 11.70,
    "sm_transport_sm1": 19.92,
    "sm_transport_sm2": 14.53,
    "dm_lower": 14.01,
    "dm_cylindrical_drill": 23.99,
    "pm_punch_gill": 27.48,
    "pm_punch_recesses": 23.64,
    "pm_punch_ribbing": 27.39,
    # Warehouse activities
    "hbw_unload": 35.89,
    "hbw_store_empty_bucket": 38.64,
    "hbw_get_empty_bucket": 36.16,
    "hbw_store": 37.98,
    # Human workstation
    "hw_human_review": 2.79,
    # VGR transport routes (per-route means)
    "vgr2_hbw2_to_dm2": 43.41,
    "vgr2_hbw2_to_ov2": 36.56,
    "vgr2_sm2_to_dm2": 43.44,
    "vgr1_dm2_to_ov1": 53.87,
    "vgr1_dm2_to_hw1": 51.75,
    "vgr1_pm1_to_hw1": 48.29,
    "vgr1_sm1_to_hw1": 40.43,
    "vgr1_hw1_to_hbw1_wait": 25.24,
    "vgr1_hbw1_wait_to_hbw1": 20.82,
    # Work transport routes
    "wt1_ov1_to_mm1": 26.09,
    "wt2_ov2_to_mm2": 29.09,
}

# System-wide failure rate per operation
FAILURE_RATE = 0.042


# =============================================================================
# Variant Routings (from topology_report.md)
# Each step: (activity, resource, duration_key)
# =============================================================================

VARIANT_ROUTINGS = {
    "WF_101": [
        ("/hbw/unload", "hbw_2", "hbw_unload"),
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_hbw2_to_dm2"),
        ("/hbw/store_empty_bucket", "hbw_2", "hbw_store_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_dm2_to_ov1"),
        ("/ov/burn", "ov_1", "ov_burn"),
        ("/ov/temper", "ov_1", "ov_temper"),
        ("/mm/mill", "mm_1", "mm_mill_mm1"),
        ("/mm/deburr", "mm_1", "mm_deburr"),
        ("/sm/sort", "sm_1", "sm_sort"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_sm1_to_hw1"),
        ("/hw/human_review", "hw_1", "hw_human_review"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hw1_to_hbw1_wait"),
        ("/hbw/get_empty_bucket", "hbw_1", "hbw_get_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hbw1_wait_to_hbw1"),
        ("/hbw/store", "hbw_1", "hbw_store"),
    ],
    "WF_102": [
        ("/hbw/unload", "hbw_2", "hbw_unload"),
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_hbw2_to_ov2"),
        ("/wt/pick_up_and_transport", "wt_2", "wt2_ov2_to_mm2"),
        ("/mm/drill", "mm_2", "mm_drill"),
        ("/sm/transport", "sm_2", "sm_transport_sm2"),
        ("/dm/lower", "dm_2", "dm_lower"),
        ("/hbw/store_empty_bucket", "hbw_2", "hbw_store_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_dm2_to_hw1"),
        ("/hw/human_review", "hw_1", "hw_human_review"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hw1_to_hbw1_wait"),
        ("/hbw/get_empty_bucket", "hbw_1", "hbw_get_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hbw1_wait_to_hbw1"),
        ("/hbw/store", "hbw_1", "hbw_store"),
    ],
    "WF_103": [
        ("/hbw/unload", "hbw_2", "hbw_unload"),
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_hbw2_to_dm2"),
        ("/hbw/store_empty_bucket", "hbw_2", "hbw_store_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_dm2_to_ov1"),
        ("/ov/burn", "ov_1", "ov_burn"),
        ("/ov/temper", "ov_1", "ov_temper"),
        ("/wt/pick_up_and_transport", "wt_1", "wt1_ov1_to_mm1"),
        ("/mm/mill", "mm_1", "mm_mill_mm1"),
        ("/mm/deburr", "mm_1", "mm_deburr"),
        ("/sm/transport", "sm_1", "sm_transport_sm1"),
        ("/pm/punch_recesses", "pm_1", "pm_punch_recesses"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_pm1_to_hw1"),
        ("/hw/human_review", "hw_1", "hw_human_review"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hw1_to_hbw1_wait"),
        ("/hbw/get_empty_bucket", "hbw_1", "hbw_get_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hbw1_wait_to_hbw1"),
        ("/hbw/store", "hbw_1", "hbw_store"),
    ],
    "WF_104": [
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_hbw2_to_ov2"),
        ("/hbw/store_empty_bucket", "hbw_2", "hbw_store_empty_bucket"),
        ("/ov/burn", "ov_2", "ov_burn"),
        ("/wt/pick_up_and_transport", "wt_2", "wt2_ov2_to_mm2"),
        ("/mm/mill", "mm_2", "mm_mill_mm2"),
        ("/sm/sort", "sm_2", "sm_sort"),
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_sm2_to_dm2"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_dm2_to_ov1"),
        ("/wt/pick_up_and_transport", "wt_1", "wt1_ov1_to_mm1"),
        ("/mm/deburr", "mm_1", "mm_deburr"),
        ("/sm/transport", "sm_1", "sm_transport_sm1"),
        ("/pm/punch_gill", "pm_1", "pm_punch_gill"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_pm1_to_hw1"),
        ("/hw/human_review", "hw_1", "hw_human_review"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hw1_to_hbw1_wait"),
        ("/hbw/get_empty_bucket", "hbw_1", "hbw_get_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hbw1_wait_to_hbw1"),
        ("/hbw/store", "hbw_1", "hbw_store"),
    ],
    "WF_105": [
        ("/hbw/unload", "hbw_2", "hbw_unload"),
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_hbw2_to_dm2"),
        ("/hbw/store_empty_bucket", "hbw_2", "hbw_store_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_dm2_to_ov1"),
        ("/ov/burn", "ov_1", "ov_burn"),
        ("/wt/pick_up_and_transport", "wt_1", "wt1_ov1_to_mm1"),
        ("/mm/deburr", "mm_1", "mm_deburr"),
        ("/sm/sort", "sm_1", "sm_sort"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_sm1_to_hw1"),
        ("/hw/human_review", "hw_1", "hw_human_review"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hw1_to_hbw1_wait"),
        ("/hbw/get_empty_bucket", "hbw_1", "hbw_get_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hbw1_wait_to_hbw1"),
        ("/hbw/store", "hbw_1", "hbw_store"),
    ],
    "WF_108": [
        ("/hbw/unload", "hbw_2", "hbw_unload"),
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_hbw2_to_ov2"),
        ("/hbw/store_empty_bucket", "hbw_2", "hbw_store_empty_bucket"),
        ("/ov/burn", "ov_2", "ov_burn"),
        ("/wt/pick_up_and_transport", "wt_2", "wt2_ov2_to_mm2"),
        ("/mm/drill", "mm_2", "mm_drill"),
        ("/mm/deburr", "mm_2", "mm_deburr"),
        ("/sm/sort", "sm_2", "sm_sort"),
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_sm2_to_dm2"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_dm2_to_hw1"),
        ("/hw/human_review", "hw_1", "hw_human_review"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hw1_to_hbw1_wait"),
        ("/hbw/get_empty_bucket", "hbw_1", "hbw_get_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hbw1_wait_to_hbw1"),
        ("/hbw/store", "hbw_1", "hbw_store"),
    ],
    "WF_109": [
        ("/hbw/unload", "hbw_2", "hbw_unload"),
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_hbw2_to_dm2"),
        ("/hbw/store_empty_bucket", "hbw_2", "hbw_store_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_dm2_to_ov1"),
        ("/ov/burn", "ov_1", "ov_burn"),
        ("/ov/temper", "ov_1", "ov_temper"),
        ("/wt/pick_up_and_transport", "wt_1", "wt1_ov1_to_mm1"),
        ("/mm/mill", "mm_1", "mm_mill_mm1"),
        ("/mm/deburr", "mm_1", "mm_deburr"),
        ("/sm/transport", "sm_1", "sm_transport_sm1"),
        ("/pm/punch_ribbing", "pm_1", "pm_punch_ribbing"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_pm1_to_hw1"),
        ("/hw/human_review", "hw_1", "hw_human_review"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hw1_to_hbw1_wait"),
        ("/hbw/get_empty_bucket", "hbw_1", "hbw_get_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hbw1_wait_to_hbw1"),
        ("/hbw/store", "hbw_1", "hbw_store"),
    ],
    "WF_1106": [
        ("/hbw/unload", "hbw_2", "hbw_unload"),
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_hbw2_to_ov2"),
        ("/hbw/store_empty_bucket", "hbw_2", "hbw_store_empty_bucket"),
        ("/wt/pick_up_and_transport", "wt_2", "wt2_ov2_to_mm2"),
        ("/mm/transport_from_to", "mm_2", "mm_transport_from_to"),
        ("/sm/transport", "sm_2", "sm_transport_sm2"),
        ("/dm/cylindrical_drill", "dm_2", "dm_cylindrical_drill"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_dm2_to_hw1"),
        ("/hw/human_review", "hw_1", "hw_human_review"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hw1_to_hbw1_wait"),
        ("/hbw/get_empty_bucket", "hbw_1", "hbw_get_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hbw1_wait_to_hbw1"),
        ("/hbw/store", "hbw_1", "hbw_store"),
    ],
    "WF_1107": [
        ("/hbw/unload", "hbw_2", "hbw_unload"),
        ("/vgr/pick_up_and_transport", "vgr_2", "vgr2_hbw2_to_dm2"),
        ("/hbw/store_empty_bucket", "hbw_2", "hbw_store_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_dm2_to_ov1"),
        ("/ov/burn", "ov_1", "ov_burn"),
        ("/wt/pick_up_and_transport", "wt_1", "wt1_ov1_to_mm1"),
        ("/mm/drill", "mm_1", "mm_drill"),
        ("/sm/transport", "sm_1", "sm_transport_sm1"),
        ("/pm/punch_ribbing", "pm_1", "pm_punch_ribbing"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_pm1_to_hw1"),
        ("/hw/human_review", "hw_1", "hw_human_review"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hw1_to_hbw1_wait"),
        ("/hbw/get_empty_bucket", "hbw_1", "hbw_get_empty_bucket"),
        ("/vgr/pick_up_and_transport", "vgr_1", "vgr1_hbw1_wait_to_hbw1"),
        ("/hbw/store", "hbw_1", "hbw_store"),
    ],
}


# =============================================================================
# Arrival Schedule (from inter_arrival_times_report.md, scaled by 0.75)
# Format: (case_id, variant, arrival_time)
# =============================================================================

ARRIVAL_SCHEDULE = [
    ("WF_101_30", "WF_101", 0.0),
    ("WF_102_31", "WF_102", 0.68),
    ("WF_103_29", "WF_103", 1.92),
    ("WF_105_21", "WF_105", 3.04),
    ("WF_1106_21", "WF_1106", 3.52),
    ("WF_1107_16", "WF_1107", 4.13),
    ("WF_108_17", "WF_108", 4.51),
    ("WF_109_15", "WF_109", 5.18),
    ("WF_104_20", "WF_104", 475.12),
    ("WF_1106_22", "WF_1106", 1068.27),
    ("WF_103_30", "WF_103", 1348.68),
    ("WF_105_22", "WF_105", 1350.45),
    ("WF_101_31", "WF_101", 1424.78),
    ("WF_102_32", "WF_102", 1425.29),
    ("WF_1107_17", "WF_1107", 1495.35),
    ("WF_104_21", "WF_104", 1499.50),
    ("WF_108_18", "WF_108", 1501.00),
    ("WF_109_16", "WF_109", 1711.68),
]


def get_duration(duration_key):
    """Sample processing duration with +/-5% Gaussian noise."""
    base = PROCESSING_TIMES[duration_key]
    return max(0.1, base * np.random.normal(1.0, 0.05))


def workpiece_process(env, case_id, variant, resources, event_log, arrival_time):
    """Simulate a single workpiece flowing through its variant routing."""
    yield env.timeout(arrival_time)

    routing = VARIANT_ROUTINGS[variant]

    for activity, resource_name, duration_key in routing:
        # Pre-determine failure (system-wide Bernoulli trial)
        failed = random.random() < FAILURE_RATE

        # Request resource, perform operation
        with resources[resource_name].request() as req:
            yield req
            start_time = env.now
            duration = get_duration(duration_key)
            yield env.timeout(duration)
            end_time = env.now

        if failed:
            # Emit failure row
            event_log.append({
                "case_id": case_id,
                "variant": variant,
                "activity": activity,
                "resource": resource_name,
                "time:timestamp": start_time,
                "operation_end_time": end_time,
                "lifecycle:state": "failure",
                "response_status_code": 418,
            })

            # Retry (always succeeds)
            with resources[resource_name].request() as req:
                yield req
                start_time = env.now
                duration = get_duration(duration_key)
                yield env.timeout(duration)
                end_time = env.now

            event_log.append({
                "case_id": case_id,
                "variant": variant,
                "activity": activity,
                "resource": resource_name,
                "time:timestamp": start_time,
                "operation_end_time": end_time,
                "lifecycle:state": "success",
                "response_status_code": 200,
            })
        else:
            event_log.append({
                "case_id": case_id,
                "variant": variant,
                "activity": activity,
                "resource": resource_name,
                "time:timestamp": start_time,
                "operation_end_time": end_time,
                "lifecycle:state": "success",
                "response_status_code": 200,
            })


def run_single_replication(seed: int) -> pd.DataFrame:
    """Run one replication of the Fischertechnik manufacturing simulation.

    Args:
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with standard event-log schema.
    """
    random.seed(seed)
    np.random.seed(seed)

    env = simpy.Environment()
    resources = {
        name: simpy.Resource(env, capacity=1)
        for name in RESOURCE_CAPACITIES
    }

    event_log = []

    for case_id, variant, arrival_time in ARRIVAL_SCHEDULE:
        env.process(
            workpiece_process(env, case_id, variant, resources, event_log, arrival_time)
        )

    env.run(until=SIMULATION_TIME)

    return pd.DataFrame(event_log)


if __name__ == "__main__":
    df = run_single_replication(seed=42)

    print(f"Total events: {len(df)}")
    print(f"Unique cases: {df['case_id'].nunique()}")
    print(f"Variants: {sorted(df['variant'].unique())}")
    print(f"Activities: {sorted(df['activity'].unique())}")
    print(f"Resources: {sorted(df['resource'].unique())}")
    print(f"States: {df['lifecycle:state'].value_counts().to_dict()}")
    print(f"Time range: {df['time:timestamp'].min():.2f} - {df['operation_end_time'].max():.2f}")

    failures = df[df['lifecycle:state'] == 'failure']
    print(f"Failures: {len(failures)}")

    for variant in sorted(df['variant'].unique()):
        v_df = df[df['variant'] == variant]
        cases = v_df['case_id'].nunique()
        events = len(v_df)
        print(f"  {variant}: {cases} cases, {events} events")