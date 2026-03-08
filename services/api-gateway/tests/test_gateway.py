from unittest.mock import patch, AsyncMock
import httpx


def test_service_map(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "routes" in data
    assert "/users/*" in data["routes"]
    assert "/playlist/*" in data["routes"]


def test_health_gateway_up(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["gateway"] == "healthy"
    assert "services" in data


@patch("app.services.proxy_service._http_client")
def test_proxy_users_forward(mock_client, client):
    mock_response = httpx.Response(
        status_code=200,
        json={"id": "user-1", "email": "test@test.com"},
        request=httpx.Request("GET", "http://test"),
    )
    mock_client.request = AsyncMock(return_value=mock_response)

    resp = client.get("/users/user-1")
    assert resp.status_code == 200


@patch("app.services.proxy_service._http_client")
def test_proxy_playlist_forward(mock_client, client):
    mock_response = httpx.Response(
        status_code=200,
        json={"id": "pl-1", "title": "Test"},
        request=httpx.Request("GET", "http://test"),
    )
    mock_client.request = AsyncMock(return_value=mock_response)

    resp = client.get("/playlist/PL_test123")
    assert resp.status_code == 200


@patch("app.services.proxy_service._http_client")
def test_proxy_service_unavailable(mock_client, client):
    mock_client.request = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

    resp = client.get("/users/user-1")
    assert resp.status_code == 503


@patch("app.services.proxy_service._http_client")
def test_proxy_service_timeout(mock_client, client):
    mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

    resp = client.get("/analytics/popular")
    assert resp.status_code == 504
