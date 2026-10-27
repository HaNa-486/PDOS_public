#!/usr/bin/env python3
"""Validate PDOS continuity, autonomy, remediation, privacy, and handoff health."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
from pathlib import Path

from pdos_common import VERSION, bullet_value, is_ancestor, repository_identity
from review_remediation import validate_project_records


PROTOCOL_VERSION = VERSION
START_MARKER = "<!-- PDOS:START -->"
END_MARKER = "<!-- PDOS:END -->"
MAX_STATE_BYTES = 16 * 1024
MAX_STATE_LINES = 200
REQUIRED_SECTIONS = ["## Repository identity", "## Product anchors", "## Current work", "## Handoff", "## Read next"]
REQUIRED_GITIGNORE = ["private/", "local/", ".env", "*.key", "*.pem", "*.p12", "*.secret"]
SECRET_FILE_PATTERNS = [".env", ".env.*", "*.key", "*.pem", "*.p12", "*.secret"]
ABSOLUTE_PATH_PATTERNS = [r"[A-Za-z]:\\", r"/(?:Users|home)/[^/\s]+"]


def _check_read_next(project_root: Path, pdos: Path, state_text: str, errors: list[str]) -> None:
    match = re.search(r"^## Read next\s*$([\s\S]*?)(?=^## |\Z)", state_text, re.MULTILINE)
    if not match:
        return
    for value in re.findall(r"`([^`]+)`", match.group(1)):
        if value.startswith("workstreams/") and value == "workstreams/":
            continue
        candidate = project_root / value if value.startswith(".pdos/") else pdos / value
        if not candidate.exists():
            errors.append(f"Read-next target does not exist: {value}")


def validate_project(project_root: Path) -> dict[str, object]:
    root = project_root.resolve()
    pdos = root / ".pdos"
    errors: list[str] = []
    warnings: list[str] = []
    state = pdos / "STATE.md"
    if not state.exists():
        return {"ok": False, "errors": ["Missing .pdos/STATE.md"], "warnings": []}

    state_text = state.read_text(encoding="utf-8")
    state_bytes = len(state_text.encode("utf-8"))
    state_lines = len(state_text.splitlines())
    if state_bytes > MAX_STATE_BYTES:
        errors.append(f"STATE.md is {state_bytes} bytes; limit is {MAX_STATE_BYTES}")
    if state_lines > MAX_STATE_LINES:
        errors.append(f"STATE.md is {state_lines} lines; limit is {MAX_STATE_LINES}")
    if bullet_value(state_text, "Protocol version") != PROTOCOL_VERSION:
        errors.append(f"STATE.md protocol must be {PROTOCOL_VERSION}")
    for section in REQUIRED_SECTIONS:
        if section not in state_text:
            errors.append(f"STATE.md missing section: {section}")
    _check_read_next(root, pdos, state_text, errors)

    version = pdos / "VERSION"
    if not version.exists() or version.read_text(encoding="utf-8").strip() != PROTOCOL_VERSION:
        errors.append(f".pdos/VERSION must be {PROTOCOL_VERSION}")

    instruction_files = [root / "AGENTS.md"]
    override = root / "AGENTS.override.md"
    if override.exists():
        instruction_files.append(override)
    for path in instruction_files:
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        if text.count(START_MARKER) != 1 or text.count(END_MARKER) != 1:
            errors.append(f"PDOS continuity block missing or malformed: {path.name}")

    ignore = pdos / ".gitignore"
    ignore_lines = set(ignore.read_text(encoding="utf-8").splitlines()) if ignore.exists() else set()
    for pattern in REQUIRED_GITIGNORE:
        if pattern not in ignore_lines:
            errors.append(f".pdos/.gitignore missing: {pattern}")

    for path in pdos.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(pdos)
        if relative.parts and relative.parts[0] in {"private", "local"}:
            continue
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in SECRET_FILE_PATTERNS):
            errors.append(f"Secret-bearing filename is in shared PDOS state: {relative.as_posix()}")
        if path.suffix.lower() in {".md", ".json", ".yaml", ".yml", ".txt"}:
            content = path.read_text(encoding="utf-8")
            if any(re.search(pattern, content) for pattern in ABSOLUTE_PATH_PATTERNS):
                errors.append(f"Shared PDOS state contains an absolute user path: {relative.as_posix()}")

    identity = repository_identity(root)
    branch = bullet_value(state_text, "Branch")
    observed = bullet_value(state_text, "Observed commit")
    if not branch or branch == "not recorded":
        warnings.append("STATE.md repository identity not recorded: Branch")
    elif identity["branch"] != "not-git" and branch != identity["branch"]:
        warnings.append("STATE.md branch differs from current repository")
    if not observed or observed == "not recorded":
        warnings.append("STATE.md repository identity not recorded: Observed commit")
    elif identity["observed_commit"] != "not-git" and not is_ancestor(root, observed, identity["observed_commit"]):
        warnings.append("STATE.md observed commit is not an ancestor of current HEAD")
    if bullet_value(state_text, "Updated") in {"", "not yet"}:
        warnings.append("STATE.md has not been updated")

    workstreams = pdos / "workstreams"
    if workstreams.exists():
        required = ["Status", "Branch", "Base commit", "Scope", "Files or areas at risk"]
        for path in workstreams.glob("*.md"):
            if path.name == "_template.md":
                continue
            text = path.read_text(encoding="utf-8")
            for label in required:
                if not bullet_value(text, label):
                    warnings.append(f"{path.name} missing workstream field: {label}")
            if bullet_value(text, "Status") not in {"active", "paused", "blocked", "completed", "cancelled"}:
                errors.append(f"{path.name} has invalid workstream status")

    records = validate_project_records(root)
    errors.extend(records["errors"])  # type: ignore[arg-type]
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "state_bytes": state_bytes,
            "state_lines": state_lines,
            "reviews": len(records["reviews"]),  # type: ignore[arg-type]
            "remediations": len(records["remediations"]),  # type: ignore[arg-type]
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PDOS project state")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--strict", action="store_true", help="Fail when warnings remain")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_project(Path(args.target))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for item in report["errors"]:
            print(f"ERROR: {item}")
        for item in report["warnings"]:
            print(f"WARNING: {item}")
        healthy = report["ok"] and not (args.strict and report["warnings"])
        print("PDOS state valid" if healthy else "PDOS state needs attention")
    return 0 if report["ok"] and not (args.strict and report["warnings"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
