import os
import uuid
import shutil

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base
from app.main import app
from app.api.deps import get_db
from app.core.security import create_access_token


def _ensure_test_db():
    """Create app_test database if it doesn't exist."""
    admin_url = settings.database_url.rsplit("/", 1)[0] + "/postgres"
    eng = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with eng.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'app_test'")
        ).scalar()
        if not exists:
            conn.execute(text("CREATE DATABASE app_test"))
    eng.dispose()


_ensure_test_db()

engine = create_engine(settings.database_url)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Outer transaction + nested SAVEPOINT. Even code that calls commit gets rolled back."""
    connection = engine.connect()
    outer = connection.begin()
    session = sessionmaker(expire_on_commit=False)(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not sess.in_nested_transaction():
            sess.begin_nested()

    yield session

    session.close()
    outer.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def clean_storage():
    path = "/tmp/test_data"
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    yield
    if os.path.exists(path):
        shutil.rmtree(path)


@pytest.fixture()
def client(db_session):
    def _override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    from httpx import ASGITransport, AsyncClient
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def make_user(db_session, **overrides):
    from app.models.user import User
    from passlib.hash import bcrypt

    defaults = {
        "nickname": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"{uuid.uuid4().hex[:8]}@example.com",
        "password_hash": bcrypt.hash("Test1234!"),
    }
    defaults.update(overrides)
    user = User(**defaults)
    db_session.add(user)
    db_session.flush()
    return user


def auth_header(user_id):
    token = create_access_token(str(user_id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def user(db_session):
    return make_user(db_session)


@pytest.fixture()
def auth_client(client, user):
    token = create_access_token(str(user.id))
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
    client.headers.pop("Authorization", None)
