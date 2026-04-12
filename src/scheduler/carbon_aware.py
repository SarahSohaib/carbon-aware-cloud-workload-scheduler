import pandas as pd
from src.scheduler.scoring import compute_score


def carbon_aware_schedule(job_row, data_df, w_carbon, w_cost, w_delay):
    current_time = job_row["timestamp"]
    deadline = current_time + pd.Timedelta(hours=24)

    candidates = data_df[
        (data_df["timestamp"] >= current_time) &
        (data_df["timestamp"] <= deadline)
    ].copy()

    if candidates.empty:
        return {
            "scheduled_time": current_time,
            "carbon_intensity": job_row["carbon_intensity"],
            "workload": job_row["workload"],
            "delay_hours": 0
        }

    candidates["delay_hours"] = (
        (candidates["timestamp"] - current_time).dt.total_seconds() / 3600
    )

    # normalize carbon
    min_c = candidates["carbon_intensity"].min()
    max_c = candidates["carbon_intensity"].max()

    candidates["carbon_norm"] = (
        (candidates["carbon_intensity"] - min_c) / (max_c - min_c + 1e-8)
    )

    candidates["cost"] = 0.5

    candidates["score"] = candidates.apply(
        lambda row: compute_score(
            row["carbon_norm"],
            row["cost"],
            row["delay_hours"],
            {
                "carbon": w_carbon,
                "cost": w_cost,
                "delay": w_delay
            }
        ),
        axis=1
    )

    best = candidates.loc[candidates["score"].idxmin()]

    return {
        "scheduled_time": best["timestamp"],
        "carbon_intensity": best["carbon_intensity"],
        "workload": job_row["workload"],
        "delay_hours": best["delay_hours"]
    }