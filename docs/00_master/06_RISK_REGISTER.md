\# Risk Register



\## R1: Crawler depth semantics misunderstood

Impact: High

Mitigation:

\- Lock semantics in 01\_ARCHITECTURE.md

\- Prove via demo\_site and external\_site

\- Add acceptance checks: depth2 no external, depth3 no external expansion



\## R2: Time constraints (1 month)

Impact: High

Mitigation:

\- Feature-by-feature delivery

\- Keep API-first, no heavy frontend

\- Use deterministic crawl environment

\- Feature-by-feature delivery with clear scope per iteration



\## R3: PDF text extraction inconsistencies

Impact: Medium

Mitigation:

\- Lock PyMuPDF

\- Use text-based sample PDFs for tests

\- Provide controlled error for non-extractable PDFs



\## R4: Token and forgot-password security issues

Impact: Medium

Mitigation:

\- Reset token TTL 60 seconds

\- One-time use tokens

\- No email existence leak

\- MailHog used for demo



\## R5: Data persistence failure in Docker

Impact: High

Mitigation:

\- Use db\_data and app\_data volumes

\- Provide restart demo steps



\## R6: Spaghetti code and maintenance

Impact: High

Mitigation:

\- Locked code structure: routers, services, models, schemas

\- No business logic in routers

\- Use clear feature specifications to prevent drift

