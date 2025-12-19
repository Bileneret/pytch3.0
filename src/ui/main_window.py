from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QListWidget, QListWidgetItem,
                             QProgressBar, QFrame, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt
from ..models import LearningGoal, GoalStatus


class MainWindow(QMainWindow):
    def __init__(self, user_id, storage_service):
        super().__init__()
        self.user_id = user_id
        self.storage = storage_service

        # 1. ЗАВАНТАЖЕННЯ КОРИСТУВАЧА (Виправляємо помилку)
        self.user = self.storage.get_user_by_id(self.user_id)

        if not self.user:
            # Критична помилка, якщо користувача не знайдено (наприклад, БД видалили під час роботи)
            print(f"CRITICAL ERROR: User with ID {user_id} not found!")
            self.close()
            return

        self.setWindowTitle(f"Pytch: {self.user.username}'s Workspace")
        self.resize(1100, 700)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- ЛІВА ПАНЕЛЬ ---
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #2b2b2b; border-right: 1px solid #3d3d3d;")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)

        app_label = QLabel("PYTCH")
        app_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 20px;")
        app_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(app_label)

        user_label = QLabel(f"👤 {self.user.username}")
        user_label.setStyleSheet("color: #aaaaaa; font-size: 14px; margin-bottom: 20px;")
        user_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(user_label)

        self.btn_dashboard = QPushButton("📊 Огляд")
        self.btn_dashboard.setStyleSheet("text-align: left; padding: 12px; border: none; color: #cccccc;")
        sidebar_layout.addWidget(self.btn_dashboard)

        sidebar_layout.addStretch()

        btn_exit = QPushButton("Вихід")
        btn_exit.setStyleSheet("background-color: #d32f2f; color: white; padding: 10px; border-radius: 5px;")
        btn_exit.clicked.connect(self.close)
        sidebar_layout.addWidget(btn_exit)

        # --- ПРАВА ПАНЕЛЬ ---
        content_area = QFrame()
        content_area.setStyleSheet("background-color: #1e1e1e;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 40, 40, 40)

        # Заголовок
        self.lbl_page_title = QLabel("Мої Навчальні Цілі")
        self.lbl_page_title.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        content_layout.addWidget(self.lbl_page_title)

        # Список
        self.goals_list = QListWidget()
        self.goals_list.setStyleSheet(
            "background-color: #252526; color: white; font-size: 14px; padding: 10px; border-radius: 5px;")
        content_layout.addWidget(self.goals_list)

        # Кнопки
        btn_add = QPushButton("+ Додати Ціль")
        btn_add.setStyleSheet("background-color: #007ACC; color: white; padding: 10px; border-radius: 5px;")
        btn_add.clicked.connect(self.add_goal_dialog)
        content_layout.addWidget(btn_add)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)

    def load_data(self):
        self.goals_list.clear()
        goals = self.storage.get_goals(self.user_id)

        if not goals:
            self.goals_list.addItem("Список порожній. Поставте собі мету!")
            return

        for goal in goals:
            status_icon = "🟢" if goal.status == GoalStatus.PLANNED else "🏁"
            item = QListWidgetItem(f"{status_icon} {goal.title}  [{goal.priority.value}]")
            item.setData(Qt.UserRole, goal)
            self.goals_list.addItem(item)

    def add_goal_dialog(self):
        text, ok = QInputDialog.getText(self, "Нова Ціль", "Назва цілі:")
        if ok and text:
            new_goal = LearningGoal(title=text, user_id=self.user_id)
            self.storage.save_goal(new_goal)
            self.load_data()