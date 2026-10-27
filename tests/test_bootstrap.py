from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "pdos" / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "bootstrap_project.py"
SPEC = importlib.util.spec_from_file_location("pdos_bootstrap", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BootstrapTests(unittest.TestCase):
    def test_creates_v04_state_policy_and_guidance_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            created, guidance, migrated = MODULE.bootstrap(root)
            self.assertIn(root / ".pdos" / "STATE.md", created)
            self.assertIn(root / ".pdos" / "AUTONOMY.md", created)
            self.assertEqual(guidance, [root / "AGENTS.md"])
            self.assertEqual(migrated, [])
            self.assertEqual((root / ".pdos" / "VERSION").read_text().strip(), MODULE.PROTOCOL_VERSION)
            first = (root / "AGENTS.md").read_text(encoding="utf-8")
            created_again, guidance_again, migrated_again = MODULE.bootstrap(root)
            self.assertEqual(created_again, [])
            self.assertEqual(guidance_again, [])
            self.assertEqual(migrated_again, [])
            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8"), first)

    def test_migrates_v03_exactly_and_preserves_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pdos = root / ".pdos"
            pdos.mkdir()
            legacy = """# PDOS state

- Protocol version: 0.3.0
- Phase: implementation
- Branch: main
- Commit: abc123
- Primary user: founder
- Product outcome: launch safely
- Current slice: permissions
- Residual risks: rollback

## Read next

- `specs/product.md`
"""
            (pdos / "STATE.md").write_text(legacy, encoding="utf-8")
            (pdos / "VERSION").write_text("0.3.0\n", encoding="utf-8")
            policy = "# Custom autonomy\n\n- Default class: human-only\n\n## auto-decide\n\n## independent-review-required\n\n## human-only\n"
            (pdos / "AUTONOMY.md").write_text(policy, encoding="utf-8")
            _, _, migrated = MODULE.bootstrap(root)
            archives = list((pdos / "archive").glob("STATE-pre-v0.4*.md"))
            self.assertEqual(len(archives), 1)
            self.assertEqual(archives[0].read_text(encoding="utf-8"), legacy)
            state = (pdos / "STATE.md").read_text(encoding="utf-8")
            self.assertIn(f"- Protocol version: {MODULE.PROTOCOL_VERSION}", state)
            self.assertIn("- Observed commit: abc123", state)
            self.assertIn("- Current slice: permissions", state)
            self.assertEqual((pdos / "AUTONOMY.md").read_text(encoding="utf-8"), policy)
            self.assertIn(pdos / "STATE.md", migrated)

    def test_malformed_agents_preflight_leaves_project_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            agents = root / "AGENTS.md"
            original = f"# Rules\n{MODULE.START_MARKER}\nmissing end\n"
            agents.write_text(original, encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.bootstrap(root)
            self.assertEqual(agents.read_text(encoding="utf-8"), original)
            self.assertFalse((root / ".pdos").exists())

    def test_refuses_future_protocol_without_modification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pdos = root / ".pdos"
            pdos.mkdir()
            future = "# PDOS state\n\n- Protocol version: 0.5.0\n"
            (pdos / "STATE.md").write_text(future, encoding="utf-8")
            (pdos / "VERSION").write_text("0.5.0\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.bootstrap(root)
            self.assertEqual((pdos / "STATE.md").read_text(encoding="utf-8"), future)
            self.assertFalse((pdos / "archive").exists())

    def test_shared_templates_do_not_contain_absolute_user_paths(self) -> None:
        for path in (ROOT / "skill" / "pdos" / "project-template").rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("C:\\Users\\", text)
                self.assertNotIn("/Users/", text)

    def test_legacy_state_with_local_path_archives_only_under_ignored_local(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pdos = root / ".pdos"
            pdos.mkdir()
            legacy = "# PDOS state\n\n- Protocol version: 0.3.0\n- Worktree: C:\\Users\\alice\\project\n"
            (pdos / "STATE.md").write_text(legacy, encoding="utf-8")
            (pdos / "VERSION").write_text("0.3.0\n", encoding="utf-8")
            MODULE.bootstrap(root)
            local_archives = list((pdos / "local" / "migration-archives").glob("STATE-pre-v0.4*.md"))
            self.assertEqual(len(local_archives), 1)
            self.assertEqual(local_archives[0].read_text(encoding="utf-8"), legacy)
            self.assertFalse(list((pdos / "archive").glob("STATE-pre-v0.4*.md")))
            self.assertNotIn("`local/migration-archives/", (pdos / "STATE.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
