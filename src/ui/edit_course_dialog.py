from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QSpinBox,
    QComboBox, QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from src.models import Course, CourseType, CourseStatus


class EditCourseDialog(QDialog):
    def __init__(self, parent, user_id=None, storage=None, course=None):
        super().__init__(parent)
        self.user_id = user_id
        self.storage = storage
        self.course = course
        self.setWindowTitle("Матеріал для розвитку" if not course else "Редагувати матеріал")
        self.resize(400, 450)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QLineEdit, QSpinBox, QComboBox { 
                background-color: #111827; border: 1px solid #1e3a8a; border-radius: 4px; padding: 8px; color: white;
            }
            QLabel { font-weight: bold; margin-top: 5px; }
            QPushButton { 
                background-color: #2563eb; color: white; border: none; border-radius: 6px; padding: 10px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Назва:"))
        self.title_inp = QLineEdit()
        if self.course: self.title_inp.setText(self.course.title)
        layout.addWidget(self.title_inp)

        # Row 1
        row1 = QHBoxLayout()

        # Topics from DB
        col_topic = QVBoxLayout()
        col_topic.addWidget(QLabel("Категорія:"))
        self.topic_combo = QComboBox()

        topics = self.storage.get_topics(self.user_id)
        for t in topics:
            self.topic_combo.addItem(t.name, t.id)

        if self.course:
            # Set current index based on topic_id
            for i in range(self.topic_combo.count()):
                if self.topic_combo.itemData(i) == self.course.topic_id:
                    self.topic_combo.setCurrentIndex(i)
                    break
        col_topic.addWidget(self.topic_combo)

        # Type
        col_type = QVBoxLayout()
        col_type.addWidget(QLabel("Тип:"))
        self.type_combo = QComboBox()
        for t in CourseType:
            self.type_combo.addItem(t.value, t)
        if self.course:
            idx = self.type_combo.findData(self.course.course_type)
            self.type_combo.setCurrentIndex(idx)
        col_type.addWidget(self.type_combo)

        row1.addLayout(col_topic)
        row1.addLayout(col_type)
        layout.addLayout(row1)

        # Status
        layout.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        for s in CourseStatus:
            self.status_combo.addItem(s.value, s)
        if self.course:
            idx = self.status_combo.findData(self.course.status)
            self.status_combo.setCurrentIndex(idx)
        layout.addWidget(self.status_combo)

        # Progress
        prog_layout = QHBoxLayout()

        c_layout = QVBoxLayout()
        c_layout.addWidget(QLabel("Пройдено:"))
        self.current_spin = QSpinBox()
        self.current_spin.setRange(0, 99999)
        if self.course: self.current_spin.setValue(self.course.completed_units)
        c_layout.addWidget(self.current_spin)

        t_layout = QVBoxLayout()
        t_layout.addWidget(QLabel("Всього:"))
        self.total_spin = QSpinBox()
        self.total_spin.setRange(1, 99999)
        self.total_spin.setValue(10)
        if self.course: self.total_spin.setValue(self.course.total_units)
        t_layout.addWidget(self.total_spin)

        prog_layout.addLayout(c_layout)
        prog_layout.addLayout(t_layout)
        layout.addLayout(prog_layout)

        layout.addWidget(QLabel("Посилання:"))
        self.link_inp = QLineEdit()
        if self.course: self.link_inp.setText(self.course.link)
        layout.addWidget(self.link_inp)

        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

    def save(self):
        title = self.title_inp.text().strip()
        if not title:
            QMessageBox.warning(self, "Помилка", "Введіть назву")
            return

        topic_id = self.topic_combo.currentData()
        c_type = self.type_combo.currentData()
        status = self.status_combo.currentData()
        curr = self.current_spin.value()
        tot = self.total_spin.value()
        link = self.link_inp.text().strip()

        if not topic_id:
            QMessageBox.warning(self, "Помилка", "Оберіть категорію")
            return

        if self.course:
            self.course.title = title
            self.course.topic_id = topic_id
            self.course.course_type = c_type
            self.course.status = status
            self.course.completed_units = curr
            self.course.total_units = tot
            self.course.link = link
            self.storage.save_course(self.course)
        else:
            new_c = Course(
                title=title, user_id=self.user_id, topic_id=topic_id, course_type=c_type,
                status=status, completed_units=curr, total_units=tot, link=link
            )
            self.storage.save_course(new_c)

        self.accept()