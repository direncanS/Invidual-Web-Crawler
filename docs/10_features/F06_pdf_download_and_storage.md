\# F06 PDF Download + Storage



\## Goal

Store found PDFs and allow download.



\## Endpoints

\- GET /pdfs

\- GET /pdfs/{pdf\_id}

\- GET /pdfs/{pdf\_id}/download



\## Requirements

\- PDFs stored under /data (Docker volume)

\- Download returns application/pdf

\- PDFs accessible via Suchprotokoll and direct PDF endpoints

\- Persistence after restart

