# core/settings.py
import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "settings.json")

DEFAULT_SETTINGS = {
    "dark_mode": False,
    "recall_days": 7,
    "similar_count": 5,
    "ideas_path": None,
    "language": "de"
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    if os.path.getsize(SETTINGS_FILE) == 0:
        return DEFAULT_SETTINGS.copy()
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    settings = DEFAULT_SETTINGS.copy()
    settings.update(data)
    return settings

def save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

def get_setting(key):
    return load_settings().get(key, DEFAULT_SETTINGS.get(key))

def update_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)