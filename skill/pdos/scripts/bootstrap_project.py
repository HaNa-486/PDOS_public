#!/usr/bin/env python3
"""Create or non-destructively upgrade PDOS state and continuity guidance."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pdos_common import VERSION, atomic_write_text, bullet_value, repository_identity, version_core


START_MARKER = "<!-- PDOS:START -->"
END_MARKER = "<!-- PDOS:END -->"
PROTOCOL_VERSION = VERSION


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_managed_block(path: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if text.count(START_MARKER) != text.count(END_MARKER) or text.count(START_MARKER) > 1:
        raise ValueError(f"Malformed or duplicate PDOS managed block in {path}")
    start, end = text.find(START_MARKER), text.find(END_MARKER)
    if start != -1 and end < start:
        raise ValueError(f"Malformed PDOS managed block in {path}")


def _merged_block(path: Path, block: str) -> str:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    start, end = existing.find(START_MARKER), existing.find(END_MARKER)
    if start != -1:
        end += len(END_MARKER)
        parts = [part for part in (existing[:start].rstrip(), block.strip(), existing[end:].lstrip().rstrip()) if part]
        return "\n\n".join(parts) + "\n"
    return existing.rstrip() + ("\n\n" if existing.strip() else "") + block.strip() + "\n"


def _instruction_targets(project_root: Path) -> list[Path]:
    targets = [project_root / "AGENTS.md"]
    override = project_root / "AGENTS.override.md"
    if override.exists():
        targets.append(override)
    return targets


def sync_agents_guidance(project_root: Path) -> list[Path]:
    block = (Path(__file__).resolve().parent.parent / "assets" / "AGENTS.pdos.md").read_text(encoding="utf-8")
    updated: list[Path] = []
    for path in _instruction_targets(project_root):
        merged = _merged_block(path, block)
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if merged != existing:
            atomic_write_text(path, merged)
            updated.append(path)
    return updated


def _state_version(pdos_root: Path) -> str:
    state = pdos_root / "STATE.md"
    if state.exists():
        value = bullet_value(state.read_text(encoding="utf-8"), "Protocol version")
        if value:
            return value
    version = pdos_root / "VERSION"
    return version.read_text(encoding="utf-8").strip() if version.exists() else ""


def preflight(project_root: Path) -> str:
    for path in _instruction_targets(project_root):
        _validate_managed_block(path)
    existing = _state_version(project_root / ".pdos")
    if existing:
        current_core = version_core(existing)
        target_core = version_core(PROTOCOL_VERSION)
        if current_core > target_core:
            raise ValueError(f"Refusing to downgrade PDOS state from {existing} to {PROTOCOL_VERSION}")
        if current_core == target_core and existing != PROTOCOL_VERSION:
            raise ValueError(f"Refusing to replace different PDOS prerelease {existing} with {PROTOCOL_VERSION}")
    return existing


def _contains_local_user_path(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]:\\|/(?:Users|home)/", text))


def _archive_path(pdos_root: Path, local_only: bool = False) -> Path:
    directory = pdos_root / "local" / "migration-archives" if local_only else pdos_root / "archive"
    candidate = directory / "STATE-pre-v0.4.md"
    index = 2
    while candidate.exists():
        candidate = directory / f"STATE-pre-v0.4-{index}.md"
        index += 1
    return candidate


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^{re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _read_next(text: str) -> list[str]:
    return re.findall(r"`([^`]+)`", _section(text, "## Read next"))


def _migrated_state(original: str, archive_ref: str, archive_read_next: bool = True) -> str:
    read_next = [item for item in _read_next(original) if item not in {"AUTONOMY.md"}]
    pointers = ["AUTONOMY.md", *read_next]
    if "specs/product.md" not in pointers:
        pointers.append("specs/product.md")
    if "plans/active.md" not in pointers:
        pointers.append("plans/active.md")
    if archive_read_next:
        pointers.append(archive_ref)
    lines = "\n".join(f"- `{item}`" for item in dict.fromkeys(pointers))
    archive_note = (
        f"; original preserved at `{archive_ref}`"
        if archive_read_next
        else "; original preserved in ignored local migration archives"
    )
    return f"""# PDOS state

Keep this concise. Every fresh PDOS context reads it first.

- Protocol version: {PROTOCOL_VERSION}
- State revision: 1
- Updated: {utc_now()}
- State confidence: requires reconciliation after v0.4 migration
- Phase: {bullet_value(original, 'Phase') or 'discovery'}

## Repository identity

- Branch: {bullet_value(original, 'Branch') or 'not recorded'}
- Observed commit: {bullet_value(original, 'Observed commit') or bullet_value(original, 'Commit') or 'not recorded'}

## Product anchors

- Primary user: {bullet_value(original, 'Primary user')}
- Product outcome: {bullet_value(original, 'Product outcome')}
- Critical journey: {bullet_value(original, 'Critical journey')}
- Non-goals: {bullet_value(original, 'Non-goals')}

## Current work

- Current slice: {bullet_value(original, 'Current slice')}
- Active workstreams: {bullet_value(original, 'Active workstreams') or 'see `workstreams/`'}
- Active review:
- Active remediations:
- Blocking dependencies: {bullet_value(original, 'Blocking dependencies')}
- Consequential open decisions: {bullet_value(original, 'Consequential open decisions')}

## Handoff

- What changed: Migrated PDOS state to {PROTOCOL_VERSION}{archive_note}.
- Verification evidence: {bullet_value(original, 'Verification evidence')}
- Not verified: Reconcile migrated state, review policy, and repository evidence before implementation.
- Residual risks: {bullet_value(original, 'Residual risks')}
- Next safe action: Review `.pdos/AUTONOMY.md`, reconcile this handoff, then validate project state.

## Read next

{lines}
"""


def bootstrap(target: Path, sync_agents: bool = True) -> tuple[list[Path], list[Path], list[Path]]:
    project_root = target.resolve()
    pdos_root = project_root / ".pdos"
    existing_version = preflight(project_root)
    template = Path(__file__).resolve().parent.parent / "project-template"
    created: list[Path] = []
    migrated: list[Path] = []

    pdos_root.mkdir(parents=True, exist_ok=True)
    state = pdos_root / "STATE.md"
    if state.exists() and existing_version != PROTOCOL_VERSION:
        original = state.read_text(encoding="utf-8")
        local_archive = _contains_local_user_path(original)
        archive = _archive_path(pdos_root, local_only=local_archive)
        atomic_write_text(archive, original)
        archive_ref = archive.relative_to(pdos_root).as_posix()
        atomic_write_text(state, _migrated_state(original, archive_ref, archive_read_next=not local_archive))
        migrated.extend([state, archive])

    for source in sorted(template.rglob("*")):
        relative = source.relative_to(template)
        output = pdos_root / relative
        if source.is_dir():
            output.mkdir(parents=True, exist_ok=True)
        elif not output.exists():
            atomic_write_text(output, source.read_text(encoding="utf-8"))
            created.append(output)

    version = pdos_root / "VERSION"
    if version.read_text(encoding="utf-8").strip() != PROTOCOL_VERSION:
        atomic_write_text(version, PROTOCOL_VERSION + "\n")
        migrated.append(version)

    for directory in (pdos_root / "private", pdos_root / "local", pdos_root / "local" / "workstreams"):
        directory.mkdir(parents=True, exist_ok=True)
    identity = repository_identity(project_root)
    local_context = pdos_root / "local" / "repository.json"
    atomic_write_text(local_context, json.dumps({"worktree": identity["worktree"]}, indent=2) + "\n")
    guidance = sync_agents_guidance(project_root) if sync_agents else []
    return created, guidance, migrated


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Product Development Operating System state")
    parser.add_argument("target", nargs="?", default=".", help="Project directory")
    parser.add_argument("--no-agents", action="store_true", help="Do not synchronize project AGENTS guidance")
    args = parser.parse_args()
    created, guidance, migrated = bootstrap(Path(args.target), sync_agents=not args.no_agents)
    print(
        f"PDOS {PROTOCOL_VERSION} state ready; created {len(created)} file(s); "
        f"updated {len(guidance)} guidance file(s); migrated {len(migrated)} file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
