from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.video_progress import VideoProgress
from app.models.learning_session import LearningSession


class ProgressRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_progress(self, user_id: str, video_id: str) -> Optional[VideoProgress]:
        return (
            self.db.query(VideoProgress)
            .filter(VideoProgress.user_id == user_id, VideoProgress.video_id == video_id)
            .first()
        )

    def upsert_progress(self, user_id: str, video_id: str, watched_seconds: int, completed: bool) -> VideoProgress:
        record = self.get_progress(user_id, video_id)
        if record:
            record.watched_seconds = watched_seconds
            record.completed = completed
            record.updated_at = datetime.now(timezone.utc)
        else:
            record = VideoProgress(
                user_id=user_id, video_id=video_id,
                watched_seconds=watched_seconds, completed=completed,
            )
            self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_completed_video_ids_for_user(self, user_id: str) -> List[str]:
        rows = (
            self.db.query(VideoProgress.video_id)
            .filter(VideoProgress.user_id == user_id, VideoProgress.completed.is_(True))
            .all()
        )
        return [r.video_id for r in rows]

    def get_user_progress_for_videos(self, user_id: str, video_ids: List[str]) -> List[VideoProgress]:
        return (
            self.db.query(VideoProgress)
            .filter(VideoProgress.user_id == user_id, VideoProgress.video_id.in_(video_ids))
            .all()
        )

    def get_incomplete_video_in_playlist(self, user_id: str, video_ids: List[str]) -> Optional[VideoProgress]:
        return (
            self.db.query(VideoProgress)
            .filter(
                VideoProgress.user_id == user_id,
                VideoProgress.video_id.in_(video_ids),
                VideoProgress.completed.is_(False),
                VideoProgress.watched_seconds > 0,
            )
            .order_by(VideoProgress.updated_at.desc())
            .first()
        )

    def create_session(self, user_id: str) -> LearningSession:
        session = LearningSession(user_id=user_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
