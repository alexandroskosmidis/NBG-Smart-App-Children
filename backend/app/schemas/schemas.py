from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models import AgeGroup, LessonStatus


# ──────────────────────────────────────────
# User Schemas
# ──────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int
    is_parent: bool = False
    parent_id: int | None = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    age: int
    age_group: AgeGroup
    coins: int
    xp: int
    is_parent: bool

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────
# Auth Schemas
# ──────────────────────────────────────────

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ──────────────────────────────────────────
# Quiz Schemas
# ──────────────────────────────────────────

class QuizQuestion(BaseModel):
    question: str
    options: list[str]       # 4 options
    correct_index: int       # 0-3
    explanation: str         # shown after answering


class QuizOut(BaseModel):
    id: int
    lesson_id: int
    questions: list[QuizQuestion]

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────
# Lesson Schemas
# ──────────────────────────────────────────

class LessonContent(BaseModel):
    """Structure of the JSON stored in Lesson.content"""
    intro: str                   # short hook paragraph
    sections: list[dict]         # [{title, body, emoji}]
    key_takeaways: list[str]     # bullet points summary
    fun_fact: str                # engaging fact for kids


class LessonOut(BaseModel):
    id: int
    title: str
    description: str
    age_group: AgeGroup
    topic: str
    order_index: int
    xp_reward: int
    coin_reward: int
    content: dict
    has_quiz: bool

    model_config = {"from_attributes": True}


class LessonListItem(BaseModel):
    id: int
    title: str
    description: str
    topic: str
    order_index: int
    xp_reward: int
    coin_reward: int

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────
# Progress Schemas
# ──────────────────────────────────────────

class LessonProgressOut(BaseModel):
    lesson_id: int
    status: LessonStatus
    quiz_score: float | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class QuizSubmit(BaseModel):
    """User sends their answers: list of chosen option indices"""
    answers: list[int]


class QuizResult(BaseModel):
    score: float          # 0.0 - 1.0
    correct_count: int
    total_questions: int
    xp_earned: int
    coins_earned: int
    passed: bool          # score >= 0.7
    feedback: list[dict]  # [{question, your_answer, correct_answer, explanation}]