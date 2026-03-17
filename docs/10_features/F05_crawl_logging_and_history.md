\# F05 Suchprotokoll (Crawl History)



\## Goal

Store and display crawl history in user profile context.



\## Endpoints

\- GET /crawl/jobs

\- GET /crawl/jobs/{job\_id}

\- GET /crawl/jobs/{job\_id}/pages

\- GET /crawl/jobs/{job\_id}/pdfs



\## Requirements

\- Persistently store:

&nbsp; - start\_url

&nbsp; - created\_at (seconds precision)

&nbsp; - visited pages list

&nbsp; - found PDFs list

\- Ownership enforced

