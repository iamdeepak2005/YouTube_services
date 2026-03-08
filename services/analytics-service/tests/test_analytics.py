def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_record_play_event(client):
    resp = client.post("/video/event", json={
        "user_id": "user-1", "video_id": "vid-1",
        "event_type": "play", "position_seconds": 0,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["event_type"] == "play"
    assert "id" in data


def test_record_pause_event(client):
    resp = client.post("/video/event", json={
        "user_id": "user-1", "video_id": "vid-1",
        "event_type": "pause", "position_seconds": 150,
    })
    assert resp.status_code == 201
    assert resp.json()["position_seconds"] == 150


def test_record_invalid_event_type(client):
    resp = client.post("/video/event", json={
        "user_id": "user-1", "video_id": "vid-1",
        "event_type": "invalid", "position_seconds": 0,
    })
    assert resp.status_code == 422


def test_dropoff_no_events(client):
    resp = client.get("/analytics/dropoff/vid-1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["dropoff_timestamp_seconds"] == 0
    assert data["exit_frequency"] == 0


def test_dropoff_with_events(client):
    for pos in [120, 125, 130, 200, 120, 128]:
        client.post("/video/event", json={
            "user_id": "user-1", "video_id": "vid-1",
            "event_type": "pause", "position_seconds": pos,
        })
    resp = client.get("/analytics/dropoff/vid-1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["dropoff_timestamp_seconds"] == 120
    assert data["exit_frequency"] >= 4


def test_popular_videos_empty(client):
    resp = client.get("/analytics/popular")
    assert resp.status_code == 200
    assert resp.json() == []


def test_popular_videos_with_data(client):
    for i in range(5):
        client.post("/video/event", json={
            "user_id": f"user-{i}", "video_id": "vid-1",
            "event_type": "play", "position_seconds": 0,
        })
    for i in range(3):
        client.post("/video/event", json={
            "user_id": f"user-{i}", "video_id": "vid-2",
            "event_type": "play", "position_seconds": 0,
        })

    resp = client.get("/analytics/popular?limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["video_id"] == "vid-1"
    assert data[0]["total_views"] == 5


def test_record_complete_event(client):
    client.post("/video/event", json={
        "user_id": "user-1", "video_id": "vid-1",
        "event_type": "play", "position_seconds": 0,
    })
    resp = client.post("/video/event", json={
        "user_id": "user-1", "video_id": "vid-1",
        "event_type": "complete", "position_seconds": 600,
    })
    assert resp.status_code == 201
    assert resp.json()["event_type"] == "complete"
