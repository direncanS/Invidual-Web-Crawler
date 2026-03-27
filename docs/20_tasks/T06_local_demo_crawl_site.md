\# T06 Local Demo Crawl Site



\## Goal

Provide deterministic crawling targets without using the internet.



\## Services

\- demo\_site (nginx): http://localhost:8088

\- external\_site (nginx): http://localhost:8089



\## Deterministic URL inside Docker network

Use:

\- http://demo\_site/index.html



\## Expected structure

demo\_site:

\- index.html links to:

&nbsp; - /level2\_a.html

&nbsp; - /level2\_b.html

&nbsp; - /pdfs/sample.pdf

&nbsp; - http://external\_site/external\_landing.html



external\_site:

\- external\_landing.html links to:

&nbsp; - /external\_extra.html



\## Test expectations

\- Depth 2: must not fetch external\_site pages

\- Depth 3: may fetch external\_landing.html but must not fetch external\_extra.html

