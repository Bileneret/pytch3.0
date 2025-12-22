import unittest
from datetime import datetime
from src.models import (
    User, LearningGoal, Habit, Course, SubGoal, Topic, Category,
    GoalStatus, GoalPriority, CourseType, CourseStatus
)


class TestModels(unittest.TestCase):
    def test_user_creation(self):
        """Перевірка створення користувача та генерації ID."""
        user = User(username="testuser", password_hash="hash123")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.total_completed_goals, 0)
        self.assertTrue(len(user.id) > 0)
        self.assertIsInstance(user.created_at, datetime)

    def test_category_creation(self):
        """Перевірка моделі Category."""
        cat = Category(name="Work", user_id="u1", color="#ffffff")
        self.assertEqual(cat.name, "Work")
        self.assertEqual(cat.user_id, "u1")
        self.assertTrue(len(cat.id) > 0)

    def test_topic_creation(self):
        """Перевірка моделі Topic."""
        topic = Topic(name="Python Dev", user_id="u1")
        self.assertEqual(topic.name, "Python Dev")
        self.assertTrue(len(topic.id) > 0)

    def test_goal_defaults(self):
        """Перевірка дефолтних статусів цілі."""
        goal = LearningGoal(title="Learn Python", user_id="u1")
        self.assertEqual(goal.status, GoalStatus.PLANNED)
        self.assertEqual(goal.priority, GoalPriority.MEDIUM)
        self.assertIsNone(goal.deadline)
        self.assertTrue(len(goal.id) > 0)

    def test_subgoal_defaults(self):
        """Перевірка створення підцілі."""
        sub = SubGoal(title="Install IDE", goal_id="g1")
        self.assertFalse(sub.is_completed)
        self.assertEqual(sub.goal_id, "g1")

    def test_habit_structure(self):
        """Перевірка структури звички."""
        habit = Habit(title="Gym", user_id="u1")
        self.assertEqual(habit.streak, 0)
        self.assertEqual(habit.last_completed_date, "")

    def test_course_logic(self):
        """Перевірка полів курсу та дефолтних значень."""
        course = Course(title="Math", user_id="u1", total_units=10)
        self.assertEqual(course.course_type, CourseType.COURSE)
        self.assertEqual(course.status, CourseStatus.IN_PROGRESS)
        self.assertEqual(course.completed_units, 0)

        # Перевірка зміни стану
        course.completed_units = 10
        course.status = CourseStatus.COMPLETED
        self.assertEqual(course.completed_units, 10)
        self.assertEqual(course.status, CourseStatus.COMPLETED)


if __name__ == '__main__':
    unittest.main()