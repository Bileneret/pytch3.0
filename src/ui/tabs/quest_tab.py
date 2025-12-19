from PyQt5.QtWidgets import QLabel, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from .base_tab import BaseTab
from ..cards import QuestCard
from ..edit_goal_dialog import EditGoalDialog
from ...models import GoalStatus


class QuestTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.setup_header()
        self.update_list()

    def setup_header(self):
        # Панель кнопок зверху (Додати, ШІ)
        header = QHBoxLayout()
        header.setContentsMargins(10, 10, 10, 0)

        title = QLabel("Мої Цілі")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        btn_add = QPushButton("+ Нова Ціль")
        btn_add.setProperty("class", "actionBtn")
        btn_add.clicked.connect(self.add_goal)

        btn_ai = QPushButton("✨ ШІ Ціль")
        btn_ai.setProperty("class", "aiBtn")
        btn_ai.clicked.connect(lambda: QMessageBox.information(self, "AI", "ШІ генерація скоро!"))

        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_add)
        header.addWidget(btn_ai)

        # Додаємо хедер ПЕРЕД скролом (insertWidget 0)
        self.layout.insertLayout(0, header)

    def update_list(self):
        self.clear_list()
        goals = self.mw.storage.get_goals(self.mw.user_id)

        # Сортуємо: спочатку активні
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