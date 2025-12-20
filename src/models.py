from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

# --- ENUMS ---
class GoalStatus(Enum):
    PLANNED = "Заплановано"
    IN_PROGRESS = "В процесі"
    COMPLETED = "Виконано"
    MISSED = "Пропущено"

class GoalPriority(Enum):
    LOW = "Низький"
    MEDIUM = "Середній"
    HIGH = "Високий"
    CRITICAL = "Критичний"

class CourseType(Enum):
    COURSE = "Курс"
    BOOK = "Книга"
    VIDEO = "Відео"
    ARTICLE = "Стаття"
    PROJECT = "Проект"
    CHALLENGE = "Челендж"

class CourseStatus(Enum):
    PLANNED = "Планую"
    IN_PROGRESS = "В процесі"
    COMPLETED = "Завершено"
    DROPPED = "Закинув"

# --- DATA CLASSES ---

@dataclass
class User:
    username: str
    password_hash: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    total_completed_goals: int = 0
    avatar_path: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Category:
    name: str
    user_id: str
    color: str = "#3b82f6"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

# НОВИЙ КЛАС ДЛЯ ТЕМ
@dataclass
class Topic:
    name: str
    user_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class LearningGoal:
    title: str
    description: str = ""
    deadline: str = None
    priority: GoalPriority = GoalPriority.MEDIUM
    status: GoalStatus = GoalStatus.PLANNED
    user_id: str = ""
    category_id: str = None
    link: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class SubGoal:
    title: str
    goal_id: str
    is_completed: bool = False
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Habit:
    title: str
    user_id: str
    streak: int = 0
    last_completed_date: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Course:
    title: str
    user_id: str
    course_type: CourseType = CourseType.COURSE
    status: CourseStatus = CourseStatus.IN_PROGRESS
    total_units: int = 10
    completed_units: int = 0
    link: str = ""
    description: str = ""
    # Зберігаємо ID теми
    topic_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))