"""Blind A/B semantic-judge protocol and validation."""

from __future__ import annotations

import hashlib
from typing import Any

from runners.command_runner import run_command


def blind_pair(case_id: str, trial: int, baseline: dict[str, Any], pdos: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    swap = int(hashlib.sha256(f"{case_id}:{trial}".encode()).hexdigest(), 16) % 2 == 1
    if swap:
        return {"A": pdos, "B": baseline}, {"A": "pdos", "B": "baseline"}
    return {"A": baseline, "B": pdos}, {"A": "baseline", "B": "pdos"}


def validate_judgment(value: dict[str, Any]) -> None:
    if value.get("winner") not in {"A", "B", "tie"}:
        raise ValueError("Semantic judgment winner must be A, B, or tie")
    for label in ("A", "B"):
        score = value.get("scores", {}).get(label) if isinstance(value.get("scores"), dict) else None
        if not isinstance(score, (int, float)) or not 0 <= score <= 100:
            raise ValueError(f"Semantic judgment score {label} must be 0..100")
    if not str(value.get("rationale", "")).strip():
        raise ValueError("Semantic judgment requires rationale")
    if not isinstance(value.get("evidence", []), list):
        raise ValueError("Semantic judgment evidence must be a list")


def judge(command: str, case: dict[str, Any], trial: int, baseline: dict[str, Any], pdos: dict[str, Any]) -> dict[str, Any]:
    outputs, mapping = blind_pair(case["id"], trial, baseline, pdos)
    request = {
        "protocol": "pdos-semantic-judge-v1",
        "case_id": case["id"],
        "rubric": ["correctness", "evidence", "actionability", "proportionality", "founder burden", "production coverage", "no fabrication"],
        "outputs": outputs,
    }
    result = run_command(command, request)
    judgment = result.get("judgment", result)
    if not isinstance(judgment, dict):
        raise ValueError("Semantic runner must return judgment object")
    validate_judgment(judgment)
    winner = judgment["winner"]
    judgment["winner_condition"] = mapping.get(winner, "tie")
    judgment["blind_mapping"] = mapping
    judgment["metadata"] = result.get("metadata", {})
    judgment["case_id"] = case["id"]
    judgment["trial"] = trial
    return judgment
