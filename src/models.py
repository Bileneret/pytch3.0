import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
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
    """Модель користувача (Учня)."""
    username: str
    password_hash: str = ""  # Нове поле для пароля
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    # Статистика навчання
    level: int = 1
    current_xp: int = 0
    xp_to_next_level: int = 100
    total_completed_goals: int = 0
    avatar_path: str = ""


@dataclass
class LearningGoal:
    """Навчальна ціль."""
    title: str
    description: str = ""
    deadline: Optional[datetime] = None
    priority: GoalPriority = GoalPriority.MEDIUM
    status: GoalStatus = GoalStatus.PLANNED

    user_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))