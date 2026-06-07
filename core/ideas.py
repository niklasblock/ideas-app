# core/ideas.py
from datetime import datetime
from uuid import uuid4
from core.storage import load_ideas, save_ideas
from datetime import datetime, timedelta
import random

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def add_idea(title):
    ideas = load_ideas()
    idea = {
        "id": max((i["id"] for i in ideas), default=0) + 1,
        "uuid": str(uuid4()),
        "title": title,
        "content": "",
        "tags": [],
        "links": {
            "related": [],
            "inspired_by": [],
            "leads_to": [],
            "part_of": []
        },
        "context": {
            "source": "brain",
            "status": "raw",
            "importance": 1,
            "energy": "medium"
        },
        "time": {
            "created": _now(),
            "updated": _now(),
            "last_viewed": _now(),
            "view_count": 0
        },
        "history": [
            {"date": _now(), "note": "Idee erstellt"}
        ]
    }
    ideas.append(idea)
    save_ideas(ideas)
    return idea

def list_ideas():
    return load_ideas()

def get_idea(idea_id):
    ideas = load_ideas()
    for idea in ideas:
        if idea["id"] == idea_id:
            return idea
    return None

def update_idea(idea_id, content):
    ideas = load_ideas()
    for idea in ideas:
        if idea["id"] == idea_id:
            idea["content"] = content
            idea.setdefault("time", {})["updated"] = _now()
            idea.setdefault("history", []).append({
                "date": _now(),
                "note": "Inhalt aktualisiert"
            })
            break
    save_ideas(ideas)

def update_idea_meta(idea_id, tags=None, context=None, links=None):
    ideas = load_ideas()
    for idea in ideas:
        if idea["id"] == idea_id:
            if tags is not None:
                idea["tags"] = tags
            if context is not None:
                idea.setdefault("context", {}).update(context)
            if links is not None:
                idea.setdefault("links", {}).update(links)
            idea.setdefault("time", {})["updated"] = _now()
            break
    save_ideas(ideas)

def delete_idea(idea_id):
    ideas = load_ideas()
    ideas = [i for i in ideas if i["id"] != idea_id]
    save_ideas(ideas)

def track_view(idea_id):
    ideas = load_ideas()
    for idea in ideas:
        if idea["id"] == idea_id:
            idea.setdefault("time", {})["last_viewed"] = _now()
            idea["time"]["view_count"] = idea["time"].get("view_count", 0) + 1
            break
    save_ideas(ideas)

def get_backlinks(idea_id):
    ideas = load_ideas()
    backlinks = []
    for idea in ideas:
        links = idea.get("links", {})
        all_linked_ids = (
            links.get("related", []) +
            links.get("inspired_by", []) +
            links.get("leads_to", []) +
            links.get("part_of", [])
        )
        if idea_id in all_linked_ids:
            backlinks.append(idea)
    return backlinks

def add_link(from_id, to_id, link_type="related"):
    ideas = load_ideas()
    for idea in ideas:
        if idea["id"] == from_id:
            idea.setdefault("links", {}).setdefault(link_type, [])
            if to_id not in idea["links"][link_type]:
                idea["links"][link_type].append(to_id)
            break
    save_ideas(ideas)

def remove_link(from_id, to_id, link_type="related"):
    ideas = load_ideas()
    for idea in ideas:
        if idea["id"] == from_id:
            links = idea.get("links", {}).get(link_type, [])
            if to_id in links:
                links.remove(to_id)
            break
    save_ideas(ideas)


def get_unseen_ideas(days=7):
    ideas = load_ideas()
    cutoff = datetime.now() - timedelta(days=days)
    result = []
    for idea in ideas:
        last_viewed = idea.get("time", {}).get("last_viewed")
        if last_viewed:
            last_viewed_dt = datetime.strptime(last_viewed, "%Y-%m-%d %H:%M")
            if last_viewed_dt < cutoff:
                result.append(idea)
    return result

def get_random_idea():
    ideas = load_ideas()
    if not ideas:
        return None
    return random.choice(ideas)

def get_unlinked_ideas():
    ideas = load_ideas()
    result = []
    for idea in ideas:
        links = idea.get("links", {})
        all_links = (
            links.get("related", []) +
            links.get("inspired_by", []) +
            links.get("leads_to", []) +
            links.get("part_of", [])
        )
        backlinks = get_backlinks(idea["id"])
        if not all_links and not backlinks:
            result.append(idea)
    return result