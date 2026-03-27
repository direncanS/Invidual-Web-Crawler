\# Acceptance Tests (Project-level)



\## Purpose

Single checklist proving:

\- KO criteria: Functionalities >= 20, Diary >= 20

\- Key requirements are met

\- Demo is deterministic



\## F01 Register + Login

\- Register succeeds with valid nickname/email/password

\- Duplicate nickname rejected

\- Duplicate email rejected

\- Invalid email format rejected

\- Weak password rejected

\- Login works and returns JWT

\- Invalid credentials rejected



\## F02 Profile

\- Auth required for /me

\- GET /me shows current data

\- PUT /me updates data with validation and uniqueness checks

\- Empty update rejected



\## F03 Forgot Password (60s)

\- Forgot-password produces email in MailHog

\- Reset within 60 seconds succeeds

\- Reset after 60 seconds fails

\- Token reuse fails

\- Invalid token fails

\- No email existence leak



\## F04 Crawl Jobs

Deterministic rule:

\- Use http://demo\_site/index.html for all crawl tests



Depth:

\- Depth 1: only start URL visited

\- Depth 2: start + same-host links, no external pages

\- Depth 3: external landing fetched, but no external expansion (external\_extra not fetched)



Limits:

\- Dedup works

\- MAX\_PAGES\_PER\_JOB enforced



\## F05 History (Suchprotokoll)

\- Jobs listed with time and results

\- Pages and PDFs visible per job

\- Ownership enforced



\## F06 PDF download

\- Download works and returns application/pdf

\- Persistence after restart



\## F07 Top-10 stats

\- Top-10 words and counts computed and stored

\- Ordering deterministic (count desc, tie alphabetical)

\- Persistence after restart



\## F08 Search

\- Word query returns matching PDFs

\- Nonexisting word returns empty list



\## F09-F11 Wordcloud

\- Single works

\- Multi works (>=2 selection)

\- Interval works (seconds precision)

\- Interval empty set returns no\_pdfs\_in\_interval and produces no image

