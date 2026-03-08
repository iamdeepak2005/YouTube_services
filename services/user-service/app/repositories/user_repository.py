from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreateRequest


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: UserCreateRequest) -> User:
        user = User(email=payload.email)
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Email '{payload.email}' is already registered.")
        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, offset: int = 0, limit: int = 20) -> List[User]:
        return self.db.query(User).offset(offset).limit(limit).all()

    def count(self) -> int:
        return self.db.query(User).count()
