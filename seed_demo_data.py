import sys
from pathlib import Path

from dotenv import load_dotenv


root = Path(__file__).resolve().parent
load_dotenv(root / ".env")

from database import Base, SessionLocal, engine
from models import Course, District, Skill, WorkforceSkill


DEMO_DATA = {
    "Bengaluru": {
        "target_learners": 50,
        "workforce": {"python": 8, "sql": 12, "cloud computing": 4, "cybersecurity": 6},
        "courses": [
            ("Python and Data Analytics", ["python", "sql"]),
            ("Cloud Computing Foundations", ["cloud computing"]),
            ("Cybersecurity Basics", ["cybersecurity"]),
        ],
    },
    "Pune": {
        "target_learners": 40,
        "workforce": {"python": 5, "sql": 7, "java": 10, "cloud computing": 3},
        "courses": [
            ("Backend Development with Java", ["java", "sql"]),
            ("Cloud Computing Foundations", ["cloud computing"]),
        ],
    },
    "Delhi / NCR": {
        "target_learners": 60,
        "workforce": {"python": 10, "sql": 8, "data analysis": 5},
        "courses": [
            ("Applied Data Analysis", ["python", "data analysis", "sql"]),
        ],
    },
}


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        for district_name, values in DEMO_DATA.items():
            district = session.query(District).filter(District.name == district_name).one_or_none()
            if district is None:
                district = District(name=district_name, target_learners=values["target_learners"], is_demo=True)
                session.add(district)
                session.flush()

            for skill_name, available_count in values["workforce"].items():
                skill = session.query(Skill).filter(Skill.name == skill_name).one_or_none()
                if skill is None:
                    skill = Skill(name=skill_name)
                    session.add(skill)
                    session.flush()
                workforce = session.query(WorkforceSkill).filter(
                    WorkforceSkill.district_id == district.id,
                    WorkforceSkill.skill_id == skill.id,
                ).one_or_none()
                if workforce is None:
                    session.add(WorkforceSkill(
                        district_id=district.id,
                        skill_id=skill.id,
                        available_count=available_count,
                        is_demo=True,
                    ))

            for course_name, skill_names in values["courses"]:
                course = session.query(Course).filter(
                    Course.name == course_name,
                    Course.district_id == district.id,
                ).one_or_none()
                if course is None:
                    course = Course(
                        name=course_name,
                        description="Demo course record pending validation with the training provider.",
                        district_id=district.id,
                        is_demo=True,
                    )
                    session.add(course)
                    session.flush()
                course.skills = [
                    session.query(Skill).filter(Skill.name == skill_name).one()
                    for skill_name in skill_names
                ]

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
    print("Demo districts, workforce skills, and courses are ready.")