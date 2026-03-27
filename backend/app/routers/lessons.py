from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.database import get_db
from app.models import (
    AgeGroup,
    Lesson,
    LessonProgress,
    LessonStatus,
    Quiz,
    User,
)
from app.schemas import (
    LessonListItem,
    LessonOut,
    LessonProgressOut,
    QuizOut,
    QuizResult,
    QuizSubmit,
)
from app.services.gemini_service import generate_lesson_content, generate_quiz

router = APIRouter(prefix="/lessons", tags=["Lessons"])


# ──────────────────────────────────────────
# GET /lessons/progress/me
# Must be declared BEFORE /{lesson_id}
# ──────────────────────────────────────────

@router.get("/progress/me", response_model=list[LessonProgressOut])
async def my_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LessonProgress)
        .where(LessonProgress.user_id == current_user.id)
        .order_by(LessonProgress.lesson_id)
    )
    return result.scalars().all()


# ──────────────────────────────────────────
# ADMIN / DEV: POST /lessons/generate
# Must be declared BEFORE /{lesson_id}
# ──────────────────────────────────────────

@router.post("/generate", status_code=201)
async def generate_lesson(
    topic: str,
    age_group_str: str,
    order_index: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Dev endpoint: asks Gemini to generate a lesson + quiz and saves them to DB.
    Call this to seed your lessons table.

    TODO:
    Protect this route with admin auth before production exposure.
    """
    try:
        age_group = AgeGroup(age_group_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Άκυρο age_group. Επιλογές: {[a.value for a in AgeGroup]}",
        )

    content = await generate_lesson_content(topic, age_group)
    quiz_questions = await generate_quiz(topic, age_group, content)

    lesson = Lesson(
        title=content.get("intro", topic)[:80],
        description=content["intro"],
        age_group=age_group,
        topic=topic,
        order_index=order_index,
        content=content,
    )
    db.add(lesson)
    await db.flush()

    quiz = Quiz(lesson_id=lesson.id, questions=quiz_questions)
    db.add(quiz)

    return {"message": "Lesson generated!", "lesson_id": lesson.id}


# ──────────────────────────────────────────
# GET /lessons
# ──────────────────────────────────────────

@router.get("/", response_model=list[LessonListItem])
async def list_lessons(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns all lessons for the logged-in user's age group, ordered."""
    result = await db.execute(
        select(Lesson)
        .where(Lesson.age_group == current_user.age_group)
        .order_by(Lesson.order_index)
    )
    return result.scalars().all()


# ──────────────────────────────────────────
# GET /lessons/{lesson_id}
# ──────────────────────────────────────────

@router.get("/{lesson_id}", response_model=LessonOut)
async def get_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson = await _get_lesson_or_404(lesson_id, db)
    _ensure_lesson_access(lesson, current_user, "μάθημα")

    # Mark as in_progress only if not already completed
    await _upsert_progress(
        current_user.id,
        lesson_id,
        LessonStatus.IN_PROGRESS,
        db,
    )

    return LessonOut(
        **{c.name: getattr(lesson, c.name) for c in lesson.__table__.columns},
        has_quiz=lesson.quiz is not None,
    )


# ──────────────────────────────────────────
# GET /lessons/{lesson_id}/quiz
# ──────────────────────────────────────────

@router.get("/{lesson_id}/quiz", response_model=QuizOut)
async def get_quiz(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson = await _get_lesson_or_404(lesson_id, db)
    _ensure_lesson_access(lesson, current_user, "quiz")

    if lesson.quiz is None:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει quiz για αυτό το μάθημα.")

    return lesson.quiz


# ──────────────────────────────────────────
# POST /lessons/{lesson_id}/quiz/submit
# ──────────────────────────────────────────

@router.post("/{lesson_id}/quiz/submit", response_model=QuizResult)
async def submit_quiz(
    lesson_id: int,
    payload: QuizSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson = await _get_lesson_or_404(lesson_id, db)
    _ensure_lesson_access(lesson, current_user, "quiz")

    if lesson.quiz is None:
        raise HTTPException(status_code=404, detail="Δεν υπάρχει quiz για αυτό το μάθημα.")

    questions = lesson.quiz.questions

    if len(payload.answers) != len(questions):
        raise HTTPException(
            status_code=400,
            detail=f"Αναμένονται {len(questions)} απαντήσεις.",
        )

    existing_progress = await _get_progress(current_user.id, lesson_id, db)

    already_completed = (
        existing_progress is not None
        and existing_progress.status == LessonStatus.COMPLETED
    )

    has_previous_graded_attempt = (
        existing_progress is not None
        and existing_progress.quiz_score is not None
        and existing_progress.status != LessonStatus.COMPLETED
    )

    # Grade the quiz
    correct_count = 0
    feedback = []

    for i, (q, user_answer) in enumerate(zip(questions, payload.answers)):
        options = q.get("options", [])
        correct_index = q.get("correct_index")

        if not isinstance(user_answer, int):
            raise HTTPException(
                status_code=400,
                detail=f"Η απάντηση στη θέση {i} πρέπει να είναι integer.",
            )

        if user_answer < 0 or user_answer >= len(options):
            raise HTTPException(
                status_code=400,
                detail=f"Μη έγκυρο answer index στη θέση {i}.",
            )

        if correct_index is None or correct_index < 0 or correct_index >= len(options):
            raise HTTPException(
                status_code=500,
                detail=f"Μη έγκυρη δομή quiz στη θέση {i}.",
            )

        is_correct = user_answer == correct_index
        if is_correct:
            correct_count += 1

        feedback.append(
            {
                "question": q["question"],
                "your_answer": options[user_answer],
                "correct_answer": options[correct_index],
                "explanation": q["explanation"],
                "is_correct": is_correct,
            }
        )

    score = correct_count / len(questions)
    passed = score >= 0.7

    # Reward policy:
    # - Completed lesson: no more rewards
    # - First failed graded attempt: quarter XP
    # - Later successful pass after a failed attempt: remaining XP + full coins
    # - First successful pass: full XP + full coins
    fail_xp = lesson.xp_reward // 4

    if already_completed:
        xp_earned = 0
        coins_earned = 0
    elif passed:
        xp_earned = lesson.xp_reward if not has_previous_graded_attempt else max(lesson.xp_reward - fail_xp, 0)
        coins_earned = lesson.coin_reward
    else:
        xp_earned = fail_xp if not has_previous_graded_attempt else 0
        coins_earned = 0

    current_user.xp += xp_earned
    current_user.coins += coins_earned

    await _upsert_progress(
        current_user.id,
        lesson_id,
        LessonStatus.COMPLETED if passed else LessonStatus.IN_PROGRESS,
        db,
        quiz_score=score,
        completed_at=datetime.now(timezone.utc) if passed else None,
    )

    return QuizResult(
        score=score,
        correct_count=correct_count,
        total_questions=len(questions),
        xp_earned=xp_earned,
        coins_earned=coins_earned,
        passed=passed,
        feedback=feedback,
    )


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────

def _ensure_lesson_access(lesson: Lesson, current_user: User, resource_name: str) -> None:
    if lesson.age_group != current_user.age_group:
        raise HTTPException(
            status_code=403,
            detail=f"Δεν έχεις πρόσβαση σε αυτό το {resource_name}.",
        )


async def _get_lesson_or_404(lesson_id: int, db: AsyncSession) -> Lesson:
    result = await db.execute(
        select(Lesson)
        .options(selectinload(Lesson.quiz))
        .where(Lesson.id == lesson_id)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Το μάθημα δεν βρέθηκε.")
    return lesson


async def _get_progress(
    user_id: int,
    lesson_id: int,
    db: AsyncSession,
) -> LessonProgress | None:
    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == user_id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    return result.scalar_one_or_none()


async def _upsert_progress(
    user_id: int,
    lesson_id: int,
    status: LessonStatus,
    db: AsyncSession,
    quiz_score: float | None = None,
    completed_at: datetime | None = None,
):
    progress = await _get_progress(user_id, lesson_id, db)

    if progress:
        # Never downgrade COMPLETED -> IN_PROGRESS
        if progress.status != LessonStatus.COMPLETED:
            progress.status = status

        if quiz_score is not None:
            progress.quiz_score = quiz_score

        if completed_at is not None:
            progress.completed_at = completed_at
    else:
        db.add(
            LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                status=status,
                quiz_score=quiz_score,
                completed_at=completed_at,
            )
        )