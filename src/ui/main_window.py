from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QListWidget, QListWidgetItem,
                             QFrame, QInputDialog, QGraphicsDropShadowEffect, QStackedWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from datetime import date
from ..models import LearningGoal, GoalStatus, Habit


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user_id, storage_service):
        super().__init__()
        self.user_id = user_id
        self.storage = storage_service

        self.user = self.storage.get_user_by_id(self.user_id)
        if not self.user:
            self.close()
            return

        self.setWindowTitle(f"LGM - {self.user.username}")
        self.resize(1100, 700)

        self.init_ui()
        self.load_goals()
        self.load_habits()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # --- СИНЯ ТЕМА (BLUE THEME CSS) ---
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0b0f19; /* Головний фон */
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }

            /* --- SIDEBAR --- */
            QFrame#Sidebar {
                background-color: #111827; /* Темно-синій фон панелі */
                border-right: 2px solid #1e3a8a; /* Обводка */
            }

            /* Тексти в панелі */
            QLabel#AppTitle {
                color: #3b82f6; /* Яскраво-синій */
                font-weight: bold;
                font-size: 24px;
                background-color: transparent;
            }
            QLabel#UserLabel {
                color: #94a3b8;
                background-color: transparent;
            }

            /* Кнопки меню (прозорі, щоб не різати фон) */
            QPushButton.menuBtn {
                text-align: left;
                padding: 15px 30px;
                border: none;
                color: #cbd5e1;
                font-size: 16px;
                background-color: transparent; /* ВАЖЛИВО: Прозорий фон */
            }
            QPushButton.menuBtn:hover {
                background-color: #1e293b; /* Трохи світліше при наведенні */
                color: #ffffff;
                border-left: 4px solid #3b82f6;
            }
            QPushButton.menuBtn:checked {
                background-color: #1e3a8a;
                color: white;
                border-left: 4px solid #60a5fa;
            }

            /* Кнопка Виходу */
            QPushButton#ExitBtn {
                background-color: transparent;
                border: 1px solid #dc2626;
                color: #fca5a5;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton#ExitBtn:hover {
                background-color: #7f1d1d;
                color: white;
            }

            /* --- CONTENT AREA --- */
            QListWidget {
                background-color: #1e293b;
                border: 2px solid #1e3a8a;
                border-radius: 8px;
                padding: 10px;
                font-size: 15px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #334155;
                color: #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #1d4ed8;
                border-left: 4px solid #60a5fa;
                color: white;
            }

            /* Кнопки дій */
            QPushButton.actionBtn {
                background-color: #1d4ed8; 
                color: white; 
                border: 2px solid #3b82f6; 
                border-radius: 8px; 
                padding: 12px 24px; 
                font-weight: bold; font-size: 14px;
            }
            QPushButton.actionBtn:hover {
                background-color: #2563eb;
                border-color: #60a5fa;
            }
        """)

        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. SIDEBAR (ЛІВА ПАНЕЛЬ) ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 30, 0, 20)

        # Заголовок (Без контейнерів, пряме додавання)
        app_label = QLabel("LGM")
        app_label.setObjectName("AppTitle")
        app_label.setAlignment(Qt.AlignCenter)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor("#3b82f6"))
        app_label.setGraphicsEffect(shadow)

        user_label = QLabel(f"{self.user.username}")
        user_label.setObjectName("UserLabel")
        user_label.setAlignment(Qt.AlignCenter)

        sidebar_layout.addWidget(app_label)
        sidebar_layout.addWidget(user_label)
        sidebar_layout.addSpacing(40)

        # Меню навігації
        self.btn_goals = self.create_menu_btn("🎯  Цілі")
        self.btn_habits = self.create_menu_btn("⚡  Звички")

        sidebar_layout.addWidget(self.btn_goals)
        sidebar_layout.addWidget(self.btn_habits)
        sidebar_layout.addStretch()

        # Кнопка Виходу (Виправлено розрізання)
        btn_exit = QPushButton("Вихід з акаунту")
        btn_exit.setObjectName("ExitBtn")
        btn_exit.clicked.connect(self.on_logout_click)

        exit_container = QWidget()
        exit_container.setStyleSheet("background-color: transparent;")  # Прозорий контейнер
        exit_layout = QVBoxLayout(exit_container)
        exit_layout.setContentsMargins(20, 0, 20, 0)
        exit_layout.addWidget(btn_exit)

        sidebar_layout.addWidget(exit_container)

        # --- 2. MAIN CONTENT (ПРАВА ПАНЕЛЬ) ---
        content_area = QFrame()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(50, 50, 50, 50)

        # Stacked Widget для перемикання вкладок
        self.stack = QStackedWidget()

        # --> PAGE 1: GOALS
        self.page_goals = QWidget()
        goals_layout = QVBoxLayout(self.page_goals)
        goals_layout.setContentsMargins(0, 0, 0, 0)

        lbl_goals = QLabel("Мої Навчальні Цілі")
        lbl_goals.setStyleSheet("font-size: 28px; font-weight: bold; color: white; margin-bottom: 10px;")

        self.goals_list = QListWidget()

        btn_add_goal = QPushButton("+ Нова Ціль")
        btn_add_goal.setProperty("class", "actionBtn")
        btn_add_goal.clicked.connect(self.add_goal_dialog)

        goals_layout.addWidget(lbl_goals)
        goals_layout.addWidget(self.goals_list)
        goals_layout.addWidget(btn_add_goal, alignment=Qt.AlignLeft)

        # --> PAGE 2: HABITS
        self.page_habits = QWidget()
        habits_layout = QVBoxLayout(self.page_habits)
        habits_layout.setContentsMargins(0, 0, 0, 0)

        lbl_habits = QLabel("Трекер Звичок")
        lbl_habits.setStyleSheet("font-size: 28px; font-weight: bold; color: white; margin-bottom: 10px;")

        self.habits_list = QListWidget()
        self.habits_list.itemDoubleClicked.connect(self.check_habit)  # Подвійний клік для виконання

        btn_add_habit = QPushButton("+ Нова Звичка")
        btn_add_habit.setProperty("class", "actionBtn")
        btn_add_habit.clicked.connect(self.add_habit_dialog)

        habits_info = QLabel("💡 Подвійний клік по звичці, щоб відмітити виконання")
        habits_info.setStyleSheet("color: #64748b; font-size: 12px; margin-top: 5px;")

        habits_layout.addWidget(lbl_habits)
        habits_layout.addWidget(self.habits_list)
        habits_layout.addWidget(habits_info)
        habits_layout.addWidget(btn_add_habit, alignment=Qt.AlignLeft)

        # Додавання сторінок у стек
        self.stack.addWidget(self.page_goals)
        self.stack.addWidget(self.page_habits)

        content_layout.addWidget(self.stack)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)

        # Підключення кнопок меню
        self.btn_goals.clicked.connect(lambda: self.switch_tab(0))
        self.btn_habits.clicked.connect(lambda: self.switch_tab(1))

        # За замовчуванням активна перша вкладка
        self.switch_tab(0)

    def create_menu_btn(self, text):
        btn = QPushButton(text)
        btn.setProperty("class", "menuBtn")
        btn.setCheckable(True)
        return btn

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        # Оновлення стану кнопок
        self.btn_goals.setChecked(index == 0)
        self.btn_habits.setChecked(index == 1)

    def on_logout_click(self):
        self.logout_requested.emit()

    # --- LOGIC: GOALS ---
    def load_goals(self):
        self.goals_list.clear()
        goals = self.storage.get_goals(self.user_id)
        if not goals:
            self.goals_list.addItem("Список цілей порожній.")
        for goal in goals:
            status_icon = "🔵" if goal.status == GoalStatus.PLANNED else "✅"
            item = QListWidgetItem(f"{status_icon}  {goal.title}   —   {goal.priority.value}")
            item.setData(Qt.UserRole, goal)
            self.goals_list.addItem(item)

    def add_goal_dialog(self):
        text, ok = QInputDialog.getText(self, "Нова Ціль", "Назва цілі:")
        if ok and text:
            new_goal = LearningGoal(title=text, user_id=self.user_id)
            self.storage.save_goal(new_goal)
            self.load_goals()

    # --- LOGIC: HABITS ---
    def load_habits(self):
        self.habits_list.clear()
        habits = self.storage.get_habits(self.user_id)

        today_str = date.today().isoformat()

        if not habits:
            self.habits_list.addItem("Немає звичок. Створіть нову!")

        for habit in habits:
            is_done_today = (habit.last_completed_date == today_str)
            icon = "🔥" if is_done_today else "⬜"
            status = "Виконано сьогодні" if is_done_today else "Не виконано"

            text = f"{icon}  {habit.title}  (Серія: {habit.streak} дн.)"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, habit)

            # Якщо виконано, фарбуємо в зеленуватий колір
            if is_done_today:
                item.setForeground(QColor("#4ade80"))

            self.habits_list.addItem(item)

    def add_habit_dialog(self):
        text, ok = QInputDialog.getText(self, "Нова Звичка", "Назва звички:")
        if ok and text:
            new_habit = Habit(title=text, user_id=self.user_id)
            self.storage.save_habit(new_habit)
            self.load_habits()

    def check_habit(self, item):
        habit = item.data(Qt.UserRole)
        if not habit: return

        today_str = date.today().isoformat()

        if habit.last_completed_date == today_str:
            return  # Вже виконано сьогодні

        # Логіка виконання
        habit.streak += 1
        habit.last_completed_date = today_str
        self.storage.save_habit(habit)
        self.load_habits()  # Оновити список