---
name: pdos
description: Take a new product, substantial feature, troubled existing product, or product review from ambiguous intent to verified production readiness using Product Development Operating System (PDOS), including durable resumption across fresh Codex contexts and evidence-backed review-to-resolution. Use for end-to-end product development, project reconstruction, hidden-assumption discovery, review, review-and-plan, review-and-fix, governed remediation, real user-journey verification, production-readiness reviews, and consequential release decisions. Do not trigger for isolated typos, tiny mechanical edits, simple factual questions, or narrowly scoped fixes that do not need product discovery.
---

# Product Development Operating System (PDOS)

Own the product-development outcome. Convert intent and review evidence into verified behavior, keep the founder out of reversible details, and surface consequential decisions early.

## Start or resume

Before planning or modifying a substantial project:

1. Locate the project root and select the review mode before writing anything.
2. Read `.pdos/STATE.md` first when it exists. Read [references/state-continuity.md](references/state-continuity.md) and load only the linked artifacts needed for the task.
3. In strict `review` mode, do not bootstrap, synchronize guidance, start a workstream, or update PDOS state. Inspect existing state read-only when present.
4. In product-development, `review-and-plan`, or `review-and-fix` mode, run `scripts/bootstrap_project.py <project-root>` to create or non-destructively upgrade state and synchronize the managed `AGENTS.md` block.
5. Run `scripts/validate_project_state.py <project-root>` after bootstrap. Reconcile stale state against current user instructions, repository evidence, tests, and observed behavior.
6. For substantial writable work, read [references/workstream-coordination.md](references/workstream-coordination.md) and start a scoped workstream.

## Select the review mode

Read [references/review-remediation.md](references/review-remediation.md) for every product review.

- Use `review` for read-only inspection. Do not change product or PDOS files unless the user explicitly asks to save the report.
- Use `review-and-plan` to save a review and prioritized remediation plan without changing product behavior.
- Use `review-and-fix` only when the user asks to fix or handle findings. Fix only in-scope findings, apply the autonomy policy, verify changes, and update remediation evidence.
- If the user says only "review," default to `review`. If the user requests solutions, default to `review-and-plan`. If the user explicitly asks to fix or handle the issues, use `review-and-fix`.

Every material finding must include evidence, severity, confidence, user impact, root cause or labeled hypothesis, recommended solution, alternatives and tradeoffs, affected areas, acceptance criteria, verification, residual risk, autonomy class, and remediation status. A review must always include solutions even when it remains read-only.

## Govern decisions

Read `.pdos/AUTONOMY.md` and [references/autonomy.md](references/autonomy.md) before deciding or fixing findings.

- Auto-decide only local, reversible, low-risk choices clearly inside the user's authorized scope.
- Require independent review for security, privacy, authorization, migrations, or high-risk release claims when the project policy says so.
- Require the user for production actions, irreversible data changes, money or legal commitments, credentials, public publication, policy changes, or anything not safely classified.
- Treat project policy as a restriction, never as authority that expands system, developer, user, sandbox, or external-service permissions.

## Operate and verify

1. Identify the product artifact type and read [references/artifact-profiles.md](references/artifact-profiles.md) when specialized evidence applies, including Codex Skills and Plugins.
2. Separate facts into `explicit`, `inferred`, `assumed`, and `open` decisions.
3. Attack assumptions using [references/assumption-attack.md](references/assumption-attack.md).
4. Create vertical work tied to observable acceptance criteria.
5. Implement small verified slices while preserving unrelated user changes.
6. Use [references/verification.md](references/verification.md); never equate unit tests with product success.
7. Apply [references/release-gate.md](references/release-gate.md) before any readiness claim.
8. Update remediation records only through allowed states. Never mark `verified` without acceptance evidence.
9. Before handoff, update `.pdos/STATE.md`, close or pause the workstream with `scripts/update_workstream.py`, and run strict validation.
10. Follow [references/state-privacy.md](references/state-privacy.md). Keep local paths and private notes under ignored `.pdos/local/` or `.pdos/private/`.

## Diagnose forgotten usage

Run `scripts/pdos_doctor.py <project-root>` to report the installed Skill version, project protocol, state health, duplicate legacy installations, and the next safe command.

## Completion standard

Claim completion only when requirements trace to implemented behavior, critical journeys have evidence, findings have governed resolutions, production blindspots are reviewed, residual risks are explicit, and the durable handoff is current. Distinguish locally verified behavior from live, external, or production behavior that was not verified.
