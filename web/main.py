from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
from core.ideas import (add_idea, list_ideas, delete_idea, get_idea, update_idea,
                        update_idea_meta, get_backlinks, add_link, remove_link,
                        get_unseen_ideas, get_random_idea, get_unlinked_ideas, track_view)
from core.similarity import get_similar_ideas
from core.settings import load_settings, save_settings, update_setting
from datetime import datetime
import os 

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("app.html")

@app.route("/api/ideas", methods=["GET"])
def api_list_ideas():
    return jsonify(list_ideas())

@app.route("/api/ideas", methods=["POST"])
def api_add_idea():
    data = request.json
    idea = add_idea(data["title"])
    return jsonify(idea)

@app.route("/api/ideas/<int:idea_id>", methods=["GET"])
def api_get_idea(idea_id):
    idea = get_idea(idea_id)
    if not idea:
        return jsonify({}), 404
    track_view(idea_id)
    idea["backlinks"] = get_backlinks(idea_id)
    return jsonify(idea)

@app.route("/api/ideas/<int:idea_id>", methods=["DELETE"])
def api_delete_idea(idea_id):
    delete_idea(idea_id)
    return jsonify({"ok": True})

@app.route("/api/ideas/<int:idea_id>/content", methods=["POST"])
def api_save_content(idea_id):
    data = request.json
    update_idea(idea_id, data["content"])
    return jsonify({"ok": True})

@app.route("/api/ideas/<int:idea_id>/meta", methods=["POST"])
def api_save_meta(idea_id):
    data = request.json
    tags = data.get("tags", [])
    context = {
        "status": data.get("status"),
        "importance": data.get("importance"),
        "energy": data.get("energy")
    }
    update_idea_meta(idea_id, tags=tags, context=context)
    return jsonify({"ok": True})

@app.route("/api/ideas/<int:idea_id>/link", methods=["POST"])
def api_add_link(idea_id):
    data = request.json
    add_link(idea_id, data["to_id"], data.get("link_type", "related"))
    return jsonify({"ok": True})

@app.route("/api/ideas/<int:idea_id>/unlink", methods=["POST"])
def api_unlink(idea_id):
    data = request.json
    remove_link(idea_id, data["to_id"], data.get("link_type", "related"))
    return jsonify({"ok": True})

@app.route("/api/ideas/<int:idea_id>/similar")
def api_similar(idea_id):
    settings = load_settings()
    return jsonify(get_similar_ideas(idea_id, top=settings.get("similar_count", 5)))

@app.route("/api/ideas/<int:idea_id>/export/md")
def api_export_md(idea_id):
    idea = get_idea(idea_id)
    content = f"# {idea['title']}\n\n{idea.get('content', '')}"
    return Response(
        content,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=idee-{idea_id}.md"}
    )

@app.route("/api/ideas/<int:idea_id>/title", methods=["POST"])
def api_save_title(idea_id):
    data = request.json
    ideas = list_ideas()
    for idea in ideas:
        if idea["id"] == idea_id:
            idea["title"] = data["title"]
            idea["time"]["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    from core.storage import save_ideas
    save_ideas(ideas)
    return jsonify({"ok": True})

@app.route("/api/recall")
def api_recall():
    settings = load_settings()
    return jsonify({
        "unseen": get_unseen_ideas(days=settings.get("recall_days", 7)),
        "unlinked": get_unlinked_ideas(),
        "random": get_random_idea()
    })

@app.route("/graph")
def graph():
    ideas = list_ideas()
    nodes = [{"id": i["id"], "title": i["title"], "status": i.get("context", {}).get("status", "raw")} for i in ideas]
    edges = []
    for idea in ideas:
        for link_type, ids in idea.get("links", {}).items():
            for to_id in ids:
                edges.append({"source": idea["id"], "target": to_id, "type": link_type})
    return render_template("graph.html", nodes=nodes, edges=edges)

@app.route("/api/settings", methods=["GET"])
def api_get_settings():
    return jsonify(load_settings())

@app.route("/api/settings", methods=["POST"])
def api_save_settings():
    from core.storage import get_ideas_path, load_ideas, save_ideas
    import shutil
    
    data = request.json
    old_path = get_ideas_path()
    
    # Einstellungen speichern
    save_settings(data)
    
    # Migration wenn Pfad geändert wurde
    new_path = data.get("ideas_path")
    if new_path and new_path != old_path and os.path.exists(old_path):
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        # Nur migrieren wenn neue Datei leer oder nicht existiert
        if not os.path.exists(new_path) or os.path.getsize(new_path) == 0:
            shutil.copy2(old_path, new_path)
    
    return jsonify({"ok": True})

def main():
    app.run(debug=True)