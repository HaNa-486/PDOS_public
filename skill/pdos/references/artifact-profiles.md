# Artifact profiles

Apply the core PDOS lifecycle to any product, then add evidence suited to the artifact.

## Codex Skill

- Define explicit positive and negative trigger examples.
- Keep `SKILL.md` concise; move detailed variants to one-level references and deterministic work to scripts.
- Validate metadata, naming, bundled resource links, and `agents/openai.yaml`.
- Test trigger selection, workflow behavior, failure boundaries, and cross-context behavior.
- Run official Skill validation and fresh-context forward tests without leaking expected answers.
- Separate deterministic fixtures, mock live-runner tests, real live-model trials, and human review in reports.
- Package only required Skill files; keep release notes, installation docs, changelog, and eval harness outside the installable Skill directory.

## Codex Plugin

- Validate `.codex-plugin/plugin.json`, included Skills, MCP/app dependencies, permissions, authentication, and marketplace metadata.
- Exercise install, update, cache-busting, fresh-conversation discovery, connector failure, and uninstall/rollback paths.
- Treat external writes, credentials, publication, and marketplace submission as human-only unless explicitly authorized.

## Web, backend, API, CLI, algorithm, or data product

- Select evidence matching the boundary: schema and contract tests for APIs, user-journey and accessibility checks for UI, reproducible benchmarks and adversarial cases for algorithms, migration/restore evidence for data, and install/exit-code behavior for CLIs.
- Do not weaken release gates merely because the artifact lacks a graphical interface.
