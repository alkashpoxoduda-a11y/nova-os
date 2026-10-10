"""
NOVA OS Custom Wallpaper & Desktop Personalization Engine
Handles image file validation, copying custom wallpapers to user directory,
theme-specific wallpapers (Light/Dark), scaling mode management, USB drive disconnection fallback,
and Live-session persistence notices.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from nova_os.config import DATA_DIR, CONFIG_DIR

SUPPORTED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
DEFAULT_WALLPAPER_DARK = "/usr/share/backgrounds/nova-os/nova-supernova-dark.png"
DEFAULT_WALLPAPER_LIGHT = "/usr/share/backgrounds/nova-os/nova-supernova-light.png"

USER_WALLPAPER_DIR = Path.home() / ".config" / "nova-os" / "wallpapers"
WALLPAPER_CONFIG_FILE = Path.home() / ".config" / "nova-os" / "wallpaper_settings.json"


class WallpaperManager:
    def __init__(self, is_live_session: bool = False):
        self.is_live_session = is_live_session
        USER_WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        if WALLPAPER_CONFIG_FILE.exists():
            try:
                with open(WALLPAPER_CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "dark_wallpaper": DEFAULT_WALLPAPER_DARK,
            "light_wallpaper": DEFAULT_WALLPAPER_LIGHT,
            "scaling_mode": "fill",  # fill, fit, stretch, center
            "current_active": DEFAULT_WALLPAPER_DARK,
            "active_theme": "dark"
        }

    def _save_settings(self):
        try:
            WALLPAPER_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(WALLPAPER_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def select_custom_wallpaper(self, filepath: str, theme: str = "dark", mode: str = "fill") -> Dict[str, Any]:
        """Validates and applies a custom wallpaper file from local disk or USB drive."""
        src_path = Path(filepath)
        if not src_path.exists():
            return {
                "success": False,
                "message": f"Файл обоев не найден: {filepath}. Если файл находился на USB-накопителе, убедитесь, что устройство подключено."
            }

        if src_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            return {
                "success": False,
                "message": f"Неподдерживаемый формат файла: {src_path.suffix}. Допустимые форматы: JPG, JPEG, PNG, WebP."
            }

        if mode not in ["fill", "fit", "stretch", "center"]:
            mode = "fill"

        # Safely copy image into user configuration catalog to preserve wallpaper even if original USB/Downloads file is moved/deleted
        dest_filename = f"user_{theme}_{src_path.name}"
        dest_path = USER_WALLPAPER_DIR / dest_filename

        try:
            shutil.copy2(src_path, dest_path)
            wallpaper_url = str(dest_path)

            if theme == "light":
                self.settings["light_wallpaper"] = wallpaper_url
            else:
                self.settings["dark_wallpaper"] = wallpaper_url

            self.settings["scaling_mode"] = mode
            self.settings["active_theme"] = theme
            self.settings["current_active"] = wallpaper_url
            self._save_settings()

            msg = "Обои рабочего стола успешно обновлены."
            if self.is_live_session:
                msg += " (Внимание: В Live-сессии настроенные обои сбросятся после перезагрузки без установки)."

            return {
                "success": True,
                "wallpaper_path": wallpaper_url,
                "scaling_mode": mode,
                "theme": theme,
                "message": msg
            }
        except Exception as e:
            return {"success": False, "message": f"Ошибка сохранения обоев: {str(e)}"}

    def reset_to_default(self) -> Dict[str, Any]:
        """Resets desktop wallpaper to official NOVA OS defaults."""
        self.settings["dark_wallpaper"] = DEFAULT_WALLPAPER_DARK
        self.settings["light_wallpaper"] = DEFAULT_WALLPAPER_LIGHT
        self.settings["current_active"] = DEFAULT_WALLPAPER_DARK
        self.settings["scaling_mode"] = "fill"
        self._save_settings()

        return {
            "success": True,
            "wallpaper_path": DEFAULT_WALLPAPER_DARK,
            "message": "Сброшено к официальным обоям NOVA OS по умолчанию."
        }

    def get_current_wallpaper_info(self) -> Dict[str, Any]:
        """Returns active wallpaper path, verifying file presence with fallback."""
        active_path = Path(self.settings.get("current_active", DEFAULT_WALLPAPER_DARK))

        # USB disconnection fallback
        if not active_path.exists():
            active_path = Path(DEFAULT_WALLPAPER_DARK)
            self.settings["current_active"] = DEFAULT_WALLPAPER_DARK
            self._save_settings()

        return {
            "active_wallpaper": str(active_path),
            "scaling_mode": self.settings.get("scaling_mode", "fill"),
            "active_theme": self.settings.get("active_theme", "dark"),
            "is_live_session": self.is_live_session
        }
