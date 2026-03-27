import json
from typing import Any

import google.generativeai as genai

from app.core.config import settings
from app.models.models import AgeGroup


genai.configure(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-flash"


def _age_group_text(age_group: AgeGroup) -> str:
    if age_group == AgeGroup.JUNIOR:
        return "children 8-11 years old"
    if age_group == AgeGroup.INTERMEDIATE:
        return "children 12-14 years old"
    return "teenagers 15-17 years old"


def _extract_json(text: str) -> Any:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    start_obj = text.find("{")
    start_arr = text.find("[")

    starts = [x for x in [start_obj, start_arr] if x != -1]
    if not starts:
        raise ValueError("No JSON found in model response.")

    start = min(starts)
    json_text = text[start:]

    return json.loads(json_text)


async def generate_lesson_content(topic: str, age_group: AgeGroup) -> dict[str, Any]:
    model = genai.GenerativeModel(MODEL_NAME)

    prompt = f"""
You are creating educational finance content for {_age_group_text(age_group)}.

Topic: {topic}

Return ONLY valid JSON with this exact structure:
{{
  "intro": "short introduction paragraph",
  "sections": [
    {{
      "title": "section title",
      "content": "simple explanatory paragraph"
    }}
  ],
  "summary": "short summary",
  "key_points": [
    "point 1",
    "point 2",
    "point 3"
  ]
}}

Rules:
- Keep the language simple, clear, and age-appropriate.
- Make the lesson practical and beginner-friendly.
- Do not include markdown.
- Do not include any text outside JSON.
- Provide 3 to 5 sections.
- Key points should be 3 to 5 short bullets.
"""

    response = model.generate_content(prompt)
    text = response.text if hasattr(response, "text") else str(response)
    data = _extract_json(text)

    if not isinstance(data, dict):
        raise ValueError("Lesson content response is not a JSON object.")

    data.setdefault("intro", f"Introduction to {topic}")
    data.setdefault("sections", [])
    data.setdefault("summary", f"Summary for {topic}")
    data.setdefault("key_points", [])

    return data


async def generate_quiz(topic: str, age_group: AgeGroup, lesson_content: dict[str, Any]) -> list[dict[str, Any]]:
    model = genai.GenerativeModel(MODEL_NAME)

    lesson_json = json.dumps(lesson_content, ensure_ascii=False)

    prompt = f"""
You are creating a multiple-choice quiz for {_age_group_text(age_group)}.

Topic: {topic}

Lesson content:
{lesson_json}

Return ONLY valid JSON as an array with exactly 5 quiz questions.
Each item must have this exact structure:
[
  {{
    "question": "question text",
    "options": ["option 1", "option 2", "option 3", "option 4"],
    "correct_index": 0,
    "explanation": "short explanation"
  }}
]

Rules:
- Exactly 5 questions.
- Exactly 4 options per question.
- correct_index must be an integer from 0 to 3.
- Questions must be easy to understand and based on the lesson content.
- Do not include markdown.
- Do not include any text outside JSON.
"""

    response = model.generate_content(prompt)
    text = response.text if hasattr(response, "text") else str(response)
    data = _extract_json(text)

    if not isinstance(data, list):
        raise ValueError("Quiz response is not a JSON array.")

    normalized_questions = []

    for item in data[:5]:
        if not isinstance(item, dict):
            continue

        question = item.get("question", "").strip()
        options = item.get("options", [])
        correct_index = item.get("correct_index", 0)
        explanation = item.get("explanation", "").strip()

        if not question:
            continue
        if not isinstance(options, list) or len(options) != 4:
            continue
        if not isinstance(correct_index, int) or not (0 <= correct_index < 4):
            continue

        normalized_questions.append(
            {
                "question": question,
                "options": options,
                "correct_index": correct_index,
                "explanation": explanation or "This is the correct answer based on the lesson.",
            }
        )

    if len(normalized_questions) != 5:
        raise ValueError("Quiz generation did not return 5 valid questions.")

    return normalized_questions