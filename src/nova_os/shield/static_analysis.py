"""
NOVA Shield - 2. Static Analyzer
Analyzes binary structure, headers, embedded scripts, suspicious imports/strings without executing.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List

SUSPICIOUS_STRINGS = [
    r"eval\(base64_decode",
    r"/bin/sh -i",
    r"rm -rf /",
    r"chmod 777",
    r"curl http.*\| sh",
    r"wget http.*\| bash",
    r"keylogger",
    r"reverse_shell",
    r"python -c 'import socket",
]


class StaticAnalyzer:
    def scan(self, filepath: str) -> Dict[str, Any]:
        path = Path(filepath)
        if not path.exists():
            return {"status": "Failed", "details": "File does not exist", "flags": []}

        if path.is_dir():
            return {"status": "Not Supported", "details": "Directory static scan required recursive processing", "flags": []}

        flags: List[str] = []
        try:
            file_size = path.stat().st_size
            if file_size > 100 * 1024 * 1024:  # > 100MB
                flags.append("Very large executable/binary")

            with open(path, "rb") as f:
                header = f.read(16)
                f.seek(0)
                content = f.read(5 * 1024 * 1024)  # Read up to 5MB for string inspection

            # Header detection
            is_elf = header.startswith(b"\x7fELF")
            is_pe = header.startswith(b"MZ")
            is_script = content.startswith(b"#!") or path.suffix in [".sh", ".py", ".pl", ".rb", ".js"]

            # Inspect strings in text/script or binary
            text_content = content.decode("ascii", errors="ignore")
            for pattern in SUSPICIOUS_STRINGS:
                if re.search(pattern, text_content, re.IGNORECASE):
                    flags.append(f"Suspicious code pattern detected: {pattern}")

            # Check double extensions (e.g. invoice.pdf.exe / setup.sh.desktop)
            if len(path.suffixes) > 1:
                flags.append(f"Multiple file extensions detected: {path.name}")

            if is_pe:
                flags.append("Windows PE Executable format on Linux host")

            if flags:
                return {
                    "status": "Suspicious" if len(flags) == 1 else "Threat Detected",
                    "details": f"Static analysis flagged {len(flags)} issues",
                    "flags": flags
                }

            return {
                "status": "Clean",
                "details": "Static analysis completed with no suspicious indicators",
                "flags": []
            }
        except Exception as e:
            return {
                "status": "Failed",
                "details": f"Static analysis error: {str(e)}",
                "flags": []
            }
