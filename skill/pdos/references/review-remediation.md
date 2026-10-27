# Review to remediation

Use one of three explicit modes.

## Modes

- `review`: remain read-only. Report evidence and solutions in the response. Save artifacts only when the user explicitly asks.
- `review-and-plan`: save a review and remediation plan, but do not change product behavior or external systems.
- `review-and-fix`: review, classify, fix only authorized finding IDs, verify, and update remediation records.

Never infer permission to move from review or planning into implementation. External actions remain subject to the current user request and platform permissions.

## Finding contract

Store a saved review under `.pdos/reviews/<review-id>.md`. Use a collision-safe review ID and finding headings such as `### F-001`. Include for every material finding:

- Severity: critical, high, medium, or low.
- Confidence: high, medium, or low.
- Status: open, planned, in_progress, implemented, verified, blocked, deferred, rejected, or reopened.
- Evidence: reproducible behavior, exact artifact location, or test result.
- User impact.
- Root cause, or a statement labeled `hypothesis` when not proven.
- Recommended solution.
- Alternatives and tradeoffs.
- Affected files or areas.
- Acceptance criteria.
- Verification plan or evidence.
- Residual risk.
- Autonomy class.
- Remediation link.

Do not close a critical finding from a model opinion alone. Preserve the original review snapshot; track execution in a separate remediation record.

## Remediation lifecycle

Use `.pdos/remediations/<remediation-id>.md` and these transitions:

```text
open -> planned -> in_progress -> implemented -> verified
open -> deferred | rejected | blocked
planned -> blocked | deferred | rejected
in_progress -> blocked
implemented -> reopened -> open
blocked -> planned | in_progress | deferred | rejected
```

Require verification evidence before `verified`. Require reason, decision authority, and revisit condition for `deferred` or `rejected`. A release cannot be `ready` while a critical or high finding remains open, planned, in progress, implemented-but-unverified, blocked, or reopened.

Run `scripts/review_remediation.py validate <project-root>` after saving artifacts. Use `scripts/review_remediation.py transition <remediation-file> <status> --evidence "..."` for deterministic state changes.
