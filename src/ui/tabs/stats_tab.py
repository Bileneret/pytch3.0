from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from .base_tab import BaseTab
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from src.models import GoalStatus, GoalPriority


class StatsTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.setup_ui()
        self.update_charts()

    def setup_ui(self):
        self.header = QLabel("Статистика Продуктивності")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding: 10px;")
        self.layout.insertWidget(0, self.header)

        # Chart Container
        self.chart_container = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_container)
        self.list_layout.addWidget(self.chart_container)

    def update_charts(self):
        # Clear old charts
        for i in range(self.chart_layout.count()):
            self.chart_layout.itemAt(i).widget().deleteLater()

        goals = self.mw.storage.get_goals(self.mw.user_id)
        if not goals:
            self.chart_layout.addWidget(QLabel("Немає даних для статистики"))
            return

        # 1. Pie Chart: Status
        status_counts = {"Planned": 0, "In Progress": 0, "Completed": 0}
        for g in goals:
            if g.status == GoalStatus.PLANNED:
                status_counts["Planned"] += 1
            elif g.status == GoalStatus.IN_PROGRESS:
                status_counts["In Progress"] += 1
            elif g.status == GoalStatus.COMPLETED:
                status_counts["Completed"] += 1

        fig1, ax1 = plt.subplots(figsize=(5, 4))
        fig1.patch.set_facecolor('#0b0f19')  # Dark background
        ax1.set_facecolor('#0b0f19')

        labels = [k for k, v in status_counts.items() if v > 0]
        sizes = [v for v in status_counts.values() if v > 0]
        colors = ['#60a5fa', '#facc15', '#4ade80']

        if sizes:
            wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            plt.setp(texts, color="white")
            plt.setp(autotexts, color="black", weight="bold")
            ax1.set_title("Розподіл за статусом", color="white")

            canvas1 = FigureCanvas(fig1)
            self.chart_layout.addWidget(canvas1)

        # 2. Bar Chart: Priority
        prio_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for g in goals:
            prio_counts[g.priority.name] += 1

        fig2, ax2 = plt.subplots(figsize=(5, 4))
        fig2.patch.set_facecolor('#0b0f19')
        ax2.set_facecolor('#0b0f19')

        cats = list(prio_counts.keys())
        vals = list(prio_counts.values())

        bars = ax2.bar(cats, vals, color='#8b5cf6')
        ax2.set_title("Цілі за пріоритетом", color="white")
        ax2.tick_params(axis='x', colors='white')
        ax2.tick_params(axis='y', colors='white')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')

        canvas2 = FigureCanvas(fig2)
        self.chart_layout.addWidget(canvas2)