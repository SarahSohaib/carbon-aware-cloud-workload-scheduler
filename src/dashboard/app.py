import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from src.simulation.runner import load_data, run_simulation
from src.scheduler.decision_analysis import get_candidates, build_insight


st.set_page_config(page_title="Carbon-Aware Scheduler", layout="wide")
st.title("Carbon-Aware Cloud Workload Scheduler")


# ─────────────────────────────────────────────────────────────
# DEFAULT WEIGHTS + SESSION STATE
# ─────────────────────────────────────────────────────────────
default_carbon = 0.8
default_delay  = 0.15
default_cost   = 0.05

if "carbon" not in st.session_state:
    st.session_state["carbon"] = default_carbon
if "delay" not in st.session_state:
    st.session_state["delay"] = default_delay
if "cost" not in st.session_state:
    st.session_state["cost"] = default_cost


w_carbon = st.sidebar.slider("Carbon Weight", 0.0, 1.0, st.session_state["carbon"])
w_delay  = st.sidebar.slider("Delay Weight", 0.0, 1.0, st.session_state["delay"])
w_cost   = st.sidebar.slider("Cost Weight", 0.0, 1.0, st.session_state["cost"])

if st.sidebar.button("Reset to Recommended"):
    st.session_state["carbon"] = default_carbon
    st.session_state["delay"] = default_delay
    st.session_state["cost"] = default_cost
    st.rerun()


# ─────────────────────────────────────────────────────────────
# DATA + SIMULATION
# ─────────────────────────────────────────────────────────────
@st.cache_data
def get_results(w_carbon, w_cost, w_delay):
    df = load_data()
    naive_df, smart_df, summary = run_simulation(df, w_carbon, w_cost, w_delay)
    return naive_df, smart_df, summary, df


with st.spinner("Running simulation..."):
    naive_df, smart_df, summary, df = get_results(w_carbon, w_cost, w_delay)


# ─────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Naive Carbon (kg)",  summary["total_carbon_naive_kg"])
c2.metric("Smart Carbon (kg)",  summary["total_carbon_smart_kg"])
c3.metric("Carbon Saved (kg)",  summary["carbon_saved_kg"])
c4.metric("% Reduction",        f"{summary['pct_reduction']}%")

st.markdown("---")


# ─────────────────────────────────────────────────────────────
# BAR + TIME GRAPH
# ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Carbon Emissions")
    fig = go.Figure([go.Bar(
        x=["Naive", "Carbon-Aware"],
        y=[summary["total_carbon_naive_kg"], summary["total_carbon_smart_kg"]],
        marker_color=["#e74c3c", "#2ecc71"],
    )])
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Carbon Intensity Over Time")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["carbon_intensity"],
        mode="lines"
    ))
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)


st.markdown("---")


# ─────────────────────────────────────────────────────────────
# PER JOB COMPARISON
# ─────────────────────────────────────────────────────────────
st.subheader("Per-Job Carbon: Naive vs Smart")

compare = pd.DataFrame({
    "job_index": naive_df["job_index"],
    "naive": naive_df["carbon_kg"],
    "smart": smart_df["carbon_kg"]
})

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=compare["job_index"], y=compare["naive"], name="Naive"))
fig3.add_trace(go.Scatter(x=compare["job_index"], y=compare["smart"], name="Smart"))
fig3.update_layout(height=350)

st.plotly_chart(fig3, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# DELAY DISTRIBUTION
# ─────────────────────────────────────────────────────────────
st.subheader("Delay Distribution")

fig4 = go.Figure([go.Histogram(x=smart_df["delay_hours"])])
st.plotly_chart(fig4, use_container_width=True)


st.markdown("---")
st.subheader("Simulation Summary")
st.json(summary)


# ══════════════════════════════════════════════════════════════
# DECISION INTELLIGENCE (NEW FEATURE)
# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Scheduling Decision Analysis")

min_ts = df["timestamp"].min().to_pydatetime()
max_ts = (df["timestamp"].max() - pd.Timedelta(hours=24)).to_pydatetime()

selected_dt = st.slider(
    "Job Submission Time",
    min_value=min_ts,
    max_value=max_ts,
    value=min_ts,
    format="YYYY-MM-DD HH:mm"
)

selected_time = pd.Timestamp(selected_dt)

candidates = get_candidates(df, selected_time)
insight    = build_insight(candidates)


if candidates.empty:
    st.warning("No options available")
else:
    best_time = insight["best_time"]

    st.success(insight["recommendation"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Delay", f"{insight['best_delay_hrs']} hrs")
    col2.metric("Now Carbon", f"{insight['now_carbon_kg']} kg")
    col3.metric("Best Carbon", f"{insight['best_carbon_kg']} kg")

    st.markdown("---")

    # Graph
    fig_d = go.Figure()

    fig_d.add_trace(go.Scatter(
        x=candidates["timestamp"],
        y=candidates["predicted_carbon"],
        mode="lines+markers",
        name="Carbon"
    ))

    fig_d.add_trace(go.Scatter(
        x=[best_time],
        y=[candidates[candidates["timestamp"] == best_time]["predicted_carbon"].values[0]],
        mode="markers",
        marker=dict(size=12, color="green"),
        name="Best"
    ))

    st.plotly_chart(fig_d, use_container_width=True)

    # Table
    st.subheader("Top Options")
    st.dataframe(candidates.head(10), use_container_width=True)