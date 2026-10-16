"""Minimal contract-v2 conformant SimPy model (test fixture)."""
import random

import numpy as np
import pandas as pd
import simpy

RESOURCE_CAPACITIES = {"m_1": 1, "m_2": 1}
SIMULATION_TIME = 3600
ARRIVAL_RATE_SCALE = 1.0
FAILURES_ENABLED = True
ROUTE = {"A": [("/cut", "m_1"), ("/paint", "m_2")], "B": [("/paint", "m_2")]}
MEAN_IAT = 60.0
MEAN_SERVICE = {"/cut": 40.0, "/paint": 30.0}
FAIL_P = {"/cut": 0.1, "/paint": 0.0}


def _case(env, cid, variant, R, log):
    arrival = env.now
    for activity, res in ROUTE[variant]:
        while True:
            q = env.now
            with R[res].request() as req:
                yield req
                s = env.now
                yield env.timeout(np.random.exponential(MEAN_SERVICE[activity]))
                failed = FAILURES_ENABLED and random.random() < FAIL_P[activity]
                log.append({"case_id": cid, "variant": variant, "activity": activity, "resource": res,
                            "case_arrival": arrival, "queue_enter": q, "time:timestamp": s,
                            "operation_end_time": env.now, "lifecycle:state": "failure" if failed else "success"})
            if not failed:
                break


def _arrivals(env, R, log):
    i = 0
    while True:
        yield env.timeout(np.random.exponential(MEAN_IAT / ARRIVAL_RATE_SCALE))
        i += 1
        env.process(_case(env, f"sim_{i}", random.choice(list(ROUTE)), R, log))


def run_single_replication(seed):
    random.seed(seed)
    np.random.seed(seed)
    env = simpy.Environment()
    R = {r: simpy.Resource(env, capacity=c) for r, c in RESOURCE_CAPACITIES.items()}
    log = []
    env.process(_arrivals(env, R, log))
    env.run(until=SIMULATION_TIME)
    return pd.DataFrame(log)


if __name__ == "__main__":
    print(run_single_replication(1).head())
