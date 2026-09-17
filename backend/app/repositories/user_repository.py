from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str):
        return self.get_by_email(db, email)

    def get_user_by_id(self, db: Session, user_id: int):
        return self.get_by_id(db, user_id)

    def create(self, db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, user: User):
        db.commit()
        db.refresh(user)
        return user