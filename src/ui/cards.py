from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QCheckBox, QProgressBar, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from ..models import GoalStatus
from datetime import date


class QuestCard(QFrame):
    """
    Картка для відображення цілі (квесту).
    """

    def __init__(self, goal, parent_tab):
        super().__init__()
        self.goal = goal
        self.parent_tab = parent_tab  # Посилання на вкладку (QuestTab)
        self.storage = parent_tab.mw.storage  # Доступ до БД через головне вікно
        self.init_ui()

    def init_ui(self):
        # Стиль картки
        self.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 2px solid #1e3a8a;
                border-radius: 8px;
            }
            QLabel { border: none; background-color: transparent; color: #e0e0e0; }
            QCheckBox { background-color: transparent; color: #e0e0e0; font-size: 13px; }
            QProgressBar {
                border: 1px solid #1e4976;
                border-radius: 4px;
                background-color: #0f172a;
                text-align: center;
                color: white;
                font-size: 10px;
                height: 12px;
            }
            QProgressBar::chunk { background-color: #2563eb; border-radius: 3px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        status_icon = "🔵" if self.goal.status == GoalStatus.PLANNED else "✅"
        title_lbl = QLabel(f"{status_icon} {self.goal.title}")
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

        delete_btn = QPushButton("✖")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #ef5350; border: none; font-size: 16px; font-weight: bold; }
            QPushButton:hover { color: #ff8a80; }
        """)
        delete_btn.clicked.connect(self.confirm_delete)

        header_layout.addWidget(title_lbl, 1)
        header_layout.addWidget(delete_btn)
        layout.addLayout(header_layout)

        # --- DESCRIPTION ---
        if self.goal.description:
            desc_lbl = QLabel(self.goal.description)
            desc_lbl.setWordWrap(True)  # ВАЖЛИВО: Перенесення слів
            desc_lbl.setStyleSheet("color: #cbd5e1; font-size: 14px; margin-bottom: 5px;")
            # ВИПРАВЛЕНО: Використання констант QSizePolicy
            desc_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            layout.addWidget(desc_lbl)

        # --- PROGRESS BAR ---
        self.subgoals = self.storage.get_subgoals(self.goal.id)
        total_subs = len(self.subgoals)
        completed_subs = sum(1 for s in self.subgoals if s.is_completed)

        if total_subs > 0:
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, total_subs)
            self.progress_bar.setValue(completed_subs)
            self.progress_bar.setFormat(f"%p% ({completed_subs}/{total_subs})")
            layout.addWidget(self.progress_bar)

        # --- DETAILS ---
        details_text = f"Пріоритет: {self.goal.priority.value}"
        if self.goal.deadline:
            details_text += f"  |  Дедлайн: {self.goal.deadline}"
        details_lbl = QLabel(details_text)
        details_lbl.setStyleSheet("font-size: 12px; color: #64748b; margin-top: 2px;")
        layout.addWidget(details_lbl)

        # --- SUBGOALS LIST ---
        if self.subgoals:
            sub_container = QFrame()
            sub_container.setStyleSheet("background-color: #111827; border-radius: 6px; margin-top: 8px; border: none;")
            sub_layout = QVBoxLayout(sub_container)
            sub_layout.setContentsMargins(10, 10, 10, 10)
            sub_layout.setSpacing(12)  # Відступ між підцілями

            for sub in self.subgoals:
                row = QWidget()
                r_layout = QVBoxLayout(row)
                r_layout.setContentsMargins(0, 0, 0, 0)
                r_layout.setSpacing(4)

                # Checkbox row
                top_row = QHBoxLayout()
                chk = QCheckBox(sub.title)
                chk.setChecked(sub.is_completed)
                chk.stateChanged.connect(lambda state, s=sub: self.toggle_subgoal(state, s))
                top_row.addWidget(chk)
                top_row.addStretch()
                r_layout.addLayout(top_row)

                # Description row
                if sub.description:
                    sub_desc = QLabel(sub.description)
                    sub_desc.setWordWrap(True)  # ВАЖЛИВО: Текст підцілі теж переноситься
                    sub_desc.setStyleSheet("color: #94a3b8; font-size: 12px; margin-left: 24px;")
                    # Також додаємо SizePolicy для коректного відображення довгих описів підцілей
                    sub_desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    r_layout.addWidget(sub_desc)

                sub_layout.addWidget(row)
            layout.addWidget(sub_container)

        layout.addSpacing(5)

        # --- BUTTONS ---
        btn_layout = QHBoxLayout()
        btn_style = """
            QPushButton { 
                background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; 
                border-radius: 6px; padding: 9px 12px; font-size: 13px; font-weight: 500;
            }
            QPushButton:hover { background-color: #2563eb; }
        """

        btn_subgoals = QPushButton("Підцілі")
        btn_subgoals.setStyleSheet(btn_style)
        btn_subgoals.clicked.connect(self.open_subgoals)

        btn_edit = QPushButton("Змінити ціль")
        btn_edit.setStyleSheet(btn_style)
        btn_edit.clicked.connect(self.edit_goal)

        btn_complete = QPushButton("Завершити")
        btn_complete.setStyleSheet("""
            QPushButton { 
                background-color: #064e3b; color: white; border: 1px solid #10b981; 
                border-radius: 6px; padding: 9px 12px; font-size: 13px; font-weight: 500;
            }
            QPushButton:hover { background-color: #065f46; }
        """)
        btn_complete.clicked.connect(self.complete_goal)

        if self.goal.status == GoalStatus.COMPLETED:
            btn_complete.setVisible(False)
            btn_edit.setVisible(False)

        btn_layout.addWidget(btn_subgoals)
        btn_layout.addWidget(btn_edit)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_complete)
        layout.addLayout(btn_layout)

    def toggle_subgoal(self, state, subgoal):
        subgoal.is_completed = (state == Qt.Checked)
        self.storage.save_subgoal(subgoal)

        # Check auto-complete
        all_subs = self.storage.get_subgoals(self.goal.id)
        total = len(all_subs)
        completed = sum(1 for s in all_subs if s.is_completed)

        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(completed)
            self.progress_bar.setFormat(f"%p% ({completed}/{total})")

        if total > 0 and completed == total and self.goal.status != GoalStatus.COMPLETED:
            self.complete_goal()
        elif self.goal.status == GoalStatus.COMPLETED:
            self.goal.status = GoalStatus.PLANNED
            self.storage.save_goal(self.goal)
            self.parent_tab.mw.update_stats(-1)  # Відкат статистики
            self.parent_tab.update_list()

    def complete_goal(self):
        self.goal.status = GoalStatus.COMPLETED
        self.storage.save_goal(self.goal)
        self.parent_tab.mw.update_stats(1)
        self.parent_tab.update_list()

    def confirm_delete(self):
        reply = QMessageBox.question(self, 'Видалення', f"Видалити '{self.goal.title}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.storage.delete_goal(self.goal.id)
            self.parent_tab.update_list()

    def open_subgoals(self):
        from .subgoals_dialog import SubgoalsDialog
        dialog = SubgoalsDialog(self.parent_tab.mw, self.goal.id, self.storage)
        if dialog.exec_():
            self.parent_tab.update_list()

    def edit_goal(self):
        from .edit_goal_dialog import EditGoalDialog
        dialog = EditGoalDialog(self.parent_tab.mw, self.goal, storage=self.storage)
        if dialog.exec_():
            self.parent_tab.update_list()


class HabitCard(QFrame):
    """Картка для звички."""

    def __init__(self, habit, parent_tab):
        super().__init__()
        self.habit = habit
        self.parent_tab = parent_tab
        self.storage = parent_tab.mw.storage
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 2px solid #1e3a8a;
                border-radius: 8px;
            }
            QLabel { border: none; background-color: transparent; color: #e0e0e0; font-size: 16px; font-weight: bold; }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        today_str = date.today().isoformat()
        is_done = (self.habit.last_completed_date == today_str)

        icon = "🔥" if is_done else "⬜"
        title = QLabel(f"{icon}  {self.habit.title}")
        streak = QLabel(f"Серія: {self.habit.streak} днів")
        streak.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: normal;")

        if is_done:
            title.setStyleSheet("color: #4ade80; font-size: 16px; font-weight: bold;")

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(streak)

    def mouseDoubleClickEvent(self, event):
        # Подвійний клік - виконати звичку
        today_str = date.today().isoformat()
        if self.habit.last_completed_date != today_str:
            self.habit.streak += 1
            self.habit.last_completed_date = today_str
            self.storage.save_habit(self.habit)
            self.parent_tab.update_list()