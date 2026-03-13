\# F03 Forgot Password (60 seconds token)



\## Goal

User can request a password reset link/token that is valid for 60 seconds.



\## Locked Implementation Choices

\- Token TTL is exactly 60 seconds (server time)

\- Token is one-time use

\- No email existence leak:

&nbsp; - always return 200/202-like response

\- Email delivery is via SMTP to MailHog (local docker)



\## Endpoints

\- POST /auth/forgot-password

\- POST /auth/reset-password



\## Requirements

\- Token TTL: 60 seconds

\- Token is one-time use

\- Do not leak if email exists

\- Send email via SMTP to MailHog in local dev



\## Errors

\- reset\_token\_invalid

\- reset\_token\_expired

\- reset\_token\_used

\- weak\_password

