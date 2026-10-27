# Changelog

## 0.4.0-alpha.1 - 2026-08-13

- Add `review`, `review-and-plan`, and `review-and-fix` contracts.
- Add evidence-backed finding schema, separate remediation ledger, guarded transitions, and release conflict checks.
- Add conservative project autonomy policy with explicit human-only defaults.
- Add v0.3 migration preflight, atomic file writes, future-version refusal, and user-policy preservation.
- Remove absolute worktree paths from shared state; store machine identity only under ignored `.pdos/local/`.
- Replace exact-HEAD state validation with observed-commit ancestry semantics.
- Add workstream close/transition tooling.
- Add a read-only doctor with version, project health, duplicate-install detection, and safe legacy-backup relocation.
- Replace discoverable sibling backups with staged installation, rollback, and backups under `$CODEX_HOME/skill-backups/`.
- Add Eval 2.0 immutable runs, field-aware deterministic grading, repeated external live-runner comparisons, blind semantic grading, human spot-check packets, token/latency metadata, and compatible-run regression gates.
- Add review-mode, finding-actionability, autonomy-gate, and clean-project eval cases while retaining v0.3 behavior cases.

## 0.3.0 - 2026-08-12

- Add durable cross-context state hydration, managed `AGENTS.md` guidance, workstream coordination, migration, privacy, and state validation.

## 0.2.0 - 2026-08-11

- Define the official Product Development Operating System (PDOS) name and add deterministic baseline-vs-PDOS Skill evals.

## 0.1.0

- Introduce the PDOS lifecycle, assumption attack, layered verification, release gate, and project bootstrap.
