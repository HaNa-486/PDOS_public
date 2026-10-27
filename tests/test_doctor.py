from __future__ import annotations

import importlib.util
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
DOCTOR = load("pdos_doctor")


def make_current(root: Path) -> None:
    BOOTSTRAP.bootstrap(root)
    state = root / ".pdos" / "STATE.md"
    text = state.read_text(encoding="utf-8")
    identity = COMMON.repository_identity(root)
    text = text.replace("- Updated: not yet", "- Updated: 2026-08-13T00:00:00Z")
    text = text.replace("- Branch: not recorded", f"- Branch: {identity['branch']}")
    text = text.replace("- Observed commit: not recorded", f"- Observed commit: {identity['observed_commit']}")
    state.write_text(text, encoding="utf-8")


class DoctorTests(unittest.TestCase):
    def test_reports_healthy_project_and_version(self) -> None:
        with tempfile.TemporaryDirectory() as project_tmp, tempfile.TemporaryDirectory() as home_tmp:
            project, home = Path(project_tmp), Path(home_tmp)
            make_current(project)
            report = DOCTOR.diagnose(project, home)
            self.assertEqual(report["installed_version"], COMMON.VERSION)
            self.assertEqual(report["project_protocol"], COMMON.VERSION)
            self.assertEqual(report["problems"], [])
            self.assertIn("Invoke $pdos", report["next_safe_action"])

    def test_reports_legacy_protocol_and_repairs_duplicate_backup(self) -> None:
        with tempfile.TemporaryDirectory() as project_tmp, tempfile.TemporaryDirectory() as home_tmp:
            project, home = Path(project_tmp), Path(home_tmp)
            pdos = project / ".pdos"
            pdos.mkdir()
            (pdos / "STATE.md").write_text("# PDOS state\n\n- Protocol version: 0.3.0\n", encoding="utf-8")
            duplicate = home / "skills" / "pdos.backup-old"
            duplicate.mkdir(parents=True)
            (duplicate / "SKILL.md").write_text("duplicate", encoding="utf-8")
            report = DOCTOR.diagnose(project, home, repair_safe=True)
            self.assertTrue(any("needs upgrade" in item for item in report["problems"]))
            self.assertTrue(report["repairs"])
            self.assertFalse(duplicate.exists())
            self.assertTrue(list((home / "skill-backups" / "pdos").rglob("SKILL.md")))


if __name__ == "__main__":
    unittest.main()
