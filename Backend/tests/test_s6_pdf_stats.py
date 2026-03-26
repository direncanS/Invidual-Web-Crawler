import os

from tests.conftest import make_user, auth_header
from app.models.crawl import CrawlJob
from app.models.pdf import PdfDocument, PdfTopWordsStat
from app.services.pdf_service import compute_top_words


def _seed_job(db_session, user):
    job = CrawlJob(user_id=user.id, start_url="http://demo_site/", depth=1, status="done")
    db_session.add(job)
    db_session.flush()
    return job


def _seed_pdf_with_stats(db_session, user, job, words_json):
    file_path = f"/tmp/test_data/pdfs/{user.id}/{job.id}/doc.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(b"%PDF-1.4 fake")
    pdf = PdfDocument(
        user_id=user.id,
        crawl_job_id=job.id,
        source_url="http://demo_site/doc.pdf",
        file_path=file_path,
        sha256="a" * 64,
    )
    db_session.add(pdf)
    db_session.flush()

    stat = PdfTopWordsStat(pdf_id=pdf.id, words_json=words_json)
    db_session.add(stat)
    db_session.flush()
    return pdf


# ─── Unit tests: compute_top_words ───


def test_compute_top_words_basic():
    text = "python python python java java ruby"
    result = compute_top_words(text, n=3)
    assert result[0]["word"] == "python"
    assert result[0]["count"] == 3
    assert result[1]["word"] == "java"
    assert len(result) == 3


def test_compute_top_words_filters_stopwords():
    text = "the the the and and python"
    result = compute_top_words(text, n=10)
    words = [r["word"] for r in result]
    assert "the" not in words
    assert "and" not in words
    assert "python" in words


def test_compute_top_words_case_insensitive():
    text = "Python python PYTHON"
    result = compute_top_words(text, n=1)
    assert result[0]["word"] == "python"
    assert result[0]["count"] == 3


def test_compute_top_words_empty():
    result = compute_top_words("", n=10)
    assert result == []


def test_compute_top_words_only_stopwords():
    text = "the and is are was were"
    result = compute_top_words(text, n=10)
    assert result == []


# ─── API endpoint tests ───


def test_get_top_words_endpoint(client, db_session):
    user = make_user(db_session)
    job = _seed_job(db_session, user)
    words = [{"word": "python", "count": 10}, {"word": "java", "count": 5}]
    pdf = _seed_pdf_with_stats(db_session, user, job, words)
    headers = auth_header(user.id)

    resp = client.get(f"/pdfs/{pdf.id}/stats/top-words", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["pdf_id"] == str(pdf.id)
    assert len(body["words"]) == 2
    assert body["words"][0]["word"] == "python"


def test_get_top_words_not_ready(client, db_session):
    user = make_user(db_session)
    job = _seed_job(db_session, user)
    file_path = f"/tmp/test_data/pdfs/{user.id}/{job.id}/nostat.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(b"%PDF-1.4 fake")
    pdf = PdfDocument(
        user_id=user.id, crawl_job_id=job.id,
        source_url="http://demo_site/nostat.pdf",
        file_path=file_path, sha256="b" * 64,
    )
    db_session.add(pdf)
    db_session.flush()
    headers = auth_header(user.id)

    resp = client.get(f"/pdfs/{pdf.id}/stats/top-words", headers=headers)
    assert resp.status_code == 409
    assert resp.json()["detail"]["error"]["code"] == "not_ready"


def test_get_top_words_no_auth(client):
    resp = client.get("/pdfs/00000000-0000-0000-0000-000000000000/stats/top-words")
    assert resp.status_code == 403
