import unittest
from datetime import datetime
from src.models import User, LearningGoal, Habit, Course, GoalStatus, GoalPriority, CourseStatus, CourseType

class TestModels(unittest.TestCase):
    def test_user_creation(self):
        """Перевірка створення користувача з дефолтними параметрами."""
        user = User(username="testuser", password_hash="hash123")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.total_completed_goals, 0)
        self.assertTrue(len(user.id) > 0)

    def test_goal_defaults(self):
        """Перевірка дефолтних статусів цілі."""
        goal = LearningGoal(title="Learn Python", user_id="u1")
        self.assertEqual(goal.status, GoalStatus.PLANNED)
        self.assertEqual(goal.priority, GoalPriority.MEDIUM)
        self.assertIsNone(goal.deadline)

    def test_habit_structure(self):
        """Перевірка структури звички."""
        habit = Habit(title="Gym", user_id="u1")
        self.assertEqual(habit.streak, 0)
        self.assertEqual(habit.last_completed_date, "")

    def test_course_logic(self):
        """Перевірка полів курсу."""
        course = Course(title="Math", user_id="u1", total_units=10)
        self.assertEqual(course.course_type, CourseType.COURSE)
        self.assertEqual(course.completed_units, 0)
        # Симулюємо прогрес
        course.completed_units = 5
        self.assertEqual(course.completed_units, 5)

if __name__ == '__main__':
    unittest.main()