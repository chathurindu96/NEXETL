# NEX-105 Evidence — Centralized Increment 1 Configuration Loading

## Scope

NEX-105 establishes the narrow configuration-resolution boundary for Increment
1. It resolves typed backend settings solely from the process environment and
maps them into Django settings. It does not implement startup validation,
semantic error classification, or fail-fast policy; those remain NEX-106 work.

## Implemented boundary

- `backend/src/nexetl/configuration.py` is the only backend source file with
  raw process-environment access.
- The standard Django entry points delegate settings-module selection to that
  configuration boundary.
- No `.env` file is loaded. `python-dotenv` was removed from the manifest and
  lockfile because it had no remaining approved use.
- Secret values have no fallback and are excluded from object representations.
- DES-001 local defaults are applied for non-secret database, host, debug, and
  cookie settings. Secure cookies default independently of debug mode.
- `.env.example` is an environment-variable reference only; it contains no
  usable secret example and does not imply runtime file loading.

## Verification

- Locked dependency verification passed: 15 packages resolved from the lock.
- Focused configuration tests passed: 6 before the source-boundary audit, then
  8 after it was added.
- Full backend suite passed: 20 tests.
- Django system check passed with temporary process-only configuration values.

## Explicitly deferred to NEX-106

- Missing-secret rejection at startup.
- Placeholder, empty-value, host-list, port-range, and broader semantic-value
  validation policy.
- Configuration error taxonomy and fail-fast behavior.

No database, migration, Pipeline Definition, endpoint, or NEX-106 source work
was introduced.
