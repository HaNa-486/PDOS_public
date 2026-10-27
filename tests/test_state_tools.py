from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "pdos" / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BOOTSTRAP = load("bootstrap_project")
COMMON = load("pdos_common")
WORKSTREAM = load("start_workstream")
UPDATE = load("update_workstream")
RECORDS = load("review_remediation")
VALIDATOR = load("validate_project_state")


def make_current(root: Path) -> None:
    BOOTSTRAP.bootstrap(root)
    state_path = root / ".pdos" / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    identity = COMMON.repository_identity(root)
    state = state.replace("- Updated: not yet", "- Updated: 2026-08-13T00:00:00Z")
    state = state.replace("- State confidence: provisional", "- State confidence: current")
    state = state.replace("- Branch: not recorded", f"- Branch: {identity['branch']}")
    state = state.replace("- Observed commit: not recorded", f"- Observed commit: {identity['observed_commit']}")
    state_path.write_text(state, encoding="utf-8")


def valid_review_and_remediation(root: Path) -> tuple[Path, Path]:
    review = root / ".pdos" / "reviews" / "REV-20260813-auth.md"
    remediation = root / ".pdos" / "remediations" / "REM-20260813-auth-F001.md"
    review.write_text("""# Review: auth

- Review ID: REV-20260813-auth
- Mode: review-and-plan
- Status: open
- Created: 2026-08-13T00:00:00Z
- Scope: auth
- Release assessment: not-ready

## Findings

### F-001

- Severity: high
- Confidence: high
- Status: open
- Evidence: cross-tenant request returns 200
- User impact: tenant leak
- Root cause: query lacks tenant scope
- Recommended solution: add tenant scope
- Alternatives and tradeoffs: policy middleware is larger
- Affected areas: api auth
- Acceptance criteria: cross-tenant returns 404
- Verification: integration test
- Residual risk: other endpoints
- Autonomy class: independent-review-required
- Remediation: remediations/REM-20260813-auth-F001.md
""", encoding="utf-8")
    remediation.write_text("""# Remediation: auth

- Remediation ID: REM-20260813-auth-F001
- Review finding: reviews/REV-20260813-auth.md#F-001
- Status: open
- Severity: high
- Autonomy class: independent-review-required
- Owner: agent
- Updated: 2026-08-13T00:00:00Z
- Decision authority: reviewer
- Reason:
- Revisit condition:

## Plan

- Recommended solution: add tenant scope
- Acceptance criteria: cross-tenant returns 404
- Verification plan: integration test
- Rollback: revert patch

## Evidence

- Implementation:
- Verification:
- Residual risk:

## History

- created
""", encoding="utf-8")
    return review, remediation


class StateToolTests(unittest.TestCase):
    def test_current_bootstrap_validates_strictly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_current(root)
            report = VALIDATOR.validate_project(root)
            self.assertTrue(report["ok"], report)
            self.assertEqual(report["warnings"], [])

    def test_workstream_creation_and_close_are_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_current(root)
            first = WORKSTREAM.start_workstream(root, "Permissions", "Implement permissions", "api, ui")
            second = WORKSTREAM.start_workstream(root, "Permissions", "Implement permissions", "api, ui")
            self.assertNotEqual(first, second)
            self.assertNotIn(str(root.resolve()), first.read_text(encoding="utf-8"))
            local = root / ".pdos" / "local" / "workstreams" / f"{first.stem}.json"
            self.assertTrue(local.exists())
            UPDATE.update(first, "completed", "fixed", "tests passed", "none", "archive")
            self.assertIn("- Status: completed", first.read_text(encoding="utf-8"))
            with self.assertRaises(ValueError):
                UPDATE.update(first, "active")

    def test_review_schema_and_remediation_transition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_current(root)
            review, remediation = valid_review_and_remediation(root)
            self.assertEqual(RECORDS.validate_project_records(root)["errors"], [])
            RECORDS.transition(remediation, "planned")
            RECORDS.transition(remediation, "in_progress")
            RECORDS.transition(remediation, "implemented")
            with self.assertRaises(ValueError):
                RECORDS.transition(remediation, "verified")
            RECORDS.transition(remediation, "verified", evidence="authorization integration test passed")
            self.assertEqual(RECORDS.validate_remediation(remediation, root), [])
            text = review.read_text(encoding="utf-8").replace("- Release assessment: not-ready", "- Release assessment: ready")
            review.write_text(text, encoding="utf-8")
            self.assertTrue(any("ready conflicts" in item for item in RECORDS.validate_review(review, root)))

    def test_invalid_autonomy_and_duplicate_finding_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_current(root)
            review, _ = valid_review_and_remediation(root)
            text = review.read_text(encoding="utf-8")
            block = re.search(r"^### F-001[\s\S]*", text, re.MULTILINE).group(0)  # type: ignore[union-attr]
            review.write_text(text + "\n" + block, encoding="utf-8")
            policy = root / ".pdos" / "AUTONOMY.md"
            policy.write_text(policy.read_text().replace("- Default class: human-only", "- Default class: unlimited"), encoding="utf-8")
            report = RECORDS.validate_project_records(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("duplicate finding" in item for item in report["errors"]))
            self.assertTrue(any("default class" in item for item in report["errors"]))

    def test_oversized_state_absolute_path_and_secret_filename_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_current(root)
            state = root / ".pdos" / "STATE.md"
            state.write_text(state.read_text(encoding="utf-8") + "C:\\Users\\alice\\secret\n" + ("x\n" * 10000), encoding="utf-8")
            (root / ".pdos" / "prod.key").write_text("not-a-real-secret", encoding="utf-8")
            report = VALIDATOR.validate_project(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("limit" in item for item in report["errors"]))
            self.assertTrue(any("absolute user path" in item for item in report["errors"]))
            self.assertTrue(any("Secret-bearing filename" in item for item in report["errors"]))


if __name__ == "__main__":
    unittest.main()
