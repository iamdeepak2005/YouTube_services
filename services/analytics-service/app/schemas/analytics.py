from datetime import datetime
from pydantic import BaseModel, Field
from app.models.video_event import EventType


class VideoEventRequest(BaseModel):
    user_id: str = Field(...)
    video_id: str = Field(...)
    event_type: EventType = Field(...)
    position_seconds: int = Field(default=0, ge=0)


class VideoEventResponse(BaseModel):
    id: str
    user_id: str
    video_id: str
    event_type: str
    position_seconds: int
    timestamp: datetime

    model_config = {"from_attributes": True}


class DropOffResponse(BaseModel):
    video_id: str
    dropoff_timestamp_seconds: int
    exit_frequency: int


class PopularVideoResponse(BaseModel):
    video_id: str
    total_views: int
    average_watch_seconds: float
    completion_rate: float
