#!/usr/bin/env python3
"""PDOS Eval 2.0: deterministic smoke plus optional repeated live comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import statistics
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVAL_ROOT = Path(__file__).resolve().parent
PACKAGE_ROOT = EVAL_ROOT.parent
sys.path.insert(0, str(EVAL_ROOT))

from graders.regression import compare as compare_regression  # noqa: E402
from graders.score import grade, load_json  # noqa: E402
from graders.semantic import judge as semantic_judge  # noqa: E402
from runners.command_runner import run_command  # noqa: E402


EVAL_VERSION = "2.0.0-alpha.1"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def hash_path(path: Path) -> str:
    digest = hashlib.sha256()
    if not path.exists():
        digest.update(b"missing")
    elif path.is_file():
        digest.update(path.read_bytes())
    else:
        for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
            digest.update(item.relative_to(path).as_posix().encode())
            digest.update(item.read_bytes())
    return digest.hexdigest()


def skill_hash() -> str:
    return hash_path(PACKAGE_ROOT / "skill" / "pdos")


def rubric_hash(cases: list[Path]) -> str:
    digest = hashlib.sha256()
    digest.update((EVAL_ROOT / "graders" / "score.py").read_bytes())
    for path in cases:
        digest.update(path.read_bytes())
        digest.update((EVAL_ROOT / "expected" / path.name).read_bytes())
    return digest.hexdigest()


def evaluate_fixture(candidate_dir: Path, cases: list[Path]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for case_path in cases:
        case = load_json(case_path)
        expected = load_json(EVAL_ROOT / "expected" / case_path.name)
        response_path = candidate_dir / case_path.name
        if not response_path.exists():
            results.append({"id": case["id"], "type": case["type"], "score": 0.0, "passed": False, "details": {"error": f"Missing response: {response_path}"}})
            continue
        try:
            results.append(grade(case, expected, load_json(response_path)))
        except (ValueError, KeyError, TypeError) as error:
            results.append({"id": case["id"], "type": case["type"], "score": 0.0, "passed": False, "details": {"error": str(error)}})
    return results


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    score = round(sum(float(item["score"]) for item in results) / max(1, len(results)), 2)
    return {"score": score, "passed": sum(1 for item in results if item["passed"]), "total": len(results)}


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * fraction))))
    return round(ordered[index], 3)


def metric_summary(captures: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [float(item["metadata"]["wall_latency_ms"]) for item in captures if isinstance(item.get("metadata", {}).get("wall_latency_ms"), (int, float))]
    token_values = [float(item["metadata"]["tokens"]["total"]) for item in captures if isinstance(item.get("metadata", {}).get("tokens", {}).get("total"), (int, float))]
    return {
        "latency_ms": {"median": round(statistics.median(latencies), 3) if latencies else None, "p95": percentile(latencies, 0.95)},
        "total_tokens": {"median": round(statistics.median(token_values), 3) if token_values else None, "p95": percentile(token_values, 0.95), "available": bool(token_values)},
    }


def _snapshot(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {item.relative_to(path).as_posix(): hash_path(item) for item in path.rglob("*") if item.is_file()}


def run_live_capture(command: str, case_path: Path, condition: str, trial: int, run_dir: Path) -> dict[str, Any]:
    case = load_json(case_path)
    expected = load_json(EVAL_ROOT / "expected" / case_path.name)
    fixture_relative = case.get("fixture")
    fixture_source = EVAL_ROOT / fixture_relative if fixture_relative else None
    context_id = uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix=f"pdos-eval-{case['id']}-{condition}-{trial}-") as temporary:
        workdir = Path(temporary)
        fixture_copy = workdir / "project"
        if fixture_source and fixture_source.exists():
            if fixture_source.is_dir():
                shutil.copytree(fixture_source, fixture_copy)
            else:
                fixture_copy.mkdir()
                shutil.copy2(fixture_source, fixture_copy / fixture_source.name)
        before = _snapshot(fixture_copy)
        request = {
            "protocol": "pdos-live-runner-v1",
            "case": case,
            "condition": condition,
            "trial": trial,
            "context_id": context_id,
            "fresh_context_required": True,
            "project_path": str(fixture_copy),
            "fixture_hash": hash_path(fixture_source) if fixture_source else None,
            "prompt_hash": sha256_bytes(case["prompt"].encode()),
            "skill_enabled": condition == "pdos",
            "skill_path": str(PACKAGE_ROOT / "skill" / "pdos") if condition == "pdos" else None,
            "skill_hash": skill_hash() if condition == "pdos" else None,
            "sandbox": "read-only" if case.get("mutation_policy", "read_only") == "read_only" else "workspace-write",
        }
        try:
            result = run_command(command, request)
            response = result.get("response")
            if not isinstance(response, dict):
                raise ValueError("Live runner must return a structured response object")
            deterministic = grade(case, expected, response)
            error = None
        except (OSError, ValueError, RuntimeError, TimeoutError) as exception:
            result = {"metadata": {"tokens": {"input": None, "output": None, "total": None}, "token_source": "unavailable"}}
            response = {}
            deterministic = {"id": case["id"], "type": case["type"], "score": 0.0, "passed": False, "details": {"error": str(exception)}}
            error = str(exception)
        after = _snapshot(fixture_copy)
        changed = sorted(name for name in set(before) | set(after) if before.get(name) != after.get(name))
        policy = case.get("mutation_policy")
        mutation_error = None
        if policy == "read_only" and changed:
            mutation_error = f"Read-only case changed files: {changed}"
        elif policy == "pdos_only":
            outside = [name for name in changed if not (name.startswith(".pdos/") or name in {"AGENTS.md", "AGENTS.override.md"})]
            if outside:
                mutation_error = f"Planning case changed product files: {outside}"
            elif case.get("requires_change") and not changed:
                mutation_error = "Planning case did not create durable PDOS artifacts"
        elif policy == "product_required" and not any(not name.startswith(".pdos/") and name not in {"AGENTS.md", "AGENTS.override.md"} for name in changed):
            mutation_error = "Fix case did not change a product file"
        if mutation_error:
            deterministic["passed"] = False
            deterministic["details"]["mutation_error"] = mutation_error
            error = error or mutation_error
    capture = {
        "case_id": case["id"], "condition": condition, "trial": trial, "context_id": context_id,
        "prompt_hash": request["prompt_hash"], "fixture_hash": request["fixture_hash"],
        "skill_hash": request["skill_hash"], "response": response, "metadata": result.get("metadata", {}),
        "changed_files": changed, "mutation_policy": case.get("mutation_policy"), "deterministic": deterministic, "error": error,
    }
    capture_dir = run_dir / "captures" / condition
    capture_dir.mkdir(parents=True, exist_ok=True)
    (capture_dir / f"{case['id']}-trial-{trial}.json").write_text(json.dumps(capture, indent=2) + "\n", encoding="utf-8")
    return capture


def summarize_live(captures: list[dict[str, Any]], cases: list[Path]) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    for case_path in cases:
        case_id = load_json(case_path)["id"]
        rows = [item["deterministic"] for item in captures if item["case_id"] == case_id]
        score = round(sum(float(row["score"]) for row in rows) / max(1, len(rows)), 2)
        summaries.append({"id": case_id, "score": score, "passed": bool(rows) and all(row["passed"] for row in rows), "trials": rows})
    return {"summary": aggregate(summaries), "cases": summaries, "metrics": metric_summary(captures)}


def markdown(report: dict[str, Any]) -> str:
    lines = ["# PDOS Eval 2.0 report", "", f"Run: `{report['run_id']}`", f"Profile: **{report['profile']}**", f"Benchmark status: **{report['benchmark_status']}**", f"Release qualified: **{str(report['release_qualified']).lower()}**", "", "| Case | Baseline | PDOS | Delta | PDOS gate |", "|---|---:|---:|---:|---|"]
    baseline = {item["id"]: item for item in report["baseline"]["cases"]}
    for item in report["pdos"]["cases"]:
        base_score = float(baseline.get(item["id"], {}).get("score", 0))
        lines.append(f"| {item['id']} | {base_score:.2f} | {float(item['score']):.2f} | {float(item['score']) - base_score:+.2f} | {'PASS' if item['passed'] else 'FAIL'} |")
    lines.extend(["", f"Baseline aggregate: **{report['baseline']['summary']['score']:.2f}**", f"PDOS aggregate: **{report['pdos']['summary']['score']:.2f}**", ""])
    if report["benchmark_status"] != "live_completed":
        lines.append("> Checked-in fixtures validate the harness only. No live-model performance claim is made.")
    for limitation in report.get("limitations", []):
        lines.append(f"- Limitation: {limitation}")
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], results_dir: Path, run_dir: Path) -> None:
    report_json = json.dumps(report, indent=2) + "\n"
    report_md = markdown(report)
    (run_dir / "report.json").write_text(report_json, encoding="utf-8")
    (run_dir / "report.md").write_text(report_md, encoding="utf-8")
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "latest.json").write_text(report_json, encoding="utf-8")
    (results_dir / "latest.md").write_text(report_md, encoding="utf-8")


def human_status(path: Path | None, required_pairs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if not path:
        return {"status": "pending", "passed": False}
    value = load_json(path)
    reviews = value.get("reviews", [])
    reviewed = {(item.get("case_id"), item.get("trial")) for item in reviews if isinstance(item, dict)} if isinstance(reviews, list) else set()
    required = {(item["case_id"], item["trial"]) for item in (required_pairs or [])}
    passed = (
        value.get("status") == "completed" and isinstance(reviews, list) and bool(reviews)
        and all(isinstance(item, dict) and item.get("decision") == "pass" for item in reviews)
        and required.issubset(reviewed)
    )
    return {"status": value.get("status", "invalid"), "passed": passed, "source": str(path), "required_pairs": len(required), "reviewed_required_pairs": len(required & reviewed)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Product Development Operating System Eval 2.0")
    parser.add_argument("--profile", choices=["smoke", "benchmark", "release"], default="smoke")
    parser.add_argument("--baseline-dir", type=Path, default=EVAL_ROOT / "fixtures" / "responses" / "baseline")
    parser.add_argument("--pdos-dir", type=Path, default=EVAL_ROOT / "fixtures" / "responses" / "pdos")
    parser.add_argument("--results-dir", type=Path, default=EVAL_ROOT / "results")
    parser.add_argument("--live-runner", default=os.environ.get("PDOS_LIVE_RUNNER"))
    parser.add_argument("--semantic-runner", default=os.environ.get("PDOS_SEMANTIC_RUNNER"))
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--require-live", action="store_true")
    parser.add_argument("--human-review", type=Path)
    parser.add_argument("--compare-run", type=Path)
    parser.add_argument("--regression-tolerance", type=float, default=2.0)
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")

    case_paths = sorted((EVAL_ROOT / "cases").glob("*.json"))
    if not case_paths:
        print("No eval cases found", file=sys.stderr)
        return 2
    generated = datetime.now(timezone.utc)
    run_id = generated.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    run_dir = args.results_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    baseline_fixture = evaluate_fixture(args.baseline_dir, case_paths)
    pdos_fixture = evaluate_fixture(args.pdos_dir, case_paths)
    report: dict[str, Any] = {
        "schema_version": 2, "eval_version": EVAL_VERSION, "rubric_hash": rubric_hash(case_paths),
        "run_id": run_id, "generated_at": generated.isoformat(), "profile": args.profile,
        "package_version": (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "skill_hash": skill_hash(), "benchmark_status": "fixture_only", "release_qualified": False,
        "baseline": {"summary": aggregate(baseline_fixture), "cases": baseline_fixture},
        "pdos": {"summary": aggregate(pdos_fixture), "cases": pdos_fixture},
        "semantic": {"status": "not_run", "judgments": []}, "human_review": {"status": "not_run", "passed": False},
        "regression": {"status": "not_run", "passed": False}, "limitations": [],
    }

    live_required = args.require_live or args.profile == "release"
    if args.profile in {"benchmark", "release"} and not args.live_runner:
        report["benchmark_status"] = "skipped_no_runner"
        report["limitations"].append("No live runner was configured; fixture scores are not model benchmark results.")
        write_report(report, args.results_dir, run_dir)
        print(markdown(report), end="")
        return 1 if live_required else (0 if all(item["passed"] for item in pdos_fixture) else 1)

    if args.profile in {"benchmark", "release"}:
        all_captures: dict[str, list[dict[str, Any]]] = {"baseline": [], "pdos": []}
        for case_path in case_paths:
            for trial in range(1, args.trials + 1):
                for condition in ("baseline", "pdos"):
                    all_captures[condition].append(run_live_capture(args.live_runner, case_path, condition, trial, run_dir))
        report["benchmark_status"] = "live_completed"
        report["baseline"] = summarize_live(all_captures["baseline"], case_paths)
        report["pdos"] = summarize_live(all_captures["pdos"], case_paths)
        models = {str(item.get("metadata", {}).get("model")) for rows in all_captures.values() for item in rows if item.get("metadata", {}).get("model")}
        paired_mismatch = any(
            next((item.get("metadata", {}).get("model") for item in all_captures["baseline"] if item["case_id"] == case_id and item["trial"] == trial), None)
            != next((item.get("metadata", {}).get("model") for item in all_captures["pdos"] if item["case_id"] == case_id and item["trial"] == trial), None)
            for case_id in [load_json(path)["id"] for path in case_paths] for trial in range(1, args.trials + 1)
        )
        report["live"] = {"trials": args.trials, "capture_count": sum(len(items) for items in all_captures.values()), "model_identity": sorted(models), "paired_model_mismatch": paired_mismatch}
        if paired_mismatch:
            report["limitations"].append("Baseline and PDOS paired trials reported different model identities.")

        human_packet = {"run_id": run_id, "status": "pending", "instructions": "Review blind pairs, every deterministic failure, and at least trial 1 for each case.", "pairs": []}
        judgments: list[dict[str, Any]] = []
        for case_path in case_paths:
            case = load_json(case_path)
            for trial in range(1, args.trials + 1):
                baseline_capture = next(item for item in all_captures["baseline"] if item["case_id"] == case["id"] and item["trial"] == trial)
                pdos_capture = next(item for item in all_captures["pdos"] if item["case_id"] == case["id"] and item["trial"] == trial)
                if trial == 1 or not baseline_capture["deterministic"]["passed"] or not pdos_capture["deterministic"]["passed"]:
                    human_packet["pairs"].append({"case_id": case["id"], "trial": trial, "baseline_capture": f"captures/baseline/{case['id']}-trial-{trial}.json", "pdos_capture": f"captures/pdos/{case['id']}-trial-{trial}.json", "decision": "pending"})
                if args.semantic_runner:
                    try:
                        judgments.append(semantic_judge(args.semantic_runner, case, trial, baseline_capture["response"], pdos_capture["response"]))
                    except (OSError, ValueError, RuntimeError, TimeoutError) as error:
                        judgments.append({"case_id": case["id"], "trial": trial, "error": str(error)})
        (run_dir / "human-review.json").write_text(json.dumps(human_packet, indent=2) + "\n", encoding="utf-8")
        if args.semantic_runner:
            schema_ok = bool(judgments) and all("error" not in item for item in judgments)
            pdos_scores: list[float] = []
            baseline_scores: list[float] = []
            for item in judgments:
                if "error" in item:
                    continue
                mapping = item["blind_mapping"]
                for label, condition in mapping.items():
                    (pdos_scores if condition == "pdos" else baseline_scores).append(float(item["scores"][label]))
            pdos_mean = round(sum(pdos_scores) / max(1, len(pdos_scores)), 2)
            baseline_mean = round(sum(baseline_scores) / max(1, len(baseline_scores)), 2)
            semantic_ok = schema_ok and pdos_mean >= baseline_mean - 2.0
            report["semantic"] = {"status": "completed" if schema_ok else "failed", "passed": semantic_ok, "pdos_mean": pdos_mean, "baseline_mean": baseline_mean, "judgments": judgments}
        else:
            report["semantic"] = {"status": "skipped_no_runner", "passed": False, "judgments": []}
            report["limitations"].append("Semantic judging was not configured.")
        report["human_review"] = human_status(args.human_review, human_packet["pairs"])
        if not args.human_review:
            report["limitations"].append("Human spot-check packet was generated but not completed.")
        if args.compare_run:
            previous_path = args.compare_run / "report.json" if args.compare_run.is_dir() else args.compare_run
            regression = compare_regression(load_json(previous_path), report, args.regression_tolerance)
            report["regression"] = {"status": "completed", **regression}
        elif args.profile == "release":
            report["limitations"].append("Release profile requires an immutable compatible comparison run.")

        minimum_delta = 5.0
        deterministic_ok = report["pdos"]["summary"]["passed"] == report["pdos"]["summary"]["total"]
        improvement_ok = report["pdos"]["summary"]["score"] - report["baseline"]["summary"]["score"] >= minimum_delta
        report["release_qualified"] = bool(
            args.profile == "release" and deterministic_ok and improvement_ok and not paired_mismatch
            and report["semantic"].get("passed") and report["human_review"].get("passed")
            and report["regression"].get("passed")
        )

    write_report(report, args.results_dir, run_dir)
    print(markdown(report), end="")
    pdos_gates = report["pdos"]["summary"]["passed"] == report["pdos"]["summary"]["total"]
    if args.profile == "release":
        return 0 if report["release_qualified"] else 1
    return 0 if pdos_gates else 1


if __name__ == "__main__":
    raise SystemExit(main())
