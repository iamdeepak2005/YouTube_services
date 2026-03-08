from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.progress_repository import ProgressRepository
from app.services.content_client import get_video_duration, get_playlist_video_ids
from app.schemas.progress import CourseCompletionResponse, CourseProgressResponse, ResumeResponse


class ProgressService:

    def __init__(self, db: Session):
        self.repo = ProgressRepository(db)

    def update_progress(self, user_id: str, video_id: str, watched_seconds: int):
        duration = get_video_duration(video_id)
        completed = watched_seconds >= settings.completion_threshold * duration if duration > 0 else False
        return self.repo.upsert_progress(
            user_id=user_id, video_id=video_id,
            watched_seconds=watched_seconds, completed=completed,
        )

    def get_resume_timestamp(self, user_id: str, video_id: str) -> ResumeResponse:
        record = self.repo.get_progress(user_id, video_id)
        resume_ts = 0
        if record and not record.completed:
            resume_ts = record.watched_seconds
        
        return ResumeResponse(
            video_id=video_id,
            resume_at_seconds=resume_ts,
        )

    def get_course_progress(self, playlist_id: str, user_id: str) -> Optional[CourseProgressResponse]:
        video_ids = get_playlist_video_ids(playlist_id)
        if not video_ids:
            return None
        progress_records = self.repo.get_user_progress_for_videos(user_id, video_ids)
        completed = sum(1 for r in progress_records if r.completed)
        total = len(video_ids)
        return CourseProgressResponse(
            playlist_id=playlist_id, user_id=user_id,
            total_videos=total, completed_videos=completed,
            remaining_videos=total - completed,
            progress_percent=round((completed / total) * 100, 2) if total > 0 else 0.0,
        )

    def get_course_completion(self, playlist_id: str, user_id: str) -> Optional[CourseCompletionResponse]:
        video_ids = get_playlist_video_ids(playlist_id)
        if not video_ids:
            return None
        progress_records = self.repo.get_user_progress_for_videos(user_id, video_ids)
        completed_count = sum(1 for r in progress_records if r.completed)
        total = len(video_ids)
        pct = round((completed_count / total) * 100, 2) if total > 0 else 0.0
        return CourseCompletionResponse(
            playlist_id=playlist_id, user_id=user_id,
            completion_percentage=pct, course_completed=pct >= 90.0,
        )
