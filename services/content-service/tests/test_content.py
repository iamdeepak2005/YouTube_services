from unittest.mock import patch
from app.models.playlist import Playlist
from app.models.video import Video


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def _seed_playlist(db_session):
    playlist = Playlist(
        youtube_playlist_id="PL_test123",
        title="Test Playlist",
        description="Test description",
    )
    db_session.add(playlist)
    db_session.flush()

    for i in range(3):
        db_session.add(Video(
            youtube_video_id=f"vid_{i}",
            playlist_id=playlist.id,
            title=f"Video {i}",
            thumbnail=f"https://img.youtube.com/{i}.jpg",
            duration=300 + i * 60,
            position=i,
        ))
    db_session.commit()
    return playlist


def test_get_playlist_cached(client, db_session):
    _seed_playlist(db_session)
    resp = client.get("/playlist/PL_test123")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Test Playlist"
    assert len(data["videos"]) == 3


@patch("app.services.content_service.fetch_playlist_from_youtube", return_value=None)
def test_get_playlist_not_found(mock_fetch, client):
    resp = client.get("/playlist/nonexistent")
    assert resp.status_code == 404


def test_get_video_metadata(client, db_session):
    _seed_playlist(db_session)
    resp = client.get("/video/metadata/vid_0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["current"]["youtube_video_id"] == "vid_0"
    assert data["next"]["youtube_video_id"] == "vid_1"


def test_get_video_metadata_last_video(client, db_session):
    _seed_playlist(db_session)
    resp = client.get("/video/metadata/vid_2")
    assert resp.status_code == 200
    assert resp.json()["next"] is None


def test_get_video_metadata_not_found(client):
    resp = client.get("/video/metadata/nonexistent")
    assert resp.status_code == 404


def test_get_next_video(client, db_session):
    _seed_playlist(db_session)
    resp = client.get("/video/next/vid_0")
    assert resp.status_code == 200
    assert resp.json()["next"]["youtube_video_id"] == "vid_1"


def test_get_next_video_last(client, db_session):
    _seed_playlist(db_session)
    resp = client.get("/video/next/vid_2")
    assert resp.status_code == 200
    assert resp.json()["next"] is None
