from PyQt5.QtWidgets import QLabel, QPushButton, QHBoxLayout, QInputDialog, QVBoxLayout, QComboBox
from PyQt5.QtCore import Qt
from .base_tab import BaseTab
from ..cards import HabitCard
from ...models import Habit




class HabitTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
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

        # Кнопка сортування
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сортувати за: Назвою", "Сортувати за: Серією"])
        self.sort_combo.setFixedWidth(200)
        self.sort_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e3a8a; color: white; border: 1px solid #3b82f6;
                border-radius: 4px; padding: 4px; font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.sort_combo.currentIndexChanged.connect(self.update_list)

        title_layout.addWidget(self.sort_combo)

        header.addLayout(title_layout)
        header.addStretch()
        self.layout.insertLayout(0, header)

    def setup_footer(self):
        footer = QHBoxLayout()
        footer.setContentsMargins(10, 10, 10, 10)

        btn_add = QPushButton("➕ Нова Звичка")
        btn_add.setProperty("class", "actionBtn")
        btn_add.clicked.connect(self.add_habit)

        footer.addWidget(btn_add)
        footer.addStretch()
        self.layout.addLayout(footer)

    def update_list(self):
        self.clear_list()
        habits = self.mw.storage.get_habits(self.mw.user_id)

        # Сортування
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

        info = QLabel("💡 Подвійний клік для виконання")
        info.setStyleSheet("color: #64748b; margin-left: 5px;")
        self.list_layout.addWidget(info)

        for habit in habits:
            card = HabitCard(habit, self)
            self.list_layout.addWidget(card)

    def add_habit(self):
        text, ok = QInputDialog.getText(self.mw, "Нова Звичка", "Назва:")
        if ok and text:
            new_habit = Habit(title=text, user_id=self.mw.user_id)
            self.mw.storage.save_habit(new_habit)
            self.update_list()