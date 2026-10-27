"""Shared deterministic helpers for PDOS project scripts."""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path


VERSION = "0.4.0-alpha.1"


def _git(project_root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(project_root), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return completed.stdout.strip() if completed.returncode == 0 else ""


def repository_identity(project_root: Path) -> dict[str, str]:
    root = project_root.resolve()
    top = _git(root, "rev-parse", "--show-toplevel")
    branch = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    commit = _git(root, "rev-parse", "HEAD")
    return {
        "branch": branch or ("detached" if commit else "not-git"),
        "observed_commit": commit or "not-git",
        "worktree": str(Path(top).resolve()) if top else str(root),
    }


def is_ancestor(project_root: Path, recorded: str, current: str) -> bool:
    if recorded in {"", "not-git", "not recorded"} or current == "not-git":
        return recorded == current
    if recorded == current:
        return True
    try:
        return subprocess.run(
            ["git", "-C", str(project_root), "merge-base", "--is-ancestor", recorded, current],
            check=False,
            capture_output=True,
            timeout=5,
        ).returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def version_core(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-[0-9A-Za-z.-]+)?", value.strip())
    if not match:
        raise ValueError(f"Unrecognized PDOS version: {value}")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("Slug must contain at least one letter or digit")
    return slug[:64].rstrip("-")


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def bullet_value(text: str, key: str) -> str:
    match = re.search(rf"^- {re.escape(key)}:\s*(.*)$", text, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""
