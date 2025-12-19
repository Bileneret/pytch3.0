from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect,
                             QStackedWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

# Імпортуємо наші нові модульні вкладки
from .tabs.quest_tab import QuestTab
from .tabs.habit_tab import HabitTab


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
        self.resize(1100, 800)
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # --- BLUE NEON THEME ---
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }

            /* SIDEBAR */
            QFrame#Sidebar { background-color: #111827; border-right: 2px solid #1e3a8a; }
            QLabel#AppTitle { color: #3b82f6; font-weight: bold; font-size: 24px; background-color: transparent; }
            QLabel#UserLabel { color: #94a3b8; background-color: transparent; }

            QPushButton.menuBtn { 
                text-align: left; padding: 15px 30px; border: none; 
                color: #cbd5e1; font-size: 16px; background-color: transparent; 
            }
            QPushButton.menuBtn:hover { 
                background-color: #1e293b; color: #ffffff; border-left: 4px solid #3b82f6; 
            }
            QPushButton.menuBtn:checked { 
                background-color: #1e3a8a; color: white; border-left: 4px solid #60a5fa; 
            }

            QPushButton#ExitBtn { 
                background-color: transparent; border: 1px solid #dc2626; 
                color: #fca5a5; padding: 10px; border-radius: 6px; 
            }
            QPushButton#ExitBtn:hover { background-color: #7f1d1d; color: white; }

            /* BUTTON STYLES FOR TABS */
            QPushButton.actionBtn { 
                background-color: #1d4ed8; color: white; border: 2px solid #3b82f6; 
                border-radius: 8px; padding: 8px 16px; font-weight: bold; font-size: 14px; 
            }
            QPushButton.actionBtn:hover { background-color: #2563eb; border-color: #60a5fa; }

            QPushButton.aiBtn { 
                background-color: #7c3aed; color: white; border: 2px solid #8b5cf6; 
                border-radius: 8px; padding: 8px 16px; font-weight: bold; font-size: 14px; 
            }
            QPushButton.aiBtn:hover { background-color: #8b5cf6; border-color: #a78bfa; }
        """)

        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- SIDEBAR ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 30, 0, 20)

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

        self.btn_goals = self.create_menu_btn("🎯  Цілі")
        self.btn_habits = self.create_menu_btn("⚡  Звички")

        sidebar_layout.addWidget(self.btn_goals)
        sidebar_layout.addWidget(self.btn_habits)
        sidebar_layout.addStretch()

        btn_exit = QPushButton("Вихід з акаунту")
        btn_exit.setObjectName("ExitBtn")
        btn_exit.clicked.connect(self.on_logout_click)

        exit_container = QWidget()
        exit_container.setStyleSheet("background-color: transparent;")
        exit_layout = QVBoxLayout(exit_container)
        exit_layout.setContentsMargins(20, 0, 20, 0)
        exit_layout.addWidget(btn_exit)
        sidebar_layout.addWidget(exit_container)

        # --- CONTENT AREA (STACKED WIDGET) ---
        content_area = QFrame()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)  # Трохи відступів для контенту

        self.stack = QStackedWidget()

        # Ініціалізація вкладок
        self.tab_quests = QuestTab(self.stack, self)
        self.tab_habits = HabitTab(self.stack, self)

        self.stack.addWidget(self.tab_quests)
        self.stack.addWidget(self.tab_habits)

        content_layout.addWidget(self.stack)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)

        # Підключення кнопок
        self.btn_goals.clicked.connect(lambda: self.switch_tab(0))
        self.btn_habits.clicked.connect(lambda: self.switch_tab(1))
        self.switch_tab(0)

    def create_menu_btn(self, text):
        btn = QPushButton(text)
        btn.setProperty("class", "menuBtn")
        btn.setCheckable(True)
        return btn

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.btn_goals.setChecked(index == 0)
        self.btn_habits.setChecked(index == 1)

    def on_logout_click(self):
        self.logout_requested.emit()

    def update_stats(self, change):
        """Оновлює статистику користувача в БД."""
        self.user.total_completed_goals += change
        if self.user.total_completed_goals < 0:
            self.user.total_completed_goals = 0
        self.storage.update_user_stats(self.user_id, self.user.total_completed_goals)