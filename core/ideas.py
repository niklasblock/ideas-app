# core/ideas.py
from datetime import datetime
from core.storage import load_ideas, save_ideas

def add_idea(text):
    ideas = load_ideas()
    idea = {
        "id": len(ideas) + 1,
        "text": text,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    ideas.append(idea)
    save_ideas(ideas)
    return idea

def list_ideas():
    return load_ideas()

def delete_idea(idea_id):
    ideas = load_ideas()
    ideas = [i for i in ideas if i["id"] != idea_id]
    save_ideas(ideas)