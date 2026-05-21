# core/storage.py
import json
import os

IDEAS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "ideas.json")

def load_ideas():
    if not os.path.exists(IDEAS_FILE):
        return []
    if os.path.getsize(IDEAS_FILE) == 0:
        return []
    with open(IDEAS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ideas(ideas):
    with open(IDEAS_FILE, "w", encoding="utf-8") as f:
        json.dump(ideas, f, indent=2, ensure_ascii=False)