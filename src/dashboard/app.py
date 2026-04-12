import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.simulation.runner import load_data, run_simulation

st.set_page_config(page_title="Carbon-Aware Scheduler", layout="wide")
st.title("Carbon-Aware Cloud Workload Scheduler")

w_carbon = st.sidebar.slider("Carbon Weight", 0.0, 1.0, 0.6)
w_delay = st.sidebar.slider("Delay Weight", 0.0, 1.0, 0.2)
w_cost = st.sidebar.slider("Cost Weight", 0.0, 1.0, 0.2)

@st.cache_data
@st.cache_data
def get_results(w_carbon, w_cost, w_delay):
    df = load_data()
    naive_df, smart_df, summary = run_simulation(df, w_carbon, w_cost, w_delay)
    return naive_df, smart_df, summary, df

with st.spinner("Running simulation..."):
    naive_df, smart_df, summary, df = get_results(w_carbon, w_cost, w_delay)

# ── KPI cards ────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Naive Carbon (kg)",  summary["total_carbon_naive_kg"])
c2.metric("Smart Carbon (kg)",  summary["total_carbon_smart_kg"])
c3.metric("Carbon Saved (kg)",  summary["carbon_saved_kg"])
c4.metric("% Reduction",        f"{summary['pct_reduction']}%")

st.markdown("---")

# ── Bar chart: naive vs smart ────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Carbon Emissions")
    fig = go.Figure([go.Bar(
        x=["Naive Scheduler", "Carbon-Aware Scheduler"],
        y=[summary["total_carbon_naive_kg"], summary["total_carbon_smart_kg"]],
        marker_color=["#e74c3c", "#2ecc71"],
        text=[f'{summary["total_carbon_naive_kg"]} kg', f'{summary["total_carbon_smart_kg"]} kg'],
        textposition="outside",
    )])
    fig.update_layout(yaxis_title="kg CO₂", plot_bgcolor="rgba(0,0,0,0)", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Carbon Intensity Over Time")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["timestamp"], y=df["carbon_intensity"],
        mode="lines", name="Carbon Intensity",
        line=dict(color="#3498db", width=1.5)
    ))
    fig2.update_layout(
        yaxis_title="gCO₂/kWh", xaxis_title="Time",
        plot_bgcolor="rgba(0,0,0,0)", height=350
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Per-job carbon comparison ─────────────────────────────────────────
st.subheader("Per-Job Carbon: Naive vs Smart")
compare = pd.DataFrame({
    "job_index":   naive_df["job_index"],
    "naive_kg":    naive_df["carbon_kg"],
    "smart_kg":    smart_df["carbon_kg"],
    "saved_kg":    naive_df["carbon_kg"] - smart_df["carbon_kg"],
    "delay_hours": smart_df["delay_hours"],
})

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=compare["job_index"], y=compare["naive_kg"],
    mode="lines", name="Naive", line=dict(color="#e74c3c", width=1)
))
fig3.add_trace(go.Scatter(
    x=compare["job_index"], y=compare["smart_kg"],
    mode="lines", name="Carbon-Aware", line=dict(color="#2ecc71", width=1)
))
fig3.update_layout(
    yaxis_title="kg CO₂", xaxis_title="Job Index",
    plot_bgcolor="rgba(0,0,0,0)", height=350
)
st.plotly_chart(fig3, use_container_width=True)

# ── Delay distribution ────────────────────────────────────────────────
st.subheader("Scheduling Delay Distribution (Carbon-Aware)")
fig4 = go.Figure([go.Histogram(
    x=smart_df["delay_hours"], nbinsx=20,
    marker_color="#9b59b6"
)])
fig4.update_layout(
    xaxis_title="Delay (hours)", yaxis_title="Job Count",
    plot_bgcolor="rgba(0,0,0,0)", height=300
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.subheader("Simulation Summary")
st.json(summary)