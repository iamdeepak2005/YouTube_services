from typing import List
from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.controllers.analytics_controller import AnalyticsController
from app.schemas.analytics import DropOffResponse, PopularVideoResponse, VideoEventRequest, VideoEventResponse

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["Analytics"])


@router.post("/video/event", response_model=VideoEventResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
def record_event(request: Request, payload: VideoEventRequest, db: Session = Depends(get_db)):
    return AnalyticsController(db).record_event(payload)


@router.get("/analytics/dropoff/{video_id}", response_model=DropOffResponse)
@limiter.limit("100/minute")
def get_dropoff(request: Request, video_id: str, db: Session = Depends(get_db)):
    return AnalyticsController(db).get_dropoff(video_id)


@router.get("/analytics/popular", response_model=List[PopularVideoResponse])
@limiter.limit("100/minute")
def get_popular_videos(request: Request, limit: int = 10, db: Session = Depends(get_db)):
    return AnalyticsController(db).get_popular_videos(limit)
