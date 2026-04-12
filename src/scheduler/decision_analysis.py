import pandas as pd


# ─────────────────────────────────────────────
# SIMPLE NORMALIZATION
# ─────────────────────────────────────────────
def normalize(series):
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min())


# ─────────────────────────────────────────────
# MAIN: GENERATE CANDIDATES
# ─────────────────────────────────────────────
def get_candidates(df, selected_time, window_hours=24):

    # future window
    candidates = df[
        (df["timestamp"] >= selected_time) &
        (df["timestamp"] <= selected_time + pd.Timedelta(hours=window_hours))
    ].copy()

    if candidates.empty:
        return candidates

    # delay
    candidates["delay_hours"] = (
        candidates["timestamp"] - selected_time
    ).dt.total_seconds() / 3600

    # prediction (rolling mean fallback)
    candidates["predicted_carbon"] = (
        df["carbon_intensity"]
        .rolling(24, min_periods=1)
        .mean()
        .shift(1)
        .reindex(candidates.index)
        .fillna(method="bfill")
    )

    # assume avg workload
    avg_workload = df["workload"].mean()

    candidates["estimated_carbon_kg"] = (
        candidates["predicted_carbon"] * avg_workload / 1000
    )

    # ─────────────────────────────────────────
    # SIMPLE SCORING (NO compute_score call)
    # ─────────────────────────────────────────
    carbon_norm = normalize(candidates["predicted_carbon"])
    delay_norm  = normalize(candidates["delay_hours"])

    # weights (same as your defaults)
    w_carbon = 0.8
    w_delay  = 0.15
    w_cost   = 0.05

    candidates["score"] = (
        w_carbon * carbon_norm +
        w_delay  * delay_norm +
        w_cost   * 0   # no cost yet
    )

    return candidates.sort_values("score")


# ─────────────────────────────────────────────
# INSIGHT GENERATION
# ─────────────────────────────────────────────
def build_insight(candidates):

    best = candidates.iloc[0]
    now  = candidates[candidates["delay_hours"] == 0]

    if not now.empty:
        now = now.iloc[0]
    else:
        now = best

    carbon_saved = now["estimated_carbon_kg"] - best["estimated_carbon_kg"]

    pct = (carbon_saved / now["estimated_carbon_kg"] * 100) if now["estimated_carbon_kg"] else 0

    return {
        "best_time": best["timestamp"],
        "best_delay_hrs": round(best["delay_hours"], 2),
        "best_carbon_kg": round(best["estimated_carbon_kg"], 2),
        "now_carbon_kg": round(now["estimated_carbon_kg"], 2),
        "carbon_saved_pct": round(pct, 2),
        "recommendation": (
            f"Delay by {round(best['delay_hours'],1)} hrs to save {round(pct,1)}% carbon"
            if pct > 0 else
            "Run now is already optimal"
        )
    }