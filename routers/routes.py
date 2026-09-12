from fastapi import APIRouter


router = APIRouter()


@router.get("/demand")
def get_demand(district: str = "", sector: str = ""):
    return {
        "district": district,
        "sector": sector,
        "demand": [
            {"skill": "Python", "openings": 12},
            {"skill": "Data Analysis", "openings": 8},
        ],
    }


@router.get("/gaps")
def get_gaps(district: str = ""):
    return {
        "district": district,
        "gaps": [
            {"skill": "Cloud Computing", "severity": "high"},
            {"skill": "Cybersecurity", "severity": "medium"},
        ],
    }


@router.get("/courses/flagged")
def get_flagged_courses(district: str = ""):
    return {
        "district": district,
        "courses": [
            {"id": 1, "name": "Introduction to Cloud Computing", "reason": "High demand"},
            {"id": 2, "name": "Cybersecurity Basics", "reason": "Skill gap"},
        ],
    }


@router.get("/districts/{district_id}/plan")
def get_district_plan(district_id: int):
    return {
        "district_id": district_id,
        "plan": {
            "priority": "Cloud Computing",
            "recommended_courses": [1, 2],
            "target_learners": 50,
        },
    }