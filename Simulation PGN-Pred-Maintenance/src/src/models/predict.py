"""
PGN Predictive Maintenance - Prediction & Alert System
Real-time failure probability and ROI calculator
"""
import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime

MODEL_DIR = Path("models/")
ALERT_THRESHOLD = 0.6
HIGH_RISK_THRESHOLD = 0.8

def predict_failure_probability(df: pd.DataFrame, model_name: str = "random_forest") -> pd.DataFrame:
    with open(MODEL_DIR / f"{model_name}.pkl", "rb") as f:
        model = pickle.load(f)
    with open(MODEL_DIR / "feature_cols.json", "r") as f:
        feature_cols = json.load(f)
        
    X = df[[c for c in feature_cols if c in df.columns]]
    probs = model.predict_proba(X)[:, 1]
    
    df = df.copy()
    df["failure_prob"] = np.round(probs, 4)
    df["alert_level"] = df["failure_prob"].apply(
        lambda p: "🔴 HIGH RISK" if p >= HIGH_RISK_THRESHOLD else ("🟡 WARNING" if p >= ALERT_THRESHOLD else "✅ NORMAL")
    )
    df["predicted_at"] = datetime.utcnow().isoformat()
    return df

def business_impact_simulation(predictions: pd.DataFrame, cost_per_downtime_hour: float = 5000, avg_repair_hours_without_ml: float = 100, avg_repair_hours_with_ml: float = 60, num_incidents_per_year: int = 10) -> dict:
    cost_without_ml = avg_repair_hours_without_ml * cost_per_downtime_hour * num_incidents_per_year
    cost_with_ml    = avg_repair_hours_with_ml    * cost_per_downtime_hour * num_incidents_per_year
    savings = cost_without_ml - cost_with_ml
    
    return {
        "cost_without_ml_usd": cost_without_ml,
        "cost_with_ml_usd": cost_with_ml,
        "annual_savings_usd": savings,
        "downtime_reduction_pct": round((savings / cost_without_ml) * 100, 1),
        "hours_saved_per_year": (avg_repair_hours_without_ml - avg_repair_hours_with_ml) * num_incidents_per_year
    }

def generate_alert_report(predictions: pd.DataFrame) -> pd.DataFrame:
    alerts = predictions[predictions["failure_prob"] >= ALERT_THRESHOLD].copy()
    if alerts.empty: return alerts
    return alerts.groupby("machine_id").agg(
        latest_timestamp=("timestamp", "max"), max_failure_prob=("failure_prob", "max")
    ).reset_index()
