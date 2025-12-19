from PyQt5.QtWidgets import QLabel, QPushButton, QHBoxLayout, QMessageBox, QVBoxLayout, QComboBox
from PyQt5.QtCore import Qt, QTimer
from .base_tab import BaseTab
from ..cards import QuestCard
from ..edit_goal_dialog import EditGoalDialog
from ..ai_goal_dialog import AIGoalDialog
from ..search_dialog import SearchDialog
from ...models import GoalStatus


class QuestTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)

        self.pinned_goal_id = None
        self.should_highlight = False

        self.setup_header()
        self.setup_footer()
        self.update_list()

    def setup_header(self):
        header = QHBoxLayout()
        header.setContentsMargins(10, 10, 10, 0)

        title_layout = QVBoxLayout()
        title = QLabel("Мої Цілі")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        title_layout.addWidget(title)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сортувати за: Дедлайном", "Сортувати за: Пріоритетом", "Сортувати за: Статусом"])
        self.sort_combo.setFixedWidth(200)
        self.sort_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e3a8a; color: white; border: 1px solid #3b82f6;
                border-radius: 4px; padding: 4px; font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.sort_combo.currentIndexChanged.connect(self.on_sort_change)

        title_layout.addWidget(self.sort_combo)

        header.addLayout(title_layout)
        header.addStretch()
        self.layout.insertLayout(0, header)

    def setup_footer(self):
        footer = QHBoxLayout()
        footer.setContentsMargins(10, 10, 10, 10)

        btn_style = "QPushButton { background-color: #1e3a8a; color: white; border: 2px solid #3b82f6; border-radius: 8px; padding: 10px 15px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #2563eb; }"
        ai_style = "QPushButton { background-color: #7c3aed; color: white; border: 2px solid #8b5cf6; border-radius: 8px; padding: 10px 15px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #8b5cf6; }"
        cleanup_style = "QPushButton { background-color: #7f1d1d; color: white; border: 2px solid #b91c1c; border-radius: 8px; padding: 10px 15px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #991b1b; }"

        btn_add = QPushButton("➕ Нова Ціль")
        btn_add.setStyleSheet(btn_style)
        btn_add.clicked.connect(self.add_goal)

        btn_ai = QPushButton("✨ ШІ Ціль")
        btn_ai.setStyleSheet(ai_style)
        btn_ai.clicked.connect(self.open_ai_dialog)

        btn_refresh = QPushButton("🔄 Оновити")
        btn_refresh.setStyleSheet(btn_style)
        btn_refresh.clicked.connect(self.update_list)

        btn_search = QPushButton("🔍 Пошук")
        btn_search.setStyleSheet(btn_style)
        btn_search.clicked.connect(self.open_search)

        btn_cleanup = QPushButton("🗑 Автовидалення")
        btn_cleanup.setStyleSheet(cleanup_style)
        btn_cleanup.clicked.connect(self.auto_cleanup)

        footer.addWidget(btn_add)
        footer.addWidget(btn_ai)
        footer.addWidget(btn_refresh)
        footer.addWidget(btn_search)
        footer.addStretch()
        footer.addWidget(btn_cleanup)

        self.layout.addLayout(footer)

    def on_sort_change(self):
        """При зміні сортування скасовуємо закріплення."""
        self.pinned_goal_id = None
        self.should_highlight = False
        self.update_list()

    def update_list(self):
        self.clear_list()
        goals = self.mw.storage.get_goals(self.mw.user_id)

        # Сортування
        sort_mode = self.sort_combo.currentText()
        if "Статусом" in sort_mode:
            goals.sort(key=lambda x: x.status == GoalStatus.COMPLETED)
        elif "Пріоритетом" in sort_mode:
            goals.sort(key=lambda x: x.priority.name)
        elif "Дедлайном" in sort_mode:
            goals.sort(key=lambda x: x.deadline if x.deadline else "9999-99-99")

        if not goals:
            lbl = QLabel("Список порожній")
            lbl.setStyleSheet("color: gray; font-size: 16px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(lbl)
            return

        # Логіка ЗАКРІПЛЕННЯ
        target_card = None

        if self.pinned_goal_id:
            pinned_goal = next((g for g in goals if g.id == self.pinned_goal_id), None)
            if pinned_goal:
                goals.remove(pinned_goal)
                goals.insert(0, pinned_goal)

        for goal in goals:
            card = QuestCard(goal, self)
            self.list_layout.addWidget(card)

            if self.pinned_goal_id and goal.id == self.pinned_goal_id:
                target_card = card

        # Підсвітка
        if target_card and self.should_highlight:
            # Викликаємо через таймер, щоб GUI встиг оновитися
            QTimer.singleShot(100, target_card.highlight_card)
            self.should_highlight = False

    def add_goal(self):
        dialog = EditGoalDialog(self.mw, user_id=self.mw.user_id, storage=self.mw.storage)
        if dialog.exec_():
            self.pinned_goal_id = None
            self.update_list()

    def open_ai_dialog(self):
        dialog = AIGoalDialog(self.mw, self.mw.user_id, self.mw.storage)
        if dialog.exec_():
            self.pinned_goal_id = None
            self.update_list()

    def open_search(self):
        goals = self.mw.storage.get_goals(self.mw.user_id)
        if not goals:
            QMessageBox.information(self.mw, "Пошук", "Список цілей порожній.")
            return

        dialog = SearchDialog(self.mw, goals, self.mw.storage)
        if dialog.exec_() and dialog.selected_goal_id:
            self.pinned_goal_id = dialog.selected_goal_id
            self.should_highlight = True
            self.update_list()

            # Безпечний скрол вгору
            if hasattr(self, 'scroll_area'):
                QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(0))

    def auto_cleanup(self):
        goals = self.mw.storage.get_goals(self.mw.user_id)
        completed_goals = [g for g in goals if g.status == GoalStatus.COMPLETED]

        if not completed_goals:
            QMessageBox.information(self.mw, "Автовидалення", "Немає виконаних цілей.")
            return

        count = len(completed_goals)
        reply = QMessageBox.question(self.mw, "Автовидалення",
                                     f"Видалити всі виконані цілі ({count} шт.)?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            for g in completed_goals:
                self.mw.storage.delete_goal(g.id)
            self.pinned_goal_id = None
            self.update_list()