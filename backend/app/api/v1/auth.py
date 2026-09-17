from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.database import get_db
from app.schemas import UserCreate, UserResponse, UserLogin, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

auth_service = AuthService()


@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(userdata: UserCreate, db: Session = Depends(get_db)):
    try:
        return auth_service.register_user(db, userdata)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(userdata: UserLogin, db: Session = Depends(get_db)):
    try:
        token = auth_service.login(db, userdata.email, userdata.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

