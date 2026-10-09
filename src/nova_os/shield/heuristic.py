"""
NOVA Shield - 5. Heuristic Analyzer
Scans for combinations of suspicious traits, obfuscation, atypical autostrain persistence mechanisms, and dangerous script patterns.
"""

import re
from pathlib import Path
from typing import Dict, Any, List

HEURISTIC_RULES = [
    {"id": "H1", "pattern": r"systemctl\s+enable", "score": 2, "desc": "Attempts to enable system service persistence"},
    {"id": "H2", "pattern": r"crontab\s+-l", "score": 2, "desc": "Reads crontab scheduling"},
    {"id": "H3", "pattern": r"/etc/autostart", "score": 3, "desc": "Modifies global autostart directory"},
    {"id": "H4", "pattern": r"base64\s+-d.*\|.*sh", "score": 5, "desc": "Decodes base64 string directly into command shell"},
    {"id": "H5", "pattern": r"LD_PRELOAD", "score": 4, "desc": "Uses LD_PRELOAD shared library injection"},
    {"id": "H6", "pattern": r"ptrace\(PTRACE_TRACEME", "score": 4, "desc": "Anti-debugging check detected"}
]


class HeuristicAnalyzer:
    def scan(self, filepath: str) -> Dict[str, Any]:
        path = Path(filepath)
        if not path.exists():
            return {"status": "Failed", "details": "File does not exist", "heuristic_score": 0, "triggers": []}

        score = 0
        triggers: List[str] = []

        try:
            with open(path, "rb") as f:
                raw_data = f.read(2 * 1024 * 1024)  # 2MB chunk

            text = raw_data.decode("ascii", errors="ignore")

            for rule in HEURISTIC_RULES:
                if re.search(rule["pattern"], text, re.IGNORECASE):
                    score += rule["score"]
                    triggers.append(f"[{rule['id']}] {rule['desc']}")

            if score >= 5:
                status = "Threat Detected"
            elif score >= 2:
                status = "Suspicious"
            else:
                status = "Clean"

            return {
                "status": status,
                "details": f"Heuristic risk score: {score}/10 with {len(triggers)} rule trigger(s)",
                "heuristic_score": score,
                "triggers": triggers
            }
        except Exception as e:
            return {
                "status": "Failed",
                "details": f"Heuristic analysis error: {str(e)}",
                "heuristic_score": 0,
                "triggers": []
            }
