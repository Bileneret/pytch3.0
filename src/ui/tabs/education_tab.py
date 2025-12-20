from PyQt5.QtWidgets import QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from .base_tab import BaseTab


class EducationTab(BaseTab):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.setup_header()
        self.setup_content()

    def setup_header(self):
        # Заголовок вкладки
        header_lbl = QLabel("Навчання")
        header_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding: 10px;")
        self.layout.insertWidget(0, header_lbl)

    def setup_content(self):
        # Поки що заглушка, тут буде функціонал навчання
        placeholder = QLabel("Тут будуть ваші курси та матеріали для навчання.")
        placeholder.setStyleSheet("color: #64748b; font-size: 16px; margin-top: 20px;")
        placeholder.setAlignment(Qt.AlignCenter)
        self.list_layout.addWidget(placeholder)

        # Можна додати кнопку "Додати курс" тощо