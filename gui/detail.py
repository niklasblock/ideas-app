# gui/detail.py
import markdown
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QTextBrowser, QLabel,
    QComboBox, QLineEdit, QFormLayout, QGroupBox, 
    QFrame 
)
from PyQt6.QtCore import Qt, QTimer
from core.ideas import (get_idea, update_idea, update_idea_meta,
                         add_link, remove_link, get_backlinks, list_ideas)

class DetailWindow(QWidget):
    def __init__(self, idea_id, dark_mode=False, on_back=None, on_theme_change=None):
        super().__init__()
        self.idea_id = idea_id  # einfach die ID speichern
        self.dark_mode = dark_mode
        self.preview_visible = False
        self.on_back = on_back
        self.idea = get_idea(idea_id)
        if not self.idea:
            print(f"Idee {idea_id} nicht gefunden")
            return
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

        # Titel + Datum + Meta + links 
        title = QLabel(self.idea['title'])
        title.setObjectName("detail_title")
        layout.addWidget(title)

        date = QLabel(self.idea['time']['created'])
        date.setObjectName("detail_date")
        layout.addWidget(date)

        meta_widget = self._build_meta_section()
        layout.addWidget(meta_widget)

        links_widget = self._build_links_section()
        layout.addWidget(links_widget)

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

    def _build_links_section(self):
        container = QWidget()
        outer = QHBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        # Verknüpfungen
        links_box = QGroupBox("Verknüpfungen")
        links_layout = QVBoxLayout(links_box)

        self.links_list = QVBoxLayout()
        links_layout.addLayout(self.links_list)
        self._refresh_links()

        # Neue Verknüpfung hinzufügen
        add_row = QHBoxLayout()
        self.link_type_cb = QComboBox()
        self.link_type_cb.addItems(["related", "inspired_by", "leads_to", "part_of"])
        self.link_target_cb = QComboBox()
        all_ideas = [i for i in list_ideas() if i["id"] != self.idea_id]
        for i in all_ideas:
            self.link_target_cb.addItem(i["title"], i["id"])
        add_link_btn = QPushButton("+ Verknüpfen")
        add_link_btn.setFixedWidth(100)
        add_link_btn.setObjectName("action_btn")
        add_link_btn.clicked.connect(self.add_link_action)
        add_row.addWidget(self.link_type_cb)
        add_row.addWidget(self.link_target_cb)
        add_row.addWidget(add_link_btn)
        links_layout.addLayout(add_row)
        outer.addWidget(links_box)

        # Backlinks
        backlinks_box = QGroupBox("Backlinks")
        backlinks_layout = QVBoxLayout(backlinks_box)
        backlinks = get_backlinks(self.idea_id)
        if backlinks:
            for b in backlinks:
                lbl = QLabel(b["title"])
                lbl.setStyleSheet("font-size: 13px;")
                backlinks_layout.addWidget(lbl)
        else:
            lbl = QLabel("Keine Backlinks")
            lbl.setStyleSheet("color: #aaa; font-size: 13px;")
            backlinks_layout.addWidget(lbl)
        backlinks_layout.addStretch()
        outer.addWidget(backlinks_box)

        return container

    def _refresh_links(self):
        while self.links_list.count():
            item = self.links_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.idea = get_idea(self.idea_id)  # immer frisch laden
        if not self.idea:
            return
        for link_type, ids in self.idea.get("links", {}).items():
            for linked_id in ids:
                linked = get_idea(linked_id)
                if linked:
                    row = QHBoxLayout()
                    row_widget = QWidget()
                    row_widget.setLayout(row)
                    type_lbl = QLabel(f"[{link_type}]")
                    type_lbl.setStyleSheet("color: #aaa; font-size: 11px;")
                    title_lbl = QLabel(linked["title"])
                    title_lbl.setStyleSheet("font-size: 13px;")
                    unlink_btn = QPushButton("✕")
                    unlink_btn.setFixedSize(24, 24)
                    unlink_btn.setStyleSheet("color: #e24b4a; border: none; background: transparent;")
                    unlink_btn.clicked.connect(lambda _, fid=self.idea_id, tid=linked_id, lt=link_type: self.remove_link_action(fid, tid, lt))
                    row.addWidget(type_lbl)
                    row.addWidget(title_lbl)
                    row.addStretch()
                    row.addWidget(unlink_btn)
                    self.links_list.addWidget(row_widget)

    def add_link_action(self):
        to_id = self.link_target_cb.currentData()
        link_type = self.link_type_cb.currentText()
        add_link(self.idea_id, to_id, link_type)
        self.idea = get_idea(self.idea_id)  # neu laden
        self._refresh_links()

    def remove_link_action(self, from_id, to_id, link_type):
        remove_link(from_id, to_id, link_type)
        self.idea = get_idea(self.idea_id)  # neu laden
        self._refresh_links()