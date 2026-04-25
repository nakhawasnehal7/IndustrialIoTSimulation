# Author SnehalNakhawa
# Date: 1st April
# Description the script for database to check database and table


import sqlite3
import pandas as pd

conn = sqlite3.connect('../data/iot_maintenance.db')

# Chek ALL Tables

tables = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table'",
    conn
)
print(tables)

# Check sensor reading table

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sensor_readings")
count = cursor.fetchone()[0]
print(f"Total rows in sensor_readings: {count}")

if count > 0:
    print("\nSample data:")
    sample = pd.read_sql_query("SELECT * FROM sensor_readings LIMIT 5", conn)
    print(sample)

    # Show fault distribution
    print("\nFault distribution:")
    fault_dist = pd.read_sql_query("""
        SELECT fault_label, COUNT(*) as count 
        FROM sensor_readings 
        GROUP BY fault_label
    """, conn)
    print(fault_dist)
else:
    print(" No data found! You need to load data first.")

# Check prediction table

cursor.execute("SELECT COUNT(*) FROM predictions")
pred_count = cursor.fetchone()[0]
print(f"Total rows in predictions: {pred_count}")

if pred_count > 0:
    pred_sample = pd.read_sql_query("SELECT * FROM predictions LIMIT 5", conn)
    print("Sample predictions:")
    print(pred_sample)
else:
    print("No predictions yet! Run training script to generate predictions.")

conn.close()
