\# F02 Profile: View + Edit



\## Goal

Logged-in user can view and edit their profile.



\## Endpoints

\- GET /me

\- PUT /me



\## Requirements

\- JWT auth required

\- GET /me returns nickname, email

\- PUT /me allows updating nickname and/or email

\- Validation and uniqueness checks

\- Empty update rejected



\## Errors

\- unauthorized

\- invalid\_token

\- invalid\_email

\- nickname\_already\_exists

\- email\_already\_exists

\- no\_fields\_to\_update



\## Files

\- app/api/routers/me.py

\- app/services/user\_service.py

\- app/schemas/user.py

\- app/models/user.py

