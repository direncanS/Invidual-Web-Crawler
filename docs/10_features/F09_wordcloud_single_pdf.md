\# F09 Wordcloud: Single PDF



\## Goal

Generate a wordcloud for one PDF.



\## Endpoint

\- POST /wordclouds/single

\- GET /wordclouds/{id}/image



\## Requirements

\- Wordcloud based on PDF stats or extracted text (implementation choice, but consistent)

\- Store generated image under /data

\- Persistence after restart

