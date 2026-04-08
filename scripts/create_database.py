# Author SnehalNakhawa
# Date: 1st April
# Description : The script used to create database tables:
# create table sensor_readings, predictions, maintenance_alerts
import sqlite3

conn = sqlite3.connect('../data/iot_maintenance.db')
cursor = conn.cursor()

print("Database 'iot_maintenance.db' created successfully!")

# Create sensor_readings table
cursor.execute('''
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    vibration REAL NOT NULL,
    temperature REAL NOT NULL,
    pressure REAL NOT NULL,
    rms_vibration REAL NOT NULL,
    mean_temp REAL NOT NULL,
    fault_label INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')
print("Table 'sensor_readings' created!")

# Create predictions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    machine_id TEXT NOT NULL,
    vibration REAL,
    temperature REAL,
    pressure REAL,
    rms_vibration REAL,
    mean_temp REAL,
    fault_prediction INTEGER,
    fault_probability REAL,
    health_score REAL,
    risk_classification TEXT,
    is_anomaly BOOLEAN,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')
print("Table 'predictions' created!")

# Create maintenance_alerts table
cursor.execute('''
CREATE TABLE IF NOT EXISTS maintenance_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT,
    timestamp TEXT NOT NULL,
    acknowledged BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')
print(" Table 'maintenance_alerts' created!")

# Commit changes
conn.commit()

# Verify tables were created
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"\nTables in database: {[table[0] for table in tables]}")

# Close connection
conn.close()
print("\nDatabase setup complete!")
