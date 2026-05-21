# gui/main.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from gui.styles import LIGHT, DARK

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.setWindowTitle("Ideen-App")
        self.setMinimumSize(700, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(12)

        # Kopfzeile
        header_layout = QHBoxLayout()
        title = QPushButton("Ideen-App")
        title.setObjectName("title_btn")
        title.setEnabled(False)
        self.theme_btn = QPushButton("Dark Mode")
        self.theme_btn.setObjectName("theme_btn")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_btn)
        self.main_layout.addLayout(header_layout)

        # Eingabe
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Neue Idee eingeben...")
        self.input_field.returnPressed.connect(self.add_idea)
        add_btn = QPushButton()
        add_btn.setText("+")
        add_btn.setObjectName("add_btn")
        add_btn.setFixedSize(44, 44)
        add_btn.clicked.connect(self.add_idea)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(add_btn)
        self.main_layout.addLayout(input_layout)

        # Tabelle
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Idee", "Zeit", ""])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.main_layout.addWidget(self.table)

        self.apply_theme()
        self.load_ideas()

    def apply_theme(self):
        self.setStyleSheet(DARK if self.dark_mode else LIGHT)
        self.theme_btn.setText("☀" if self.dark_mode else "☾")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def load_ideas(self):
        from core.ideas import list_ideas
        self.table.setRowCount(0)
        for idea in list_ideas():
            self._add_row(idea)

    def _add_row(self, idea):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 40)
        self.table.setItem(row, 0, QTableWidgetItem(f"#{idea['id']}"))
        self.table.setItem(row, 1, QTableWidgetItem(idea['text']))
        self.table.setItem(row, 2, QTableWidgetItem(idea['created']))
        delete_btn = QPushButton("Löschen")
        delete_btn.setFixedHeight(28)
        delete_btn.setStyleSheet(
            "QPushButton { color: #e24b4a; border: 1px solid #f0d0d0; border-radius: 6px; background: transparent; font-size: 12px; padding: 0 10px; }"
            "QPushButton:hover { background-color: #fff0f0; }"
        )
        delete_btn.clicked.connect(lambda _, id=idea['id']: self.delete_idea(id))
        self.table.setColumnWidth(3, 100)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setCellWidget(row, 3, delete_btn)

    def add_idea(self):
        from core.ideas import add_idea
        text = self.input_field.text().strip()
        if text:
            idea = add_idea(text)
            self._add_row(idea)
            self.input_field.clear()

    def delete_idea(self, idea_id):
        from core.ideas import delete_idea
        delete_idea(idea_id)
        self.load_ideas()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())