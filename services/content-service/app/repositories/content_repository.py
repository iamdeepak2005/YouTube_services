from typing import Dict, List, Optional
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.playlist import Playlist
from app.models.video import Video

logger = logging.getLogger(__name__)


class ContentRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_playlist_by_youtube_id(self, youtube_playlist_id: str) -> Optional[Playlist]:
        return (
            self.db.query(Playlist)
            .filter(Playlist.youtube_playlist_id == youtube_playlist_id)
            .first()
        )

    def create_or_update_playlist(
        self,
        youtube_playlist_id: str,
        title: str,
        description: str,
        videos_data: List[dict],
    ) -> Playlist:
        playlist = self.get_playlist_by_youtube_id(youtube_playlist_id)

        if playlist:
            playlist.title = title
            playlist.description = description
            playlist.last_synced_at = datetime.now(timezone.utc)
        else:
            playlist = Playlist(
                youtube_playlist_id=youtube_playlist_id,
                title=title,
                description=description,
            )
            self.db.add(playlist)
            self.db.flush()

        existing_videos: Dict[str, Video] = {v.youtube_video_id: v for v in playlist.videos}
        incoming_ids = {v["youtube_video_id"] for v in videos_data}

        for vid_id, video in list(existing_videos.items()):
            if vid_id not in incoming_ids:
                self.db.delete(video)

        for vdata in videos_data:
            if vdata["youtube_video_id"] in existing_videos:
                video = existing_videos[vdata["youtube_video_id"]]
                video.title = vdata["title"]
                video.thumbnail = vdata["thumbnail"]
                video.duration = vdata["duration"]
                video.position = vdata["position"]
            else:
                video = Video(
                    youtube_video_id=vdata["youtube_video_id"],
                    playlist_id=playlist.id,
                    title=vdata["title"],
                    thumbnail=vdata["thumbnail"],
                    duration=vdata["duration"],
                    position=vdata["position"],
                )
                self.db.add(video)

        self.db.commit()
        self.db.refresh(playlist)
        return playlist

    def get_video_by_youtube_id(self, youtube_video_id: str) -> Optional[Video]:
        return self.db.query(Video).filter(Video.youtube_video_id == youtube_video_id).first()

    def get_videos_by_playlist(self, playlist_id: str) -> List[Video]:
        return (
            self.db.query(Video)
            .filter(Video.playlist_id == playlist_id)
            .order_by(Video.position)
            .all()
        )

    def get_all_playlists(self, offset: int = 0, limit: int = 20) -> List[Playlist]:
        return self.db.query(Playlist).offset(offset).limit(limit).all()

    def count_playlists(self) -> int:
        return self.db.query(Playlist).count()
