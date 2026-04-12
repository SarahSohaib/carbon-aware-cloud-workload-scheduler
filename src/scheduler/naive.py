import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.config import COST_PER_UNIT


def naive_schedule(job_row):
    return {
        "job_index":       job_row.name,
        "scheduled_time":  job_row["timestamp"],
        "carbon_intensity": job_row["carbon_intensity"],
        "workload":        job_row["workload"],
        "cost":            job_row["workload"] * COST_PER_UNIT,
        "delay_hours":     0.0,
        "policy":          "naive",
    }