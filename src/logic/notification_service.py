from apscheduler.schedulers.background import BackgroundScheduler
from plyer import notification
from datetime import datetime, timedelta
import os


class NotificationService:
    def __init__(self, storage, user_id):
        self.storage = storage
        self.user_id = user_id
        self.scheduler = BackgroundScheduler()
        self.notified_goals = set()

    def start(self):
        if not self.scheduler.running:
            self.scheduler.add_job(self.check_deadlines, 'interval', minutes=1)
            self.scheduler.start()

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

    def check_deadlines(self):
        goals = self.storage.get_goals(self.user_id)
        now = datetime.now()

        for g in goals:
            if not g.deadline or g.status.name == "COMPLETED":
                continue

            try:
                if len(g.deadline) == 10:
                    deadline_dt = datetime.strptime(g.deadline, "%Y-%m-%d")
                    deadline_dt = deadline_dt.replace(hour=9, minute=0)
                else:
                    deadline_dt = datetime.strptime(g.deadline, "%Y-%m-%d %H:%M")

                diff = deadline_dt - now

                # Якщо залишилось менше 10 хвилин (і ми ще не нагадували)
                if 0 < diff.total_seconds() <= 600:
                    if g.id not in self.notified_goals:
                        self.send_windows_notification(g.title)
                        self.notified_goals.add(g.id)

            except ValueError:
                continue

    def send_windows_notification(self, title):
        try:
            # Встановити кастомну іконку
            # icon_path = os.path.abspath("assets/icon.ico")

            notification.notify(
                title="Learning Goal Manager",  # 1) Повна назва
                message=f"Через 10 хвилин кінець дедлайну Вашої цілі: \"{title}\". Ви не забули про неї?",

                app_name="Learning Goal Manager",
                timeout=10
                # Примітка: plyer не підтримує додавання кнопок у повідомлення (action center).
                # Для цього потрібна компіляція в .exe або використання winrt, що ускладнить скрипт.
            )
        except Exception as e:
            print(f"Notification error: {e}")