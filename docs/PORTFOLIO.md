# PDOS: architecture and engineering walkthrough

## Problem and scope

AI-assisted product work can lose decisions between conversations, over-interrupt the owner, or mistake a plausible review for verified completion. Product Development Operating System (PDOS) explores a file-based workflow for making those gaps visible.

This walkthrough connects design decisions to source code and tests. PDOS is an open-source alpha maintained by [HaNa-486](https://github.com/HaNa-486) and developed with AI assistance. It does not yet establish live-model benefit or production readiness.

## A short source tour

| Engineering concern | Implementation to inspect | Evidence / boundary |
| --- | --- | --- |
| Recover context after a new conversation | [Bootstrap and migration](../skill/pdos/scripts/bootstrap_project.py), [state template](../skill/pdos/project-template/STATE.md) | Idempotency and migration tests; not proof an agent always reads state |
| Keep review separate from permission to edit | [Skill modes](../skill/pdos/SKILL.md), [remediation transitions](../skill/pdos/scripts/review_remediation.py) | Validated records and tests; not an OS-level permission boundary |
| Keep consequential decisions with the owner | [Autonomy policy template](../skill/pdos/project-template/AUTONOMY.md) | Policy can restrict authority, never grant credentials or external permissions |
| Upgrade an installation without discoverable backup duplicates | [Installer](../install.py), [installer tests](../tests/test_install.py) | Staging, backup and simulated rollback tests |
| Evaluate the Skill rather than only its generated product | [Eval runner](../evals/run_evals.py), [cases](../evals/cases), [graders](../evals/graders) | Fixture smoke and mock protocol tests; real model benefit remains unmeasured |

## Design decisions and tradeoffs

1. **Files over hidden conversation memory.** A concise `.pdos/STATE.md` points to relevant specs and decisions. Files are reviewable and portable, but stale state and process overhead remain risks.
2. **Three modes over blanket autonomy.** `review`, `review-and-plan`, and `review-and-fix` make the requested mutation scope explicit. Instructions alone cannot enforce a sandbox or external authorization.
3. **Separate evidence levels.** Deterministic fixtures test harness behavior. Mock runners test integration contracts. Live paired trials, semantic judging and human review are separate requirements for quality claims.
4. **Fail closed on missing release evidence.** A green smoke test must not turn into production approval. The release profile requires additional evidence and a compatible regression comparison.
5. **Core Skill separate from delivery orchestration.** This repository does not bundle Autopilot, provider connectors, multi-agent execution, or production deployment. That keeps the installation and evaluation boundary smaller.

## Example workflow (illustrative, not a measured customer outcome)

An owner asks for a document-analysis feature. A PDOS-guided review should investigate upload constraints, authorization, retry behavior and failure recovery, then record evidence and recommendations. In read-only mode it must not change the product. Only an authorized fix workflow should implement changes, verify acceptance criteria, and leave an updated handoff.

The [hidden-assumption](../evals/cases/hidden-assumption-discovery.json), [read-only review](../evals/cases/review-read-only-no-mutation.json), and [end-to-end workflow](../evals/cases/end-to-end-product-workflow.json) cases make parts of that intent inspectable. Their fixture results do not demonstrate a real agent completed the workflow.

## What is demonstrated, and what is not

See [VALIDATION.md](../VALIDATION.md) for the dated rerun evidence. The repository supports exercising local state tools, installation behavior, deterministic grading, and mocked runner contracts.

It does **not** establish increased developer productivity, fewer real founder interruptions, improved production reliability, or lower token cost. No such percentage or benchmark advantage is claimed.

The current grader can over-credit keyword matches, negation, echoed concepts, or fabricated evidence. A repository-owned deterministic release ZIP builder is also missing. Both are documented next steps, not completed achievements.

## Explore the implementation

- Run the two offline commands in the [README](../README.md#try-it-without-installing).
- Inspect one case, its baseline and PDOS fixture responses, expected outcome, and scoring implementation together.
- Read the installation rollback test and the project-state migration tests.
- Challenge the grader with counterexamples before trusting a score.
- Propose a small, testable improvement via the [contribution guide](../CONTRIBUTING.md).
