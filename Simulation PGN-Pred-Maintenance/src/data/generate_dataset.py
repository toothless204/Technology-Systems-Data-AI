"""
PGN Predictive Maintenance - Industrial Dataset Generator
Simulates realistic sensor data for gas pipeline monitoring
"""
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

def generate_sensor_data(
    n_points: int = 5000,
    n_machines: int = 3,
    output_path: str = "data/raw/sensor_data.csv"
) -> pd.DataFrame:
    all_dfs = []
    
    machine_configs = {
        "M001": {"base_pressure": 50, "base_temp": 70, "base_flow": 100},
        "M002": {"base_pressure": 45, "base_temp": 65, "base_flow": 95},
        "M003": {"base_pressure": 55, "base_temp": 75, "base_flow": 110},
    }
    
    failure_windows = {
        "M001": [(1000, 1100, "pressure_spike")],
        "M002": [(2000, 2080, "temperature_drift"), (3500, 3560, "flow_drop")],
        "M003": [(800, 880, "vibration_surge"), (4200, 4280, "pressure_spike")],
    }
    
    time = pd.date_range(start="2024-01-01", periods=n_points, freq="H")
    
    for machine_id in list(machine_configs.keys())[:n_machines]:
        cfg = machine_configs[machine_id]
        
        pressure   = np.random.normal(cfg["base_pressure"], 5, n_points)
        temperature= np.random.normal(cfg["base_temp"], 3, n_points)
        flow       = np.random.normal(cfg["base_flow"], 10, n_points)
        vibration  = np.random.normal(5, 1, n_points)
        failure    = np.zeros(n_points)
        
        for (start, end, mode) in failure_windows.get(machine_id, []):
            window_len = end - start
            ramp = np.linspace(0, 1, window_len)
            
            if mode == "pressure_spike":
                pressure[start:end] += ramp * np.random.normal(20, 5, window_len)
                vibration[start:end] += ramp * np.random.normal(3, 1, window_len)
            elif mode == "temperature_drift":
                temperature[start:end] += ramp * np.random.normal(15, 2, window_len)
                flow[start:end] -= ramp * np.random.normal(10, 3, window_len)
            elif mode == "flow_drop":
                flow[start:end] -= ramp * np.random.normal(30, 5, window_len)
                pressure[start:end] += ramp * np.random.normal(10, 3, window_len)
            elif mode == "vibration_surge":
                vibration[start:end] += ramp * np.random.normal(8, 2, window_len)
                pressure[start:end] += ramp * np.random.normal(5, 2, window_len)
            
            failure[start:end] = 1
        
        df = pd.DataFrame({
            "timestamp":   time,
            "machine_id":  machine_id,
            "pressure":    np.round(pressure, 3),
            "temperature": np.round(temperature, 3),
            "flow":        np.round(flow, 3),
            "vibration":   np.round(vibration, 3),
            "failure":     failure.astype(int)
        })
        
        all_dfs.append(df)
    
    final_df = pd.concat(all_dfs, ignore_index=True).sort_values("timestamp")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)
    print(f"Dataset generated: {len(final_df)} rows | Failure rate: {final_df['failure'].mean():.2%}")
    return final_df

if __name__ == "__main__":
    generate_sensor_data()
