from typing import Dict, List, Optional, Tuple
import logging

from sqlalchemy.orm import Session

from app.models.playlist import Playlist
from app.repositories.content_repository import ContentRepository
from app.services.youtube_client import fetch_playlist_from_youtube

logger = logging.getLogger(__name__)


class ContentService:

    def __init__(self, db: Session):
        self.repo = ContentRepository(db)

    def sync_playlist(self, youtube_playlist_id: str) -> Optional[Playlist]:
        data = fetch_playlist_from_youtube(youtube_playlist_id)
        if not data:
            return None

        return self.repo.create_or_update_playlist(
            youtube_playlist_id=youtube_playlist_id,
            title=data["title"],
            description=data["description"],
            videos_data=data["videos"],
        )

    def get_full_playlist(self, youtube_playlist_id: str) -> Optional[Playlist]:
        playlist = self.repo.get_playlist_by_youtube_id(youtube_playlist_id)
        if not playlist:
            playlist = self.sync_playlist(youtube_playlist_id)
        return playlist

    def get_video_metadata(self, youtube_video_id: str) -> Dict[str, Optional[dict]]:
        video = self.repo.get_video_by_youtube_id(youtube_video_id)
        if not video:
            return {"current": None, "next": None}

        playlist_videos = self.repo.get_videos_by_playlist(video.playlist_id)
        current_idx = -1
        for i, v in enumerate(playlist_videos):
            if v.youtube_video_id == youtube_video_id:
                current_idx = i
                break

        next_video = None
        if current_idx != -1 and current_idx + 1 < len(playlist_videos):
            next_v = playlist_videos[current_idx + 1]
            next_video = {
                "youtube_video_id": next_v.youtube_video_id,
                "title": next_v.title,
                "thumbnail": next_v.thumbnail,
                "position": next_v.position,
            }

        return {
            "current": {
                "youtube_video_id": video.youtube_video_id,
                "title": video.title,
                "thumbnail": video.thumbnail,
                "duration": video.duration,
                "position": video.position,
                "embed_url": f"https://www.youtube.com/embed/{video.youtube_video_id}",
                "iframe_snippet": f'<iframe width="100%" height="100%" src="https://www.youtube.com/embed/{video.youtube_video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
            },
            "next": next_video,
        }

    def list_all_playlists(self, offset: int = 0, limit: int = 20) -> Tuple[List[Playlist], int]:
        playlists = self.repo.get_all_playlists(offset=offset, limit=limit)
        total = self.repo.count_playlists()
        return playlists, total
