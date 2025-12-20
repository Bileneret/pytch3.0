from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QColor, QFont, QBrush
from datetime import datetime, timedelta
from .base_tab import BaseTab
from ..edit_habit_dialog import EditHabitDialog
from ..search_dialog import SearchDialog


class HabitTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.mw = main_window

        today = QDate.currentDate()
        self.monday = today.addDays(-(today.dayOfWeek() - 1))

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # === 1. HEADER (Fixed Top) ===
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(10, 10, 10, 0)
        header_layout.setSpacing(10)

        # Title
        title = QLabel("Трекер Звичок")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        header_layout.addWidget(title)

        # Controls Row (Sort + Nav)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)

        # Sort Combo (Style like QuestTab)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сорт: Серія", "Сорт: Назва"])
        self.sort_combo.setFixedWidth(150)
        self.sort_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e3a8a; color: white; border: 1px solid #3b82f6;
                border-radius: 4px; padding: 4px; font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.sort_combo.currentIndexChanged.connect(self.load_data)
        controls_layout.addWidget(self.sort_combo)

        # Week Navigation
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(8)

        btn_prev = QPushButton("◀")
        btn_prev.setFixedSize(30, 24)
        btn_prev.setStyleSheet(
            "QPushButton { background-color: #1e3a8a; color: white; border-radius: 4px; border: 1px solid #3b82f6; } QPushButton:hover { background-color: #2563eb; }")
        btn_prev.clicked.connect(lambda: self.change_week(-1))

        self.lbl_week_range = QLabel()
        self.lbl_week_range.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: bold;")
        self.lbl_week_range.setAlignment(Qt.AlignCenter)
        self.lbl_week_range.setFixedWidth(110)

        btn_next = QPushButton("▶")
        btn_next.setFixedSize(30, 24)
        btn_next.setStyleSheet(
            "QPushButton { background-color: #1e3a8a; color: white; border-radius: 4px; border: 1px solid #3b82f6; } QPushButton:hover { background-color: #2563eb; }")
        btn_next.clicked.connect(lambda: self.change_week(1))

        nav_layout.addWidget(btn_prev)
        nav_layout.addWidget(self.lbl_week_range)
        nav_layout.addWidget(btn_next)

        controls_layout.addWidget(nav_widget)
        controls_layout.addStretch()  # Push everything to the left

        header_layout.addLayout(controls_layout)

        # Додаємо хедер у головний лейаут (над скролом)
        self.layout.insertWidget(0, header_container)

        # === 2. CONTENT (Scrollable Table) ===
        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(9)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #111827;
                border: 1px solid #1e3a8a;
                border-radius: 8px;
                gridline-color: #1e3a8a;
                color: #e0e0e0;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #94a3b8;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #3b82f6;
                font-weight: bold;
            }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected {
                background-color: #2563eb; 
                color: white;
            }
        """)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 8):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
            self.table.setColumnWidth(i, 60)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(8, 80)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setWordWrap(True)

        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        self.list_layout.addWidget(self.table)

        hint = QLabel(
            "💡 Подвійний клік по клітинці дня, щоб відмітити виконання. Подвійний клік по назві — редагувати.")
        hint.setStyleSheet("color: #64748b; margin-top: 5px; font-size: 12px;")
        hint.setAlignment(Qt.AlignCenter)
        self.list_layout.addWidget(hint)

        # === 3. FOOTER (Fixed Bottom) ===
        footer = QHBoxLayout()
        footer.setContentsMargins(10, 10, 10, 10)

        btn_style = "QPushButton { background-color: #1e3a8a; color: white; border: 2px solid #3b82f6; border-radius: 8px; padding: 10px 15px; font-weight: bold; } QPushButton:hover { background-color: #2563eb; }"

        btn_add = QPushButton("➕ Нова Звичка")
        btn_add.setStyleSheet(btn_style)
        btn_add.clicked.connect(self.add_habit)

        btn_refresh = QPushButton("🔄 Оновити")
        btn_refresh.setStyleSheet(btn_style)
        btn_refresh.clicked.connect(self.load_data)

        btn_search = QPushButton("🔍 Пошук")
        btn_search.setStyleSheet(btn_style)
        btn_search.clicked.connect(self.open_search)

        footer.addWidget(btn_add)
        footer.addWidget(btn_refresh)
        footer.addWidget(btn_search)
        footer.addStretch()

        # Додаємо футер у головний лейаут (під скролом)
        self.layout.addLayout(footer)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(10, self.table.resizeRowsToContents)

    def change_week(self, offset):
        self.monday = self.monday.addDays(offset * 7)
        self.load_data()

    def open_search(self):
        habits = self.mw.storage.get_habits(self.mw.user_id)
        if not habits:
            QMessageBox.information(self.mw, "Інфо", "Список звичок порожній")
            return

        dialog = SearchDialog(self.mw, habits, self.mw.storage)
        if dialog.exec_() and dialog.selected_goal_id:
            target_id = dialog.selected_goal_id
            for row in range(self.table.rowCount()):
                habit_data = self.table.item(row, 0).data(Qt.UserRole)
                if habit_data.id == target_id:
                    self.table.selectRow(row)
                    self.table.scrollToItem(self.table.item(row, 0))
                    return

    def load_data(self):
        self.table.setRowCount(0)

        sunday = self.monday.addDays(6)
        self.lbl_week_range.setText(f"{self.monday.toString('dd.MM')} - {sunday.toString('dd.MM')}")

        days_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
        headers = ["Звичка"]
        for i in range(7):
            day_date = self.monday.addDays(i)
            headers.append(f"{days_names[i]}\n{day_date.toString('dd.MM')}")
        headers.append("🔥 Серія")
        self.table.setHorizontalHeaderLabels(headers)

        habits = self.mw.storage.get_habits(self.mw.user_id)

        sort_mode = self.sort_combo.currentText()
        if "Назва" in sort_mode:
            habits.sort(key=lambda h: h.title.lower())
        else:
            habits.sort(key=lambda h: h.streak, reverse=True)

        start_str = self.monday.toString("yyyy-MM-dd")
        end_str = self.monday.addDays(6).toString("yyyy-MM-dd")

        for row_idx, habit in enumerate(habits):
            self.table.insertRow(row_idx)

            # Name
            name_item = QTableWidgetItem(habit.title)
            name_item.setData(Qt.UserRole, habit)
            name_item.setForeground(QBrush(QColor("white")))
            font = QFont()
            font.setBold(True)
            name_item.setFont(font)
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 0, name_item)

            logs = self.mw.storage.get_habit_logs(habit.id, start_str, end_str)

            # Days
            for day_idx in range(7):
                current_date = self.monday.addDays(day_idx)
                date_str = current_date.toString("yyyy-MM-dd")

                cell_item = QTableWidgetItem()
                cell_item.setTextAlignment(Qt.AlignCenter)

                if date_str in logs:
                    cell_item.setText("✅")
                    cell_item.setBackground(QColor("#064e3b"))
                else:
                    if current_date < QDate.currentDate():
                        cell_item.setText("—")
                        cell_item.setForeground(QBrush(QColor("#475569")))
                    elif current_date == QDate.currentDate():
                        cell_item.setBackground(QColor("#1e293b"))

                cell_item.setData(Qt.UserRole, date_str)
                self.table.setItem(row_idx, day_idx + 1, cell_item)

            # Streak
            streak_item = QTableWidgetItem(f"{habit.streak} 🔥")
            streak_item.setTextAlignment(Qt.AlignCenter)
            streak_item.setForeground(QBrush(QColor("#facc15")))
            self.table.setItem(row_idx, 8, streak_item)

        QTimer.singleShot(50, self.table.resizeRowsToContents)

    def on_cell_double_clicked(self, row, col):
        habit_item = self.table.item(row, 0)
        habit = habit_item.data(Qt.UserRole)

        if col == 0:
            dialog = EditHabitDialog(self.mw, habit, storage=self.mw.storage)
            if dialog.exec_():
                self.load_data()
        elif 1 <= col <= 7:
            cell_item = self.table.item(row, col)
            date_str = cell_item.data(Qt.UserRole)
            target_date = QDate.fromString(date_str, "yyyy-MM-dd")

            if target_date > QDate.currentDate():
                QMessageBox.warning(self.mw, "Упс!", "Не можна відмічати звички наперед.")
                return

            is_done = self.mw.storage.toggle_habit_date(habit.id, date_str)

            if is_done:
                cell_item.setText("✅")
                cell_item.setBackground(QColor("#064e3b"))
            else:
                if target_date < QDate.currentDate():
                    cell_item.setText("—")
                    cell_item.setBackground(QColor("#111827"))
                    cell_item.setForeground(QBrush(QColor("#475569")))
                else:
                    cell_item.setText("")
                    cell_item.setBackground(
                        QColor("#1e293b") if target_date == QDate.currentDate() else QColor("#111827"))

            updated_habit_list = self.mw.storage.get_habits(self.mw.user_id)
            new_streak = 0
            for h in updated_habit_list:
                if h.id == habit.id:
                    new_streak = h.streak
                    break

            streak_item = self.table.item(row, 8)
            streak_item.setText(f"{new_streak} 🔥")

    def add_habit(self):
        dialog = EditHabitDialog(self.mw, user_id=self.mw.user_id, storage=self.mw.storage)
        if dialog.exec_():
            self.load_data()