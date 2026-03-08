def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_create_user(client):
    resp = client.post("/users", json={"email": "test@example.com"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data


def test_create_user_duplicate_email(client):
    client.post("/users", json={"email": "dup@example.com"})
    resp = client.post("/users", json={"email": "dup@example.com"})
    assert resp.status_code == 409


def test_create_user_invalid_email(client):
    resp = client.post("/users", json={"email": "not-an-email"})
    assert resp.status_code == 422


def test_get_user(client):
    create_resp = client.post("/users", json={"email": "get@example.com"})
    user_id = create_resp.json()["id"]
    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "get@example.com"


def test_get_user_not_found(client):
    resp = client.get("/users/nonexistent-id")
    assert resp.status_code == 404


def test_list_users_empty(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_users_paginated(client):
    for i in range(5):
        client.post("/users", json={"email": f"user{i}@example.com"})

    resp = client.get("/users?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2
    assert data["total_pages"] == 3
