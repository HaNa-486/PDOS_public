# Verification ladder

Use the lowest-cost evidence first, but do not stop before the risk is covered.

1. Static checks: formatting, lint, types, schemas, dependency and secret checks.
2. Unit tests: local rules, boundaries, transformations, and failure behavior.
3. Integration tests: databases, queues, storage, identity, third-party adapters.
4. Contract tests: API shapes, events, migrations, compatibility, malformed dependency responses.
5. End-to-end tests: critical journeys across real boundaries.
6. Experience checks: first use, loading, empty, error, retry, refresh, mobile, keyboard, accessibility.
7. Production checks: configuration, observability, alerts, capacity, security, rollout, rollback, recovery.

Tie every critical acceptance criterion to evidence. Record commands or artifacts, results, and anything not run. A passing test suite is evidence, not a substitute for inspecting the product journey.
