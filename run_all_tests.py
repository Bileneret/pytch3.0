import unittest
import sys
import os

def run_all_tests():
    # Додаємо поточну директорію в шлях, щоб тести бачили папку src
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    print("========================================")
    print("🚀 ЗАПУСК ПОВНОГО ТЕСТУВАННЯ LGM...")
    print("========================================\n")

    # Автоматичний пошук тестів у папці tests/
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')

    # Запуск
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ ВСІ ТЕСТИ ПРОЙШЛИ УСПІШНО!")
        sys.exit(0)
    else:
        print("\n❌ Є ПОМИЛКИ В ТЕСТАХ.")
        sys.exit(1)

if __name__ == '__main__':
    run_all_tests()