# Changelog

Version entries record development history. This public repository starts with a `0.4.0-alpha.1` source snapshot; it does not contain separate distributions of the earlier versions. See [Migration](docs/MIGRATION.md) only if your project already has older PDOS state.

## Documentation refresh - 2026-10-28

- Reorganize the README around a concrete synthetic example, quick start, engineering evidence, and limitations.
- Move installation, usage, and existing-project upgrade details into dedicated guides.
- Clarify read-only behavior, installation checks, doctor version reporting, and the limits of eval scoring and adapter isolation.
- No product-code or version change; the package remains `0.4.0-alpha.1`.

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
- Add Eval 2.0 per-run reports, structured-response deterministic grading, repeated external live-runner interfaces, A/B semantic judging, human spot-check packets, token/latency metadata, and compatible-run regression gates. These are harness capabilities, not completed live-model evidence; see the [eval guide](evals/README.md) for limitations.
- Add review-mode, finding-actionability, autonomy-gate, and clean-project eval cases while retaining v0.3 behavior cases.

## 0.3.0 - 2026-08-12

- Add durable cross-context state hydration, managed `AGENTS.md` guidance, workstream coordination, migration, privacy, and state validation.

## 0.2.0 - 2026-08-11

- Define the official Product Development Operating System (PDOS) name and add deterministic baseline-vs-PDOS Skill evals.

## 0.1.0

- Introduce the PDOS lifecycle, assumption attack, layered verification, release gate, and project bootstrap.
