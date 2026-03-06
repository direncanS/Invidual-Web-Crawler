# Individual Web Crawler

Dockerized web crawler with user authentication, configurable depth crawling, PDF extraction, word frequency analysis, and wordcloud generation.

## Tech Stack

Python 3.11 | FastAPI | PostgreSQL 16 | Redis | Celery | PyMuPDF | MailHog | Docker

## Quick Start

```bash
# 1. Clone
git clone <repo-url> && cd web_crawler

# 2. Start all services
docker compose up -d --build

# 3. Open
#    Frontend  → http://localhost:3000
#    API Docs  → http://localhost:8000/docs
#    MailHog   → http://localhost:8025
#    Demo Site → http://localhost:8088
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| **frontend** | 3000 | React UI (Nginx reverse proxy) |
| **backend** | 8000 | FastAPI REST API |
| **worker** | — | Celery background worker (crawl, PDF, wordcloud) |
| **db** | — | PostgreSQL 16 database |
| **redis** | — | Celery broker & result backend |
| **mailhog** | 8025 | Email capture UI (password reset emails) |
| **demo_site** | 8088 | Static HTML site for deterministic crawl testing |
| **external_site** | 8089 | External site linked from demo_site |

## Features

| ID | Feature | Endpoints | Description |
|----|---------|-----------|-------------|
| F01 | Auth | `POST /auth/register`, `/login` | JWT registration & login |
| F02 | Profile | `GET /me`, `PUT /me` | View & update nickname/email |
| F03 | Password Reset | `POST /auth/forgot-password`, `/reset-password` | 60s one-time token via email |
| F04 | Crawl | `POST /crawl/jobs` | Depth 1-3 crawling with deduplication |
| F05 | History | `GET /crawl/jobs`, `/crawl/jobs/{id}` | Job listing, detail, pages, PDFs |
| F06 | PDFs | `GET /pdfs/`, `/pdfs/{id}`, `/pdfs/{id}/download` | List, detail, binary download |
| F07 | Top Words | `GET /pdfs/{id}/stats/top-words` | Top-10 word frequency per PDF |
| F08 | Search | `GET /search/top-words?word=` | Find PDFs containing a word |
| F09 | Wordcloud Single | `POST /wordclouds/single` | Generate wordcloud for 1 PDF |
| F10 | Wordcloud Multi | `POST /wordclouds/multi` | Generate wordcloud for 2+ PDFs |
| F11 | Wordcloud Interval | `POST /wordclouds/interval` | Generate wordcloud for PDFs in time range |

## API Endpoints

All authenticated endpoints require `Authorization: Bearer <token>`.

### Auth

```
POST /auth/register          {"nickname", "email", "password"}        → 201 {id, nickname, email}
POST /auth/login             {"email_or_nickname", "password"}        → 200 {access_token}
POST /auth/forgot-password   {"email"}                                → 200 {message}
POST /auth/reset-password    {"token", "new_password"}                → 200 {message}
```

### Profile

```
GET  /me                                                              → 200 {id, nickname, email}
PUT  /me                     {"nickname?", "email?"}                  → 200 {id, nickname, email}
```

### Crawl

```
POST /crawl/jobs             {"start_url", "depth": 1-3}             → 201 CrawlJob
GET  /crawl/jobs                                                      → 200 {jobs: [...]}
GET  /crawl/jobs/{id}                                                 → 200 CrawlJob
GET  /crawl/jobs/{id}/pages                                           → 200 [CrawledPage]
GET  /crawl/jobs/{id}/pdfs                                            → 200 {pdfs: [...]}
```

### PDFs

```
GET  /pdfs/                                                           → 200 {pdfs: [...]}
GET  /pdfs/{id}                                                       → 200 PdfResponse
GET  /pdfs/{id}/download                                              → 200 application/pdf
GET  /pdfs/{id}/stats/top-words                                       → 200 {pdf_id, words: [{word, count}]}
```

### Search

```
GET  /search/top-words?word=<string>                                  → 200 {results: [PdfResponse]}
```

### Wordclouds

```
POST /wordclouds/single      {"pdf_id"}                              → 201 WordcloudArtifact
POST /wordclouds/multi       {"pdf_ids": [uuid, ...]}                → 201 WordcloudArtifact
POST /wordclouds/interval    {"start_datetime", "end_datetime"}      → 201 WordcloudArtifact
GET  /wordclouds/{id}/image                                           → 200 image/png
```

## Testing

```bash
# Run all 74 tests (inside backend container)
docker compose exec backend pytest -v

# Run specific test suite
docker compose exec backend pytest tests/test_s4_crawl.py -v
```

Test suites: S0 (health), S1 (register), S2 (login), S3 (profile), S4 (crawl), S5 (history/PDF), S6 (PDF stats), S7 (search), S8 (wordcloud).

## Project Structure

```
web_crawler/
├── docker-compose.yml
├── README.md
│
├── Backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI entry point
│       ├── api/
│       │   ├── deps.py          # get_db, get_current_user
│       │   └── routers/         # auth, me, crawl, pdfs, search, wordclouds, health
│       ├── core/                # config, security, celery, errors, stopwords
│       ├── db/                  # session factory
│       ├── models/              # SQLAlchemy ORM (user, crawl, pdf, wordcloud)
│       ├── schemas/             # Pydantic validation
│       ├── services/            # Business logic
│       ├── tasks/               # Celery tasks (crawl, PDF extraction, wordcloud)
│       ├── storage/             # File system helpers
│       └── tests/               # pytest test suite (9 files, 74 tests)
│
├── Frontend/
│   ├── Dockerfile
│   ├── nginx.conf               # Reverse proxy config
│   ├── package.json
│   └── src/
│       ├── api/                 # Axios API modules
│       ├── components/          # UI and layout components
│       ├── context/             # AuthContext (JWT management)
│       ├── hooks/               # useAuth, usePolling
│       └── pages/               # 13 page components
│
├── demo_site/                   # Nginx-served HTML for crawl testing
│   ├── index.html
│   ├── level2_a.html
│   ├── level2_b.html
│   ├── deep/ignored.html
│   └── pdfs/sample.pdf
│
├── external_site/               # External site (linked from demo_site)
│   └── external_landing.html
│
└── docs/                        # Architecture, feature specs, tasks
    ├── 00_master/
    ├── 10_features/
    └── 20_tasks/
```

## Demo Site Graph

The demo site provides a deterministic page structure for testing crawl depth behavior:

```
http://demo_site/index.html          ← Depth 1 (root)
├── /level2_a.html                   ← Depth 2
│   ├── http://external_site/external_landing.html  ← Depth 3 (external)
│   └── /deep/ignored.html           ← Depth 3 (not expanded further)
├── /level2_b.html                   ← Depth 2
│   ├── /level2_a.html               ← (deduped)
│   └── /pdfs/sample.pdf             ← PDF (discovered at depth 2)
├── /pdfs/sample.pdf                 ← PDF (deduped with above)
└── http://external_site/...         ← External link (fetched at depth 3 only)
```

| Depth | Pages Fetched |
|-------|---------------|
| 1 | `index.html` only |
| 2 | `index.html` + `level2_a.html` + `level2_b.html` (same-host links) |
| 3 | All above + `external_landing.html` (external links resolved, not expanded) |
