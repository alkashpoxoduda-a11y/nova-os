"""
Unit tests for NOVA Welcome Wizard
"""

import unittest
import tempfile
from pathlib import Path
from nova_os.welcome import NovaWelcomeEngine

class TestWelcome(unittest.TestCase):
    def setUp(self):
        self.welcome = NovaWelcomeEngine()

    def test_language_selection(self):
        res1 = self.welcome.set_language("ru")
        self.assertTrue(res1["success"])
        res2 = self.welcome.set_language("en")
        self.assertTrue(res2["success"])

    def test_user_validation_blocks_debian_user(self):
        val1 = self.welcome.validate_user_account("Debian Live User", "debian", "1234")
        self.assertFalse(val1["valid"])
        self.assertIn("debian", val1["errors"][0])

        val2 = self.welcome.validate_user_account("Алексей", "alexey", "secret123")
        self.assertTrue(val2["valid"])

    def test_create_and_finish(self):
        res_user = self.welcome.create_user_account("Алексей", "alexey", "pass123")
        self.assertTrue(res_user["success"])

if __name__ == "__main__":
    unittest.main()
