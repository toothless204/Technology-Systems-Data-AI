"""
PGN Predictive Maintenance - Temporal Model Training
Enforces chronological splits to prevent future-data leakage
"""
import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score

TARGET_COL   = "failure"
EXCLUDE_COLS = ["timestamp", "machine_id", "failure"]
MODEL_DIR    = Path("models/")

def build_models() -> dict:
    return {
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=15, class_weight="balanced", n_jobs=-1, random_state=42
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42
        )
    }

def train_all_models(data_path: str = "data/processed/features.csv"):
    df = pd.read_csv(data_path, parse_dates=["timestamp"])
    feature_cols = [c for c in df.columns if c not in EXCLUDE_COLS]
    
    # Strictly Chronological Split
    df = df.sort_values("timestamp")
    split_idx = int(len(df) * 0.80) 
    
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    X_train, y_train = train_df[feature_cols], train_df[TARGET_COL]
    X_test, y_test = test_df[feature_cols], test_df[TARGET_COL]
    
    print(f"📦 Temporal Split: Train={len(train_df)} | Test={len(test_df)}")
    
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    models = build_models()
    all_metrics = []
    
    for name, model in models.items():
        print(f"🔧 Training {name}...")
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        report = classification_report(y_test, y_pred, output_dict=True)
        
        metrics = {
            "model_name": name,
            "accuracy": round(report["accuracy"], 4),
            "recall": round(report["1"]["recall"], 4),
            "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
            "avg_precision": round(average_precision_score(y_test, y_prob), 4),
        }
        all_metrics.append(metrics)
        
        with open(MODEL_DIR / f"{name}.pkl", "wb") as f:
            pickle.dump(model, f)
            
        if hasattr(model, "feature_importances_"):
            fi = pd.DataFrame({"feature": feature_cols, "importance": np.abs(model.feature_importances_)})
            fi.sort_values("importance", ascending=False).head(15).to_csv(MODEL_DIR / f"{name}_feature_importance.csv", index=False)
            
    pd.DataFrame(all_metrics).to_csv(MODEL_DIR / "metrics_summary.csv", index=False)
    with open(MODEL_DIR / "feature_cols.json", "w") as f:
        json.dump(feature_cols, f)
        
    print("\n✅ Temporal models trained and saved.")
    return models, all_metrics

if __name__ == "__main__":
    train_all_models()
