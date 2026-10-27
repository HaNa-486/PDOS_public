from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "evals" / "run_evals.py"
MOCK = ROOT / "tests" / "fixtures" / "mock_runner.py"


class EvalRunnerTests(unittest.TestCase):
    def run_eval(self, results: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(RUNNER), "--results-dir", str(results), *arguments],
            cwd=ROOT, check=False, capture_output=True, text=True, timeout=120,
        )

    def test_fixture_smoke_is_explicitly_not_live(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            results = Path(temporary)
            completed = self.run_eval(results)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            report = json.loads((results / "latest.json").read_text(encoding="utf-8"))
            self.assertEqual(report["benchmark_status"], "fixture_only")
            self.assertFalse(report["release_qualified"])
            self.assertEqual(report["pdos"]["summary"]["passed"], report["pdos"]["summary"]["total"])
            self.assertGreater(report["pdos"]["summary"]["score"], report["baseline"]["summary"]["score"])
            self.assertTrue((results / "runs" / report["run_id"] / "report.json").exists())

    def test_missing_pdos_response_fails_gate(self) -> None:
        with tempfile.TemporaryDirectory() as empty, tempfile.TemporaryDirectory() as results:
            completed = self.run_eval(Path(results), "--pdos-dir", empty)
            self.assertEqual(completed.returncode, 1)

    def test_benchmark_without_runner_skips_but_require_live_fails(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            skipped = self.run_eval(Path(first), "--profile", "benchmark")
            self.assertEqual(skipped.returncode, 0)
            report = json.loads((Path(first) / "latest.json").read_text())
            self.assertEqual(report["benchmark_status"], "skipped_no_runner")
            required = self.run_eval(Path(second), "--profile", "benchmark", "--require-live")
            self.assertEqual(required.returncode, 1)

    def test_repeated_live_benchmark_captures_metadata_and_blind_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            results = Path(temporary)
            command = f'"{sys.executable}" "{MOCK}"'
            completed = self.run_eval(results, "--profile", "benchmark", "--trials", "2", "--live-runner", command, "--semantic-runner", command)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            report = json.loads((results / "latest.json").read_text(encoding="utf-8"))
            total_cases = report["pdos"]["summary"]["total"]
            self.assertEqual(report["live"]["capture_count"], total_cases * 2 * 2)
            self.assertEqual(report["benchmark_status"], "live_completed")
            self.assertEqual(report["semantic"]["status"], "completed")
            self.assertTrue(report["pdos"]["metrics"]["total_tokens"]["available"])
            self.assertFalse(report["live"]["paired_model_mismatch"])
            run_dir = results / "runs" / report["run_id"]
            captures = list((run_dir / "captures").rglob("*.json"))
            self.assertEqual(len(captures), total_cases * 2 * 2)
            sample = json.loads(captures[0].read_text())
            self.assertTrue(sample["context_id"])
            self.assertIn("prompt_hash", sample)
            self.assertIn("fixture_hash", sample)
            self.assertEqual(sample["metadata"]["tokens"]["total"], 150)

    def test_release_profile_fails_without_human_and_regression_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            command = f'"{sys.executable}" "{MOCK}"'
            completed = self.run_eval(Path(temporary), "--profile", "release", "--trials", "1", "--live-runner", command, "--semantic-runner", command)
            self.assertEqual(completed.returncode, 1)
            report = json.loads((Path(temporary) / "latest.json").read_text())
            self.assertFalse(report["release_qualified"])
            self.assertEqual(report["human_review"]["status"], "pending")
            self.assertEqual(report["regression"]["status"], "not_run")


if __name__ == "__main__":
    unittest.main()
