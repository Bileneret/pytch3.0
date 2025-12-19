from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QListWidget,
                             QListWidgetItem, QLabel)
from PyQt5.QtCore import Qt


class SearchDialog(QDialog):
    def __init__(self, parent, goals):
        super().__init__(parent)
        self.goals = goals
        self.selected_goal_id = None

        self.setWindowTitle("Пошук цілей 🔍")
        self.resize(400, 500)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: white; font-family: 'Segoe UI'; }
            QLineEdit { 
                background-color: #172a45; color: white; border: 1px solid #1e4976; 
                padding: 10px; border-radius: 6px; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #3b82f6; }

            QListWidget { 
                background-color: #111827; border: 1px solid #1e4976; 
                border-radius: 6px; padding: 5px; outline: none;
            }
            QListWidget::item { 
                padding: 10px; border-bottom: 1px solid #1e293b; color: #e0e0e0;
            }
            QListWidget::item:hover { background-color: #1e3a8a; }
            QListWidget::item:selected { background-color: #2563eb; color: white; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Введіть назву цілі:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук...")
        self.search_input.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_input)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.results_list)

        self.setLayout(layout)
        self.populate_list(self.goals)

    def populate_list(self, goals):
        self.results_list.clear()
        for goal in goals:
            item = QListWidgetItem(f"{goal.title}")
            item.setData(Qt.UserRole, goal.id)
            self.results_list.addItem(item)

    def filter_list(self, text):
        filtered_goals = [g for g in self.goals if text.lower() in g.title.lower()]
        self.populate_list(filtered_goals)

    def on_item_clicked(self, item):
        self.selected_goal_id = item.data(Qt.UserRole)
        self.accept()