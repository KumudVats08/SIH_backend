from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from database import Base


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