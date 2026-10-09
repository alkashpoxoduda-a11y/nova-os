"""
Internationalization (i18n) support for NOVA OS (ru, en, uz)
"""

TRANSLATIONS = {
    "ru": {
        "welcome_title": "Добро пожаловать в NOVA OS",
        "welcome_subtitle": "Современная, безопасная и быстрая операционная система",
        "btn_next": "Далее",
        "btn_back": "Назад",
        "btn_finish": "Завершить и войти",
        "btn_start": "Начать",
        "step_1": "Приветствие",
        "step_2": "Выбор языка",
        "step_3": "Регион и время",
        "step_4": "Раскладка клавиатуры",
        "step_5": "Сетевые подключения",
        "step_6": "Учётная запись пользователя",
        "step_7": "Безопасность и приватность",
        "step_8": "Профиль компьютера",
        "step_9": "Голосовой ИИ-помощник NOVA AI",
        "step_10": "Завершение настройки",
        "lang_ru": "Русский",
        "lang_en": "English",
        "lang_uz": "O'zbekcha",
        "profile_home": "NOVA Home - Универсальный баланс",
        "profile_lite": "NOVA Lite - Для слабых ПК",
        "profile_gaming": "NOVA Gaming - Для игр и высокой производительности",
        "profile_dev": "NOVA Dev - Для разработчиков и инженеров",
        "ai_greeting": "Добро пожаловать в NOVA OS, {user}. Твоя система готова к работе.",
        "ai_headphone_greeting": "Добро пожаловать, {user}."
    },
    "en": {
        "welcome_title": "Welcome to NOVA OS",
        "welcome_subtitle": "A modern, secure, and fast operating system",
        "btn_next": "Next",
        "btn_back": "Back",
        "btn_finish": "Finish & Login",
        "btn_start": "Start",
        "step_1": "Welcome",
        "step_2": "Language Selection",
        "step_3": "Region & Timezone",
        "step_4": "Keyboard Layout",
        "step_5": "Network Connections",
        "step_6": "User Account",
        "step_7": "Security & Privacy",
        "step_8": "System Profile",
        "step_9": "NOVA AI Assistant",
        "step_10": "Setup Completion",
        "lang_ru": "Russian",
        "lang_en": "English",
        "lang_uz": "Uzbek",
        "profile_home": "NOVA Home - Everyday Balance",
        "profile_lite": "NOVA Lite - Low-spec PC Optimization",
        "profile_gaming": "NOVA Gaming - High Gaming Performance",
        "profile_dev": "NOVA Dev - Developer & Engineer Suite",
        "ai_greeting": "Welcome to NOVA OS, {user}. Your system is ready for work.",
        "ai_headphone_greeting": "Welcome, {user}."
    },
    "uz": {
        "welcome_title": "NOVA OS tizimiga xush kelibsiz",
        "welcome_subtitle": "Zamonaviy, xavfsiz va tezkor operatsion tizim",
        "btn_next": "Keyingisi",
        "btn_back": "Orqaga",
        "btn_finish": "Tugatish va kirish",
        "btn_start": "Boshlash",
        "step_1": "Xush kelibsiz",
        "step_2": "Tilni tanlash",
        "step_3": "Mintaqa va vaqt",
        "step_4": "Klaviatura joylashuvi",
        "step_5": "Tarmoq ulanishi",
        "step_6": "Foydalanuvchi hisobi",
        "step_7": "Xavfsizlik va maxfiylik",
        "step_8": "Tizim profili",
        "step_9": "NOVA AI Ovozli yordamchi",
        "step_10": "Sozlashni yakunlash",
        "lang_ru": "Ruscha",
        "lang_en": "Inglizcha",
        "lang_uz": "O'zbekcha",
        "profile_home": "NOVA Home - Barcha uchun universal",
        "profile_lite": "NOVA Lite - Kuchli bo'lmagan PK uchun",
        "profile_gaming": "NOVA Gaming - O'yinlar uchun yuqori unumdorlik",
        "profile_dev": "NOVA Dev - Dasturchilar uchun",
        "ai_greeting": "NOVA OS ga xush kelibsiz, {user}. Tizimingiz ishlashga tayyor.",
        "ai_headphone_greeting": "Xush kelibsiz, {user}."
    }
}

def get_text(key: str, lang: str = "ru", **kwargs) -> str:
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["ru"])
    text = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
