"""
NOVA Shield Unified 5-Level Security Analysis Engine, Quarantine Manager, and UI Scanner Dialog Integrator
"""

import os
import shutil
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

from nova_os.config import QUARANTINE_DIR, DATA_DIR
from nova_os.shield.signature import SignatureScanner
from nova_os.shield.static_analysis import StaticAnalyzer
from nova_os.shield.behavior import BehaviorAnalyzer
from nova_os.shield.reputation import ReputationChecker
from nova_os.shield.heuristic import HeuristicAnalyzer


class QuarantineManager:
    def __init__(self, quarantine_dir: Path = QUARANTINE_DIR):
        self.quarantine_dir = quarantine_dir
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.quarantine_dir / "quarantine_manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        if self.meta_file.exists():
            try:
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_manifest(self):
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, ensure_ascii=False, indent=2)

    def quarantine_file(self, filepath: str, threat_info: Dict[str, Any]) -> Dict[str, Any]:
        src = Path(filepath)
        if not src.exists():
            return {"success": False, "message": "Source file does not exist"}

        with open(src, "rb") as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()

        q_id = f"q_{int(time.time())}_{sha256[:8]}"
        q_path = self.quarantine_dir / q_id

        try:
            shutil.move(str(src), str(q_path))
            q_path.chmod(0o000)  # Remove read/write/execute permissions to isolate file

            self.manifest[q_id] = {
                "id": q_id,
                "original_path": str(src),
                "quarantined_path": str(q_path),
                "timestamp": time.time(),
                "sha256": sha256,
                "threat_info": threat_info
            }
            self._save_manifest()
            return {"success": True, "quarantine_id": q_id, "message": "File quarantined and isolated successfully"}
        except Exception as e:
            return {"success": False, "message": f"Quarantine failed: {str(e)}"}

    def restore_file(self, q_id: str) -> Dict[str, Any]:
        if q_id not in self.manifest:
            return {"success": False, "message": "Quarantine ID not found"}

        item = self.manifest[q_id]
        q_path = Path(item["quarantined_path"])
        orig_path = Path(item["original_path"])

        if not q_path.exists():
            return {"success": False, "message": "Quarantined file artifact missing"}

        try:
            q_path.chmod(0o644)
            orig_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(q_path), str(orig_path))
            del self.manifest[q_id]
            self._save_manifest()
            return {"success": True, "message": "File restored to original path successfully"}
        except Exception as e:
            return {"success": False, "message": f"Restore failed: {str(e)}"}

    def list_quarantined(self) -> List[Dict[str, Any]]:
        return list(self.manifest.values())


class NovaShieldEngine:
    def __init__(self):
        self.signature_scanner = SignatureScanner()
        self.static_analyzer = StaticAnalyzer()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.reputation_checker = ReputationChecker()
        self.heuristic_analyzer = HeuristicAnalyzer()
        self.quarantine_manager = QuarantineManager()

    def scan_file(self, filepath: str) -> Dict[str, Any]:
        path = Path(filepath)
        if not path.exists():
            return {
                "filepath": filepath,
                "exists": False,
                "overall_status": "Failed",
                "summary": "File not found",
                "modules": {}
            }

        modules = {
            "signature": self.signature_scanner.scan(filepath),
            "static": self.static_analyzer.scan(filepath),
            "behavior": self.behavior_analyzer.scan(filepath),
            "reputation": self.reputation_checker.scan(filepath),
            "heuristic": self.heuristic_analyzer.scan(filepath)
        }

        # Calculate overall status
        threat_count = sum(1 for m in modules.values() if m.get("status") == "Threat Detected")
        suspicious_count = sum(1 for m in modules.values() if m.get("status") == "Suspicious")

        if threat_count == 5:
            overall_status = "Critical Threat"
            warning_msg = "Все 5 модулей обнаружили признаки вредоносного файла."
        elif threat_count > 0:
            overall_status = "Threat Detected"
            warning_msg = "NOVA Shield обнаружил потенциально опасный файл. Рекомендуем не открывать его до завершения анализа."
        elif suspicious_count > 0 and (path.suffix in [".exe", ".sh", ".py", ".bin", ".elf", ".so"]):
            overall_status = "Suspicious"
            warning_msg = "Файл имеет неоднозначные характеристики или неизвестное происхождение."
        else:
            overall_status = "Clean"
            warning_msg = "Файл успешно прошёл проверку безопасности NOVA Shield."

        return {
            "filepath": str(path.resolve()),
            "exists": True,
            "overall_status": overall_status,
            "threat_count": threat_count,
            "suspicious_count": suspicious_count,
            "warning_message": warning_msg,
            "modules": modules,
            "timestamp": time.time()
        }
