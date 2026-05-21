# gui/main.py
import sys
from PyQt6.QtWidgets import (QApplication, 
                             QMainWindow, 
                             QWidget, 
                             QVBoxLayout, 
                             QHBoxLayout, 
                             QLineEdit, 
                             QPushButton, 
                             QListWidget) 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💡 Ideen-App")
        self.setMinimumSize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Eingabe
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Neue Idee...")
        add_button = QPushButton("Hinzufügen")
        add_button.clicked.connect(self.add_idea)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(add_button)
        self.layout.addLayout(input_layout)

        # Liste
        self.idea_list = QListWidget()
        self.layout.addWidget(self.idea_list)

        # Löschen Button
        delete_button = QPushButton("Ausgewählte Idee löschen")
        delete_button.clicked.connect(self.delete_idea)
        self.layout.addWidget(delete_button)

        # Ideen beim Start laden
        self.load_ideas()

    def add_idea(self):
        from core.ideas import add_idea
        text = self.input_field.text().strip()
        if text:
            idea = add_idea(text)
            self.idea_list.addItem(f"[{idea['id']}] {idea['created']} – {idea['text']}")
            self.input_field.clear()

    def load_ideas(self):
        from core.ideas import list_ideas
        self.idea_list.clear()
        for idea in list_ideas():
            self.idea_list.addItem(f"[{idea['id']}] {idea['created']} – {idea['text']}")

    def delete_idea(self):
        from core.ideas import delete_idea
        selected = self.idea_list.currentItem()
        if selected:
            idea_id = int(selected.text().split("]")[0].replace("[", ""))
            delete_idea(idea_id)
            self.load_ideas()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())