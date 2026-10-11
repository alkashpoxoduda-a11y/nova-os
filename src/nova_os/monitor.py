"""
NOVA Monitor - Task Manager & System Resource Monitor
Reports CPU usage, RAM stats, Disk usage, Network metrics, and process lists.
"""

import os
import shutil
import subprocess
from typing import Dict, Any, List, Optional

class NovaSystemMonitor:
    def get_system_resources(self) -> Dict[str, Any]:
        """Returns real CPU, RAM, and Disk metrics."""
        # RAM stats
        mem_total_mb = 0
        mem_available_mb = 0
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        mem_total_mb = int(line.split()[1]) // 1024
                    elif line.startswith("MemAvailable:"):
                        mem_available_mb = int(line.split()[1]) // 1024
        except Exception:
            pass

        mem_used_mb = max(0, mem_total_mb - mem_available_mb)
        mem_percent = round((mem_used_mb / mem_total_mb * 100), 1) if mem_total_mb > 0 else 0.0

        # Disk stats
        disk_usage = shutil.disk_usage("/")
        disk_total_gb = round(disk_usage.total / (1024**3), 1)
        disk_used_gb = round(disk_usage.used / (1024**3), 1)
        disk_percent = round((disk_usage.used / disk_usage.total * 100), 1) if disk_usage.total > 0 else 0.0

        # Process count
        process_count = len([p for p in os.listdir("/proc") if p.isdigit()])

        return {
            "ram_total_mb": mem_total_mb,
            "ram_used_mb": mem_used_mb,
            "ram_percent": mem_percent,
            "disk_total_gb": disk_total_gb,
            "disk_used_gb": disk_used_gb,
            "disk_percent": disk_percent,
            "process_count": process_count
        }

    def list_active_processes(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Lists active running processes using ps."""
        processes = []
        try:
            res = subprocess.run(["ps", "-eo", "pid,user,%cpu,%mem,comm", "--sort=-%cpu"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                lines = res.stdout.strip().split("\n")[1:limit+1]
                for line in lines:
                    parts = line.split(None, 4)
                    if len(parts) >= 5:
                        processes.append({
                            "pid": parts[0],
                            "user": parts[1],
                            "cpu_percent": parts[2],
                            "mem_percent": parts[3],
                            "command": parts[4]
                        })
        except Exception:
            pass
        return processes
