from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class ProblemModel:
    id: str
    title: str
    content: str
    answer: str
    category: str
    difficulty: str
    created_at: datetime
    created_by: str
    tags: List[str] = None

@dataclass
class FeedbackModel:
    id: str
    problem_id: str
    student_id: str
    submission: str
    feedback: Optional[str]
    score: Optional[float]
    reviewed_by: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime] = None

@dataclass
class UserModel:
    id: str
    username: str
    password: str
    role: str
    name: str
    email: str
    created_at: datetime 