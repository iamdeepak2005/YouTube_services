from unittest.mock import patch


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@patch("app.services.recommendation_engine.fetch_playlist_videos", return_value=[])
def test_recommend_playlist_not_found(mock_playlist, client):
    resp = client.get("/recommend/PL_missing?user_id=u1")
    assert resp.status_code == 404


@patch("app.services.recommendation_engine.fetch_playlist_videos", return_value=[{"youtube_video_id": "v1", "title": "Vid 1", "duration": 600}])
@patch("app.services.recommendation_engine.fetch_resume_timestamp", return_value=30)
@patch("app.services.recommendation_engine.fetch_course_progress", return_value={"completed_videos": 0})
def test_recommend_resume_unfinished(mock_progress, mock_resume, mock_playlist, client):
    resp = client.get("/recommend/v1?user_id=u1")
    assert resp.status_code == 200
    assert resp.json()["reason"] == "resume_unfinished"
    assert resp.json()["video"]["youtube_video_id"] == "v1"


@patch("app.services.recommendation_engine.fetch_playlist_videos", return_value=[
    {"youtube_video_id": "v1", "title": "Vid 1", "duration": 600},
    {"youtube_video_id": "v2", "title": "Vid 2", "duration": 600}
])
@patch("app.services.recommendation_engine.fetch_course_progress", return_value={"completed_videos": 1})
@patch("app.services.recommendation_engine.fetch_resume_timestamp", return_value=0)
def test_recommend_next_in_sequence(mock_resume, mock_progress, mock_playlist, client):
    resp = client.get("/recommend/PL1?user_id=u1")
    assert resp.status_code == 200
    assert resp.json()["reason"] == "next_in_sequence"
    assert resp.json()["video"]["youtube_video_id"] == "v2"


@patch("app.services.recommendation_engine.fetch_playlist_videos", return_value=[{"youtube_video_id": "v1", "title": "Vid 1", "duration": 600}])
@patch("app.services.recommendation_engine.fetch_course_progress", return_value={"completed_videos": 1})
@patch("app.services.recommendation_engine.fetch_resume_timestamp", return_value=0)
@patch("app.services.recommendation_engine.fetch_popular_videos", return_value=[{"video_id": "pop1", "title": "Pop 1"}])
def test_recommend_popular_fallback(mock_pop, mock_resume, mock_progress, mock_playlist, client):
    resp = client.get("/recommend/PL1?user_id=u1")
    assert resp.status_code == 200
    assert resp.json()["reason"] == "popular_video"
