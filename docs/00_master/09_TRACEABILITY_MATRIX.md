\# Traceability Matrix



\## Mapping rules

\- Each Feature must map to:

&nbsp; - Use Cases (UC)

&nbsp; - Test Cases (TC)

&nbsp; - Endpoints

&nbsp; - Core files



\## Matrix



\### F01 Auth

\- UC: UC1, UC0 (login implicit)

\- TC: TC1.1, TC1.2, TC1.3, TC0.1, TC0.2 (if included)

\- Endpoints: /auth/register, /auth/login

\- Files: app/api/routers/auth.py, app/services/auth\_service.py, app/models/\*, app/schemas/auth.py



\### F02 Profile

\- UC: UC3

\- TC: TC3.1, TC3.2

\- Endpoints: /me (GET, PUT)

\- Files: app/api/routers/me.py, app/services/user\_service.py, app/schemas/user.py



\### F03 Forgot Password

\- UC: UC2

\- TC: TC2.1, TC2.2, TC2.3

\- Endpoints: /auth/forgot-password, /auth/reset-password

\- Files: app/services/auth\_service.py, app/core/email.py, app/models/password\_reset\_token.py



\### F04 Crawl

\- UC: UC4

\- TC: TC4.1, TC4.2, TC4.3

\- Endpoints: /crawl/jobs etc

\- Files: app/services/crawl\_service.py, worker/tasks.py



\### F05 History

\- UC: UC5

\- TC: TC5.1

\- Endpoints: /crawl/jobs, /crawl/jobs/{id}

\- Files: models, services



\### F06 PDF Download

\- UC: UC5

\- TC: TC5.2

\- Endpoints: /pdfs/{id}/download

\- Files: app/services/pdf\_service.py, app/storage/paths.py



\### F07 PDF Stats

\- UC: UC6

\- TC: TC6.1, TC6.2

\- Endpoints: /pdfs/{id}/stats/top-words

\- Files: app/services/pdf\_stats\_service.py, PyMuPDF usage



\### F08 Search

\- UC: UC7

\- TC: TC7.1

\- Endpoints: /search/top-words

\- Files: app/services/search\_service.py



\### F09-F11 Wordcloud

\- UC: UC8

\- TC: TC8.1, TC8.2, TC8.3

\- Endpoints: /wordclouds/\*

\- Files: app/services/wordcloud\_service.py, storage paths

