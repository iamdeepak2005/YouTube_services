from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class VideoResponse(BaseModel):
    id: str
    youtube_video_id: str
    title: str
    thumbnail: Optional[str]
    duration: int
    position: int

    model_config = {"from_attributes": True}


class PlaylistResponse(BaseModel):
    id: str
    youtube_playlist_id: str
    title: str
    description: Optional[str]
    last_synced_at: datetime
    videos: List[VideoResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class VideoMetadataResponse(BaseModel):
    current: Optional[dict]
    next: Optional[dict]


class ErrorResponse(BaseModel):
    detail: str
