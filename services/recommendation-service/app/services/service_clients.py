from typing import List
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


def fetch_playlist_videos(youtube_playlist_id: str) -> List[dict]:
    url = f"{settings.content_service_url}/playlist/{youtube_playlist_id}"
    try:
        resp = httpx.get(url, timeout=10.0)
        if resp.status_code == 200:
            return resp.json().get("videos", [])
    except Exception as exc:
        logger.warning("Content service call failed: %s", exc)
    return []


def fetch_course_progress(youtube_playlist_id: str, user_id: str) -> dict:
    url = f"{settings.progress_service_url}/course/{youtube_playlist_id}/progress?user_id={user_id}"
    try:
        resp = httpx.get(url, timeout=5.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception as exc:
        logger.warning("Progress service call failed: %s", exc)
    return {}


def fetch_resume_timestamp(video_id: str, user_id: str) -> int:
    url = f"{settings.progress_service_url}/video/resume/{video_id}?user_id={user_id}"
    try:
        resp = httpx.get(url, timeout=5.0)
        if resp.status_code == 200:
            return resp.json().get("resume_at_seconds", 0)
    except Exception as exc:
        logger.warning("Progress service resume call failed: %s", exc)
    return 0


def fetch_popular_videos(limit: int = 5) -> List[dict]:
    url = f"{settings.analytics_service_url}/analytics/popular?limit={limit}"
    try:
        resp = httpx.get(url, timeout=5.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception as exc:
        logger.warning("Analytics service call failed: %s", exc)
    return []
