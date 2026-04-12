import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.config import COST_PER_UNIT


def naive_schedule(job, carbon_index):
    ts      = job["submit_time"]
    closest = carbon_index.index.asof(ts)
    row     = carbon_index.loc[closest]

    return {
        "job_index":        job["job_id"],
        "scheduled_time":   ts,
        "carbon_intensity": row["carbon_intensity"],
        "workload":         job["workload"],
        "cost":             job["workload"] * COST_PER_UNIT,
        "delay_hours":      0.0,
        "policy":           "naive",
    }