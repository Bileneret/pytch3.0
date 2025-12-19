from PyQt5.QtWidgets import QLabel, QPushButton, QHBoxLayout, QMessageBox, QVBoxLayout
from PyQt5.QtCore import Qt
from .base_tab import BaseTab
from ..cards import QuestCard
from ..edit_goal_dialog import EditGoalDialog
from ...models import GoalStatus


class QuestTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.setup_header()
        self.setup_footer()
        self.update_list()

    def setup_header(self):
        header = QHBoxLayout()
        header.setContentsMargins(10, 10, 10, 0)
        title = QLabel("Мої Цілі")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        header.addWidget(title)
        header.addStretch()
        self.layout.insertLayout(0, header)

    def setup_footer(self):
        footer = QHBoxLayout()
        footer.setContentsMargins(10, 10, 10, 10)

        btn_style = """
            QPushButton { 
                background-color: #1e3a8a; color: white; border: 2px solid #3b82f6; 
                border-radius: 8px; padding: 10px 15px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #2563eb; }
        """

        # Кнопка ШІ (Фіолетова)
        ai_style = """
            QPushButton { 
                background-color: #7c3aed; color: white; border: 2px solid #8b5cf6; 
                border-radius: 8px; padding: 10px 15px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #8b5cf6; }
        """

        btn_add = QPushButton("+ Нова Ціль")
        btn_add.setStyleSheet(btn_style)
        btn_add.clicked.connect(self.add_goal)

        # ПОВЕРНУТО КНОПКУ ШІ
        btn_ai = QPushButton("✨ ШІ Ціль")
        btn_ai.setStyleSheet(ai_style)
        btn_ai.clicked.connect(lambda: QMessageBox.information(self.mw, "AI", "ШІ генерація цілей скоро!"))

        btn_refresh = QPushButton("🔄 Оновити")
        btn_refresh.setStyleSheet(btn_style)
        btn_refresh.clicked.connect(self.update_list)

        btn_search = QPushButton("🔍 Пошук")
        btn_search.setStyleSheet(btn_style)
        btn_search.clicked.connect(lambda: QMessageBox.information(self.mw, "Інфо", "Пошук в розробці"))

        btn_cleanup = QPushButton("🗑 Автовидалення")
        btn_cleanup.setStyleSheet("""
            QPushButton { 
                background-color: #7f1d1d; color: white; border: 2px solid #b91c1c; 
                border-radius: 8px; padding: 10px 15px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #991b1b; }
        """)
        btn_cleanup.clicked.connect(lambda: QMessageBox.information(self.mw, "Інфо", "Автовидалення виконаних"))

        footer.addWidget(btn_add)
        footer.addWidget(btn_ai)  # Додано
        footer.addWidget(btn_refresh)
        footer.addWidget(btn_search)
        footer.addStretch()
        footer.addWidget(btn_cleanup)

        self.layout.addLayout(footer)

    def update_list(self):
        self.clear_list()
        goals = self.mw.storage.get_goals(self.mw.user_id)
        goals.sort(key=lambda x: x.status == GoalStatus.COMPLETED)

        if not goals:
            lbl = QLabel("Список порожній")
            lbl.setStyleSheet("color: gray; font-size: 16px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(lbl)
            return

        for goal in goals:
            card = QuestCard(goal, self)
            self.list_layout.addWidget(card)

    def add_goal(self):
        dialog = EditGoalDialog(self.mw, user_id=self.mw.user_id, storage=self.mw.storage)
        if dialog.exec_():
            self.update_list()