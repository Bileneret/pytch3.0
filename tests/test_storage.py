import unittest
import os
import shutil
import sqlite3
import time  # Додали імпорт часу
from datetime import date, timedelta
from src.storage import StorageService
from src.models import User, LearningGoal, Habit, Course


class TestStorage(unittest.TestCase):
    def setUp(self):
        """Створюємо тимчасову БД для кожного тесту."""
        self.test_dir = "tests/test_data"
        self.test_db_path = os.path.join(self.test_dir, "test_app.db")

        # Створюємо папку, якщо немає
        os.makedirs(self.test_dir, exist_ok=True)

        self.storage = StorageService(db_path=self.test_db_path)
        self.user = User(username="tester", password_hash="123")
        self.storage.create_user(self.user)

    def tearDown(self):
        """Видаляємо БД після тестів з повторними спробами для Windows."""
        # 1. Закриваємо з'єднання в класі Storage
        if hasattr(self.storage, 'close'):
            try:
                self.storage.close()
            except:
                pass

        # 2. Видаляємо папку з механізмом повторних спроб (Retry Mechanism)
        if os.path.exists(self.test_dir):
            retries = 5
            for i in range(retries):
                try:
                    shutil.rmtree(self.test_dir)
                    break  # Якщо видалилось успішно — виходимо з циклу
                except PermissionError:
                    if i < retries - 1:
                        time.sleep(0.1)  # Чекаємо 100 мс і пробуємо знову
                    else:
                        print(f"⚠️ Warning: Не вдалося видалити {self.test_dir} після {retries} спроб.")

    def test_create_and_get_goal(self):
        goal = LearningGoal(title="Test Goal", user_id=self.user.id)
        self.storage.save_goal(goal)

        goals = self.storage.get_goals(self.user.id)
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0].title, "Test Goal")

    def test_delete_goal(self):
        goal = LearningGoal(title="To Delete", user_id=self.user.id)
        self.storage.save_goal(goal)
        self.storage.delete_goal(goal.id)

        goals = self.storage.get_goals(self.user.id)
        self.assertEqual(len(goals), 0)

    def test_habit_streak_logic(self):
        """Критичний тест: чи правильно рахується серія (streak)."""
        habit = Habit(title="Run", user_id=self.user.id)
        self.storage.save_habit(habit)
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        # 1. Відмічаємо сьогодні -> streak має стати 1
        self.storage.toggle_habit_date(habit.id, today)
        updated_habit = self.storage.get_habits(self.user.id)[0]
        self.assertEqual(updated_habit.streak, 1)

        # 2. Емуляція: "Ми виконали вчора"
        self.storage.toggle_habit_date(habit.id, today)  # Знімаємо "сьогодні"

        # Хакаємо базу, щоб записати вчорашній лог
        with sqlite3.connect(self.test_db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO habit_logs (habit_id, date) VALUES (?, ?)", (habit.id, yesterday))
            c.execute("UPDATE habits SET streak = 1, last_completed_date = ? WHERE id = ?", (yesterday, habit.id))
            conn.commit()

        # 3. Виконуємо знову СЬОГОДНІ
        self.storage.toggle_habit_date(habit.id, today)

        updated_habit_2 = self.storage.get_habits(self.user.id)[0]
        self.assertEqual(updated_habit_2.streak, 2)
        self.assertEqual(updated_habit_2.last_completed_date, today)


if __name__ == '__main__':
    unittest.main()