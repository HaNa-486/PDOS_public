# Production release gate

Do not label a release production-ready until applicable items are evidenced:

- Critical user journeys succeed, including failure and recovery.
- Authentication, authorization, tenant boundaries, secrets, and sensitive data handling are reviewed.
- Migrations, retries, idempotency, partial writes, backups, and restore behavior are understood.
- Logs, metrics, traces, alerts, ownership, and actionable runbooks exist.
- Capacity, latency, rate limits, cost bounds, dependency failures, and abuse paths are considered.
- Accessibility, responsive layout, empty/loading/error states, and data deletion/retention are covered.
- Rollout and rollback are executable; compatibility is maintained where required.
- Residual risks, unverified external steps, and explicit go/no-go ownership are documented.

Report `ready`, `conditionally ready`, or `not ready` with evidence. Never silently downgrade a failed critical gate.
