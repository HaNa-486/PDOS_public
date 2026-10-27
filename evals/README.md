# PDOS Eval 2.0

Eval 2.0 separates harness validation from live-model evidence.

## Profiles

- `smoke`: grade checked-in baseline and PDOS fixtures. It proves the cases, graders, reports, and gates execute deterministically. It does not measure Codex.
- `benchmark`: run repeated fresh-context baseline Codex and Codex+PDOS trials through an external runner. Without a runner it reports `skipped_no_runner`; `--require-live` makes the skip fail.
- `release`: require live trials, all deterministic PDOS gates, the minimum baseline delta, blind semantic judging, completed human review, paired-model compatibility, and an immutable compatible regression run. Missing evidence fails closed.

Every run creates a new uniquely named directory under `results/runs/<run-id>/`. `results/latest.*` is only a convenience copy. Preserve prior run directories unchanged for regression comparisons; they are ordinary local files, not a tamper-proof evidence store.

## Smoke

```bash
python evals/run_evals.py --profile smoke
```

The response fixtures are hand-authored synthetic captures named `<case-id>.json`. Graders select fields according to the case type, but concept checks still use normalized substring matching and some checks count fields or self-reported flags. Negation, prompt echo, or fabricated evidence can receive credit. Smoke demonstrates harness execution, not resistance to these failure modes or real agent performance. See [known limitations](../VALIDATION.md#known-limitations).

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

`runners/codex_exec_runner.py` invokes `codex exec --ephemeral --json`. Its integration contract is covered by local tests; a completed real Codex benchmark is not provided. Before a live run, verify compatibility with your installed CLI and configure two already-authenticated, isolated homes:

```text
PDOS_BASELINE_CODEX_HOME   contains no PDOS skill
PDOS_CANDIDATE_CODEX_HOME contains exactly one PDOS skill matching the candidate hash
PDOS_CODEX_MODEL          pins the same model for paired trials
```

The adapter checks for PDOS metadata in top-level `skills/*/SKILL.md` entries under each selected home. Within that search scope it rejects a detected baseline PDOS Skill, a candidate count other than one, or a candidate hash mismatch. This is not a full audit of plugin caches, project instructions, other discovery locations, or runtime configuration. The operator remains responsible for baseline isolation and model configuration.

The adapter does not copy credential files or create credentials; authentication must already be configured. It can retain model output, usage metadata, and command errors, so review captures and logs for sensitive content before sharing. Configure the homes yourself, then pass the adapter command as `--live-runner`. Live runs may incur model costs and are separate from the offline smoke test.

## Semantic judge

`--semantic-runner` receives `pdos-semantic-judge-v1` with anonymous A/B outputs. Condition labels are hidden and deterministically swapped. It must return winner `A`, `B`, or `tie`, numeric A/B scores from 0 to 100, rationale, and evidence. Invalid judgments remain failures.

The semantic rubric covers correctness, evidence, actionability, proportionality, founder burden, production coverage, and fabrication.

## Human spot check

Live runs create `human-review.json` containing trial 1 for every case plus every deterministic failure. Review the raw captures and submit a completed document using `human/review-template.json`. Release qualification requires at least one review and every decision to be `pass`.

## Regression

Use `--compare-run <immutable-run-directory-or-report.json>`. Comparison is rejected when eval/rubric hashes or live model identities are incompatible. A compatible PDOS aggregate drop larger than `--regression-tolerance` fails.

Never manufacture a prior live-model baseline from hand-authored fixtures. Use a real compatible prior run preserved unchanged.

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
