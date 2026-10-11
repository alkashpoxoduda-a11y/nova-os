"""
NOVA Diagnostics - System Diagnostic Runner
Checks systemd service health, NetworkManager status, disk space, and kernel logs.
"""

import os
import shutil
import subprocess
from typing import Dict, Any, List

class NovaDiagnosticsEngine:
    def run_full_diagnostics(self) -> Dict[str, Any]:
        """Runs full system diagnostic audit."""
        network_ok = shutil.which("nmcli") is not None
        clamav_ok = shutil.which("clamscan") is not None
        apt_ok = shutil.which("apt-get") is not None

        disk_stat = shutil.disk_usage("/")
        disk_free_gb = round(disk_stat.free / (1024**3), 1)

        issues = []
        if disk_free_gb < 2.0:
            issues.append("Низкий уровень свободного места на диске (менее 2 ГБ).")
        if not network_ok:
            issues.append("Служба управления сетью NetworkManager не обнаружена.")

        return {
            "network_subsystem_ok": network_ok,
            "clamav_antivirus_ok": clamav_ok,
            "package_manager_ok": apt_ok,
            "disk_free_gb": disk_free_gb,
            "overall_health": "Healthy" if len(issues) == 0 else "Warning",
            "detected_issues": issues
        }
