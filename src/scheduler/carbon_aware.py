import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.config import COST_PER_UNIT
from src.scheduler.scoring import compute_score

MAX_DEFER_HOURS = 6


def carbon_aware_schedule(job, carbon_index, weights):
    submit   = job["submit_time"]
    deadline = submit + pd.Timedelta(hours=MAX_DEFER_HOURS)

    window = carbon_index.loc[
        (carbon_index.index >= submit) &
        (carbon_index.index <= deadline)
    ]

    if window.empty:
        window = carbon_index.iloc[[-1]]

    c_min, c_max = window["carbon_intensity"].min(), window["carbon_intensity"].max()
    c_range      = c_max - c_min + 1e-8

    best_score = float("inf")
    best_row   = None
    best_delay = 0.0

    for ts, row in window.iterrows():
        delay       = (ts - submit).total_seconds() / 3600
        carbon_norm = (row["carbon_intensity"] - c_min) / c_range
        delay_norm  = (delay / MAX_DEFER_HOURS) ** 2

        score = compute_score(carbon_norm, 0.0, delay_norm, weights)

        if score < best_score:
            best_score = score
            best_row   = row
            best_delay = delay
            best_ts    = ts

    return {
        "job_index":        job["job_id"],
        "scheduled_time":   best_ts,
        "carbon_intensity": best_row["carbon_intensity"],
        "workload":         job["workload"],
        "cost":             job["workload"] * COST_PER_UNIT,
        "delay_hours":      round(best_delay, 2),
        "policy":           "carbon_aware",
    }