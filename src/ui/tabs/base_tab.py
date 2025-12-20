from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt


class BaseTab(QWidget):
    """
    Базовий клас для вкладки. Забезпечує скролінг контенту.
    """

    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.mw = main_window

        # Основний лейаут вкладки
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.create_scroll_area()

    def create_scroll_area(self):
        # ЗБЕРІГАЄМО scroll_area В self, ЩОБ МАТИ ДОСТУП З НАСЛІДНИКІВ
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # Прозорий фон скролу
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")

        # Лейаут для карток (вирівнювання по верху)
        self.list_layout = QVBoxLayout(container)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.list_layout.setSpacing(10)
        self.list_layout.setContentsMargins(5, 5, 5, 20)

        self.scroll_area.setWidget(container)
        self.layout.addWidget(self.scroll_area)

    def clear_list(self):
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()