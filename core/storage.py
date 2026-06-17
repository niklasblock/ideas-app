# core/storage.py
import json
import os

DEFAULT_IDEAS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "ideas.json")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "settings.json")

def get_ideas_path():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_IDEAS_FILE
    if os.path.getsize(SETTINGS_FILE) == 0:
        return DEFAULT_IDEAS_FILE
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        settings = json.load(f)
    custom_path = settings.get("ideas_path")
    if custom_path and os.path.isabs(custom_path):
        return custom_path
    return DEFAULT_IDEAS_FILE

def load_ideas():
    path = get_ideas_path()
    if not os.path.exists(path):
        return []
    if os.path.getsize(path) == 0:
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ideas(ideas):
    path = get_ideas_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ideas, f, indent=2, ensure_ascii=False)