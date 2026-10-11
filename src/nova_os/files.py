"""
NOVA Files - Explorer & Storage Device Manager
Handles directory navigation, file copy/move/rename/delete operations, USB drive auto-detection via udisks2,
and storage volume space reporting.
"""

import os
import shutil
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

class NovaFilesExplorer:
    def __init__(self, start_dir: Optional[str] = None):
        self.current_dir = Path(start_dir) if start_dir else Path.home()

    def list_directory(self, target_path: Optional[str] = None) -> List[Dict[str, Any]]:
        dir_path = Path(target_path) if target_path else self.current_dir
        if not dir_path.exists() or not dir_path.is_dir():
            return []

        items = []
        try:
            for item in dir_path.iterdir():
                items.append({
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size_bytes": item.stat().st_size if not item.is_dir() else 0,
                    "path": str(item)
                })
        except PermissionError:
            pass
        return items

    def create_directory(self, dir_name: str) -> Dict[str, Any]:
        target = self.current_dir / dir_name
        try:
            target.mkdir(parents=True, exist_ok=False)
            return {"success": True, "message": f"Папка '{dir_name}' успешно создана."}
        except FileExistsError:
            return {"success": False, "message": f"Папка '{dir_name}' уже существует."}
        except Exception as e:
            return {"success": False, "message": f"Ошибка создания папки: {str(e)}"}

    def copy_item(self, src: str, dest_dir: str) -> Dict[str, Any]:
        src_path = Path(src)
        dest_path = Path(dest_dir) / src_path.name

        if not src_path.exists():
            return {"success": False, "message": "Исходный файл не существует."}

        try:
            if src_path.is_dir():
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)
            return {"success": True, "message": f"Скопировано в {dest_path.name}"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка копирования: {str(e)}"}

    def delete_item(self, target: str) -> Dict[str, Any]:
        path = Path(target)
        if not path.exists():
            return {"success": False, "message": "Файл или папка не существует."}

        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            return {"success": True, "message": f"'{path.name}' успешно удалён."}
        except Exception as e:
            return {"success": False, "message": f"Ошибка удаления: {str(e)}"}

    def list_usb_drives(self) -> List[Dict[str, Any]]:
        """Lists detected external USB storage drives using lsblk/udisks2."""
        drives = []
        try:
            res = subprocess.run(["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MOUNTPOINTS,LABEL,MODEL"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                for dev in data.get("blockdevices", []):
                    for part in dev.get("children", [dev]):
                        mounts = part.get("mountpoints", [])
                        if mounts and any(m and (m.startswith("/media/") or m.startswith("/run/media/")) for m in mounts if m):
                            drives.append({
                                "device": f"/dev/{part['name']}",
                                "label": part.get("label") or "USB Drive",
                                "mountpoint": [m for m in mounts if m][0],
                                "size": part.get("size", "0B")
                            })
        except Exception:
            pass
        return drives
