#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


request = json.load(sys.stdin)
if request.get("protocol") == "pdos-semantic-judge-v1":
    result = {
        "judgment": {"winner": "B", "scores": {"A": 60, "B": 90}, "rationale": "B has more complete evidence and safer decisions.", "evidence": ["structured findings", "autonomy gate"]},
        "metadata": {"model": "mock-semantic", "tokens": {"input": 10, "output": 5, "total": 15}}
    }
else:
    root = Path(__file__).resolve().parents[2]
    case_id = request["case"]["id"]
    condition = request["condition"]
    response = json.loads((root / "evals" / "fixtures" / "responses" / condition / f"{case_id}.json").read_text(encoding="utf-8"))
    if condition == "pdos" and case_id == "review-and-plan-actionability":
        artifact = Path(request["project_path"]) / ".pdos" / "reviews" / "mock.md"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("mock durable review\n", encoding="utf-8")
    if condition == "pdos" and case_id == "review-and-fix-with-evidence":
        (Path(request["project_path"]) / "mock-fix.txt").write_text("mock verified fix\n", encoding="utf-8")
    result = {"response": response, "metadata": {"model": "mock-model", "tokens": {"input": 100, "output": 50, "total": 150}, "token_source": "mock"}}
json.dump(result, sys.stdout)
