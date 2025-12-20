from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QScrollArea, QWidget, QFrame
from PyQt5.QtCore import Qt


class FAQItem(QWidget):
    """
    Окремий елемент FAQ: Кнопка-питання та Текст-відповідь.
    """

    def __init__(self, question, answer):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 5)
        self.layout.setSpacing(0)

        # Кнопка питання
        self.btn_question = QPushButton(question)
        self.btn_question.setCursor(Qt.PointingHandCursor)
        self.btn_question.setStyleSheet("""
            QPushButton {
                text-align: left;
                background-color: #1f2937;
                color: #e5e7eb;
                padding: 12px 15px;
                border: 1px solid #374151;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #374151;
                border-color: #4b5563;
            }
        """)
        self.btn_question.clicked.connect(self.toggle_answer)
        self.layout.addWidget(self.btn_question)

        # Контейнер для відповіді (спочатку прихований)
        self.answer_frame = QFrame()
        self.answer_frame.setVisible(False)
        self.answer_frame.setStyleSheet("""
            QFrame {
                background-color: #111827;
                border-left: 2px solid #3b82f6;
                margin-top: 0px;
                border-bottom-right-radius: 6px;
                border-bottom-left-radius: 6px;
            }
        """)

        ans_layout = QVBoxLayout(self.answer_frame)
        self.lbl_answer = QLabel(answer)
        self.lbl_answer.setWordWrap(True)
        self.lbl_answer.setStyleSheet("color: #9ca3af; font-size: 13px; padding: 10px; border: none;")
        ans_layout.addWidget(self.lbl_answer)

        self.layout.addWidget(self.answer_frame)

    def toggle_answer(self):
        """Перемикає видимість відповіді."""
        is_visible = self.answer_frame.isVisible()
        self.answer_frame.setVisible(not is_visible)

        # Зміна стилю активної кнопки (опціонально)
        if not is_visible:
            self.btn_question.setStyleSheet(
                self.btn_question.styleSheet().replace("#374151", "#3b82f6"))  # Підсвітка рамки
        else:
            self.btn_question.setStyleSheet(
                self.btn_question.styleSheet().replace("#3b82f6", "#374151"))  # Повернення рамки


class FAQDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Часті запитання (FAQ)")
        self.resize(500, 600)
        self.setStyleSheet("background-color: #0b0f19;")

        layout = QVBoxLayout(self)

        # Заголовок
        lbl_title = QLabel("Довідка та FAQ")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #60a5fa; margin-bottom: 10px;")
        layout.addWidget(lbl_title)

        # Область прокрутки
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(10)

        # === НАПОВНЕННЯ ПИТАННЯМИ ===
        self.add_faq_item(
            "Що це за програма?",
            "Goal Manager Pro - це комплексний інструмент для саморозвитку і слідкування за власними цілями. Він поєднує в собі трекер цілей, менеджер звичок, планувальник навчання та аналітику Вашої продуктивності."
        )

        self.add_faq_item(
            "Як працюють \"Цілі\"?",
            "У вкладці \"Цілі\" Ви створюєте завдання з дедлайнами та пріоритетами. Великі цілі можна розбивати на підзавдання (Subgoals) власноруч або використовуючи вбудований серсіс із Штучним Інтелектом (ШІ). Виконання цілей підвищує вашу загальну статистику."
        )

        self.add_faq_item(
            "Що таке система \"Розвиток\"?",
            "Це розділ для керування Вашим навчанням. Ви можете додавати курси, книги або статті тощо. Вказуйте загальну кількість юнітів (сторінок, уроків, частин) та відстежуйте прогрес читання/перегляду без жорстких дедлайнів."
        )

        self.add_faq_item(
            "Як відстежувати звички?",
            "У вкладці \"Звички\" Ви сворюєте щоденне завдання з можливістю відмічати виконання по дням. Програма автоматично рахує Вашу серію днів виконання звички без перерв. Якщо пропустити день - серія обнулиться."
        )

        self.add_faq_item(
            "Чи можна перенести свої дані?",
            "Так, використовуючи дві кнопки у головному меню: \"Імпорт\" та \"Експорт\" у боковому панелі над кнопкою \"Вийти\". Експорт - завантажить дані цілей, звичок та розвитку у один JSON файл. Цей файл можна завантажити пізніше завдяки Імпорту на новому / іншому акаунті."
        )

        self.add_faq_item(
            "Я забув пароль, що робити?",
            "На даний момент відновлення паролю локальне. Якщо ви забули пароль, вам доведеться створити новий акаунт та імпортувати свої дані з минулого акаунту."
        )

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Кнопка закриття
        btn_close = QPushButton("Зрозуміло")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; 
                color: white; 
                padding: 10px; 
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def add_faq_item(self, question, answer):
        item = FAQItem(question, answer)
        self.content_layout.addWidget(item)