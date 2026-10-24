"""Explicit, runtime-neutral skill delivery."""

import io
from pathlib import Path
import subprocess
import tempfile
import unittest

from boundary.cli.main import main


class SkillDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Boundary Tests"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "tests@example.invalid"], cwd=self.root, check=True)
        (self.root / "README.md").write_text("fixture\n")
        subprocess.run(["git", "add", "README.md"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=self.root, check=True)

    def call(self, *args):
        output, errors = io.StringIO(), io.StringIO()
        code = main(args, repository_root=self.root, stdout=output, stderr=errors)
        return code, output.getvalue(), errors.getvalue()

    def test_explicit_directory_and_repair(self):
        self.assertEqual(0, self.call("skills", "install", "--directory", "custom/skills")[0])
        target = self.root / "custom/skills/boundary-scope/SKILL.md"
        self.assertIn("name: boundary-scope", target.read_text())
        self.assertFalse((self.root / ".agents").exists())
        self.assertFalse((self.root / ".claude").exists())
        self.assertEqual(0, self.call("skills", "check", "--directory", "custom/skills")[0])
        target.write_text(target.read_text() + "stale\n")
        self.assertEqual(2, self.call("skills", "check", "--directory", "custom/skills")[0])
        self.assertEqual(0, self.call("skills", "install", "--directory", "custom/skills")[0])
        self.assertEqual(0, self.call("skills", "check", "--directory", "custom/skills")[0])
        self.assertEqual(0, self.call("skills", "remove", "--directory", "custom/skills")[0])
        self.assertFalse(target.exists())

    def test_rejects_unsafe_paths_and_preserves_unrelated_files(self):
        for value in ("../outside", "/tmp/outside", ".git/skills", ".boundary-state/skills"):
            with self.subTest(value=value):
                self.assertEqual(2, self.call("skills", "install", "--directory", value)[0])
        target = self.root / "custom/skills/boundary-scope/SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_text("user file\n")
        self.assertEqual(2, self.call("skills", "install", "--directory", "custom/skills")[0])
        self.assertEqual("user file\n", target.read_text())
        target.unlink()
        target.symlink_to(self.root / "README.md")
        self.assertEqual(2, self.call("skills", "install", "--directory", "custom/skills")[0])
        self.assertEqual("fixture\n", (self.root / "README.md").read_text())

    def test_setup_only_ignores_local_evidence(self):
        self.assertEqual(0, self.call("setup", "install")[0])
        content = (self.root / ".gitignore").read_text()
        self.assertIn("/.boundary-state/", content)
        self.assertNotIn("skills/", content)
        self.assertEqual(0, self.call("setup", "check")[0])


if __name__ == "__main__":
    unittest.main()
