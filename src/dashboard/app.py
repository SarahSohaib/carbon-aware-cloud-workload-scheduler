import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from src.simulation.runner           import load_data, run_simulation
from src.scheduler.decision_analysis import get_candidates, build_insight
from src.config                      import DEFAULT_WEIGHTS

if "initialized" not in st.session_state:
    st.session_state["carbon"] = DEFAULT_WEIGHTS["carbon"]
    st.session_state["delay"]  = DEFAULT_WEIGHTS["delay"]
    st.session_state["cost"]   = DEFAULT_WEIGHTS["cost"]
    st.session_state["initialized"] = True
st.set_page_config(page_title="Carbon-Aware Scheduler", layout="wide")

st.markdown("""
<style>
.subtitle   { color: #999; font-size: 0.85rem; margin-top: -8px; margin-bottom: 12px; }
.helper     { color: #999; font-size: 0.82rem; margin-top: -6px; margin-bottom: 16px; }
.section-gap{ margin-top: 2rem; }
.guide-step { color: #bbb; font-size: 0.83rem; line-height: 2.2; }
</style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────────
st.title("Carbon-Aware Cloud Workload Scheduler")
st.markdown(
    '<p class="subtitle">Evaluates the impact of scheduling decisions on carbon emissions '
    'by comparing immediate execution against carbon-optimized time slot selection.</p>',
    unsafe_allow_html=True,
)

# ── Sidebar: Weights ──────────────────────────────────────────────────
st.sidebar.header("Scoring Weights")
st.sidebar.caption("Adjust the relative importance of each factor in the scheduling score.")

for key, default in DEFAULT_WEIGHTS.items():
    if key not in st.session_state:
        st.session_state[key] = default

w_carbon = st.sidebar.slider("Carbon Weight", 0.0, 1.0, st.session_state["carbon"], step=0.05)
w_delay  = st.sidebar.slider("Delay Weight",  0.0, 1.0, st.session_state["delay"],  step=0.05)
w_cost   = st.sidebar.slider("Cost Weight",   0.0, 1.0, st.session_state["cost"],   step=0.05)

if st.sidebar.button("Reset to Defaults"):
    for key, val in DEFAULT_WEIGHTS.items():
        st.session_state[key] = val
    st.rerun()

weights = {"carbon": w_carbon, "cost": w_cost, "delay": w_delay}

st.sidebar.markdown("---")
st.sidebar.header("Dataset")
st.sidebar.caption("Upload a CSV file with columns: timestamp, carbon_intensity, workload.")
upload = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# ── Data loading ──────────────────────────────────────────────────────
@st.cache_data
def get_results(w_carbon, w_cost, w_delay, file_key):
    if upload is not None:
        df = pd.read_csv(upload)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
    else:
        df = load_data()
    naive_df, smart_df, summary = run_simulation(df, w_carbon, w_cost, w_delay)
    return naive_df, smart_df, summary, df

file_key = upload.name if upload else "default"

with st.spinner("Running simulation..."):
    naive_df, smart_df, summary, df = get_results(w_carbon, w_cost, w_delay, file_key)

# ── KPI cards ─────────────────────────────────────────────────────────
st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.subheader("Emissions Overview")
st.markdown(
    '<p class="subtitle">Aggregate carbon output across all jobs under each scheduling policy.</p>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Immediate Execution (kg)",      summary["total_carbon_naive_kg"],
          help="Total carbon emitted if all jobs execute immediately without optimization.")
c2.metric("Carbon-Aware Scheduling (kg)",  summary["total_carbon_smart_kg"],
          help="Total carbon emitted after shifting jobs to lower-intensity time windows.")
c3.metric("Carbon Saved (kg)",             summary["carbon_saved_kg"])
c4.metric("Reduction (%)",                 f"{summary['pct_reduction']}%")

st.markdown(
    f'<p class="helper">Carbon-aware scheduling reduces emissions by '
    f'<strong>{summary["pct_reduction"]}%</strong> with an average scheduling '
    f'delay of <strong>{summary["avg_delay_hours"]} hours</strong>.</p>',
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Bar + time chart ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Carbon by Scheduling Policy")
    st.markdown(
        '<p class="subtitle">Aggregate emissions comparison between immediate and optimized execution.</p>',
        unsafe_allow_html=True,
    )
    fig = go.Figure([go.Bar(
        x=["Immediate Execution", "Carbon-Aware Scheduling"],
        y=[summary["total_carbon_naive_kg"], summary["total_carbon_smart_kg"]],
        marker_color=["#e74c3c", "#2ecc71"],
        text=[f'{summary["total_carbon_naive_kg"]} kg',
              f'{summary["total_carbon_smart_kg"]} kg'],
        textposition="outside",
    )])
    fig.update_layout(
        height=350, plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="kg CO2", yaxis=dict(gridcolor="#333"),
        margin=dict(t=20),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Carbon Intensity Over Time")
    st.markdown(
        '<p class="subtitle">Grid carbon intensity across the dataset period (gCO2/kWh).</p>',
        unsafe_allow_html=True,
    )
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["timestamp"], y=df["carbon_intensity"],
        mode="lines", name="Carbon Intensity",
        line=dict(color="#3498db", width=1.5),
        fill="tozeroy", fillcolor="rgba(52,152,219,0.08)",
    ))
    fig2.update_layout(
        height=350, plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="gCO2/kWh", xaxis_title="Time",
        yaxis=dict(gridcolor="#333"), margin=dict(t=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Per-job comparison ────────────────────────────────────────────────
st.subheader("Per-Job Emission Comparison")
st.markdown(
    '<p class="subtitle">Comparison of per-job emissions under each scheduling policy.</p>',
    unsafe_allow_html=True,
)

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=naive_df["job_index"], y=naive_df["carbon_kg"],
    mode="lines", name="Immediate Execution",
    line=dict(color="#e74c3c", width=1),
))
fig3.add_trace(go.Scatter(
    x=smart_df["job_index"], y=smart_df["carbon_kg"],
    mode="lines", name="Carbon-Aware Scheduling",
    line=dict(color="#2ecc71", width=1),
))
fig3.update_layout(
    height=350, plot_bgcolor="rgba(0,0,0,0)",
    yaxis_title="kg CO2", xaxis_title="Job Index",
    yaxis=dict(gridcolor="#333"), legend=dict(orientation="h", y=-0.2),
    margin=dict(t=20),
)
st.plotly_chart(fig3, use_container_width=True)

# ── Delay distribution ────────────────────────────────────────────────
st.subheader("Scheduling Delay Distribution")
st.markdown(
    '<p class="subtitle">Distribution of deferral durations applied by the carbon-aware scheduler.</p>',
    unsafe_allow_html=True,
)

fig4 = go.Figure([go.Histogram(
    x=smart_df["delay_hours"], nbinsx=20,
    marker_color="#9b59b6",
)])
fig4.update_layout(
    height=280, plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Delay (hours)", yaxis_title="Number of Jobs",
    yaxis=dict(gridcolor="#333"), margin=dict(t=20),
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.subheader("Simulation Summary")
st.markdown(
    '<p class="subtitle">Complete output metrics from the simulation run.</p>',
    unsafe_allow_html=True,
)
st.json(summary)

# ══════════════════════════════════════════════════════════════════════
# DECISION ANALYSIS
# ══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.header("Scheduling Decision Analysis")
st.markdown(
    '<p class="subtitle">Identifies the optimal execution time slot within a 24-hour window '
    'based on predicted carbon intensity and configured scoring weights.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="guide-step">'
    '1. Select a job submission time<br>'
    '2. Review available scheduling options within the 24-hour window<br>'
    '3. Compare emission impact across candidate time slots'
    '</p>',
    unsafe_allow_html=True,
)
st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)

min_ts = df["timestamp"].min().to_pydatetime()
max_ts = (df["timestamp"].max() - pd.Timedelta(hours=24)).to_pydatetime()

selected_dt = st.slider(
    "Job Submission Time",
    min_value=min_ts, max_value=max_ts, value=min_ts,
    format="YYYY-MM-DD HH:mm",
)
selected_time = pd.Timestamp(selected_dt)

candidates = get_candidates(df, selected_time, weights)
insight    = build_insight(candidates, weights)

if candidates.empty:
    st.warning("No scheduling candidates found in the selected window.")
else:
    best_time = insight["best_time"]

    if insight.get("best_delay_hrs", 0) > 0:
        st.success(insight["recommendation"])
    else:
        st.info(insight["recommendation"])

    m1, m2, m3 = st.columns(3)
    m1.metric("Recommended Delay",         f"{insight['best_delay_hrs']} hrs",
              help="Hours to defer execution to reach the optimal time slot.")
    m2.metric("Immediate Execution (kg)",  f"{insight['now_carbon_kg']} kg",
              help="Estimated emissions if the job executes at the selected time.")
    m3.metric("Optimal Time Slot (kg)",    f"{insight['best_carbon_kg']} kg",
              help="Estimated emissions at the recommended time slot.")

    st.markdown("---")

    st.subheader("Predicted Carbon Intensity — Candidate Slots")
    st.markdown(
        '<p class="subtitle">Forecasted carbon intensity across available time slots '
        'within the scheduling window.</p>',
        unsafe_allow_html=True,
    )

    fig_d = go.Figure()
    fig_d.add_trace(go.Scatter(
        x=candidates["timestamp"], y=candidates["predicted_carbon"],
        mode="lines+markers", name="Predicted Carbon Intensity",
        line=dict(color="#3498db", width=2),
        marker=dict(size=5),
        fill="tozeroy", fillcolor="rgba(52,152,219,0.06)",
    ))

    now_row = candidates[candidates["delay_hours"] == 0]
    if not now_row.empty:
        fig_d.add_trace(go.Scatter(
            x=now_row["timestamp"], y=now_row["predicted_carbon"],
            mode="markers", name="Immediate Execution",
            marker=dict(color="#e74c3c", size=13, symbol="circle",
                        line=dict(width=2, color="white")),
        ))

    best_row = candidates[candidates["timestamp"] == best_time]
    if not best_row.empty:
        fig_d.add_trace(go.Scatter(
            x=best_row["timestamp"], y=best_row["predicted_carbon"],
            mode="markers", name="Optimal Time Slot",
            marker=dict(color="#2ecc71", size=15, symbol="star",
                        line=dict(width=1, color="white")),
        ))

    fig_d.update_layout(
        height=380, plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Time", yaxis_title="Predicted Carbon Intensity (gCO2/kWh)",
        yaxis=dict(gridcolor="#333"),
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=20),
    )
    st.plotly_chart(fig_d, use_container_width=True)

    st.subheader("Candidate Slot Rankings")
    st.markdown(
        '<p class="subtitle">Scheduling options ranked by composite efficiency score (lower is better).</p>',
        unsafe_allow_html=True,
    )

    display = candidates[["timestamp", "delay_hours", "predicted_carbon",
                           "estimated_carbon_kg", "score"]].head(10).copy()
    display = display.rename(columns={
        "predicted_carbon":    "Expected Carbon (gCO2/kWh)",
        "estimated_carbon_kg": "Emissions (kg)",
        "score":               "Efficiency Score",
        "delay_hours":         "Delay (hrs)",
    })
    display.index = range(1, len(display) + 1)

    def highlight_rows(row):
        ts = candidates.iloc[row.name - 1]["timestamp"]
        if ts == best_time:
            return ["background-color: rgba(46,204,113,0.15)"] * len(row)
        if candidates.iloc[row.name - 1]["delay_hours"] == 0:
            return ["background-color: rgba(231,76,60,0.12)"] * len(row)
        return [""] * len(row)

    st.dataframe(
        display.style.apply(highlight_rows, axis=1).format({
            "Expected Carbon (gCO2/kWh)": "{:.2f}",
            "Emissions (kg)":             "{:.4f}",
            "Efficiency Score":           "{:.4f}",
            "Delay (hrs)":                "{:.1f}",
        }),
        use_container_width=True,
    )
    st.caption("Green: optimal time slot  |  Red: immediate execution")