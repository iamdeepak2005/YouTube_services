from typing import Tuple, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.pagination import PaginatedResponse, PaginationParams
from app.repositories.content_repository import ContentRepository
from app.schemas.content import PlaylistResponse, VideoMetadataResponse
from app.services.content_service import ContentService


class ContentController:

    def __init__(self, db: Session):
        self.service = ContentService(db)

    def get_playlist(self, playlist_id: str):
        playlist = self.service.get_full_playlist(playlist_id)
        if not playlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Playlist '{playlist_id}' not found.",
            )
        return playlist

    def list_playlists(self, pagination: PaginationParams):
        playlists, total = self.service.list_all_playlists(
            offset=pagination.offset, limit=pagination.page_size
        )
        return PaginatedResponse[PlaylistResponse].create(
            items=playlists, total=total,
            page=pagination.page, page_size=pagination.page_size,
        )

    def get_video_metadata(self, video_id: str):
        metadata = self.service.get_video_metadata(video_id)
        if not metadata["current"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video '{video_id}' not found.",
            )
        return metadata

    def get_next_video(self, video_id: str):
        metadata = self.service.get_video_metadata(video_id)
        if not metadata["current"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video '{video_id}' not found.",
            )
        return {"next": metadata["next"]}
