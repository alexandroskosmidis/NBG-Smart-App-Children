from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Lesson, Quiz, LessonProgress, LessonStatus
from app.schemas import LessonOut, LessonListItem, QuizOut, QuizSubmit, QuizResult, LessonProgressOut
from app.auth import get_current_user
from app.services.gemini_service import generate_lesson_content, generate_quiz

router = APIRouter(prefix="/lessons", tags=["Lessons"])


# ──────────────────────────────────────────
# GET /lessons  →  list lessons for user's age group
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
    lessons = result.scalars().all()
    return lessons


# ──────────────────────────────────────────
# GET /lessons/{lesson_id}  →  full lesson content
# ──────────────────────────────────────────

@router.get("/{lesson_id}", response_model=LessonOut)
async def get_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson = await _get_lesson_or_404(lesson_id, db)

    # Guard: user can only access lessons of their age group
    if lesson.age_group != current_user.age_group:
        raise HTTPException(403, "Δεν έχεις πρόσβαση σε αυτό το μάθημα.")

    # Mark as in_progress if not started yet
    await _upsert_progress(current_user.id, lesson_id, LessonStatus.IN_PROGRESS, db)

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

    if lesson.age_group != current_user.age_group:
        raise HTTPException(403, "Δεν έχεις πρόσβαση σε αυτό το quiz.")

    if lesson.quiz is None:
        raise HTTPException(404, "Δεν υπάρχει quiz για αυτό το μάθημα.")

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

    if lesson.quiz is None:
        raise HTTPException(404, "Δεν υπάρχει quiz για αυτό το μάθημα.")

    questions = lesson.quiz.questions
    if len(payload.answers) != len(questions):
        raise HTTPException(400, f"Αναμένονται {len(questions)} απαντήσεις.")

    # Grade the quiz
    correct_count = 0
    feedback = []
    for i, (q, user_answer) in enumerate(zip(questions, payload.answers)):
        is_correct = user_answer == q["correct_index"]
        if is_correct:
            correct_count += 1
        feedback.append({
            "question":       q["question"],
            "your_answer":    q["options"][user_answer],
            "correct_answer": q["options"][q["correct_index"]],
            "explanation":    q["explanation"],
            "is_correct":     is_correct,
        })

    score  = correct_count / len(questions)
    passed = score >= 0.7

    # Rewards only on pass
    xp_earned    = lesson.xp_reward    if passed else lesson.xp_reward // 4
    coins_earned = lesson.coin_reward  if passed else 0

    # Update user coins & XP
    current_user.xp    += xp_earned
    current_user.coins += coins_earned

    # Update lesson progress
    await _upsert_progress(
        current_user.id, lesson_id,
        LessonStatus.COMPLETED if passed else LessonStatus.IN_PROGRESS,
        db,
        quiz_score=score,
        completed_at=datetime.utcnow() if passed else None,
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
# GET /lessons/progress/me
# ──────────────────────────────────────────

@router.get("/progress/me", response_model=list[LessonProgressOut])
async def my_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LessonProgress).where(LessonProgress.user_id == current_user.id)
    )
    return result.scalars().all()


# ──────────────────────────────────────────
# ADMIN: POST /lessons/generate  →  generate lesson via Gemini (dev/admin use)
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
    """
    from app.models import AgeGroup
    try:
        age_group = AgeGroup(age_group_str)
    except ValueError:
        raise HTTPException(400, f"Άκυρο age_group. Επιλογές: {[a.value for a in AgeGroup]}")

    # Generate content
    content = await generate_lesson_content(topic, age_group)
    quiz_questions = await generate_quiz(topic, age_group, content)

    lesson = Lesson(
        title=content.get("intro", topic)[:80],   # use first 80 chars of intro as title fallback
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
# Helpers
# ──────────────────────────────────────────

async def _get_lesson_or_404(lesson_id: int, db: AsyncSession) -> Lesson:
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(404, "Το μάθημα δεν βρέθηκε.")
    return lesson


async def _upsert_progress(
    user_id: int,
    lesson_id: int,
    status: LessonStatus,
    db: AsyncSession,
    quiz_score: float | None = None,
    completed_at: datetime | None = None,
):
    result = await db.execute(
        select(LessonProgress)
        .where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id)
    )
    progress = result.scalar_one_or_none()

    if progress:
        # Don't downgrade a completed lesson back to in_progress
        if progress.status != LessonStatus.COMPLETED:
            progress.status = status
        if quiz_score is not None:
            progress.quiz_score = quiz_score
        if completed_at is not None:
            progress.completed_at = completed_at
    else:
        db.add(LessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status=status,
            quiz_score=quiz_score,
            completed_at=completed_at,
        ))