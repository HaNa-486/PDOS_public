# Contributing

PDOS is an experimental alpha. Small, reproducible fixes and adversarial eval cases are especially useful. No maintainer response time or release schedule is guaranteed.

## Local setup

Use Git and Python 3.12 for the tested setup. The package declares Python 3.9+, but its minimum version has not been verified in the published validation run. No production credentials, model API keys, or installed PDOS Skill are needed to run the offline suite:

```bash
python -m unittest discover -s tests -v
python evals/run_evals.py --profile smoke
git diff --check
```

Do not run the default installer just to contribute: it changes your local Skill installation. Installer tests use temporary destinations.

## Propose a change

1. Open an issue for a significant design change; describe the problem, evidence, acceptance criteria, and tradeoffs.
2. Fork the repository and work on a small branch.
3. Add a regression test and update relevant documentation.
4. Run the offline checks above. Report commands, runtime/OS, and anything not tested.
5. Submit a pull request with a short explanation and evidence. Do not describe fixture or mock scores as live-model performance.

No private `.pdos` history is required to contribute. Generated state, local audit scratch, and raw evaluation reports are ignored in this public source repository. The distributable templates under `skill/pdos/project-template/` and synthetic fixtures under `evals/fixtures/` remain versioned.

## Privacy and scope

- Use synthetic examples; never include customer data, credentials, personal paths, or private conversation transcripts.
- Use a GitHub noreply commit email if you do not want a personal address published.
- Review generated reports before sharing: live captures can contain prompts, paths, and account-specific output.
- Follow [SECURITY.md](SECURITY.md) for suspected vulnerabilities.
- Paid/live benchmarks, external writes, and release publication require separate maintainer authorization.

## Useful next contributions

- Adversarial tests for negation, prompt echo, and fabricated evidence, followed by grader hardening.
- A deterministic, allowlist-based release builder with tamper detection and clean-extraction tests.
- Reproducible live paired trials with pinned models, cost limits, semantic review, and human spot checks.
- Installer verification on macOS and Linux, with exact environment and results recorded.

Contributions are intended to be distributed under the repository's [MIT License](LICENSE). Do not submit material you are not entitled to contribute.
