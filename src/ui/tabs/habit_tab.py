from PyQt5.QtWidgets import QLabel, QPushButton, QHBoxLayout, QMessageBox, QVBoxLayout, QComboBox
from PyQt5.QtCore import Qt, QTimer
from .base_tab import BaseTab
from ..cards import HabitCard
from ..edit_habit_dialog import EditHabitDialog
from ..search_dialog import SearchDialog
from ...models import Habit


class HabitTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.pinned_habit_id = None
        self.should_highlight = False
        self.setup_header()
        self.setup_footer()
        self.update_list()

    def setup_header(self):
        header = QHBoxLayout()
        header.setContentsMargins(10, 10, 10, 0)
        title_layout = QVBoxLayout()
        title = QLabel("Трекер Звичок")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        title_layout.addWidget(title)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сортувати за: Назвою", "Сортувати за: Серією"])
        self.sort_combo.setFixedWidth(200)
        self.sort_combo.setStyleSheet(
            "QComboBox { background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; border-radius: 4px; padding: 4px; font-size: 12px; } QComboBox::drop-down { border: none; }")
        self.sort_combo.currentIndexChanged.connect(self.on_sort_change)
        title_layout.addWidget(self.sort_combo)
        header.addLayout(title_layout)
        header.addStretch()
        self.layout.insertLayout(0, header)

    def setup_footer(self):
        footer = QHBoxLayout()
        footer.setContentsMargins(10, 10, 10, 10)
        btn_style = "QPushButton { background-color: #1e3a8a; color: white; border: 2px solid #3b82f6; border-radius: 8px; padding: 10px 15px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #2563eb; }"

        btn_add = QPushButton("➕ Нова Звичка")
        btn_add.setStyleSheet(btn_style)
        btn_add.clicked.connect(self.add_habit)

        btn_refresh = QPushButton("🔄 Оновити")
        btn_refresh.setStyleSheet(btn_style)
        btn_refresh.clicked.connect(self.update_list)

        btn_search = QPushButton("🔍 Пошук")
        btn_search.setStyleSheet(btn_style)
        btn_search.clicked.connect(self.open_search)

        btn_cleanup = QPushButton("🗑 Автовидалення")
        btn_cleanup.setStyleSheet(
            "QPushButton { background-color: #7f1d1d; color: white; border: 2px solid #b91c1c; border-radius: 8px; padding: 10px 15px; font-weight: bold; font-size: 13px; }")
        btn_cleanup.clicked.connect(self.auto_cleanup)

        footer.addWidget(btn_add)
        footer.addWidget(btn_refresh)
        footer.addWidget(btn_search)
        footer.addStretch()
        footer.addWidget(btn_cleanup)
        self.layout.addLayout(footer)

    def on_sort_change(self):
        self.pinned_habit_id = None
        self.should_highlight = False
        self.update_list()

    def update_list(self):
        self.clear_list()
        habits = self.mw.storage.get_habits(self.mw.user_id)
        mode = self.sort_combo.currentText()
        if "Серією" in mode:
            habits.sort(key=lambda h: h.streak, reverse=True)
        else:
            habits.sort(key=lambda h: h.title)

        if not habits:
            lbl = QLabel("Немає звичок")
            lbl.setStyleSheet("color: gray; font-size: 16px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(lbl)
            return

        target_card = None
        if self.pinned_habit_id:
            pinned = next((h for h in habits if h.id == self.pinned_habit_id), None)
            if pinned:
                habits.remove(pinned)
                habits.insert(0, pinned)

        for habit in habits:
            card = HabitCard(habit, self)
            self.list_layout.addWidget(card)
            if self.pinned_habit_id and habit.id == self.pinned_habit_id:
                target_card = card

        if target_card and self.should_highlight:
            QTimer.singleShot(100, target_card.highlight_card)
            self.should_highlight = False

    def add_habit(self):
        dialog = EditHabitDialog(self.mw, user_id=self.mw.user_id, storage=self.mw.storage)
        if dialog.exec_():
            self.pinned_habit_id = None
            self.update_list()

    def open_search(self):
        habits = self.mw.storage.get_habits(self.mw.user_id)
        if not habits:
            QMessageBox.information(self.mw, "Пошук", "Список звичок порожній.")
            return

        dialog = SearchDialog(self.mw, habits, self.mw.storage)
        if dialog.exec_() and dialog.selected_goal_id:
            self.pinned_habit_id = dialog.selected_goal_id
            self.should_highlight = True
            self.update_list()
            # ВИПРАВЛЕНО
            if hasattr(self, 'scroll_area'):
                QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(0))

    def auto_cleanup(self):
        QMessageBox.information(self.mw, "Інфо", "Для звичок автовидалення поки не застосовується.")