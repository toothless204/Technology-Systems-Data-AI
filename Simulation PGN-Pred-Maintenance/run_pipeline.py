"""
PGN Predictive Maintenance - Main Pipeline Runner
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent))

from src.data.generate_dataset import generate_sensor_data
from src.data.preprocess import preprocess_pipeline
from src.models.train import train_all_models
from src.models.predict import predict_failure_probability, business_impact_simulation
from src.models.optimize import optimize_maintenance_schedule

def run_pipeline():
    print("=" * 60)
    print("🚀 PGN PREDICTIVE & PRESCRIPTIVE MAINTENANCE PIPELINE")
    print("=" * 60)
    
    print("\n[1/5] 📦 Generating industrial sensor dataset...")
    generate_sensor_data()
    
    print("\n[2/5] 🔧 Running feature engineering (EWMA + Lags)...")
    preprocess_pipeline()
    
    print("\n[3/5] 🤖 Training Temporal ML models...")
    train_all_models()
    
    print("\n[4/5] 📊 Generating real-time predictions...")
    df = pd.read_csv("data/processed/features.csv", parse_dates=["timestamp"])
    predictions = predict_failure_probability(df, model_name="random_forest")
    impact = business_impact_simulation(predictions)
    
    print("\n[5/5] 🛠️ Solving linear program for optimal maintenance routing...")
    optimal_schedule = optimize_maintenance_schedule(predictions, cost_pm=1000, cost_fail=5000, max_tech_hours=16)
    
    erp_path = Path("reports/daily_erp_schedule.json")
    erp_path.parent.mkdir(parents=True, exist_ok=True)
    optimal_schedule.to_json(erp_path, orient="records", indent=2)
    
    print("\n" + "=" * 60)
    print("✅ FULL SYSTEM EXECUTED SUCCESSFULLY")
    print("=" * 60)
    print("  → Daily ERP Payload saved: reports/daily_erp_schedule.json")
    print("  → Launch dashboard:        streamlit run dashboard/app.py")

if __name__ == "__main__":
    run_pipeline()
