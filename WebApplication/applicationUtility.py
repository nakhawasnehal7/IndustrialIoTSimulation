import os
import sqlite3
from turtle import st

import joblib
import pandas as pd

DB_PATH = '../data/iot_maintenance.db'
MODELS_PATH = '../models/'


class ApplicationUtility:

    def load_models(model_paths=None, ):
        """Load trained ML models"""
        try:
            rf_model = joblib.load(os.path.join(MODELS_PATH, 'random_forest_model.pkl'))
            iso_forest = joblib.load(os.path.join(MODELS_PATH, 'isolation_forest_model.pkl'))
            scaler = joblib.load(os.path.join(MODELS_PATH, 'scaler.pkl'))
            return rf_model, iso_forest, scaler
        except Exception as e:
            st.error(f"⚠️ Error loading models: {e}")
            st.info("Please run the training script first: `python complete_workflow.py`")
            return None, None, None

    def get_db_connection(Db=None):

        """Create database connection"""
        if not os.path.exists(DB_PATH):
            st.error(f"⚠️ Database not found at: {DB_PATH}")
            st.info("Please run the training script first: `python complete_workflow.py`")
            return None
        return sqlite3.connect(DB_PATH)

    def load_sensor_data(limit=1000):
        """Load recent sensor readings"""
        conn = ApplicationUtility.get_db_connection()
        if conn is None:
            return pd.DataFrame()
        query = f"""
            SELECT * FROM sensor_readings 
            ORDER BY id DESC 
            LIMIT {limit}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def load_predictions(limit=500):
        """Load recent predictions"""
        conn = ApplicationUtility.get_db_connection()
        if conn is None:
            return pd.DataFrame()
        query = f"""
            SELECT * FROM predictions 
            ORDER BY id DESC 
            LIMIT {limit}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_machine_health_summary(limit=0):
        """Get current machine health summary"""
        conn = ApplicationUtility.get_db_connection()
        if conn is None:
            return None
        query = """
            SELECT 
                COUNT(*) as total_predictions,
                AVG(health_score) as avg_health,
                SUM(CASE WHEN is_anomaly = 1 THEN 1 ELSE 0 END) as anomaly_count,
                SUM(CASE WHEN fault_prediction > 0 THEN 1 ELSE 0 END) as fault_count
            FROM predictions
            WHERE timestamp > datetime('now', '-24 hours')
        """
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result.iloc[0] if not result.empty else None

    def get_risk_distribution(limit=0):
        """Get risk distribution"""
        conn = ApplicationUtility.get_db_connection()
        if conn is None:
            return pd.DataFrame()
        query = """
            SELECT 
                risk_classification,
                COUNT(*) as count
            FROM predictions
            GROUP BY risk_classification
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def classify_risk(health_score):
        """Classify risk level"""
        if health_score >= 80:
            return "Low Risk"
        elif health_score >= 60:
            return "Medium Risk"
        elif health_score >= 40:
            return "High Risk"
        else:
            return "Critical Risk"
