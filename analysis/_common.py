"""Shared paths and helpers for the WSC re-analysis scripts in analysis/."""
import os, sys
import simpy

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # repo root
sys.path.insert(0, R)                                                # -> import evaluate_v2
RUN = {"A": "colossal-unyielding-flounder", "B": "silent-xanthic-worm", "C": "elated-shellfish-of-attraction"}
STATS = {"tagged": 0, "untagged": 0}
OrigResource = simpy.Resource


def block_csv(b):
    return f"{R}/data/fischertechnik_lab_{b}/block-{b}.csv"


def model_path(b):
    return f"{R}/output/fischertechnik_lab_{b}/{RUN[b]}/reports/simulation/simulation.py"


class HbwPriority(simpy.PriorityResource):
    """Drop-in for simpy.Resource: requests from in-process cases precede new-order
    /hbw/unload requests; all other requests share priority 0 (FIFO preserved).
    The activity is read from the calling frame's local `activity` (all three models use it)."""
    def request(self, *a, **k):
        act = sys._getframe(1).f_locals.get("activity")
        STATS["tagged" if act is not None else "untagged"] += 1
        return super().request(priority=1 if act == "/hbw/unload" else 0)
