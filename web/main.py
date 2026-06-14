from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
from core.ideas import (add_idea, list_ideas, delete_idea, get_idea, update_idea,
                        update_idea_meta, get_backlinks, add_link, remove_link,
                        get_unseen_ideas, get_random_idea, get_unlinked_ideas, track_view)
from core.similarity import get_similar_ideas
from datetime import datetime

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
    return jsonify(get_similar_ideas(idea_id))

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
    return jsonify({
        "unseen": get_unseen_ideas(days=7),
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

def main():
    app.run(debug=True)