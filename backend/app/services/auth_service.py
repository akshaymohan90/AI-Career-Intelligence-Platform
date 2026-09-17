from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.utils.security import hash_password,verify_password, create_access_token


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def register_user(self, db: Session, user_create: UserCreate):
        existing_user = self.user_repository.get_by_email(db, user_create.email)
        if existing_user:
            raise ValueError("User with this email already exists.")

        new_user = User(
            full_name=user_create.full_name,
            email=user_create.email,
            password=hash_password(user_create.password),
        )

        return self.user_repository.create(db, new_user)

    def login(self, db: Session, email: str, password: str):
        user = self.user_repository.get_by_email(db, email)
        if not user or not verify_password(password, user.password):
            raise ValueError("Invalid email or password.")

        return create_access_token(user.id)