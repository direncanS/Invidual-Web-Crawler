from tests.conftest import make_user


def test_register_success(client, db_session):
    resp = client.post("/auth/register", json={
        "nickname": "newuser",
        "email": "new@example.com",
        "password": "Test1234!",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["nickname"] == "newuser"
    assert body["email"] == "new@example.com"


def test_register_duplicate_nickname(client, db_session):
    make_user(db_session, nickname="taken")
    resp = client.post("/auth/register", json={
        "nickname": "taken",
        "email": "unique@example.com",
        "password": "Test1234!",
    })
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"]["code"] == "nickname_already_exists"


def test_register_duplicate_email(client, db_session):
    make_user(db_session, email="dup@example.com")
    resp = client.post("/auth/register", json={
        "nickname": "uniquenick",
        "email": "dup@example.com",
        "password": "Test1234!",
    })
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"]["code"] == "email_already_exists"


def test_register_invalid_email(client):
    resp = client.post("/auth/register", json={
        "nickname": "someone",
        "email": "not-an-email",
        "password": "Test1234!",
    })
    assert resp.status_code == 422


def test_register_weak_password(client):
    resp = client.post("/auth/register", json={
        "nickname": "someone",
        "email": "ok@example.com",
        "password": "short",
    })
    assert resp.status_code == 422


def test_register_short_nickname(client):
    resp = client.post("/auth/register", json={
        "nickname": "ab",
        "email": "ok@example.com",
        "password": "Test1234!",
    })
    assert resp.status_code == 422


def test_login_with_email(client, db_session):
    make_user(db_session, email="login@example.com", nickname="loginuser")
    resp = client.post("/auth/login", json={
        "email_or_nickname": "login@example.com",
        "password": "Test1234!",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_with_nickname(client, db_session):
    make_user(db_session, nickname="nicklogin", email="nicklogin@example.com")
    resp = client.post("/auth/login", json={
        "email_or_nickname": "nicklogin",
        "password": "Test1234!",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client, db_session):
    make_user(db_session, email="wrong@example.com", nickname="wrongpw")
    resp = client.post("/auth/login", json={
        "email_or_nickname": "wrong@example.com",
        "password": "WrongPass1!",
    })
    assert resp.status_code == 401
    assert resp.json()["detail"]["error"]["code"] == "invalid_credentials"


def test_login_nonexistent_user(client):
    resp = client.post("/auth/login", json={
        "email_or_nickname": "ghost@example.com",
        "password": "Test1234!",
    })
    assert resp.status_code == 401
    assert resp.json()["detail"]["error"]["code"] == "invalid_credentials"
