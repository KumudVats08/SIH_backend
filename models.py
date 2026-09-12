from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from database import Base


job_skills = Table(
    "job_skills",
    Base.metadata,
    Column("job_id", Integer, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)

course_skills = Table(
    "course_skills",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)


class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)


class GapValidation(Base):
    __tablename__ = "gap_validations"

    id = Column(Integer, primary_key=True, index=True)
    gap_id = Column(Integer, nullable=False, index=True)
    employer_id = Column(Integer, ForeignKey("employers.id"), nullable=False)
    decision = Column(String(20), nullable=False)
    comment = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    platform = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True, index=True)
    employment_type = Column(String(50), nullable=True)
    sector = Column(String(100), nullable=True, index=True)
    job_url = Column(String(500), nullable=True)
    experience_min = Column(Integer, nullable=True)
    experience_max = Column(Integer, nullable=True)

    skills = relationship("Skill", secondary=job_skills, back_populates="jobs")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    jobs = relationship("Job", secondary=job_skills, back_populates="skills")
    courses = relationship("Course", secondary=course_skills, back_populates="skills")


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    target_learners = Column(Integer, nullable=False, default=50)
    is_demo = Column(Boolean, nullable=False, default=True)

    workforce_skills = relationship("WorkforceSkill", back_populates="district")
    courses = relationship("Course", back_populates="district")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True, index=True)
    is_demo = Column(Boolean, nullable=False, default=True)

    district = relationship("District", back_populates="courses")
    skills = relationship("Skill", secondary=course_skills, back_populates="courses")


class WorkforceSkill(Base):
    __tablename__ = "workforce_skills"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    available_count = Column(Integer, nullable=False, default=0)
    is_demo = Column(Boolean, nullable=False, default=True)

    district = relationship("District", back_populates="workforce_skills")
    skill = relationship("Skill")