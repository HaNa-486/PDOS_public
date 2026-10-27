#!/usr/bin/env python3
"""Report PDOS installation version, project health, duplicates, and next safe action."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from pdos_common import VERSION, bullet_value
from validate_project_state import validate_project


def _codex_home(override: str | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    if os.environ.get("CODEX_HOME"):
        return Path(os.environ["CODEX_HOME"]).expanduser().resolve()
    return Path.home() / ".codex"


def diagnose(project_root: Path, codex_home: Path, repair_safe: bool = False) -> dict[str, object]:
    skill_root = Path(__file__).resolve().parent.parent
    installed_version_file = skill_root / "VERSION"
    installed_version = installed_version_file.read_text(encoding="utf-8").strip() if installed_version_file.exists() else "missing"
    problems: list[str] = []
    repairs: list[str] = []
    required = [skill_root / "SKILL.md", skill_root / "VERSION", skill_root / "scripts" / "bootstrap_project.py"]
    for path in required:
        if not path.exists():
            problems.append(f"Installed skill is missing {path.relative_to(skill_root).as_posix()}")
    if installed_version != VERSION:
        problems.append(f"Installed version metadata mismatch: expected {VERSION}, found {installed_version}")

    legacy = sorted((codex_home / "skills").glob("pdos.backup-*")) if (codex_home / "skills").exists() else []
    if legacy:
        problems.append(f"Found {len(legacy)} discoverable legacy PDOS backup(s)")
        if repair_safe:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            destination_root = codex_home / "skill-backups" / "pdos" / f"legacy-{stamp}"
            destination_root.mkdir(parents=True, exist_ok=True)
            for path in legacy:
                destination = destination_root / path.name
                shutil.move(str(path), str(destination))
                repairs.append(f"Moved {path} to {destination}")

    project = project_root.resolve()
    state = project / ".pdos" / "STATE.md"
    project_version = bullet_value(state.read_text(encoding="utf-8"), "Protocol version") if state.exists() else "missing"
    if project_version == "missing":
        health = {"ok": False, "errors": ["PDOS project state is not initialized"], "warnings": []}
        problems.append("Project state is not initialized")
        next_action = f"Run bootstrap_project.py for {project}"
    elif project_version != VERSION:
        health = {"ok": False, "errors": [f"Project protocol {project_version} needs upgrade to {VERSION}"], "warnings": []}
        problems.append(f"Project protocol needs upgrade: {project_version} -> {VERSION}")
        next_action = f"Run bootstrap_project.py for {project}, then run validate_project_state.py --strict"
    else:
        health = validate_project(project)
        problems.extend(str(item) for item in health["errors"])
        next_action = (
            "Project is healthy. Invoke $pdos with review, review-and-plan, or review-and-fix."
            if health["ok"] and not health["warnings"]
            else "Resolve reported state issues, update the handoff, then run strict validation."
        )
    return {
        "pdos_full_name": "Product Development Operating System (PDOS)",
        "installed_version": installed_version,
        "skill_path": str(skill_root),
        "project_path": str(project),
        "project_protocol": project_version,
        "project_health": health,
        "discoverable_legacy_backups": [str(item) for item in legacy],
        "problems": problems,
        "repairs": repairs,
        "next_safe_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Product Development Operating System (PDOS)")
    parser.add_argument("target", nargs="?", default=".", help="Project root")
    parser.add_argument("--codex-home")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repair-safe", action="store_true", help="Move discoverable legacy backups outside skills/")
    args = parser.parse_args()
    report = diagnose(Path(args.target), _codex_home(args.codex_home), args.repair_safe)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Product Development Operating System (PDOS) {report['installed_version']}")
        print(f"Project protocol: {report['project_protocol']}")
        for problem in report["problems"]:
            print(f"ISSUE: {problem}")
        for repair in report["repairs"]:
            print(f"REPAIRED: {repair}")
        print(f"Next safe action: {report['next_safe_action']}")
    return 0 if not report["problems"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
