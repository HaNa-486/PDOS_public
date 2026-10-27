# PDOS Eval 2.0

Eval 2.0 separates harness validation from live-model evidence.

## Profiles

- `smoke`: grade checked-in baseline and PDOS fixtures. It proves the cases, graders, reports, and gates execute deterministically. It does not measure Codex.
- `benchmark`: run repeated fresh-context baseline Codex and Codex+PDOS trials through an external runner. Without a runner it reports `skipped_no_runner`; `--require-live` makes the skip fail.
- `release`: require live trials, all deterministic PDOS gates, the minimum baseline delta, blind semantic judging, completed human review, paired-model compatibility, and an immutable compatible regression run. Missing evidence fails closed.

Every run has an immutable ID under `results/runs/<run-id>/`. `results/latest.*` is only a convenience copy.

## Smoke

```bash
python evals/run_evals.py --profile smoke
```

The response fixtures are structured captures named `<case-id>.json`. Graders read only behavior-relevant fields instead of matching the entire response, reducing prompt-echo and unrelated-keyword false positives.

## Live runner protocol

Pass a command with `--live-runner`. The harness sends one JSON object on stdin:

```json
{
  "protocol": "pdos-live-runner-v1",
  "case": {"id": "...", "type": "...", "prompt": "..."},
  "condition": "baseline",
  "trial": 1,
  "context_id": "unique-id",
  "fresh_context_required": true,
  "project_path": "isolated fixture copy",
  "prompt_hash": "sha256",
  "fixture_hash": "sha256 or null",
  "skill_enabled": false,
  "skill_path": null,
  "skill_hash": null
}
```

The runner must start a genuinely fresh context, keep baseline free of PDOS, make the candidate Skill at `skill_path` available only for the PDOS condition, and return:

```json
{
  "response": {"structured": "case response"},
  "metadata": {
    "model": "exact model identity",
    "settings": {},
    "tokens": {"input": 100, "output": 50, "total": 150},
    "token_source": "runner"
  }
}
```

When usage is unavailable, token values must be `null`, never zero; wall-clock latency is measured by the harness. Nonzero exit, timeout, malformed JSON, missing structured response, and paired model mismatch are preserved as failed evidence.

Example:

```bash
python evals/run_evals.py --profile benchmark --live-runner "your-adapter" --trials 3
```

### Reference `codex exec` adapter

`runners/codex_exec_runner.py` follows the official non-interactive `codex exec --ephemeral --json` pattern. Configure two already-authenticated, isolated homes:

```text
PDOS_BASELINE_CODEX_HOME   contains no PDOS skill
PDOS_CANDIDATE_CODEX_HOME contains exactly one PDOS skill matching the candidate hash
PDOS_CODEX_MODEL          pins the same model for paired trials
```

The adapter refuses a contaminated baseline, duplicate candidate skills, or a mismatched candidate hash. It does not copy or expose `auth.json` and never creates credentials. Configure the homes yourself, then pass the adapter command as `--live-runner`.

## Semantic judge

`--semantic-runner` receives `pdos-semantic-judge-v1` with anonymous A/B outputs. Condition labels are hidden and deterministically swapped. It must return winner `A`, `B`, or `tie`, numeric A/B scores from 0 to 100, rationale, and evidence. Invalid judgments remain failures.

The semantic rubric covers correctness, evidence, actionability, proportionality, founder burden, production coverage, and fabrication.

## Human spot check

Live runs create `human-review.json` containing trial 1 for every case plus every deterministic failure. Review the raw captures and submit a completed document using `human/review-template.json`. Release qualification requires at least one review and every decision to be `pass`.

## Regression

Use `--compare-run <immutable-run-directory-or-report.json>`. Comparison is rejected when eval/rubric hashes or live model identities are incompatible. A compatible PDOS aggregate drop larger than `--regression-tolerance` fails.

Never manufacture a v0.3 live baseline from hand-authored fixtures. Use a real prior immutable run.

## Cases

The suite covers:

- Skill trigger selection for substantial work and tiny edits.
- Hidden-assumption discovery.
- Founder-interruption minimization.
- Production blindspots.
- End-to-end product workflow.
- Fresh-context state continuity.
- Read-only review behavior.
- Review-and-plan finding actionability.
- Review-and-fix authorization and evidence behavior.
- Consequential autonomy gates.
- Clean-project resistance to fabricated findings.

## Current boundary

This package ships no OpenAI credentials and performs no direct model API call. An external runner must integrate the Codex environment or another approved live-model surface. A passed smoke or mock-runner benchmark never qualifies a release.
