#!/usr/bin/env python3
"""Stage, validate, atomically install, and safely back up the PDOS skill."""

from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def validate_skill(path: Path) -> str:
    required = [path / "SKILL.md", path / "VERSION", path / "scripts" / "bootstrap_project.py"]
    missing = [item.relative_to(path).as_posix() for item in required if not item.is_file()]
    if missing:
        raise ValueError(f"Invalid PDOS skill; missing: {', '.join(missing)}")
    skill_text = (path / "SKILL.md").read_text(encoding="utf-8")
    if "name: pdos" not in skill_text or "Product Development Operating System (PDOS)" not in skill_text:
        raise ValueError("Invalid PDOS SKILL.md metadata or official name")
    version = (path / "VERSION").read_text(encoding="utf-8").strip()
    if not version:
        raise ValueError("Empty PDOS skill VERSION")
    return version


def install(source: Path, destination: Path, codex_home: Path) -> dict[str, object]:
    source = source.resolve()
    destination = destination.expanduser().resolve()
    codex_home = codex_home.expanduser().resolve()
    version = validate_skill(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".pdos-stage-", dir=destination.parent))
    shutil.rmtree(stage)
    backup: Path | None = None
    legacy_moved: list[str] = []
    installed = False
    try:
        shutil.copytree(source, stage)
        if validate_skill(stage) != version:
            raise ValueError("Staged skill version changed during copy")
        if destination.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
            backup = codex_home / "skill-backups" / "pdos" / stamp / "pdos"
            backup.parent.mkdir(parents=True, exist_ok=False)
            os.replace(destination, backup)
        os.replace(stage, destination)
        installed = True
        for legacy in sorted((codex_home / "skills").glob("pdos.backup-*")):
            stamp = datetime.now(timezone.utc).strftime("legacy-%Y%m%d-%H%M%S-%f")
            target = codex_home / "skill-backups" / "pdos" / stamp / legacy.name
            target.parent.mkdir(parents=True, exist_ok=False)
            shutil.move(str(legacy), str(target))
            legacy_moved.append(str(target))
    except BaseException:
        if installed and destination.exists():
            failed = destination.parent / f".pdos-failed-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
            os.replace(destination, failed)
            shutil.rmtree(failed, ignore_errors=True)
        if backup and backup.exists() and not destination.exists():
            os.replace(backup, destination)
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
        raise
    return {
        "version": version,
        "destination": str(destination),
        "backup": str(backup) if backup else None,
        "legacy_backups_moved": legacy_moved,
    }


def main() -> int:
    package_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Install Product Development Operating System (PDOS)")
    parser.add_argument("--source", type=Path, default=package_root / "skill" / "pdos")
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--codex-home", type=Path)
    args = parser.parse_args()
    codex_home = args.codex_home or Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    destination = args.destination or codex_home / "skills" / "pdos"
    result = install(args.source, destination, codex_home)
    print(f"Installed Product Development Operating System (PDOS) {result['version']} to {result['destination']}")
    if result["backup"]:
        print(f"Previous installation backed up outside skill discovery at {result['backup']}")
    if result["legacy_backups_moved"]:
        print(f"Moved {len(result['legacy_backups_moved'])} legacy discoverable backup(s) outside skills/")
    print("Restart Codex, invoke $pdos once in the project, then run pdos_doctor.py for a health report.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
