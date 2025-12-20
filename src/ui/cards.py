from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QCheckBox, QProgressBar, QMessageBox, QSizePolicy, QToolButton)
from PyQt5.QtCore import Qt, QTimer, QSize, QUrl
from PyQt5.QtGui import QColor, QCursor, QDesktopServices
from ..models import GoalStatus
from datetime import date
import sip


class WrapLabel(QLabel):
    """
    Лейбл з 'агресивним' переносом слів.
    Ignored політика по горизонталі означає, що віджет не буде вимагати
    ширини, рівної довжині тексту, а прийме ту ширину, яку дасть layout.
    """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        # Ignored Horizontal = стискай мене як хочеш
        # Minimum Vertical = розширюй мене вниз, скільки треба тексту
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        self.setMinimumWidth(0)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)


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

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # === 1. HEADER ===
        header_layout = QHBoxLayout()
        # Важливо: AlignTop, щоб при розширенні картки вниз заголовок лишався зверху
        header_layout.setAlignment(Qt.AlignTop)

        # Контейнер для лівої частини (Назва + Категорія)
        title_container = QWidget()
        # Політика Expanding по горизонталі, щоб зайняти все місце і відштовхнути кнопки
        title_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        # НАЗВА ЦІЛІ (WrapLabel)
        self.title_lbl = WrapLabel(self.get_title_text())
        self.title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white; border: none;")
        title_layout.addWidget(self.title_lbl)

        # Кнопка категорії
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

        # Додаємо ліву частину
        header_layout.addWidget(title_container, 1)

        # Праві кнопки (Link, Edit, Delete)
        btns_container = QHBoxLayout()
        btns_container.setAlignment(Qt.AlignTop)  # Кнопки притиснуті до верху
        btns_container.setSpacing(5)

        if hasattr(self.goal, 'link') and self.goal.link:
            btn_link = QPushButton("🔗")
            btn_link.setFixedSize(30, 30)
            btn_link.setCursor(QCursor(Qt.PointingHandCursor))
            btn_link.setStyleSheet("""
                QPushButton { background-color: #0f172a; border-radius: 15px; color: #3b82f6; border: 1px solid #1e40af; }
                QPushButton:hover { background-color: #1e3a8a; }
            """)
            btn_link.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.goal.link)))
            btns_container.addWidget(btn_link)

        btn_edit_gear = QPushButton("⚙️")
        btn_edit_gear.setFixedSize(30, 30)
        btn_edit_gear.setCursor(QCursor(Qt.PointingHandCursor))
        btn_edit_gear.setStyleSheet("""
            QPushButton { background-color: transparent; color: #94a3b8; border: none; font-size: 18px; }
            QPushButton:hover { color: white; }
        """)
        btn_edit_gear.clicked.connect(self.edit_goal)
        btns_container.addWidget(btn_edit_gear)

        delete_btn = QPushButton("✖")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        delete_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #ef5350; border: none; font-size: 18px; font-weight: bold; }
            QPushButton:hover { color: #ff8a80; }
        """)
        delete_btn.clicked.connect(self.confirm_delete)
        btns_container.addWidget(delete_btn)

        header_layout.addLayout(btns_container)
        layout.addLayout(header_layout)

        # === 2. DESCRIPTION (WrapLabel) ===
        if self.goal.description:
            desc_lbl = WrapLabel(self.goal.description)
            desc_lbl.setStyleSheet("color: #cbd5e1; font-size: 14px; margin-bottom: 8px; border: none;")
            layout.addWidget(desc_lbl)

        # === 3. PROGRESS BAR ===
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

        # === 4. DETAILS ===
        details_text = f"Пріоритет: {self.goal.priority.value}"
        if self.goal.deadline:
            details_text += f"  |  Дедлайн: {self.goal.deadline}"
        details_lbl = QLabel(details_text)
        details_lbl.setStyleSheet("font-size: 12px; color: #64748b; margin-top: 5px; border: none;")
        layout.addWidget(details_lbl)

        # === 5. SUBGOALS ===
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
                row.setSpacing(10)
                row.setAlignment(Qt.AlignTop)

                chk = QCheckBox()
                chk.setChecked(sub.is_completed)
                chk.setFixedSize(20, 20)
                chk.setStyleSheet("QCheckBox { background: transparent; border: none; }")
                chk.stateChanged.connect(lambda state, s=sub: self.toggle_subgoal(state, s))

                # Текст підцілі - WrapLabel
                lbl_sub_text = WrapLabel(sub.title)
                lbl_sub_text.setStyleSheet("color: #e0e0e0; font-size: 14px; border: none; background: transparent;")

                if sub.is_completed:
                    lbl_sub_text.setStyleSheet(
                        "color: #64748b; font-size: 14px; border: none; background: transparent; text-decoration: line-through;")

                row.addWidget(chk)
                row.addWidget(lbl_sub_text, 1)
                sub_layout.addLayout(row)

            layout.addWidget(self.sub_container)

        layout.addSpacing(8)

        # === 6. BUTTONS ===
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

        self.btn_complete = QPushButton("Завершити")
        self.btn_complete.setStyleSheet("""
            QPushButton { 
                background-color: #064e3b; color: white; border: 1px solid #10b981; 
                border-radius: 6px; padding: 10px 14px; font-size: 13px; font-weight: 500;
            }
            QPushButton:hover { background-color: #065f46; }
        """)
        self.btn_complete.clicked.connect(self.force_complete_goal)

        if self.goal.status == GoalStatus.COMPLETED:
            self.btn_complete.setVisible(False)

        btn_layout.addWidget(btn_subgoals)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_complete)
        layout.addLayout(btn_layout)

    # --- Methods ---
    def get_title_text(self):
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
        subgoal.is_completed = (state == Qt.Checked)
        self.storage.save_subgoal(subgoal)
        all_subs = self.storage.get_subgoals(self.goal.id)
        total = len(all_subs)
        completed = sum(1 for s in all_subs if s.is_completed)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(completed)
            self.progress_bar.setFormat(f"%p% ({completed}/{total})")
        QTimer.singleShot(50, self._check_completion_logic)

    def _check_completion_logic(self):
        all_subs = self.storage.get_subgoals(self.goal.id)
        total = len(all_subs)
        completed = sum(1 for s in all_subs if s.is_completed)
        if total == 0: return
        user = self.storage.get_user_by_id(self.goal.user_id)
        if not user: return
        new_status = self.goal.status
        if completed == total:
            new_status = GoalStatus.COMPLETED
        elif completed > 0:
            new_status = GoalStatus.IN_PROGRESS
        else:
            new_status = GoalStatus.PLANNED
        if new_status != self.goal.status:
            if new_status == GoalStatus.COMPLETED and self.goal.status != GoalStatus.COMPLETED:
                user.total_completed_goals += 1
                self.storage.update_user_stats(user.id, user.total_completed_goals)
                self.btn_complete.setVisible(False)
            elif self.goal.status == GoalStatus.COMPLETED and new_status != GoalStatus.COMPLETED:
                if user.total_completed_goals > 0:
                    user.total_completed_goals -= 1
                    self.storage.update_user_stats(user.id, user.total_completed_goals)
                self.btn_complete.setVisible(True)
            self.goal.status = new_status
            self.storage.save_goal(self.goal)
            self.title_lbl.setText(self.get_title_text())

    def force_complete_goal(self):
        self.goal.status = GoalStatus.COMPLETED
        self.storage.save_goal(self.goal)
        user = self.storage.get_user_by_id(self.goal.user_id)
        if user:
            user.total_completed_goals += 1
            self.storage.update_user_stats(user.id, user.total_completed_goals)
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
        dialog = EditGoalDialog(
            self.parent_tab.mw,
            user_id=self.goal.user_id,
            storage=self.storage,
            goal=self.goal
        )
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
        header_row.setAlignment(Qt.AlignTop)

        today_str = date.today().isoformat()
        is_done = (self.habit.last_completed_date == today_str)
        icon = "🔥" if is_done else "⬜"

        # НАЗВА ЗВИЧКИ (WrapLabel)
        title = WrapLabel(f"{icon}  {self.habit.title}")
        if is_done:
            title.setStyleSheet("color: #4ade80; font-size: 16px; font-weight: bold; border: none;")
        else:
            title.setStyleSheet("color: #e0e0e0; font-size: 16px; font-weight: bold; border: none;")

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
        streak.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: normal; border: none;")
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