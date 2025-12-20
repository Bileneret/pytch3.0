from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea,
    QHBoxLayout, QPushButton, QMessageBox, QLineEdit, QTextEdit,
    QWidget, QProgressBar, QSizePolicy, QFrame, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from src.models import SubGoal, GoalStatus

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


class ResizableTextBrowser(QTextEdit):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setPlainText(text)
        self.setFrameStyle(QFrame.NoFrame)
        self.setReadOnly(True)
        self.setStyleSheet("color: #94a3b8; font-size: 13px; background-color: transparent; border: none;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.document().contentsChanged.connect(self.adjust_height)
        self.adjust_height()

    def adjust_height(self):
        doc_height = self.document().size().height()
        self.setFixedHeight(int(doc_height + 10))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_height()


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


class SubgoalItemWidget(QFrame):
    def __init__(self, subgoal, parent_dialog):
        super().__init__()
        self.subgoal = subgoal
        self.parent_dialog = parent_dialog
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QFrame { background-color: #1e293b; border-bottom: 1px solid #334155; border-radius: 4px; }
            QFrame:hover { background-color: #1e3a8a; } 
            QLabel { background-color: transparent; border: none; color: white; }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        chk = QCheckBox()
        chk.setChecked(self.subgoal.is_completed)
        chk.setStyleSheet("""
            QCheckBox { background-color: transparent; }
            QCheckBox::indicator { 
                width: 18px; height: 18px; 
                background-color: transparent; 
                border: 1px solid #94a3b8; 
                border-radius: 3px;
            }
            QCheckBox::indicator:checked { 
                background-color: #2563eb; 
                border: 1px solid #3b82f6;
                image: url(:/icons/check.png);
            }
        """)
        # Використовуємо lambda для передачі стану
        chk.stateChanged.connect(lambda state: self.parent_dialog.toggle_subgoal(state, self.subgoal))

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_lbl = QLabel(self.subgoal.title)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: bold;")
        title_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        text_layout.addWidget(title_lbl)

        if self.subgoal.description:
            desc_widget = ResizableTextBrowser(self.subgoal.description)
            text_layout.addWidget(desc_widget)

        layout.addWidget(chk)
        layout.addLayout(text_layout, 1)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.parent_dialog.handle_item_click(self, event.modifiers())


class SubgoalsDialog(QDialog):
    def __init__(self, parent, goal_id, storage):
        super().__init__(parent)
        self.goal_id = goal_id
        self.storage = storage
        self.parent_window = parent

        # Отримуємо ціль при ініціалізації
        goals = self.storage.get_goals(self.parent_window.user_id)
        self.goal = next((g for g in goals if g.id == goal_id), None)
        self.selected_widgets = []

        self.setWindowTitle("Управління підцілями")
        self.resize(500, 650)
        self.init_ui()
        self.update_list()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: white; font-family: 'Segoe UI'; }
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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: 2px solid #1e3a8a; border-radius: 8px; background-color: #111827; }")

        container = QWidget()
        container.setStyleSheet("background-color: #111827;")
        self.items_layout = QVBoxLayout(container)
        self.items_layout.setAlignment(Qt.AlignTop)
        self.items_layout.setSpacing(5)
        self.items_layout.setContentsMargins(5, 5, 5, 5)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setVisible(False)
        self.loading_bar.setFixedHeight(10)
        layout.addWidget(self.loading_bar)

        btns_layout = QHBoxLayout()
        btn_add = QPushButton("Додати")
        btn_add.clicked.connect(self.add_subgoal)
        btn_ai = QPushButton("AI Генерація")
        btn_ai.setObjectName("AiBtn")
        btn_ai.clicked.connect(self.generate_ai_subgoals)
        btn_edit = QPushButton("Редагувати")
        btn_edit.clicked.connect(self.edit_subgoal)
        btn_del = QPushButton("Видалити")
        btn_del.setObjectName("DelBtn")
        btn_del.clicked.connect(self.delete_subgoal)

        btns_layout.addWidget(btn_add)
        btns_layout.addWidget(btn_ai)
        btns_layout.addWidget(btn_edit)
        btns_layout.addWidget(btn_del)
        layout.addLayout(btns_layout)

        btn_close = QPushButton("Закрити")
        btn_close.setStyleSheet("background-color: transparent; border: 1px solid #475569; margin-top: 10px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.setLayout(layout)

    def update_list(self):
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        self.selected_widgets = []

        subgoals = self.storage.get_subgoals(self.goal_id)
        for sub in subgoals:
            item_widget = SubgoalItemWidget(sub, self)
            self.items_layout.addWidget(item_widget)

    def handle_item_click(self, widget, modifiers):
        is_ctrl = modifiers & Qt.ControlModifier
        if is_ctrl:
            if widget in self.selected_widgets:
                self.deselect_item(widget)
            else:
                self.select_item(widget, append=True)
        else:
            for w in list(self.selected_widgets):
                self.deselect_item(w)
            self.select_item(widget, append=False)

    def select_item(self, widget, append=False):
        if not append:
            self.selected_widgets = []
        self.selected_widgets.append(widget)
        widget.setStyleSheet("QFrame { background-color: #1d4ed8; border: 1px solid #60a5fa; border-radius: 4px; }")

    def deselect_item(self, widget):
        if widget in self.selected_widgets:
            self.selected_widgets.remove(widget)
        widget.setStyleSheet(
            "QFrame { background-color: #1e293b; border-bottom: 1px solid #334155; border-radius: 4px; } QFrame:hover { background-color: #1e3a8a; }")

    def add_subgoal(self):
        dialog = SubGoalInputDialog(self)
        if dialog.exec_():
            title, desc = dialog.get_data()
            if title:
                new_sub = SubGoal(title=title, description=desc, goal_id=self.goal_id)
                self.storage.save_subgoal(new_sub)
                self.update_list()
                # Викликаємо перевірку через таймер
                QTimer.singleShot(100, self._check_completion_logic)

    def edit_subgoal(self):
        if not self.selected_widgets:
            QMessageBox.warning(self, "Увага", "Оберіть підціль для редагування")
            return
        if len(self.selected_widgets) > 1:
            QMessageBox.warning(self, "Увага", "Для редагування треба вибрати лише одну підціль.")
            return

        widget = self.selected_widgets[0]
        sub = widget.subgoal
        dialog = SubGoalInputDialog(self, title_text=sub.title, desc_text=sub.description)
        if dialog.exec_():
            title, desc = dialog.get_data()
            if title:
                sub.title = title
                sub.description = desc
                self.storage.save_subgoal(sub)
                self.update_list()

    def delete_subgoal(self):
        if not self.selected_widgets:
            QMessageBox.warning(self, "Увага", "Оберіть підціль(лі) для видалення")
            return

        count = len(self.selected_widgets)
        msg = "Видалити цю підціль?" if count == 1 else f"Видалити {count} підцілей?"
        reply = QMessageBox.question(self, "Видалити", msg, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for widget in self.selected_widgets:
                self.storage.delete_subgoal(widget.subgoal.id)
            self.update_list()
            QTimer.singleShot(100, self._check_completion_logic)

    def toggle_subgoal(self, state, sub):
        """Зміна стану підцілі та запуск логіки перевірки."""
        # 1. Зберігаємо стан миттєво
        sub.is_completed = (state == Qt.Checked)
        self.storage.save_subgoal(sub)

        # 2. Відкладений виклик перевірки, щоб уникнути крашів
        QTimer.singleShot(50, self._check_completion_logic)

    def _check_completion_logic(self):
        """Перевіряє, чи всі підцілі виконані, і змінює статус головної цілі."""
        # Отримуємо найсвіжіші дані
        all_subs = self.storage.get_subgoals(self.goal_id)
        if not all_subs: return

        total = len(all_subs)
        completed = sum(1 for s in all_subs if s.is_completed)

        # Оновлюємо об'єкт цілі з бази даних, щоб уникнути конфліктів
        goals = self.storage.get_goals(self.parent_window.user_id)
        current_goal = next((g for g in goals if g.id == self.goal_id), None)
        if not current_goal: return
        self.goal = current_goal

        # Отримуємо користувача з бази даних (ВИПРАВЛЕННЯ КРАШУ)
        # Раніше ми зверталися до self.parent_window.user, якого не існувало
        user = self.storage.get_user_by_id(self.parent_window.user_id)
        if not user: return

        # ЛОГІКА АВТОЗАВЕРШЕННЯ
        if total > 0 and completed == total:
            if self.goal.status != GoalStatus.COMPLETED:
                self.goal.status = GoalStatus.COMPLETED
                self.storage.save_goal(self.goal)

                # Оновлюємо статистику
                user.total_completed_goals += 1
                self.storage.update_user_stats(user.id, user.total_completed_goals)

                #QMessageBox.information(self, "Вітаємо", "Всі підцілі виконано! Головна ціль завершена.")

        # ЛОГІКА ВІДКАТУ (Автовідміна завершення)
        elif self.goal.status == GoalStatus.COMPLETED and completed < total:
            # Повертаємо в статус "В процесі" (або PLANNED)
            self.goal.status = GoalStatus.IN_PROGRESS if completed > 0 else GoalStatus.PLANNED
            self.storage.save_goal(self.goal)

            # Відкат статистики
            if user.total_completed_goals > 0:
                user.total_completed_goals -= 1
                self.storage.update_user_stats(user.id, user.total_completed_goals)

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
        QTimer.singleShot(100, self._check_completion_logic)
        QMessageBox.information(self, "Успіх", f"Додано {len(subgoals_data)} кроків!")

    def on_ai_error(self, err_msg):
        self.loading_bar.setVisible(False)
        self.setEnabled(True)
        QMessageBox.warning(self, "Помилка AI", err_msg)