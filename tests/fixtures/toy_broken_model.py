"""Contract-violating model (test fixture): trace replay + file I/O + import-time work."""
import random

import numpy as np
import pandas as pd
import simpy

RESOURCE_CAPACITIES = {"m_1": 1}
SIMULATION_TIME = 3600
ARRIVAL_SCHEDULE = [("WF_101_30", 0.0), ("WF_102_31", 10.0)]
DURATIONS = pd.read_csv(__file__.replace(".py", ".csv")) if False else None
print("loading model")


def _case(env, cid, R, log):
    with R["m_1"].request() as req:
        yield req
        s = env.now
        yield env.timeout(10)
        log.append({"case_id": cid, "variant": "A", "activity": "/cut", "resource": "m_1",
                    "time:timestamp": s, "operation_end_time": env.now, "lifecycle:state": "success"})


def _arr(env, R, log):
    for cid, t in ARRIVAL_SCHEDULE:
        yield env.timeout(max(0, t - env.now))
        env.process(_case(env, cid, R, log))


def run_single_replication(seed):
    random.seed(seed)
    np.random.seed(seed)
    env = simpy.Environment()
    R = {r: simpy.Resource(env, capacity=c) for r, c in RESOURCE_CAPACITIES.items()}
    log = []
    env.process(_arr(env, R, log))
    env.run(until=SIMULATION_TIME)
    return pd.DataFrame(log)
