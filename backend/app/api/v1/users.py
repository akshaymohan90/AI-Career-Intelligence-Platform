from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

user_service = UserService()


@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.put(
    "/me",
    response_model=UserResponse
)
def update_my_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return user_service.update_profile(
            db,
            current_user,
            data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )



@router.delete("/me")
def deactivate_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_service.deactivate_account(db, current_user)
    return {"message": "Account deactivated successfully"}