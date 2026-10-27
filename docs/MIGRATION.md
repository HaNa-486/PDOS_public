# Migrating an existing PDOS project

[README](../README.md) · [Installation](INSTALLATION.md) · [Usage](USAGE.md) · [Changelog](../CHANGELOG.md)

This guide is for projects that already have PDOS state, particularly protocol `0.3.0`. New users do not need an older release to use the current alpha. This public repository starts with a v0.4 alpha source snapshot; earlier version entries describe development history, not releases bundled here.

## Installation upgrade versus project migration

Replacing the installed Skill updates its instructions and tools. Migrating a project updates that project's `.pdos` records and managed guidance. Installing the new Skill does not automatically migrate every project on your computer.

## Before migrating

1. Commit or back up your project's files, including local records that Git ignores. Check for unfinished changes.
2. Inspect the existing protocol in `.pdos/STATE.md` and the project autonomy policy. Do not change version numbers to bypass compatibility checks.
3. Install the candidate using the [installation guide](INSTALLATION.md), preserving any printed backup path, then restart Codex.
4. Open the intended project and explicitly authorize state migration. Plain `review` remains read-only and must not trigger it.

Example request:

```text
Use $pdos to migrate this project's existing v0.3 PDOS state to the
installed v0.4 alpha protocol. Preserve existing project decisions and
policy, validate the result, and report the diff and archive location.
Do not implement product changes or perform external writes.
```

## What the migration code does

The [bootstrap script](../skill/pdos/scripts/bootstrap_project.py) preflights version compatibility and managed instruction blocks before writing. For older project state it archives the original `STATE.md`, creates an updated handoff, adds missing templates, updates the protocol marker, and synchronizes the managed guidance. Existing files such as a project autonomy policy are not replaced by the template-copy step.

The original state normally goes under `.pdos/archive/`. When the script detects an absolute user path in it, the archive goes under ignored `.pdos/local/migration-archives/` instead. This path check is a limited heuristic, not a general sensitive-data scanner; inspect archives before sharing them.

The script refuses newer protocols and differing prerelease identifiers with the same core version. It uses atomic writes per file, but the entire multi-file migration is **not** one all-or-nothing transaction. Keep your own backup and inspect the result if any step fails.

## Validate and reconcile

From the PDOS source repository root, the explicit commands are:

```text
python skill/pdos/scripts/bootstrap_project.py "<project-directory>"
python skill/pdos/scripts/validate_project_state.py "<project-directory>" --strict
```

Replace the placeholder with the intended target. **The first command writes project files**; run it only after the preparation and authorization above. You may instead use the equivalent scripts from the actual installed Skill directory.

Review the changed files, the archived state, preserved policy, and handoff pointers. Migration can leave placeholders or stale repository identity that need reconciliation; do not equate a successful bootstrap exit with a finished product review. Resolve reported issues before resuming implementation.

If preflight rejects the project, preserve it and diagnose the cause. Do not force a downgrade or remove the previous state merely to make validation pass. See [validation evidence and limitations](../VALIDATION.md) for what has actually been tested.
