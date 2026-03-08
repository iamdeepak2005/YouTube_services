import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture(scope="function")
def app():
    return create_app()


@pytest.fixture(scope="function")
def client(app):
    return TestClient(app)
