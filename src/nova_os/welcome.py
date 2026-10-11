"""
NOVA Welcome - First Launch Setup Wizard
Blocks default 'debian live user' experience, enforcing interactive configuration of
Language (Russian default, English), User Account Creation (with optional password),
Timezone, and NetworkManager connections.
Includes assistant voice greeting on startup.
"""

import json
import re
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from nova_os.i18n import get_text
from nova_os.network import NetworkManagerEngine
from nova_os.ai_assistant import NovaAIAssistant

WELCOME_STATE_FILE = Path.home() / ".config" / "nova-os" / "welcome_completed.json"

WELCOME_VOICE_GREETING_RU = "Здравствуйте! Мы рады, что вы начали использование нашей операционной системы NOVA OS. Для начала выберите язык компьютера и создайте учётную запись."
WELCOME_VOICE_GREETING_EN = "Hello! We are glad you have started using NOVA OS. To begin, please select your language and create a user account."


class NovaWelcomeEngine:
    def __init__(self):
        self.network = NetworkManagerEngine()
        self.ai = NovaAIAssistant()
        self.state = {
            "completed": self.is_completed(),
            "language": "ru",
            "timezone": "UTC+3",
            "user": {
                "display_name": "",
                "username": "",
                "password": "",  # Optional password
                "auto_login": True
            },
            "network": {
                "connected_ssid": None
            }
        }

    def announce_welcome_greeting(self) -> str:
        """Speaks the initial voice greeting using local system TTS assistant engine."""
        greeting_text = WELCOME_VOICE_GREETING_RU if self.state["language"] == "ru" else WELCOME_VOICE_GREETING_EN
        self.ai.speak_text(greeting_text)
        return greeting_text

    @classmethod
    def is_completed(cls) -> bool:
        if WELCOME_STATE_FILE.exists():
            try:
                with open(WELCOME_STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("completed", False)
            except Exception:
                return False
        return False

    def set_language(self, lang_code: str) -> Dict[str, Any]:
        if lang_code in ["ru", "en"]:
            self.state["language"] = lang_code
            self.ai.language = lang_code
            greeting = self.announce_welcome_greeting()
            return {
                "success": True,
                "language": lang_code,
                "greeting_spoken": greeting,
                "message": f"Язык системы изменён на {get_text('lang_' + lang_code, lang_code)}"
            }
        return {"success": False, "message": "Неподдерживаемый язык."}

    def validate_user_account(self, display_name: str, username: str, password: str = "") -> Dict[str, Any]:
        errors = []
        if not display_name.strip():
            errors.append("Имя пользователя не может быть пустым.")

        # Prevent default 'debian' or 'live' user names
        clean_user = username.strip().lower()
        if clean_user in ["debian", "live", "root", "debian-live"]:
            errors.append("Имя системного пользователя не должно совпадать с дефолтными именем 'debian' или 'live'.")

        if not clean_user or not re.match(r"^[a-z_][a-z0-9_-]*$", clean_user):
            errors.append("Системный логин должен содержать только строчные латинские буквы, цифры и символы подчеркивания.")

        # Password is now OPTIONAL! If user enters a password, it must be at least 4 chars.
        if password and len(password) < 4:
            errors.append("Если задаётся пароль, он должен содержать не менее 4 символов.")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def create_user_account(self, display_name: str, username: str, password: str = "", auto_login: bool = True) -> Dict[str, Any]:
        val = self.validate_user_account(display_name, username, password)
        if not val["valid"]:
            return {"success": False, "errors": val["errors"]}

        self.state["user"]["display_name"] = display_name
        self.state["user"]["username"] = username.strip().lower()
        self.state["user"]["password"] = password  # Can be empty string
        self.state["user"]["auto_login"] = auto_login

        return {"success": True, "message": f"Учётная запись '{display_name}' ({username}) успешно создана."}

    def finish_wizard(self) -> Dict[str, Any]:
        if not self.state["user"]["username"]:
            return {"success": False, "message": "Завершение невозможно: учётная запись пользователя не создана."}

        self.state["completed"] = True
        try:
            WELCOME_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(WELCOME_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
            return {
                "success": True,
                "message": "Настройка NOVA OS успешно завершена. Добро пожаловать в систему!"
            }
        except Exception as e:
            return {"success": False, "message": f"Ошибка сохранения настроек: {str(e)}"}
