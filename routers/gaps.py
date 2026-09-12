from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_employer
from database import get_db
from models import Employer, GapValidation


router = APIRouter(prefix="/gaps", tags=["gaps"])


class GapValidationRequest(BaseModel):
    gap_id: int
    decision: Literal["confirm", "reject"]
    comment: str | None = None


@router.post("/validate")
def validate_gap(
    request: GapValidationRequest,
    current_employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    validation = GapValidation(
        gap_id=request.gap_id,
        employer_id=current_employer.id,
        decision=request.decision,
        comment=request.comment,
    )
    db.add(validation)
    db.commit()
    db.refresh(validation)
    return {
        "id": validation.id,
        "gap_id": validation.gap_id,
        "decision": validation.decision,
        "comment": validation.comment,
    }


@router.get("/validate")
def list_validations(
    current_employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    validations = (
        db.query(GapValidation)
        .filter(GapValidation.employer_id == current_employer.id)
        .order_by(GapValidation.id.desc())
        .all()
    )
    return [
        {
            "id": validation.id,
            "gap_id": validation.gap_id,
            "decision": validation.decision,
            "comment": validation.comment,
            "created_at": validation.created_at,
        }
        for validation in validations
    ]