# Using PDOS

[README](../README.md) · [Installation](INSTALLATION.md) · [Migration](MIGRATION.md)

PDOS is intended for substantial product work and project reviews. For an isolated typo or small mechanical edit, a normal focused request is usually sufficient. Use a non-production project while evaluating this alpha.

## Choose what may change

After installing the Skill, invoke `$pdos` in the intended project and specify the mode:

| Mode | Intended behavior | Write boundary |
| --- | --- | --- |
| `review` | Report evidence, issues, and recommended solutions in the conversation | No product or PDOS file writes unless separately requested |
| `review-and-plan` | Save an evidence-backed review and prioritized remediation plan | May initialize/update PDOS records and managed guidance; no product implementation |
| `review-and-fix` | Implement specifically authorized findings, test them, and record evidence | Scoped product and PDOS changes, within user and tool permissions |

These are workflow contracts, not operating-system enforcement. Platform permissions and the user's authorization still control what may run. Agreement between agents is not verification evidence.

### Review without changes

```text
Use $pdos in review mode. Find material issues and include evidence,
recommended solutions, and acceptance criteria. Do not modify files,
initialize PDOS state, or perform external writes.
```

Strict review reads existing state when available but does not bootstrap, migrate, or synchronize `AGENTS.md`. Ask separately if you want the report saved.

### Save a plan

```text
Use $pdos in review-and-plan mode. Save an evidence-backed review and
prioritized remediation plan. You may create the required PDOS records
and project guidance, but do not change product code or external systems.
```

### Implement an approved fix

```text
Use $pdos in review-and-fix mode for finding F-001 from the saved review.
Follow the project autonomy policy, change only the approved scope,
run its acceptance checks, and record evidence and remaining risks.
Do not deploy, merge, or expand the task without authorization.
```

Replace `F-001` with an actual finding from your review. A saved finding is not itself permission to implement it.

### Start a new product

```text
Use $pdos to explore this idea: [describe the product and intended users].
Identify assumptions, constraints, and acceptance criteria. You may create
planning and handoff files, but ask before implementation or external actions.
```

This requests a bounded planning workflow, not guaranteed production readiness.

## Project records and new conversations

In an authorized writable workflow, bootstrap creates or upgrades `.pdos/` and synchronizes a managed block in `AGENTS.md` (also `AGENTS.override.md` if present). Existing content outside that managed block is retained; malformed blocks cause preflight refusal.

- `.pdos/STATE.md`: concise handoff and pointers to the relevant work.
- `.pdos/AUTONOMY.md`: project decision boundaries, which cannot grant additional tool permissions.
- Specs, plans, reviews, and remediations: requirements, findings, decisions, and verification evidence.
- `.pdos/local/` and `.pdos/private/`: ignored local notes; not secure secret storage.

Do not assume a new conversation remembers the previous one. Ask it to read the current files and reconcile them with the repository:

```text
Use $pdos to resume from .pdos/STATE.md. Check the current repository
against the handoff, summarize the next authorized step, and identify
stale or conflicting information before making changes.
```

Skill loading and instruction following are not guaranteed by the presence of these files. Check which Skill was loaded and what it actually read when continuity matters.

In your own product, review what should be shared versus kept local. In **this public source repository**, root `.pdos/` is intentionally ignored and absent from a fresh clone; distributable templates and synthetic fixtures are versioned separately. No private development history is required to contribute.

For diagnostics, including the distinction between a source-copy version and an installed-copy version, see [Installation and troubleshooting](INSTALLATION.md#confirm-which-copy-you-are-using).
