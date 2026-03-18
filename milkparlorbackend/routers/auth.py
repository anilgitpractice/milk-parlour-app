from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import AuthResponse, LoginRequest, RegisterRequest, User


router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    if str(payload.email).endswith("@blocked.com"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email domain not allowed.")

    existing = db.query(User).filter(User.email == str(payload.email)).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    user = User(
        email=str(payload.email),
        hashed_password=payload.password,
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()

    return AuthResponse(access_token="mock-registration-token")


@router.post("/login", response_model=AuthResponse)
async def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(payload.email)).first()
    if user is None or user.hashed_password != payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    return AuthResponse(access_token="mock-login-token")

