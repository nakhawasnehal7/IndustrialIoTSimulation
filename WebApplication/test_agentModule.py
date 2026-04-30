import unittest
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

import WebApplication.agentModule as am


class TestAgentModule(unittest.TestCase):

    def test_is_agent_available_returns_bool(self):
        result = am.is_agent_available()
        self.assertIsInstance(result, bool)

    def test_get_agent_status(self):
        status = am.get_agent_status()
        self.assertIn("available", status)

    def test_run_agent_query_empty(self):
        self.assertEqual(am.run_agent_query(""), "Please enter a valid question.")


if __name__ == "__main__":
    unittest.main()
