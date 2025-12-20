import hashlib
import random
import sqlite3
from datetime import datetime, timedelta
from src.storage import StorageService
# ДОДАНО нові моделі для імпорту
from src.models import (
    User, LearningGoal, GoalPriority, GoalStatus,
    SubGoal, Habit, Category,
    Topic, Course, CourseType, CourseStatus
)

# Списки слів
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
    db_path = "data/app.db"

    # Використовуємо storage тільки для початкових перевірок і створення юзера/категорій,
    # де немає конфлікту транзакцій.
    storage = StorageService(db_path)

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

    # 2. КАТЕГОРІЇ
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

    # 3. ЗВИЧКИ ТА ІСТОРІЯ (Один курсор для всього блоку)
    print(f"⚡ Генерація {len(HABITS_LIST)} звичок та історії виконань...")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    for title in HABITS_LIST:
        # Стрік
        streak = random.randint(0, 60)

        # Визначаємо останню дату
        r = random.random()
        if r < 0.5:
            days_ago = 0  # Сьогодні
        elif r < 0.8:
            days_ago = 1  # Вчора
        else:
            days_ago = random.randint(2, 10)  # Давно

        last_date_obj = datetime.now() - timedelta(days=days_ago)
        last_date_str = last_date_obj.strftime("%Y-%m-%d")

        # Створюємо об'єкт звички (щоб згенерувати ID)
        habit = Habit(
            title=title,
            user_id=user_id,
            streak=streak,
            last_completed_date=last_date_str
        )

        c.execute('''INSERT OR REPLACE INTO habits VALUES (?, ?, ?, ?, ?)''',
                  (habit.id, habit.user_id, habit.title, habit.streak, habit.last_completed_date))

        # ГЕНЕРАЦІЯ ІСТОРІЇ (ГАЛОЧОК)
        if streak > 0:
            for i in range(streak):
                log_date = last_date_obj - timedelta(days=i)
                log_date_str = log_date.strftime("%Y-%m-%d")

                c.execute("INSERT OR IGNORE INTO habit_logs (habit_id, date) VALUES (?, ?)",
                          (habit.id, log_date_str))

    conn.commit()  # Фіксуємо зміни звичок і логів
    conn.close()  # Закриваємо з'єднання перед наступним блоком

    # 4. ЦІЛІ
    print("🎯 Генерація 100 цілей...")
    priorities = list(GoalPriority)

    for i in range(100):
        title = f"{random.choice(VERBS)} {random.choice(NOUNS)}"
        if random.random() > 0.5:
            title += f" ({random.choice(CONTEXTS)})"

        desc = f"Це автоматично згенерована ціль №{i + 1}..."
        cat = random.choice(created_cats)
        priority = random.choices(priorities, weights=[20, 40, 30, 10], k=1)[0]

        days_offset = random.randint(-60, 90)
        deadline_date = datetime.now() + timedelta(days=days_offset)
        deadline_str = deadline_date.strftime("%Y-%m-%d")

        if days_offset < -5:
            status = random.choices([GoalStatus.MISSED, GoalStatus.COMPLETED], weights=[70, 30], k=1)[0]
        elif days_offset < 0:
            status = random.choices([GoalStatus.MISSED, GoalStatus.COMPLETED], weights=[40, 60], k=1)[0]
        else:
            status = random.choices([GoalStatus.PLANNED, GoalStatus.IN_PROGRESS], weights=[60, 40], k=1)[0]

        goal = LearningGoal(
            title=title,
            description=desc,
            deadline=deadline_str,
            priority=priority,
            status=status,
            user_id=user_id,
            category_id=cat.id
        )
        created_offset = random.randint(0, 30)
        goal.created_at = datetime.now() - timedelta(days=created_offset)

        storage.save_goal(goal)

        num_subs = random.randint(2, 6)
        force_done = (status == GoalStatus.COMPLETED)

        for j in range(num_subs):
            sub = SubGoal(
                title=f"Етап {j + 1}: {random.choice(VERBS)} частину",
                goal_id=goal.id,
                is_completed=True if force_done else random.choice([True, False])
            )
            storage.save_subgoal(sub)

    # 5. РОЗВИТОК (DEVELOPMENT)
    print("🚀 Генерація 25 матеріалів для Розвитку...")

    # Нестандартні теми
    custom_topics_names = [
        "GameDev 🎮", "Data Science 📊", "Digital Art 🎨",
        "Crypto 🪙", "Psychology 🧠", "Music 🎸", "Biohacking 🧬"
    ]

    db_topics = []
    # Створюємо теми в БД
    for t_name in custom_topics_names:
        t = Topic(name=t_name, user_id=user_id)
        storage.save_topic(t)
        db_topics.append(t)

    # Шаблони назв
    dev_prefixes = ["Основи", "Просунутий курс", "Майстер-клас", "Книга по", "Проект:", "Лекція:"]
    dev_suffixes = ["для новачків", "PRO", "2025", "за 30 днів", "Part 1", "Ultimate Guide"]

    for i in range(25):
        topic = random.choice(db_topics)

        # Генеруємо назву: "Основи GameDev для новачків"
        # Беремо перше слово з теми (наприклад 'GameDev' з 'GameDev 🎮') для чистоти назви
        topic_clean_word = topic.name.split()[0]
        title = f"{random.choice(dev_prefixes)} {topic_clean_word} {random.choice(dev_suffixes)}"

        # Тип (Курс, Книга, Челендж...)
        c_type = random.choice(list(CourseType))

        # Загальний обсяг (сторінок, уроків, відсотків)
        if c_type == CourseType.BOOK:
            total = random.randint(200, 800)
        elif c_type == CourseType.PROJECT:
            total = 100
        else:
            total = random.randint(10, 100)

        # Прогрес (скільки зроблено)
        # 10% шанс, що тільки почали (0), 10% що закінчили, 80% - випадкове число
        rand_factor = random.random()
        if rand_factor < 0.1:
            completed = 0
        elif rand_factor > 0.9:
            completed = total
        else:
            completed = random.randint(0, total)

        # Визначаємо статус на основі прогресу
        if completed == 0:
            status = CourseStatus.PLANNED
        elif completed == total:
            status = CourseStatus.COMPLETED
        else:
            status = CourseStatus.IN_PROGRESS

        course = Course(
            title=title,
            user_id=user_id,
            topic_id=topic.id,
            course_type=c_type,
            total_units=total,
            completed_units=completed,
            status=status,
            description=f"Автоматично згенерований матеріал №{i + 1}"
        )

        # Трохи розкидаємо дати створення
        course.created_at = datetime.now() - timedelta(days=random.randint(0, 60))

        storage.save_course(course)

    print("✅ Успішно! База даних заповнена з історією звичок, цілями та розвитком.")
    print(f"   Користувач: {username} / 123123")


if __name__ == "__main__":
    seed_data()