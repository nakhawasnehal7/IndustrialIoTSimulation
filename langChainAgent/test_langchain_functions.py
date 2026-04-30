import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from langChainAgent.LangChainFunctions import LangChainFunctions


class TestLangChainFunctions(unittest.TestCase):

    @patch("langChainAgent.LangChainFunctions.pd.read_sql")
    @patch("langChainAgent.LangChainFunctions.get_db_connection")
    def test_get_health_status_success(self, mock_conn, mock_read_sql):
        mock_read_sql.return_value = pd.DataFrame({
            "total_predictions": [10],
            "avg_health": [75],
            "min_health": [60],
            "max_health": [90],
            "anomaly_count": [2],
            "fault_count": [1]
        })

        result = LangChainFunctions.get_health_status()

        self.assertIn("Machine Health Summary", result)
        self.assertIn("Total Predictions: 10", result)

    @patch("langChainAgent.LangChainFunctions.pd.read_sql")
    @patch("langChainAgent.LangChainFunctions.get_db_connection")
    def test_predict_maintenance(self, mock_read_sql_query, mock_conn):
        mock_read_sql_query.return_value = pd.DataFrame({
            "machine_id": ["M1"],
            "avg_health": [35],
            "avg_fault_prob": [0.8],
            "prediction_count": [10],
            "min_health": [30],
            "anomaly_count": [3]
        })

        result = LangChainFunctions.predict_maintenance_needs()

        self.assertIn(" ", result)
        self.assertIn(" ", result)

    @patch("langChainAgent.LangChainFunctions.pd.read_sql")
    @patch("langChainAgent.LangChainFunctions.get_db_connection")
    def test_sensor_trends(self, mock_read_sql_query, mock_conn):
        mock_read_sql_query.return_value = MagicMock()

        df = pd.DataFrame({
            "avg_temp": [90],
            "max_temp": [120],
            "avg_vib": [0.5],
            "max_vib": [1.0],
            "avg_press": [8],
            "max_press": [10],
            "reading_count": [100]
        })

        mock_read_sql_query.return_value = df

        result = LangChainFunctions.get_sensor_trends()

        assert result is not None
        assert " " in result


if __name__ == "__main__":
    unittest.main()
