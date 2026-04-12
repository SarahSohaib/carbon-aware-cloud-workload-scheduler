import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.scheduler.scoring import compute_score

WINDOW_HOURS = 6


# ─────────────────────────────────────────────
# CARBON PREDICTION (HOURLY + FALLBACK)
# ─────────────────────────────────────────────
def _predict_carbon(df: pd.DataFrame, window: pd.DataFrame) -> pd.Series:
    try:
        base = df.copy()
        base["hour"] = pd.to_datetime(base["timestamp"]).dt.hour
        hourly_avg = base.groupby("hour")["carbon_intensity"].mean()

        predicted = window.index.hour.map(hourly_avg)

        if predicted.isna().all():
            raise ValueError("hourly prediction failed")

        return predicted.fillna(base["carbon_intensity"].mean())

    except Exception:
        return (
            df.set_index("timestamp")["carbon_intensity"]
            .rolling(6, min_periods=1)
            .mean()
            .shift(1)
            .reindex(window.index)
            .bfill()
            .fillna(df["carbon_intensity"].mean())
        )


# ─────────────────────────────────────────────
# BUILD INDEX
# ─────────────────────────────────────────────
def build_carbon_index(df):
    return (
        df[["timestamp", "carbon_intensity", "workload"]]
        .copy()
        .assign(timestamp=lambda x: pd.to_datetime(x["timestamp"]))
        .set_index("timestamp")
        .sort_index()
    )


# ─────────────────────────────────────────────
# GENERATE CANDIDATES
# ─────────────────────────────────────────────
def get_candidates(df, selected_time, weights):
    carbon_index = build_carbon_index(df)
    deadline = selected_time + pd.Timedelta(hours=WINDOW_HOURS)

    window = carbon_index.loc[
        (carbon_index.index >= selected_time) &
        (carbon_index.index <= deadline)
    ].copy()

    if window.empty:
        return pd.DataFrame()

    # prediction
    window["predicted_carbon"] = _predict_carbon(df, window)

    # estimated emissions
    avg_workload = df["workload"].mean()
    window["estimated_carbon_kg"] = (
        window["predicted_carbon"] * avg_workload / 1000
    )

    # delay
    window["delay_hours"] = (
        (window.index - selected_time).total_seconds() / 3600
    )

    # normalization (SAFE)
    c_min = window["predicted_carbon"].min()
    c_max = window["predicted_carbon"].max()
    c_range = (c_max - c_min) if (c_max - c_min) != 0 else 1

    d_max = window["delay_hours"].max()
    d_max = d_max if d_max != 0 else 1

    carbon_norm = (window["predicted_carbon"] - c_min) / c_range
    delay_norm = (window["delay_hours"] / d_max) ** 2

    # scoring
    window["score"] = [
        compute_score(c, 0.0, d, weights)
        for c, d in zip(carbon_norm, delay_norm)
    ]

    window = window.reset_index()

    return window.sort_values("score").reset_index(drop=True)


# ─────────────────────────────────────────────
# INSIGHT GENERATION
# ─────────────────────────────────────────────
def build_insight(candidates, weights):
    if candidates.empty:
        return {}

    best = candidates.iloc[0]

    # find "run now" row properly
    now_rows = candidates[candidates["delay_hours"].abs() < 1e-6]
    now = now_rows.iloc[0] if not now_rows.empty else candidates.iloc[0]

    carbon_now  = now["estimated_carbon_kg"]
    carbon_best = best["estimated_carbon_kg"]

    saved = carbon_now - carbon_best
    saved_pct = (saved / carbon_now * 100) if carbon_now else 0

    return {
        "best_time":        best["timestamp"],
        "best_delay_hrs":   round(best["delay_hours"], 2),
        "best_carbon_kg":   round(carbon_best, 4),
        "now_carbon_kg":    round(carbon_now, 4),
        "carbon_saved_pct": round(saved_pct, 2),
        "recommendation": (
            f"Delay by {round(best['delay_hours'], 1)} hrs to reduce emissions by "
            f"{round(saved_pct, 1)}% ({round(saved, 4)} kg CO₂)"
            if best["delay_hours"] > 0 and saved > 0
            else "Running immediately is already optimal."
        ),
    }