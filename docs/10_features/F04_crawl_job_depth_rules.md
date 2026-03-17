\# F04 Crawl Job + Depth Rules



\## Goal

Start a crawl job and process pages according to depth rules.



\## Locked Implementation Choices

\- Deterministic tests use local docker network URL:

&nbsp; - http://demo\_site/index.html

\- Enforce MAX\_PAGES\_PER\_JOB

\- Deduplicate visited URLs per job

\- Depth semantics must follow 01\_ARCHITECTURE.md exactly

\- External expansion is forbidden



\## Endpoint

\- POST /crawl/jobs (auth)



\## Requirements

\- Validate start\_url

\- Depth is 1, 2, or 3

\- Deduplicate visited URLs per job

\- Enforce MAX\_PAGES\_PER\_JOB

\- Use Celery worker for execution



\## Locked Depth Semantics

\- Depth 1: fetch only start URL

\- Depth 2: fetch start URL and same-host links (no external)

\- Depth 3: additionally fetch external pages discovered from depth-2 pages

&nbsp; - No external expansion allowed



\## Deterministic Testing

Use local URL inside Docker network:

\- http://demo\_site/index.html



\## Data

\- CrawlJob stored with status and timestamps

\- CrawledPage stored with url and depth\_level

