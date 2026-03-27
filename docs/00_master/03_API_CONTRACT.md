\# API Contract (Draft)



\## Conventions

\- All authenticated endpoints require `Authorization: Bearer <JWT>`.

\- Errors use the locked error response shape:

{

&nbsp; "error": {

&nbsp;   "code": "<string>",

&nbsp;   "message": "<string>",

&nbsp;   "http\_status": <int>

&nbsp; }

}



\## Auth (F01, F03)

POST /auth/register

\- Request: nickname, email, password

\- Responses:

&nbsp; - 201 success

&nbsp; - 400 invalid\_email, weak\_password, nickname\_already\_exists, email\_already\_exists



POST /auth/login

\- Request: email\_or\_nickname, password

\- Response: access\_token (JWT)

\- Errors: 401 invalid\_credentials



POST /auth/forgot-password

\- Request: email

\- Response: 200 (or 202) always (no email existence leak)

\- Side effect: email sent to MailHog with reset link/token



POST /auth/reset-password

\- Request: token, new\_password

\- Responses:

&nbsp; - 200 success

&nbsp; - 400 reset\_token\_invalid, reset\_token\_expired, reset\_token\_used, weak\_password



\## Profile (F02)

GET /me (auth)

PUT /me (auth)

\- Update nickname/email with validation and uniqueness checks



\## Crawl (F04, F05)

POST /crawl/jobs (auth)

\- Request: start\_url, depth

\- Response: job\_id, status



GET /crawl/jobs (auth)

GET /crawl/jobs/{job\_id} (auth)

GET /crawl/jobs/{job\_id}/pages (auth)

GET /crawl/jobs/{job\_id}/pdfs (auth)



\## PDFs (F06, F07)

GET /pdfs (auth)

GET /pdfs/{pdf\_id} (auth)

GET /pdfs/{pdf\_id}/download (auth)

GET /pdfs/{pdf\_id}/stats/top-words (auth)



\## Search (F08)

GET /search/top-words?word=... (auth)

\- Returns PDFs where word appears in stored top-10 list



\## Wordclouds (F09-F11)

POST /wordclouds/single (auth)

POST /wordclouds/multi (auth)

POST /wordclouds/interval (auth)

GET /wordclouds/{id}/image (auth)



\## Optional UI (F00\_UI)

Server-rendered UI may be added without changing API behavior.

