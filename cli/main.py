# cli/main.py
from core.ideas import add_idea, list_ideas, delete_idea

def main():
    print("💡 Ideen-App")
    print("Befehle: add | list | delete | quit")
    while True:
        cmd = input("\n> ").strip().lower()
        if cmd == "quit":
            break
        elif cmd == "add":
            text = input("Idee: ").strip()
            if text:
                idea = add_idea(text)
                print(f"✅ Idee gespeichert (ID {idea['id']})")
        elif cmd == "list":
            ideas = list_ideas()
            if not ideas:
                print("Noch keine Ideen gespeichert.")
            for idea in ideas:
                print(f"[{idea['id']}] {idea['created']} – {idea['text']}")
        elif cmd == "delete":
            try:
                idea_id = int(input("ID: "))
                delete_idea(idea_id)
                print(f"🗑️ Idee {idea_id} gelöscht.")
            except ValueError:
                print("Ungültige ID.")
        else:
            print("Unbekannter Befehl.")