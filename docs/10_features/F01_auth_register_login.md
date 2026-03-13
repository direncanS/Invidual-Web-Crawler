\# F01 Auth: Register + Login



\## Goal

Implement registration and login.



\## Locked Implementation Choices

\- JWT access token via Authorization: Bearer <token>

\- Password hashing: passlib bcrypt

\- Password rule: minimum length 8

\- Login accepts email or nickname in one field

\- Errors are returned in the locked error response shape



\## Requirements

\- Register with nickname, email, password

\- Validate email format

\- Enforce uniqueness for nickname and email

\- Password is stored as a hash

\- Login with email\_or\_nickname + password returns JWT



\## Endpoints

\- POST /auth/register

\- POST /auth/login



\## Errors

\- invalid\_email

\- weak\_password

\- nickname\_already\_exists

\- email\_already\_exists

\- invalid\_credentials



\## Files (expected)

\- app/api/routers/auth.py

\- app/schemas/auth.py

\- app/models/user.py

\- app/services/auth\_service.py

\- app/core/security.py

