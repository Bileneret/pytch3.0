from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QListWidget, QListWidgetItem, QLabel,
                             QColorDialog, QMessageBox, QWidget)
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt
from ..models import Category


class CategoryDialog(QDialog):
    def __init__(self, parent, user_id, storage):
        super().__init__(parent)
        self.user_id = user_id
        self.storage = storage
        self.selected_color = "#3b82f6"  # Default blue

        self.setWindowTitle("Керування категоріями")
        self.resize(400, 500)
        self.setup_ui()
        self.load_categories()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QLineEdit { padding: 8px; border: 1px solid #1e3a8a; border-radius: 4px; background: #111827; color: white; }
            QListWidget { background: #111827; border: 1px solid #1e3a8a; border-radius: 4px; }
            QPushButton { background: #1e3a8a; color: white; border: none; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background: #2563eb; }
            QPushButton#ColorBtn { border: 1px solid #555; }
        """)

        layout = QVBoxLayout(self)

        # Form
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Назва категорії...")

        self.color_btn = QPushButton()
        self.color_btn.setObjectName("ColorBtn")
        self.color_btn.setFixedSize(35, 35)
        self.color_btn.setStyleSheet(f"background-color: {self.selected_color}; border-radius: 4px;")
        self.color_btn.clicked.connect(self.pick_color)

        add_btn = QPushButton("Додати")
        add_btn.clicked.connect(self.add_category)

        form_layout.addWidget(self.color_btn)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(add_btn)
        layout.addLayout(form_layout)

        # List
        self.cat_list = QListWidget()
        layout.addWidget(self.cat_list)

        # Delete Btn
        del_btn = QPushButton("Видалити обрану")
        del_btn.setStyleSheet("background-color: #7f1d1d; color: white;")
        del_btn.clicked.connect(self.delete_category)
        layout.addWidget(del_btn)

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_btn.setStyleSheet(f"background-color: {self.selected_color}; border-radius: 4px;")

    def load_categories(self):
        self.cat_list.clear()
        cats = self.storage.get_categories(self.user_id)
        for c in cats:
            item = QListWidgetItem(c.name)
            # Create a colored icon
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(c.color))
            item.setIcon(QIcon(pixmap))
            item.setData(Qt.UserRole, c.id)
            self.cat_list.addItem(item)

    def add_category(self):
        name = self.name_input.text().strip()
        if not name:
            return

        cat = Category(name=name, color=self.selected_color, user_id=self.user_id)
        self.storage.save_category(cat)
        self.name_input.clear()
        self.load_categories()

    def delete_category(self):
        item = self.cat_list.currentItem()
        if not item: return

        cat_id = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "Видалення", "Видалити категорію? Цілі залишаться, але без категорії.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.storage.delete_category(cat_id)
            self.load_categories()