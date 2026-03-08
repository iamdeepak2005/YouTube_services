from typing import List
from sqlalchemy.orm import Session

from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import VideoEventRequest, DropOffResponse, PopularVideoResponse


class AnalyticsService:

    def __init__(self, db: Session):
        self.repo = AnalyticsRepository(db)

    def record_event(self, payload: VideoEventRequest):
        return self.repo.record_event(
            user_id=payload.user_id, video_id=payload.video_id,
            event_type=payload.event_type, position_seconds=payload.position_seconds,
        )

    def get_dropoff(self, video_id: str) -> DropOffResponse:
        return self.repo.get_dropoff_timestamp(video_id)

    def get_popular_videos(self, limit: int = 10) -> List[PopularVideoResponse]:
        return self.repo.get_popular_videos(limit=limit)
