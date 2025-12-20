from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
                             QFrame, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt
from .base_tab import BaseTab
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from datetime import datetime, date
from collections import Counter

# Налаштування кольорів
BG_DARK = '#0b0f19'  # Фон вікна
BG_CARD = '#111827'  # Фон карток/графіків
TEXT_MAIN = '#e0e0e0'  # Основний текст
TEXT_SUB = '#94a3b8'  # Допоміжний текст
BORDER = '#1e3a8a'  # Бордери

# Глобальний стиль matplotlib
plt.style.use('dark_background')
plt.rcParams.update({
    'axes.facecolor': BG_CARD,
    'figure.facecolor': BG_CARD,
    'text.color': TEXT_MAIN,
    'axes.labelcolor': TEXT_SUB,
    'xtick.color': TEXT_SUB,
    'ytick.color': TEXT_SUB,
    'font.size': 10,
    'axes.grid': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.bottom': False,
    'axes.spines.left': False
})


class StatsTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.mw = main_window

        # Налаштування скролу базової вкладки
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.list_layout.setContentsMargins(20, 20, 20, 40)  # Зовнішні відступи сторінки
        self.list_layout.setSpacing(20)

        self.setup_ui()
        self.update_charts()

    def setup_ui(self):
        # Заголовок
        header_lbl = QLabel("Аналітика та Статистика")
        header_lbl.setStyleSheet("font-size: 26px; font-weight: bold; color: white; margin-bottom: 10px;")
        self.list_layout.addWidget(header_lbl)

        # Вкладки (Tabs)
        self.tabs = QTabWidget()
        # ВИПРАВЛЕНО: Збільшено padding та додано min-width для вкладок
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 0; background: transparent; }}
            QTabBar::tab {{ 
                background: {BG_CARD}; 
                color: {TEXT_SUB}; 
                padding: 12px 50px; /* Збільшено горизонтальний відступ */
                margin-right: 10px; 
                min-width: 100px;   /* Мінімальна ширина вкладки */
                border: 1px solid {BORDER};
                border-top-left-radius: 8px; 
                border-top-right-radius: 8px;
                font-weight: bold; font-size: 14px;
            }}
            QTabBar::tab:selected {{ 
                background: #1e3a8a; 
                color: white; 
                border-bottom: 3px solid #60a5fa;
            }}
            QTabBar::tab:hover {{ background: #1e293b; color: white; }}
        """)

        self.goals_page = QWidget()
        self.habits_page = QWidget()

        self.tabs.addTab(self.goals_page, "🎯 Цілі")
        self.tabs.addTab(self.habits_page, "⚡ Звички")

        self.list_layout.addWidget(self.tabs)

        # Лейаути сторінок
        self.goals_layout = QVBoxLayout(self.goals_page)
        self.goals_layout.setSpacing(30)
        self.goals_layout.setContentsMargins(0, 20, 0, 20)

        self.habits_layout = QVBoxLayout(self.habits_page)
        self.habits_layout.setSpacing(30)
        self.habits_layout.setContentsMargins(0, 20, 0, 20)

    def update_charts(self):
        # Очищення старих віджетів
        self._clear_layout(self.goals_layout)
        self._clear_layout(self.habits_layout)

        # Очищення пам'яті matplotlib
        plt.close('all')

        self.render_goals_stats()
        self.render_habits_stats()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    # --- GOALS ---
    def render_goals_stats(self):
        from ...models import GoalStatus
        goals = self.mw.storage.get_goals(self.mw.user_id)

        if not goals:
            self.goals_layout.addWidget(QLabel("Немає даних", alignment=Qt.AlignCenter))
            return

        # 1. KPI Cards
        total = len(goals)
        completed = sum(1 for g in goals if g.status == GoalStatus.COMPLETED)
        in_progress = sum(1 for g in goals if g.status == GoalStatus.IN_PROGRESS)
        rate = int((completed / total) * 100) if total > 0 else 0

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(20)
        kpi_row.addWidget(self.create_kpi("Всього цілей", str(total), "#60a5fa"))
        kpi_row.addWidget(self.create_kpi("Успішність", f"{rate}%", "#4ade80"))
        kpi_row.addWidget(self.create_kpi("В процесі", str(in_progress), "#facc15"))
        self.goals_layout.addLayout(kpi_row)

        # 2. Charts Grid
        grid = QGridLayout()
        grid.setSpacing(20)

        # Status Pie
        counts = [completed, in_progress, total - completed - in_progress]
        labels = ["Виконано", "В процесі", "Заплановано"]
        colors = ["#4ade80", "#facc15", "#94a3b8"]
        grid.addWidget(self.create_chart_box("Статус виконання", self.plot_pie(counts, labels, colors)), 0, 0)

        # Priority Bar
        p_counts = Counter(g.priority.value for g in goals)
        p_labels = ["Низький", "Середній", "Високий", "Критичний"]
        p_vals = [p_counts.get(l, 0) for l in p_labels]
        grid.addWidget(self.create_chart_box("Пріоритети", self.plot_bar(p_labels, p_vals, "#8b5cf6")), 0, 1)

        # Categories Donut
        cats = self.mw.storage.get_categories(self.mw.user_id)
        cat_map = {c.id: (c.name, c.color) for c in cats}
        c_counts = Counter()
        for g in goals:
            name = cat_map[g.category_id][0] if g.category_id and g.category_id in cat_map else "Без категорії"
            c_counts[name] += 1

        c_labels = list(c_counts.keys())
        c_vals = list(c_counts.values())
        c_colors = []
        for name in c_labels:
            col = "#94a3b8"
            for c in cats:
                if c.name == name: col = c.color; break
            c_colors.append(col)

        grid.addWidget(self.create_chart_box("Категорії", self.plot_donut(c_vals, c_labels, c_colors)), 1, 0)

        # Timeline Line
        dates = []
        for g in goals:
            if g.deadline:
                try:
                    dates.append(datetime.strptime(g.deadline, "%Y-%m-%d").strftime("%Y-%m"))
                except:
                    pass
        d_counts = Counter(dates)
        d_labels = sorted(d_counts.keys())[-6:]
        d_vals = [d_counts[d] for d in d_labels]
        grid.addWidget(self.create_chart_box("Дедлайни (6 міс)", self.plot_line(d_labels, d_vals, "#f472b6")), 1, 1)

        self.goals_layout.addLayout(grid)

    # --- HABITS ---
    def render_habits_stats(self):
        habits = self.mw.storage.get_habits(self.mw.user_id)

        if not habits:
            self.habits_layout.addWidget(QLabel("Немає даних", alignment=Qt.AlignCenter))
            return

        # 1. KPI
        total = len(habits)
        best = max((h.streak for h in habits), default=0)
        today = date.today().isoformat()
        done = sum(1 for h in habits if h.last_completed_date == today)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(20)
        kpi_row.addWidget(self.create_kpi("Активних звичок", str(total), "#a78bfa"))
        kpi_row.addWidget(self.create_kpi("Рекорд серії", f"{best} дн.", "#f472b6"))
        kpi_row.addWidget(self.create_kpi("Зроблено сьогодні", f"{done}/{total}", "#4ade80"))
        self.habits_layout.addLayout(kpi_row)

        # 2. Charts
        grid = QGridLayout()
        grid.setSpacing(20)

        # Top Streaks
        top = sorted(habits, key=lambda h: h.streak, reverse=True)[:5]
        names = [h.title for h in top]
        vals = [h.streak for h in top]
        grid.addWidget(self.create_chart_box("Топ серій", self.plot_hbar(names, vals, "#2dd4bf")), 0, 0)

        # Today Pie
        grid.addWidget(self.create_chart_box("Прогрес дня",
                                             self.plot_pie([done, total - done], ["Виконано", "Залишилось"],
                                                           ["#4ade80", "#ef4444"])), 0, 1)

        self.habits_layout.addLayout(grid)

    # --- COMPONENTS ---
    def create_kpi(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-left: 6px solid {color};
                border-radius: 12px;
            }}
        """)
        l = QVBoxLayout(card)
        l.setContentsMargins(25, 20, 25, 20)

        t = QLabel(title)
        t.setStyleSheet(f"color: {TEXT_SUB}; font-size: 14px; font-weight: bold; border: none;")
        v = QLabel(value)
        v.setStyleSheet("color: white; font-size: 28px; font-weight: 900; border: none;")

        l.addWidget(t)
        l.addWidget(v)
        return card

    def create_chart_box(self, title_text, fig):
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        l = QVBoxLayout(box)
        l.setContentsMargins(15, 15, 15, 15)

        t = QLabel(title_text)
        t.setStyleSheet("color: white; font-size: 16px; font-weight: bold; border: none; margin-bottom: 5px;")
        l.addWidget(t)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background: transparent; border: none;")
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.setMinimumHeight(300)
        l.addWidget(canvas)

        return box

    # --- PLOTTING ---
    def plot_pie(self, values, labels, colors):
        fig, ax = plt.subplots()
        data = [(v, l, c) for v, l, c in zip(values, labels, colors) if v > 0]
        if data:
            v, l, c = zip(*data)
            wedges, texts, autotexts = ax.pie(v, labels=l, colors=c, autopct='%1.0f%%', startangle=90,
                                              textprops={'color': TEXT_MAIN, 'fontsize': 9})
            plt.setp(autotexts, weight="bold", color="black")
        else:
            ax.text(0.5, 0.5, "Немає даних", ha='center', color=TEXT_SUB)

        fig.tight_layout(pad=3.0)  # ВАЖЛИВО: Відступи, щоб текст не обрізався
        return fig

    def plot_donut(self, values, labels, colors):
        fig, ax = plt.subplots()
        data = [(v, l, c) for v, l, c in zip(values, labels, colors) if v > 0]
        if data:
            v, l, c = zip(*data)
            ax.pie(v, labels=l, colors=c, autopct='%1.0f%%', startangle=90, pctdistance=0.85,
                   textprops={'color': TEXT_MAIN, 'fontsize': 9})
            ax.add_artist(plt.Circle((0, 0), 0.65, fc=BG_CARD))
        else:
            ax.text(0.5, 0.5, "Немає даних", ha='center', color=TEXT_SUB)

        fig.tight_layout(pad=3.0)
        return fig

    def plot_bar(self, cats, vals, color):
        fig, ax = plt.subplots()
        bars = ax.bar(cats, vals, color=color, alpha=0.9)
        ax.bar_label(bars, color=TEXT_MAIN, padding=3)
        fig.tight_layout(pad=3.0)
        return fig

    def plot_hbar(self, cats, vals, color):
        fig, ax = plt.subplots()
        bars = ax.barh(cats, vals, color=color, alpha=0.9)
        ax.bar_label(bars, color=TEXT_MAIN, padding=3)
        ax.invert_yaxis()
        fig.tight_layout(pad=3.0)
        return fig

    def plot_line(self, cats, vals, color):
        fig, ax = plt.subplots()
        ax.plot(cats, vals, marker='o', color=color, linewidth=2)
        ax.fill_between(cats, vals, color=color, alpha=0.2)
        for x, y in zip(cats, vals):
            ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 8), ha='center', color=TEXT_MAIN)
        fig.tight_layout(pad=3.0)
        return fig