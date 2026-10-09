"""
Unit tests for NOVA Thermal Guard
"""

import unittest
from nova_os.thermal import ThermalGuard

class TestThermalGuard(unittest.TestCase):
    def setUp(self):
        self.guard = ThermalGuard()

    def test_normal_temperature(self):
        res = self.guard.check_system(mock_temps={"cpu": 45.0, "gpu": 50.0})
        self.assertEqual(res["status"], "NORMAL")
        self.assertIsNone(res["voice_message"])

    def test_elevated_temperature(self):
        res = self.guard.check_system(mock_temps={"cpu": 82.0, "gpu": 60.0})
        self.assertEqual(res["status"], "ELEVATED")
        self.assertIn("Повышенная температура", res["ui_message"])
        self.assertIsNone(res["voice_message"])

    def test_dangerous_temperature(self):
        res = self.guard.check_system(mock_temps={"cpu": 92.0})
        self.assertEqual(res["status"], "DANGEROUS")
        self.assertIn("Внимание", res["voice_message"])

    def test_critical_temperature(self):
        res = self.guard.check_system(mock_temps={"cpu": 100.0})
        self.assertEqual(res["status"], "CRITICAL")
        self.assertIn("критической", res["voice_message"])

    def test_sensor_fault_handling(self):
        # Empty temperatures dictionary
        res = self.guard.check_system(mock_temps={})
        self.assertEqual(res["status"], "SENSOR_ERROR")

if __name__ == "__main__":
    unittest.main()
