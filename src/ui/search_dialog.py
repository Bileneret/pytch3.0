import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QLabel, QAbstractItemView, QWidget
)
from PyQt5.QtCore import Qt, QSize
from src.models import LearningGoal

import faulthandler
faulthandler.enable()


class SearchDialog(QDialog):
    def __init__(self, parent, goals: list[LearningGoal], storage):
        super().__init__(parent)
        self.setWindowTitle("Пошук цілей 🔍")
        self.resize(500, 600)
        self.storage = storage

        self.goals = sorted(goals, key=lambda g: g.title.lower())

        self.goals_data = []
        for g in self.goals:
            subs = self.storage.get_subgoals(g.id)
            self.goals_data.append({
                "goal": g,
                "subgoals": subs
            })

        self.selected_goal_id = None
        self.setup_ui()
        self.update_list("")

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }

            QListWidget {
                background-color: #111827;
                border: 2px solid #1e3a8a;
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #1e293b;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #1d4ed8;
                border: 1px solid #60a5fa;
                border-radius: 4px;
            }

            QLineEdit {
                background-color: #172a45;
                color: white;
                border: 2px solid #1e4976;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Введіть текст (шукає в цілях та підцілях)...")
        self.input_search.textChanged.connect(self.update_list)
        layout.addWidget(self.input_search)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)

        self.input_search.setFocus()

    def update_list(self, text):
        self.list_widget.clear()
        query = text.strip()

        for item_data in self.goals_data:
            goal = item_data["goal"]
            subgoals = item_data["subgoals"]
            match_found = False

            title_html = goal.title
            desc_html = goal.description if goal.description else ""
            found_subs_html = []

            if not query:
                match_found = True
            else:
                hl_title = self._highlight_text(query, goal.title)
                if hl_title:
                    title_html = hl_title
                    match_found = True

                hl_desc = self._highlight_text(query, goal.description)
                if hl_desc:
                    desc_html = hl_desc
                    match_found = True

                for sub in subgoals:
                    hl_sub_title = self._highlight_text(query, sub.title)
                    hl_sub_desc = self._highlight_text(query, sub.description)
                    if hl_sub_title or hl_sub_desc:
                        match_found = True
                        display_sub = f"• {hl_sub_title if hl_sub_title else sub.title}"
                        if hl_sub_desc:
                            display_sub += f" <span style='color:#7f8c8d'>({hl_sub_desc})</span>"
                        found_subs_html.append(display_sub)

            if match_found:
                item = QListWidgetItem()
                item.setData(Qt.UserRole, goal.id)

                display_html = f"<div style='font-weight: bold; font-size: 15px; color: white;'>{title_html}</div>"
                if desc_html:
                    display_html += f"<div style='color: #94a3b8; font-size: 13px; margin-top: 4px;'>{desc_html}</div>"
                if found_subs_html:
                    subs_str = "<br>".join(found_subs_html)
                    display_html += f"<div style='color: #a78bfa; font-size: 12px; margin-top: 6px; font-style: italic;'>Знайдено у підцілях:<br>{subs_str}</div>"

                lbl = QLabel(display_html)
                lbl.setWordWrap(True)
                lbl.setTextFormat(Qt.RichText)
                lbl.setStyleSheet("background: transparent;")

                base_height = 60
                if found_subs_html:
                    base_height += len(found_subs_html) * 20
                item.setSizeHint(QSize(400, base_height))

                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, lbl)

    def _highlight_text(self, query, text):
        if not text or not query: return None
        pattern = re.compile(f"({re.escape(query)})", re.IGNORECASE)
        if pattern.search(text):
            return pattern.sub(r'<span style="background-color: #7c3aed; color: white; font-weight: bold;">\1</span>',
                               text)
        return None

    def on_item_clicked(self, item):
        self.selected_goal_id = item.data(Qt.UserRole)

    def on_item_double_clicked(self, item):
        self.selected_goal_id = item.data(Qt.UserRole)
        self.accept()