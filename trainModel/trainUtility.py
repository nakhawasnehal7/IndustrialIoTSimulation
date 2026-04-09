# Author SnehalNakhawa
# Date: 1st April
# Description : TrainUtility utility class for methods used for training the models


class TrainUtility:

    def calculate_health_score(vibration, temperature, pressure, fault_prob, anomaly_score):
        """
        Calculate the health score
        :param temperature:
        :param pressure:
        :param fault_prob:
        :param anomaly_score:
        :return: max health score
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

    def classify_risk(health_score):
        """
        This is the classification based on the health score calculated
        :return: type of risk "Low/Medium/High/Critical"
        """
        if health_score >= 80:
            return "Low Risk"
        elif health_score >= 60:
            return "Medium Risk"
        elif health_score >= 40:
            return "High Risk"
        else:
            return "Critical Risk"
