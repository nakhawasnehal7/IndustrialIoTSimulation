# Author SnehalNakhawa
# Date: 1st April
# Description : It train the data using RandomForestClassifier and IsolationForest models

import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, accuracy_score
import joblib
from datetime import datetime

from trainUtility import TrainUtility

# Connect to database
conn = sqlite3.connect('../data/iot_maintenance.db')

# Load data
print("Loading data from database...")
query = """
    SELECT vibration, temperature, pressure, rms_vibration, mean_temp, fault_label
    FROM sensor_readings
"""
df = pd.read_sql_query(query, conn)
print(f"Loaded {len(df)} records")

# Display distribution
print("Fault Distribution:")
print(df['fault_label'].value_counts().sort_index())

# Prepare data
print("[2] Preparing data...")
X = df[['vibration', 'temperature', 'pressure', 'rms_vibration', 'mean_temp']]
y = df['fault_label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

# Train Random Forest
print("[3] Training Random Forest Classifier...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)

rf_model.fit(X_train_scaled, y_train)
y_pred = rf_model.predict(X_test_scaled)
y_pred_proba = rf_model.predict_proba(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)
print(f"Model trained! Accuracy: {accuracy:.3f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred,
                            target_names=['Normal', 'Fault', 'Critical']))

# Feature importance
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\nFeature Importance:")
print(feature_importance.to_string(index=False))

# Train Isolation Forest
print("\n[4] Training Isolation Forest for Anomaly Detection...")
X_normal = X_train_scaled[y_train == 0]
iso_forest = IsolationForest(
    contamination=0.1,
    random_state=42,
    n_estimators=100,
    n_jobs=-1
)
iso_forest.fit(X_normal)

anomaly_pred = iso_forest.predict(X_test_scaled)
anomaly_scores = iso_forest.score_samples(X_test_scaled)
anomaly_count = sum(anomaly_pred == -1)

print(f"Isolation Forest trained!")
print(f" Detected {anomaly_count}/{len(X_test)} anomalies ({anomaly_count / len(X_test) * 100:.1f}%)")

# Calculate health scores
print("\n[5] Calculating health scores and making predictions...")

# Generate predictions


predictions = []
for i in range(len(X_test)):
    max_fault_prob = max(y_pred_proba[i][1], y_pred_proba[i][2])

    health_score = TrainUtility.calculate_health_score(
        X_test.iloc[i]['vibration'],
        X_test.iloc[i]['temperature'],
        X_test.iloc[i]['pressure'],
        max_fault_prob,
        anomaly_scores[i]
    )

    predictions.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'machine_id': f'MACHINE_{(i % 100) + 1:03d}',
        'vibration': float(X_test.iloc[i]['vibration']),
        'temperature': float(X_test.iloc[i]['temperature']),
        'pressure': float(X_test.iloc[i]['pressure']),
        'rms_vibration': float(X_test.iloc[i]['rms_vibration']),
        'mean_temp': float(X_test.iloc[i]['mean_temp']),
        'fault_prediction': int(y_pred[i]),
        'fault_probability': float(max_fault_prob),
        'health_score': float(health_score),
        'risk_classification': TrainUtility.classify_risk(health_score),
        'is_anomaly': int(anomaly_pred[i] == -1)
    })

print(f"Generated {len(predictions)} predictions")

# Save predictions to database
print("\n[6] Saving predictions to database...")
predictions_df = pd.DataFrame(predictions)
predictions_df.to_sql('predictions', conn, if_exists='append', index=False)
print(f"Saved {len(predictions)} predictions to database")

# Verify saved predictions
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM predictions")
total_predictions = cursor.fetchone()[0]
print(f"Total predictions in database: {total_predictions}")

# Display risk distribution
print("\n[7] Risk Distribution:")
risk_dist = pd.read_sql_query("""
    SELECT 
        risk_classification, 
        COUNT(*) as count,
        ROUND(AVG(health_score), 1) as avg_health_score
    FROM predictions
    GROUP BY risk_classification
    ORDER BY avg_health_score DESC
""", conn)
print(risk_dist.to_string(index=False))

# Display sample predictions
print("\n[8] Sample Predictions:")
sample = pd.read_sql_query("""
    SELECT 
        machine_id,
        ROUND(health_score, 1) as health_score,
        risk_classification,
        fault_prediction,
        ROUND(fault_probability * 100, 1) as fault_prob_pct,
        is_anomaly
    FROM predictions
    ORDER BY health_score ASC
    LIMIT 10
""", conn)
print(sample.to_string(index=False))

# Save models
print("\n[9] Saving models...")
joblib.dump(rf_model, '../models/random_forest_model.pkl')
joblib.dump(iso_forest, '../models/isolation_forest_model.pkl')
joblib.dump(scaler, '../models/scaler.pkl')
print("Models saved successfully!")

conn.close()
