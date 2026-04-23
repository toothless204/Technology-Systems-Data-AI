"""
PGN Predictive Maintenance - Streamlit Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.data.generate_dataset import generate_sensor_data
from src.data.preprocess import preprocess_pipeline
from src.models.predict import predict_failure_probability, business_impact_simulation
from src.models.optimize import optimize_maintenance_schedule

st.set_page_config(page_title="PGN PredMaint", page_icon="🔧", layout="wide")

# CSS Styling
st.markdown("""
<style>
    .metric-card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; text-align: center; }
    .metric-value { font-size: 2.2rem; font-weight: 600; color: #58a6ff; }
    .metric-label { font-size: 0.8rem; color: #8b949e; text-transform: uppercase; }
    .section-header { color: #58a6ff; font-size: 0.75rem; text-transform: uppercase; border-bottom: 1px solid #21262d; padding-bottom: 8px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#8b949e"), margin=dict(l=40, r=20, t=40, b=40))

@st.cache_data
def load_data():
    if not Path("data/processed/features.csv").exists():
        generate_sensor_data()
        preprocess_pipeline()
    return pd.read_csv("data/processed/features.csv", parse_dates=["timestamp"])

@st.cache_data
def get_predictions(model_name: str):
    try: return predict_failure_probability(load_data(), model_name)
    except Exception: return None

with st.sidebar:
    st.markdown("## 🔧 PGN PredMaint")
    selected_machine = st.selectbox("Machine ID", ["All", "M001", "M002", "M003"])
    model_choice = st.selectbox("Active Model", ["random_forest", "gradient_boosting"])
    alert_threshold = st.slider("Alert Threshold", 0.3, 0.9, 0.6, 0.05)
    
    if st.button("📊 Run Full Pipeline"):
        with st.spinner("Executing..."):
            generate_sensor_data()
            preprocess_pipeline()
        st.cache_data.clear()
        st.rerun()

st.markdown("# PGN Predictive & Prescriptive Maintenance")
st.markdown("---")

df = load_data()
predictions = get_predictions(model_choice)

df_view = df if selected_machine == "All" else df[df["machine_id"] == selected_machine]
pred_view = predictions if predictions is None or selected_machine == "All" else predictions[predictions["machine_id"] == selected_machine]

# KPI Row
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f"<div class='metric-card'><div class='metric-value'>{len(df_view):,}</div><div class='metric-label'>Readings</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='metric-card'><div class='metric-value'>{df_view['failure'].mean():.1%}</div><div class='metric-label'>Failure Rate</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='metric-card'><div class='metric-value'>{df_view['machine_id'].nunique()}</div><div class='metric-label'>Machines</div></div>", unsafe_allow_html=True)
high_risk = (pred_view["failure_prob"] >= alert_threshold).sum() if pred_view is not None else "N/A"
k4.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#f85149'>{high_risk}</div><div class='metric-label'>Active Alerts</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📡 Sensor Data", "🚨 Alert Monitor", "📊 Model Performance", "💰 Business Impact", "🛠️ Prescriptive Action Plan"])

with tab1:
    sensor_choice = st.selectbox("Sensor", ["pressure", "temperature", "flow", "vibration"])
    fig = go.Figure()
    for m in df_view["machine_id"].unique():
        m_data = df_view[df_view["machine_id"] == m].tail(300)
        fig.add_trace(go.Scatter(x=m_data["timestamp"], y=m_data[sensor_choice], name=m, mode="lines"))
    fig.update_layout(title=f"{sensor_choice.title()} Timeline", height=400, **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    if pred_view is not None:
        fig_alert = go.Figure()
        for m in pred_view["machine_id"].unique():
            m_data = pred_view[pred_view["machine_id"] == m].tail(300)
            fig_alert.add_trace(go.Scatter(x=m_data["timestamp"], y=m_data["failure_prob"], name=m, mode="lines", fill="tozeroy"))
        fig_alert.add_hline(y=alert_threshold, line_dash="dash", line_color="#d29922")
        fig_alert.update_layout(title="Failure Probability", height=400, **PLOTLY_LAYOUT)
        st.plotly_chart(fig_alert, use_container_width=True)

with tab3:
    path = Path("models/metrics_summary.csv")
    if path.exists(): st.dataframe(pd.read_csv(path), use_container_width=True)
    else: st.info("Train models to see metrics.")

with tab4:
    impact = business_impact_simulation(df)
    st.markdown(f"### Annual Savings: ${impact['annual_savings_usd']:,.0f} ({impact['downtime_reduction_pct']}% reduction)")

with tab5:
    st.markdown("<div class='section-header'>Daily Maintenance Optimization</div>", unsafe_allow_html=True)
    if pred_view is not None:
        c1, c2, c3 = st.columns(3)
        cost_pm = c1.number_input("Cost of Prev. Maintenance ($)", value=1000)
        cost_fail = c2.number_input("Cost of Catastrophic Failure ($)", value=5000)
        max_tech_hours = c3.number_input("Available Tech Hours Today", value=16)
        
        if st.button("⚙️ Run Optimization Solver"):
            opt_results = optimize_maintenance_schedule(pred_view, cost_pm, cost_fail, max_tech_hours)
            st.success("Optimization Complete.")
            st.dataframe(opt_results.style.map(lambda x: 'color: #3fb950; font-weight: bold;' if x == 'Schedule Maintenance' else '', subset=['action']).format({"failure_prob": "{:.1%}", "expected_cost": "${:,.2f}"}), use_container_width=True, hide_index=True)
            
            st.download_button("📥 Export Schedule to ERP (JSON)", opt_results.to_json(orient="records", indent=2), "schedule.json", "application/json")
    else: st.warning("Run ML pipeline first.")
