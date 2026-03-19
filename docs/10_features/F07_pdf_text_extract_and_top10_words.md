\# F07 PDF Text Extraction + Top-10 Words



\## Goal

Extract text from PDFs and compute top-10 words and counts.



\## Locked Implementation Choices

\- Text extraction library is PyMuPDF (pymupdf / fitz)

\- Token normalization:

&nbsp; - lowercase

&nbsp; - strip punctuation

&nbsp; - keep letters and digits

\- Deterministic ordering:

&nbsp; - count desc

&nbsp; - tie alphabetical

\- Store computed stats, do not recompute on every request

\- Controlled error on extraction failure:

&nbsp; - pdf\_text\_not\_extractable



\## Locked library

\- Text extraction must use PyMuPDF (pymupdf / fitz).



\## Endpoint

\- GET /pdfs/{pdf\_id}/stats/top-words



\## Requirements

\- Normalize tokens (lowercase, strip punctuation)

\- Count word frequency

\- Store top 10 words and counts per PDF

\- Deterministic ordering:

&nbsp; - count desc

&nbsp; - tie-breaker alphabetical

\- If text extraction fails, return controlled error:

&nbsp; - pdf\_text\_not\_extractable



\## Persistence

\- Stored stats remain after restart

