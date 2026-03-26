import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from tests.conftest import make_user, auth_header
from app.models.crawl import CrawlJob
from app.models.pdf import PdfDocument
from app.models.wordcloud import WordcloudArtifact


def _seed_pdf(db_session, user, source_url="http://demo_site/doc.pdf"):
    job = CrawlJob(user_id=user.id, start_url="http://demo_site/", depth=1, status="done")
    db_session.add(job)
    db_session.flush()
    file_path = f"/tmp/test_data/pdfs/{user.id}/{job.id}/doc.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(b"%PDF-1.4 fake")
    pdf = PdfDocument(
        user_id=user.id, crawl_job_id=job.id,
        source_url=source_url, file_path=file_path, sha256="d" * 64,
    )
    db_session.add(pdf)
    db_session.flush()
    return pdf


# ─── Single wordcloud ───


@patch("app.tasks.wordcloud_tasks.generate_wordcloud.delay")
def test_create_single_wordcloud(mock_delay, client, db_session):
    user = make_user(db_session)
    pdf = _seed_pdf(db_session, user)
    headers = auth_header(user.id)
    resp = client.post("/wordclouds/single", json={"pdf_id": str(pdf.id)}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["mode"] == "single"
    mock_delay.assert_called_once()


@patch("app.tasks.wordcloud_tasks.generate_wordcloud.delay")
def test_create_single_pdf_not_found(mock_delay, client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.post("/wordclouds/single", json={
        "pdf_id": "00000000-0000-0000-0000-000000000000",
    }, headers=headers)
    assert resp.status_code == 404


# ─── Multi wordcloud ───


@patch("app.tasks.wordcloud_tasks.generate_wordcloud.delay")
def test_create_multi_wordcloud(mock_delay, client, db_session):
    user = make_user(db_session)
    pdf1 = _seed_pdf(db_session, user, "http://demo_site/a.pdf")
    pdf2 = _seed_pdf(db_session, user, "http://demo_site/b.pdf")
    headers = auth_header(user.id)
    resp = client.post("/wordclouds/multi", json={
        "pdf_ids": [str(pdf1.id), str(pdf2.id)],
    }, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["mode"] == "multi"


def test_create_multi_too_few_pdfs(client, db_session):
    user = make_user(db_session)
    pdf = _seed_pdf(db_session, user)
    headers = auth_header(user.id)
    resp = client.post("/wordclouds/multi", json={
        "pdf_ids": [str(pdf.id)],
    }, headers=headers)
    assert resp.status_code == 422


# ─── Interval wordcloud ───


@patch("app.tasks.wordcloud_tasks.generate_wordcloud.delay")
def test_create_interval_wordcloud(mock_delay, client, db_session):
    user = make_user(db_session)
    _seed_pdf(db_session, user)
    now = datetime.now(timezone.utc)
    headers = auth_header(user.id)
    resp = client.post("/wordclouds/interval", json={
        "start_datetime": (now - timedelta(hours=1)).isoformat(),
        "end_datetime": (now + timedelta(hours=1)).isoformat(),
    }, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["mode"] == "interval"


@patch("app.tasks.wordcloud_tasks.generate_wordcloud.delay")
def test_create_interval_no_pdfs(mock_delay, client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.post("/wordclouds/interval", json={
        "start_datetime": "2000-01-01T00:00:00Z",
        "end_datetime": "2000-01-02T00:00:00Z",
    }, headers=headers)
    assert resp.status_code == 404


# ─── Image endpoint ───


def test_get_image_not_ready(client, db_session):
    user = make_user(db_session)
    artifact = WordcloudArtifact(user_id=user.id, mode="single", image_path=None)
    db_session.add(artifact)
    db_session.flush()
    headers = auth_header(user.id)
    resp = client.get(f"/wordclouds/{artifact.id}/image", headers=headers)
    assert resp.status_code == 409
    assert resp.json()["detail"]["error"]["code"] == "not_ready"


def test_get_image_not_found(client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.get("/wordclouds/00000000-0000-0000-0000-000000000000/image", headers=headers)
    assert resp.status_code == 404


def test_wordcloud_no_auth(client):
    resp = client.post("/wordclouds/single", json={
        "pdf_id": "00000000-0000-0000-0000-000000000000",
    })
    assert resp.status_code == 403
