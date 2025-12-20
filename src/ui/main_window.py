from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame, \
    QGridLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
import json
from src.ui.tabs.quest_tab import QuestTab
from src.ui.tabs.habit_tab import HabitTab
from src.ui.tabs.stats_tab import StatsTab
from src.ui.tabs.calendar_tab import CalendarTab
from src.ui.tabs.education_tab import DevelopmentTab


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
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # --- SIDEBAR ---
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #111827; border-right: 1px solid #1e3a8a; border-radius: 8px;")
        sidebar.setFixedWidth(220)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(15, 25, 15, 25)
        side_layout.setSpacing(15)

        # === LOGO ===
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

        # Navigation Buttons
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

        self.btn_development = QPushButton("🚀 Розвиток")
        self.btn_development.setCheckable(True)
        self.btn_development.setStyleSheet(btn_style)
        self.btn_development.clicked.connect(lambda: self.switch_tab(1))

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
        side_layout.addWidget(self.btn_development)
        side_layout.addWidget(self.btn_habits)
        side_layout.addWidget(self.btn_stats)
        side_layout.addWidget(self.btn_calendar)

        side_layout.addStretch()

        # --- IMPORT / EXPORT BUTTONS ---
        data_btns_layout = QHBoxLayout()
        data_btns_layout.setSpacing(5)

        gray_btn_style = """
            QPushButton { 
                background-color: #374151; 
                color: #e5e7eb; 
                border-radius: 6px; 
                padding: 8px; 
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4b5563; }
        """

        self.btn_import = QPushButton("Імпорт")
        self.btn_import.setStyleSheet(gray_btn_style)
        self.btn_import.clicked.connect(self.import_data)

        self.btn_export = QPushButton("Експорт")
        self.btn_export.setStyleSheet(gray_btn_style)
        self.btn_export.clicked.connect(self.export_data)

        data_btns_layout.addWidget(self.btn_import)
        data_btns_layout.addWidget(self.btn_export)

        side_layout.addLayout(data_btns_layout)

        # --- LOGOUT BUTTON ---
        btn_logout = QPushButton("Вийти")
        btn_logout.setStyleSheet(
            "background-color: #7f1d1d; color: white; border-radius: 6px; padding: 12px; font-weight: bold;")
        # Підключаємо до методу підтвердження, а не напряму
        btn_logout.clicked.connect(self.confirm_logout)
        side_layout.addWidget(btn_logout)

        main_layout.addWidget(sidebar)

        # --- CONTENT ---
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(5, 5, 5, 5)

        self.tab_quests = QuestTab(self.stack, self)
        self.tab_development = DevelopmentTab(self.stack, self)
        self.tab_habits = HabitTab(self.stack, self)
        self.tab_stats = StatsTab(self.stack, self)
        self.tab_calendar = CalendarTab(self.stack, self)

        self.stack.addWidget(self.tab_quests)
        self.stack.addWidget(self.tab_development)
        self.stack.addWidget(self.tab_habits)
        self.stack.addWidget(self.tab_stats)
        self.stack.addWidget(self.tab_calendar)

        main_layout.addWidget(self.stack)

        self.btn_quests.setChecked(True)
        self.stack.setCurrentIndex(0)

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.btn_quests.setChecked(index == 0)
        self.btn_development.setChecked(index == 1)
        self.btn_habits.setChecked(index == 2)
        self.btn_stats.setChecked(index == 3)
        self.btn_calendar.setChecked(index == 4)

        if index == 0: self.tab_quests.update_list()
        if index == 1: self.tab_development.update_list()
        if index == 2: self.tab_habits.load_data()
        if index == 3: self.tab_stats.update_charts()
        if index == 4: self.tab_calendar.highlight_dates()

    def confirm_logout(self):
        """Діалог підтвердження виходу."""
        reply = QMessageBox.question(
            self,
            "Підтвердження виходу",
            "Ви дійсно хочете вийти з акаунту?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()

    def export_data(self):
        """Експорт даних у JSON."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Експорт даних", "lgm_backup.json", "JSON Files (*.json);;All Files (*)", options=options
        )
        if file_path:
            try:
                data = self.storage.export_user_data(self.user_id)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Успіх", "Дані успішно експортовано!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося експортувати дані:\n{e}")

    def import_data(self):
        """Імпорт даних з JSON."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Імпорт даних", "", "JSON Files (*.json);;All Files (*)", options=options
        )
        if file_path:
            reply = QMessageBox.question(
                self, "Імпорт даних",
                "Імпорт об'єднає нові дані з поточними.\nПродовжити?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.storage.import_user_data(data, self.user_id)
                QMessageBox.information(self, "Успіх", "Дані успішно імпортовано!")

                # Оновлюємо всі вкладки
                self.switch_tab(self.stack.currentIndex())

            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося імпортувати дані:\n{e}")