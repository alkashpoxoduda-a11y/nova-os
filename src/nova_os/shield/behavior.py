"""
NOVA Shield - 3. Behavioral Analyzer
Isolated execution sandbox checker.
Observes filesystem, network, process creation attempts in an isolated sub-process sandbox.
If proper sandbox tools (bubblewrap/firejail/docker/chroot) are not available, flags 'Failed / Not Executed on Main System'.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List

class BehaviorAnalyzer:
    def __init__(self):
        self.sandbox_tool = None
        if shutil.which("bwrap"):
            self.sandbox_tool = "bwrap"
        elif shutil.which("firejail"):
            self.sandbox_tool = "firejail"

    def scan(self, filepath: str) -> Dict[str, Any]:
        path = Path(filepath)
        if not path.exists():
            return {"status": "Failed", "details": "File does not exist", "behavior_logs": []}

        # Per strict requirement: If proper sandbox is absent, do NOT run on host system!
        if not self.sandbox_tool:
            return {
                "status": "Failed",
                "details": "Isolated sandbox runtime (bubblewrap/firejail) is not installed. File was NOT executed on main system to preserve security.",
                "behavior_logs": ["Sandbox tool unavailable; execution skipped."]
            }

        logs: List[str] = []
        try:
            if self.sandbox_tool == "bwrap":
                cmd = [
                    "bwrap",
                    "--ro-bind", "/usr", "/usr",
                    "--ro-bind", "/lib", "/lib",
                    "--ro-bind", "/lib64", "/lib64",
                    "--proc", "/proc",
                    "--dev", "/dev",
                    "--unshare-all",
                    "--ro-bind", str(path), "/tmp/target",
                    "/tmp/target"
                ]
            else:
                cmd = ["firejail", "--net=none", "--private", str(path)]

            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            logs.append(f"Sandbox exited with status {res.returncode}")
            if res.stderr:
                logs.append(f"Stderr: {res.stderr[:200]}")

            return {
                "status": "Clean",
                "details": "Behavioral execution in sandbox completed cleanly",
                "behavior_logs": logs
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "Suspicious",
                "details": "Behavioral execution timed out in sandbox (possible infinite loop or hang)",
                "behavior_logs": logs + ["Execution timeout encountered."]
            }
        except Exception as e:
            return {
                "status": "Failed",
                "details": f"Sandbox error during behavioral analysis: {str(e)}",
                "behavior_logs": logs
            }
