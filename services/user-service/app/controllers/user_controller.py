from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.pagination import PaginatedResponse, PaginationParams
from app.schemas.user import UserCreateRequest, UserResponse
from app.services.user_service import UserService


class UserController:

    def __init__(self, db: Session):
        self.service = UserService(db)

    def create_user(self, payload: UserCreateRequest):
        try:
            return self.service.register_user(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    def get_user(self, user_id: str):
        user = self.service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user_id}' not found.",
            )
        return user

    def list_users(self, pagination: PaginationParams):
        users, total = self.service.list_users(
            offset=pagination.offset, limit=pagination.page_size
        )
        return PaginatedResponse[UserResponse].create(
            items=users, total=total,
            page=pagination.page, page_size=pagination.page_size,
        )
