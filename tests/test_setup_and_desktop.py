"""
Unit tests for NOVA Setup Engine and NOVA Desktop Shell
"""

import unittest
import os
import shutil
from pathlib import Path
from nova_os.setup_engine import SetupEngine
from nova_os.desktop import NovaDesktopShell, AppLauncher, NotificationCenter, NovaFileManager
from nova_os.i18n import get_text

class TestSetupEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SetupEngine()

    def test_language_selection(self):
        self.assertTrue(self.engine.set_language("en"))
        self.assertEqual(self.engine.state["language"], "en")
        self.assertFalse(self.engine.set_language("invalid_lang"))

    def test_user_validation(self):
        # Invalid username
        res = self.engine.validate_user("Invalid Name!", "123", "Test User")
        self.assertFalse(res["valid"])

        # Valid user
        res = self.engine.validate_user("jules", "secret123", "Jules Engineer")
        self.assertTrue(res["valid"])

    def test_profile_selection(self):
        self.assertTrue(self.engine.set_profile("nova-gaming"))
        self.assertEqual(self.engine.state["profile"], "nova-gaming")
        self.assertFalse(self.engine.set_profile("nonexistent"))

    def test_i18n(self):
        ru_text = get_text("welcome_title", "ru")
        en_text = get_text("welcome_title", "en")
        uz_text = get_text("welcome_title", "uz")
        self.assertIn("NOVA OS", ru_text)
        self.assertIn("NOVA OS", en_text)
        self.assertIn("NOVA OS", uz_text)

class TestNovaDesktop(unittest.TestCase):
    def setUp(self):
        self.shell = NovaDesktopShell()

    def test_app_launcher_search(self):
        launcher = AppLauncher()
        results = launcher.search_apps("terminal")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["id"], "nova-terminal")

    def test_notifications(self):
        nc = NotificationCenter()
        nc.add_notification("Test Title", "Test Message", "info")
        self.assertEqual(len(nc.get_all()), 1)
        nc.clear()
        self.assertEqual(len(nc.get_all()), 0)

    def test_virtual_desktops(self):
        self.assertTrue(self.shell.desktop_manager.switch_desktop(2))
        self.assertEqual(self.shell.desktop_manager.current_desktop, 2)
        self.assertFalse(self.shell.desktop_manager.switch_desktop(10))

    def test_profile_switch(self):
        self.assertTrue(self.shell.switch_profile("nova-dev"))
        self.assertEqual(self.shell.active_profile, "nova-dev")

if __name__ == "__main__":
    unittest.main()
