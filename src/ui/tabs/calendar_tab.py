from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget,
                             QListWidget, QLabel, QListWidgetItem, QFrame)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QTextCharFormat, QBrush, QColor
from .base_tab import BaseTab
from datetime import datetime


class CalendarTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.setup_ui()
        self.highlight_dates()

    def setup_ui(self):
        # Header
        self.header = QLabel("📅 Календар Дедлайнів")
        self.header.setStyleSheet("font-size: 26px; font-weight: bold; color: white; margin-bottom: 15px;")
        self.list_layout.addWidget(self.header)

        # Main Layout (Horizontal: Calendar | List)
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # === 1. CALENDAR WIDGET (STANDARD) ===
        # Використовуємо звичайний QCalendarWidget - це найнадійніший варіант
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        # Стилізація
        self.calendar.setStyleSheet("""
            /* Фон самого календаря */
            QCalendarWidget QWidget { 
                background-color: #111827; 
                color: #e0e0e0;
                alternate-background-color: #111827;
            }

            /* Верхня панель (місяць/рік) */
            QCalendarWidget QWidget#qt_calendar_navigationbar { 
                background-color: #1e3a8a; 
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 5px;
            }

            /* Кнопки навігації */
            QCalendarWidget QToolButton {
                color: white;
                background-color: transparent;
                border: none;
                font-weight: bold;
                icon-size: 24px;
                padding: 5px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #2563eb;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton::menu-indicator { image: none; }

            /* Меню вибору місяця/року */
            QCalendarWidget QMenu, QCalendarWidget QSpinBox {
                background-color: #1e293b;
                color: white;
                border: 1px solid #3b82f6;
                selection-background-color: #3b82f6;
            }

            /* Сітка днів */
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #111827;
                color: #e0e0e0;
                selection-background-color: #3b82f6; 
                selection-color: white;
                font-size: 14px;
                border: 1px solid #1e3a8a;
                border-top: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                outline: 0;
            }

            /* Дні тижня (Пн, Вт...) */
            QCalendarWidget QTableView QHeaderView::section {
                background-color: #0f172a; 
                color: #94a3b8; 
                font-weight: bold;
                padding: 5px;
                border: none;
                border-bottom: 1px solid #1e3a8a;
            }
        """)

        self.calendar.clicked.connect(self.on_date_click)
        content_layout.addWidget(self.calendar, stretch=3)

        # === 2. DEADLINE LIST (RIGHT SIDE) ===
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #111827;
                border: 1px solid #1e3a8a;
                border-radius: 8px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)

        lbl_list = QLabel("Задачі на цей день:")
        lbl_list.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: bold; border: none;")
        right_layout.addWidget(lbl_list)

        self.day_list = QListWidget()
        self.day_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: #1e293b;
                border-radius: 6px;
                padding: 10px;
                margin-bottom: 5px;
                color: white;
                font-size: 13px;
            }
            QListWidget::item:hover {
                background-color: #2d3748;
            }
        """)
        # Підключаємо подвійний клік для переходу
        self.day_list.itemDoubleClicked.connect(self.on_item_double_click)

        right_layout.addWidget(self.day_list)

        content_layout.addWidget(right_panel, stretch=2)

        self.list_layout.addWidget(content_container)

    def highlight_dates(self):
        """Підсвітка дат з дедлайнами (Червоний фон)"""
        goals = self.mw.storage.get_goals(self.mw.user_id)

        # Створюємо формат: Червоний фон, білий жирний текст
        fmt_deadline = QTextCharFormat()
        fmt_deadline.setBackground(QBrush(QColor("#ef4444")))
        fmt_deadline.setForeground(QBrush(QColor("white")))
        fmt_deadline.setFontWeight(75)  # Bold

        # Скидаємо попередні формати
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        for g in goals:
            if g.deadline:
                try:
                    dt = datetime.strptime(g.deadline, "%Y-%m-%d")
                    qdate = QDate(dt.year, dt.month, dt.day)
                    # Застосовуємо формат до дати
                    self.calendar.setDateTextFormat(qdate, fmt_deadline)
                except:
                    pass

    def on_date_click(self, qdate):
        self.day_list.clear()
        selected_str = qdate.toString("yyyy-MM-dd")

        goals = self.mw.storage.get_goals(self.mw.user_id)
        found_tasks = []

        for g in goals:
            if g.deadline == selected_str:
                found_tasks.append(g)

        if found_tasks:
            for g in found_tasks:
                icon = "✅" if g.status.name == "COMPLETED" else "⏰"
                item = QListWidgetItem(f"{icon} {g.title}")
                # Зберігаємо ID для переходу
                item.setData(Qt.UserRole, g.id)
                self.day_list.addItem(item)
        else:
            empty_item = QListWidgetItem("Немає дедлайнів 🎉")
            empty_item.setFlags(Qt.NoItemFlags)
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setForeground(QBrush(QColor("#64748b")))
            self.day_list.addItem(empty_item)

    def on_item_double_click(self, item):
        """Перехід до цілі при подвійному кліку"""
        goal_id = item.data(Qt.UserRole)
        if goal_id:
            # 1. Перемикаємось на вкладку цілей (індекс 0)
            self.mw.switch_tab(0)

            # 2. Налаштовуємо вкладку цілей на показ цієї цілі
            # (Переконайтеся, що в QuestTab ці атрибути існують)
            self.mw.tab_quests.pinned_goal_id = goal_id
            self.mw.tab_quests.should_highlight = True
            self.mw.tab_quests.update_list()

            # 3. Скролимо вгору (безпечно)
            if hasattr(self.mw.tab_quests, 'scroll_area'):
                self.mw.tab_quests.scroll_area.verticalScrollBar().setValue(0)