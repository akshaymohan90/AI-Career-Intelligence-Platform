from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def update_profile(self, db: Session, user: User, user_update: UserUpdate):
        if user_update.full_name is not None:
            user.full_name = user_update.full_name

        if user_update.email is not None:
            existing_user = self.user_repository.get_by_email(db, user_update.email)
            if existing_user and existing_user.id != user.id:
                raise ValueError("Email is already registered")

            user.email = user_update.email

        return self.user_repository.update(db, user)

    def deactivate_account(self, db: Session, user: User):
        user.is_active = False
        return self.user_repository.update(db, user)