"""
NOVA Setup Engine (10-step First Launch Master)
Handles configuration state, user creation validation, profile application, and setup persistence.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from nova_os.config import CONFIG_DIR, DATA_DIR, PROFILES, SUPPORTED_LANGUAGES
from nova_os.i18n import get_text

SETUP_STATE_FILE = DATA_DIR / "setup_config.json"

class SetupEngine:
    def __init__(self):
        self.state: Dict[str, Any] = {
            "step": 1,
            "language": "ru",
            "region": {
                "country": "RU",
                "timezone": "UTC+3",
                "time_format": "24h",
                "auto_sync_time": True
            },
            "keyboard": {
                "layout": "us,ru",
                "switch_shortcut": "Alt+Shift"
            },
            "network": {
                "connected": False,
                "ssid": None
            },
            "user": {
                "display_name": "",
                "username": "",
                "avatar": "default.png",
                "password": "",
                "auto_login": False,
                "theme": "dark",
                "screen_lock": True
            },
            "security": {
                "mic_permission": True,
                "cam_permission": True,
                "diagnostics": False,
                "local_only_data": True
            },
            "profile": "nova-home",
            "ai": {
                "enabled": True,
                "voice": "nova_female_ru",
                "language": "ru",
                "speed": 1.0,
                "volume": 80,
                "greeting_enabled": True,
                "headphone_greeting": False
            },
            "completed": False
        }

    def set_language(self, lang_code: str) -> bool:
        if lang_code in SUPPORTED_LANGUAGES:
            self.state["language"] = lang_code
            self.state["ai"]["language"] = lang_code
            return True
        return False

    def validate_user(self, username: str, password: str, display_name: str) -> Dict[str, Any]:
        errors = []
        if not display_name.strip():
            errors.append("Display name cannot be empty")

        if not username or not re.match(r"^[a-z_][a-z0-9_-]*$", username):
            errors.append("Username must start with a lowercase letter and contain only alphanumeric characters, dashes, or underscores")

        if len(password) < 4:
            errors.append("Password must be at least 4 characters long")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def set_user(self, display_name: str, username: str, password: str, auto_login: bool = False, theme: str = "dark") -> Dict[str, Any]:
        val = self.validate_user(username, password, display_name)
        if val["valid"]:
            self.state["user"]["display_name"] = display_name
            self.state["user"]["username"] = username
            self.state["user"]["password"] = password
            self.state["user"]["auto_login"] = auto_login
            self.state["user"]["theme"] = theme
        return val

    def set_profile(self, profile_name: str) -> bool:
        if profile_name in PROFILES:
            self.state["profile"] = profile_name
            return True
        return False

    def finish_setup(self) -> Dict[str, Any]:
        self.state["completed"] = True
        try:
            SETUP_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SETUP_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
            return {"success": True, "message": "Setup configuration saved successfully"}
        except Exception as e:
            return {"success": False, "message": f"Failed to save setup configuration: {str(e)}"}

    @classmethod
    def is_setup_completed(cls) -> bool:
        if SETUP_STATE_FILE.exists():
            try:
                with open(SETUP_STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("completed", False)
            except Exception:
                return False
        return False
