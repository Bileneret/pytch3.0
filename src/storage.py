import sqlite3
import os
from .models import User, LearningGoal, GoalStatus, GoalPriority, Habit, SubGoal


class StorageService:
    def __init__(self, db_path="data/app.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, username TEXT, password_hash TEXT,
            total_completed_goals INTEGER, avatar_path TEXT, created_at TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY, user_id TEXT, title TEXT, description TEXT,
            deadline TEXT, priority TEXT, status TEXT, created_at TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS habits (
            id TEXT PRIMARY KEY, user_id TEXT, title TEXT, streak INTEGER, last_completed_date TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS subgoals (
            id TEXT PRIMARY KEY, goal_id TEXT, title TEXT, is_completed INTEGER, description TEXT
        )''')

        conn.commit()
        conn.close()

    # --- USER ---
    def get_user_by_username(self, username: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        return self._map_row_to_user(row)

    def get_user_by_id(self, user_id: str):
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
            user.total_completed_goals = row[3]
            user.avatar_path = row[4]
            return user
        return None

    def create_user(self, user: User):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)''',
                  (user.id, user.username, user.password_hash, user.total_completed_goals, user.avatar_path,
                   str(user.created_at)))
        conn.commit()
        conn.close()
        return user

    def update_user_stats(self, user_id, completed_goals):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE users SET total_completed_goals = ? WHERE id = ?", (completed_goals, user_id))
        conn.commit()
        conn.close()

    # --- GOALS ---
    def save_goal(self, goal: LearningGoal):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # INSERT OR REPLACE може змінювати rowid, тому сортування треба робити по created_at
        c.execute('''INSERT OR REPLACE INTO goals VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (goal.id, goal.user_id, goal.title, goal.description,
                   str(goal.deadline) if goal.deadline else None,
                   goal.priority.name, goal.status.name, str(goal.created_at)))
        conn.commit()
        conn.close()

    def get_goals(self, user_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Сортуємо по даті створення, щоб порядок був стабільним
        c.execute("SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = c.fetchall()
        conn.close()
        goals = []
        for r in rows:
            g = LearningGoal(title=r[2], description=r[3])
            g.id = r[0]
            g.user_id = r[1]
            g.deadline = r[4]
            if r[5] in GoalPriority.__members__: g.priority = GoalPriority[r[5]]
            if r[6] in GoalStatus.__members__: g.status = GoalStatus[r[6]]
            goals.append(g)
        return goals

    def delete_goal(self, goal_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        c.execute("DELETE FROM subgoals WHERE goal_id = ?", (goal_id,))
        conn.commit()
        conn.close()

    # --- HABITS ---
    def save_habit(self, habit: Habit):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO habits VALUES (?, ?, ?, ?, ?)''',
                  (habit.id, habit.user_id, habit.title, habit.streak, habit.last_completed_date))
        conn.commit()
        conn.close()

    def get_habits(self, user_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM habits WHERE user_id = ?", (user_id,))
        rows = c.fetchall()
        conn.close()
        habits = []
        for r in rows:
            h = Habit(title=r[2], user_id=r[1])
            h.id = r[0]
            h.streak = r[3]
            h.last_completed_date = r[4]
            habits.append(h)
        return habits

    # --- SUBGOALS ---
    def save_subgoal(self, subgoal: SubGoal):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO subgoals VALUES (?, ?, ?, ?, ?)''',
                  (subgoal.id, subgoal.goal_id, subgoal.title, 1 if subgoal.is_completed else 0, subgoal.description))
        conn.commit()
        conn.close()

    def get_subgoals(self, goal_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM subgoals WHERE goal_id = ?", (goal_id,))
        rows = c.fetchall()
        conn.close()
        subgoals = []
        for r in rows:
            s = SubGoal(title=r[2], goal_id=r[1])
            s.id = r[0]
            s.is_completed = bool(r[3])
            s.description = r[4] if len(r) > 4 else ""
            subgoals.append(s)
        return subgoals

    def delete_subgoal(self, subgoal_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM subgoals WHERE id = ?", (subgoal_id,))
        conn.commit()
        conn.close()