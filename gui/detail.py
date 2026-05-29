# gui/detail.py
import markdown
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QTextBrowser, QLabel,
    QComboBox, QLineEdit, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from core.ideas import get_idea, update_idea, update_idea_meta, track_view

class DetailWindow(QWidget):
    def __init__(self, idea_id, dark_mode=False, on_back=None, on_theme_change=None):
        super().__init__()
        self.idea_id = get_idea(idea_id)
        self.dark_mode = dark_mode
        self.preview_visible = False
        self.on_back = on_back
        self.idea = get_idea(idea_id)
        self.on_theme_change = on_theme_change


        self.setWindowTitle(self.idea['title'])
        self.setMinimumSize(900, 650)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton("← Zurück")
        back_btn.setObjectName("back_btn")
        back_btn.clicked.connect(self.on_back if on_back else self.close)
        self.theme_btn = QPushButton("☀" if self.dark_mode else "☾")
        self.theme_btn.setObjectName("theme_btn")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header.addWidget(back_btn)
        header.addStretch()
        header.addWidget(self.theme_btn)
        layout.addLayout(header)

        # Titel + Datum
        title = QLabel(self.idea['title'])
        title.setObjectName("detail_title")
        layout.addWidget(title)

        date = QLabel(self.idea['time']['created'])
        date.setObjectName("detail_date")
        layout.addWidget(date)

        meta_widget = self._build_meta_section()
        layout.addWidget(meta_widget)

        # Action Buttons
        actions = QHBoxLayout()
        self.copy_btn = QPushButton("⎘ Kopieren")
        self.copy_btn.setObjectName("action_btn")
        self.copy_btn.clicked.connect(self.copy_content)

        self.preview_btn = QPushButton("◎ Vorschau")
        self.preview_btn.setObjectName("action_btn")
        self.preview_btn.clicked.connect(self.toggle_preview)

        save_btn = QPushButton("Speichern")
        save_btn.setObjectName("action_btn")
        save_btn.clicked.connect(self.save)

        actions.addWidget(self.copy_btn)
        actions.addWidget(self.preview_btn)
        actions.addStretch()
        actions.addWidget(save_btn)
        layout.addLayout(actions)

        # Editor + Vorschau
        editor_row = QHBoxLayout()

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Idee ausarbeiten...")
        self.editor.setText(self.idea.get('content', ''))
        self.editor.textChanged.connect(self.on_text_changed)
        editor_row.addWidget(self.editor)

        self.preview = QTextBrowser()
        self.preview.setVisible(False)
        editor_row.addWidget(self.preview)

        layout.addLayout(editor_row)
        self.apply_theme()

    def apply_theme(self):
        import PyQt6.QtWidgets as w
        from gui.styles import DARK, LIGHT
        w.QApplication.instance().setStyleSheet(DARK if self.dark_mode else LIGHT)
        self.theme_btn.setText("☀" if self.dark_mode else "☾")

    def toggle_preview(self):
        self.preview_visible = not self.preview_visible
        self.preview.setVisible(self.preview_visible)
        self.preview_btn.setText("◉ Vorschau aus" if self.preview_visible else "◎ Vorschau")
        if self.preview_visible:
            self.update_preview()

    def update_preview(self):
        html = markdown.markdown(self.editor.toPlainText())
        self.preview.setHtml(html)

    def on_text_changed(self):
        if self.preview_visible:
            self.update_preview()

    def save(self):
        update_idea(self.idea_id, self.editor.toPlainText())

    def copy_content(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.editor.toPlainText())
        self.copy_btn.setText("✓ Kopiert!")
        QTimer.singleShot(3000, lambda: self.copy_btn.setText("⎘ Kopieren"))

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText("☀" if self.dark_mode else "☾")
        if self.on_theme_change:
            self.on_theme_change(self.dark_mode)

    def _build_meta_section(self):
        group = QGroupBox()
        form = QHBoxLayout(group)
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(16)

        # Status
        status_col = QVBoxLayout()
        status_label = QLabel("Status")
        status_label.setObjectName("meta_label")
        self.status_cb = QComboBox()
        self.status_cb.addItems(["raw", "refined", "applied", "archived"])
        self.status_cb.setCurrentText(self.idea.get("context", {}).get("status", "raw"))
        status_col.addWidget(status_label)
        status_col.addWidget(self.status_cb)
        form.addLayout(status_col)

        # Importance
        imp_col = QVBoxLayout()
        imp_label = QLabel("Wichtigkeit")
        imp_label.setObjectName("meta_label")
        self.importance_cb = QComboBox()
        self.importance_cb.addItems(["1", "2", "3", "4", "5"])
        self.importance_cb.setCurrentText(str(self.idea.get("context", {}).get("importance", 1)))
        imp_col.addWidget(imp_label)
        imp_col.addWidget(self.importance_cb)
        form.addLayout(imp_col)

        # Energy
        energy_col = QVBoxLayout()
        energy_label = QLabel("Energie")
        energy_label.setObjectName("meta_label")
        self.energy_cb = QComboBox()
        self.energy_cb.addItems(["low", "medium", "high"])
        self.energy_cb.setCurrentText(self.idea.get("context", {}).get("energy", "medium"))
        energy_col.addWidget(energy_label)
        energy_col.addWidget(self.energy_cb)
        form.addLayout(energy_col)

        # Tags
        tags_col = QVBoxLayout()
        tags_label = QLabel("Tags")
        tags_label.setObjectName("meta_label")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("ki, business, idee")
        self.tags_input.setText(", ".join(self.idea.get("tags", [])))
        tags_col.addWidget(tags_label)
        tags_col.addWidget(self.tags_input)
        form.addLayout(tags_col)

        # Speichern
        save_meta_btn = QPushButton("Speichern")
        save_meta_btn.setObjectName("action_btn")
        save_meta_btn.clicked.connect(self.save_meta)
        form.addWidget(save_meta_btn)
        form.setAlignment(save_meta_btn, Qt.AlignmentFlag.AlignBottom)

        return group

    def save_meta(self):
        tags = [t.strip() for t in self.tags_input.text().split(",") if t.strip()]
        context = {
            "status": self.status_cb.currentText(),
            "importance": int(self.importance_cb.currentText()),
            "energy": self.energy_cb.currentText()
        }
        update_idea_meta(self.idea["id"], tags=tags, context=context)