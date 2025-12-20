from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QCheckBox, QProgressBar, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from ..models import GoalStatus
from datetime import date
import sip  # ВАЖЛИВО: Для перевірки чи живий об'єкт C++


class QuestCard(QFrame):
    def __init__(self, goal, parent_tab):
        super().__init__()
        self.goal = goal
        self.parent_tab = parent_tab
        self.storage = parent_tab.mw.storage
        self.category = None

        if self.goal.category_id:
            cats = self.storage.get_categories(self.goal.user_id)
            for c in cats:
                if c.id == self.goal.category_id:
                    self.category = c
                    break

        self.init_ui()

    def init_ui(self):
        self.setObjectName("CardFrame")

        border_color = self.category.color if self.category else "#1e3a8a"

        self.style_normal = f"""
            QFrame#CardFrame {{
                background-color: #1e293b;
                border: 2px solid {border_color}; 
                border-radius: 8px;
            }}
            QLabel {{ border: none; background-color: transparent; color: #e0e0e0; }}
            QCheckBox {{ background-color: transparent; color: #e0e0e0; font-size: 13px; }}
        """

        self.style_highlight = f"""
            QFrame#CardFrame {{
                background-color: #1e3a8a;
                border: 2px solid #ea80fc; 
                border-radius: 8px;
            }}
            QLabel {{ border: none; background-color: transparent; color: #ffffff; }}
            QCheckBox {{ background-color: transparent; color: #ffffff; font-size: 13px; }}
        """

        self.setStyleSheet(self.style_normal)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        status_icon = "🔵"
        if self.goal.status == GoalStatus.COMPLETED:
            status_icon = "✅"
        elif self.goal.status == GoalStatus.IN_PROGRESS:
            status_icon = "🟡"
        elif self.goal.status == GoalStatus.MISSED:
            status_icon = "🔴"

        title_text = f"{status_icon} {self.goal.title}"
        if self.category:
            title_text += f"  <span style='font-size:12px; color:{self.category.color};'>[{self.category.name}]</span>"

        title_lbl = QLabel(title_text)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white; border: none;")

        delete_btn = QPushButton("✖")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #ef5350; border: none; font-size: 16px; font-weight: bold; } QPushButton:hover { color: #ff8a80; }")
        delete_btn.clicked.connect(self.confirm_delete)

        header_layout.addWidget(title_lbl, 1)
        header_layout.addWidget(delete_btn)
        layout.addLayout(header_layout)

        # Description
        if self.goal.description:
            desc_lbl = QLabel(self.goal.description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("color: #cbd5e1; font-size: 14px; margin-bottom: 5px; border: none;")
            desc_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            desc_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(desc_lbl)

        # Progress
        self.subgoals = self.storage.get_subgoals(self.goal.id)
        total_subs = len(self.subgoals)
        completed_subs = sum(1 for s in self.subgoals if s.is_completed)

        if total_subs > 0:
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, total_subs)
            self.progress_bar.setValue(completed_subs)
            self.progress_bar.setFormat(f"%p% ({completed_subs}/{total_subs})")
            self.progress_bar.setStyleSheet(
                "QProgressBar { border: 1px solid #1e4976; border-radius: 4px; background-color: #0f172a; text-align: center; color: white; font-size: 10px; height: 12px; } QProgressBar::chunk { background-color: #2563eb; border-radius: 3px; }")
            layout.addWidget(self.progress_bar)

        # Details
        details_text = f"Пріоритет: {self.goal.priority.value}"
        if self.goal.deadline: details_text += f"  |  Дедлайн: {self.goal.deadline}"
        details_lbl = QLabel(details_text)
        details_lbl.setStyleSheet("font-size: 12px; color: #64748b; margin-top: 2px; border: none;")
        layout.addWidget(details_lbl)

        # Subgoals
        if self.subgoals:
            sub_container = QFrame()
            sub_container.setStyleSheet("background-color: #111827; border-radius: 6px; margin-top: 8px; border: none;")
            sub_layout = QVBoxLayout(sub_container)
            sub_layout.setContentsMargins(10, 10, 10, 10)
            sub_layout.setSpacing(8)
            for sub in self.subgoals:
                row = QHBoxLayout()
                row.setContentsMargins(0, 0, 0, 0)
                chk = QCheckBox(sub.title)
                chk.setChecked(sub.is_completed)
                chk.setStyleSheet(
                    "QCheckBox { background: transparent; color: #e0e0e0; font-size: 13px; border: none; }")
                chk.stateChanged.connect(lambda state, s=sub: self.toggle_subgoal(state, s))
                row.addWidget(chk)
                row.addStretch()
                sub_layout.addLayout(row)
            layout.addWidget(sub_container)

        layout.addSpacing(5)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_style = "QPushButton { background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; border-radius: 6px; padding: 9px 12px; font-size: 13px; font-weight: 500; } QPushButton:hover { background-color: #2563eb; }"

        btn_subgoals = QPushButton("Підцілі")
        btn_subgoals.setStyleSheet(btn_style)
        btn_subgoals.clicked.connect(self.open_subgoals)

        btn_edit = QPushButton("Змінити ціль")
        btn_edit.setStyleSheet(btn_style)
        btn_edit.clicked.connect(self.edit_goal)

        btn_complete = QPushButton("Завершити")
        btn_complete.setStyleSheet(
            "QPushButton { background-color: #064e3b; color: white; border: 1px solid #10b981; border-radius: 6px; padding: 9px 12px; font-size: 13px; font-weight: 500; } QPushButton:hover { background-color: #065f46; }")
        btn_complete.clicked.connect(self.force_complete_goal)

        if self.goal.status == GoalStatus.COMPLETED:
            btn_complete.setVisible(False)
            btn_edit.setVisible(False)

        btn_layout.addWidget(btn_subgoals)
        btn_layout.addWidget(btn_edit)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_complete)
        layout.addLayout(btn_layout)

    def highlight_card(self):
        self.setStyleSheet(self.style_highlight)
        QTimer.singleShot(1500, self.reset_style)

    def reset_style(self):
        # ЗАХИСТ ВІД КРАШУ: Перевіряємо, чи об'єкт не видалено
        if sip.isdeleted(self) or not self.isVisible():
            return
        try:
            self.setStyleSheet(self.style_normal)
        except RuntimeError:
            pass

    def toggle_subgoal(self, state, subgoal):
        subgoal.is_completed = (state == Qt.Checked)
        self.storage.save_subgoal(subgoal)
        all_subs = self.storage.get_subgoals(self.goal.id)
        total = len(all_subs)
        completed = sum(1 for s in all_subs if s.is_completed)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(completed)
            self.progress_bar.setFormat(f"%p% ({completed}/{total})")

        old_status = self.goal.status
        new_status = old_status
        if total > 0:
            if completed == total:
                new_status = GoalStatus.COMPLETED
            elif completed > 0:
                new_status = GoalStatus.IN_PROGRESS
            else:
                new_status = GoalStatus.PLANNED

        if new_status != old_status:
            self.goal.status = new_status
            self.storage.save_goal(self.goal)
            self.parent_tab.update_list()

    def force_complete_goal(self):
        self.goal.status = GoalStatus.COMPLETED
        self.storage.save_goal(self.goal)
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
        if dialog.exec_(): self.parent_tab.update_list()

    def edit_goal(self):
        from .edit_goal_dialog import EditGoalDialog
        dialog = EditGoalDialog(self.parent_tab.mw, self.goal, storage=self.storage)
        if dialog.exec_(): self.parent_tab.update_list()


class HabitCard(QFrame):
    def __init__(self, habit, parent_tab):
        super().__init__()
        self.habit = habit
        self.parent_tab = parent_tab
        self.storage = parent_tab.mw.storage
        self.init_ui()

    def init_ui(self):
        self.setObjectName("HabitFrame")
        self.style_normal = """
            QFrame#HabitFrame {
                background-color: #1e293b;
                border: 2px solid #1e3a8a;
                border-radius: 8px;
            }
            QLabel { border: none; background-color: transparent; color: #e0e0e0; font-size: 16px; font-weight: bold; }
        """
        self.style_highlight = """
            QFrame#HabitFrame {
                background-color: #1e3a8a;
                border: 2px solid #ea80fc;
                border-radius: 8px;
            }
            QLabel { border: none; background-color: transparent; color: #ffffff; font-size: 16px; font-weight: bold; }
        """
        self.setStyleSheet(self.style_normal)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        # ВІДНОВЛЕНО ІМПОРТ date НА ПОЧАТКУ ФАЙЛУ
        today_str = date.today().isoformat()
        is_done = (self.habit.last_completed_date == today_str)
        icon = "🔥" if is_done else "⬜"
        title = QLabel(f"{icon}  {self.habit.title}")
        if is_done: title.setStyleSheet("color: #4ade80; font-size: 16px; font-weight: bold;")

        delete_btn = QPushButton("✖")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #ef5350; border: none; font-size: 16px; font-weight: bold; } QPushButton:hover { color: #ff8a80; }")
        delete_btn.clicked.connect(self.confirm_delete)

        header_row.addWidget(title, 1)
        header_row.addWidget(delete_btn)
        layout.addLayout(header_row)

        info_row = QHBoxLayout()
        streak = QLabel(f"Серія: {self.habit.streak} днів")
        streak.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: normal;")
        info_row.addWidget(streak)
        info_row.addStretch()
        layout.addLayout(info_row)
        layout.addSpacing(5)

        btn_layout = QHBoxLayout()
        btn_style = "QPushButton { background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; border-radius: 6px; padding: 7px 10px; font-size: 13px; font-weight: 500; } QPushButton:hover { background-color: #2563eb; }"

        btn_edit = QPushButton("Редагувати")
        btn_edit.setStyleSheet(btn_style)
        btn_edit.clicked.connect(self.edit_habit)

        btn_complete = QPushButton("Виконати" if not is_done else "Виконано")
        if is_done:
            btn_complete.setStyleSheet(
                "QPushButton { background-color: #064e3b; color: #4ade80; border: 1px solid #10b981; border-radius: 6px; padding: 7px 10px; }")
            btn_complete.setEnabled(False)
        else:
            btn_complete.setStyleSheet(
                "QPushButton { background-color: #064e3b; color: white; border: 1px solid #10b981; border-radius: 6px; padding: 7px 10px; } QPushButton:hover { background-color: #065f46; }")
            btn_complete.clicked.connect(self.complete_habit)

        btn_layout.addWidget(btn_edit)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_complete)
        layout.addLayout(btn_layout)

    def highlight_card(self):
        self.setStyleSheet(self.style_highlight)
        QTimer.singleShot(1500, self.reset_style)

    def reset_style(self):
        if sip.isdeleted(self) or not self.isVisible(): return
        try:
            self.setStyleSheet(self.style_normal)
        except:
            pass

    def confirm_delete(self):
        reply = QMessageBox.question(self, 'Видалення', f"Видалити звичку '{self.habit.title}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Спробуємо видалити (прямий SQL якщо методу нема, але краще додати метод в storage)
            import sqlite3
            conn = sqlite3.connect(self.storage.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM habits WHERE id = ?", (self.habit.id,))
            conn.commit()
            conn.close()
            self.parent_tab.update_list()

    def edit_habit(self):
        from .edit_habit_dialog import EditHabitDialog
        dialog = EditHabitDialog(self.parent_tab.mw, self.habit, storage=self.storage)
        if dialog.exec_(): self.parent_tab.update_list()

    def complete_habit(self):
        today_str = date.today().isoformat()
        if self.habit.last_completed_date != today_str:
            self.habit.streak += 1
            self.habit.last_completed_date = today_str
            self.storage.save_habit(self.habit)
            self.parent_tab.update_list()