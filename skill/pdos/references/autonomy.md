# Autonomy policy

Read `.pdos/AUTONOMY.md` before implementation or consequential recommendations.

Classify each decision as:

- `auto-decide`: local, reversible, low-risk, explicitly in scope, and covered by verification and rollback.
- `independent-review-required`: security, privacy, authorization, migrations, high-risk release claims, or another area where independent evidence materially reduces correlated error.
- `human-only`: production actions, irreversible data operations, credentials, money, legal commitments, public publication, changes to the autonomy policy, conflicting product goals, or anything unclassified.

Default to `human-only` when no rule clearly applies. An independent reviewer must receive source evidence and scope, not the parent’s conclusion, before offering an opinion. Agent agreement never overrides failed tests, missing evidence, or a human-only boundary.

Project policy may narrow autonomy. It cannot grant permissions not already authorized by system, developer, user, sandbox, repository, or external-service controls.
