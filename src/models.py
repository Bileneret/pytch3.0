import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

class GoalPriority(Enum):
    LOW = "Низький"
    MEDIUM = "Середній"
    HIGH = "Високий"
    CRITICAL = "Критичний"

class GoalStatus(Enum):
    PLANNED = "Заплановано"
    IN_PROGRESS = "В процесі"
    COMPLETED = "Виконано"
    MISSED = "Прострочено"

@dataclass
class User:
    username: str
    password_hash: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    total_completed_goals: int = 0
    avatar_path: str = ""

@dataclass
class Category:
    """Нова модель: Категорія цілі"""
    name: str
    color: str = "#3b82f6" # Hex колір (за замовчуванням синій)
    user_id: str = ""
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
class LearningGoal:
    title: str
    description: str = ""
    deadline: Optional[datetime] = None
    priority: GoalPriority = GoalPriority.MEDIUM
    status: GoalStatus = GoalStatus.PLANNED
    user_id: str = ""
    category_id: Optional[str] = None  # Зв'язок з категорією
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Habit:
    title: str
    user_id: str
    streak: int = 0
    last_completed_date: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))