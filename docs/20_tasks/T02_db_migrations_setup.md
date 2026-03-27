\# T02 Database Migrations Setup



\## Goal

Set up Alembic migrations and create initial schema.



\## Steps

1\. Implement SQLAlchemy models under app/models

2\. Update alembic/env.py:

&nbsp;  - import Base and set target\_metadata = Base.metadata

3\. Create initial migration:

&nbsp;  - alembic revision --autogenerate -m "initial schema"

4\. Apply migrations:

&nbsp;  - alembic upgrade head



\## Required tables (minimum)

\- users

\- crawl\_jobs

\- crawled\_pages

\- pdf\_documents

\- pdf\_top\_words\_stats

\- wordcloud\_artifacts

\- wordcloud\_artifact\_pdfs

\- password\_reset\_tokens



\## Evidence

\- Show migration file

\- Show docker logs confirming upgrade




