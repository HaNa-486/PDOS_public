#!/usr/bin/env python3
"""Update a PDOS workstream with a guarded terminal or coordination status."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

from pdos_common import atomic_write_text, bullet_value


ALLOWED = {
    "active": {"paused", "blocked", "completed", "cancelled"},
    "paused": {"active", "blocked", "completed", "cancelled"},
    "blocked": {"active", "paused", "completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


def update(path: Path, status: str, changed: str = "", verification: str = "", risks: str = "", next_action: str = "") -> None:
    text = path.read_text(encoding="utf-8")
    current = bullet_value(text, "Status")
    if status not in ALLOWED.get(current, set()):
        raise ValueError(f"Invalid workstream transition: {current} -> {status}")
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    values = {
        "Status": status,
        "Updated": stamp,
        "What changed": changed,
        "Verification": verification,
        "Residual risks": risks,
        "Next safe action": next_action,
    }
    for key, value in values.items():
        if value or key in {"Status", "Updated"}:
            text = re.sub(rf"^- {re.escape(key)}:\s*.*$", f"- {key}: {value}", text, count=1, flags=re.MULTILINE)
    atomic_write_text(path, text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update a PDOS workstream")
    parser.add_argument("file")
    parser.add_argument("status", choices=sorted(ALLOWED))
    parser.add_argument("--changed", default="")
    parser.add_argument("--verification", default="")
    parser.add_argument("--risks", default="")
    parser.add_argument("--next-action", default="")
    args = parser.parse_args()
    update(Path(args.file), args.status, args.changed, args.verification, args.risks, args.next_action)
    print(f"Updated {args.file} to {args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
