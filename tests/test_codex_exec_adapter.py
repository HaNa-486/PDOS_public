from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evals" / "runners" / "codex_exec_runner.py"
SPEC = importlib.util.spec_from_file_location("pdos_codex_exec_runner", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def add_pdos(home: Path, source: Path) -> Path:
    destination = home / "skills" / "pdos"
    destination.parent.mkdir(parents=True)
    import shutil
    shutil.copytree(source, destination)
    return destination


class CodexExecAdapterTests(unittest.TestCase):
    def test_rejects_contaminated_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            add_pdos(home, ROOT / "skill" / "pdos")
            with mock.patch.dict(os.environ, {"PDOS_BASELINE_CODEX_HOME": str(home)}, clear=False):
                with self.assertRaises(RuntimeError):
                    MODULE.select_home({"condition": "baseline"})

    def test_requires_exactly_one_matching_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            skill = add_pdos(home, ROOT / "skill" / "pdos")
            expected = MODULE.hash_path(skill)
            with mock.patch.dict(os.environ, {"PDOS_CANDIDATE_CODEX_HOME": str(home)}, clear=False):
                self.assertEqual(MODULE.select_home({"condition": "pdos", "skill_hash": expected}), home.resolve())
                with self.assertRaises(RuntimeError):
                    MODULE.select_home({"condition": "pdos", "skill_hash": "wrong"})


if __name__ == "__main__":
    unittest.main()
