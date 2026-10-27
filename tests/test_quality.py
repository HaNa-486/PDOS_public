from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class QualityTests(unittest.TestCase):
    def test_text_assets_are_strict_utf8_without_known_mojibake(self) -> None:
        extensions = {".md", ".yaml", ".yml", ".json", ".py", ".ps1", ".sh", ".txt"}
        bad_markers = ["\ufffd"]
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix.lower() in extensions and "results" not in path.parts and "__pycache__" not in path.parts:
                text = path.read_bytes().decode("utf-8", errors="strict")
                for marker in bad_markers:
                    self.assertNotIn(marker, text, str(path))

    def test_skill_references_are_direct_and_exist(self) -> None:
        skill = ROOT / "skill" / "pdos"
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        import re
        references = re.findall(r"\]\((references/[^)]+)\)", text)
        self.assertIn("references/artifact-profiles.md", references)
        for relative in references:
            self.assertTrue((skill / relative).is_file(), relative)

if __name__ == "__main__":
    unittest.main()
