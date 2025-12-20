from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QProgressBar, QFrame, QSizePolicy, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QCursor
from .base_tab import BaseTab
from ..edit_course_dialog import EditCourseDialog
from ..topic_manager_dialog import TopicManagerDialog
from ..search_dialog import SearchDialog
from ...models import CourseStatus, CourseType


class CourseCard(QFrame):
    # Сигнал, який повідомляє, що картка змінилася і список треба оновити
    course_changed = pyqtSignal()

    def __init__(self, course, parent_tab, topic_name=""):
        super().__init__()
        self.course = course
        self.parent_tab = parent_tab
        self.topic_name = topic_name
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("CardFrame")

        self.style_normal = """
            QFrame#CardFrame {
                background-color: #1e293b;
                border: 2px solid #334155;
                border-radius: 10px;
            }
            QLabel { border: none; background-color: transparent; color: #e0e0e0; }
        """

        self.style_highlight = """
            QFrame#CardFrame {
                background-color: #1e3a8a;
                border: 2px solid #ea80fc; 
                border-radius: 10px;
            }
            QLabel { border: none; background-color: transparent; color: #ffffff; }
        """

        self.setStyleSheet(self.style_normal)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # 1. HEADER
        header_layout = QHBoxLayout()

        title_widget = QWidget()
        title_inner = QVBoxLayout(title_widget)
        title_inner.setContentsMargins(0, 0, 0, 0)
        title_inner.setSpacing(2)

        icon_map = {
            CourseType.BOOK: "📖",
            CourseType.COURSE: "🎓",
            CourseType.VIDEO: "📺",
            CourseType.ARTICLE: "📄",
            CourseType.PROJECT: "🚀",
            CourseType.CHALLENGE: "🏆"
        }
        icon = icon_map.get(self.course.course_type, "🎓")

        # Title
        title_lbl = QLabel(f"{icon} {self.course.title}")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        title_lbl.setWordWrap(True)
        title_inner.addWidget(title_lbl)

        # Topic Label
        if self.topic_name:
            topic_lbl = QLabel(f"[{self.topic_name}]")
            topic_lbl.setStyleSheet("color: #60a5fa; font-size: 12px; font-weight: bold;")
            title_inner.addWidget(topic_lbl)

        header_layout.addWidget(title_widget, 1)

        # --- BUTTONS ---

        if self.course.link:
            btn_link = QPushButton("🔗")
            btn_link.setFixedSize(30, 30)
            btn_link.setCursor(QCursor(Qt.PointingHandCursor))
            btn_link.setStyleSheet("""
                QPushButton { background-color: #0f172a; border-radius: 15px; color: #3b82f6; border: 1px solid #1e40af; }
                QPushButton:hover { background-color: #1e3a8a; }
            """)
            btn_link.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.course.link)))
            header_layout.addWidget(btn_link)

        btn_edit = QPushButton("⚙️")
        btn_edit.setFixedSize(30, 30)
        btn_edit.setCursor(QCursor(Qt.PointingHandCursor))
        btn_edit.setStyleSheet("""
            QPushButton { background-color: transparent; color: #94a3b8; border: none; font-size: 18px; }
            QPushButton:hover { color: white; }
        """)
        btn_edit.clicked.connect(self.edit_course)
        header_layout.addWidget(btn_edit)

        btn_del = QPushButton("✖")
        btn_del.setFixedSize(28, 28)
        btn_del.setCursor(QCursor(Qt.PointingHandCursor))
        btn_del.setStyleSheet("""
            QPushButton { background-color: transparent; color: #ef5350; border: none; font-size: 18px; font-weight: bold; }
            QPushButton:hover { color: #ff8a80; }
        """)
        btn_del.clicked.connect(self.delete_course)
        header_layout.addWidget(btn_del)

        main_layout.addLayout(header_layout)

        # 2. PROGRESS BAR
        prog_layout = QHBoxLayout()

        chunk_color = "#10b981"
        if "Спорт" in self.topic_name:
            chunk_color = "#f59e0b"
        elif "Твор" in self.topic_name:
            chunk_color = "#ec4899"
        elif "Кар" in self.topic_name:
            chunk_color = "#6366f1"

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.course.total_units)
        self.progress_bar.setValue(self.course.completed_units)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat(f"%v / %m {self.get_unit_name()}")
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #1e4976;
                border-radius: 4px;
                background-color: #0f172a;
                text-align: center;
                color: white;
                font-size: 11px;
            }}
            QProgressBar::chunk {{ background-color: {chunk_color}; border-radius: 3px; }}
        """)

        btn_minus = QPushButton("-")
        btn_minus.setFixedSize(24, 24)
        btn_minus.setStyleSheet("background-color: #334155; border-radius: 4px; font-weight: bold; color: white;")
        btn_minus.clicked.connect(lambda: self.change_progress(-1))

        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(24, 24)
        btn_plus.setStyleSheet(f"background-color: {chunk_color}; border-radius: 4px; font-weight: bold; color: white;")
        btn_plus.clicked.connect(lambda: self.change_progress(1))

        prog_layout.addWidget(btn_minus)
        prog_layout.addWidget(self.progress_bar)
        prog_layout.addWidget(btn_plus)

        main_layout.addLayout(prog_layout)

    def get_unit_name(self):
        if self.course.course_type == CourseType.BOOK: return "стор."
        if self.course.course_type == CourseType.CHALLENGE: return "раз"
        if self.course.course_type == CourseType.PROJECT: return "%%"
        if "Спорт" in self.topic_name: return "км/раз"
        return "од."

    def change_progress(self, delta):
        old_status = self.course.status
        new_val = self.course.completed_units + delta

        if 0 <= new_val <= self.course.total_units:
            self.course.completed_units = new_val

            if new_val == self.course.total_units:
                self.course.status = CourseStatus.COMPLETED
            elif new_val > 0 and self.course.status == CourseStatus.PLANNED:
                self.course.status = CourseStatus.IN_PROGRESS
            elif new_val == 0 and self.course.status == CourseStatus.IN_PROGRESS:
                self.course.status = CourseStatus.PLANNED

            self.parent_tab.mw.storage.save_course(self.course)

            # Оновлюємо UI локально
            self.progress_bar.setValue(new_val)

            # Перевіряємо, чи треба перебудовувати список
            status_changed = (old_status != self.course.status)
            sort_mode = self.parent_tab.sort_combo.currentText()
            is_sorting_by_progress = "Прогрес" in sort_mode

            if status_changed or is_sorting_by_progress:
                # ВАЖЛИВО: Емітимо сигнал, а не викликаємо функцію напряму
                self.course_changed.emit()

    def edit_course(self):
        dialog = EditCourseDialog(self.parent_tab.mw, user_id=self.course.user_id,
                                  storage=self.parent_tab.mw.storage, course=self.course)
        if dialog.exec_():
            self.course_changed.emit()

    def delete_course(self):
        reply = QMessageBox.question(self, "Видалення", f"Видалити '{self.course.title}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.parent_tab.mw.storage.delete_course(self.course.id)
            self.course_changed.emit()

    def highlight_card(self):
        self.setStyleSheet(self.style_highlight)
        QTimer.singleShot(1500, self.reset_style)

    def reset_style(self):
        try:
            self.setStyleSheet(self.style_normal)
        except RuntimeError:
            pass


class DevelopmentTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.pinned_course_id = None
        self.should_highlight = False

        self.setup_header()
        self.setup_footer()

        self.load_topics()
        self.update_list()

    def setup_header(self):
        header = QHBoxLayout()
        header.setContentsMargins(10, 10, 10, 0)

        title_layout = QVBoxLayout()
        title = QLabel("🚀 Центр Розвитку")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        title_layout.addWidget(title)

        filters_row = QHBoxLayout()

        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Сорт: Статус",
            "Сорт: Назва",
            "Сорт: Прогрес",
            "Сорт: Дата"
        ])
        self.sort_combo.setFixedWidth(150)
        self.sort_combo.setStyleSheet(
            "background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; border-radius: 4px;")
        self.sort_combo.currentIndexChanged.connect(self.update_list)

        self.topic_filter = QComboBox()
        self.topic_filter.addItem("Всі теми", None)
        self.topic_filter.setFixedWidth(150)
        self.topic_filter.setStyleSheet(
            "background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; border-radius: 4px;")
        self.topic_filter.currentIndexChanged.connect(self.update_list)

        filters_row.addWidget(self.sort_combo)
        filters_row.addWidget(self.topic_filter)

        title_layout.addLayout(filters_row)
        header.addLayout(title_layout)
        header.addStretch()

        self.layout.insertLayout(0, header)

    def setup_footer(self):
        footer = QHBoxLayout()
        footer.setContentsMargins(10, 10, 10, 10)

        btn_style = "QPushButton { background-color: #1e3a8a; color: white; border: 2px solid #3b82f6; border-radius: 8px; padding: 10px 15px; font-weight: bold; } QPushButton:hover { background-color: #2563eb; }"
        btn_action_style = "QPushButton { background-color: #7c3aed; color: white; border: 2px solid #8b5cf6; border-radius: 8px; padding: 10px 15px; font-weight: bold; } QPushButton:hover { background-color: #8b5cf6; }"

        btn_add = QPushButton("➕ Новий Матеріал")
        btn_add.setStyleSheet(btn_style)
        btn_add.clicked.connect(self.add_course)

        btn_manage = QPushButton("🗂 Теми")
        btn_manage.setStyleSheet(btn_action_style)
        btn_manage.clicked.connect(self.open_topic_manager)

        btn_refresh = QPushButton("🔄 Оновити")
        btn_refresh.setStyleSheet(btn_style)
        btn_refresh.clicked.connect(self.update_list)

        btn_search = QPushButton("🔍 Пошук")
        btn_search.setStyleSheet(btn_style)
        btn_search.clicked.connect(self.open_search)

        footer.addWidget(btn_add)
        footer.addWidget(btn_manage)
        footer.addWidget(btn_refresh)
        footer.addWidget(btn_search)
        footer.addStretch()

        self.layout.addLayout(footer)

    def load_topics(self):
        current = self.topic_filter.currentData()
        self.topic_filter.blockSignals(True)
        self.topic_filter.clear()
        self.topic_filter.addItem("Всі теми", None)

        topics = self.mw.storage.get_topics(self.mw.user_id)
        for t in topics:
            self.topic_filter.addItem(t.name, t.id)

        if current:
            idx = self.topic_filter.findData(current)
            if idx >= 0: self.topic_filter.setCurrentIndex(idx)
        self.topic_filter.blockSignals(False)

    def update_list(self):
        self.clear_list()

        all_courses = self.mw.storage.get_courses(self.mw.user_id)

        # Filter
        topic_id = self.topic_filter.currentData()
        if topic_id:
            all_courses = [c for c in all_courses if c.topic_id == topic_id]

        # Sort
        sort_mode = self.sort_combo.currentText()
        if "Назва" in sort_mode:
            all_courses.sort(key=lambda x: x.title.lower())
        elif "Прогрес" in sort_mode:
            all_courses.sort(key=lambda x: (x.completed_units / x.total_units if x.total_units > 0 else 0),
                             reverse=True)
        elif "Дата" in sort_mode:
            all_courses.sort(key=lambda x: x.created_at, reverse=True)
        else:  # "Статус"
            all_courses.sort(key=lambda x: x.status != CourseStatus.IN_PROGRESS)

        if not all_courses:
            lbl = QLabel("Список порожній")
            lbl.setStyleSheet("color: gray; font-size: 16px; margin-top: 20px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(lbl)
            return

        topics = self.mw.storage.get_topics(self.mw.user_id)
        topic_map = {t.id: t.name for t in topics}

        target_card = None

        if self.pinned_course_id:
            pinned = next((c for c in all_courses if c.id == self.pinned_course_id), None)
            if pinned:
                all_courses.remove(pinned)
                all_courses.insert(0, pinned)

        for course in all_courses:
            t_name = topic_map.get(course.topic_id, "")
            card = CourseCard(course, self, topic_name=t_name)

            # ВАЖЛИВО: Підключаємо сигнал через чергу (QueuedConnection)
            # Це ключ до виправлення крашу 0xC0000409
            card.course_changed.connect(self.update_list, Qt.QueuedConnection)

            self.list_layout.addWidget(card)

            if self.pinned_course_id and course.id == self.pinned_course_id:
                target_card = card

        if target_card and self.should_highlight:
            QTimer.singleShot(100, target_card.highlight_card)
            self.should_highlight = False

    def add_course(self):
        current_topic_id = self.topic_filter.currentData()

        dialog = EditCourseDialog(self.mw, user_id=self.mw.user_id, storage=self.mw.storage)

        if current_topic_id:
            idx = dialog.topic_combo.findData(current_topic_id)
            if idx >= 0: dialog.topic_combo.setCurrentIndex(idx)

        if dialog.exec_():
            self.pinned_course_id = None
            self.update_list()

    def open_topic_manager(self):
        dialog = TopicManagerDialog(self.mw, self.mw.user_id, self.mw.storage)
        dialog.exec_()
        self.load_topics()
        self.update_list()

    def open_search(self):
        courses = self.mw.storage.get_courses(self.mw.user_id)
        if not courses:
            QMessageBox.information(self.mw, "Пошук", "Список матеріалів порожній.")
            return

        dialog = SearchDialog(self.mw, courses, self.mw.storage)
        if dialog.exec_() and dialog.selected_goal_id:
            self.pinned_course_id = dialog.selected_goal_id
            self.should_highlight = True
            self.update_list()

            if hasattr(self, 'scroll_area'):
                QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(0))