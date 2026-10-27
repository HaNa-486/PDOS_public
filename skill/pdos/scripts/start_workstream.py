#!/usr/bin/env python3
"""Create a collision-safe shared workstream plus ignored local environment metadata."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from pdos_common import atomic_write_text, repository_identity, slugify


def start_workstream(project_root: Path, slug: str, scope: str, areas: str = "") -> Path:
    root = project_root.resolve()
    pdos = root / ".pdos"
    if not (pdos / "STATE.md").exists():
        raise FileNotFoundError("PDOS state not found; run bootstrap_project.py first")
    directory = pdos / "workstreams"
    directory.mkdir(parents=True, exist_ok=True)
    identity = repository_identity(root)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    base = f"{now.date().isoformat()}-{slugify(slug)}"
    index = 1
    while True:
        suffix = "" if index == 1 else f"-{index}"
        output = directory / f"{base}{suffix}.md"
        if not output.exists():
            break
        index += 1
    stamp = now.isoformat().replace("+00:00", "Z")
    content = f"""# Workstream: {scope}

- Status: active
- Started: {stamp}
- Updated: {stamp}
- Branch: {identity['branch']}
- Base commit: {identity['observed_commit']}
- Scope: {scope}
- Files or areas at risk: {areas}

## Coordination

- Overlap checked: pending
- Dependencies:
- Consequential conflicts:

## Handoff

- What changed:
- Verification:
- Residual risks:
- Next safe action:
"""
    atomic_write_text(output, content)
    local = pdos / "local" / "workstreams" / f"{output.stem}.json"
    atomic_write_text(local, json.dumps({"worktree": identity["worktree"]}, indent=2) + "\n")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Start a scoped PDOS workstream")
    parser.add_argument("target")
    parser.add_argument("slug")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--areas", default="")
    args = parser.parse_args()
    print(start_workstream(Path(args.target), args.slug, args.scope, args.areas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
