from typing import List
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_video_duration(youtube_video_id: str) -> int:
    url = f"{settings.content_service_url}/video/metadata/{youtube_video_id}"
    try:
        response = httpx.get(url, timeout=5.0)
        if response.status_code == 200:
            return response.json().get("current", {}).get("duration", 0)
    except Exception as exc:
        logger.warning("Could not fetch video duration: %s", exc)
    return 0


def get_playlist_video_ids(youtube_playlist_id: str) -> List[str]:
    url = f"{settings.content_service_url}/playlist/{youtube_playlist_id}"
    try:
        response = httpx.get(url, timeout=10.0)
        if response.status_code == 200:
            return [v["youtube_video_id"] for v in response.json().get("videos", [])]
    except Exception as exc:
        logger.warning("Could not fetch playlist: %s", exc)
    return []
