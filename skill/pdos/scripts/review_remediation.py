#!/usr/bin/env python3
"""Validate PDOS reviews/remediations and perform guarded lifecycle transitions."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pdos_common import atomic_write_text, bullet_value


AUTONOMY_CLASSES = {"auto-decide", "independent-review-required", "human-only"}
STATUSES = {"open", "planned", "in_progress", "implemented", "verified", "blocked", "deferred", "rejected", "reopened"}
TRANSITIONS = {
    "open": {"planned", "blocked", "deferred", "rejected"},
    "planned": {"in_progress", "blocked", "deferred", "rejected"},
    "in_progress": {"implemented", "blocked"},
    "implemented": {"verified", "reopened"},
    "verified": {"reopened"},
    "blocked": {"planned", "in_progress", "deferred", "rejected"},
    "deferred": {"planned", "reopened"},
    "rejected": {"reopened"},
    "reopened": {"open"},
}
REVIEW_FIELDS = ["Review ID", "Mode", "Status", "Created", "Scope", "Release assessment"]
FINDING_FIELDS = [
    "Severity", "Confidence", "Status", "Evidence", "User impact", "Root cause",
    "Recommended solution", "Alternatives and tradeoffs", "Affected areas", "Acceptance criteria",
    "Verification", "Residual risk", "Autonomy class", "Remediation",
]
REMEDIATION_FIELDS = [
    "Remediation ID", "Review finding", "Status", "Severity", "Autonomy class", "Owner", "Updated",
    "Decision authority", "Reason", "Revisit condition",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sections(text: str, pattern: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    result: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result.append((match.group(1).strip(), text[match.end():end]))
    return result


def validate_autonomy(path: Path) -> list[str]:
    if not path.exists():
        return ["Missing .pdos/AUTONOMY.md"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if bullet_value(text, "Default class") not in AUTONOMY_CLASSES:
        errors.append("AUTONOMY.md default class must be a supported autonomy class")
    for name in sorted(AUTONOMY_CLASSES):
        if f"## {name}" not in text:
            errors.append(f"AUTONOMY.md missing section: {name}")
    return errors


def validate_review(path: Path, project_root: Path | None = None) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for field in REVIEW_FIELDS:
        if not bullet_value(text, field):
            errors.append(f"{path.name}: missing review field {field}")
    if bullet_value(text, "Mode") not in {"review", "review-and-plan", "review-and-fix"}:
        errors.append(f"{path.name}: invalid review mode")
    findings = _sections(text, r"^###\s+(F-\d{3,})\s*$")
    if not findings:
        errors.append(f"{path.name}: review has no findings")
        return errors
    ids = [item[0] for item in findings]
    if len(ids) != len(set(ids)):
        errors.append(f"{path.name}: duplicate finding ID")
    unresolved_critical = False
    for finding_id, body in findings:
        for field in FINDING_FIELDS:
            if not bullet_value(body, field):
                errors.append(f"{path.name}#{finding_id}: missing {field}")
        severity = bullet_value(body, "Severity")
        status = bullet_value(body, "Status")
        autonomy = bullet_value(body, "Autonomy class")
        if severity not in {"critical", "high", "medium", "low"}:
            errors.append(f"{path.name}#{finding_id}: invalid severity")
        if status not in STATUSES:
            errors.append(f"{path.name}#{finding_id}: invalid status")
        if autonomy not in AUTONOMY_CLASSES:
            errors.append(f"{path.name}#{finding_id}: invalid autonomy class")
        if severity in {"critical", "high"} and status != "verified":
            unresolved_critical = True
        remediation = bullet_value(body, "Remediation").split("#", 1)[0]
        if project_root and remediation and not (project_root / ".pdos" / remediation).exists():
            errors.append(f"{path.name}#{finding_id}: remediation link does not exist: {remediation}")
    if bullet_value(text, "Release assessment") == "ready" and unresolved_critical:
        errors.append(f"{path.name}: ready conflicts with unresolved critical/high finding")
    return errors


def validate_remediation(path: Path, project_root: Path | None = None) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for field in REMEDIATION_FIELDS:
        if not bullet_value(text, field):
            if field not in {"Reason", "Revisit condition"}:
                errors.append(f"{path.name}: missing remediation field {field}")
    status = bullet_value(text, "Status")
    autonomy = bullet_value(text, "Autonomy class")
    if status not in STATUSES:
        errors.append(f"{path.name}: invalid remediation status")
    if autonomy not in AUTONOMY_CLASSES:
        errors.append(f"{path.name}: invalid autonomy class")
    evidence = _section_body(text, "## Evidence")
    if status == "verified" and not bullet_value(evidence, "Verification"):
        errors.append(f"{path.name}: verified remediation requires verification evidence")
    if status in {"deferred", "rejected"}:
        for field in ("Reason", "Decision authority", "Revisit condition"):
            if not bullet_value(text, field) or bullet_value(text, field) == "pending":
                errors.append(f"{path.name}: {status} remediation requires {field}")
    reference = bullet_value(text, "Review finding")
    if project_root and reference:
        file_ref, _, anchor = reference.partition("#")
        review_path = project_root / ".pdos" / file_ref
        if not review_path.exists():
            errors.append(f"{path.name}: review link does not exist: {file_ref}")
        elif anchor and f"### {anchor}" not in review_path.read_text(encoding="utf-8"):
            errors.append(f"{path.name}: review finding anchor does not exist: {anchor}")
    return errors


def _section_body(text: str, heading: str) -> str:
    match = re.search(rf"^{re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)", text, re.MULTILINE)
    return match.group(1) if match else ""


def validate_project_records(project_root: Path) -> dict[str, object]:
    pdos = project_root.resolve() / ".pdos"
    errors = validate_autonomy(pdos / "AUTONOMY.md")
    reviews: list[str] = []
    remediations: list[str] = []
    for path in sorted((pdos / "reviews").glob("*.md")):
        if path.name != "_template.md":
            errors.extend(validate_review(path, project_root.resolve()))
            reviews.append(path.name)
    for path in sorted((pdos / "remediations").glob("*.md")):
        if path.name != "_template.md":
            errors.extend(validate_remediation(path, project_root.resolve()))
            remediations.append(path.name)
    return {"ok": not errors, "errors": errors, "reviews": reviews, "remediations": remediations}


def transition(path: Path, new_status: str, evidence: str = "", reason: str = "", authority: str = "", revisit: str = "") -> None:
    if new_status not in STATUSES:
        raise ValueError(f"Unknown remediation status: {new_status}")
    text = path.read_text(encoding="utf-8")
    current = bullet_value(text, "Status")
    if new_status not in TRANSITIONS.get(current, set()):
        raise ValueError(f"Invalid remediation transition: {current} -> {new_status}")
    if new_status == "verified" and not evidence.strip():
        raise ValueError("Verification evidence is required for verified")
    if new_status in {"deferred", "rejected"} and not all(item.strip() for item in (reason, authority, revisit)):
        raise ValueError(f"{new_status} requires reason, authority, and revisit condition")
    updated = re.sub(r"^- Status:\s*.*$", f"- Status: {new_status}", text, count=1, flags=re.MULTILINE)
    updated = re.sub(r"^- Updated:\s*.*$", f"- Updated: {utc_now()}", updated, count=1, flags=re.MULTILINE)
    if reason:
        updated = re.sub(r"^- Reason:\s*.*$", f"- Reason: {reason}", updated, count=1, flags=re.MULTILINE)
    if authority:
        updated = re.sub(r"^- Decision authority:\s*.*$", f"- Decision authority: {authority}", updated, count=1, flags=re.MULTILINE)
    if revisit:
        updated = re.sub(r"^- Revisit condition:\s*.*$", f"- Revisit condition: {revisit}", updated, count=1, flags=re.MULTILINE)
    if evidence:
        updated = re.sub(r"^- Verification:\s*.*$", f"- Verification: {evidence}", updated, count=1, flags=re.MULTILINE)
    history = f"- {utc_now()} {new_status}: {evidence or reason or 'status updated'}."
    if not updated.endswith("\n"):
        updated += "\n"
    updated += history + "\n"
    atomic_write_text(path, updated)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or transition PDOS review/remediation records")
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("target", nargs="?", default=".")
    validate_parser.add_argument("--json", action="store_true")
    transition_parser = sub.add_parser("transition")
    transition_parser.add_argument("file")
    transition_parser.add_argument("status")
    transition_parser.add_argument("--evidence", default="")
    transition_parser.add_argument("--reason", default="")
    transition_parser.add_argument("--authority", default="")
    transition_parser.add_argument("--revisit", default="")
    args = parser.parse_args()
    if args.command == "transition":
        transition(Path(args.file), args.status, args.evidence, args.reason, args.authority, args.revisit)
        print(f"Updated {args.file} to {args.status}")
        return 0
    report = validate_project_records(Path(args.target))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for error in report["errors"]:
            print(f"ERROR: {error}")
        print("PDOS review/remediation records valid" if report["ok"] else "PDOS records need attention")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
