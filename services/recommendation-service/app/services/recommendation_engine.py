import logging

from app.services.service_clients import fetch_course_progress, fetch_playlist_videos, fetch_popular_videos, fetch_resume_timestamp

logger = logging.getLogger(__name__)


def build_recommendation(youtube_playlist_id: str, user_id: str) -> dict:
    videos = fetch_playlist_videos(youtube_playlist_id)

    if not videos:
        return {"reason": "playlist_not_found", "video": None, "resume_at_seconds": 0}

    progress = fetch_course_progress(youtube_playlist_id, user_id)
    completed_count = progress.get("completed_videos", 0)

    for video in videos:
        yt_vid_id = video["youtube_video_id"]
        resume_at = fetch_resume_timestamp(yt_vid_id, user_id)
        if 0 < resume_at < video.get("duration", 1):
            return {"reason": "resume_unfinished", "video": video, "resume_at_seconds": resume_at}

    next_index = completed_count
    if next_index < len(videos):
        return {"reason": "next_in_sequence", "video": videos[next_index], "resume_at_seconds": 0}

    popular = fetch_popular_videos(limit=1)
    if popular:
        popular_vid_id = popular[0]["video_id"]
        matching = next((v for v in videos if v["youtube_video_id"] == popular_vid_id), popular[0])
        return {"reason": "popular_video", "video": matching, "resume_at_seconds": 0}

    return {"reason": "no_recommendation", "video": None, "resume_at_seconds": 0}
