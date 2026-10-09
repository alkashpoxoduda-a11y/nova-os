"""
Unit tests for Profiles, Control Center, and Recovery System
"""

import unittest
from nova_os.profiles import ProfileManager
from nova_os.control_center import NovaControlCenter, NovaRecoverySystem

class TestProfilesAndControlCenter(unittest.TestCase):
    def setUp(self):
        self.pm = ProfileManager()
        self.cc = NovaControlCenter()
        self.rec = NovaRecoverySystem()

    def test_profile_switching(self):
        res1 = self.pm.apply_profile("nova-lite")
        self.assertTrue(res1["success"])
        self.assertEqual(self.pm.current_profile, "nova-lite")
        self.assertTrue(len(res1["actions_taken"]) > 0)

        res2 = self.pm.apply_profile("nova-gaming")
        self.assertTrue(res2["success"])
        self.assertEqual(self.pm.current_profile, "nova-gaming")

        res3 = self.pm.apply_profile("nova-dev")
        self.assertTrue(res3["success"])

        res4 = self.pm.apply_profile("invalid-profile")
        self.assertFalse(res4["success"])

    def test_control_center_status(self):
        status = self.cc.get_system_status()
        self.assertEqual(status["os_name"], "NOVA OS")
        self.assertEqual(status["version"], "1.0.0")

    def test_recovery_diagnostics(self):
        diag = self.rec.run_diagnostics()
        self.assertTrue(diag["disk_access"])
        self.assertEqual(diag["status"], "Healthy")

        restore = self.rec.restore_system_settings()
        self.assertTrue(restore["success"])

if __name__ == "__main__":
    unittest.main()
