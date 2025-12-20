from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                             QPushButton, QLineEdit, QMessageBox, QLabel)
from src.models import Topic


class TopicManagerDialog(QDialog):
    def __init__(self, parent, user_id, storage):
        super().__init__(parent)
        self.user_id = user_id
        self.storage = storage
        self.setWindowTitle("Керування темами")
        self.resize(300, 400)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: white; }
            QListWidget { background-color: #111827; border: 1px solid #1e3a8a; border-radius: 4px; color: white; }
            QLineEdit { background-color: #1f2937; color: white; border: 1px solid #374151; padding: 5px; border-radius: 4px; }
            QPushButton { background-color: #2563eb; color: white; border-radius: 4px; padding: 6px; }
            QPushButton:hover { background-color: #1d4ed8; }
            QLabel { color: #9ca3af; }
        """)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Input row
        input_layout = QHBoxLayout()
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Нова тема...")

        btn_add = QPushButton("➕")
        btn_add.setFixedWidth(40)
        btn_add.clicked.connect(self.add_topic)

        input_layout.addWidget(self.inp_name)
        input_layout.addWidget(btn_add)
        layout.addLayout(input_layout)

        # Delete button
        btn_del = QPushButton("Видалити обрану")
        btn_del.setStyleSheet("background-color: #7f1d1d; color: white;")
        btn_del.clicked.connect(self.delete_topic)
        layout.addWidget(btn_del)

        self.load_topics()

    def load_topics(self):
        self.list_widget.clear()
        self.topics = self.storage.get_topics(self.user_id)
        for t in self.topics:
            self.list_widget.addItem(t.name)

    def add_topic(self):
        name = self.inp_name.text().strip()
        if not name: return

        # Check duplicate
        if any(t.name.lower() == name.lower() for t in self.topics):
            QMessageBox.warning(self, "Помилка", "Така тема вже існує")
            return

        new_topic = Topic(name=name, user_id=self.user_id)
        self.storage.save_topic(new_topic)
        self.inp_name.clear()
        self.load_topics()

    def delete_topic(self):
        row = self.list_widget.currentRow()
        if row < 0: return

        topic = self.topics[row]
        reply = QMessageBox.question(self, "Видалення",
                                     f"Видалити тему '{topic.name}'?\nКурси залишаться, але будуть без теми.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.storage.delete_topic(topic.id)
            self.load_topics()