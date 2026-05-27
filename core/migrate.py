# core/migrate.py
from core.storage import load_ideas, save_ideas
from datetime import datetime

def migrate():
    ideas = load_ideas()
    changed = False

    for idea in ideas:
        # text -> title
        if "text" in idea and "title" not in idea:
            idea["title"] = idea.pop("text")
            changed = True

        # created -> time object
        if "created" in idea and "time" not in idea:
            idea["time"] = {
                "created": idea.pop("created"),
                "updated": idea.get("updated", datetime.now().strftime("%Y-%m-%d %H:%M")),
                "last_viewed": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "view_count": 0
            }
            changed = True

        # fehlende Felder ergänzen
        idea.setdefault("uuid", str(__import__("uuid").uuid4()))
        idea.setdefault("content", "")
        idea.setdefault("tags", [])
        idea.setdefault("links", {"related": [], "inspired_by": [], "leads_to": [], "part_of": []})
        idea.setdefault("context", {"source": "brain", "status": "raw", "importance": 1, "energy": "medium"})
        idea.setdefault("history", [{"date": idea.get("time", {}).get("created", ""), "note": "Migriert"}])

    if changed:
        save_ideas(ideas)
        print(f"✅ {len(ideas)} Ideen migriert.")
    else:
        print("Keine Migration nötig.")

if __name__ == "__main__":
    migrate()