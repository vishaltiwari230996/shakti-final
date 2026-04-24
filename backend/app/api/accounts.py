"""Account signup / login / me — email + password, backed by Neon."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.database.crud import plans as plans_crud
from app.database.crud import users as users_crud
from app.database.models import User
from app.database.schemas.user import UserCreate, UserRead
from app.services.accounts_service import (
    hash_password,
    issue_token,
    verify_password,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone_number: Optional[str] = Field(None, max_length=32)
    plan_name: Optional[str] = "Free"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = users_crud.get_by_email(db, str(payload.email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    # Ensure the requested plan exists; otherwise fall back to Free.
    plan_name = payload.plan_name or "Free"
    if plans_crud.get_by_name(db, plan_name) is None:
        plan_name = "Free" if plans_crud.get_by_name(db, "Free") else None

    user = users_crud.create(
        db,
        UserCreate(
            name=payload.name,
            email=payload.email,
            phone_number=payload.phone_number,
            plan_name=plan_name,
        ),
    )
    user.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(user)

    token = issue_token(user.uid)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = users_crud.get_by_email(db, str(payload.email))
    if user is None or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = issue_token(user.uid)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
