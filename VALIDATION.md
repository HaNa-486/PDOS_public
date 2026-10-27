# Validation and limitations

## Public snapshot verification

Report date: **2026-10-27 (Asia/Taipei)**. Product version: `0.4.0-alpha.1`.

Checks were run from the separate public-source directory on Windows using Python 3.12.10, Git 2.54.0.windows.1 and PowerShell 7.6.5. They do not certify other runtime versions or operating systems.

| Check | Command / method | Observed result |
| --- | --- | --- |
| Local unit/integration suite | `python -m unittest discover -s tests -v` | 26 tests passed |
| Deterministic fixture smoke | `python evals/run_evals.py --profile smoke` | 12/12 PDOS fixture gates passed; `fixture_only`; `release_qualified: false` |
| Missing-live-evidence refusal | `python evals/run_evals.py --profile release --require-live` with no runner configured | Exit 1; `skipped_no_runner`; `release_qualified: false` (expected refusal) |

The suite covers bootstrap/migration, state validation, workstreams, review/remediation transitions, installer backup and simulated rollback, doctor behavior, runner isolation checks, fixture scoring, and mocked repeated/semantic runs. It does not demonstrate those agent behaviors in real product work.

The optional installed Codex Skill quick-validator was attempted but could not start because its separate `PyYAML` dependency was missing. It is **not** recorded as a pass. The repository's own metadata/reference and installer tests did pass and require no third-party Python dependencies.

Raw generated reports remain under ignored `evals/results/`; they are not published as model benchmark evidence. Re-run the commands to inspect their full output. Dates in generated reports use the runtime's UTC clock; the report date above uses the maintainer's local calendar.

## Known limitations

1. **No demonstrated live-model benefit.** A real repeated baseline Codex versus Codex+PDOS benchmark, semantic judge review, completed human spot check, and compatible live regression comparison are not provided. Token cost, latency, variance, founder interruptions and productivity effects remain unmeasured.
2. **Deterministic grading can over-credit text.** The current grader uses concept/alias matching and counts some structured fields. Negation, echoed concepts, or fabricated evidence can receive credit. A fixture pass is only a harness smoke signal, not proof the task was done. Adversarial grader hardening remains open.
3. **No repository-owned reproducible release builder.** This publication is a source repository. A deterministic allowlist-based ZIP builder and independent archive verifier are still pending. No release ZIP or clean-extracted release certification is claimed here.
4. **Limited platform evidence.** The tests were rerun on Windows/Python 3.12.10. macOS/Linux installation and the declared minimum Python version were not executed in this publication run.
5. **Instructions are not enforcement.** An autonomy policy and review record do not establish tool authorization, actor identity, sandbox isolation, or production safety.
6. **Core PDOS only.** GitHub/CI/preview deployment, PR/merge execution and multi-agent delivery orchestration are not included. Installing this Skill does not install PDOS Autopilot or provider connectors.

## Historical evidence is not current evidence

The private development package previously recorded additional forward tests and packaging checks in August 2026. Those private artifacts are not part of this public snapshot, so this document does not use them as reproducible evidence or claim they were rerun.

## Interpretation

This repository is available for **alpha experimentation, code review and community contribution**. It is not production-qualified. Public-source availability and an MIT License do not imply a successful product release gate.

Before a future quality claim, harden adversarial grading and collect real paired live runs with pinned model/settings, fresh contexts, bounded cost, semantic evaluation, human review and compatible regression evidence. Any published report must distinguish synthetic, mocked and real-model results.
