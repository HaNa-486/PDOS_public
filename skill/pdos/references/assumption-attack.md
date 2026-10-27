# Assumption attack

Probe these surfaces before implementation and again before release:

- Identity and permissions: anonymous, expired session, role changes, tenant isolation, ownership.
- Input and data: empty, malformed, duplicated, oversized, stale, deleted, migrated, partially written.
- Time and concurrency: double submit, refresh, retries, races, idempotency, timezone, long-running work.
- Dependencies: timeout, rate limit, unavailable API, malformed AI output, version drift, partial success.
- Lifecycle and recovery: cancel, resume, retry, rollback, restore, deletion, retention, audit.
- Experience: loading, empty, error, success, mobile layout, keyboard, accessibility, clear next action.
- Operations: secrets, logs, metrics, alerts, cost bounds, capacity, abuse, deployment and rollback.

For each meaningful assumption, record:

```text
Statement | class | confidence | impact | evidence | chosen default | validation
```

Ask the founder only when the impact is consequential and no safe reversible default exists. Bundle related decisions, recommend an option, and explain the consequence of silence.
