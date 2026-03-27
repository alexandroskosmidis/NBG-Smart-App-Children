from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.models import AgeGroup, LessonStatus


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
    options: list[str]
    correct_index: int
    explanation: str


class QuizOut(BaseModel):
    id: int
    lesson_id: int
    questions: list[QuizQuestion]

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────
# Lesson Schemas
# ──────────────────────────────────────────

class LessonSection(BaseModel):
    title: str
    body: str
    emoji: str | None = None


class LessonContent(BaseModel):
    intro: str
    sections: list[LessonSection]
    key_takeaways: list[str]
    fun_fact: str


class LessonOut(BaseModel):
    id: int
    title: str
    description: str
    age_group: AgeGroup
    topic: str
    order_index: int
    xp_reward: int
    coin_reward: int
    content: LessonContent
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
    answers: list[int]


class QuizFeedbackItem(BaseModel):
    question: str
    your_answer: int
    correct_answer: int
    explanation: str


class QuizResult(BaseModel):
    score: float
    correct_count: int
    total_questions: int
    xp_earned: int
    coins_earned: int
    passed: bool
    feedback: list[QuizFeedbackItem]