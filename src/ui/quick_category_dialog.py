from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QLabel, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap
from .category_dialog import CategoryDialog


class QuickCategoryDialog(QDialog):
    def __init__(self, parent, user_id, storage):
        super().__init__(parent)
        self.user_id = user_id
        self.storage = storage
        self.selected_category_id = None

        self.setWindowTitle("Оберіть категорію")
        self.resize(300, 400)
        self.setup_ui()
        self.load_categories()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QListWidget { 
                background-color: #111827; 
                border: 1px solid #1e3a8a; 
                border-radius: 6px; 
                outline: none;
            }
            QListWidget::item { 
                padding: 10px; 
                border-bottom: 1px solid #1e293b; 
                color: white;
            }
            QListWidget::item:selected { 
                background-color: #1e3a8a; 
                border-radius: 4px;
            }
            QListWidget::item:hover { background-color: #1f2937; }

            QPushButton { 
                background-color: #2563eb; color: white; border: none; 
                border-radius: 6px; padding: 10px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #1d4ed8; }

            QPushButton#ManageBtn {
                background-color: transparent; border: 1px solid #3b82f6; color: #3b82f6;
            }
            QPushButton#ManageBtn:hover { background-color: #1e3a8a; color: white; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Доступні категорії:"))

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.select_and_close)
        layout.addWidget(self.list_widget)

        # Кнопки
        btn_layout = QHBoxLayout()

        manage_btn = QPushButton("Керування (+)")
        manage_btn.setObjectName("ManageBtn")
        manage_btn.clicked.connect(self.open_manager)

        select_btn = QPushButton("Обрати")
        select_btn.clicked.connect(self.select_and_close)

        btn_layout.addWidget(manage_btn)
        btn_layout.addWidget(select_btn)
        layout.addLayout(btn_layout)

    def load_categories(self):
        self.list_widget.clear()
        cats = self.storage.get_categories(self.user_id)

        if not cats:
            item = QListWidgetItem("Немає категорій")
            item.setFlags(Qt.NoItemFlags)
            self.list_widget.addItem(item)
            return

        for c in cats:
            item = QListWidgetItem(c.name)
            # Кольоровий квадратик
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(c.color))
            item.setIcon(QIcon(pixmap))

            item.setData(Qt.UserRole, c.id)
            self.list_widget.addItem(item)

    def select_and_close(self):
        item = self.list_widget.currentItem()
        if item and item.flags() & Qt.ItemIsEnabled:
            self.selected_category_id = item.data(Qt.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "Увага", "Оберіть категорію зі списку")

    def open_manager(self):
        # Відкриває повний менеджер категорій, якщо треба створити нову
        dialog = CategoryDialog(self, self.user_id, self.storage)
        dialog.exec_()
        self.load_categories()