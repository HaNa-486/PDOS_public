# Installation and troubleshooting

[README](../README.md) · [Usage](USAGE.md) · [Existing-project migration](MIGRATION.md)

PDOS installs as a standalone Codex Skill. It does not install a Plugin, provider connectors, authentication, or a deployment service. Installing the Skill and initializing PDOS state in a target project are separate actions.

## Before installing

- Start with a non-production project and preserve important work.
- Use Python 3.12 for the tested setup. The package declares Python 3.9+, but current validation was run only on Windows/Python 3.12.10.
- A Codex environment is needed to use the Skill. The [offline tests](../README.md#try-it-without-installing) need neither Codex authentication nor a Skill installation.
- Clone this repository, or extract a source download, and open a terminal in its root. A source download is not a separately verified release ZIP.
- The default installer replaces an existing `pdos` installation. To keep your current installation unchanged, run the offline checks and inspect the source without installing.

## Install

From the repository root:

```bash
python install.py
```

If your Python 3 command is `python3`, use `python3 install.py` instead.

Platform wrappers are also included:

```powershell
# Windows PowerShell
.\install.ps1
```

```bash
# macOS / Linux (wrapper included; not executed in the published validation run)
bash install.sh
```

If PowerShell blocks `.ps1` execution, use the Python command above without changing your execution policy. The PowerShell wrapper accepts `-Destination` and `-CodexHome`; it does **not** have a `-DryRun` option.

The Python installer accepts `--destination`, `--codex-home`, and `--source`. Inspect the available arguments before overriding them:

```bash
python install.py --help
```

## What the installer changes

By default, the destination is `skills/pdos` under `CODEX_HOME`, or under the current user's `.codex` directory when `CODEX_HOME` is unset. `--codex-home` explicitly selects a different home; `--destination` overrides the final Skill path.

The installer stages the Skill, checks required files/name/version, then activates the staged copy. Existing installations are backed up under `skill-backups/pdos/` inside the selected Codex home, outside Skill discovery. It also relocates legacy `skills/pdos.backup-*` directories there.

On activation failure, the installer attempts to restore the prior installation. These are structural checks and tested failure-handling mechanisms, not a complete safety or quality certification. Preserve the printed backup location, especially if you modified the previously installed Skill.

No target product files are changed by the installer. Project initialization or migration happens later, only in an authorized writable workflow; see [Usage](USAGE.md) and [Migration](MIGRATION.md).

## Confirm which copy you are using

Restart Codex after installing, open the intended project, and invoke `$pdos` explicitly. Ask it to identify the loaded Skill path and version before making changes.

For a local diagnostic, run `scripts/pdos_doctor.py` from the **actual Skill directory you want to inspect**, with your project as its argument:

```text
python "<installed-pdos-directory>/scripts/pdos_doctor.py" "<project-directory>" --json
```

Replace the placeholders with your paths. Add `--codex-home` if you selected a non-default home. The doctor reports the version of its **own** Skill directory: running the source copy from this clone does not prove Codex loaded that same installed copy.

The default doctor is read-only. It reports version information, project-state issues, legacy backup directories, and a suggested next action. A missing `.pdos/STATE.md` is normal for a project that has not been initialized, and for a fresh clone of this public source repository; do not bootstrap merely to make that warning disappear during read-only review.

`--repair-safe` is a write operation: it moves detected legacy backup directories outside Skill discovery. Use it only after inspecting the diagnostic and deciding that relocation is appropriate. Doctor reports can contain local paths; redact them before sharing.

## If something goes wrong

- **Python not found:** verify your Python 3 command with `python --version` or `python3 --version`, then invoke the installer with that interpreter.
- **Different version than expected:** compare the loaded Skill path with the installed directory. Restarting alone does not resolve multiple copies or an unintended destination.
- **Project protocol mismatch:** use the [migration guide](MIGRATION.md); do not hand-edit version numbers to suppress checks.
- **Installation error:** retain the error and backup path locally. Check the actual destination and backup before retrying or restoring; do not delete backups to silence discovery warnings.

For a bug report, provide redacted diagnostics, OS/Python versions, reproduction steps, and expected versus actual behavior. See [Contributing](../CONTRIBUTING.md).
