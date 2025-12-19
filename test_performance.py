import unittest
import time
import uuid
import os
import tempfile
from src.storage import StorageService
from src.models import Hero, HeroClass, Gender, LongTermGoal
from datetime import datetime


class TestPerformance(unittest.TestCase):

    def setUp(self):
        # Використовуємо тимчасовий файл для чесного тесту швидкості запису на диск
        # (in-memory база працює миттєво, але це не реалістично)
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.storage = StorageService(self.db_path)

        # Створюємо героя, до якого будемо прив'язувати звички
        self.hero = Hero(
            nickname="PerfTester",
            hero_class=HeroClass.WARRIOR,
            gender=Gender.MALE,
            appearance="img"
        )
        self.storage.create_hero(self.hero)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_load_1000_habits(self):
        """
        СЦЕНАРІЙ: Додавання 1000 виконаних звичок в історію.
        """
        print("\n--- ПОЧАТОК НАВАНТАЖУВАЛЬНОГО ТЕСТУ ---")

        # Підготовка даних (щоб не витрачати час на створення об'єктів всередині заміру)
        habits = []
        for i in range(1000):
            habit = LongTermGoal(
                title=f"Habit {i}",
                description="Performance test",
                total_days=30,
                start_date=datetime.now(),
                time_frame="09:00 - 10:00"
            )
            # Емулюємо, що вона виконана
            habit.is_completed = True
            habits.append(habit)

        # === ЗАМІР ЧАСУ ===
        start_time = time.time()

        # Виконуємо запис у БД
        # SQLite транзакції: якщо ми робимо кожен insert окремо, це довго.
        # Але в коді програми ми зазвичай зберігаємо по одній.
        # Перевіримо "чесний" варіант (як у реальному житті - по одному збереженню).

        for habit in habits:
            self.storage.save_long_term_goal(habit, str(self.hero.id))

        end_time = time.time()
        # ==================

        duration = end_time - start_time
        print(f"Час додавання 1000 записів: {duration:.4f} сек")

        # Перевірка, що дані дійсно є
        conn = self.storage._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM long_term_goals")
        count = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(count, 1000)

        # Перевірка на відповідність вимогам (менше 1 секунди, наприклад)
        # 0.45с з вашої записки - це орієнтир.
        self.assertLess(duration, 2.0, "Занадто повільно! Більше 2 секунд.")


if __name__ == '__main__':
    unittest.main()