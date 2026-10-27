# Product Development Operating System (PDOS) v0.4 alpha

PDOS is a Codex Skill for evidence-backed product development: uncover assumptions, review issues, define decision boundaries, and carry project context into the next conversation. Its goal is verified production readiness; this alpha does **not** yet demonstrate that outcome or a measured improvement over baseline Codex.

This is `0.4.0-alpha.1`. It is a candidate for controlled local testing, not an authorization for autonomous production deployment.

**Start here:** [Five-minute evaluation](#try-it-without-installing) · [Engineering portfolio](docs/PORTFOLIO.md) · [繁體中文](docs/README.zh-TW.md) · [Validation and limitations](VALIDATION.md) · [Contributing](CONTRIBUTING.md)

Maintained by [HaNa-486](https://github.com/HaNa-486). Developed with AI assistance and published for community inspection and experimentation. This repository contains core PDOS only, not PDOS Autopilot, external connectors, or private development logs. See [publication scope](docs/PUBLICATION.md).

## Why this exists

An AI coding conversation can produce working code while leaving assumptions, unfinished decisions, and verification gaps behind. PDOS makes those concerns explicit and stores a concise handoff in project files. It is intended for substantial features and project reviews, not every typo or one-line fix.

The engineering question is not merely "did the agent finish?" but "what evidence shows it behaved correctly, and which decisions still belong to the user?" The eval harness tests those boundaries separately from the product being developed.

## Try it without installing

Requirements: Git and Python 3.9+ for local tests; the test suite and fixture smoke use the Python standard library. No model credentials are needed for these commands.

```bash
git clone https://github.com/HaNa-486/PDOS_public.git
cd PDOS_public
python -m unittest discover -s tests -v
python evals/run_evals.py --profile smoke
```

Expected: the local suite passes and the smoke report says `fixture_only` and `Release qualified: false`. These are hand-authored fixtures, **not** measurements of live model quality or developer productivity. Installation is optional and described below.

For reviewers: read [the design walkthrough](docs/PORTFOLIO.md), inspect [the Skill](skill/pdos/SKILL.md), then compare [the grader](evals/graders/score.py) with [its known limitations](VALIDATION.md#known-limitations).

## What v0.4 adds

- Three explicit modes: `review`, `review-and-plan`, and `review-and-fix`.
- Every material finding includes evidence, root cause or hypothesis, a recommended solution, alternatives, acceptance criteria, verification, and residual risk.
- `.pdos/AUTONOMY.md` separates `auto-decide`, `independent-review-required`, and `human-only` decisions.
- Saved reviews and remediations have validated schemas and guarded lifecycle transitions.
- v0.3 project state migrates non-destructively with the original archived.
- `pdos_doctor.py` reports installed version, project protocol, state health, duplicate legacy installations, and the next safe action.
- Installer staging, rollback, and backups outside `skills/` prevent incomplete or duplicate Skill discovery.
- Eval 2.0 supports immutable runs, repeated baseline Codex vs Codex+PDOS trials, external live runners, blind semantic grading, human spot-check packets, token/latency metadata, and version regression checks.

## Install the alpha

Run the installer from the cloned repository root (or an extracted source download). It replaces an existing `pdos` installation after staging and structural validation; this is not a full safety or quality certification. Previous versions are backed up under `$CODEX_HOME/skill-backups/pdos/`, outside Skill discovery. This publication does not ship a separately verified release ZIP.

Windows PowerShell:

```powershell
.\install.ps1
```

If local PowerShell policy blocks scripts, run the same installer once with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

macOS or Linux:

```bash
bash install.sh
```

Restart Codex after installation. To keep v0.3 installed while testing this source candidate, do not run the installer; invoke the candidate by its `skill/pdos` path during evaluation.

This is a standalone Skill installation, not a Plugin marketplace installation. It does not install GitHub connectors, configure account authentication, or deploy anything.

## Use PDOS

Start a product:

```text
Use $pdos to take this product from idea to verified production readiness. Only interrupt me for consequential decisions. My idea is: ...
```

Review without changes:

```text
Use $pdos in review mode. Find material issues and include recommended solutions, but do not modify files.
```

Review and create a plan:

```text
Use $pdos in review-and-plan mode. Save an evidence-backed review and prioritized remediation plan, but do not change product behavior.
```

Review and fix authorized findings:

```text
Use $pdos in review-and-fix mode. Apply the autonomy policy, fix only in-scope findings, verify the result, and update remediation evidence.
```

Resume in a fresh task:

```text
Use $pdos to resume this project from .pdos/STATE.md, handle the account-permissions slice, and leave an updated handoff.
```

## What appears in a project

On first use, PDOS safely merges a managed block into root `AGENTS.md` and creates `.pdos/` with:

- `STATE.md` as the concise fresh-context handoff.
- `AUTONOMY.md` as the decision boundary.
- `specs/`, `plans/`, `decisions/`, `reviews/`, `remediations/`, `workstreams/`, and `archive/`.
- ignored `local/` and `private/` directories for machine paths or sensitive local notes.

PDOS does not create root `PROJECT_SPEC.md` or `DEPLOYMENT_CHECKLIST.md`; equivalent durable artifacts live under `.pdos/`.

## Diagnose or remember how to use it

Run:

```powershell
python path\to\pdos\scripts\pdos_doctor.py path\to\project
```

The report shows the current Skill version, project protocol, detected problems, and a suggested next command. `--json` provides machine-readable output. `--repair-safe` only moves legacy discoverable backups outside `skills/`; it does not rewrite product files or autonomy policy.

## Upgrade a v0.3 project

Install v0.4 alpha, restart Codex, open the intended project root, and invoke `$pdos` once. Bootstrap performs a preflight before any writes, preserves the original v0.3 state, creates missing v0.4 policy/remediation templates without overwriting user files, updates the managed `AGENTS.md` block, and refuses future-version downgrades.

## Run validation

Python 3.9+ and the standard library are sufficient.

```bash
python -m unittest discover -s tests -v
python evals/run_evals.py --profile smoke
```

Smoke uses checked-in fixtures and never claims live-model performance. For a real repeated comparison, provide an external runner implementing `pdos-live-runner-v1`:

```bash
python evals/run_evals.py --profile benchmark --live-runner "your-runner" --semantic-runner "your-semantic-runner" --trials 3
```

The `release` profile fails closed unless live trials, deterministic gates, semantic grading, completed human review, and a compatible immutable regression run all pass. See `evals/README.md`.

## Boundaries

- PDOS v0.4 does not orchestrate GitHub, CI, preview deployment, PR approval, merge, or production release. Those belong to the later PDOS Autopilot Skill.
- Checked-in and mock-runner results validate the harness, not actual Codex quality.
- A project autonomy policy can restrict actions but cannot grant permissions beyond the user, platform, sandbox, repository, or external service.

## License

This project is licensed under the [MIT License](LICENSE).
