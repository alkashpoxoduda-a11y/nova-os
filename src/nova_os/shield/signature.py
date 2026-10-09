"""
NOVA Shield - 1. Signature Scanner
Checks files against ClamAV daemon/cli or local threat signature database.
"""

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Dict, Any

# Embedded sample signatures database for offline/fallback testing (EICAR, known malicious hashes)
KNOWN_SIGNATURE_HASHES = {
    # EICAR standard test file SHA256
    "131f95c51cc819465fa1797f6ccacf9d494aaaff46fa3eac73ae63ff5fe16346": "EICAR-Test-File (Standard Antivirus Test)",
    "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f": "Trojan.Linux.Generic.A",
}

KNOWN_SIGNATURE_STRINGS = [
    (b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*", "EICAR-Test-File (Standard Antivirus Test)"),
    (b"MALWARE_TEST_SIGNATURE_NOVA_SHIELD", "Test.Threat.NovaShield")
]


class SignatureScanner:
    def __init__(self, use_clamav: bool = True):
        self.use_clamav = use_clamav

    def scan(self, filepath: str) -> Dict[str, Any]:
        path = Path(filepath)
        if not path.exists():
            return {
                "status": "Failed",
                "details": "File does not exist",
                "threat_name": None
            }

        # Check clamscan command if available and requested
        if self.use_clamav:
            try:
                res = subprocess.run(["clamscan", "--no-summary", str(path)], capture_output=True, text=True, timeout=10)
                if res.returncode == 1:
                    threat_info = res.stdout.strip().split(":")[-1].replace("FOUND", "").strip()
                    return {
                        "status": "Threat Detected",
                        "details": f"ClamAV detected threat: {threat_info}",
                        "threat_name": threat_info or "ClamAV.Threat"
                    }
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        # Fallback / Built-in local signature check
        try:
            with open(path, "rb") as f:
                content = f.read()

            sha256 = hashlib.sha256(content).hexdigest()
            if sha256 in KNOWN_SIGNATURE_HASHES:
                threat = KNOWN_SIGNATURE_HASHES[sha256]
                return {
                    "status": "Threat Detected",
                    "details": f"Signature match in database: {threat}",
                    "threat_name": threat
                }

            for sig_str, threat_name in KNOWN_SIGNATURE_STRINGS:
                if sig_str in content:
                    return {
                        "status": "Threat Detected",
                        "details": f"Pattern match in database: {threat_name}",
                        "threat_name": threat_name
                    }

            return {
                "status": "Clean",
                "details": "No known signature matched in database",
                "threat_name": None
            }
        except Exception as e:
            return {
                "status": "Failed",
                "details": f"Error reading file for signature scan: {str(e)}",
                "threat_name": None
            }
