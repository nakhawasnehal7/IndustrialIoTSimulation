# Author SnehalNakhawa
# Date: 1st April
# Description : Reading the CSV files for data and storing in the database

import os
import sqlite3
import pandas as pd

# Read your CSV file
print("Reading CSV file")
df = pd.read_csv('../data/industrial_fault_detection.csv')

print(f"Loaded {len(df)} rows from CSV")
print(f"Original columns: {df.columns.tolist()}")

# Rename columns to match database schema
df = df.rename(columns={
    'Timestamp': 'timestamp',
    'Vibration (mm/s)': 'vibration',
    'Temperature (°C)': 'temperature',
    'Pressure (bar)': 'pressure',
    'RMS Vibration': 'rms_vibration',
    'Mean Temp': 'mean_temp',
    'Fault Label': 'fault_label'
})

print(f"Renamed columns: {df.columns.tolist()}")

# Connect to database
new_path = '../data/iot_maintenance_new.db'
os.makedirs(os.path.dirname(new_path), exist_ok=True)

conn = sqlite3.connect(new_path)

# Load data into SQLite
print("Loading data into SQLite...")
df.to_sql('sensor_readings', conn, if_exists='append', index=False)

print(f"Successfully loaded {len(df)} rows into database!")

# Verify data was loaded
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sensor_readings")
count = cursor.fetchone()[0]
print(f"Total rows in database: {count}")

# Show sample data
print("\nSample data from database:")
sample = pd.read_sql_query("SELECT * FROM sensor_readings LIMIT 5", conn)
print(sample)

conn.close()
