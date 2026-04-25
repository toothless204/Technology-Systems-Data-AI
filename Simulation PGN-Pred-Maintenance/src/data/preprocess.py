"""
PGN Predictive Maintenance - Data Preprocessing & Feature Engineering
Handles cleaning, time-series alignment, and concept drift (EWMA)
"""
import pandas as pd
import numpy as np
from pathlib import Path

def load_raw_data(path: str = "data/raw/sensor_data.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["timestamp", "machine_id"])
    sensor_cols = ["pressure", "temperature", "flow", "vibration"]
    df[sensor_cols] = df[sensor_cols].fillna(df[sensor_cols].median())
    
    for col in sensor_cols:
        mean = df.groupby("machine_id")[col].transform("mean")
        std  = df.groupby("machine_id")[col].transform("std")
        df[col] = df[col].clip(lower=mean - 5*std, upper=mean + 5*std)
    return df

def engineer_features(df: pd.DataFrame, window: int = 24) -> pd.DataFrame:
    df = df.sort_values(["machine_id", "timestamp"]).reset_index(drop=True)
    sensor_cols = ["pressure", "temperature", "flow", "vibration"]
    
    for col in sensor_cols:
        grp = df.groupby("machine_id")[col]
        
        # Exponential Weighted Moving Average (EWMA) for Concept Drift
        df[f"{col}_ewma"] = grp.transform(lambda x: x.ewm(span=window, adjust=False).mean())
        df[f"{col}_roll_std"]  = grp.transform(lambda x: x.rolling(window, min_periods=1).std().fillna(0))
        
        # Lag features
        df[f"{col}_lag1"]  = grp.shift(1)
        df[f"{col}_lag6"]  = grp.shift(6)
        df[f"{col}_lag24"] = grp.shift(24)
        
        # Z-score and ROC
        mean = df.groupby("machine_id")[col].transform("mean")
        std  = df.groupby("machine_id")[col].transform("std")
        df[f"{col}_zscore"] = (df[col] - mean) / (std + 1e-9)
        df[f"{col}_roc"] = df.groupby("machine_id")[col].diff()
    
    df = df.dropna().reset_index(drop=True)
    print(f"✅ Feature engineering done: {df.shape[1]} features | {len(df)} samples")
    return df

def preprocess_pipeline(
    raw_path: str = "data/raw/sensor_data.csv",
    output_path: str = "data/processed/features.csv"
) -> pd.DataFrame:
    df = engineer_features(clean_data(load_raw_data(raw_path)))
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    preprocess_pipeline()
