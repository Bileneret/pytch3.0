import google.generativeai as genai
import json
import re
from datetime import datetime
from src.config import Config
from src.models import GoalPriority


class AIService:
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            print("Warning: API Key not found. AI features might fail.")
            pass

        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            # 5. Використовуємо gemini-2.5-flash
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception as e:
            print(f"Failed to configure AI: {e}")

    def generate_subgoals(self, goal_title: str, goal_desc: str, difficulty_str: str) -> list:
        """Метод для генерації тільки підцілей (одноразовий)."""
        # Адаптація діапазонів
        if difficulty_str == GoalPriority.LOW.value:
            count_range = "2-3"
        elif difficulty_str == GoalPriority.MEDIUM.value:
            count_range = "3-5"
        elif difficulty_str == GoalPriority.HIGH.value:
            count_range = "5-7"
        elif difficulty_str == GoalPriority.CRITICAL.value:
            count_range = "8-10"
        else:
            count_range = "3-5"

        prompt = f"""
        Ти - коуч-помічник.
        Ціль: "{goal_title}". Опис: "{goal_desc}". Складність: {difficulty_str}.

        Завдання: Згенерувати список із {count_range} кроків.
        Відповідь - ТІЛЬКИ JSON масив:
        [
            {{"title": "Назва кроку", "description": "Деталі"}}
        ]
        """
        try:
            response = self.model.generate_content(prompt)
            json_str = self._extract_json_string(response.text)
            return json.loads(json_str) if json_str else []
        except Exception as e:
            print(f"AI Error: {e}")
            return []

    def start_chat(self):
        """Починає чат-сесію."""

        # Інструкція завжди додавати json та базовий промт для ШІ, якщо є пропозиція плану.
        system_instruction = """
        Ти - помічник у "Learning Goals Manager". Твоя мета - допомогти створити ціль з планом.
        Спілкуйся українською мовою. Стиль: дружній, мотивуючий.

        АЛГОРИТМ РОБОТИ:
        1. Якщо користувач просто вітається або пише щось неясно -> розпитай деталі.
        2. Якщо користувач назвав тему -> запропонуй план дій.

        ВИМОГИ ДО ПЛАНУ (Важливо!):
        - НІЯКИХ "Тиждень 1", "Тиждень 2".
        - НІЯКИХ Markdown форматувань тексту: "**Назва**", "```Code```".
        - Використовуй тільки плоский список: "День 1", "День 2", "День 3" і т.д.
        - Якщо ціль складна або довга -> обов'язково додай "День відпочинку" (Вихідний).

        ТЕХНІЧНА ВИМОГА (КРИТИЧНО ВАЖЛИВО):
        Якщо ти пропонуєш конкретний план/ціль, ти ПОВИНЕН в кінці повідомлення додати блок JSON.
        Саме цей JSON дозволяє програмі створити кнопку "Додати ціль". Без нього кнопка не з'явиться.

        Формат JSON:
        ```json
        {
            "title": "Назва цілі",
            "description": "Опис цілі",
            "difficulty": "MEDIUM",  // LOW, MEDIUM, HIGH, CRITICAL
            "deadline_days": 7,
            "subgoals": [
                {"title": "День 1: Теорія", "description": "Почитати документацію"},
                {"title": "День 2: Практика", "description": "Написати код"},
                {"title": "День 3: Вихідний", "description": "Відпочинок"}
            ]
        }
        ```
        Не додавай JSON, якщо ти просто задаєш уточнюючі питання. Додавай його тільки коли пропонуєш конкретний план.
        """

        chat = self.model.start_chat(history=[
            {"role": "user", "parts": [system_instruction]},
            {"role": "model", "parts": ["Зрозумів. Я готовий. Чекаю на ввід користувача."]}
        ])
        return chat

    def send_to_chat(self, chat, message: str) -> tuple[str, dict]:
        try:
            response = chat.send_message(message)
            text = response.text.strip()

            json_data = None
            # Шукаємо json
            if "```json" in text or text.strip().startswith("{"):
                json_str = self._extract_json_string(text)
                if json_str:
                    try:
                        json_data = json.loads(json_str)
                    except:
                        pass

            # Чистимо текст від json для користувача, щоб не дублювати
            clean_text = re.sub(r"```json\s*.*?\s*```", "", text, flags=re.DOTALL).strip()
            if not clean_text: clean_text = text  # Якщо раптом все вирізали

            return clean_text, json_data

        except Exception as e:
            return f"Error: {str(e)}", None

    def _extract_json_string(self, text):
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match: return match.group(1)
        if text.strip().startswith("{") and text.strip().endswith("}"): return text.strip()
        if text.strip().startswith("[") and text.strip().endswith("]"): return text.strip()
        return None