from unittest.mock import patch, MagicMock

from tests.conftest import make_user, auth_header
from app.models.crawl import CrawlJob, CrawledPage


# ─── Layer 1: API endpoint tests ───


@patch("app.tasks.crawl_tasks.execute_crawl_job.delay")
def test_create_crawl_job(mock_delay, client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.post("/crawl/jobs", json={
        "start_url": "http://demo_site/index.html",
        "depth": 1,
    }, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["start_url"] == "http://demo_site/index.html"
    assert body["depth"] == 1
    assert body["status"] == "queued"


def test_create_crawl_job_invalid_depth(client, db_session):
    user = make_user(db_session)
    headers = auth_header(user.id)
    resp = client.post("/crawl/jobs", json={
        "start_url": "http://demo_site/index.html",
        "depth": 5,
    }, headers=headers)
    assert resp.status_code == 422


def test_create_crawl_job_no_auth(client):
    resp = client.post("/crawl/jobs", json={
        "start_url": "http://demo_site/index.html",
        "depth": 1,
    })
    assert resp.status_code == 403


# ─── Layer 2: Task unit tests ───

MOCK_HTML_WITH_LINKS = """
<html><body>
    <a href="/page2.html">Page 2</a>
    <a href="http://external.com/other.html">External</a>
    <a href="/doc.pdf">PDF</a>
</body></html>
"""

MOCK_HTML_EMPTY = "<html><body>No links here</body></html>"


@patch("app.tasks.crawl_tasks.download_pdf")
@patch("app.tasks.crawl_tasks._fetch_page")
def test_crawl_task_depth_1(mock_fetch, mock_pdf_dl, db_session):
    user = make_user(db_session)
    job = CrawlJob(user_id=user.id, start_url="http://demo_site/index.html", depth=1, status="queued")
    db_session.add(job)
    db_session.flush()

    mock_fetch.return_value = (200, MOCK_HTML_EMPTY)

    from app.tasks.crawl_tasks import execute_crawl_job
    with patch("app.tasks.crawl_tasks.SessionLocal", return_value=db_session):
        with patch.object(db_session, "close"):
            execute_crawl_job(str(job.id))

    pages = db_session.query(CrawledPage).filter(CrawledPage.crawl_job_id == job.id).all()
    assert len(pages) == 1
    assert pages[0].depth_level == 1
    assert job.status == "done"


@patch("app.tasks.crawl_tasks.download_pdf")
@patch("app.tasks.crawl_tasks._fetch_page")
def test_crawl_task_depth_2(mock_fetch, mock_pdf_dl, db_session):
    user = make_user(db_session)
    job = CrawlJob(user_id=user.id, start_url="http://demo_site/index.html", depth=2, status="queued")
    db_session.add(job)
    db_session.flush()

    def fetch_side_effect(url):
        if url == "http://demo_site/index.html":
            return (200, MOCK_HTML_WITH_LINKS)
        return (200, MOCK_HTML_EMPTY)

    mock_fetch.side_effect = fetch_side_effect

    from app.tasks.crawl_tasks import execute_crawl_job
    with patch("app.tasks.crawl_tasks.SessionLocal", return_value=db_session):
        with patch.object(db_session, "close"):
            execute_crawl_job(str(job.id))

    pages = db_session.query(CrawledPage).filter(CrawledPage.crawl_job_id == job.id).all()
    depth_levels = sorted([p.depth_level for p in pages])
    assert 1 in depth_levels
    assert 2 in depth_levels
    assert len(pages) == 2  # start page + /page2.html (same host)
    assert job.status == "done"


@patch("app.tasks.crawl_tasks.download_pdf")
@patch("app.tasks.crawl_tasks._fetch_page")
def test_crawl_task_depth_3(mock_fetch, mock_pdf_dl, db_session):
    user = make_user(db_session)
    job = CrawlJob(user_id=user.id, start_url="http://demo_site/index.html", depth=3, status="queued")
    db_session.add(job)
    db_session.flush()

    def fetch_side_effect(url):
        if url == "http://demo_site/index.html":
            return (200, MOCK_HTML_WITH_LINKS)
        if url == "http://demo_site/page2.html":
            html = '<html><body><a href="http://external.com/ext.html">Ext</a></body></html>'
            return (200, html)
        return (200, MOCK_HTML_EMPTY)

    mock_fetch.side_effect = fetch_side_effect

    from app.tasks.crawl_tasks import execute_crawl_job
    with patch("app.tasks.crawl_tasks.SessionLocal", return_value=db_session):
        with patch.object(db_session, "close"):
            execute_crawl_job(str(job.id))

    pages = db_session.query(CrawledPage).filter(CrawledPage.crawl_job_id == job.id).all()
    depth_levels = sorted([p.depth_level for p in pages])
    assert 1 in depth_levels
    assert 2 in depth_levels
    assert 3 in depth_levels
    assert job.status == "done"
