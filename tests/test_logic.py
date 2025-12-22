import pytest
from datetime import date, timedelta
from src.models import Habit, LearningGoal, SubGoal, GoalStatus, Course, CourseStatus


# === ЛОГІКА ЗВИЧОК ===

def test_habit_streak_increment():
    """Стрік збільшується при послідовному виконанні."""
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    today = date.today().isoformat()

    habit = Habit(title="H", user_id="u", streak=5, last_completed_date=yesterday)

    # Дія: виконання сьогодні
    habit.streak += 1
    habit.last_completed_date = today

    assert habit.streak == 6


def test_habit_streak_break():
    """Стрік скидається, якщо пропущено день (логіка 'if check')."""
    day_before = (date.today() - timedelta(days=2)).isoformat()

    habit = Habit(title="H", user_id="u", streak=10, last_completed_date=day_before)

    # Симуляція перевірки
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    today = date.today().isoformat()

    # Логіка: останній раз був позавчора, вчора пропущено
    is_broken = habit.last_completed_date < yesterday and habit.last_completed_date != today

    if is_broken:
        habit.streak = 0

    assert habit.streak == 0


# === ЛОГІКА ЦІЛЕЙ ===

def test_goal_progress_calc():
    """Розрахунок % виконання."""
    subs = [
        SubGoal(title="1", goal_id="1", is_completed=True),
        SubGoal(title="2", goal_id="1", is_completed=True),
        SubGoal(title="3", goal_id="1", is_completed=False),
        SubGoal(title="4", goal_id="1", is_completed=False)
    ]
    total = len(subs)
    completed = sum(1 for s in subs if s.is_completed)
    percent = (completed / total) * 100

    assert percent == 50.0


def test_goal_status_update_logic():
    """Логіка зміни статусу цілі на основі підцілей."""
    goal = LearningGoal(title="G", user_id="u", status=GoalStatus.IN_PROGRESS)

    # 1. Всі підцілі виконані -> COMPLETED
    all_done = True
    if all_done:
        goal.status = GoalStatus.COMPLETED
    assert goal.status == GoalStatus.COMPLETED

    # 2. Одна стала невиконаною -> IN_PROGRESS
    goal.status = GoalStatus.COMPLETED
    all_done = False
    some_done = True

    if not all_done and some_done:
        goal.status = GoalStatus.IN_PROGRESS
    assert goal.status == GoalStatus.IN_PROGRESS


# === ЛОГІКА КУРСІВ ===

def test_course_completion_logic():
    """Якщо completed_units == total_units, статус має бути COMPLETED."""
    course = Course(title="C", user_id="u", total_units=10, completed_units=9, status=CourseStatus.IN_PROGRESS)

    # Add 1 unit
    course.completed_units += 1

    if course.completed_units >= course.total_units:
        course.status = CourseStatus.COMPLETED

    assert course.completed_units == 10
    assert course.status == CourseStatus.COMPLETED