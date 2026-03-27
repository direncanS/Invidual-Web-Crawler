\# T05 Demo Script (10-minute walkthrough)



\## Start

1\) docker compose up --build

2\) Open Swagger: http://localhost:8000/docs

3\) Open MailHog: http://localhost:8025

4\) Open demo site: http://localhost:8088/index.html



\## Auth

\- Register

\- Login and authorize in Swagger



\## Forgot password

\- Request reset

\- Open MailHog email

\- Reset within 60 seconds

\- Attempt token reuse (must fail)



\## Crawl

Use deterministic start\_url inside Docker:

\- http://demo\_site/index.html



Show:

\- Depth 1 result

\- Depth 2 result (no external pages)

\- Depth 3 result (external landing fetched, but external\_extra not fetched)



\## History + PDFs

\- Show Suchprotokoll

\- Download a PDF



\## Stats + Search

\- Show top-10 stats

\- Search a word that exists and one that does not



\## Wordcloud

\- Single

\- Interval with empty set (no\_pdfs\_in\_interval)



\## Persistence

\- Restart backend and worker

\- Re-check stats and wordcloud (if generated)

