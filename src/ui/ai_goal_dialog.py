from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QProgressBar, QMessageBox, QFrame, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from datetime import datetime, timedelta
from src.logic.ai_service import AIService
from src.models import LearningGoal, GoalPriority, SubGoal


class AIChatWorker(QThread):
    response_received = pyqtSignal(str, object)

    def __init__(self, ai_service, chat_session, message):
        super().__init__()
        self.service = ai_service
        self.chat = chat_session
        self.message = message

    def run(self):
        try:
            text, json_data = self.service.send_to_chat(self.chat, self.message)
            self.response_received.emit(text, json_data)
        except Exception as e:
            self.response_received.emit(f"Помилка: {str(e)}", None)


class ChatInputArea(QTextEdit):
    submit_request = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Опишіть ціль (наприклад: 'Хочу вивчити Python')...")
        self.setStyleSheet("""
            QTextEdit {
                background-color: #172a45;
                color: #e0e0e0;
                border: 1px solid #1e4976;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 1px solid #3b82f6;
            }
        """)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedHeight(45)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            self.submit_request.emit()
        else:
            super().keyPressEvent(event)
            self.adjust_height()

    def adjust_height(self):
        doc_height = self.document().size().height()
        new_height = min(max(45, int(doc_height + 10)), 100)
        self.setFixedHeight(new_height)


class ChatBubble(QFrame):
    def __init__(self, text, is_user=True):
        super().__init__()
        # 4. Прибираємо всі рамки з самого фрейму
        self.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Стилізація повідомлень (БЕЗ РАМОК)
        if is_user:
            label.setStyleSheet("""
                QLabel {
                    background-color: #2563eb; 
                    color: white;
                    border-radius: 12px;
                    padding: 12px;
                    font-size: 14px;
                    border: none; /* Прибираємо біле обведення */
                }
            """)
            layout.addStretch()
            layout.addWidget(label)
        else:
            label.setStyleSheet("""
                QLabel {
                    background-color: #1e3a8a;
                    color: #e0e0e0;
                    border-radius: 12px;
                    padding: 12px;
                    font-size: 14px;
                    border: none; /* Прибираємо рамку */
                }
            """)
            layout.addWidget(label)
            layout.addStretch()


class AIGoalDialog(QDialog):
    def __init__(self, parent, user_id, storage):
        super().__init__(parent)
        self.user_id = user_id
        self.storage = storage
        self.setWindowTitle("AI Асистент 🤖")
        self.resize(500, 700)

        try:
            self.ai_service = AIService()
            self.chat_session = self.ai_service.start_chat()
        except Exception as e:
            QMessageBox.warning(self, "Помилка", f"Не вдалося запустити AI: {e}")
            self.ai_service = None

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI'; }
            QScrollArea { border: none; background: transparent; }
            QPushButton {
                background-color: #1e3a8a; color: white; border: 1px solid #3b82f6;
                border-radius: 6px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2563eb; }
            /* Кнопка прийняття цілі */
            QPushButton#AcceptBtn {
                background-color: #059669; border-color: #10b981; margin-top: 5px;
            }
            QPushButton#AcceptBtn:hover { background-color: #047857; }

            QProgressBar { border: none; background-color: #0f172a; height: 3px; }
            QProgressBar::chunk { background-color: #3b82f6; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Чат
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area)

        # Прогрес бар
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setVisible(False)
        main_layout.addWidget(self.loading_bar)

        # Ввід
        input_layout = QHBoxLayout()
        self.text_input = ChatInputArea()
        self.text_input.submit_request.connect(self.send_message)

        self.btn_send = QPushButton("➤")
        self.btn_send.setFixedSize(45, 45)
        self.btn_send.setStyleSheet("border-radius: 22px; font-size: 18px;")
        self.btn_send.clicked.connect(self.send_message)

        input_layout.addWidget(self.text_input)
        input_layout.addWidget(self.btn_send)
        main_layout.addLayout(input_layout)

        # Старт
        self.add_message("Привіт! Напишіть тему цілі, а я складу план (День 1, День 2...).", is_user=False)

    def add_message(self, text, is_user=True):
        if not text: return
        bubble = ChatBubble(text, is_user)
        self.chat_layout.addWidget(bubble)
        self.scroll_to_bottom()

    def add_system_widget(self, widget):
        """Додає віджет (кнопку) в потік чату."""
        container = QHBoxLayout()
        container.addStretch()
        container.addWidget(widget)
        container.addStretch()
        self.chat_layout.addLayout(container)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def send_message(self):
        text = self.text_input.toPlainText().strip()
        if not text: return

        if not self.ai_service:
            QMessageBox.warning(self, "Помилка", "AI сервіс недоступний.")
            return

        self.add_message(text, is_user=True)
        self.text_input.clear()
        self.text_input.adjust_height()

        # Блокування
        self.text_input.setReadOnly(True)
        self.btn_send.setEnabled(False)
        self.loading_bar.setVisible(True)

        self.worker = AIChatWorker(self.ai_service, self.chat_session, text)
        self.worker.response_received.connect(self.on_response)
        self.worker.start()

    def on_response(self, text, json_data):
        self.loading_bar.setVisible(False)
        # 2. Розблоковуємо ввід, щоб можна було правити ціль далі
        self.text_input.setReadOnly(False)
        self.btn_send.setEnabled(True)
        self.text_input.setFocus()

        self.add_message(text, is_user=False)

        # 1. Якщо прийшов JSON (ціль готова) - показуємо кнопку
        if json_data:
            btn_accept = QPushButton(f"✅ Додати ціль: {json_data.get('title', 'Ціль')}")
            btn_accept.setObjectName("AcceptBtn")
            btn_accept.setCursor(Qt.PointingHandCursor)
            # Прив'язуємо дані до кнопки через лямбду
            btn_accept.clicked.connect(lambda: self.create_goal_from_json(json_data))
            self.add_system_widget(btn_accept)

    def create_goal_from_json(self, data):
        try:
            # Парсинг складності
            diff_str = data.get("difficulty", "MEDIUM").upper()
            priority = GoalPriority.MEDIUM
            for p in GoalPriority:
                if p.value == diff_str or p.name == diff_str:
                    priority = p
                    break

            # Дедлайн
            deadline = None
            if "deadline_days" in data:
                days = int(data.get("deadline_days", 7))
                deadline = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

            # Створення
            new_goal = LearningGoal(
                title=data.get("title", "Нова ціль"),
                description=data.get("description", ""),
                deadline=deadline,
                priority=priority,
                user_id=self.user_id
            )
            self.storage.save_goal(new_goal)

            # Підцілі
            subgoals = data.get("subgoals", [])
            for sub in subgoals:
                new_sub = SubGoal(
                    title=sub.get("title", "Step"),
                    description=sub.get("description", ""),
                    goal_id=new_goal.id
                )
                self.storage.save_subgoal(new_sub)

            QMessageBox.information(self, "Успіх", "Ціль успішно додана!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити ціль: {e}")