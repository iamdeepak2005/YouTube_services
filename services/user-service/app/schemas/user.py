from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., description="Unique email address for the learner")

    model_config = {"json_schema_extra": {"example": {"email": "learner@example.com"}}}


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    detail: str
