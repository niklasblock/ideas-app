# gui/recall.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from core.ideas import get_unseen_ideas, get_random_idea, get_unlinked_ideas

class RecallWindow(QWidget):
    def __init__(self, dark_mode=False, on_back=None, on_theme_change=None, on_idea_open=None):
        super().__init__()
        self.dark_mode = dark_mode
        self.on_back = on_back
        self.on_theme_change = on_theme_change
        self.on_idea_open = on_idea_open

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton("← Zurück")
        back_btn.setObjectName("back_btn")
        back_btn.clicked.connect(on_back if on_back else self.close)
        self.theme_btn = QPushButton("☀" if dark_mode else "☾")
        self.theme_btn.setObjectName("theme_btn")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header.addWidget(back_btn)
        header.addStretch()
        header.addWidget(self.theme_btn)
        layout.addLayout(header)

        title = QLabel("Recall")
        title.setObjectName("detail_title")
        layout.addWidget(title)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(24)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        self._build_content()
        self.apply_theme()

    def _build_content(self):
        # Zufällige Idee
        self._add_section("Zufällige Idee", [get_random_idea()] if get_random_idea() else [], show_refresh=True)
        # Lange nicht gesehen
        self._add_section("Lange nicht gesehen", get_unseen_ideas(days=7))
        # Unverknüpft
        self._add_section("Unverknüpfte Ideen", get_unlinked_ideas())

    def _add_section(self, title, ideas, show_refresh=False):
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(8)
        section_layout.setContentsMargins(0, 0, 0, 0)

        header_row = QHBoxLayout()
        title_lbl = QLabel(f"{title}  ({len(ideas)})" if not show_refresh else title)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 500;")
        header_row.addWidget(title_lbl)
        if show_refresh:
            refresh_btn = QPushButton("↻")
            refresh_btn.setObjectName("action_btn")
            refresh_btn.setFixedWidth(36)
            refresh_btn.clicked.connect(self._refresh)
            header_row.addWidget(refresh_btn)
        header_row.addStretch()
        section_layout.addLayout(header_row)

        if ideas and ideas[0] is not None:
            for idea in ideas:
                card = self._make_card(idea)
                section_layout.addWidget(card)
        else:
            empty = QLabel("Keine Ideen")
            empty.setStyleSheet("color: #aaa; font-size: 13px;")
            section_layout.addWidget(empty)

        self.content_layout.addWidget(section)

    def _make_card(self, idea):
        card = QWidget()
        card.setStyleSheet(
            "QWidget { background: white; border: 1px solid #e0e0e0; border-radius: 10px; }"
        )
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)

        title = QPushButton(idea["title"])
        title.setObjectName("action_btn")
        title.setStyleSheet("text-align: left; font-size: 13px; font-weight: 500; border: none;")
        title.clicked.connect(lambda _, id=idea["id"]: self.on_idea_open(id) if self.on_idea_open else None)

        status = QLabel(idea.get("context", {}).get("status", "raw"))
        status.setStyleSheet("color: #aaa; font-size: 11px;")

        date = QLabel(idea.get("time", {}).get("last_viewed", ""))
        date.setStyleSheet("color: #aaa; font-size: 11px;")

        card_layout.addWidget(title)
        card_layout.addStretch()
        card_layout.addWidget(status)
        card_layout.addWidget(date)

        return card

    def _refresh(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._build_content()

    def apply_theme(self):
        from gui.styles import DARK, LIGHT
        self.setStyleSheet(DARK if self.dark_mode else LIGHT)
        self.theme_btn.setText("☀" if self.dark_mode else "☾")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.on_theme_change:
            self.on_theme_change(self.dark_mode)
        self.apply_theme()