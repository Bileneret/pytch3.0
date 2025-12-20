import hashlib
import random
from datetime import datetime, timedelta
from src.storage import StorageService
from src.models import User, LearningGoal, GoalPriority, GoalStatus, SubGoal, Habit, Category

# Списки слів для генерації назв цілей
VERBS = [
    "Вивчити", "Зробити", "Написати", "Купити", "Відвідати", "Завершити",
    "Підготувати", "Організувати", "Прочитати", "Переробити", "Проаналізувати",
    "Створити", "Запустити", "Протестувати", "Оптимізувати"
]

NOUNS = [
    "звіт", "проект", "курс Python", "статтю", "подарунок", "презентацію",
    "документи", "квартиру", "сайт", "модуль", "дизайн",
    "бюджет", "резюме", "портфоліо", "план тренувань"
]

CONTEXTS = [
    "для роботи", "до дедлайну", "для замовника", "на вихідних",
    "терміново", "для душі", "для саморозвитку", "разом з другом",
    "для підвищення", "на завтра", "для курсової"
]

# Список звичок
HABITS_LIST = [
    "Пити воду (2л)", "Зарядка вранці", "Читання 30 хв", "Медитація",
    "Коміт на GitHub", "Англійська (Duolingo)", "Не їсти цукор", "Лягати до 23:00",
    "Планування дня", "Прогулянка 5км", "Вітаміни", "Прибирання столу",
    "Дзвінок батькам", "Облік фінансів", "Без соцмереж перед сном"
]


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def seed_data():
    print("🌱 Починаємо ГЕНЕРАЦІЮ великого обсягу даних...")

    # Ініціалізація стореджа (шлях може відрізнятись залежно від того, звідки запускаєте)
    storage = StorageService("data/app.db")

    # 1. КОРИСТУВАЧ
    username = "tester"
    pass_hash = hash_password("123123")

    user = storage.get_user_by_username(username)
    if not user:
        print(f"👤 Створення користувача {username}...")
        user = User(username=username, password_hash=pass_hash)
        storage.create_user(user)
    else:
        print(f"👤 Користувач {username} знайдений.")

    user_id = user.id

    # 2. КАТЕГОРІЇ (8 штук)
    print("🗂️ Створення категорій...")
    categories_data = [
        ("Робота", "#3b82f6"),  # Blue
        ("Здоров'я", "#ef4444"),  # Red
        ("Навчання", "#10b981"),  # Green
        ("Фінанси", "#f59e0b"),  # Orange
        ("Подорожі", "#8b5cf6"),  # Purple
        ("Хобі", "#ec4899"),  # Pink
        ("IT & Code", "#6366f1"),  # Indigo
        ("Побут", "#64748b")  # Slate
    ]

    created_cats = []
    for name, color in categories_data:
        cat = Category(name=name, color=color, user_id=user_id)
        storage.save_category(cat)
        created_cats.append(cat)

    # 3. ЗВИЧКИ (15 штук)
    print(f"⚡ Генерація {len(HABITS_LIST)} звичок...")
    for title in HABITS_LIST:
        # Випадковий стрік від 0 до 60
        streak = random.randint(0, 60)

        # Визначаємо дату останнього виконання
        # 40% що сьогодні, 30% вчора, 30% давно (стрік міг бути перерваний, але для спрощення запишемо дату)
        r = random.random()
        if r < 0.4:
            days_ago = 0
        elif r < 0.7:
            days_ago = 1
        else:
            days_ago = random.randint(2, 10)

        last_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        habit = Habit(
            title=title,
            user_id=user_id,
            streak=streak,
            last_completed_date=last_date
        )
        storage.save_habit(habit)

    # 4. ЦІЛІ (100 штук)
    print("🎯 Генерація 100 цілей з підцілями...")

    priorities = list(GoalPriority)

    for i in range(100):
        # Генерація назви
        title = f"{random.choice(VERBS)} {random.choice(NOUNS)}"
        if random.random() > 0.5:
            title += f" ({random.choice(CONTEXTS)})"

        # Опис (Lorem Ipsum style)
        desc = f"Це автоматично згенерована ціль №{i + 1}. Тут має бути детальний опис завдання, " \
               f"яке необхідно виконати для досягнення успіху в категорії."

        # Категорія
        cat = random.choice(created_cats)

        # Пріоритет (зважений рандом: середніх більше)
        priority = random.choices(priorities, weights=[20, 40, 30, 10], k=1)[0]

        # Дедлайн: розкид від -60 днів до +90 днів (для гарного графіка)
        days_offset = random.randint(-60, 90)
        deadline_date = datetime.now() + timedelta(days=days_offset)
        deadline_str = deadline_date.strftime("%Y-%m-%d")

        # Статус (Логіка залежить від дедлайну)
        if days_offset < -5:
            # Якщо дедлайн давно пройшов
            status = random.choices(
                [GoalStatus.MISSED, GoalStatus.COMPLETED, GoalStatus.IN_PROGRESS],
                weights=[60, 30, 10], k=1
            )[0]
        elif days_offset < 0:
            # Якщо пройшов недавно
            status = random.choice([GoalStatus.MISSED, GoalStatus.COMPLETED])
        else:
            # Якщо дедлайн у майбутньому
            status = random.choices(
                [GoalStatus.PLANNED, GoalStatus.IN_PROGRESS, GoalStatus.COMPLETED],
                weights=[50, 40, 10], k=1
            )[0]

        # Створення цілі
        goal = LearningGoal(
            title=title,
            description=desc,
            deadline=deadline_str,
            priority=priority,
            status=status,
            user_id=user_id,
            category_id=cat.id
        )
        storage.save_goal(goal)

        # 5. ПІДЦІЛІ (2-6 штук для кожної цілі)
        num_subs = random.randint(2, 6)
        completed_count = 0

        # Якщо ціль виконана - всі підцілі виконані
        if status == GoalStatus.COMPLETED:
            force_all_done = True
        # Якщо запланована - нічого не виконано (зазвичай)
        elif status == GoalStatus.PLANNED:
            force_all_done = False
            force_none_done = True
        else:
            force_all_done = False
            force_none_done = False

        for j in range(num_subs):
            sub_title = f"Етап {j + 1}: {random.choice(VERBS)} частину {j + 1}"

            is_done = False
            if force_all_done:
                is_done = True
            elif not force_none_done:
                # В процесі або прострочено - рандом
                is_done = random.choice([True, False])

            sub = SubGoal(
                title=sub_title,
                goal_id=goal.id,
                is_completed=is_done
            )
            storage.save_subgoal(sub)

    print("✅ Успішно! База даних заповнена.")
    print(f"   Користувач: {username}")
    print(f"   Пароль: 123123")
    print("🚀 Тепер запустіть main.py")


if __name__ == "__main__":
    seed_data()