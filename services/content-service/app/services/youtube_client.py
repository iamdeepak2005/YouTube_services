import re
import logging
from typing import Any, Dict, List, Optional, Tuple

from googleapiclient.discovery import build

from app.core.config import settings

logger = logging.getLogger(__name__)


def _parse_duration(iso_duration: str) -> int:
    pattern = re.compile(r"PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?")
    match = pattern.match(iso_duration)
    if not match:
        return 0
    parts = match.groupdict(default="0")
    return int(parts["hours"]) * 3600 + int(parts["minutes"]) * 60 + int(parts["seconds"])


def fetch_playlist_from_youtube(youtube_playlist_id: str) -> Dict[str, Any]:
    if not settings.youtube_api_key:
        raise ValueError("YOUTUBE_API_KEY is not set.")

    youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)

    playlist_response = youtube.playlists().list(part="snippet", id=youtube_playlist_id).execute()
    playlist_items = playlist_response.get("items", [])
    if not playlist_items:
        raise ValueError(f"Playlist '{youtube_playlist_id}' not found on YouTube.")

    snippet = playlist_items[0]["snippet"]
    playlist_title = snippet.get("title", "Untitled Playlist")
    playlist_description = snippet.get("description", "")

    video_ids_ordered: List[Tuple[str, int]] = []
    next_page_token: Optional[str] = None

    while True:
        params: Dict[str, Any] = {
            "part": "snippet,contentDetails",
            "playlistId": youtube_playlist_id,
            "maxResults": 50,
        }
        if next_page_token:
            params["pageToken"] = next_page_token

        items_response = youtube.playlistItems().list(**params).execute()
        for item in items_response.get("items", []):
            vid_id = item["contentDetails"]["videoId"]
            position = item["snippet"]["position"]
            video_ids_ordered.append((vid_id, position))

        next_page_token = items_response.get("nextPageToken")
        if not next_page_token:
            break

    video_details: Dict[str, dict] = {}
    for batch_start in range(0, len(video_ids_ordered), 50):
        batch_ids = [v[0] for v in video_ids_ordered[batch_start:batch_start + 50]]
        detail_response = youtube.videos().list(part="snippet,contentDetails", id=",".join(batch_ids)).execute()
        for item in detail_response.get("items", []):
            vid_id = item["id"]
            thumbnails = item["snippet"].get("thumbnails", {})
            thumbnail_url = thumbnails.get("high", {}).get("url") or thumbnails.get("default", {}).get("url") or ""
            video_details[vid_id] = {
                "title": item["snippet"].get("title", ""),
                "thumbnail": thumbnail_url,
                "duration": _parse_duration(item["contentDetails"].get("duration", "PT0S")),
            }

    videos = []
    for youtube_video_id, position in video_ids_ordered:
        details = video_details.get(youtube_video_id, {})
        videos.append({
            "youtube_video_id": youtube_video_id,
            "title": details.get("title", "Unknown"),
            "thumbnail": details.get("thumbnail", ""),
            "duration": details.get("duration", 0),
            "position": position,
        })

    return {"title": playlist_title, "description": playlist_description, "videos": videos}
