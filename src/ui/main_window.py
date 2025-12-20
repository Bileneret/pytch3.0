from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame, \
    QGridLayout
from PyQt5.QtCore import Qt, pyqtSignal
from src.ui.tabs.quest_tab import QuestTab
from src.ui.tabs.habit_tab import HabitTab
from src.ui.tabs.stats_tab import StatsTab
from src.ui.tabs.calendar_tab import CalendarTab
from src.ui.tabs.education_tab import EducationTab


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user_id, storage):
        super().__init__()
        self.user_id = user_id
        self.storage = storage
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Goal Manager Pro")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI';")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # Збільшено зовнішні відступи головного вікна
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # --- SIDEBAR ---
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #111827; border-right: 1px solid #1e3a8a; border-radius: 8px;")
        sidebar.setFixedWidth(220)  # Трохи ширший сайдбар
        side_layout = QVBoxLayout(sidebar)
        # Збільшено внутрішні відступи сайдбару
        side_layout.setContentsMargins(15, 25, 15, 25)
        side_layout.setSpacing(15)

        # === ЛОГОТИП LGM ===
        logo_container = QWidget()
        logo_container.setFixedHeight(60)
        logo_grid = QGridLayout(logo_container)
        logo_grid.setContentsMargins(0, 0, 0, 0)

        lbl_shadow = QLabel("LGM")
        lbl_shadow.setAlignment(Qt.AlignCenter)
        lbl_shadow.setStyleSheet(
            "font-size: 48px; font-weight: 900; color: #60a5fa; font-family: 'Arial Black'; padding-top: 4px; padding-left: 4px;")

        lbl_main = QLabel("LGM")
        lbl_main.setAlignment(Qt.AlignCenter)
        lbl_main.setStyleSheet("font-size: 48px; font-weight: 900; color: #2563eb; font-family: 'Arial Black';")

        logo_grid.addWidget(lbl_shadow, 0, 0)
        logo_grid.addWidget(lbl_main, 0, 0)
        side_layout.addWidget(logo_container)
        # ===================

        # Navigation Buttons
        # Збільшено padding у кнопок
        btn_style = """
            QPushButton { 
                text-align: left; 
                padding: 14px 18px; 
                background: transparent; 
                border-radius: 8px; 
                color: #94a3b8; 
                font-size: 14px; 
                font-weight: 500; 
            }
            QPushButton:hover { background-color: #1e293b; color: white; }
            QPushButton:checked { background-color: #2563eb; color: white; }
        """

        self.btn_quests = QPushButton("🎯 Цілі")
        self.btn_quests.setCheckable(True)
        self.btn_quests.setStyleSheet(btn_style)
        self.btn_quests.clicked.connect(lambda: self.switch_tab(0))

        self.btn_education = QPushButton("🎓 Навчання")
        self.btn_education.setCheckable(True)
        self.btn_education.setStyleSheet(btn_style)
        self.btn_education.clicked.connect(lambda: self.switch_tab(1))

        self.btn_habits = QPushButton("⚡ Звички")
        self.btn_habits.setCheckable(True)
        self.btn_habits.setStyleSheet(btn_style)
        self.btn_habits.clicked.connect(lambda: self.switch_tab(2))

        self.btn_stats = QPushButton("📊 Статистика")
        self.btn_stats.setCheckable(True)
        self.btn_stats.setStyleSheet(btn_style)
        self.btn_stats.clicked.connect(lambda: self.switch_tab(3))

        self.btn_calendar = QPushButton("📅 Календар")
        self.btn_calendar.setCheckable(True)
        self.btn_calendar.setStyleSheet(btn_style)
        self.btn_calendar.clicked.connect(lambda: self.switch_tab(4))

        side_layout.addWidget(self.btn_quests)
        side_layout.addWidget(self.btn_education)
        side_layout.addWidget(self.btn_habits)
        side_layout.addWidget(self.btn_stats)
        side_layout.addWidget(self.btn_calendar)

        side_layout.addStretch()

        btn_logout = QPushButton("Вийти")
        btn_logout.setStyleSheet(
            "background-color: #7f1d1d; color: white; border-radius: 6px; padding: 12px; font-weight: bold;")
        btn_logout.clicked.connect(self.logout_requested.emit)
        side_layout.addWidget(btn_logout)

        main_layout.addWidget(sidebar)

        # --- CONTENT ---
        self.stack = QStackedWidget()
        # Додаємо трохи відступу для контенту справа
        self.stack.setContentsMargins(5, 5, 5, 5)

        self.tab_quests = QuestTab(self.stack, self)
        self.tab_education = EducationTab(self.stack, self)
        self.tab_habits = HabitTab(self.stack, self)
        self.tab_stats = StatsTab(self.stack, self)
        self.tab_calendar = CalendarTab(self.stack, self)

        self.stack.addWidget(self.tab_quests)
        self.stack.addWidget(self.tab_education)
        self.stack.addWidget(self.tab_habits)
        self.stack.addWidget(self.tab_stats)
        self.stack.addWidget(self.tab_calendar)

        main_layout.addWidget(self.stack)

        self.btn_quests.setChecked(True)
        self.stack.setCurrentIndex(0)

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.btn_quests.setChecked(index == 0)
        self.btn_education.setChecked(index == 1)
        self.btn_habits.setChecked(index == 2)
        self.btn_stats.setChecked(index == 3)
        self.btn_calendar.setChecked(index == 4)

        if index == 3: self.tab_stats.update_charts()
        if index == 4: self.tab_calendar.highlight_dates()