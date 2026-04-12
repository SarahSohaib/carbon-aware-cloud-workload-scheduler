import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.scheduler.naive        import naive_schedule
from src.scheduler.carbon_aware import carbon_aware_schedule

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "carbon_aware_workload_dataset.csv")


def load_data():
    df = pd.read_csv(DATA_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def run_simulation(df, w_carbon, w_cost, w_delay):
    if df is None:
        df = load_data()

    naive_results = []
    smart_results = []

    for _, row in df.iterrows():
        naive_results.append(naive_schedule(row))
        smart_results.append(
            carbon_aware_schedule(row, df, w_carbon, w_cost, w_delay)
        )

    naive_df = pd.DataFrame(naive_results)
    smart_df = pd.DataFrame(smart_results)

    naive_df["carbon_kg"] = naive_df["carbon_intensity"] * naive_df["workload"] / 1000
    smart_df["carbon_kg"] = smart_df["carbon_intensity"] * smart_df["workload"] / 1000

    total_naive = naive_df["carbon_kg"].sum()
    total_smart = smart_df["carbon_kg"].sum()
    pct_saved   = ((total_naive - total_smart) / total_naive * 100) if total_naive else 0

    summary = {
        "total_carbon_naive_kg": round(total_naive, 4),
        "total_carbon_smart_kg": round(total_smart, 4),
        "carbon_saved_kg":       round(total_naive - total_smart, 4),
        "pct_reduction":         round(pct_saved, 2),
        "total_jobs":            len(df),
        "avg_delay_hours":       round(smart_df["delay_hours"].mean(), 2),
    }

    return naive_df, smart_df, summary


if __name__ == "__main__":
    df = load_data()
    naive_df, smart_df, summary = run_simulation(df, 0.6, 0.2, 0.2)

    print("\n── Simulation Results ──────────────────────")
    for k, v in summary.items():
        print(f"  {k:<28}: {v}")