import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SKILLS = {
    "boundary-scope": REPO_ROOT / "skills" / "scope" / "SKILL.md",
    "boundary-implement": REPO_ROOT / "skills" / "implement" / "SKILL.md",
    "boundary-contracts": REPO_ROOT / "skills" / "contracts" / "SKILL.md",
}


class CanonicalBoundarySkillTests(unittest.TestCase):
    def _content(self, name: str) -> str:
        return SKILLS[name].read_text(encoding="utf-8")

    def test_canonical_skills_are_small_plain_markdown(self):
        for name, path in SKILLS.items():
            with self.subTest(skill=name):
                content = path.read_text(encoding="utf-8")
                self.assertTrue(content.startswith(f"# {name}\n"))
                self.assertLessEqual(len(content.splitlines()), 250)
                self.assertFalse(content.startswith("---\n"))

    def test_canonical_skills_exclude_vendor_and_transient_state(self):
        forbidden = (
            ".agents/",
            ".specdd/",
            "Spec Kit",
            "SpecDD",
            "Codex",
            "Claude",
            "SPECDD_AUTHORITY",
            "boundary.json",
            "authorizationSnapshot",
        )
        version_pattern = re.compile(r"\b\d+\.\d+(?:\.\d+)?\b")
        hash_pattern = re.compile(r"\b[0-9a-fA-F]{40,64}\b")

        for name in SKILLS:
            with self.subTest(skill=name):
                content = self._content(name)
                for marker in forbidden:
                    self.assertNotIn(marker, content)
                self.assertIsNone(version_pattern.search(content))
                self.assertIsNone(hash_pattern.search(content))

    def test_scope_skill_uses_generic_request(self):
        content = self._content("boundary-scope")
        for marker in ("exact repository-relative targets", "boundary inspect", "structured write declaration", "boundary pre-change --request FILE"):
            self.assertIn(marker, content)

    def test_implementation_skill_describes_all_closing_transitions(self):
        content = self._content("boundary-implement")
        for marker in ("boundary inspect --authorized", "boundary post-change", "boundary post-abandon", "Git `HEAD`", "same task identity"):
            self.assertIn(marker, content)

    def test_contract_skill_enforces_operation_separation(self):
        content = self._content("boundary-contracts")
        for marker in ("persistent Boundary contracts", "boundary contracts pre-change", "boundary contracts check", "boundary post-change", "fresh implementation pre-change"):
            self.assertIn(marker, content)


if __name__ == "__main__":
    unittest.main()
