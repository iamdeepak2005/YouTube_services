from typing import List
from collections import Counter

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.video_event import VideoEvent, EventType
from app.schemas.analytics import DropOffResponse, PopularVideoResponse


class AnalyticsRepository:

    def __init__(self, db: Session):
        self.db = db

    def record_event(self, user_id: str, video_id: str, event_type: EventType, position_seconds: int) -> VideoEvent:
        event = VideoEvent(
            user_id=user_id, video_id=video_id,
            event_type=event_type, position_seconds=position_seconds,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_dropoff_timestamp(self, video_id: str) -> DropOffResponse:
        events = (
            self.db.query(VideoEvent.position_seconds)
            .filter(VideoEvent.video_id == video_id, VideoEvent.event_type.in_([EventType.pause, EventType.seek]))
            .all()
        )
        if not events:
            return DropOffResponse(video_id=video_id, dropoff_timestamp_seconds=0, exit_frequency=0)

        buckets = [(pos[0] // 10) * 10 for pos in events]
        most_common_bucket, frequency = Counter(buckets).most_common(1)[0]
        return DropOffResponse(video_id=video_id, dropoff_timestamp_seconds=most_common_bucket, exit_frequency=frequency)

    def get_popular_videos(self, limit: int = 10) -> List[PopularVideoResponse]:
        play_counts = dict(
            self.db.query(VideoEvent.video_id, func.count(VideoEvent.id))
            .filter(VideoEvent.event_type == EventType.play)
            .group_by(VideoEvent.video_id).all()
        )
        avg_watch = dict(
            self.db.query(VideoEvent.video_id, func.avg(VideoEvent.position_seconds))
            .filter(VideoEvent.event_type == EventType.pause)
            .group_by(VideoEvent.video_id).all()
        )
        complete_counts = dict(
            self.db.query(VideoEvent.video_id, func.count(func.distinct(VideoEvent.user_id)))
            .filter(VideoEvent.event_type == EventType.complete)
            .group_by(VideoEvent.video_id).all()
        )
        unique_viewers = dict(
            self.db.query(VideoEvent.video_id, func.count(func.distinct(VideoEvent.user_id)))
            .filter(VideoEvent.event_type == EventType.play)
            .group_by(VideoEvent.video_id).all()
        )

        results = []
        for video_id, total_views in sorted(play_counts.items(), key=lambda x: -x[1])[:limit]:
            viewers = unique_viewers.get(video_id, 0)
            completions = complete_counts.get(video_id, 0)
            completion_rate = round(completions / viewers, 4) if viewers > 0 else 0.0
            results.append(PopularVideoResponse(
                video_id=video_id, total_views=total_views,
                average_watch_seconds=round(float(avg_watch.get(video_id, 0)), 2),
                completion_rate=completion_rate,
            ))
        return results
