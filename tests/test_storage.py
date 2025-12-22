import unittest
import os
import shutil
import sqlite3
import time
from datetime import date, timedelta
from src.storage import StorageService
from src.models import User, LearningGoal, Habit, SubGoal, Category, Topic, Course, CourseType


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
                # Закриваємо з'єднання, якщо воно відкрите (хоча StorageService відкриває/закриває на льоту)
                pass
            except:
                pass

        if os.path.exists(self.test_dir):
            for i in range(5):
                try:
                    shutil.rmtree(self.test_dir)
                    break
                except PermissionError:
                    time.sleep(0.1)

    # --- USER STATS ---
    def test_update_user_stats(self):
        self.storage.update_user_stats(self.user.id, 5)
        updated_user = self.storage.get_user_by_id(self.user.id)
        self.assertEqual(updated_user.total_completed_goals, 5)

    # --- CATEGORIES ---
    def test_category_crud(self):
        cat = Category(name="Work", user_id=self.user.id, color="#000000")
        self.storage.save_category(cat)

        cats = self.storage.get_categories(self.user.id)
        self.assertEqual(len(cats), 1)
        self.assertEqual(cats[0].name, "Work")

        self.storage.delete_category(cat.id)
        cats_after = self.storage.get_categories(self.user.id)
        self.assertEqual(len(cats_after), 0)

    # --- TOPICS ---
    def test_topic_crud(self):
        topic = Topic(name="Science", user_id=self.user.id)
        self.storage.save_topic(topic)

        topics = self.storage.get_topics(self.user.id)
        # StorageService створює дефолтні теми, якщо список порожній.
        # Перевіримо, чи є наша тема в списку.
        names = [t.name for t in topics]
        self.assertIn("Science", names)

        self.storage.delete_topic(topic.id)
        topics_after = self.storage.get_topics(self.user.id)
        names_after = [t.name for t in topics_after]
        self.assertNotIn("Science", names_after)

    # --- COURSES ---
    def test_course_crud(self):
        course = Course(title="PyBook", user_id=self.user.id, course_type=CourseType.BOOK)
        self.storage.save_course(course)

        courses = self.storage.get_courses(self.user.id)
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0].title, "PyBook")

        self.storage.delete_course(course.id)
        courses_after = self.storage.get_courses(self.user.id)
        self.assertEqual(len(courses_after), 0)

    # --- GOALS & SUBGOALS ---
    def test_goal_lifecycle(self):
        goal = LearningGoal(title="Integration Test", user_id=self.user.id)
        self.storage.save_goal(goal)

        # Update
        goal.title = "Updated Title"
        self.storage.save_goal(goal)
        fetched = self.storage.get_goals(self.user.id)[0]
        self.assertEqual(fetched.title, "Updated Title")

        # Delete
        self.storage.delete_goal(goal.id)
        self.assertEqual(len(self.storage.get_goals(self.user.id)), 0)

    def test_subgoal_lifecycle(self):
        parent = LearningGoal(title="P", user_id=self.user.id)
        self.storage.save_goal(parent)

        sub = SubGoal(title="Sub 1", goal_id=parent.id)
        self.storage.save_subgoal(sub)

        subs = self.storage.get_subgoals(parent.id)
        self.assertEqual(len(subs), 1)

        # Update status
        subs[0].is_completed = True
        self.storage.save_subgoal(subs[0])
        updated = self.storage.get_subgoals(parent.id)[0]
        self.assertTrue(updated.is_completed)

        # Delete
        self.storage.delete_subgoal(sub.id)
        self.assertEqual(len(self.storage.get_subgoals(parent.id)), 0)

    # --- HABITS & STREAKS ---
    def test_habit_streak_logic(self):
        habit = Habit(title="Run", user_id=self.user.id)
        self.storage.save_habit(habit)

        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        # 1. Сьогодні
        self.storage.toggle_habit_date(habit.id, today)
        self.assertEqual(self.storage.get_habits(self.user.id)[0].streak, 1)

        # 2. Емуляція "Вчора" через прямий запис у базу, бо toggle працює з поточною датою логічно
        self.storage.toggle_habit_date(habit.id, today)  # знімаємо сьогодні

        with sqlite3.connect(self.test_db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO habit_logs (habit_id, date) VALUES (?, ?)", (habit.id, yesterday))
            conn.commit()
            # Перерахунок стріка викликається в toggle, тому викличемо його штучно
            self.storage._recalc_streak(c, habit.id)

        h_after = self.storage.get_habits(self.user.id)[0]
        # Має бути 1, бо вчора виконано
        self.assertEqual(h_after.streak, 1)

        # 3. Додаємо сьогодні -> Streak має стати 2
        self.storage.toggle_habit_date(habit.id, today)
        self.assertEqual(self.storage.get_habits(self.user.id)[0].streak, 2)

    # --- IMPORT / EXPORT ---
    def test_import_export(self):
        # Create some data
        cat = Category(name="ImpExp", user_id=self.user.id)
        self.storage.save_category(cat)

        # Export
        data = self.storage.export_user_data(self.user.id)
        self.assertIn("categories", data)
        self.assertEqual(data["categories"][0]["name"], "ImpExp")

        # Import to new user
        new_user = User(username="newbie", password_hash="111")
        self.storage.create_user(new_user)

        self.storage.import_user_data(data, new_user.id)

        cats_new = self.storage.get_categories(new_user.id)
        self.assertEqual(len(cats_new), 1)
        self.assertEqual(cats_new[0].name, "ImpExp")
        self.assertEqual(cats_new[0].user_id, new_user.id)  # ID має змінитись на нового юзера


if __name__ == '__main__':
    unittest.main()