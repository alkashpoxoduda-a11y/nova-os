"""
Unit tests for NOVA Installer Engine
"""

import unittest
from nova_os.installer import NovaInstallerEngine

class TestInstaller(unittest.TestCase):
    def setUp(self):
        self.installer = NovaInstallerEngine()

    def test_list_disks(self):
        disks = self.installer.list_disks()
        self.assertTrue(len(disks) > 0)
        self.assertIn("device", disks[0])

    def test_select_disk_and_install(self):
        sel_res = self.installer.select_target_disk("/dev/sda")
        self.assertEqual(sel_res["selected_disk"], "/dev/sda")
        self.assertIn("ВНИМАНИЕ", sel_res["warning"])

        inst_res = self.installer.start_installation(dry_run=True)
        self.assertTrue(inst_res["success"])
        self.assertEqual(len(inst_res["steps_completed"]), 7)

if __name__ == "__main__":
    unittest.main()
