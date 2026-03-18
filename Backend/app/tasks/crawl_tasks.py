import logging
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.core.celery_app import celery
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.crawl import CrawlJob, CrawledPage
from app.models.pdf import PdfDocument
from app.services.pdf_service import download_pdf

logger = logging.getLogger(__name__)


def _is_pdf_url(url: str) -> bool:
    return urlparse(url).path.lower().endswith(".pdf")


def _same_host(url: str, base_url: str) -> bool:
    return urlparse(url).netloc == urlparse(base_url).netloc


def _extract_links(html: str, base_url: str) -> tuple[list[str], list[str]]:
    """Return (page_links, pdf_links) as absolute URLs."""
    soup = BeautifulSoup(html, "html.parser")
    page_links: list[str] = []
    pdf_links: list[str] = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        absolute = urljoin(base_url, href)
        # Strip fragments
        absolute = absolute.split("#")[0]
        if not absolute.startswith(("http://", "https://")):
            continue
        if _is_pdf_url(absolute):
            pdf_links.append(absolute)
        else:
            page_links.append(absolute)
    return page_links, pdf_links


def _fetch_page(url: str) -> tuple[int | None, str]:
    resp = requests.get(url, timeout=settings.request_timeout_seconds)
    resp.raise_for_status()
    return resp.status_code, resp.text


@celery.task(name="app.tasks.crawl_tasks.execute_crawl_job")
def execute_crawl_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
        if job is None:
            logger.error("Crawl job %s not found", job_id)
            return

        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        visited: set[str] = set()
        pages_fetched = 0

        def _record_page(url: str, depth_level: int, status_code: int | None) -> None:
            nonlocal pages_fetched
            if url in visited:
                return
            visited.add(url)
            page = CrawledPage(
                crawl_job_id=job.id,
                url=url,
                depth_level=depth_level,
                status_code=status_code,
            )
            db.add(page)
            db.commit()
            pages_fetched += 1

        def _handle_pdfs(pdf_urls: list[str]) -> None:
            for pdf_url in pdf_urls:
                if pdf_url in visited:
                    continue
                visited.add(pdf_url)
                try:
                    download_pdf(pdf_url, job.user_id, job.id, db)
                    from app.tasks.pdf_tasks import process_pdf

                    pdf_doc = (
                        db.query(PdfDocument)
                        .filter(
                            PdfDocument.crawl_job_id == job.id,
                            PdfDocument.source_url == pdf_url,
                        )
                        .first()
                    )
                    if pdf_doc:
                        process_pdf.delay(str(pdf_doc.id))
                except Exception:
                    logger.exception("Failed to download PDF: %s", pdf_url)

        # ── Depth 1: only start URL ──
        try:
            status_code, html = _fetch_page(job.start_url)
        except requests.ConnectionError:
            job.status = "failed"
            job.error_code = "unreachable_url"
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            return
        except requests.HTTPError:
            job.status = "failed"
            job.error_code = "start_url_http_error"
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        _record_page(job.start_url, 1, status_code)
        page_links_d1, pdf_links_d1 = _extract_links(html, job.start_url)
        _handle_pdfs(pdf_links_d1)

        if job.depth >= 2:
            # ── Depth 2: follow same-host links ──
            same_host_links = [
                link for link in page_links_d1
                if _same_host(link, job.start_url) and link not in visited
            ]
            depth2_external: list[str] = []
            for link in same_host_links:
                if pages_fetched >= settings.max_pages_per_job:
                    break
                time.sleep(settings.rate_limit_seconds)
                try:
                    sc, h = _fetch_page(link)
                    _record_page(link, 2, sc)
                    d2_pages, d2_pdfs = _extract_links(h, link)
                    _handle_pdfs(d2_pdfs)
                    # Collect external links for depth 3
                    for d2_link in d2_pages:
                        if not _same_host(d2_link, job.start_url) and d2_link not in visited:
                            depth2_external.append(d2_link)
                except Exception:
                    logger.exception("Failed to fetch depth-2 page: %s", link)

            if job.depth >= 3:
                # ── Depth 3: fetch external pages found at depth 2 (no further expansion) ──
                seen_external: set[str] = set()
                for ext_link in depth2_external:
                    if ext_link in seen_external or ext_link in visited:
                        continue
                    seen_external.add(ext_link)
                    if pages_fetched >= settings.max_pages_per_job:
                        break
                    time.sleep(settings.rate_limit_seconds)
                    try:
                        sc, h = _fetch_page(ext_link)
                        _record_page(ext_link, 3, sc)
                        _, d3_pdfs = _extract_links(h, ext_link)
                        _handle_pdfs(d3_pdfs)
                    except Exception:
                        logger.exception("Failed to fetch depth-3 page: %s", ext_link)

        job.status = "done"
        job.finished_at = datetime.now(timezone.utc)
        db.commit()

    except Exception:
        logger.exception("Crawl job %s failed unexpectedly", job_id)
        try:
            job.status = "failed"
            job.error_code = "internal_error"
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
        except Exception:
            logger.exception("Failed to update job status")
    finally:
        db.close()
