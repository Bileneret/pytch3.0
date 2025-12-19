import sqlite3
import os
from .models import User, LearningGoal, GoalStatus, GoalPriority


class StorageService:
    def __init__(self, db_path="data/app.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Таблиця користувачів (додано password_hash)
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT,
                password_hash TEXT,
                level INTEGER,
                current_xp INTEGER,
                xp_to_next_level INTEGER,
                total_completed_goals INTEGER,
                avatar_path TEXT,
                created_at TEXT
            )
        ''')

        # Таблиця цілей
        c.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                title TEXT,
                description TEXT,
                deadline TEXT,
                priority TEXT,
                status TEXT,
                created_at TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def get_user_by_username(self, username: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        return self._map_row_to_user(row)

    def get_user_by_id(self, user_id: str):
        """Отримання користувача по ID (важливо для MainWindow)."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return self._map_row_to_user(row)

    def _map_row_to_user(self, row):
        if row:
            user = User(username=row[1])
            user.id = row[0]
            user.password_hash = row[2]
            user.level = row[3]
            user.current_xp = row[4]
            user.xp_to_next_level = row[5]
            user.total_completed_goals = row[6]
            user.avatar_path = row[7]
            return user
        return None

    def create_user(self, user: User):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO users (id, username, password_hash, level, current_xp, xp_to_next_level, total_completed_goals, avatar_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user.id, user.username, user.password_hash, user.level, user.current_xp,
              user.xp_to_next_level, user.total_completed_goals, user.avatar_path, str(user.created_at)))
        conn.commit()
        conn.close()
        return user

    def update_user(self, user: User):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            UPDATE users SET level=?, current_xp=?, xp_to_next_level=?, total_completed_goals=?
            WHERE id=?
        ''', (user.level, user.current_xp, user.xp_to_next_level, user.total_completed_goals, user.id))
        conn.commit()
        conn.close()

    def save_goal(self, goal: LearningGoal):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO goals (id, user_id, title, description, deadline, priority, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (goal.id, goal.user_id, goal.title, goal.description,
              str(goal.deadline) if goal.deadline else None,
              goal.priority.name, goal.status.name, str(goal.created_at)))
        conn.commit()
        conn.close()

    def get_goals(self, user_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,))
        rows = c.fetchall()
        conn.close()

        goals = []
        for r in rows:
            g = LearningGoal(title=r[2], description=r[3])
            g.id = r[0]
            g.user_id = r[1]
            if r[5] in GoalPriority.__members__:
                g.priority = GoalPriority[r[5]]
            if r[6] in GoalStatus.__members__:
                g.status = GoalStatus[r[6]]
            goals.append(g)
        return goals