import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.repositories.content_repository import ContentRepository
from app.services.youtube_client import fetch_playlist_from_youtube

logger = logging.getLogger(__name__)


def sync_all_playlists() -> None:
    logger.info("Playlist sync started at %s", datetime.now(timezone.utc).isoformat())
    db = SessionLocal()
    try:
        repo = ContentRepository(db)
        for playlist in repo.get_all_playlists():
            try:
                data = fetch_playlist_from_youtube(playlist.youtube_playlist_id)
                repo.create_or_update_playlist(
                    youtube_playlist_id=playlist.youtube_playlist_id,
                    title=data["title"],
                    description=data["description"],
                    videos_data=data["videos"],
                )
                logger.info("Synced playlist '%s'", playlist.youtube_playlist_id)
            except Exception as exc:
                logger.error("Failed to sync '%s': %s", playlist.youtube_playlist_id, exc)
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        sync_all_playlists,
        trigger="interval",
        hours=24,
        id="playlist_sync",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    return scheduler
