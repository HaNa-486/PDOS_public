"""Compatibility and score regression checks for immutable PDOS eval runs."""

from __future__ import annotations

from typing import Any


def compare(previous: dict[str, Any], current: dict[str, Any], tolerance: float = 2.0) -> dict[str, Any]:
    reasons: list[str] = []
    for field in ("eval_version", "rubric_hash"):
        if previous.get(field) != current.get(field):
            reasons.append(f"incompatible {field}")
    previous_model = previous.get("live", {}).get("model_identity")
    current_model = current.get("live", {}).get("model_identity")
    if previous_model and current_model and previous_model != current_model:
        reasons.append("incompatible model identity")
    if reasons:
        return {"compatible": False, "passed": False, "reasons": reasons}
    previous_score = float(previous.get("pdos", {}).get("summary", {}).get("score", 0))
    current_score = float(current.get("pdos", {}).get("summary", {}).get("score", 0))
    delta = round(current_score - previous_score, 2)
    return {"compatible": True, "passed": delta >= -abs(tolerance), "delta": delta, "tolerance": tolerance, "reasons": []}
