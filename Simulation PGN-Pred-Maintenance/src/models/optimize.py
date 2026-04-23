"""
PGN Predictive Maintenance - Operations Research Optimizer
Translates ML probabilities into actionable, capacity-constrained schedules.
"""
import pandas as pd
import pulp

def optimize_maintenance_schedule(
    predictions_df: pd.DataFrame, 
    cost_pm: float = 1000, 
    cost_fail: float = 5000, 
    max_tech_hours: int = 16
) -> pd.DataFrame:
    
    latest_preds = predictions_df.groupby("machine_id").last().reset_index()
    machines = latest_preds["machine_id"].tolist()
    probs = dict(zip(machines, latest_preds["failure_prob"]))
    
    # Asumsi: Setiap maintenance butuh 4 jam kerja teknisi
    hours = {m: 4 for m in machines}
    
    prob = pulp.LpProblem("Maintenance_Scheduling", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("maintain", machines, cat=pulp.LpBinary)
    
    # Fungsi Objektif: Minimasi expected cost
    prob += pulp.lpSum([cost_pm * x[i] + probs[i] * cost_fail * (1 - x[i]) for i in machines])
    
    # Constraint Kapasitas Teknisi
    prob += pulp.lpSum([hours[i] * x[i] for i in machines]) <= max_tech_hours
    
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    results = []
    for i in machines:
        action = "Schedule Maintenance" if pulp.value(x[i]) == 1 else "Monitor"
        expected_loss = cost_pm if action == "Schedule Maintenance" else probs[i] * cost_fail
        results.append({
            "machine_id": i,
            "failure_prob": probs[i],
            "action": action,
            "expected_cost": expected_loss
        })
        
    return pd.DataFrame(results).sort_values("failure_prob", ascending=False)
