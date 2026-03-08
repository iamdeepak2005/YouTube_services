from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.pagination import PaginatedResponse, PaginationParams
from app.controllers.content_controller import ContentController
from app.schemas.content import PlaylistResponse, VideoMetadataResponse

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["Content"])


@router.get("/playlist/all", response_model=PaginatedResponse[PlaylistResponse])
@limiter.limit("100/minute")
def list_playlists(request: Request, pagination: PaginationParams = Depends(), db: Session = Depends(get_db)):
    return ContentController(db).list_playlists(pagination)


@router.get("/playlist/{playlist_id}", response_model=PlaylistResponse)
@limiter.limit("100/minute")
def get_playlist(request: Request, playlist_id: str, db: Session = Depends(get_db)):
    return ContentController(db).get_playlist(playlist_id)


@router.get("/video/metadata/{video_id}", response_model=VideoMetadataResponse)
@limiter.limit("100/minute")
def get_video_metadata(request: Request, video_id: str, db: Session = Depends(get_db)):
    return ContentController(db).get_video_metadata(video_id)


@router.get("/video/next/{video_id}")
@limiter.limit("100/minute")
def get_next_video(request: Request, video_id: str, db: Session = Depends(get_db)):
    return ContentController(db).get_next_video(video_id)
