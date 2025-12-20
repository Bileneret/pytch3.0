from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QCheckBox, QProgressBar, QMessageBox, QSizePolicy, QToolButton)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QCursor
from ..models import GoalStatus
from datetime import date
import sip


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
                border-radius: 10px;
            }}
            QLabel {{ border: none; background-color: transparent; color: #e0e0e0; }}
            QCheckBox {{ background-color: transparent; color: #e0e0e0; font-size: 13px; }}
        """

        self.style_highlight = f"""
            QFrame#CardFrame {{
                background-color: #1e3a8a;
                border: 2px solid #ea80fc; 
                border-radius: 10px;
            }}
            QLabel {{ border: none; background-color: transparent; color: #ffffff; }}
            QCheckBox {{ background-color: transparent; color: #ffffff; font-size: 13px; }}
        """

        self.setStyleSheet(self.style_normal)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 1. HEADER
        header_layout = QHBoxLayout()

        # Title Widget
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        # Title (Зберігаємо посилання на лейбл, щоб оновлювати текст без перемальовки картки)
        self.title_lbl = QLabel(self.get_title_text())
        self.title_lbl.setWordWrap(True)
        self.title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white; border: none;")
        title_layout.addWidget(self.title_lbl)

        # Category Button
        self.cat_btn = QPushButton()
        self.cat_btn.setCursor(QCursor(Qt.PointingHandCursor))

        if self.category:
            self.cat_btn.setText(f"[{self.category.name}]")
            self.cat_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {self.category.color}; 
                    text-align: left; font-size: 12px; font-weight: bold; border: none;
                    padding: 0px; margin: 0px;
                }}
                QPushButton:hover {{ color: #ffffff; }}
            """)
        else:
            self.cat_btn.setText("+ Додати категорію")
            self.cat_btn.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #60a5fa; 
                    text-align: left; font-size: 12px; border: none;
                    padding: 0px; margin: 0px;
                }
                QPushButton:hover { color: #93c5fd; text-decoration: underline; }
            """)

        self.cat_btn.clicked.connect(self.open_quick_category)
        title_layout.addWidget(self.cat_btn)

        header_layout.addWidget(title_widget, 1)

        # Delete Button
        delete_btn = QPushButton("✖")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #ef5350; border: none; font-size: 18px; font-weight: bold; }
            QPushButton:hover { color: #ff8a80; }
        """)
        delete_btn.clicked.connect(self.confirm_delete)
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # 2. DESCRIPTION
        if self.goal.description:
            desc_lbl = QLabel(self.goal.description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("color: #cbd5e1; font-size: 14px; margin-bottom: 8px; border: none;")
            desc_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            desc_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(desc_lbl)

        # 3. PROGRESS BAR
        self.subgoals = self.storage.get_subgoals(self.goal.id)
        total_subs = len(self.subgoals)
        completed_subs = sum(1 for s in self.subgoals if s.is_completed)

        if total_subs > 0:
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, total_subs)
            self.progress_bar.setValue(completed_subs)
            self.progress_bar.setFormat(f"%p% ({completed_subs}/{total_subs})")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #1e4976;
                    border-radius: 4px;
                    background-color: #0f172a;
                    text-align: center;
                    color: white;
                    font-size: 11px;
                    height: 14px;
                }
                QProgressBar::chunk { background-color: #2563eb; border-radius: 3px; }
            """)
            layout.addWidget(self.progress_bar)

        # 4. DETAILS
        details_text = f"Пріоритет: {self.goal.priority.value}"
        if self.goal.deadline:
            details_text += f"  |  Дедлайн: {self.goal.deadline}"
        details_lbl = QLabel(details_text)
        details_lbl.setStyleSheet("font-size: 12px; color: #64748b; margin-top: 5px; border: none;")
        layout.addWidget(details_lbl)

        # 5. SUBGOALS (COLLAPSIBLE)
        if self.subgoals:
            self.toggle_btn = QToolButton()
            self.toggle_btn.setText(f" Підцілі ({len(self.subgoals)})")
            self.toggle_btn.setCheckable(True)
            self.toggle_btn.setChecked(False)
            self.toggle_btn.setStyleSheet("""
                QToolButton {
                    color: #94a3b8; background: transparent; border: none; font-size: 13px; font-weight: bold;
                }
                QToolButton:hover { color: white; }
                QToolButton:checked { color: #60a5fa; }
            """)
            self.toggle_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.toggle_btn.setArrowType(Qt.RightArrow)
            self.toggle_btn.clicked.connect(self.on_toggle_subgoals)
            layout.addWidget(self.toggle_btn)

            self.sub_container = QFrame()
            self.sub_container.setVisible(False)
            self.sub_container.setStyleSheet(
                "background-color: #111827; border-radius: 8px; margin-top: 5px; border: none;")
            sub_layout = QVBoxLayout(self.sub_container)
            sub_layout.setContentsMargins(12, 12, 12, 12)
            sub_layout.setSpacing(8)

            for sub in self.subgoals:
                row = QHBoxLayout()
                row.setContentsMargins(0, 0, 0, 0)

                chk = QCheckBox(sub.title)
                chk.setChecked(sub.is_completed)
                chk.setStyleSheet(
                    "QCheckBox { background: transparent; color: #e0e0e0; font-size: 14px; border: none; padding: 4px; }")
                chk.stateChanged.connect(lambda state, s=sub: self.toggle_subgoal(state, s))

                row.addWidget(chk)
                row.addStretch()
                sub_layout.addLayout(row)

            layout.addWidget(self.sub_container)

        layout.addSpacing(8)

        # 6. BUTTONS
        btn_layout = QHBoxLayout()
        btn_style = """
            QPushButton { 
                background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; 
                border-radius: 6px; padding: 10px 14px; font-size: 13px; font-weight: 500;
            }
            QPushButton:hover { background-color: #2563eb; }
        """

        btn_subgoals = QPushButton("Підцілі")
        btn_subgoals.setStyleSheet(btn_style)
        btn_subgoals.clicked.connect(self.open_subgoals)

        btn_edit = QPushButton("Змінити")
        btn_edit.setStyleSheet(btn_style)
        btn_edit.clicked.connect(self.edit_goal)

        btn_complete = QPushButton("Завершити")
        btn_complete.setStyleSheet("""
            QPushButton { 
                background-color: #064e3b; color: white; border: 1px solid #10b981; 
                border-radius: 6px; padding: 10px 14px; font-size: 13px; font-weight: 500;
            }
            QPushButton:hover { background-color: #065f46; }
        """)
        btn_complete.clicked.connect(self.force_complete_goal)

        if self.goal.status == GoalStatus.COMPLETED:
            btn_complete.setVisible(False)
            btn_edit.setVisible(False)

        btn_layout.addWidget(btn_subgoals)
        btn_layout.addWidget(btn_edit)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_complete)
        layout.addLayout(btn_layout)

    # --- METHODS ---
    def get_title_text(self):
        """Повертає текст заголовка з іконкою статусу"""
        status_icon = "🔵"
        if self.goal.status == GoalStatus.COMPLETED:
            status_icon = "✅"
        elif self.goal.status == GoalStatus.IN_PROGRESS:
            status_icon = "🟡"
        elif self.goal.status == GoalStatus.MISSED:
            status_icon = "🔴"
        return f"{status_icon} {self.goal.title}"

    def on_toggle_subgoals(self, checked):
        self.sub_container.setVisible(checked)
        if checked:
            self.toggle_btn.setArrowType(Qt.DownArrow)
        else:
            self.toggle_btn.setArrowType(Qt.RightArrow)

    def open_quick_category(self):
        from .quick_category_dialog import QuickCategoryDialog
        dialog = QuickCategoryDialog(self.parent_tab.mw, self.goal.user_id, self.storage)
        if dialog.exec_() and dialog.selected_category_id:
            self.goal.category_id = dialog.selected_category_id
            self.storage.save_goal(self.goal)
            self.parent_tab.update_list()

    def highlight_card(self):
        self.setStyleSheet(self.style_highlight)
        QTimer.singleShot(1500, self.reset_style)

    def reset_style(self):
        if sip.isdeleted(self) or not self.isVisible(): return
        try:
            self.setStyleSheet(self.style_normal)
        except RuntimeError:
            pass

    def toggle_subgoal(self, state, subgoal):
        # 1. Зберігаємо стан підцілі
        subgoal.is_completed = (state == Qt.Checked)
        self.storage.save_subgoal(subgoal)

        # 2. Перераховуємо прогрес
        all_subs = self.storage.get_subgoals(self.goal.id)
        total = len(all_subs)
        completed = sum(1 for s in all_subs if s.is_completed)

        # 3. Оновлюємо прогрес-бар локально
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(completed)
            self.progress_bar.setFormat(f"%p% ({completed}/{total})")

        # 4. Логіка зміни статусу цілі
        old_status = self.goal.status
        new_status = old_status

        if total > 0:
            if completed == total:
                new_status = GoalStatus.COMPLETED
            elif completed > 0:
                new_status = GoalStatus.IN_PROGRESS
            else:
                new_status = GoalStatus.PLANNED

        # 5. Якщо статус змінився - зберігаємо і оновлюємо ЛОКАЛЬНО
        if new_status != old_status:
            self.goal.status = new_status
            self.storage.save_goal(self.goal)

            # ВАЖЛИВО: Оновлюємо лише іконку в заголовку, а НЕ весь список.
            # Це запобігає згортанню списку підцілей.
            self.title_lbl.setText(self.get_title_text())

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
        if dialog.exec_():
            self.parent_tab.update_list()

    def edit_goal(self):
        from .edit_goal_dialog import EditGoalDialog
        dialog = EditGoalDialog(self.parent_tab.mw, self.goal, storage=self.storage)
        if dialog.exec_():
            self.parent_tab.update_list()


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
            QFrame#HabitFrame { background-color: #1e293b; border: 2px solid #1e3a8a; border-radius: 10px; }
            QLabel { border: none; background-color: transparent; color: #e0e0e0; font-size: 16px; font-weight: bold; }
        """
        self.style_highlight = """
            QFrame#HabitFrame { background-color: #1e3a8a; border: 2px solid #ea80fc; border-radius: 10px; }
            QLabel { border: none; background-color: transparent; color: #ffffff; font-size: 16px; font-weight: bold; }
        """
        self.setStyleSheet(self.style_normal)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header_row = QHBoxLayout()
        today_str = date.today().isoformat()
        is_done = (self.habit.last_completed_date == today_str)
        icon = "🔥" if is_done else "⬜"
        title = QLabel(f"{icon}  {self.habit.title}")
        if is_done: title.setStyleSheet("color: #4ade80; font-size: 16px; font-weight: bold;")

        delete_btn = QPushButton("✖")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #ef5350; border: none; font-size: 18px; font-weight: bold; } QPushButton:hover { color: #ff8a80; }")
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
        btn_style = "QPushButton { background-color: #1e3a8a; color: white; border: 1px solid #3b82f6; border-radius: 6px; padding: 8px 12px; font-size: 13px; font-weight: 500; } QPushButton:hover { background-color: #2563eb; }"

        btn_edit = QPushButton("Редагувати")
        btn_edit.setStyleSheet(btn_style)
        btn_edit.clicked.connect(self.edit_habit)

        btn_complete = QPushButton("Виконати" if not is_done else "Виконано")
        if is_done:
            btn_complete.setStyleSheet(
                "QPushButton { background-color: #064e3b; color: #4ade80; border: 1px solid #10b981; border-radius: 6px; padding: 8px 12px; }")
            btn_complete.setEnabled(False)
        else:
            btn_complete.setStyleSheet(
                "QPushButton { background-color: #064e3b; color: white; border: 1px solid #10b981; border-radius: 6px; padding: 8px 12px; } QPushButton:hover { background-color: #065f46; }")
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