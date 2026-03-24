\# F08 Search PDFs by Word



\## Goal

Search PDFs by checking whether a given word appears in the stored top-10 words list.



\## Endpoint

\- GET /search/top-words?word=...



\## Requirements

\- Normalize the input word

\- Return list of PDFs where word is present in top-10 stats

\- If no matches, return empty list (not an error)

\- Reject invalid words (too short, invalid characters)

