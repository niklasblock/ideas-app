# web/main.py
from flask import Flask, render_template, request, redirect, url_for
from core.ideas import add_idea, list_ideas, delete_idea

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

@app.route("/delete/<int:idea_id>", methods=["POST"])
def delete(idea_id):
    delete_idea(idea_id)
    return redirect(url_for("index"))

def main():
    app.run(debug=True)