\# F11 Wordcloud: Time Interval



\## Goal

Generate a wordcloud from PDFs found within a given time range with seconds precision.



\## Endpoint

\- POST /wordclouds/interval

\- GET /wordclouds/{id}/image



\## Requirements

\- Input: start\_datetime, end\_datetime (seconds precision)

\- Select PDFs discovered in \[start,end]

\- If no PDFs in interval:

&nbsp; - return message: no\_pdfs\_in\_interval

&nbsp; - do not generate an image

\- If PDFs exist:

&nbsp; - generate and persist image

