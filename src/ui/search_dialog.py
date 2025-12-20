import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QLabel, QAbstractItemView, QWidget
)
from PyQt5.QtCore import Qt, QSize
from src.models import LearningGoal, Habit


class SearchDialog(QDialog):
    def __init__(self, parent, items: list, storage):
        super().__init__(parent)
        self.setWindowTitle("Пошук 🔍")
        self.resize(500, 600)
        self.storage = storage

        # Сортування
        self.items = sorted(items, key=lambda x: x.title.lower())

        # Кешування даних
        self.items_data = []
        for item in self.items:
            data = {"item": item, "subgoals": []}
            # Якщо це Ціль, вантажимо підцілі
            if isinstance(item, LearningGoal):
                data["subgoals"] = self.storage.get_subgoals(item.id)
            self.items_data.append(data)

        self.selected_goal_id = None  # Використовуємо це поле і для цілей, і для звичок
        self.setup_ui()
        self.update_list("")

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QListWidget { background-color: #111827; border: 2px solid #1e3a8a; border-radius: 8px; padding: 5px; outline: none; }
            QListWidget::item { border-bottom: 1px solid #1e293b; padding: 5px; }
            QListWidget::item:selected { background-color: #1d4ed8; border-radius: 4px; }
            QLineEdit { background-color: #172a45; color: white; border: 2px solid #1e4976; border-radius: 8px; padding: 10px; font-size: 14px; }
            QLineEdit:focus { border: 2px solid #3b82f6; }
        """)
        layout = QVBoxLayout(self)
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Введіть текст...")
        self.input_search.textChanged.connect(self.update_list)
        layout.addWidget(self.input_search)
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)
        self.input_search.setFocus()

    def update_list(self, text):
        self.list_widget.clear()
        query = text.strip()

        for data in self.items_data:
            item = data["item"]
            subgoals = data["subgoals"]
            match_found = False

            title_html = item.title
            desc_html = ""
            found_subs_html = []

            # Перевірка для LearningGoal
            if isinstance(item, LearningGoal):
                desc_html = item.description if item.description else ""

            if not query:
                match_found = True
            else:
                hl_t = self._highlight(query, item.title)
                if hl_t: title_html = hl_t; match_found = True

                if desc_html:
                    hl_d = self._highlight(query, desc_html)
                    if hl_d: desc_html = hl_d; match_found = True

                for sub in subgoals:
                    hl_s = self._highlight(query, sub.title)
                    if hl_s:
                        found_subs_html.append(f"• {hl_s}")
                        match_found = True

            if match_found:
                list_item = QListWidgetItem()
                list_item.setData(Qt.UserRole, item.id)

                icon = "🔥" if isinstance(item, Habit) else "🎯"
                display = f"<div style='font-weight:bold; font-size:15px; color:white;'>{icon} {title_html}</div>"
                if desc_html: display += f"<div style='color:#94a3b8; font-size:13px;'>{desc_html}</div>"
                if found_subs_html:
                    display += f"<div style='color:#a78bfa; font-size:12px; margin-top:4px;'>Знайдено: {', '.join(found_subs_html)}</div>"

                lbl = QLabel(display)
                lbl.setWordWrap(True)
                lbl.setTextFormat(Qt.RichText)
                lbl.setStyleSheet("background: transparent;")

                h = 60 + (20 * len(found_subs_html) if found_subs_html else 0)
                list_item.setSizeHint(QSize(400, h))

                self.list_widget.addItem(list_item)
                self.list_widget.setItemWidget(list_item, lbl)

    def _highlight(self, query, text):
        if not text or not query: return None
        pattern = re.compile(f"({re.escape(query)})", re.IGNORECASE)
        if pattern.search(text):
            return pattern.sub(r'<span style="background-color:#7c3aed; color:white;">\1</span>', text)
        return None

    def on_item_clicked(self, item):
        self.selected_goal_id = item.data(Qt.UserRole)

    def on_item_double_clicked(self, item):
        self.selected_goal_id = item.data(Qt.UserRole)
        self.accept()