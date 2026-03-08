from fastapi import APIRouter, Depends, Request, status, BackgroundTasks
import httpx
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.config import settings
from app.controllers.progress_controller import ProgressController
from app.schemas.progress import (
    CourseCompletionResponse, CourseProgressResponse,
    ProgressResponse, ProgressUpdateRequest, ResumeResponse,
)

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["Progress"])


async def send_analytics_event_background(payload: ProgressUpdateRequest, completed: bool):
    url = f"{getattr(settings, 'analytics_service_url', 'http://analytics-service:8004')}/video/event"
    event_type = payload.event_type or ("complete" if completed else "play")
    data = {
        "user_id": payload.user_id,
        "video_id": payload.video_id,
        "event_type": event_type,
        "position_seconds": payload.watched_seconds
    }
    
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(url, json=data)
    except Exception:
        pass  # Silently fail background analytics so it doesn't interrupt progress saving

@router.post("/video/progress", response_model=ProgressResponse, status_code=status.HTTP_200_OK)
@limiter.limit("100/minute")
def update_progress(request: Request, payload: ProgressUpdateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    result = ProgressController(db).update_progress(payload)
    background_tasks.add_task(send_analytics_event_background, payload, result.completed)
    return result


@router.get("/video/resume/{video_id}", response_model=ResumeResponse)
@limiter.limit("100/minute")
def resume_video(request: Request, video_id: str, user_id: str, db: Session = Depends(get_db)):
    return ProgressController(db).resume_video(video_id, user_id)


@router.get("/course/{playlist_id}/progress", response_model=CourseProgressResponse)
@limiter.limit("100/minute")
def course_progress(request: Request, playlist_id: str, user_id: str, db: Session = Depends(get_db)):
    return ProgressController(db).course_progress(playlist_id, user_id)


@router.get("/course/{playlist_id}/completion", response_model=CourseCompletionResponse)
@limiter.limit("100/minute")
def course_completion(request: Request, playlist_id: str, user_id: str, db: Session = Depends(get_db)):
    return ProgressController(db).course_completion(playlist_id, user_id)
