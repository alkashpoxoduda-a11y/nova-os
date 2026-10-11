"""
Unit tests for NOVA Welcome Wizard with optional password and TTS greeting
"""

import unittest
from nova_os.welcome import NovaWelcomeEngine

class TestWelcome(unittest.TestCase):
    def setUp(self):
        self.welcome = NovaWelcomeEngine()

    def test_language_selection_and_greeting(self):
        res1 = self.welcome.set_language("ru")
        self.assertTrue(res1["success"])
        self.assertIn("Здравствуйте", res1["greeting_spoken"])

        res2 = self.welcome.set_language("en")
        self.assertTrue(res2["success"])
        self.assertIn("Hello", res2["greeting_spoken"])

    def test_optional_empty_password(self):
        # Empty password is valid!
        val_empty = self.welcome.validate_user_account("Алексей", "alexey", password="")
        self.assertTrue(val_empty["valid"])

        res_create = self.welcome.create_user_account("Алексей", "alexey", password="")
        self.assertTrue(res_create["success"])

    def test_user_validation_blocks_debian_user(self):
        val1 = self.welcome.validate_user_account("Debian Live User", "debian", "1234")
        self.assertFalse(val1["valid"])
        self.assertIn("debian", val1["errors"][0])

if __name__ == "__main__":
    unittest.main()
