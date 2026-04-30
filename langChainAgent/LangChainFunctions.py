import sqlite3

import pandas as pd


def get_db_connection(self):
    """Get database connection"""
    return sqlite3.connect('../data/iot_maintenance.db')


class LangChainFunctions:

    def get_health_status(query: str = "") -> str:
        """
        Get current machine health status and statistics
        """
        try:
            conn = get_db_connection(self=None)
            summary_query = """
              SELECT 
                    COUNT(*) as total_predictions,
                    AVG(health_score) as avg_health,
                    MIN(health_score) as min_health,
                    MAX(health_score) as max_health,
                    SUM(CASE WHEN is_anomaly = 1 THEN 1 ELSE 0 END) as anomaly_count,
                    SUM(CASE WHEN fault_prediction > 0 THEN 1 ELSE 0 END) as fault_count
                FROM predictions
                WHERE timestamp > datetime('now', '-24 hours')
            """
            summary = pd.read_sql(summary_query, conn)
            if summary.empty or summary['total_predictions'][0] == 0:
                conn.close()
                return "No Predictions available in the last 24 hours"

            result = f"""
    Machine Health Summary (Last 24 hours):
    - Total Predictions: {int(summary['total_predictions'][0])}
    - Average Health Score: {summary['avg_health'][0]:.1f}/100
    - Health Score Range: {summary['min_health'][0]:.1f} to {summary['max_health'][0]:.1f}
    - Anomalies Detected: {int(summary['anomaly_count'][0])}
    - Faults Detected: {int(summary['fault_count'][0])}

    Status: {"ATTENTION NEEDED" if summary['avg_health'][0] < 70 else "HEALTHY"}
            """
            conn.close()
            return result.strip()
        except Exception as e:
            return f"Error retrieving status: {str(e)}"

    def get_high_risk_machine(query: str = "") -> str:
        """
        Get list of machines with high risk or critical status
        """
        try:
            conn = get_db_connection()
            query_sql = """
                SELECT 
                    machine_id,
                    health_score,
                    risk_classification,
                    fault_prediction,
                    timestamp,
                    vibration,
                    temperature,
                    pressure
                FROM predictions
                WHERE health_score < 60
                ORDER BY health_score ASC
                LIMIT 10
            """
            df = pd.read_sql(query_sql, conn)
            conn.close()

            if df.empty:
                return "No high risk machines detected"

            result = f"High Risk Machines ({len(df)} found):\n\n"
            for idx, row in df.iterrows():
                fault_label = ['Normal', 'Fault', 'Critical'][int(row['fault_prediction'])]
                result += f"""
    Machine: {row['machine_id']}
    - Health Score: {row['health_score']:.1f}/100
    - Risk Level: {row['risk_classification']}
    - Fault Status: {fault_label}
    - Last Reading: {row['timestamp']}
    - Sensors: Temp={row['temperature']:.1f}°C, Vib={row['vibration']:.2f}mm/s, Press={row['pressure']:.2f}bar

    """
            return result.strip()
        except Exception as e:
            return f"Error retrieving high risk machines: {str(e)}"

    def get_anomaly_report(query: str = "") -> str:
        """
        Get recent anomaly detections
        """
        try:
            conn = get_db_connection()
            query_sql = """
                SELECT 
                    machine_id,
                    vibration,
                    temperature,
                    pressure,
                    health_score,
                    timestamp,
                    anomaly_score
                FROM predictions
                WHERE is_anomaly = 1
                ORDER BY timestamp DESC
                LIMIT 15
            """
            df = pd.read_sql_query(query_sql, conn)
            conn.close()

            if df.empty:
                return "No anomalies detected"

            result = f"Recent Anomalies ({len(df)} found):\n\n"
            for idx, row in df.iterrows():
                result += f"""
    Machine: {row['machine_id']} at {row['timestamp']}
    - Temperature: {row['temperature']:.1f}°C
    - Vibration: {row['vibration']:.2f}mm/s
    - Pressure: {row['pressure']:.2f}bar
    - Health Score: {row['health_score']:.1f}/100
    - Anomaly Score: {row['anomaly_score']:.3f}

    """
            return result.strip()
        except Exception as e:
            return f"Error retrieving anomalies: {str(e)}"

    def predict_maintenance_needs(query: str = "") -> str:
        """Predicts which machines need maintenance"""
        try:
            conn = get_db_connection()
            query_sql = """
                SELECT 
                    machine_id,
                    AVG(health_score) as avg_health,
                    AVG(fault_probability) as avg_fault_prob,
                    COUNT(*) as prediction_count,
                    MIN(health_score) as min_health,
                    SUM(CASE WHEN is_anomaly = 1 THEN 1 ELSE 0 END) as anomaly_count
                FROM predictions
                WHERE timestamp > datetime('now', '-7 days')
                GROUP BY machine_id
                HAVING avg_health < 75
                ORDER BY avg_health ASC
            """
            df = pd.read_sql_query(query_sql, conn)
            conn.close()

            if df.empty:
                return "No maintenance needed - all machines healthy"

            result = f"MAINTENANCE RECOMMENDATIONS ({len(df)} machines):\n\n"
            for idx, row in df.iterrows():
                if row['avg_health'] < 40:
                    urgency = "URGENT - Schedule within 24 hours"
                elif row['avg_health'] < 55:
                    urgency = "HIGH PRIORITY - Schedule within 3 days"
                elif row['avg_health'] < 70:
                    urgency = "MEDIUM - Schedule within 1 week"
                else:
                    urgency = "LOW - Monitor closely"

                result += f"""
    Machine: {row['machine_id']}
    - Priority: {urgency}
    - Average Health: {row['avg_health']:.1f}/100
    - Fault Probability: {row['avg_fault_prob']:.1%}
    - Anomalies (7 days): {int(row['anomaly_count'])}
    - Predictions Analyzed: {int(row['prediction_count'])}

    """
            return result.strip()
        except Exception as e:
            return f"Error predicting maintenance: {str(e)}"

    def get_sensor_trends(query: str = "") -> str:
        """Get sensor reading trends for analysis"""
        try:
            conn = get_db_connection()
            query_sql = """
                SELECT 
                    AVG(temperature) as avg_temp,
                    MAX(temperature) as max_temp,
                    AVG(vibration) as avg_vib,
                    MAX(vibration) as max_vib,
                    AVG(pressure) as avg_press,
                    MAX(pressure) as max_press,
                    COUNT(*) as reading_count
                FROM predictions
                WHERE timestamp > datetime('now', '-24 hours')
            """
            df = pd.read_sql_query(query_sql, conn)
            conn.close()

            result = f"""
    Sensor Trends (Last 24 hours):

    Temperature:
    - Average: {df['avg_temp'][0]:.1f}°C
    - Peak: {df['max_temp'][0]:.1f}°C
    - Status: {"High" if df['avg_temp'][0] > 100 else "Normal"}

    Vibration:
    - Average: {df['avg_vib'][0]:.3f}mm/s
    - Peak: {df['max_vib'][0]:.3f}mm/s
    - Status: {"High" if df['avg_vib'][0] > 0.7 else "Normal"}

    Pressure:
    - Average: {df['avg_press'][0]:.2f}bar
    - Peak: {df['max_press'][0]:.2f}bar
    - Status: {"Abnormal" if abs(df['avg_press'][0] - 8) > 1 else "Normal"}

    Total Readings: {int(df['reading_count'][0])}
            """
            return result.strip()
        except Exception as e:
            return f"Error getting sensor trends: {str(e)}"
