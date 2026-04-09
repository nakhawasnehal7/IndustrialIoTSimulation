import sqlite3
import pandas as pd

conn = sqlite3.connect('data/iot_maintenance.db')

# 1. Get all high-risk predictions
print("\n1. HIGH RISK PREDICTIONS:")
high_risk = pd.read_sql_query("""
    SELECT 
        timestamp,
        machine_id,
        health_score,
        risk_classification,
        fault_probability
    FROM predictions
    WHERE health_score < 60
    ORDER BY health_score ASC
    LIMIT 10
""", conn)
print(high_risk)

# 2. Get anomaly detections
print("\n2. ANOMALY DETECTIONS:")
anomalies = pd.read_sql_query("""
    SELECT 
        timestamp,
        machine_id,
        temperature,
        vibration,
        pressure,
        health_score
    FROM predictions
    WHERE is_anomaly = 1
    ORDER BY timestamp DESC
    LIMIT 10
""", conn)
print(anomalies)

# 3. Risk distribution
print("\n3. RISK DISTRIBUTION:")
risk_dist = pd.read_sql_query("""
    SELECT 
        risk_classification,
        COUNT(*) as count,
        AVG(health_score) as avg_health_score
    FROM predictions
    GROUP BY risk_classification
    ORDER BY avg_health_score DESC
""", conn)
print(risk_dist)

# 4. Prediction accuracy (if we have actual labels)
print("\n4. RECENT PREDICTIONS:")
recent = pd.read_sql_query("""
    SELECT *
    FROM predictions
    ORDER BY timestamp DESC
    LIMIT 5
""", conn)
print(recent)

conn.close()
