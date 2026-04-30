import unittest
from trainModel.trainUtility import TrainUtility


class TestTrainUtility(unittest.TestCase):

    def test_calculate_health_score_normal_values(self):
        score = TrainUtility.calculate_health_score(
            0.5, 50, 8, 0.2, 0.1
        )
        self.assertTrue(0 <= score <= 100)

    def test_calculate_health_score_perfect(self):
        score = TrainUtility.calculate_health_score(
            0, 0, 8, 0, 0.5
        )
        self.assertGreaterEqual(score, 80)

    def test_calculate_health_score_worst(self):
        score = TrainUtility.calculate_health_score(
            10, 200, 20, 1, -1
        )
        self.assertEqual(score, 0)

    def test_classify_risk(self):
        self.assertEqual(TrainUtility.classify_risk(85), "Low Risk")
        self.assertEqual(TrainUtility.classify_risk(70), "Medium Risk")
        self.assertEqual(TrainUtility.classify_risk(50), "High Risk")
        self.assertEqual(TrainUtility.classify_risk(20), "Critical Risk")


if __name__ == "__main__":
    unittest.main()