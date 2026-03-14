from sqlalchemy import text

from tests.conftest import make_user, auth_header
from app.core.security import decode_access_token


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_openapi_endpoint(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "paths" in resp.json()


def test_db_session_works(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_user_fixture_creates_user(user):
    assert user.id is not None
    assert user.nickname is not None
    assert user.email is not None


def test_auth_header_produces_valid_token(user):
    headers = auth_header(user.id)
    token = headers["Authorization"].replace("Bearer ", "")
    decoded_id = decode_access_token(token)
    assert decoded_id == str(user.id)
