\# DB Relationships + UI Plan (v1 Locked, Changeable via Migrations)



\## Goal

\- Define a clean relational schema aligned with current architecture (routers, services, models, schemas).

\- Lock v1 database relationships to avoid scope drift.

\- Still allow future changes via Alembic migrations (controlled changes).

\- Add a minimal UI to reduce grading risk if the instructor expects a visible interface.



\## Part A: Database Schema v1



\### A1) Locked rules (v1)

\- Database is PostgreSQL 16.

\- Schema changes only via Alembic migrations.

\- No destructive changes without a migration note in the diary.

\- Ownership enforced at query level: every user-owned resource must be filtered by user\_id.



\### A2) Entities and relationships (ERD text)

User (1) to (N) CrawlJob

CrawlJob (1) to (N) CrawledPage

CrawlJob (1) to (N) PdfDocument

PdfDocument (1) to (0..1) PdfTopWordsStat

User (1) to (N) WordcloudArtifact

User (1) to (N) PasswordResetToken

WordcloudArtifact (N) to (N) PdfDocument via join table



\### A3) Tables (v1)



\#### users

\- id (uuid, PK)

\- nickname (varchar, unique, not null)

\- email (varchar, unique, not null)

\- password\_hash (varchar, not null)

\- created\_at (timestamptz, not null)

\- updated\_at (timestamptz, not null)



Indexes:

\- unique(nickname)

\- unique(email)



\#### password\_reset\_tokens

\- id (uuid, PK)

\- user\_id (uuid, FK -> users.id, on delete cascade, not null)

\- token\_hash (varchar, unique, not null)

\- expires\_at (timestamptz, not null)

\- used\_at (timestamptz, null)

\- created\_at (timestamptz, not null)



Indexes:

\- index(user\_id)

\- index(expires\_at)



\#### crawl\_jobs

\- id (uuid, PK)

\- user\_id (uuid, FK -> users.id, on delete cascade, not null)

\- start\_url (text, not null)

\- depth (smallint, not null) constraint: depth in (1,2,3)

\- status (varchar, not null) values: queued|running|done|failed

\- error\_code (varchar, null)

\- created\_at (timestamptz, not null)

\- started\_at (timestamptz, null)

\- finished\_at (timestamptz, null)



Indexes:

\- index(user\_id, created\_at desc)

\- index(status)



\#### crawled\_pages

\- id (uuid, PK)

\- crawl\_job\_id (uuid, FK -> crawl\_jobs.id, on delete cascade, not null)

\- url (text, not null)

\- depth\_level (smallint, not null) constraint: depth\_level in (1,2,3)

\- status\_code (int, null)

\- fetched\_at (timestamptz, not null)



Constraints:

\- unique(crawl\_job\_id, url)



Indexes:

\- index(crawl\_job\_id)

\- index(crawl\_job\_id, depth\_level)



\#### pdf\_documents

\- id (uuid, PK)

\- user\_id (uuid, FK -> users.id, on delete cascade, not null)

\- crawl\_job\_id (uuid, FK -> crawl\_jobs.id, on delete cascade, not null)

\- source\_url (text, not null)

\- file\_path (text, not null) relative under /data

\- sha256 (varchar, null)

\- downloaded\_at (timestamptz, not null)



Constraints:

\- unique(crawl\_job\_id, source\_url)



Indexes:

\- index(user\_id, downloaded\_at desc)

\- index(crawl\_job\_id)



\#### pdf\_top\_words\_stats

\- id (uuid, PK)

\- pdf\_id (uuid, FK -> pdf\_documents.id, on delete cascade, not null)

\- words\_json (jsonb, not null) ordered list length 10

\- created\_at (timestamptz, not null)



Constraints:

\- unique(pdf\_id)



\#### wordcloud\_artifacts

\- id (uuid, PK)

\- user\_id (uuid, FK -> users.id, on delete cascade, not null)

\- mode (varchar, not null) values: single|multi|interval

\- interval\_start (timestamptz, null)

\- interval\_end (timestamptz, null)

\- image\_path (text, null) allowed for no\_pdfs\_in\_interval

\- created\_at (timestamptz, not null)



Indexes:

\- index(user\_id, created\_at desc)



\#### wordcloud\_artifact\_pdfs (join table)

\- wordcloud\_id (uuid, FK -> wordcloud\_artifacts.id, on delete cascade, not null)

\- pdf\_id (uuid, FK -> pdf\_documents.id, on delete cascade, not null)



Constraints:

\- primary key(wordcloud\_id, pdf\_id)



Indexes:

\- index(pdf\_id)



\### A4) Why these relationships

\- Clear ownership boundary via user\_id on root tables.

\- Cascading deletes keep data consistent.

\- Unique constraints prevent duplicates and simplify tests.

\- Join table provides relational integrity for wordcloud provenance.



\## Part B: Frontend UI Plan (Minimal, Low Risk)



\### B1) Decision

Add minimal server-rendered UI using:

\- FastAPI + Jinja2 templates

\- Static files for basic styling



Reason:

\- Lowest integration risk

\- No separate build pipeline

\- Works inside same Docker container

\- Visible UI for instructors who expect it



React remains optional later.



\### B2) UI Pages (mapped to features)

1\) Landing page: purpose + links

2\) Register page: maps to F01

3\) Login page: maps to F01

4\) Profile page: maps to F02 + F05

5\) New Crawl page: maps to F04

6\) Job Detail page: maps to F05 + F06

7\) PDF Stats page: maps to F07

8\) Search page: maps to F08

9\) Wordcloud page: maps to F09-F11



\### B3) Non-goals (v1)

\- No advanced design

\- No SPA requirements

\- Swagger remains primary full UI for endpoints



\## Part C: Migration and Updates Policy



Allowed:

\- Add columns, tables, indexes via migrations

\- Adjust constraints via migrations



Locked:

\- Ownership boundary remains

\- Crawler semantics remain

