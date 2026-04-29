from datetime import datetime

import pandas as pd

from applicationUtility import ApplicationUtility, load_models


class PredictionFunction:
    @staticmethod
    def calculate_health_score(vibration, temperature, pressure, fault_prob, anomaly_score):
        """
        Calculate machine health score
        :param temperature: measure the temperature value : float
        :param pressure: pressure value : float
        :param fault_prob: fault probability 1 or 0
        :param anomaly_score: binary value 0 or 1
        :return:
        """

        vibration_norm = max(0, 100 - (vibration / 1.0) * 100)
        temp_norm = max(0, 100 - (temperature / 150) * 100)
        pressure_norm = max(0, 100 - abs(pressure - 8) / 2 * 100)
        fault_contrib = (1 - fault_prob) * 100
        anomaly_contrib = min(100, max(0, (anomaly_score + 0.5) * 100))

        health_score = (
                vibration_norm * 0.25 + temp_norm * 0.25 +
                pressure_norm * 0.20 + fault_contrib * 0.20 +
                anomaly_contrib * 0.10
        )
        return max(0, min(100, health_score))

    @staticmethod
    def make_prediction(vibration, temperature, pressure, rms_vibration, mean_temp):
        """
        Make real-time prediction
        :param temperature: measure the temperature value : float
        :param pressure: pressure value : float
        :param rms_vibration: rms vibration : float
        :param mean_temp: f mean temperature float value
        :return: array of the prediction
        """

        rf_model, iso_forest, scaler = load_models()

        if rf_model is None or iso_forest is None or scaler is None:
            return None
        print("Snehal make_predictionmake_predictionmake_predictionmake_predictionmake_predictionmake_predictionmake_predictionmake_predictionmake_predictionmake_predictionmake_predictionmake_prediction")
        #Prepare input
        #try:
        input_data = pd.DataFrame([[vibration, temperature, pressure, rms_vibration, mean_temp]],
                                      columns=['vibration', 'temperature', 'pressure', 'rms_vibration', 'mean_temp'])

        # Scale features
        input_scaled = scaler.transform(input_data)

        # Random Forest prediction
        fault_pred = rf_model.predict(input_scaled)[0]
        fault_proba = rf_model.predict_proba(input_scaled)[0]

        # Isolation Forest anomaly detection
        anomaly_pred = iso_forest.predict(input_scaled)[0]
        anomaly_score = iso_forest.score_samples(input_scaled)[0]

        # Calculate health score
        max_fault_prob = max(fault_proba[1], fault_proba[2]) if len(fault_proba) > 2 else fault_proba[1]
        health_score = PredictionFunction.calculate_health_score(vibration, temperature, pressure, max_fault_prob,
                                                                     anomaly_score)
        risk_level = ApplicationUtility.classify_risk(health_score)
        # except Exception as e:
        #     # st.error(f"Failed at step above: {type(e).__name__}: {e}")
        #     import traceback
        #     # st.code(traceback.format_exc())
        #     return None

        return {
            'fault_prediction': int(fault_pred),
            'fault_label': ['Normal', 'Fault', 'Critical'][int(fault_pred)] if int(fault_pred) < 3 else 'Unknown',
            'fault_probability': {
                'normal': float(fault_proba[0]),
                'fault': float(fault_proba[1]) if len(fault_proba) > 1 else 0.0,
                'critical': float(fault_proba[2]) if len(fault_proba) > 2 else 0.0
            },
            'is_anomaly': bool(anomaly_pred == -1),
            'anomaly_score': float(anomaly_score),
            'health_score': float(health_score),
            'risk_classification': risk_level
        }

    @staticmethod
    def save_prediction_to_db(sensor_data, prediction, machine_id='MACHINE_001'):
        """
        Save the prediction data
        :param prediction:  prediction values
        :param machine_id:  Machine ID
        :return:
        """
        conn = ApplicationUtility.get_db_connection()
        if conn is None:
            return False

        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO predictions (
                    timestamp, machine_id, vibration, temperature, pressure,
                    rms_vibration, mean_temp, fault_prediction, fault_probability,
                    health_score, risk_classification, is_anomaly
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                machine_id,
                sensor_data['vibration'],
                sensor_data['temperature'],
                sensor_data['pressure'],
                sensor_data['rms_vibration'],
                sensor_data['mean_temp'],
                prediction['fault_prediction'],
                prediction['fault_probability']['fault'],
                prediction['health_score'],
                prediction['risk_classification'],
                prediction['is_anomaly']
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            # st.error(f"Error saving to database: {e}")
            conn.close()
            return False
