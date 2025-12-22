import unittest
import os
import shutil
import sqlite3
import time
from datetime import date, timedelta
from src.storage import StorageService
from src.models import User, LearningGoal, Habit, SubGoal


class TestStorage(unittest.TestCase):
    def setUp(self):
        """Створюємо ізольовану БД."""
        self.test_dir = "tests/test_data_storage"
        self.test_db_path = os.path.join(self.test_dir, "test_app.db")
        os.makedirs(self.test_dir, exist_ok=True)

        self.storage = StorageService(db_path=self.test_db_path)
        self.user = User(username="tester", password_hash="123")
        self.storage.create_user(self.user)

    def tearDown(self):
        """Очищення ресурсів."""
        if hasattr(self.storage, 'close'):
            try:
                self.storage.close()
            except:
                pass

        if os.path.exists(self.test_dir):
            for i in range(5):
                try:
                    shutil.rmtree(self.test_dir)
                    break
                except PermissionError:
                    time.sleep(0.1)

    def test_create_and_get_goal(self):
        """Збереження та отримання цілі."""
        goal = LearningGoal(title="Integration Test", user_id=self.user.id)
        self.storage.save_goal(goal)
        goals = self.storage.get_goals(self.user.id)
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0].title, "Integration Test")

    def test_delete_goal(self):
        """Видалення цілі."""
        goal = LearningGoal(title="To Delete", user_id=self.user.id)
        self.storage.save_goal(goal)
        self.storage.delete_goal(goal.id)
        goals = self.storage.get_goals(self.user.id)
        self.assertEqual(len(goals), 0)

    def test_subgoal_lifecycle(self):
        """Робота з підцілями (CRUD)."""
        parent = LearningGoal(title="P", user_id=self.user.id)
        self.storage.save_goal(parent)

        sub = SubGoal(title="Sub 1", goal_id=parent.id)
        self.storage.save_subgoal(sub)

        subs = self.storage.get_subgoals(parent.id)
        self.assertEqual(len(subs), 1)

        subs[0].is_completed = True
        self.storage.save_subgoal(subs[0])
        updated = self.storage.get_subgoals(parent.id)[0]
        self.assertTrue(updated.is_completed)

    def test_habit_streak_logic(self):
        """Розрахунок серії звички (Time Travel)."""
        habit = Habit(title="Run", user_id=self.user.id)
        self.storage.save_habit(habit)

        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        # 1. Сьогодні
        self.storage.toggle_habit_date(habit.id, today)
        self.assertEqual(self.storage.get_habits(self.user.id)[0].streak, 1)

        # 2. Емуляція "Вчора"
        self.storage.toggle_habit_date(habit.id, today)  # Reset
        with sqlite3.connect(self.test_db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO habit_logs (habit_id, date) VALUES (?, ?)", (habit.id, yesterday))
            c.execute("UPDATE habits SET streak = 1, last_completed_date = ? WHERE id = ?", (yesterday, habit.id))
            conn.commit()

        # 3. Знову сьогодні -> Streak 2
        self.storage.toggle_habit_date(habit.id, today)
        self.assertEqual(self.storage.get_habits(self.user.id)[0].streak, 2)


if __name__ == '__main__':
    unittest.main()