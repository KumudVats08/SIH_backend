from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Course, District, Job, Skill, WorkforceSkill


router = APIRouter()


def _skill_demand(db: Session, district: str = "", sector: str = ""):
    query = (
        db.query(Skill.name, func.count(Job.id).label("openings"))
        .join(Skill.jobs)
    )
    if district:
        query = query.filter(Job.location.ilike(f"%{district.strip()}%"))
    if sector:
        query = query.filter(Job.sector.ilike(f"%{sector.strip()}%"))
    return query.group_by(Skill.id, Skill.name).order_by(func.count(Job.id).desc()).all()


@router.get("/demand")
def get_demand(
    district: str = "",
    sector: str = "",
    db: Session = Depends(get_db),
):
    demand = _skill_demand(db, district, sector)
    return {
        "district": district,
        "sector": sector,
        "demand": [{"skill": name, "openings": openings} for name, openings in demand],
    }


@router.get("/gaps")
def get_gaps(district: str = "", db: Session = Depends(get_db)):
    demand = _skill_demand(db, district)
    district_record = (
        db.query(District)
        .filter(District.name.ilike(district.strip()))
        .first()
        if district.strip()
        else None
    )
    workforce = {}
    if district_record:
        workforce = {
            item.skill_id: item.available_count
            for item in db.query(WorkforceSkill).filter(
                WorkforceSkill.district_id == district_record.id
            )
        }

    return {
        "district": district,
        "gaps": [
            {
                "skill": name,
                "severity": "high" if openings >= 10 else "medium" if openings >= 5 else "low",
                "openings": openings,
                "available_workers": workforce.get(
                    db.query(Skill).filter(Skill.name == name).first().id, 0
                ) if district_record and db.query(Skill).filter(Skill.name == name).first() else None,
                "source": "jobs+demo_workforce" if district_record else "job_demand",
            }
            for name, openings in demand
        ],
    }


@router.get("/courses/flagged")
def get_flagged_courses(district: str = "", db: Session = Depends(get_db)):
    demand = dict(_skill_demand(db, district))
    courses = db.query(Course).all()
    flagged = []
    for course in courses:
        matching_skills = [skill.name for skill in course.skills if skill.name in demand]
        if matching_skills:
            flagged.append({
                "id": course.id,
                "name": course.name,
                "reason": "Addresses in-demand skills",
                "skills": matching_skills,
                "is_demo": course.is_demo,
            })
    return {
        "district": district,
        "courses": flagged,
    }


@router.get("/districts/{district_id}/plan")
def get_district_plan(district_id: int, db: Session = Depends(get_db)):
    district = db.query(District).filter(District.id == district_id).first()
    if district is None:
        raise HTTPException(status_code=404, detail="District not found")
    demand = _skill_demand(db, district.name)
    priority = demand[0][0] if demand else None
    courses = [
        {"id": course.id, "name": course.name}
        for course in db.query(Course).filter(Course.district_id == district.id).all()
    ]
    return {
        "district_id": district_id,
        "plan": {
            "priority": priority,
            "recommended_courses": courses,
            "target_learners": district.target_learners,
            "is_demo": district.is_demo,
        },
    }