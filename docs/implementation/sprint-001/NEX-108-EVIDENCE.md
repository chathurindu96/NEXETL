# NEX-108 Evidence — Security Bootstrap Settings

Status: complete in the pre-existing NEX-108 commit.

The centralized configuration validates the secret key, debug and allowed-hosts
policy, and secure Session/CSRF cookie flags. `SESSION_COOKIE_HTTPONLY` and
`SameSite=Lax` are explicit; local HTTP needs explicit secure-flag overrides.
No secret value is committed or logged.
