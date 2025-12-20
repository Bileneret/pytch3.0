from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QProgressBar, QFrame, QSizePolicy, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QCursor, QColor
from .base_tab import BaseTab
from ..edit_course_dialog import EditCourseDialog
from ...models import CourseStatus, CourseType, DevelopmentTopic


class CourseCard(QFrame):
    def __init__(self, course, parent_tab):
        super().__init__()
        self.course = course
        self.parent_tab = parent_tab
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 10px;
            }
            QLabel { border: none; color: #e0e0e0; background: transparent; }
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header = QHBoxLayout()

        icon_map = {
            CourseType.BOOK: "📖",
            CourseType.COURSE: "🎓",
            CourseType.VIDEO: "📺",
            CourseType.ARTICLE: "📄",
            CourseType.PROJECT: "🚀",
            CourseType.CHALLENGE: "🏆"
        }
        icon = icon_map.get(self.course.course_type, "🎓")

        title_lbl = QLabel(f"{icon} {self.course.title}")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        title_lbl.setWordWrap(True)
        header.addWidget(title_lbl, 1)

        # Link Button
        if self.course.link:
            btn_link = QPushButton("🔗")
            btn_link.setFixedSize(30, 30)
            btn_link.setCursor(QCursor(Qt.PointingHandCursor))
            btn_link.setStyleSheet(
                "background-color: #0f172a; border-radius: 15px; color: #3b82f6; border: 1px solid #1e40af;")
            btn_link.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.course.link)))
            header.addWidget(btn_link)

        # Edit Button
        btn_edit = QPushButton("⚙️")
        btn_edit.setFixedSize(30, 30)
        btn_edit.setStyleSheet("background-color: transparent; color: #94a3b8; border: none; font-size: 18px;")
        btn_edit.clicked.connect(self.edit_course)
        header.addWidget(btn_edit)

        # Delete Button
        btn_del = QPushButton("✖")
        btn_del.setFixedSize(30, 30)
        btn_del.setStyleSheet("background-color: transparent; color: #ef4444; border: none; font-weight: bold;")
        btn_del.clicked.connect(self.delete_course)
        header.addWidget(btn_del)

        main_layout.addLayout(header)

        # Progress
        prog_layout = QHBoxLayout()

        btn_minus = QPushButton("-")
        btn_minus.setFixedSize(30, 30)
        btn_minus.setStyleSheet("background-color: #334155; border-radius: 4px; font-weight: bold;")
        btn_minus.clicked.connect(lambda: self.change_progress(-1))

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.course.total_units)
        self.progress_bar.setValue(self.course.completed_units)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat(f"%v / %m {self.get_unit_name()}")
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #334155;
                border-radius: 5px;
                background-color: #0f172a;
                color: white;
                text-align: center;
            }
            QProgressBar::chunk { background-color: #10b981; border-radius: 4px; }
        """)

        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(30, 30)
        btn_plus.setStyleSheet("background-color: #10b981; border-radius: 4px; font-weight: bold; color: white;")
        btn_plus.clicked.connect(lambda: self.change_progress(1))

        prog_layout.addWidget(btn_minus)
        prog_layout.addWidget(self.progress_bar)
        prog_layout.addWidget(btn_plus)

        main_layout.addLayout(prog_layout)

    def get_unit_name(self):
        if self.course.course_type == CourseType.BOOK: return "стор."
        if self.course.course_type == CourseType.CHALLENGE: return "раз"
        if self.course.course_type == CourseType.PROJECT: return "%"
        return "ур."

    def change_progress(self, delta):
        new_val = self.course.completed_units + delta
        if 0 <= new_val <= self.course.total_units:
            self.course.completed_units = new_val

            if new_val == self.course.total_units:
                self.course.status = CourseStatus.COMPLETED
            elif new_val > 0 and self.course.status == CourseStatus.PLANNED:
                self.course.status = CourseStatus.IN_PROGRESS

            self.parent_tab.mw.storage.save_course(self.course)
            self.parent_tab.refresh_list()

    def edit_course(self):
        # Передаємо аргументи іменовано, щоб уникнути помилок
        dialog = EditCourseDialog(self.parent_tab.mw, user_id=self.course.user_id,
                                  storage=self.parent_tab.mw.storage, course=self.course)
        if dialog.exec_():
            self.parent_tab.refresh_list()

    def delete_course(self):
        reply = QMessageBox.question(self, "Видалення", f"Видалити '{self.course.title}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.parent_tab.mw.storage.delete_course(self.course.id)
            self.parent_tab.refresh_list()


class DevelopmentTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.selected_topic = DevelopmentTopic.EDUCATION  # Default
        self.setup_header()
        self.refresh_list()

    def setup_header(self):
        # Container for the whole header
        header_widget = QWidget()
        main_layout = QVBoxLayout(header_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # 1. Title
        title = QLabel("🚀 Центр Розвитку")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        main_layout.addWidget(title)

        # 2. Topic Buttons (Big & Nice)
        self.topic_layout = QHBoxLayout()
        self.topic_layout.setSpacing(10)

        self.topic_buttons = {}

        topics = [
            (DevelopmentTopic.EDUCATION, "🎓 Навчання"),
            (DevelopmentTopic.SPORT, "💪 Спорт"),
            (DevelopmentTopic.CREATIVITY, "🎨 Творчість"),
            (DevelopmentTopic.CAREER, "💼 Кар'єра")
        ]

        for topic_enum, text in topics:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            # При кліку викликаємо зміну топіка
            btn.clicked.connect(lambda checked, t=topic_enum: self.change_topic(t))
            self.topic_buttons[topic_enum] = btn
            self.topic_layout.addWidget(btn)

        # Кнопка "Інше" (Other)
        btn_other = QPushButton("📂 Інше")
        btn_other.setCheckable(True)
        btn_other.setFixedHeight(40)
        btn_other.clicked.connect(lambda: self.change_topic(DevelopmentTopic.OTHER))
        self.topic_buttons[DevelopmentTopic.OTHER] = btn_other
        self.topic_layout.addWidget(btn_other)

        self.update_btn_styles()
        main_layout.addLayout(self.topic_layout)

        # 3. Add Button (Right aligned in a row with filters if needed, or just below)
        row_controls = QHBoxLayout()

        self.filter_status = QComboBox()
        self.filter_status.addItems(["Всі статуси", "В процесі", "Заплановано", "Завершено"])
        self.filter_status.setStyleSheet(
            "background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; padding: 5px;")
        self.filter_status.currentIndexChanged.connect(self.refresh_list)

        btn_add = QPushButton("➕ Додати")
        btn_add.setStyleSheet("""
            QPushButton { background-color: #2563eb; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        btn_add.clicked.connect(self.add_course)

        row_controls.addWidget(self.filter_status)
        row_controls.addStretch()
        row_controls.addWidget(btn_add)

        main_layout.addLayout(row_controls)

        self.layout.insertWidget(0, header_widget)

    def change_topic(self, topic):
        self.selected_topic = topic
        self.update_btn_styles()
        self.refresh_list()

    def update_btn_styles(self):
        for topic, btn in self.topic_buttons.items():
            if topic == self.selected_topic:
                # Active Style
                btn.setStyleSheet("""
                    QPushButton { 
                        background-color: #2563eb; color: white; border: 2px solid #60a5fa; 
                        border-radius: 8px; font-weight: bold; font-size: 14px;
                    }
                """)
                btn.setChecked(True)
            else:
                # Inactive Style
                btn.setStyleSheet("""
                    QPushButton { 
                        background-color: #1e293b; color: #94a3b8; border: 1px solid #334155; 
                        border-radius: 8px; font-weight: 500; font-size: 14px;
                    }
                    QPushButton:hover { background-color: #334155; color: white; }
                """)
                btn.setChecked(False)

    def refresh_list(self):
        self.clear_list()
        all_courses = self.mw.storage.get_courses(self.mw.user_id)

        # 1. Filter by Topic
        topic_courses = [c for c in all_courses if c.topic == self.selected_topic]

        # 2. Filter by Status
        status_txt = self.filter_status.currentText()
        filtered = []
        for c in topic_courses:
            if status_txt == "Всі статуси":
                filtered.append(c)
            elif status_txt == "В процесі" and c.status == CourseStatus.IN_PROGRESS:
                filtered.append(c)
            elif status_txt == "Заплановано" and c.status == CourseStatus.PLANNED:
                filtered.append(c)
            elif status_txt == "Завершено" and c.status == CourseStatus.COMPLETED:
                filtered.append(c)

        if not filtered:
            lbl = QLabel(f"У категорії '{self.selected_topic.value}' поки пусто")
            lbl.setStyleSheet("color: #64748b; font-size: 16px; margin-top: 40px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(lbl)
            return

        # Sort: In Progress first
        filtered.sort(key=lambda x: x.status != CourseStatus.IN_PROGRESS)

        for course in filtered:
            card = CourseCard(course, self)
            self.list_layout.addWidget(card)

    def add_course(self):
        # Створюємо нову ціль із вже вибраним топіком
        new_c = type('obj', (object,),
                     {'topic': self.selected_topic, 'title': '', 'link': '', 'course_type': CourseType.COURSE,
                      'status': CourseStatus.IN_PROGRESS, 'completed_units': 0, 'total_units': 10})
        # Але EditDialog приймає course=None для створення.
        # Щоб передати дефолтний топік, можна трохи схитрувати або просто вибрати його в діалозі.
        # Для простоти передамо None, користувач сам вибере.

        dialog = EditCourseDialog(self.mw, user_id=self.mw.user_id, storage=self.mw.storage)
        # Хак: встановлюємо поточний топік в діалозі
        idx = dialog.topic_combo.findData(self.selected_topic)
        if idx >= 0: dialog.topic_combo.setCurrentIndex(idx)

        if dialog.exec_():
            self.refresh_list()