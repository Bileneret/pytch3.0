import sqlite3
import os
from datetime import datetime, date, timedelta
from .models import User, LearningGoal, GoalStatus, GoalPriority, Habit, SubGoal, Category, Course, CourseType, \
    CourseStatus


class StorageService:
    def __init__(self, db_path="data/app.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Ініціалізація бази даних та створення таблиць."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # ... (Users, Categories - без змін)
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, username TEXT, password_hash TEXT,
            total_completed_goals INTEGER, avatar_path TEXT, created_at TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY, user_id TEXT, name TEXT, color TEXT
        )''')

        # 3. GOALS (ОНОВЛЕНО: додано link)
        c.execute('''CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY, user_id TEXT, title TEXT, description TEXT,
            deadline TEXT, priority TEXT, status TEXT, created_at TEXT, category_id TEXT, link TEXT
        )''')

        # Міграції
        try:
            c.execute("ALTER TABLE goals ADD COLUMN category_id TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            c.execute("ALTER TABLE goals ADD COLUMN link TEXT")
        except sqlite3.OperationalError:
            pass

            # ... (Subgoals, Habits, HabitLogs, Courses - без змін)
        c.execute('''CREATE TABLE IF NOT EXISTS subgoals (
            id TEXT PRIMARY KEY, goal_id TEXT, title TEXT, is_completed INTEGER, description TEXT, created_at TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS habits (
            id TEXT PRIMARY KEY, user_id TEXT, title TEXT, streak INTEGER, last_completed_date TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS habit_logs (
            habit_id TEXT, date TEXT,
            PRIMARY KEY (habit_id, date)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY, user_id TEXT, title TEXT, type TEXT, 
            status TEXT, total_units INTEGER, completed_units INTEGER, 
            link TEXT, description TEXT, created_at TEXT
        )''')

        conn.commit()
        conn.close()

    # ... (User, Category methods - без змін) ...
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

    def save_category(self, category: Category):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO categories VALUES (?, ?, ?, ?)''',
                  (category.id, category.user_id, category.name, category.color))
        conn.commit()
        conn.close()

    def get_categories(self, user_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM categories WHERE user_id = ?", (user_id,))
        rows = c.fetchall()
        conn.close()
        cats = []
        for r in rows:
            cats.append(Category(id=r[0], user_id=r[1], name=r[2], color=r[3]))
        return cats

    def delete_category(self, cat_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        c.execute("UPDATE goals SET category_id = NULL WHERE category_id = ?", (cat_id,))
        conn.commit()
        conn.close()

    # ==========================
    # GOAL METHODS (ОНОВЛЕНО)
    # ==========================
    def save_goal(self, goal: LearningGoal):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT 1 FROM goals WHERE id = ?", (goal.id,))
        exists = c.fetchone()

        deadline_str = str(goal.deadline) if goal.deadline else None

        if exists:
            c.execute(
                '''UPDATE goals SET title=?, description=?, deadline=?, priority=?, status=?, category_id=?, link=? WHERE id=?''',
                (goal.title, goal.description, deadline_str,
                 goal.priority.name, goal.status.name, goal.category_id, goal.link, goal.id))
        else:
            c.execute('''INSERT INTO goals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (goal.id, goal.user_id, goal.title, goal.description,
                       deadline_str, goal.priority.name, goal.status.name,
                       str(goal.created_at), goal.category_id, goal.link))
        conn.commit()
        conn.close()

    def get_goals(self, user_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
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
            # r[7] created_at
            if len(r) > 8: g.category_id = r[8]
            if len(r) > 9: g.link = r[9] if r[9] else ""

            if r[7]:
                try:
                    g.created_at = datetime.fromisoformat(r[7])
                except:
                    pass
            goals.append(g)
        return goals

    def delete_goal(self, goal_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        c.execute("DELETE FROM subgoals WHERE goal_id = ?", (goal_id,))
        conn.commit()
        conn.close()

    # ==========================
    # HABIT METHODS
    # ==========================
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

    def delete_habit(self, habit_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        c.execute("DELETE FROM habit_logs WHERE habit_id = ?", (habit_id,))
        conn.commit()
        conn.close()

    def toggle_habit_date(self, habit_id: str, date_str: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("SELECT 1 FROM habit_logs WHERE habit_id = ? AND date = ?", (habit_id, date_str))
        exists = c.fetchone()

        is_completed = False
        if exists:
            c.execute("DELETE FROM habit_logs WHERE habit_id = ? AND date = ?", (habit_id, date_str))
        else:
            c.execute("INSERT INTO habit_logs VALUES (?, ?)", (habit_id, date_str))
            is_completed = True

        conn.commit()
        self._recalc_streak(c, habit_id)
        conn.close()
        return is_completed

    def get_habit_logs(self, habit_id: str, start_date: str, end_date: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT date FROM habit_logs WHERE habit_id = ? AND date BETWEEN ? AND ?",
                  (habit_id, start_date, end_date))
        rows = c.fetchall()
        conn.close()
        return {r[0] for r in rows}

    def _recalc_streak(self, cursor, habit_id):
        cursor.execute("SELECT date FROM habit_logs WHERE habit_id = ? ORDER BY date DESC", (habit_id,))
        rows = cursor.fetchall()

        dates = [datetime.strptime(r[0], "%Y-%m-%d").date() for r in rows]

        if not dates:
            streak = 0
            last_date = ""
        else:
            today = date.today()
            streak = 0
            if dates[0] < today - timedelta(days=1):
                streak = 0
            else:
                current_check = dates[0]
                streak = 1
                for i in range(1, len(dates)):
                    if dates[i] == current_check - timedelta(days=1):
                        streak += 1
                        current_check = dates[i]
                    else:
                        break
            last_date = dates[0].isoformat()

        cursor.execute("UPDATE habits SET streak = ?, last_completed_date = ? WHERE id = ?",
                       (streak, last_date, habit_id))
        cursor.connection.commit()

    # ==========================
    # SUBGOAL METHODS
    # ==========================
    def save_subgoal(self, subgoal: SubGoal):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO subgoals VALUES (?, ?, ?, ?, ?, ?)''',
                  (subgoal.id, subgoal.goal_id, subgoal.title,
                   1 if subgoal.is_completed else 0,
                   subgoal.description,
                   str(subgoal.created_at)))
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
            if len(r) > 5 and r[5]:
                try:
                    s.created_at = datetime.fromisoformat(r[5])
                except:
                    pass
            subgoals.append(s)

        subgoals.sort(key=lambda x: (x.is_completed, x.created_at))
        return subgoals

    def delete_subgoal(self, subgoal_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM subgoals WHERE id = ?", (subgoal_id,))
        conn.commit()
        conn.close()

    # ==========================
    # COURSE METHODS (НОВІ)
    # ==========================
    def save_course(self, course: Course):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (course.id, course.user_id, course.title,
                   course.course_type.name, course.status.name,
                   course.total_units, course.completed_units,
                   course.link, course.description, str(course.created_at)))
        conn.commit()
        conn.close()

    def get_courses(self, user_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM courses WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = c.fetchall()
        conn.close()

        courses = []
        for r in rows:
            c_type = CourseType[r[3]] if r[3] in CourseType.__members__ else CourseType.COURSE
            c_status = CourseStatus[r[4]] if r[4] in CourseStatus.__members__ else CourseStatus.PLANNED

            course = Course(
                id=r[0], user_id=r[1], title=r[2],
                course_type=c_type, status=c_status,
                total_units=r[5], completed_units=r[6],
                link=r[7], description=r[8]
            )
            try:
                course.created_at = datetime.fromisoformat(r[9])
            except:
                pass
            courses.append(course)
        return courses

    def delete_course(self, course_id: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        conn.commit()
        conn.close()