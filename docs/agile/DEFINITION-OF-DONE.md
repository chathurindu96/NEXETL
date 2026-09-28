# Definition of Done

A ticket is Done only when all applicable conditions are evidenced.

- [ ] Acceptance criteria are satisfied.
- [ ] Implementation conforms to approved requirements, architecture, ADRs, detailed design, and PLAN-001 sequencing.
- [ ] No unnecessary out-of-scope or speculative implementation was introduced.
- [ ] Applicable unit, application, integration, API, security, configuration, frontend, and E2E tests pass.
- [ ] Security checks pass; authentication, authorization, CSRF, validation, error disclosure, and DB safety were addressed where applicable.
- [ ] No secrets, credentials, session values, CSRF tokens, certificates, or sensitive diagnostics were committed or logged.
- [ ] `INSTALLATION.md` records new installation steps and exact dependencies when installs changed.
- [ ] `RUN.md` records new or changed runtime commands when applicable.
- [ ] `DATABASE.md` records database queries, SQL, migrations, schema operations, and verification when applicable.
- [ ] `COMMAND-LOG.md` records relevant implementation, installation, runtime, migration, test, and verification commands.
- [ ] Requirement/design/verification traceability is current.
- [ ] Human-maintained and generated-file changes are reported separately.
- [ ] Git diff and change scope were reviewed; unexpected blast radius was resolved rather than worked around.
- [ ] Relevant documentation is complete and accurate.
- [ ] PR review is complete where the team workflow requires it.
- [ ] Objective evidence is attached or linked to the issue.
- [ ] The issue is ready to close with no hidden follow-up required for its stated scope.

A successful process exit alone is not proof of correctness. Evidence must cover the relevant behavior, inputs, outputs, types, null handling, mappings, rejected input, side effects, persistence, and failure paths.
