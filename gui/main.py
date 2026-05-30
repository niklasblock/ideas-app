# gui/main.py
import sys
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget
)
from PyQt6.QtCore import Qt
from gui.styles import LIGHT, DARK

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.setWindowTitle("Ideen-App")
        self.setMinimumSize(900, 650)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.list_page = QWidget()
        self.stack.addWidget(self.list_page)
        self._build_list_page()

        self.apply_theme()
        self.load_ideas()

    def _build_list_page(self):
        layout = QVBoxLayout(self.list_page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        title = QPushButton("Ideen-App")
        title.setObjectName("title_btn")
        title.setEnabled(False)
        graph_btn = QPushButton("Graph")
        graph_btn.setObjectName("action_btn")
        graph_btn.clicked.connect(self.open_graph)
        self.theme_btn = QPushButton("☾")
        self.theme_btn.setObjectName("theme_btn")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(graph_btn)
        header_layout.addWidget(self.theme_btn)
        layout.addLayout(header_layout)

        # Eingabe
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Neue Idee eingeben...")
        self.input_field.returnPressed.connect(self.add_idea)
        add_btn = QPushButton("+")
        add_btn.setObjectName("add_btn")
        add_btn.setFixedSize(44, 44)
        add_btn.clicked.connect(self.add_idea)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)

        # Tabelle
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Idee", "Zeit", ""])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(3, 110)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.cellDoubleClicked.connect(self.open_detail)
        layout.addWidget(self.table)

    def open_detail(self, row, col):
        from gui.detail import DetailWindow
        id_text = self.table.item(row, 0).text().replace("#", "")
        idea_id = int(id_text)

        if self.stack.count() > 1:
            self.stack.removeWidget(self.stack.widget(1))

        self.detail_page = DetailWindow(
            idea_id,
            dark_mode=self.dark_mode,
            on_back=self.show_list,
            on_theme_change=self.set_theme
        )
        self.stack.addWidget(self.detail_page)
        self.stack.setCurrentIndex(1)

    def set_theme(self, dark_mode):
        self.dark_mode = dark_mode
        self.apply_theme()

    def show_list(self):
        self.stack.setCurrentIndex(0)
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
        self.table.setRowHeight(row, 54)
        self.table.setItem(row, 0, QTableWidgetItem(f"#{idea['id']}"))
        self.table.setItem(row, 1, QTableWidgetItem(idea['title']))
        self.table.setItem(row, 2, QTableWidgetItem(idea['time']['created']))
        delete_btn = QPushButton("Löschen")
        delete_btn.setFixedHeight(28)
        delete_btn.setStyleSheet(
            "QPushButton { color: #e24b4a; border: 1px solid #f0d0d0; border-radius: 6px; background: transparent; font-size: 12px; padding: 0 10px; }"
            "QPushButton:hover { background-color: #fff0f0; }"
        )
        delete_btn.clicked.connect(lambda _, id=idea['id']: self.delete_idea(id))
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(4, 0, 4, 0)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(delete_btn)
        self.table.setCellWidget(row, 3, container)

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

    def open_graph(self):
        from gui.graph import GraphWindow
        if self.stack.count() > 1:
            self.stack.removeWidget(self.stack.widget(1))
        self.graph_page = GraphWindow(
            dark_mode=self.dark_mode,
            on_back=self.show_list,
            on_theme_change=self.set_theme
        )
        self.stack.addWidget(self.graph_page)
        self.stack.setCurrentIndex(1)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())