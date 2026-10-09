"""
Unit tests for NOVA AI Assistant
"""

import unittest
import tempfile
from pathlib import Path
from nova_os.ai_assistant import NovaAIAssistant

class TestNovaAI(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.ai = NovaAIAssistant(language="ru", user_name="Алексей")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_greetings(self):
        g1 = self.ai.get_greeting(headphone_event=False)
        self.assertIn("Алексей", g1)
        self.assertIn("NOVA OS", g1)

        g2 = self.ai.get_greeting(headphone_event=True)
        self.assertIn("Алексей", g2)

    def test_query_processing(self):
        res1 = self.ai.process_query("Открой Терминал")
        self.assertEqual(res1["action"], "open_app")
        self.assertEqual(res1["target"], "Терминал")

        res2 = self.ai.process_query("Покажи ошибки в логах")
        self.assertEqual(res2["action"], "analyze_logs")

    def test_file_editing_with_permission_and_undo(self):
        target_file = Path(self.tmp_dir.name) / "config.ini"
        target_file.write_text("initial=true\n")

        # Request change requiring permission
        res = self.ai.create_or_edit_file(str(target_file), "initial=false\nnew_key=1", require_approval=True)
        self.assertTrue(res["requires_permission"])

        # Approve change
        app_res = self.ai.approve_and_apply_file_change(str(target_file), "initial=false\nnew_key=1")
        self.assertEqual(app_res["status"], "Success")
        self.assertIn("new_key=1", target_file.read_text())

        # Test Undo
        undo_res = self.ai.undo_file_change(str(target_file))
        self.assertEqual(undo_res["status"], "Success")
        self.assertEqual(target_file.read_text(), "initial=true\n")

if __name__ == "__main__":
    unittest.main()
