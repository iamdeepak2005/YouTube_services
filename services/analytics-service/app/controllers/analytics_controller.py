from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.analytics import VideoEventRequest
from app.services.analytics_service import AnalyticsService


class AnalyticsController:

    def __init__(self, db: Session):
        self.service = AnalyticsService(db)

    def record_event(self, payload: VideoEventRequest):
        return self.service.record_event(payload)

    def get_dropoff(self, video_id: str):
        return self.service.get_dropoff(video_id)

    def get_popular_videos(self, limit: int):
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="limit must be 1-100.")
        return self.service.get_popular_videos(limit=limit)
