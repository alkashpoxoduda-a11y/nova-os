"""
Unit tests for NOVA Sentinel, Files, Hub, Monitor, and Diagnostics
"""

import unittest
import tempfile
from pathlib import Path
from nova_os.sentinel import NovaSentinel
from nova_os.files import NovaFilesExplorer
from nova_os.hub import NovaHubAppStore
from nova_os.monitor import NovaSystemMonitor
from nova_os.diagnostics import NovaDiagnosticsEngine

class TestModules(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.sentinel = NovaSentinel()
        self.files = NovaFilesExplorer(start_dir=self.tmp_dir.name)
        self.hub = NovaHubAppStore()
        self.monitor = NovaSystemMonitor()
        self.diag = NovaDiagnosticsEngine()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_sentinel_status(self):
        status = self.sentinel.get_protection_status()
        self.assertIn("status", status)

    def test_files_create_and_delete(self):
        c_res = self.files.create_directory("TestFolder")
        self.assertTrue(c_res["success"])

        items = self.files.list_directory()
        self.assertEqual(len(items), 1)

        d_res = self.files.delete_item(str(Path(self.tmp_dir.name) / "TestFolder"))
        self.assertTrue(d_res["success"])

    def test_hub_search(self):
        pkgs = self.hub.search_packages("firefox")
        self.assertTrue(len(pkgs) > 0)

    def test_monitor_stats(self):
        stats = self.monitor.get_system_resources()
        self.assertIn("ram_percent", stats)
        self.assertIn("disk_percent", stats)

    def test_diagnostics(self):
        res = self.diag.run_full_diagnostics()
        self.assertIn("overall_health", res)

if __name__ == "__main__":
    unittest.main()
