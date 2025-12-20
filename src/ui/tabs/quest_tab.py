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
        self.sort_combo.addItems(["Сорт: Дедлайн", "Сорт: Пріоритет", "Сорт: Статус"])
        self.sort_combo.setFixedWidth(150)
        self.sort_combo.setStyleSheet(
            "background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; border-radius: 4px;")
        self.sort_combo.currentIndexChanged.connect(self.update_list)

        self.cat_filter = QComboBox()
        self.cat_filter.addItem("Всі категорії", None)
        self.cat_filter.setFixedWidth(150)
        self.cat_filter.setStyleSheet(
            "background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; border-radius: 4px;")
        self.cat_filter.currentIndexChanged.connect(self.update_list)

        filters = QHBoxLayout()
        filters.addWidget(self.sort_combo)
        filters.addWidget(self.cat_filter)
        title_layout.addLayout(filters)

        header.addLayout(title_layout)
        header.addStretch()
        self.layout.insertLayout(0, header)

    def load_categories(self):
        current = self.cat_filter.currentData()
        self.cat_filter.blockSignals(True)
        self.cat_filter.clear()
        self.cat_filter.addItem("Всі категорії", None)
        cats = self.mw.storage.get_categories(self.mw.user_id)
        for c in cats:
            self.cat_filter.addItem(c.name, c.id)
        if current:
            idx = self.cat_filter.findData(current)
            if idx >= 0: self.cat_filter.setCurrentIndex(idx)
        self.cat_filter.blockSignals(False)

    def setup_footer(self):
        footer = QHBoxLayout()
        footer.setContentsMargins(10, 10, 10, 10)
        btn_style = "QPushButton { background-color: #1e3a8a; color: white; border: 2px solid #3b82f6; border-radius: 8px; padding: 10px 15px; font-weight: bold; }"

        btn_add = QPushButton("➕ Нова Ціль")
        btn_add.setStyleSheet(btn_style)
        btn_add.clicked.connect(self.add_goal)

        btn_ai = QPushButton("✨ ШІ Ціль")
        btn_ai.setStyleSheet(
            "QPushButton { background-color: #7c3aed; color: white; border: 2px solid #8b5cf6; border-radius: 8px; padding: 10px 15px; font-weight: bold; }")
        btn_ai.clicked.connect(self.open_ai_dialog)

        btn_refresh = QPushButton("🔄 Оновити")
        btn_refresh.setStyleSheet(btn_style)
        btn_refresh.clicked.connect(self.update_list)

        btn_search = QPushButton("🔍 Пошук")
        btn_search.setStyleSheet(btn_style)
        btn_search.clicked.connect(self.open_search)

        btn_cleanup = QPushButton("🗑 Автовидалення")
        btn_cleanup.setStyleSheet(
            "QPushButton { background-color: #7f1d1d; color: white; border: 2px solid #b91c1c; border-radius: 8px; padding: 10px 15px; font-weight: bold; }")
        btn_cleanup.clicked.connect(self.auto_cleanup)

        footer.addWidget(btn_add)
        footer.addWidget(btn_ai)
        footer.addWidget(btn_refresh)
        footer.addWidget(btn_search)
        footer.addStretch()
        footer.addWidget(btn_cleanup)
        self.layout.addLayout(footer)

    def on_sort_change(self):
        self.pinned_goal_id = None
        self.update_list()

    def update_list(self):
        self.load_categories()
        self.clear_list()
        goals = self.mw.storage.get_goals(self.mw.user_id)

        cat_id = self.cat_filter.currentData()
        if cat_id: goals = [g for g in goals if g.category_id == cat_id]

        sort_mode = self.sort_combo.currentText()
        if "Статус" in sort_mode:
            goals.sort(key=lambda x: x.status == GoalStatus.COMPLETED)
        elif "Пріоритет" in sort_mode:
            goals.sort(key=lambda x: x.priority.name)
        elif "Дедлайн" in sort_mode:
            goals.sort(key=lambda x: x.deadline if x.deadline else "9999-99-99")

        if not goals:
            lbl = QLabel("Список порожній")
            lbl.setStyleSheet("color: gray; font-size: 16px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(lbl)
            return

        target_card = None
        if self.pinned_goal_id:
            pinned = next((g for g in goals if g.id == self.pinned_goal_id), None)
            if pinned:
                goals.remove(pinned)
                goals.insert(0, pinned)

        for goal in goals:
            card = QuestCard(goal, self)
            self.list_layout.addWidget(card)
            if self.pinned_goal_id and goal.id == self.pinned_goal_id:
                target_card = card

        if target_card and self.should_highlight:
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

            # ВИПРАВЛЕНО: Використовуємо self.scroll_area, створений в BaseTab
            if hasattr(self, 'scroll_area'):
                QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(0))

    def auto_cleanup(self):
        goals = self.mw.storage.get_goals(self.mw.user_id)
        completed_goals = [g for g in goals if g.status == GoalStatus.COMPLETED]
        if not completed_goals:
            QMessageBox.information(self.mw, "Автовидалення", "Немає виконаних цілей.")
            return

        count = len(completed_goals)
        reply = QMessageBox.question(self.mw, "Автовидалення", f"Видалити всі виконані цілі ({count} шт.)?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for g in completed_goals:
                self.mw.storage.delete_goal(g.id)
            self.pinned_goal_id = None
            self.update_list()