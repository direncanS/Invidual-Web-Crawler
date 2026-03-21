import os

from tests.conftest import make_user, auth_header
from app.models.crawl import CrawlJob, CrawledPage
from app.models.pdf import PdfDocument


def _seed_job(db_session, user, status="done", depth=1):
    job = CrawlJob(user_id=user.id, start_url="http://demo_site/index.html", depth=depth, status=status)
    db_session.add(job)
    db_session.flush()
    return job


def _seed_page(db_session, job, url="http://demo_site/index.html", depth_level=1):
    page = CrawledPage(crawl_job_id=job.id, url=url, depth_level=depth_level, status_code=200)
    db_session.add(page)
    db_session.flush()
    return page


def _seed_pdf(db_session, user, job, source_url="http://demo_site/doc.pdf"):
    file_path = f"/tmp/test_data/pdfs/{user.id}/{job.id}/doc.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(b"%PDF-1.4 fake pdf content")
    pdf = PdfDocument(
        user_id=user.id,
        crawl_job_id=job.id,
        source_url=source_url,
        file_path=file_path,
        sha256="abcd1234" * 8,
    )
    db_session.add(pdf)
    db_session.flush()
    return pdf


# ─── Crawl history tests ───


def test_list_jobs(client, db_session):
    user = make_user(db_session)
    _seed_job(db_session, user)
    _seed_job(db_session, user, status="queued")
    headers = auth_header(user.id)
    resp = client.get("/crawl/jobs", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["jobs"]) == 2


def test_list_jobs_no_auth(client):
    resp = client.get("/crawl/jobs")
    assert resp.status_code == 403


def test_get_job_detail(client, db_session):
    user = make_user(db_session)
    job = _seed_job(db_session, user)
    headers = auth_header(user.id)
    resp = client.get(f"/crawl/jobs/{job.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_get_job_not_found(client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.get("/crawl/jobs/00000000-0000-0000-0000-000000000000", headers=headers)
    assert resp.status_code == 404


def test_get_job_pages(client, db_session):
    user = make_user(db_session)
    job = _seed_job(db_session, user, depth=2)
    _seed_page(db_session, job, "http://demo_site/index.html", 1)
    _seed_page(db_session, job, "http://demo_site/page2.html", 2)
    headers = auth_header(user.id)
    resp = client.get(f"/crawl/jobs/{job.id}/pages", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_ownership_isolation(client, db_session):
    user1 = make_user(db_session)
    user2 = make_user(db_session)
    job = _seed_job(db_session, user1)
    headers = auth_header(user2.id)
    resp = client.get(f"/crawl/jobs/{job.id}", headers=headers)
    assert resp.status_code == 404


# ─── PDF tests ───


def test_list_pdfs(client, db_session):
    user = make_user(db_session)
    job = _seed_job(db_session, user)
    _seed_pdf(db_session, user, job)
    headers = auth_header(user.id)
    resp = client.get("/pdfs/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["pdfs"]) == 1


def test_get_pdf_detail(client, db_session):
    user = make_user(db_session)
    job = _seed_job(db_session, user)
    pdf = _seed_pdf(db_session, user, job)
    headers = auth_header(user.id)
    resp = client.get(f"/pdfs/{pdf.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["source_url"] == "http://demo_site/doc.pdf"


def test_get_job_pdfs(client, db_session):
    user = make_user(db_session)
    job = _seed_job(db_session, user)
    _seed_pdf(db_session, user, job)
    headers = auth_header(user.id)
    resp = client.get(f"/crawl/jobs/{job.id}/pdfs", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["pdfs"]) == 1


def test_list_pdfs_no_auth(client):
    resp = client.get("/pdfs/")
    assert resp.status_code == 403
