"""
SimPy simulation of the Fischertechnik Lab B manufacturing system.
15 resources, 9 workflow types, batch arrivals, failure/retry logic.
"""

import random
import numpy as np
import pandas as pd
import simpy

# =============================================================================
# CONSTANTS
# =============================================================================

SIMULATION_TIME = 7200  # 2 hours in seconds

RESOURCE_CAPACITIES = {
    "hbw_1": 1, "hbw_2": 1,
    "vgr_1": 1, "vgr_2": 1,
    "wt_1": 1, "wt_2": 1,
    "mm_1": 1, "mm_2": 1,
    "ov_1": 1, "ov_2": 1,
    "sm_1": 1, "sm_2": 1,
    "pm_1": 1, "dm_2": 1, "hw_1": 1,
}

# =============================================================================
# PROCESSING TIME DISTRIBUTIONS (from durations report, actual_duration)
# Returns duration in seconds
# =============================================================================

def proc_time(activity, resource):
    """Return a sampled processing time for the given activity-resource pair."""
    key = (activity, resource)
    dist = PROCESSING_DISTRIBUTIONS.get(key)
    if dist is None:
        raise ValueError(f"No processing time defined for {key}")
    return dist()


PROCESSING_DISTRIBUTIONS = {
    # hbw_2
    ("/hbw/unload", "hbw_2"): lambda: max(1.0, np.random.normal(38, 11)),
    ("/hbw/store_empty_bucket", "hbw_2"): lambda: max(1.0, np.random.normal(37, 6)),
    # hbw_1
    ("/hbw/get_empty_bucket", "hbw_1"): lambda: max(1.0, np.random.normal(39, 5)),
    ("/hbw/store", "hbw_1"): lambda: max(1.0, np.random.normal(38, 3)),
    # vgr
    ("/vgr/pick_up_and_transport", "vgr_1"): lambda: max(1.0, np.random.normal(37, 14)),
    ("/vgr/pick_up_and_transport", "vgr_2"): lambda: max(1.0, np.random.normal(41, 4)),
    # wt
    ("/wt/pick_up_and_transport", "wt_1"): lambda: max(1.0, np.random.normal(26, 1)),
    ("/wt/pick_up_and_transport", "wt_2"): lambda: 30.0,  # Deterministic
    # ov
    ("/ov/burn", "ov_1"): lambda: max(1.0, np.random.normal(27, 5)),
    ("/ov/burn", "ov_2"): lambda: max(1.0, np.random.exponential(34)),
    ("/ov/temper", "ov_1"): lambda: 53.0,  # Deterministic
    # mm
    ("/mm/mill", "mm_1"): lambda: max(1.0, np.random.normal(6, 2)),
    ("/mm/mill", "mm_2"): lambda: 14.0,  # Deterministic
    ("/mm/deburr", "mm_1"): lambda: max(1.0, np.random.normal(14, 1)),
    ("/mm/deburr", "mm_2"): lambda: max(1.0, np.random.normal(14, 1)),
    ("/mm/drill", "mm_2"): lambda: np.random.uniform(5, 16),
    ("/mm/transport_from_to", "mm_1"): lambda: max(1.0, np.random.normal(16, 6)),
    ("/mm/transport_from_to", "mm_2"): lambda: max(1.0, np.random.normal(16, 6)),
    # sm
    ("/sm/sort", "sm_1"): lambda: max(1.0, np.random.exponential(17)),
    ("/sm/sort", "sm_2"): lambda: max(1.0, np.random.normal(9, 1)),
    ("/sm/transport", "sm_1"): lambda: max(1.0, np.random.normal(21, 7)),
    ("/sm/transport", "sm_2"): lambda: 15.0,  # Deterministic
    # pm
    ("/pm/punch_gill", "pm_1"): lambda: 28.0,  # Deterministic
    ("/pm/punch_recesses", "pm_1"): lambda: 23.0,  # Deterministic
    ("/pm/punch_ribbing", "pm_1"): lambda: max(1.0, np.random.normal(25, 4)),
    # dm
    ("/dm/lower", "dm_2"): lambda: 14.0,  # Deterministic
    ("/dm/cylindrical_drill", "dm_2"): lambda: max(1.0, np.random.normal(31, 3)),
    # hw
    ("/hw/human_review", "hw_1"): lambda: max(1.0, np.random.exponential(17)),
}

# =============================================================================
# FAILURE RATES (from quantities report)
# =============================================================================

FAILURE_RATES = {
    ("/wt/pick_up_and_transport", "wt_1"): 0.148,
    ("/hbw/store_empty_bucket", "hbw_2"): 0.056,
    ("/hbw/unload", "hbw_2"): 0.053,
    ("/vgr/pick_up_and_transport", "vgr_1"): 0.012,
}

# =============================================================================
# WORKFLOW MIX (from quantities report - case counts)
# =============================================================================

WORKFLOW_TYPES = ["WF_101", "WF_102", "WF_103", "WF_104", "WF_105",
                  "WF_108", "WF_109", "WF_1106", "WF_1107"]
WORKFLOW_WEIGHTS = [6, 5, 5, 5, 4, 3, 4, 4, 2]  # case counts out of 38

# =============================================================================
# BATCH ARRIVAL PARAMETERS (from inter-arrival report)
# =============================================================================

# Between-batch: mean=424.87s, CV=0.837 → Gamma(shape=1.427, scale=297.7)
BETWEEN_BATCH_SHAPE = 1.427  # 1/CV² = 1/0.837²
BETWEEN_BATCH_SCALE = 297.7  # mean/shape = 424.87/1.427

# Within-batch: mean=3.64s, CV=1.761 → Gamma(shape=0.322, scale=11.3)
WITHIN_BATCH_SHAPE = 0.322  # 1/CV² = 1/1.761²
WITHIN_BATCH_SCALE = 11.3  # mean/shape = 3.64/0.322

BATCH_SIZES = [1, 2, 4, 5, 7, 9]
BATCH_SIZE_PROBS = np.array([0.53, 0.08, 0.15, 0.08, 0.08, 0.08])


# =============================================================================
# WORKFLOW ROUTING DEFINITIONS
# Each step: (activity, resource)
# Conditional steps have probability
# =============================================================================

def get_workflow_steps(wf_type):
    """Return the list of steps for a given workflow type."""
    if wf_type == "WF_101":
        return [
            ("/hbw/unload", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/hbw/store_empty_bucket", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/ov/burn", "ov_1"),
            ("/ov/temper", "ov_1"),
            ("/wt/pick_up_and_transport", "wt_1"),
            ("/mm/mill", "mm_1"),
            ("/mm/deburr", "mm_1"),
            ("/sm/sort", "sm_1"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/hw/human_review", "hw_1"),
        ]
    elif wf_type == "WF_102":
        steps = [
            ("/hbw/unload", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/hbw/store_empty_bucket", "hbw_2"),
        ]
        # ov_2 burn conditional (60%)
        if np.random.random() < 0.60:
            steps.append(("/ov/burn", "ov_2"))
        steps += [
            ("/wt/pick_up_and_transport", "wt_2"),
            ("/mm/drill", "mm_2"),
            ("/sm/transport", "sm_2"),
            ("/dm/lower", "dm_2"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/hw/human_review", "hw_1"),
        ]
        return steps
    elif wf_type == "WF_103":
        return [
            ("/hbw/unload", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/hbw/store_empty_bucket", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/ov/burn", "ov_1"),
            ("/ov/temper", "ov_1"),
            ("/wt/pick_up_and_transport", "wt_1"),
            ("/mm/mill", "mm_1"),
            ("/mm/deburr", "mm_1"),
            ("/sm/transport", "sm_1"),
            ("/pm/punch_recesses", "pm_1"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/hw/human_review", "hw_1"),
        ]
    elif wf_type == "WF_104":
        steps = [
            ("/hbw/unload", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/hbw/store_empty_bucket", "hbw_2"),
        ]
        # ov_2 burn conditional (80%)
        if np.random.random() < 0.80:
            steps.append(("/ov/burn", "ov_2"))
        steps += [
            ("/wt/pick_up_and_transport", "wt_2"),
            ("/mm/mill", "mm_2"),
            ("/sm/sort", "sm_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/wt/pick_up_and_transport", "wt_1"),
            ("/mm/deburr", "mm_1"),
            ("/sm/transport", "sm_1"),
            ("/pm/punch_gill", "pm_1"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/hw/human_review", "hw_1"),
        ]
        return steps
    elif wf_type == "WF_105":
        steps = [
            ("/hbw/unload", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/hbw/store_empty_bucket", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/ov/burn", "ov_1"),
            ("/wt/pick_up_and_transport", "wt_1"),
            ("/mm/deburr", "mm_1"),
            ("/sm/sort", "sm_1"),
        ]
        # human review conditional (50%) — includes preceding vgr_1 transport
        if np.random.random() < 0.50:
            steps.append(("/vgr/pick_up_and_transport", "vgr_1"))
            steps.append(("/hw/human_review", "hw_1"))
        return steps
    elif wf_type == "WF_108":
        steps = [
            ("/hbw/unload", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/hbw/store_empty_bucket", "hbw_2"),
        ]
        # ov_2 burn conditional (67%)
        if np.random.random() < 0.67:
            steps.append(("/ov/burn", "ov_2"))
        steps += [
            ("/wt/pick_up_and_transport", "wt_2"),
            ("/mm/drill", "mm_2"),
            ("/mm/deburr", "mm_2"),
            ("/sm/sort", "sm_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/hw/human_review", "hw_1"),
        ]
        return steps
    elif wf_type == "WF_109":
        return [
            ("/hbw/unload", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/hbw/store_empty_bucket", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/ov/burn", "ov_1"),
            ("/ov/temper", "ov_1"),
            ("/wt/pick_up_and_transport", "wt_1"),
            ("/mm/mill", "mm_1"),
            ("/mm/deburr", "mm_1"),
            ("/sm/transport", "sm_1"),
            ("/pm/punch_ribbing", "pm_1"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/hw/human_review", "hw_1"),
        ]
    elif wf_type == "WF_1106":
        steps = [
            ("/hbw/unload", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/hbw/store_empty_bucket", "hbw_2"),
            ("/ov/burn", "ov_2"),
            ("/wt/pick_up_and_transport", "wt_2"),
        ]
        # Step 6 varies: deburr, mill, or transport_from_to on mm_2
        mm_op = np.random.choice(["/mm/deburr", "/mm/mill", "/mm/transport_from_to"], p=[1/3, 1/3, 1/3])
        steps.append((mm_op, "mm_2"))
        steps += [
            ("/sm/transport", "sm_2"),
            ("/dm/cylindrical_drill", "dm_2"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/hw/human_review", "hw_1"),
        ]
        return steps
    elif wf_type == "WF_1107":
        steps = [
            ("/hbw/unload", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_2"),
            ("/hbw/store_empty_bucket", "hbw_2"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/ov/burn", "ov_1"),
            ("/wt/pick_up_and_transport", "wt_1"),
        ]
        # Step 7 varies: transport_from_to or mill on mm_1
        mm_op = np.random.choice(["/mm/transport_from_to", "/mm/mill"], p=[0.5, 0.5])
        steps.append((mm_op, "mm_1"))
        steps += [
            ("/sm/transport", "sm_1"),
        ]
        # Step 9 varies: punch_ribbing or punch_recesses on pm_1
        pm_op = np.random.choice(["/pm/punch_ribbing", "/pm/punch_recesses"], p=[0.5, 0.5])
        steps.append((pm_op, "pm_1"))
        steps += [
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/hw/human_review", "hw_1"),
        ]
        return steps
    else:
        raise ValueError(f"Unknown workflow type: {wf_type}")


def get_storage_tail(wf_type):
    """Return the optional storage tail steps for a given workflow type.
    
    Some workflows have a pre-storage vgr_1 transport between human_review
    and the storage tail.
    """
    # Workflows with pre-storage vgr_1 transport
    if wf_type in ("WF_102", "WF_104", "WF_105"):
        return [
            ("/vgr/pick_up_and_transport", "vgr_1"),  # pre-storage transport
            ("/hbw/get_empty_bucket", "hbw_1"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/vgr/pick_up_and_transport", "vgr_1"),
            ("/hbw/store", "hbw_1"),
        ]
    # Workflows without pre-storage vgr (standard tail)
    return [
        ("/hbw/get_empty_bucket", "hbw_1"),
        ("/vgr/pick_up_and_transport", "vgr_1"),
        ("/vgr/pick_up_and_transport", "vgr_1"),
        ("/hbw/store", "hbw_1"),
    ]


# =============================================================================
# WORKFLOW STORAGE TAIL PROBABILITY BY TYPE
# =============================================================================

STORAGE_TAIL_PROBS = {
    "WF_101": 0.83,
    "WF_102": 0.60,
    "WF_103": 0.00,  # No storage tail
    "WF_104": 0.60,
    "WF_105": 0.50,
    "WF_108": 0.67,
    "WF_109": 0.00,  # No storage tail
    "WF_1106": 0.50,
    "WF_1107": 1.00,
}


# =============================================================================
# SIMULATION
# =============================================================================

def batch_arrival_process(env, resources, event_log, case_counter):
    """Generate batch arrivals with gamma-distributed IATs (report §3.2)."""
    while True:
        # Between-batch delay: Gamma matching report CV=0.837
        delay = np.random.gamma(BETWEEN_BATCH_SHAPE, BETWEEN_BATCH_SCALE)
        yield env.timeout(delay)

        # Check if we're past simulation time
        if env.now >= SIMULATION_TIME:
            break

            # Batch size from empirical distribution (report §3.3)
        batch_size = np.random.choice(BATCH_SIZES, p=BATCH_SIZE_PROBS)

        # Release cases within batch
        for i in range(batch_size):
            if env.now >= SIMULATION_TIME:
                break
            if i > 0:
                # Within-batch delay: Gamma matching report CV=1.761
                yield env.timeout(np.random.gamma(WITHIN_BATCH_SHAPE, WITHIN_BATCH_SCALE))
            if env.now >= SIMULATION_TIME:
                break

            case_id = f"case_{case_counter[0]}"
            case_counter[0] += 1

            # Select workflow type
            wf_type = np.random.choice(WORKFLOW_TYPES, p=np.array(WORKFLOW_WEIGHTS) / sum(WORKFLOW_WEIGHTS))

            env.process(workpiece_process(env, case_id, wf_type, resources, event_log))


def workpiece_process(env, case_id, wf_type, resources, event_log):
    """Process a single workpiece through its workflow."""
    steps = get_workflow_steps(wf_type)

    for activity, resource in steps:
        # Check for failure
        fail_rate = FAILURE_RATES.get((activity, resource), 0.0)
        failed = np.random.random() < fail_rate

        if failed:
            if resource == "wt_1":
                # Log the initial failure FIRST (the one detected above)
                with resources[resource].request() as req:
                    yield req
                    start_time = env.now
                    duration = proc_time(activity, resource)
                    yield env.timeout(duration)
                    end_time = env.now
                    event_log.append({
                        "case_id": case_id,
                        "variant": wf_type,
                        "activity": activity,
                        "resource": resource,
                        "time:timestamp": start_time,
                        "operation_end_time": end_time,
                        "lifecycle:state": "failure",
                        "response_status_code": 418,
                    })
                # Then retry up to 2 more times
                success = False
                for attempt in range(2):
                    retry_delay = np.random.exponential(90.7)
                    yield env.timeout(retry_delay)
                    with resources[resource].request() as req:
                        yield req
                        start_time = env.now
                        duration = proc_time(activity, resource)
                        yield env.timeout(duration)
                        end_time = env.now
                        if np.random.random() >= fail_rate:
                            event_log.append({
                                "case_id": case_id,
                                "variant": wf_type,
                                "activity": activity,
                                "resource": resource,
                                "time:timestamp": start_time,
                                "operation_end_time": end_time,
                                "lifecycle:state": "success",
                                "response_status_code": 200,
                            })
                            success = True
                            break
                        else:
                            event_log.append({
                                "case_id": case_id,
                                "variant": wf_type,
                                "activity": activity,
                                "resource": resource,
                                "time:timestamp": start_time,
                                "operation_end_time": end_time,
                                "lifecycle:state": "failure",
                                "response_status_code": 418,
                            })
                if not success:
                    return  # All retries failed
            else:
                # Terminal failure for other resources
                with resources[resource].request() as req:
                    yield req
                    start_time = env.now
                    duration = proc_time(activity, resource)
                    yield env.timeout(duration)
                    end_time = env.now

                    event_log.append({
                        "case_id": case_id,
                        "variant": wf_type,
                        "activity": activity,
                        "resource": resource,
                        "time:timestamp": start_time,
                        "operation_end_time": end_time,
                        "lifecycle:state": "failure",
                        "response_status_code": 418,
                    })
                return  # Case terminated
        else:
            # Normal processing (no failure)
            with resources[resource].request() as req:
                yield req
                start_time = env.now
                duration = proc_time(activity, resource)
                yield env.timeout(duration)
                end_time = env.now

                event_log.append({
                    "case_id": case_id,
                    "variant": wf_type,
                    "activity": activity,
                    "resource": resource,
                    "time:timestamp": start_time,
                    "operation_end_time": end_time,
                    "lifecycle:state": "success",
                    "response_status_code": 200,
                })

    # Optional storage tail
    tail_prob = STORAGE_TAIL_PROBS.get(wf_type, 0.60)
    if np.random.random() < tail_prob:
        tail_steps = get_storage_tail(wf_type)
        for activity, resource in tail_steps:
            fail_rate = FAILURE_RATES.get((activity, resource), 0.0)
            failed = np.random.random() < fail_rate

            if failed and resource == "wt_1":
                # Log the initial failure FIRST
                with resources[resource].request() as req:
                    yield req
                    start_time = env.now
                    duration = proc_time(activity, resource)
                    yield env.timeout(duration)
                    end_time = env.now
                    event_log.append({
                        "case_id": case_id,
                        "variant": wf_type,
                        "activity": activity,
                        "resource": resource,
                        "time:timestamp": start_time,
                        "operation_end_time": end_time,
                        "lifecycle:state": "failure",
                        "response_status_code": 418,
                    })
                # Then retry up to 2 more times
                success = False
                for attempt in range(2):
                    retry_delay = np.random.exponential(90.7)
                    yield env.timeout(retry_delay)
                    with resources[resource].request() as req:
                        yield req
                        start_time = env.now
                        duration = proc_time(activity, resource)
                        yield env.timeout(duration)
                        end_time = env.now
                        if np.random.random() >= fail_rate:
                            event_log.append({
                                "case_id": case_id,
                                "variant": wf_type,
                                "activity": activity,
                                "resource": resource,
                                "time:timestamp": start_time,
                                "operation_end_time": end_time,
                                "lifecycle:state": "success",
                                "response_status_code": 200,
                            })
                            success = True
                            break
                        else:
                            event_log.append({
                                "case_id": case_id,
                                "variant": wf_type,
                                "activity": activity,
                                "resource": resource,
                                "time:timestamp": start_time,
                                "operation_end_time": end_time,
                                "lifecycle:state": "failure",
                                "response_status_code": 418,
                            })
                if not success:
                    return
            elif failed:
                with resources[resource].request() as req:
                    yield req
                    start_time = env.now
                    duration = proc_time(activity, resource)
                    yield env.timeout(duration)
                    end_time = env.now
                    event_log.append({
                        "case_id": case_id,
                        "variant": wf_type,
                        "activity": activity,
                        "resource": resource,
                        "time:timestamp": start_time,
                        "operation_end_time": end_time,
                        "lifecycle:state": "failure",
                        "response_status_code": 418,
                    })
                return
            else:
                with resources[resource].request() as req:
                    yield req
                    start_time = env.now
                    duration = proc_time(activity, resource)
                    yield env.timeout(duration)
                    end_time = env.now
                    event_log.append({
                        "case_id": case_id,
                        "variant": wf_type,
                        "activity": activity,
                        "resource": resource,
                        "time:timestamp": start_time,
                        "operation_end_time": end_time,
                        "lifecycle:state": "success",
                        "response_status_code": 200,
                    })


def run_single_replication(seed):
    """Run a single replication of the simulation.
    
    Args:
        seed: Random seed for reproducibility.
        
    Returns:
        pandas.DataFrame with standard event-log schema.
    """
    # Seed BOTH RNGs as required by contract
    random.seed(seed)
    np.random.seed(seed)

    env = simpy.Environment()

    # Create individual resources (capacity 1 each)
    resources = {name: simpy.Resource(env, capacity=1)
                 for name, cap in RESOURCE_CAPACITIES.items()}

    event_log = []
    case_counter = [0]

    # Start batch arrival process
    env.process(batch_arrival_process(env, resources, event_log, case_counter))

    # Run simulation
    env.run(until=SIMULATION_TIME)

    # Build DataFrame
    df = pd.DataFrame(event_log)

    # Ensure correct column order
    columns = ["case_id", "variant", "activity", "resource",
               "time:timestamp", "operation_end_time",
               "lifecycle:state", "response_status_code"]
    df = df[columns]

    return df


# =============================================================================
# MAIN (demo run)
# =============================================================================

if __name__ == "__main__":
    print("Running Fischertechnik Lab B simulation...")
    print(f"Simulation time: {SIMULATION_TIME}s")
    print(f"Resources: {len(RESOURCE_CAPACITIES)}")
    print()

    df = run_single_replication(seed=42)

    print(f"Total events logged: {len(df)}")
    print(f"Unique cases: {df['case_id'].nunique()}")
    print(f"Workflow types: {df['variant'].nunique()}")
    print()

    # Throughput
    completed = df[df["lifecycle:state"] == "success"]
    print(f"Successful operations: {len(completed)}")
    print(f"Failed operations: {len(df[df['lifecycle:state'] == 'failure'])}")
    print()

    # Resource utilization
    print("Events by resource:")
    print(df.groupby("resource").size().sort_values(ascending=False))
    print()

    # Events by workflow type
    print("Events by workflow type:")
    print(df.groupby("variant").size().sort_values(ascending=False))
    print()

    # Time range
    if len(df) > 0:
        print(f"First event at: {df['time:timestamp'].min():.1f}s")
        print(f"Last event at: {df['operation_end_time'].max():.1f}s")

    print()
    print("Schema check:")
    print(df.dtypes)
    print()
    print(df.head(10))
