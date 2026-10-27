from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pdos_install", ROOT / "install.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SOURCE = ROOT / "skill" / "pdos"


def old_install(path: Path) -> None:
    (path / "scripts").mkdir(parents=True)
    (path / "SKILL.md").write_text("---\nname: pdos\n---\nProduct Development Operating System (PDOS)\n", encoding="utf-8")
    (path / "VERSION").write_text("0.3.0\n", encoding="utf-8")
    (path / "scripts" / "bootstrap_project.py").write_text("# old\n", encoding="utf-8")


class InstallTests(unittest.TestCase):
    def test_backup_and_legacy_copies_live_outside_skill_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "codex"
            destination = home / "skills" / "pdos"
            old_install(destination)
            legacy = home / "skills" / "pdos.backup-legacy"
            old_install(legacy)
            result = MODULE.install(SOURCE, destination, home)
            self.assertEqual((destination / "VERSION").read_text().strip(), "0.4.0-alpha.1")
            self.assertTrue(result["backup"])
            self.assertFalse(any((home / "skills").glob("pdos.backup-*")))
            self.assertGreaterEqual(len(list((home / "skill-backups" / "pdos").rglob("VERSION"))), 2)

    def test_invalid_source_preserves_existing_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "codex"
            destination = home / "skills" / "pdos"
            old_install(destination)
            invalid = root / "invalid"
            invalid.mkdir()
            with self.assertRaises(ValueError):
                MODULE.install(invalid, destination, home)
            self.assertEqual((destination / "VERSION").read_text().strip(), "0.3.0")

    def test_install_failure_rolls_back_previous_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "codex"
            destination = home / "skills" / "pdos"
            old_install(destination)
            original_replace = MODULE.os.replace
            calls = {"count": 0}

            def injected(source, target):
                calls["count"] += 1
                if calls["count"] == 2:
                    raise OSError("injected stage activation failure")
                return original_replace(source, target)

            with mock.patch.object(MODULE.os, "replace", side_effect=injected):
                with self.assertRaises(OSError):
                    MODULE.install(SOURCE, destination, home)
            self.assertEqual((destination / "VERSION").read_text().strip(), "0.3.0")

    def test_release_skill_and_template_versions_match(self) -> None:
        release = (ROOT / "VERSION").read_text().strip()
        self.assertEqual((SOURCE / "VERSION").read_text().strip(), release)
        self.assertEqual((SOURCE / "project-template" / "VERSION").read_text().strip(), release)


if __name__ == "__main__":
    unittest.main()
