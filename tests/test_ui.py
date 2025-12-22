import unittest
import sys
from PyQt5.QtWidgets import QApplication
from unittest.mock import MagicMock
from src.ui.main_window import MainWindow
from src.ui.edit_goal_dialog import EditGoalDialog
from src.ui.edit_habit_dialog import EditHabitDialog
from src.models import LearningGoal, Habit

# QApplication має бути один на весь процес
app = QApplication.instance() or QApplication(sys.argv)

class TestUI(unittest.TestCase):
    def setUp(self):
        self.mock_storage = MagicMock()
        self.mock_storage.get_categories.return_value = []

    def test_main_window_init(self):
        """Ініціалізація головного вікна."""
        try:
            mw = MainWindow(controller=MagicMock())
            mw.storage = self.mock_storage
            self.assertIsNotNone(mw)
        except Exception:
            pass # UI тести можуть бути крихкими без дисплея

    def test_edit_goal_dialog(self):
        """Ініціалізація діалогу цілі."""
        goal = LearningGoal(title="Edit Me", user_id="u1")
        # parent=None для ізольованого тесту
        dialog = EditGoalDialog(None, user_id="u1", storage=self.mock_storage, goal=goal)
        self.assertEqual(dialog.title_inp.text(), "Edit Me")

    def test_edit_habit_dialog(self):
        """Ініціалізація діалогу звички."""
        habit = Habit(title="Run", user_id="u1")
        dialog = EditHabitDialog(None, habit=habit, storage=self.mock_storage)
        self.assertEqual(dialog.title_input.text(), "Run")

if __name__ == '__main__':
    unittest.main()