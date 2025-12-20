from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QListWidget, QListWidgetItem, QDesktopWidget, QFrame, QHBoxLayout,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import QTimer, Qt, QTime, QDate, pyqtSignal, QSize, QPoint
from PyQt5.QtGui import QColor, QFont, QCursor
from datetime import datetime, timedelta


class DeadlineItemWidget(QFrame):
    """Картка для відображення дедлайну у списку."""

    def __init__(self, title, time_str, is_urgent=False):
        super().__init__()
        # Стилізація картки (червона рамка, якщо терміново)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #111827;
                border: 1px solid {'#ef4444' if is_urgent else '#1e3a8a'};
                border-radius: 8px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # Назва цілі
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            "color: white; font-weight: bold; font-size: 14px; border: none; background: transparent;")

        # Час дедлайну
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet(
            f"color: {'#fca5a5' if is_urgent else '#94a3b8'}; font-size: 14px; border: none; background: transparent;")

        layout.addWidget(lbl_title, 1)
        layout.addWidget(lbl_time)


class SleepWindow(QWidget):
    wake_up_requested = pyqtSignal()

    # Відступ від краю (в пікселях), де спрацьовує зміна розміру
    RESIZE_MARGIN = 10

    def __init__(self, storage, user_id):
        super().__init__()
        self.storage = storage
        self.user_id = user_id

        # Змінні для керування переміщенням та розміром
        self.drag_pos = None
        self.resize_edge = None  # 'top', 'bottom', 'left', 'right' тощо

        self.setWindowTitle("Sleep Mode")
        self.resize(500, 600)

        # Безрамковий режим
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setStyleSheet("background-color: #0b0f19; color: #e0e0e0; font-family: 'Segoe UI';")

        # ВАЖЛИВО: Вмикаємо відстеження миші для динамічних рамок
        self.setMouseTracking(True)

        self.init_ui()
        self.center_on_screen()

        # Таймер годинника
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        self.load_deadlines()

    def init_ui(self):
        # Головний лейаут з відступами (щоб мишка могла схопити край)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- ТОП БАР ---
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        # Кнопка ЗГОРНУТИ
        btn_min = QPushButton("─")
        btn_min.setFixedSize(30, 30)
        btn_min.setToolTip("Згорнути")
        btn_min.setCursor(Qt.PointingHandCursor)
        btn_min.setStyleSheet("""
            QPushButton { background-color: transparent; color: #94a3b8; border: none; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background-color: #1f2937; color: white; border-radius: 4px; }
        """)
        btn_min.clicked.connect(self.showMinimized)
        top_bar.addWidget(btn_min)

        # Кнопка ЗАКРИТИ (ПРОКИНУТИСЯ)
        btn_close_top = QPushButton("✕")
        btn_close_top.setFixedSize(30, 30)
        btn_close_top.setToolTip("Прокинутися")
        btn_close_top.setCursor(Qt.PointingHandCursor)
        btn_close_top.setStyleSheet("""
            QPushButton { background-color: transparent; color: #94a3b8; border: none; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background-color: #7f1d1d; color: white; border-radius: 4px; }
        """)
        btn_close_top.clicked.connect(self.wake_up)
        top_bar.addWidget(btn_close_top)

        main_layout.addLayout(top_bar)

        # --- ВМІСТ ---
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 0, 20, 0)

        # ЛОГО
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(0)
        lbl_lgm = QLabel("LGM")
        lbl_lgm.setAlignment(Qt.AlignCenter)
        lbl_lgm.setStyleSheet("font-size: 64px; font-weight: 900; color: #1e3a8a; font-family: 'Arial Black';")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor("#1e3a8a"))
        lbl_lgm.setGraphicsEffect(shadow)
        logo_layout.addWidget(lbl_lgm)
        content_layout.addLayout(logo_layout)

        content_layout.addStretch(1)

        # ГОДИННИК
        self.lbl_time = QLabel()
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setStyleSheet(
            "font-family: 'Consolas', 'Courier New'; font-size: 72px; font-weight: bold; color: #60a5fa;")
        content_layout.addWidget(self.lbl_time)

        self.lbl_date = QLabel()
        self.lbl_date.setAlignment(Qt.AlignCenter)
        self.lbl_date.setStyleSheet("font-size: 20px; color: #94a3b8; font-weight: 500;")
        content_layout.addWidget(self.lbl_date)

        content_layout.addStretch(1)

        # СПИСОК
        self.lbl_list_header = QLabel("ПЛАН НА 7 ДНІВ")
        self.lbl_list_header.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold; letter-spacing: 1px;")
        self.lbl_list_header.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.lbl_list_header)

        self.deadlines_list = QListWidget()
        self.deadlines_list.setFocusPolicy(Qt.NoFocus)
        self.deadlines_list.setStyleSheet("""
            QListWidget { background: transparent; border: none; }
            QListWidget::item { background: transparent; padding: 5px; }
            QListWidget::item:hover { background: transparent; }
            QListWidget::item:selected { background: transparent; }
        """)
        self.deadlines_list.setFixedHeight(220)
        content_layout.addWidget(self.deadlines_list)

        content_layout.addStretch(1)

        # КНОПКА
        self.btn_wake = QPushButton("ПРОКИНУТИСЯ")
        self.btn_wake.setCursor(Qt.PointingHandCursor)
        self.btn_wake.setFixedSize(200, 50)
        self.btn_wake.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; border: none;
                border-radius: 25px; font-size: 14px; font-weight: bold; letter-spacing: 1px;
            }
            QPushButton:hover { background-color: #3b82f6; }
            QPushButton:pressed { background-color: #1d4ed8; }
        """)
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(20)
        btn_shadow.setColor(QColor("#2563eb"))
        self.btn_wake.setGraphicsEffect(btn_shadow)
        self.btn_wake.clicked.connect(self.wake_up)

        btn_container = QVBoxLayout()
        btn_container.setAlignment(Qt.AlignCenter)
        btn_container.addWidget(self.btn_wake)
        content_layout.addLayout(btn_container)

        # Відступ знизу, щоб підняти кнопку
        content_layout.addSpacing(40)

        main_layout.addLayout(content_layout)

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_time(self):
        current_time = QTime.currentTime()
        self.lbl_time.setText(current_time.toString("HH:mm:ss"))
        current_date = QDate.currentDate()
        self.lbl_date.setText(current_date.toString("dd MMMM yyyy").upper())

    def load_deadlines(self):
        self.deadlines_list.clear()
        goals = self.storage.get_goals(self.user_id)
        now = datetime.now()
        limit_date = now + timedelta(days=7)

        valid_goals = []
        for g in goals:
            # Фільтруємо завершені або без дедлайну
            if not g.deadline or g.status.name == "COMPLETED": continue
            try:
                # Парсинг дедлайну
                if len(g.deadline) == 10:
                    dt = datetime.strptime(g.deadline, "%Y-%m-%d").replace(hour=23, minute=59)
                else:
                    dt = datetime.strptime(g.deadline, "%Y-%m-%d %H:%M")

                # Перевірка діапазону
                if now <= dt <= limit_date:
                    valid_goals.append((g, dt))
            except ValueError:
                continue

        # Сортування
        valid_goals.sort(key=lambda x: x[1])

        for g, dt in valid_goals:
            item = QListWidgetItem(self.deadlines_list)
            item.setSizeHint(QSize(0, 60))

            is_urgent = (dt - now) < timedelta(hours=24)
            time_str = dt.strftime("%d.%m %H:%M")

            # Створюємо віджет (тепер клас DeadlineItemWidget визначено коректно)
            widget = DeadlineItemWidget(g.title, time_str, is_urgent)
            self.deadlines_list.setItemWidget(item, widget)

        if not valid_goals:
            item = QListWidgetItem("На найближчі 7 днів чисто 🎉")
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QColor("#4ade80"))
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            item.setFont(font)
            self.deadlines_list.addItem(item)

    def wake_up(self):
        self.wake_up_requested.emit()

    # --- ЛОГІКА ДИНАМІЧНИХ РАМОК (RESIZE & MOVE) ---

    def _check_edge(self, pos):
        """Визначає, чи знаходиться курсор на краю вікна."""
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        m = self.RESIZE_MARGIN

        edge = ""
        if y < m:
            edge += "top"
        elif y > h - m:
            edge += "bottom"

        if x < m:
            edge += "_left" if edge else "left"
        elif x > w - m:
            edge += "_right" if edge else "right"

        return edge if edge else None

    def _update_cursor(self, edge):
        """Змінює курсор в залежності від краю."""
        if edge == "top" or edge == "bottom":
            self.setCursor(Qt.SizeVerCursor)
        elif edge == "left" or edge == "right":
            self.setCursor(Qt.SizeHorCursor)
        elif edge == "top_left" or edge == "bottom_right":
            self.setCursor(Qt.SizeFDiagCursor)
        elif edge == "top_right" or edge == "bottom_left":
            self.setCursor(Qt.SizeBDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edge = self._check_edge(event.pos())
            if edge:
                # Починаємо зміну розміру
                self.resize_edge = edge
                self.drag_pos = event.globalPos()
            else:
                # Починаємо переміщення вікна
                self.resize_edge = None
                self.drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        # 1. Якщо не натиснута кнопка - просто міняємо курсор
        if not event.buttons() & Qt.LeftButton:
            edge = self._check_edge(event.pos())
            self._update_cursor(edge)
            return

        # 2. Якщо натиснута кнопка і ми в режимі зміни розміру
        if self.resize_edge:
            delta = event.globalPos() - self.drag_pos
            self.drag_pos = event.globalPos()

            geo = self.geometry()

            # Логіка зміни геометрії залежно від сторони
            if "top" in self.resize_edge:
                geo.setTop(geo.top() + delta.y())
            elif "bottom" in self.resize_edge:
                geo.setBottom(geo.bottom() + delta.y())

            if "left" in self.resize_edge:
                geo.setLeft(geo.left() + delta.x())
            elif "right" in self.resize_edge:
                geo.setRight(geo.right() + delta.x())

            self.setGeometry(geo)

        # 3. Якщо натиснута кнопка і ми в режимі переміщення
        elif self.drag_pos:
            delta = event.globalPos() - self.drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.resize_edge = None
        self.drag_pos = None
        self.setCursor(Qt.ArrowCursor)