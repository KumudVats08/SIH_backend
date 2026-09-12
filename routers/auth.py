from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_employer, hash_password, verify_password
from database import get_db
from models import Employer


router = APIRouter(prefix="/auth", tags=["auth"])


class EmployerCredentials(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register_employer(credentials: EmployerCredentials, db: Session = Depends(get_db)):
    existing_employer = db.query(Employer).filter(Employer.email == credentials.email).first()
    if existing_employer:
        raise HTTPException(status_code=400, detail="Email is already registered")

    employer = Employer(
        email=credentials.email,
        password_hash=hash_password(credentials.password),
    )
    db.add(employer)
    db.commit()
    db.refresh(employer)
    return {"id": employer.id, "email": employer.email}


@router.post("/login")
def login_employer(credentials: EmployerCredentials, db: Session = Depends(get_db)):
    employer = db.query(Employer).filter(Employer.email == credentials.email).first()
    if employer is None or not verify_password(credentials.password, employer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return {"access_token": create_access_token(employer), "token_type": "bearer"}


@router.get("/me")
def get_my_profile(current_employer: Employer = Depends(get_current_employer)):
    return {"id": current_employer.id, "email": current_employer.email}