# web/main.py
from flask import Flask, render_template, request, redirect, url_for, Response
from core.ideas import add_idea, list_ideas, delete_idea, get_idea, update_idea, update_idea_meta

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    ideas = list_ideas()
    return render_template("index.html", ideas=ideas)

@app.route("/add", methods=["POST"])
def add():
    text = request.form.get("text", "").strip()
    if text:
        add_idea(text)
    return redirect(url_for("index"))

@app.route("/idea/<int:idea_id>")
def detail(idea_id):
    idea = get_idea(idea_id)
    if not idea:
        return redirect(url_for("index"))
    return render_template("detail.html", idea=idea)

@app.route("/idea/<int:idea_id>/save", methods=["POST"])
def save(idea_id):
    content = request.form.get("content", "")
    update_idea(idea_id, content)
    return redirect(url_for("detail", idea_id=idea_id))

@app.route("/idea/<int:idea_id>/export/md")
def export_md(idea_id):
    idea = get_idea(idea_id)
    content = f"# {idea['title']}\n\n{idea.get('content', '')}"
    return Response(
        content,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=idee-{idea_id}.md"}
    )

@app.route("/delete/<int:idea_id>", methods=["POST"])
def delete(idea_id):
    delete_idea(idea_id)
    return redirect(url_for("index"))

@app.route("/idea/<int:idea_id>/meta", methods=["POST"])
def save_meta(idea_id):
    tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
    context = {
        "status": request.form.get("status"),
        "importance": int(request.form.get("importance")),
        "energy": request.form.get("energy")
    }
    update_idea_meta(idea_id, tags=tags, context=context)
    return redirect(url_for("detail", idea_id=idea_id))

def main():
    app.run(debug=True)