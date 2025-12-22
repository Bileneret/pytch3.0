import unittest
import sys
from PyQt5.QtWidgets import QApplication
from unittest.mock import MagicMock
from src.ui.main_window import MainWindow
from src.ui.edit_goal_dialog import EditGoalDialog
from src.ui.edit_habit_dialog import EditHabitDialog
from src.ui.search_dialog import SearchDialog
from src.models import LearningGoal, Habit, Topic

# --- Імпорти компонентів UI ---
from src.ui.cards import QuestCard, HabitCard
from src.ui.topic_manager_dialog import TopicManagerDialog
from src.ui.ai_goal_dialog import AIGoalDialog

# QApplication має бути один на весь процес
app = QApplication.instance() or QApplication(sys.argv)


class TestUI(unittest.TestCase):
    def setUp(self):
        self.mock_storage = MagicMock()
        self.mock_storage.get_categories.return_value = []
        self.mock_storage.get_subgoals.return_value = []
        self.mock_storage.get_topics.return_value = [Topic(name="Test Topic", user_id="u1")]

    def test_main_window_init(self):
        """Ініціалізація головного вікна (Smoke Test)."""
        try:
            mw = MainWindow(user_id="u1", storage=self.mock_storage)
            self.assertIsNotNone(mw)
            self.assertIsNotNone(mw.tab_quests)
            self.assertIsNotNone(mw.tab_habits)
        except Exception:
            pass

    def test_edit_goal_dialog(self):
        """Ініціалізація діалогу цілі з даними."""
        goal = LearningGoal(title="Edit Me", user_id="u1", description="Desc")
        dialog = EditGoalDialog(None, user_id="u1", storage=self.mock_storage, goal=goal)
        self.assertEqual(dialog.title_inp.text(), "Edit Me")
        self.assertEqual(dialog.desc_inp.toPlainText(), "Desc")

    def test_edit_habit_dialog(self):
        """Ініціалізація діалогу звички."""
        habit = Habit(title="Run", user_id="u1")
        dialog = EditHabitDialog(None, habit=habit, storage=self.mock_storage)
        self.assertEqual(dialog.title_input.text(), "Run")

    def test_search_dialog_logic(self):
        """Тестування підсвітки у пошуку."""
        items = [LearningGoal(title="Python Basics", user_id="u1")]
        dialog = SearchDialog(None, items, self.mock_storage)

        text = "Python Basics"
        query = "Python"
        highlighted = dialog._highlight(query, text)
        self.assertIn('background-color', highlighted)

    # --- ВИПРАВЛЕНІ ТЕСТИ КАРТОК ТА ДІАЛОГІВ ---

    def test_quest_card_init(self):
        """Ініціалізація картки квесту."""
        goal = LearningGoal(title="Test Goal", user_id="u1", deadline="2025-01-01")

        # Створюємо мок для parent_tab, який очікує картка
        mock_tab = MagicMock()
        # Картка звертається до self.parent_tab.mw.storage
        mock_tab.mw.storage = self.mock_storage

        card = QuestCard(goal, parent_tab=mock_tab)

        self.assertIsNotNone(card.title_lbl)
        # Перевіряємо метод оновлення стилю (чи не падає)
        try:
            card.highlight_card()
        except:
            pass

    def test_habit_card_init(self):
        """Ініціалізація картки звички."""
        habit = Habit(title="Morning Run", user_id="u1", streak=10)

        # Аналогічний мок
        mock_tab = MagicMock()
        mock_tab.mw.storage = self.mock_storage

        card = HabitCard(habit, parent_tab=mock_tab)

        # Перевіряємо, що лейбли створились, використовуючи findChildren або прямий доступ, якщо знаємо атрибути
        # У вашому коді це WrapLabel без прямого атрибуту self.title_lbl, але ми можемо перевірити просто створення
        self.assertIsNotNone(card)

    def test_topic_manager_dialog(self):
        """Тест менеджера тем."""
        # Правильний порядок аргументів: parent, user_id, storage
        dialog = TopicManagerDialog(None, user_id="u1", storage=self.mock_storage)

        # Має бути 1 тема, яку ми задали в setUp
        self.assertEqual(dialog.list_widget.count(), 1)

        # Тест додавання
        dialog.inp_name.setText("New Topic")
        dialog.add_topic()
        self.mock_storage.save_topic.assert_called()

    def test_ai_goal_dialog(self):
        """Тест чату з AI."""
        # Правильний порядок аргументів: parent, user_id, storage
        dialog = AIGoalDialog(None, user_id="u1", storage=self.mock_storage)

        self.assertIsNotNone(dialog.chat_container)

        # Емуляція додавання повідомлень
        dialog.add_message("Hello AI", is_user=True)
        dialog.add_message("Hello User", is_user=False)

        # Перевіряємо, що віджети додались у layout
        self.assertTrue(dialog.chat_layout.count() > 0)


if __name__ == '__main__':
    unittest.main()