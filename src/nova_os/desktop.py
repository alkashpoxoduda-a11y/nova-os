"""
NOVA Desktop Environment & Desktop Shell Manager
Manages taskbar panel, app launcher menu, notification center, quick settings,
virtual desktops, file manager engine, NetworkManager integration, and Wallpaper Manager.
Includes low-resource layout optimization for 1366x768 screens.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from nova_os.config import DATA_DIR, PROFILES
from nova_os.i18n import get_text
from nova_os.network import NetworkManagerEngine
from nova_os.wallpaper import WallpaperManager

class AppLauncher:
    def __init__(self):
        self.default_apps = [
            {"id": "nova-filemanager", "name": "NOVA File Manager", "icon": "folder-blue", "exec": "nova-fm", "category": "System"},
            {"id": "nova-terminal", "name": "NOVA Terminal", "icon": "utilities-terminal", "exec": "nova-terminal", "category": "Development"},
            {"id": "nova-browser", "name": "Web Browser (Firefox ESR)", "icon": "web-browser", "exec": "firefox-esr", "category": "Network"},
            {"id": "nova-control-center", "name": "NOVA Control Center", "icon": "preferences-system", "exec": "nova-control-center", "category": "System"},
            {"id": "nova-shield", "name": "NOVA Shield Security", "icon": "security-high", "exec": "nova-shield", "category": "Security"},
            {"id": "nova-software", "name": "NOVA App Center", "icon": "system-software-install", "exec": "nova-software", "category": "System"},
            {"id": "steam", "name": "Steam", "icon": "steam", "exec": "steam", "category": "Games"},
            {"id": "telegram", "name": "Telegram Desktop", "icon": "telegram", "exec": "telegram-desktop", "category": "Network"},
            {"id": "code", "name": "VS Code", "icon": "code", "exec": "code", "category": "Development"}
        ]

    def search_apps(self, query: str) -> List[Dict[str, Any]]:
        if not query.strip():
            return self.default_apps
        q = query.lower()
        return [app for app in self.default_apps if q in app["name"].lower() or q in app["category"].lower()]


class NotificationCenter:
    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []

    def add_notification(self, title: str, message: str, level: str = "info", source: str = "NOVA OS"):
        item = {
            "id": len(self.notifications) + 1,
            "title": title,
            "message": message,
            "level": level,  # info, warning, danger
            "source": source
        }
        self.notifications.append(item)
        return item

    def get_all(self) -> List[Dict[str, Any]]:
        return self.notifications

    def clear(self):
        self.notifications.clear()


class VirtualDesktopManager:
    def __init__(self, count: int = 4):
        self.total_desktops = count
        self.current_desktop = 1

    def switch_desktop(self, desktop_num: int) -> bool:
        if 1 <= desktop_num <= self.total_desktops:
            self.current_desktop = desktop_num
            return True
        return False


class NovaFileManager:
    def __init__(self, root_dir: Optional[str] = None):
        self.current_path = Path(root_dir) if root_dir else Path.home()

    def list_directory(self, path: Optional[str] = None) -> List[Dict[str, Any]]:
        target = Path(path) if path else self.current_path
        if not target.exists() or not target.is_dir():
            return []

        items = []
        try:
            for item in target.iterdir():
                items.append({
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if not item.is_dir() else 0,
                    "path": str(item)
                })
        except PermissionError:
            pass
        return items


class NovaDesktopShell:
    def __init__(self, screen_resolution: str = "1366x768"):
        self.app_launcher = AppLauncher()
        self.notifications = NotificationCenter()
        self.desktop_manager = VirtualDesktopManager()
        self.file_manager = NovaFileManager()
        self.network = NetworkManagerEngine()
        self.wallpaper = WallpaperManager()
        self.current_theme = "dark"
        self.active_profile = "nova-home"
        self.screen_resolution = screen_resolution
        self.pinned_apps = ["nova-filemanager", "nova-terminal", "nova-browser", "nova-control-center"]

    def set_theme(self, theme: str) -> bool:
        if theme in ["dark", "light"]:
            self.current_theme = theme
            return True
        return False

    def switch_profile(self, profile: str) -> bool:
        if profile in PROFILES:
            self.active_profile = profile
            self.notifications.add_notification(
                "NOVA OS Profile Switch",
                f"Системный профиль изменён на {profile}",
                "info"
            )
            return True
        return False

    def get_layout_config(self) -> Dict[str, Any]:
        """Returns resolution-aware compact layout settings (optimized for 1366x768)."""
        is_low_res = self.screen_resolution in ["1024x768", "1366x768"]
        return {
            "screen_resolution": self.screen_resolution,
            "panel_height_px": 36 if is_low_res else 44,
            "icon_size_px": 24 if is_low_res else 32,
            "compact_view": is_low_res,
            "max_settings_height_px": 600 if is_low_res else 900
        }
