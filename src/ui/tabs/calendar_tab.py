from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget, QListWidget, QLabel, QListWidgetItem
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
        self.header = QLabel("Календар Дедлайнів")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding: 10px;")
        self.layout.insertWidget(0, self.header)

        # Calendar Layout
        content = QWidget()
        hbox = QHBoxLayout(content)

        # Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget { alternate-background-color: #1e293b; color: white; }
            QCalendarWidget QToolButton { color: white; icon-size: 24px; }
            QCalendarWidget QMenu { color: white; }
            QCalendarWidget QSpinBox { color: white; }
        """)
        self.calendar.clicked.connect(self.on_date_click)
        hbox.addWidget(self.calendar)

        # List for selected day
        self.day_list = QListWidget()
        self.day_list.setStyleSheet(
            "background-color: #111827; border: 1px solid #1e3a8a; border-radius: 4px; color: white;")
        hbox.addWidget(self.day_list)

        self.list_layout.addWidget(content)

    def highlight_dates(self):
        goals = self.mw.storage.get_goals(self.mw.user_id)
        fmt = QTextCharFormat()
        fmt.setBackground(QBrush(QColor("#ef4444")))  # Red for deadline
        fmt.setForeground(QBrush(QColor("white")))

        for g in goals:
            if g.deadline:
                try:
                    dt = datetime.strptime(g.deadline, "%Y-%m-%d")
                    qdate = QDate(dt.year, dt.month, dt.day)
                    self.calendar.setDateTextFormat(qdate, fmt)
                except:
                    pass

    def on_date_click(self, qdate):
        self.day_list.clear()
        selected_str = qdate.toString("yyyy-MM-dd")

        goals = self.mw.storage.get_goals(self.mw.user_id)
        found = False
        for g in goals:
            if g.deadline == selected_str:
                item = QListWidgetItem(f"⏰ {g.title}")
                self.day_list.addItem(item)
                found = True

        if not found:
            self.day_list.addItem("Немає дедлайнів на цей день")