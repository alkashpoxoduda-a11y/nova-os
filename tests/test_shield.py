"""
Unit tests for NOVA Shield 5-level analysis engine and quarantine manager
"""

import unittest
import tempfile
import os
from pathlib import Path
from nova_os.shield import NovaShieldEngine, QuarantineManager

class TestNovaShield(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.engine = NovaShieldEngine()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_clean_file_scan(self):
        clean_file = Path(self.tmp_dir.name) / "hello.txt"
        clean_file.write_text("Hello World NOVA OS clean text file")

        result = self.engine.scan_file(str(clean_file))
        self.assertEqual(result["overall_status"], "Clean")
        self.assertEqual(result["modules"]["signature"]["status"], "Clean")

    def test_eicar_signature_detection(self):
        eicar_file = Path(self.tmp_dir.name) / "eicar.com"
        eicar_file.write_bytes(b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")

        result = self.engine.scan_file(str(eicar_file))
        self.assertIn(result["overall_status"], ["Threat Detected", "Critical Threat"])
        self.assertEqual(result["modules"]["signature"]["status"], "Threat Detected")

    def test_all_5_modules_triggers(self):
        # Construct a file triggering all 5 scanners
        bad_file = Path(self.tmp_dir.name) / "malware.sh.exe"
        bad_content = (
            b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*\n"
            b"eval(base64_decode('test')); systemctl enable evil;\n"
            b"base64 -d | sh; LD_PRELOAD=/tmp/evil.so; ptrace(PTRACE_TRACEME);\n"
        )
        bad_file.write_bytes(bad_content)

        result = self.engine.scan_file(str(bad_file))
        self.assertTrue(result["threat_count"] >= 3)
        self.assertIn("NOVA Shield", result["warning_message"])

    def test_quarantine_and_restore(self):
        test_file = Path(self.tmp_dir.name) / "suspicious.bin"
        test_file.write_text("suspicious payload")

        q_dir = Path(self.tmp_dir.name) / "quarantine"
        qm = QuarantineManager(quarantine_dir=q_dir)

        q_res = qm.quarantine_file(str(test_file), {"threat": "Test.Threat"})
        self.assertTrue(q_res["success"])
        self.assertFalse(test_file.exists())

        q_id = q_res["quarantine_id"]
        r_res = qm.restore_file(q_id)
        self.assertTrue(r_res["success"])
        self.assertTrue(test_file.exists())

if __name__ == "__main__":
    unittest.main()
