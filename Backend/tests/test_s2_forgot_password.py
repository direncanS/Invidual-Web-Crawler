import hashlib
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from tests.conftest import make_user


@patch("app.services.auth_service.send_reset_email")
def test_forgot_password_existing_email(mock_send, client, db_session):
    user = make_user(db_session, email="forgot@example.com")
    resp = client.post("/auth/forgot-password", json={"email": "forgot@example.com"})
    assert resp.status_code == 200
    mock_send.assert_called_once()
    assert mock_send.call_args[0][0] == "forgot@example.com"


@patch("app.services.auth_service.send_reset_email")
def test_forgot_password_nonexistent_email(mock_send, client, db_session):
    resp = client.post("/auth/forgot-password", json={"email": "ghost@example.com"})
    assert resp.status_code == 200
    mock_send.assert_not_called()


@patch("app.services.auth_service.send_reset_email")
def test_reset_password_success(mock_send, client, db_session):
    user = make_user(db_session, email="reset@example.com", nickname="resetuser")
    client.post("/auth/forgot-password", json={"email": "reset@example.com"})
    raw_token = mock_send.call_args[0][1]

    resp = client.post("/auth/reset-password", json={
        "token": raw_token,
        "new_password": "NewPass123!",
    })
    assert resp.status_code == 200

    login_resp = client.post("/auth/login", json={
        "email_or_nickname": "reset@example.com",
        "password": "NewPass123!",
    })
    assert login_resp.status_code == 200


@patch("app.services.auth_service.send_reset_email")
def test_reset_password_old_password_fails(mock_send, client, db_session):
    user = make_user(db_session, email="oldpw@example.com", nickname="oldpwuser")
    client.post("/auth/forgot-password", json={"email": "oldpw@example.com"})
    raw_token = mock_send.call_args[0][1]

    client.post("/auth/reset-password", json={
        "token": raw_token,
        "new_password": "NewPass123!",
    })

    login_resp = client.post("/auth/login", json={
        "email_or_nickname": "oldpw@example.com",
        "password": "Test1234!",
    })
    assert login_resp.status_code == 401
    assert login_resp.json()["detail"]["error"]["code"] == "invalid_credentials"


@patch("app.services.auth_service.send_reset_email")
def test_reset_password_token_reuse(mock_send, client, db_session):
    user = make_user(db_session, email="reuse@example.com", nickname="reuseuser")
    client.post("/auth/forgot-password", json={"email": "reuse@example.com"})
    raw_token = mock_send.call_args[0][1]

    client.post("/auth/reset-password", json={
        "token": raw_token,
        "new_password": "NewPass123!",
    })

    resp = client.post("/auth/reset-password", json={
        "token": raw_token,
        "new_password": "AnotherPw1!",
    })
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"]["code"] == "reset_token_used"


def test_reset_password_invalid_token(client):
    resp = client.post("/auth/reset-password", json={
        "token": "totally-invalid-token",
        "new_password": "NewPass123!",
    })
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"]["code"] == "reset_token_invalid"


@patch("app.services.auth_service.send_reset_email")
def test_reset_password_expired_token(mock_send, client, db_session):
    from app.models.user import PasswordResetToken

    user = make_user(db_session, email="expired@example.com", nickname="expireduser")
    client.post("/auth/forgot-password", json={"email": "expired@example.com"})
    raw_token = mock_send.call_args[0][1]

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    reset_row = db_session.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()
    reset_row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.flush()

    resp = client.post("/auth/reset-password", json={
        "token": raw_token,
        "new_password": "NewPass123!",
    })
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"]["code"] == "reset_token_expired"


def test_reset_password_weak_password(client):
    resp = client.post("/auth/reset-password", json={
        "token": "some-token",
        "new_password": "short",
    })
    assert resp.status_code == 422
