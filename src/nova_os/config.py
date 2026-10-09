"""
Global Constants and Configurations for NOVA OS
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = Path("/var/lib/nova-os") if Path("/var/lib/nova-os").exists() else BASE_DIR / "data"
QUARANTINE_DIR = DATA_DIR / "quarantine"
LOG_DIR = Path("/var/log/nova-os") if Path("/var/log/nova-os").exists() else BASE_DIR / "logs"

# Ensure directories exist
for path in [DATA_DIR, QUARANTINE_DIR, LOG_DIR]:
    path.mkdir(parents=True, exist_ok=True)

SUPPORTED_LANGUAGES = {
    "ru": "Русский",
    "en": "English",
    "uz": "O'zbekcha"
}

PROFILES = ["nova-lite", "nova-gaming", "nova-dev", "nova-home"]

THEMES = ["dark", "light"]
