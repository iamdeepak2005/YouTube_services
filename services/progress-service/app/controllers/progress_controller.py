from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.progress import ProgressUpdateRequest
from app.services.progress_service import ProgressService


class ProgressController:

    def __init__(self, db: Session):
        self.service = ProgressService(db)

    def update_progress(self, payload: ProgressUpdateRequest):
        return self.service.update_progress(
            user_id=payload.user_id, video_id=payload.video_id,
            watched_seconds=payload.watched_seconds,
        )

    def resume_video(self, video_id: str, user_id: str):
        return self.service.get_resume_timestamp(user_id, video_id)

    def course_progress(self, playlist_id: str, user_id: str):
        result = self.service.get_course_progress(playlist_id, user_id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist '{playlist_id}' not found.")
        return result

    def course_completion(self, playlist_id: str, user_id: str):
        result = self.service.get_course_completion(playlist_id, user_id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist '{playlist_id}' not found.")
        return result
