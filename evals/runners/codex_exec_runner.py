#!/usr/bin/env python3
"""Reference live adapter for `codex exec` using pre-isolated CODEX_HOME directories."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def hash_path(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(item.read_bytes())
    return digest.hexdigest()


def discover_pdos_skills(codex_home: Path) -> list[Path]:
    found: list[Path] = []
    skills = codex_home / "skills"
    if not skills.exists():
        return found
    for skill_md in skills.glob("*/SKILL.md"):
        try:
            text = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        if "name: pdos" in text:
            found.append(skill_md.parent)
    return found


def select_home(request: dict[str, Any]) -> Path:
    condition = request["condition"]
    variable = "PDOS_BASELINE_CODEX_HOME" if condition == "baseline" else "PDOS_CANDIDATE_CODEX_HOME"
    value = os.environ.get(variable)
    if not value:
        raise RuntimeError(f"{variable} must point to a preconfigured, authenticated, isolated Codex home")
    home = Path(value).expanduser().resolve()
    found = discover_pdos_skills(home)
    if condition == "baseline" and found:
        raise RuntimeError("Baseline Codex home contains a discoverable PDOS skill")
    if condition == "pdos":
        if len(found) != 1:
            raise RuntimeError(f"Candidate Codex home must contain exactly one PDOS skill; found {len(found)}")
        expected = request.get("skill_hash")
        if expected and hash_path(found[0]) != expected:
            raise RuntimeError("Candidate Codex home PDOS hash does not match the evaluated skill")
    return home


def response_contract(case_type: str) -> str:
    common = "Return a JSON object containing only claims supported by your work."
    contracts = {
        "trigger": "Include boolean trigger_skill.",
        "hidden_assumptions": "Include assumptions as an array of concise strings.",
        "production_blindspots": "Include findings as an array of concise strings.",
        "founder_interruption": "Include questions and decisions arrays; mark consequential and safe booleans.",
        "end_to_end": "Include workflow.phases, workflow.artifacts, evidence, notes, and findings.",
        "state_continuity": "Include continuity flags and loaded_files.",
        "review_mode": "Include review.mode, product_mutated, pdos_artifacts_written, plus evidence.",
        "finding_contract": "Include findings as structured objects with every field requested by the case.",
        "autonomy_gate": "Include decisions with topic, autonomy_class, and executed.",
        "clean_project": "Include findings and evidence; do not invent issues.",
    }
    return common + " " + contracts.get(case_type, "")


def execute(request: dict[str, Any]) -> dict[str, Any]:
    home = select_home(request)
    codex_bin = os.environ.get("PDOS_CODEX_BIN", "codex")
    model = os.environ.get("PDOS_CODEX_MODEL")
    case = request["case"]
    prompt = (
        f"{case['prompt']}\n\n"
        f"Evaluation capture contract: {response_contract(case['type'])} "
        "Place that JSON object as a string in the required response_json field."
    )
    schema = {
        "type": "object",
        "properties": {"response_json": {"type": "string"}},
        "required": ["response_json"],
        "additionalProperties": False,
    }
    with tempfile.TemporaryDirectory(prefix="pdos-codex-exec-") as temporary:
        temp = Path(temporary)
        schema_path = temp / "schema.json"
        output_path = temp / "last.json"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        command = [
            codex_bin, "exec", "--ephemeral", "--json", "--sandbox", request.get("sandbox", "read-only"),
            "--skip-git-repo-check", "--output-schema", str(schema_path),
            "--output-last-message", str(output_path),
        ]
        if model:
            command.extend(["--model", model])
        command.append(prompt)
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(home)
        completed = subprocess.run(
            command, cwd=request["project_path"], env=environment, check=False,
            capture_output=True, text=True, timeout=float(os.environ.get("PDOS_CODEX_TIMEOUT", "600")),
        )
        if completed.returncode != 0:
            raise RuntimeError(f"codex exec failed ({completed.returncode}): {completed.stderr[-2000:]}")
        usage: dict[str, Any] = {}
        for line in completed.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                usage = event["usage"]
        final = json.loads(output_path.read_text(encoding="utf-8"))
        response = json.loads(final["response_json"])
        if not isinstance(response, dict):
            raise ValueError("response_json must encode an object")
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    total = input_tokens + output_tokens if isinstance(input_tokens, int) and isinstance(output_tokens, int) else None
    return {
        "response": response,
        "metadata": {
            "model": model or "codex-default-unpinned",
            "settings": {"sandbox": request.get("sandbox", "read-only"), "ephemeral": True},
            "tokens": {"input": input_tokens, "output": output_tokens, "total": total},
            "token_source": "codex-exec-jsonl" if total is not None else "unavailable",
        },
    }


def main() -> int:
    try:
        request = json.load(sys.stdin)
        json.dump(execute(request), sys.stdout)
        return 0
    except BaseException as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
