import os

from tests.conftest import make_user, auth_header
from app.models.crawl import CrawlJob
from app.models.pdf import PdfDocument, PdfTopWordsStat


def _seed_pdf_with_words(db_session, user, words_json, source_url="http://demo_site/doc.pdf"):
    job = CrawlJob(user_id=user.id, start_url="http://demo_site/", depth=1, status="done")
    db_session.add(job)
    db_session.flush()

    file_path = f"/tmp/test_data/pdfs/{user.id}/{job.id}/doc.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(b"%PDF-1.4 fake")
    pdf = PdfDocument(
        user_id=user.id, crawl_job_id=job.id,
        source_url=source_url, file_path=file_path, sha256="c" * 64,
    )
    db_session.add(pdf)
    db_session.flush()

    stat = PdfTopWordsStat(pdf_id=pdf.id, words_json=words_json)
    db_session.add(stat)
    db_session.flush()
    return pdf


def test_search_with_match(client, db_session):
    user = make_user(db_session)
    _seed_pdf_with_words(db_session, user, [{"word": "python", "count": 10}])
    headers = auth_header(user.id)
    resp = client.get("/search/top-words?word=python", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1


def test_search_no_match(client, db_session):
    user = make_user(db_session)
    _seed_pdf_with_words(db_session, user, [{"word": "python", "count": 10}])
    headers = auth_header(user.id)
    resp = client.get("/search/top-words?word=golang", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 0


def test_search_case_insensitive(client, db_session):
    user = make_user(db_session)
    _seed_pdf_with_words(db_session, user, [{"word": "python", "count": 10}])
    headers = auth_header(user.id)
    resp = client.get("/search/top-words?word=Python", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1


def test_search_no_auth(client):
    resp = client.get("/search/top-words?word=python")
    assert resp.status_code == 403


def test_search_ownership_isolation(client, db_session):
    user1 = make_user(db_session)
    user2 = make_user(db_session)
    _seed_pdf_with_words(db_session, user1, [{"word": "python", "count": 10}])
    headers = auth_header(user2.id)
    resp = client.get("/search/top-words?word=python", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 0


def test_search_empty_query(client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.get("/search/top-words?word=", headers=headers)
    assert resp.status_code == 422
