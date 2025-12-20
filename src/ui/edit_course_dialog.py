from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QSpinBox,
    QComboBox, QPushButton, QLabel, QHBoxLayout, QMessageBox, QTextEdit
)
from src.models import Course, CourseType, CourseStatus


class EditCourseDialog(QDialog):
    def __init__(self, parent, user_id=None, storage=None, course=None):
        super().__init__(parent)
        self.user_id = user_id
        self.storage = storage
        self.course = course
        self.setWindowTitle("Матеріал для навчання" if not course else "Редагувати матеріал")
        self.resize(400, 400)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QLineEdit, QSpinBox, QComboBox, QTextEdit { 
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

        type_layout = QHBoxLayout()

        type_container = QVBoxLayout()
        type_container.addWidget(QLabel("Тип:"))
        self.type_combo = QComboBox()
        for t in CourseType:
            self.type_combo.addItem(t.value, t)
        if self.course:
            idx = self.type_combo.findData(self.course.course_type)
            self.type_combo.setCurrentIndex(idx)
        type_container.addWidget(self.type_combo)

        status_container = QVBoxLayout()
        status_container.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        for s in CourseStatus:
            self.status_combo.addItem(s.value, s)
        if self.course:
            idx = self.status_combo.findData(self.course.status)
            self.status_combo.setCurrentIndex(idx)
        status_container.addWidget(self.status_combo)

        type_layout.addLayout(type_container)
        type_layout.addLayout(status_container)
        layout.addLayout(type_layout)

        # Progress
        prog_layout = QHBoxLayout()

        current_c = QVBoxLayout()
        current_c.addWidget(QLabel("Пройдено:"))
        self.current_spin = QSpinBox()
        self.current_spin.setRange(0, 99999)
        if self.course: self.current_spin.setValue(self.course.completed_units)
        current_c.addWidget(self.current_spin)

        total_c = QVBoxLayout()
        total_c.addWidget(QLabel("Всього (стор/уроків):"))
        self.total_spin = QSpinBox()
        self.total_spin.setRange(1, 99999)
        self.total_spin.setValue(10)
        if self.course: self.total_spin.setValue(self.course.total_units)
        total_c.addWidget(self.total_spin)

        prog_layout.addLayout(current_c)
        prog_layout.addLayout(total_c)
        layout.addLayout(prog_layout)

        layout.addWidget(QLabel("Посилання (опціонально):"))
        self.link_inp = QLineEdit()
        self.link_inp.setPlaceholderText("https://...")
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

        c_type = self.type_combo.currentData()
        status = self.status_combo.currentData()
        curr = self.current_spin.value()
        tot = self.total_spin.value()
        link = self.link_inp.text().strip()

        if self.course:
            self.course.title = title
            self.course.course_type = c_type
            self.course.status = status
            self.course.completed_units = curr
            self.course.total_units = tot
            self.course.link = link
            self.storage.save_course(self.course)
        else:
            new_c = Course(
                title=title, user_id=self.user_id, course_type=c_type,
                status=status, completed_units=curr, total_units=tot, link=link
            )
            self.storage.save_course(new_c)

        self.accept()