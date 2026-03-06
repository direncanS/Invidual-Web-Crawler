\# Data Model (High-level, v1)



\## Purpose

Define v1 entities and relationships aligned with locked architecture and the DB plan.



\## Entities

User

\- id (uuid)

\- nickname (unique)

\- email (unique)

\- password\_hash

\- created\_at, updated\_at



PasswordResetToken

\- id

\- user\_id

\- token\_hash (unique)

\- expires\_at

\- used\_at (nullable)

\- created\_at



CrawlJob

\- id

\- user\_id

\- start\_url

\- depth (1..3)

\- status (queued, running, done, failed)

\- error\_code (nullable)

\- created\_at, started\_at, finished\_at



CrawledPage

\- id

\- crawl\_job\_id

\- url

\- depth\_level

\- status\_code (nullable)

\- fetched\_at

\- unique(crawl\_job\_id, url)



PdfDocument

\- id

\- user\_id

\- crawl\_job\_id

\- source\_url

\- file\_path (relative under /data)

\- sha256 (optional)

\- downloaded\_at

\- unique(crawl\_job\_id, source\_url)



PdfTopWordsStat

\- id

\- pdf\_id (unique)

\- words\_json (jsonb; ordered list length 10)

\- created\_at



WordcloudArtifact

\- id

\- user\_id

\- mode (single|multi|interval)

\- interval\_start (nullable)

\- interval\_end (nullable)

\- image\_path (nullable; allowed for no\_pdfs\_in\_interval)

\- created\_at



WordcloudArtifactPdf (join table)

\- wordcloud\_id

\- pdf\_id

\- primary key(wordcloud\_id, pdf\_id)



\## Relationship overview

User 1..N CrawlJob

CrawlJob 1..N CrawledPage

CrawlJob 1..N PdfDocument

PdfDocument 1..0..1 PdfTopWordsStat

User 1..N WordcloudArtifact

WordcloudArtifact N..N PdfDocument via join table



\## Determinism notes

\- Top-10 ordering: count desc, tie alphabetical

\- Interval selection uses PdfDocument.downloaded\_at timestamps (seconds precision)

