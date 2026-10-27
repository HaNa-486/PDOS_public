# Product Development Operating System (PDOS)

**Structured product reviews, explicit decisions, and project handoffs for AI-assisted development.**

PDOS is a Codex Skill: reusable workflow instructions backed by Python tools. It helps organize requirements, review findings, authorized fixes, and verification evidence in files that can be inspected and resumed in a later conversation.

**Status:** `0.4.0-alpha.1` · MIT licensed · For non-production experimentation. The public examples and eval fixtures use **synthetic demonstration data**, not customer or production data.

[Quick start](#try-it-without-installing) · [Installation](docs/INSTALLATION.md) · [Usage guide](docs/USAGE.md) · [Architecture and tradeoffs](docs/PORTFOLIO.md) · [繁體中文](docs/README.zh-TW.md)

## Why use it?

A coding conversation can leave important questions unresolved: Which assumptions were checked? Was a change authorized? What evidence supports a fix? What should the next session do?

PDOS provides a workflow for recording those answers. It is intended for substantial features and project reviews; small edits usually do not need this process. It is a local Skill and toolkit, not a hosted application or an autonomous deployment service.

## Example: finding missing requirements

Consider this request from the included PDF-analysis test case:

```text
Create a site where users sign in, upload PDFs, and AI analyzes them and shows the result.
```

The hand-authored expected response includes concerns such as:

- Reject oversized or malformed PDFs before processing.
- Persist job status so a page refresh can recover an in-progress analysis.
- Enforce access checks on every file and result lookup.

These are **synthetic expected-response examples, not output from a recorded live model run**. Inspect the [input case](evals/cases/hidden-assumption-discovery.json), [response fixture](evals/fixtures/responses/pdos/hidden-assumption-discovery.json), and [scoring logic](evals/graders/score.py) together. In actual use, a review should connect findings to repository evidence and propose acceptance criteria before changes are authorized.

## Try it without installing

Use Git and Python 3.12 for the tested setup (Windows/Python 3.12.10). The package declares Python 3.9+; the minimum version and other platforms have not been verified in the published validation run. If your Python 3 command is `python3`, substitute it below.

```bash
git clone https://github.com/HaNa-486/PDOS_public.git
cd PDOS_public
python -m unittest discover -s tests -v
python evals/run_evals.py --profile smoke
```

These offline checks use the Python standard library, do not require model credentials, and do not change your normal Codex installation. They exercise the tools and harness, not a live agent. The published validation records **26 passing automated tests** and **12 passing PDOS fixture cases**.

The smoke report should say `fixture_only` and `Release qualified: false`. That is expected: fixture scores are not evidence that PDOS improves model quality or developer productivity. See [validation and limitations](VALIDATION.md).

## Use it in a project

Follow the [installation guide](docs/INSTALLATION.md), open a non-production project in Codex, and start with a read-only review:

```text
Use $pdos in review mode. Inspect this project's requirements and failure paths.
Report evidence-backed issues, recommended fixes, and acceptance criteria.
Do not modify code or create project files.
```

Review the findings before choosing `review-and-plan` or authorizing `review-and-fix`. Strict `review` does not initialize or update project files. Writable workflows can create `.pdos/` handoff records and managed `AGENTS.md` guidance. The [usage guide](docs/USAGE.md) explains each mode, project files, and resuming work.

## Engineering highlights

| Concern | Implementation | Evidence to inspect |
| --- | --- | --- |
| Recover project context | File-based state, preflight checks, and migration archives | [Bootstrap tests](tests/test_bootstrap.py) |
| Separate review from authorized changes | Three workflow modes, policy templates, and validated remediation transitions | [Skill contract](skill/pdos/SKILL.md), [state-tool tests](tests/test_state_tools.py) |
| Handle installation failures | Staging, structural checks, backups outside Skill discovery, and rollback handling | [Installer](install.py), [failure-injection tests](tests/test_install.py) |
| Evaluate workflow behavior | Baseline/PDOS fixtures, external-runner interfaces, per-run reports, and release-evidence checks | [Eval guide](evals/README.md), [runner tests](tests/test_eval_runner.py) |

The architecture combines instructions, deterministic Python helpers, and local project records. Instructions and policy files are **not** a security sandbox or a grant of external permissions. Read the [design walkthrough](docs/PORTFOLIO.md) for the tradeoffs and source tour.

## Validation and scope

- **Implemented and locally tested:** state tooling, installer behavior, deterministic fixture evaluation, and mocked runner contracts.
- **Not established:** real-model benchmark improvements, reduced cost or interruptions, or production readiness. The current grader can over-credit keywords or unsupported claims.
- **Not included:** PDOS Autopilot, provider connectors, GitHub/CI/deployment orchestration, or a verified release ZIP builder.

See the [full validation record](VALIDATION.md) before relying on a result. Report security concerns using [SECURITY.md](SECURITY.md), without posting sensitive data publicly.

## Documentation and contributing

- [Installation and troubleshooting](docs/INSTALLATION.md)
- [Usage, review modes, and project handoffs](docs/USAGE.md)
- [Migration guide for existing projects](docs/MIGRATION.md) and [development history](CHANGELOG.md)
- [Evaluation protocols](evals/README.md) and [public source scope](docs/PUBLICATION.md)
- [Contributing](CONTRIBUTING.md) — regression tests, adversarial eval cases, and reproducible bug reports are welcome.

Maintained by [HaNa-486](https://github.com/HaNa-486), developed with AI assistance, and distributed under the [MIT License](LICENSE).
