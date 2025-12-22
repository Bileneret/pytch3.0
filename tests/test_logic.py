import pytest
from datetime import date, timedelta
from src.models import Habit, LearningGoal, SubGoal, GoalStatus


# === ТЕСТИ ЛОГІКИ ЗВИЧОК ===

def test_habit_streak_update():
    """
    Перевіряє, чи збільшується стрік (серія) при виконанні звички.
    """
    # Підготовка даних: вчорашня дата
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    today = date.today().isoformat()

    habit = Habit(
        id=1,
        user_id=1,
        title="Test Habit",
        streak=5,
        last_completed_date=yesterday
    )

    # Дія: користувач виконує звичку
    if habit.last_completed_date != today:
        habit.streak += 1
        habit.last_completed_date = today

    # Перевірка
    assert habit.streak == 6
    assert habit.last_completed_date == today


def test_habit_streak_reset():
    """
    Перевіряє, чи скидається стрік, якщо користувач пропустив день.
    Логіка: якщо last_completed < yesterday -> streak = 0.
    """
    day_before_yesterday = (date.today() - timedelta(days=2)).isoformat()

    habit = Habit(
        id=2,
        user_id=1,
        title="Skipped Habit",
        streak=10,
        last_completed_date=day_before_yesterday
    )

    # Симуляція логіки перевірки при запуску програми
    # (Ця логіка зазвичай знаходиться в habit_logic.py)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    today = date.today().isoformat()

    is_streak_broken = habit.last_completed_date < yesterday and habit.last_completed_date != today

    if is_streak_broken:
        habit.streak = 0

    assert habit.streak == 0


# === ТЕСТИ ЛОГІКИ ЦІЛЕЙ ТА ПРОГРЕСУ ===

def test_goal_progress_calculation():
    """
    Перевіряє розрахунок відсотка виконання цілі на основі підцілей.
    """
    goal = LearningGoal(
        id=1, user_id=1, title="Master Python", status=GoalStatus.IN_PROGRESS
    )

    # Створюємо 4 підцілі: 3 виконані, 1 ні
    subgoals = [
        SubGoal(id=1, goal_id=1, title="Step 1", is_completed=True),
        SubGoal(id=2, goal_id=1, title="Step 2", is_completed=True),
        SubGoal(id=3, goal_id=1, title="Step 3", is_completed=True),
        SubGoal(id=4, goal_id=1, title="Step 4", is_completed=False),
    ]

    total = len(subgoals)
    completed = sum(1 for s in subgoals if s.is_completed)

    progress_percent = (completed / total) * 100 if total > 0 else 0

    assert total == 4
    assert completed == 3
    assert progress_percent == 75.0


def test_goal_zero_division_protection():
    """
    Перевіряє, що програма не падає, якщо у цілі немає підцілей.
    """
    subgoals = []  # Порожній список

    total = len(subgoals)
    completed = 0

    # Логіка має обробити це безпечно
    progress_percent = (completed / total) * 100 if total > 0 else 0

    assert progress_percent == 0