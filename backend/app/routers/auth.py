"""
Addresses for registering, signing up, and logging in.

Mounted at /api/v1/auth by main.py. Paths here never end in "/" (T-02).
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    ApplicantSignupRequest, LoginRequest, RegisterRequest, TokenResponse, UserResponse,
)
from app.services import auth_service
from app.services.activity_service import request_meta
from app.services.errors import EmailAlreadyRegistered, InvalidCredentials, RuleViolation

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    """Bank staff account. This is the address the trainer's tests use."""
    try:
        return auth_service.register_staff(db, data, meta=request_meta(request))
    except EmailAlreadyRegistered as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except RuleViolation as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)


@router.post("/register-applicant", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_applicant(data: ApplicantSignupRequest, request: Request, db: Session = Depends(get_db)):
    """Customer signup. Creates the login and the borrower profile together."""
    try:
        return auth_service.signup_applicant(db, data, meta=request_meta(request))
    except EmailAlreadyRegistered as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """JSON in, token out. A wrong email and a wrong password get the same answer."""
    try:
        user, token = auth_service.authenticate(db, data.email, data.password, meta=request_meta(request))
    except InvalidCredentials as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(
        access_token=token,
        expires_in_hours=settings.access_token_expire_hours,
        email=user.email,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    """Who am I? Handy for the front-end after a page refresh."""
    return user
