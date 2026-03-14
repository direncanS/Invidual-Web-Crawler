from tests.conftest import make_user, auth_header


def test_get_me_success(client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.get("/me", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == str(user.id)
    assert body["nickname"] == user.nickname
    assert body["email"] == user.email


def test_get_me_no_auth(client):
    resp = client.get("/me")
    assert resp.status_code == 403


def test_get_me_invalid_token(client):
    resp = client.get("/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401
    assert resp.json()["detail"]["error"]["code"] == "invalid_token"


def test_put_me_update_nickname(client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.put("/me", json={"nickname": "newnick"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["nickname"] == "newnick"


def test_put_me_update_email(client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.put("/me", json={"email": "newemail@example.com"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "newemail@example.com"


def test_put_me_update_both(client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.put("/me", json={
        "nickname": "bothnick",
        "email": "both@example.com",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["nickname"] == "bothnick"
    assert resp.json()["email"] == "both@example.com"


def test_put_me_empty_body(client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.put("/me", json={}, headers=headers)
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"]["code"] == "no_fields_to_update"


def test_put_me_duplicate_nickname(client, db_session):
    make_user(db_session, nickname="existing")
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.put("/me", json={"nickname": "existing"}, headers=headers)
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"]["code"] == "nickname_already_exists"


def test_put_me_duplicate_email(client, db_session):
    make_user(db_session, email="taken@example.com")
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.put("/me", json={"email": "taken@example.com"}, headers=headers)
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"]["code"] == "email_already_exists"


def test_put_me_invalid_email(client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.put("/me", json={"email": "not-an-email"}, headers=headers)
    assert resp.status_code == 422


def test_put_me_no_auth(client):
    resp = client.put("/me", json={"nickname": "hacker"})
    assert resp.status_code == 403


def test_register_login_get_me_integration(client, db_session):
    reg_resp = client.post("/auth/register", json={
        "nickname": "integuser",
        "email": "integ@example.com",
        "password": "Test1234!",
    })
    assert reg_resp.status_code == 201

    login_resp = client.post("/auth/login", json={
        "email_or_nickname": "integ@example.com",
        "password": "Test1234!",
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    me_resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["nickname"] == "integuser"
    assert me_resp.json()["email"] == "integ@example.com"
