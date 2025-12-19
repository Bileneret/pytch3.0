from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QHBoxLayout, QPushButton, QMessageBox, QLineEdit, QTextEdit,
    QAbstractItemView, QWidget, QProgressBar, QSizePolicy, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from src.models import SubGoal

try:
    from src.logic.ai_service import AIService
except ImportError:
    AIService = None


class AIWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, goal_title, goal_desc, difficulty):
        super().__init__()
        self.goal_title = goal_title
        self.goal_desc = goal_desc
        self.difficulty = difficulty

    def run(self):
        if not AIService:
            self.error.emit("AI Service не знайдено.")
            return
        try:
            service = AIService()
            subgoals_data = service.generate_subgoals(self.goal_title, self.goal_desc, self.difficulty)
            self.finished.emit(subgoals_data)
        except Exception as e:
            self.error.emit(str(e))


class SubGoalInputDialog(QDialog):
    def __init__(self, parent=None, title_text="", desc_text=""):
        super().__init__(parent)
        self.setWindowTitle("Підціль")
        self.resize(400, 300)
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QLabel { color: #90caf9; font-weight: bold; font-size: 14px; margin-top: 10px; }
            QLineEdit, QTextEdit { 
                background-color: #172a45; color: white; border: 1px solid #1e4976; 
                padding: 8px; border-radius: 6px; 
            }
            QLineEdit:focus, QTextEdit:focus { border: 1px solid #3b82f6; }
            QPushButton { 
                background-color: #1d4ed8; color: white; border: 1px solid #3b82f6;
                padding: 8px 16px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2563eb; }
            QPushButton#CancelBtn { background-color: #1e293b; border: 1px solid #475569; color: #cbd5e1; }
            QPushButton#CancelBtn:hover { background-color: #334155; }
        """)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Назва:"))
        self.title_input = QLineEdit(title_text)
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("Опис:"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlainText(desc_text)
        layout.addWidget(self.desc_input)

        btns = QHBoxLayout()
        btn_save = QPushButton("Зберегти")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("Скасувати")
        btn_cancel.setObjectName("CancelBtn")
        btn_cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        layout.addLayout(btns)
        self.setLayout(layout)

    def get_data(self):
        return self.title_input.text().strip(), self.desc_input.toPlainText().strip()


class SubgoalListWidget(QWidget):
    """
    Кастомний віджет, який вставляється всередину QListWidgetItem.
    Це дозволяє мати Title + Description (WordWrap) в одному елементі списку.
    """

    def __init__(self, subgoal):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        # Назва
        title_lbl = QLabel(subgoal.title)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: white; background: transparent;")
        layout.addWidget(title_lbl)

        # Опис (якщо є)
        if subgoal.description:
            desc_lbl = QLabel(subgoal.description)
            desc_lbl.setWordWrap(True)  # Автоматичний перенос тексту
            desc_lbl.setStyleSheet("font-size: 13px; color: #94a3b8; background: transparent;")
            # Важливо: політика розміру для розтягування
            desc_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            layout.addWidget(desc_lbl)


class SubgoalsDialog(QDialog):
    def __init__(self, parent, goal_id, storage):
        super().__init__(parent)
        self.goal_id = goal_id
        self.storage = storage
        self.parent_window = parent

        goals = self.storage.get_goals(self.parent_window.user_id)
        self.goal = next((g for g in goals if g.id == goal_id), None)

        self.setWindowTitle("Управління підцілями")
        self.resize(500, 600)
        self.init_ui()
        self.update_list()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: white; font-family: 'Segoe UI'; }
            QListWidget { 
                background-color: #111827; border: 2px solid #1e3a8a; 
                border-radius: 8px; padding: 5px; outline: none;
            }
            QListWidget::item { 
                background-color: #1e293b; border-bottom: 1px solid #334155; 
                margin-bottom: 5px; border-radius: 4px; 
            }
            QListWidget::item:selected { 
                background-color: #1d4ed8; border: 1px solid #60a5fa; 
            }
            QPushButton { 
                background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; 
                border-radius: 6px; padding: 9px 12px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #2563eb; }
            QPushButton#AiBtn { background-color: #7c3aed; border-color: #8b5cf6; }
            QPushButton#AiBtn:hover { background-color: #8b5cf6; }
            QPushButton#DelBtn { background-color: #7f1d1d; border-color: #ef4444; }
            QPushButton#DelBtn:hover { background-color: #b91c1c; }
            QProgressBar {
                border: 2px solid #1e3a8a; border-radius: 5px; text-align: center; background-color: #0f172a;
            }
            QProgressBar::chunk { background-color: #7c3aed; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header = QLabel(f"Підцілі для: {self.goal.title if self.goal else '...'}")
        header.setStyleSheet("color: #90caf9; font-size: 16px; font-weight: bold;")
        header.setWordWrap(True)
        layout.addWidget(header)

        # QListWidget (Classic approach)
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.itemDoubleClicked.connect(self.edit_subgoal)
        layout.addWidget(self.list_widget)

        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setVisible(False)
        self.loading_bar.setFixedHeight(10)
        layout.addWidget(self.loading_bar)

        btns = QHBoxLayout()
        btn_add = QPushButton("Додати")
        btn_add.clicked.connect(self.add_subgoal)

        btn_edit = QPushButton("Редагувати")
        btn_edit.clicked.connect(self.edit_subgoal)

        btn_ai = QPushButton("AI Генерація")
        btn_ai.setObjectName("AiBtn")
        btn_ai.clicked.connect(self.generate_ai_subgoals)

        btn_del = QPushButton("Видалити")
        btn_del.setObjectName("DelBtn")
        btn_del.clicked.connect(self.delete_subgoal)

        btns.addWidget(btn_add)
        btns.addWidget(btn_edit)
        btns.addWidget(btn_ai)
        btns.addWidget(btn_del)
        layout.addLayout(btns)

        btn_close = QPushButton("Закрити")
        btn_close.setStyleSheet("background-color: transparent; border: 1px solid #475569; margin-top: 10px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.setLayout(layout)

    def update_list(self):
        self.list_widget.clear()
        subgoals = self.storage.get_subgoals(self.goal_id)

        for sub in subgoals:
            item = QListWidgetItem()
            # Зберігаємо об'єкт підцілі в UserRole
            item.setData(Qt.UserRole, sub)

            # Створюємо кастомний віджет для відображення
            widget = SubgoalListWidget(sub)

            # Встановлюємо розмір елемента списку на основі розміру віджета
            item.setSizeHint(widget.sizeHint())

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def add_subgoal(self):
        dialog = SubGoalInputDialog(self)
        if dialog.exec_():
            title, desc = dialog.get_data()
            if title:
                new_sub = SubGoal(title=title, description=desc, goal_id=self.goal_id)
                self.storage.save_subgoal(new_sub)
                self.update_list()

    def edit_subgoal(self):
        # Якщо викликано подвійним кліком, отримуємо item, інакше з selectedItems
        items = self.list_widget.selectedItems()
        if not items:
            QMessageBox.warning(self, "Увага", "Оберіть підціль для редагування")
            return

        item = items[0]
        sub = item.data(Qt.UserRole)

        dialog = SubGoalInputDialog(self, title_text=sub.title, desc_text=sub.description)
        if dialog.exec_():
            title, desc = dialog.get_data()
            if title:
                sub.title = title
                sub.description = desc
                self.storage.save_subgoal(sub)
                self.update_list()

    def delete_subgoal(self):
        items = self.list_widget.selectedItems()
        if not items:
            QMessageBox.warning(self, "Увага", "Оберіть підціль для видалення")
            return

        reply = QMessageBox.question(self, "Видалити", "Видалити обрану підціль?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for item in items:
                sub = item.data(Qt.UserRole)
                self.storage.delete_subgoal(sub.id)
            self.update_list()

    def generate_ai_subgoals(self):
        if not self.goal: return
        if not AIService:
            QMessageBox.information(self, "AI", "AI сервіс недоступний.")
            return

        self.loading_bar.setVisible(True)
        self.setEnabled(False)
        difficulty = self.goal.priority.value if hasattr(self.goal, 'priority') else "Середній"
        self.thread = AIWorker(self.goal.title, self.goal.description, difficulty)
        self.thread.finished.connect(self.on_ai_finished)
        self.thread.error.connect(self.on_ai_error)
        self.thread.start()

    def on_ai_finished(self, subgoals_data):
        self.loading_bar.setVisible(False)
        self.setEnabled(True)
        if not subgoals_data:
            QMessageBox.information(self, "AI", "Не вдалося згенерувати підцілі.")
            return
        for data in subgoals_data:
            title = data.get('title', 'AI Step') if isinstance(data, dict) else str(data)
            desc = data.get('description', '') if isinstance(data, dict) else ""
            new_sub = SubGoal(title=title, description=desc, goal_id=self.goal_id)
            self.storage.save_subgoal(new_sub)
        self.update_list()
        QMessageBox.information(self, "Успіх", f"Додано {len(subgoals_data)} кроків!")

    def on_ai_error(self, err_msg):
        self.loading_bar.setVisible(False)
        self.setEnabled(True)
        QMessageBox.warning(self, "Помилка AI", err_msg)