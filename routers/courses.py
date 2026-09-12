import os

from fastapi import APIRouter, Depends, HTTPException, Path
from groq import Groq
from pydantic import BaseModel, Field

from auth import get_current_employer
from models import Employer


router = APIRouter(prefix="/courses", tags=["courses"])


class CourseSuggestionRequest(BaseModel):
    skills: list[str] = Field(..., min_length=1, max_length=20)
    gap_info: str = Field(..., min_length=10, max_length=2000)


@router.post("/{course_id}/suggest")
def suggest_course(
    course_id: int = Path(..., gt=0),
    request: CourseSuggestionRequest = ...,
    current_employer: Employer = Depends(get_current_employer),
):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured")

    client = Groq(api_key=api_key)
    prompt = (
        f"Course ID: {course_id}\n"
        f"Course skills: {', '.join(request.skills)}\n"
        f"Skill gap: {request.gap_info}\n\n"
        "Give one short recommendation explaining how this course addresses the gap."
    )

    try:
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            messages=[
                {
                    "role": "system",
                    "content": "You provide concise course recommendations.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=80,
        )
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"AI service error: {error}")

    suggestion = response.choices[0].message.content
    return {"course_id": course_id, "suggestion": suggestion}