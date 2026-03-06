\# Architecture



\## 1) Overview

The system is a dockerized, API-first service.



Components:

\- FastAPI backend (REST API)

\- PostgreSQL for persistent data

\- Redis + Celery worker for background tasks (crawl, PDF processing, wordcloud generation)

\- MailHog for local email capture (forgot password)

\- Nginx demo sites for deterministic crawling (demo\_site and external\_site)

\- Docker volume for persistent storage of PDFs and generated images



\## 2) Locked Technology Stack (Do not change)

Backend:

\- Python 3.11

\- FastAPI

\- Celery worker

\- Redis (broker and result backend)



Database:

\- PostgreSQL 16



Email (local):

\- MailHog



Storage:

\- Docker volume mounted as /data



Deterministic crawl test websites:

\- demo\_site (nginx)

\- external\_site (nginx)



\## 3) Backend Code Structure (Locked)

Repository layout:

\- Repo root: docker-compose.yml, demo\_site/, external\_site/

\- Backend/ contains application code



Backend/app structure (MVC-like separation):

\- app/api/routers: HTTP endpoints

\- app/schemas: Pydantic request/response models

\- app/models: SQLAlchemy ORM models

\- app/services: business logic (crawler, pdf, stats, wordcloud)

\- app/storage: filesystem path helpers for /data

\- app/core: config, security, celery app, error definitions

\- app/db: session management



Rule:

\- No business logic in router files except simple orchestration and input validation.



\## 4) Persistence

DB: Postgres volume (db\_data)

Files: app\_data volume mounted to /data



Expected filesystem structure in /data:

\- /data/pdfs/<user\_id>/<crawl\_job\_id>/\*.pdf

\- /data/wordclouds/<user\_id>/\*.png



\## 5) Background Jobs

Long tasks must be executed by Celery:

\- Crawl execution and page discovery

\- PDF download and storage

\- PDF text extraction and stats creation

\- Wordcloud generation



The API should:

\- Create a job and return a job\_id

\- Provide job status and results via endpoints



\## 6) Crawler Semantics (Locked)

Start URL must be validated:

\- unreachable\_url for connection problems

\- start\_url\_http\_error for HTTP errors



Depth rules:

\- Depth 1: fetch only start URL

\- Depth 2: fetch start URL and same-host links from start page and its depth-2 pages (no external pages)

\- Depth 3: additionally fetch external pages that are discovered from depth-2 pages

&nbsp; - External expansion is NOT allowed

&nbsp; - External pages are fetched once, but their links are not followed



Limits:

\- Deduplicate visited URLs per job

\- Enforce MAX\_PAGES\_PER\_JOB



Deterministic test mode:

\- Use local demo site URL inside Docker network: http://demo\_site/index.html



\## 7) PDF Processing Pipeline (Locked)

Steps:

1\. Download PDFs and store under /data

2\. Extract text from PDFs

3\. Compute top-10 words and counts

4\. Persist results in DB

5\. Expose stats via API



\### 7.3 PDF text extraction library (Locked)

\- Use PyMuPDF (package: pymupdf, module: fitz) for extracting text from PDFs.

\- Do not switch extraction libraries unless there is a blocking technical reason documented in the diary.



\## 8) Security (Locked baseline)

\- JWT auth for protected endpoints

\- Ownership enforced: users can only access their own resources

\- Forgot-password token TTL is 60 seconds

\- Forgot-password must not leak whether an email exists



\## 9) API-first Demo

\- Swagger UI is the primary UI

\- Optional minimal frontend is out of scope unless required




