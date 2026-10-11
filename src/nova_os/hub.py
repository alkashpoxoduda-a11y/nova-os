"""
NOVA Hub - Software App Center & APT Package Manager
Provides package search, category filtering, package installation and removal via APT.
"""

import subprocess
import shutil
from typing import Dict, Any, List, Optional

RECOMMENDED_PACKAGES = [
    {"name": "firefox-esr", "category": "Internet", "desc": "Быстрый и безопасный веб-браузер Firefox"},
    {"name": "vlc", "category": "Multimedia", "desc": "Медиапроигрыватель VLC"},
    {"name": "gimp", "category": "Graphics", "desc": "Графический редактор GIMP"},
    {"name": "libreoffice", "category": "Office", "desc": "Офисный пакет LibreOffice"},
    {"name": "steam", "category": "Games", "desc": "Игровая платформа Steam"},
    {"name": "kate", "category": "Development", "desc": "Текстовый редактор Kate"},
    {"name": "htop", "category": "System", "desc": "Монитор процессов htop"}
]


class NovaHubAppStore:
    def __init__(self):
        self.has_apt = shutil.which("apt-get") is not None

    def search_packages(self, query: str) -> List[Dict[str, Any]]:
        if not query.strip():
            return RECOMMENDED_PACKAGES

        q = query.lower()
        results = [p for p in RECOMMENDED_PACKAGES if q in p["name"].lower() or q in p["category"].lower() or q in p["desc"].lower()]

        if self.has_apt and len(results) == 0:
            try:
                res = subprocess.run(["apt-cache", "search", query], capture_output=True, text=True, timeout=5)
                if res.returncode == 0:
                    for line in res.stdout.strip().split("\n")[:10]:
                        if " - " in line:
                            parts = line.split(" - ", 1)
                            results.append({
                                "name": parts[0].strip(),
                                "category": "System",
                                "desc": parts[1].strip()
                            })
            except Exception:
                pass

        return results

    def install_package(self, package_name: str) -> Dict[str, Any]:
        """Installs a system package using apt-get."""
        if not self.has_apt:
            return {"success": False, "message": "Пакетный менеджер APT недоступен."}

        try:
            res = subprocess.run(["sudo", "apt-get", "install", "-y", package_name], capture_output=True, text=True, timeout=120)
            if res.returncode == 0:
                return {"success": True, "message": f"Приложение '{package_name}' успешно установлено."}
            else:
                return {"success": False, "message": f"Ошибка установки: {res.stderr[:200]}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Установка приложения превысила время ожидания."}
        except Exception as e:
            return {"success": False, "message": f"Ошибка установки: {str(e)}"}

    def remove_package(self, package_name: str) -> Dict[str, Any]:
        """Removes a system package using apt-get."""
        if not self.has_apt:
            return {"success": False, "message": "Пакетный менеджер APT недоступен."}

        try:
            res = subprocess.run(["sudo", "apt-get", "remove", "-y", package_name], capture_output=True, text=True, timeout=60)
            if res.returncode == 0:
                return {"success": True, "message": f"Приложение '{package_name}' успешно удалено."}
            else:
                return {"success": False, "message": f"Ошибка удаления: {res.stderr[:200]}"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка удаления: {str(e)}"}
