"""End-to-end generic CLI and worktree lifecycle coverage."""

import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from boundary.cli.main import build_parser, main
from boundary.operation.storage import current_operation_path


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stderr or result.stdout)
    return result.stdout.strip()


def request(path: str = "src/a.py", task: str = "task-a") -> dict:
    return {
        "schema": "boundary.pre-change-request/v1",
        "changeId": "change-a",
        "tasks": [{"id": task, "writes": [path]}],
        "selectedTaskIds": [task],
    }


class GenericCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Boundary Tests")
        git(self.root, "config", "user.email", "tests@example.invalid")
        contract = self.root / "contracts" / "app.contract.md"
        contract.parent.mkdir()
        contract.write_text(
            "---\nschema: boundary.contract/v1\nid: app\nowns:\n"
            "  - src/**\n---\n\n# App\n\n## Purpose\n\nOwn app files.\n",
            encoding="utf-8",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "baseline")
        self.call("integration", "install")

    def call(self, *args: str, root: Path | None = None, body: dict | None = None):
        out, err = io.StringIO(), io.StringIO()
        code = main(args, repository_root=root or self.root, stdout=out, stderr=err,
                    stdin=io.StringIO(json.dumps(body)) if body is not None else None)
        value = out.getvalue()
        try:
            value = json.loads(value)
        except ValueError:
            pass
        return code, value, err.getvalue()

    def open(self, path: str = "src/a.py", task: str = "task-a"):
        return self.call("pre-change", "--request", "-", body=request(path, task))

    def write(self, relative: str, content: str = "pass\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_scope_and_unchanged_head(self):
        code, opened, _ = self.open()
        self.assertEqual(0, code)
        self.assertEqual("open", opened["status"])
        self.assertEqual(["src/a.py"], opened["allowedTargets"])
        self.assertTrue(current_operation_path(self.root).is_file())
        self.assertFalse((self.root / ".git" / "boundary").exists())
        self.write("src/a.py")
        code, closed, _ = self.call("post-change")
        self.assertEqual(0, code)
        self.assertEqual("verified", closed["status"])
        code, again, _ = self.call("post-change")
        self.assertEqual(2, code)
        self.assertEqual("NO_OPEN_OPERATION", again["code"])

    def test_undeclared_write_and_abandonment(self):
        self.open()
        self.write("src/b.py")
        code, blocked, _ = self.call("post-change")
        self.assertEqual(2, code)
        self.assertEqual("UNDECLARED_WRITE", blocked["code"])
        self.assertEqual("open", self.call("status")[1]["status"])
        code, abandoned, _ = self.call("post-abandon")
        self.assertEqual(0, code)
        self.assertEqual("abandoned", abandoned["status"])
        self.assertTrue((self.root / "src/b.py").is_file())
        code, opened, _ = self.open("src/c.py")
        self.assertEqual(0, code)
        self.assertEqual("open", opened["status"])

    def test_abandoned_dirty_target_cannot_be_reused(self):
        self.open()
        self.write("src/a.py")
        self.call("post-abandon")
        code, blocked, _ = self.open()
        self.assertEqual(2, code)
        self.assertEqual("DIRTY_TARGET_NOT_VERIFIED", blocked["code"])
        git(self.root, "add", "src/a.py")
        git(self.root, "commit", "-qm", "checkpoint")
        self.assertEqual(0, self.open()[0])

    def test_changed_head_blocks_until_abandon(self):
        self.open()
        git(self.root, "commit", "--allow-empty", "-qm", "move")
        code, blocked, _ = self.call("post-change")
        self.assertEqual(2, code)
        self.assertEqual("GIT_BASELINE_CHANGED", blocked["code"])
        self.assertEqual("open", self.call("status")[1]["status"])
        self.assertEqual("abandoned", self.call("post-abandon")[1]["status"])

    def test_request_validation_and_old_commands(self):
        malformed = request()
        malformed["selectedTaskIds"] = []
        self.assertEqual("INVALID_REQUEST", self.call("pre-change", "--request", "-", body=malformed)[1]["code"])
        for command in ("authorize", "verify"):
            with self.assertRaises(SystemExit):
                build_parser().parse_args([command])

    def test_root_ignore_management_and_open_gate(self):
        path = self.root / ".gitignore"
        path.write_text("user-rule\n" + path.read_text(), encoding="utf-8")
        before = path.read_text()
        self.assertEqual(0, self.call("integration", "install")[0])
        self.assertEqual(before, path.read_text())
        self.open()
        self.assertEqual(2, self.call("integration", "remove")[0])
        self.call("post-abandon")
        self.assertEqual(0, self.call("integration", "remove")[0])
        self.assertEqual("user-rule\n", path.read_text())
        path.write_text("# BEGIN Boundary generated state\n", encoding="utf-8")
        self.assertEqual(2, self.call("integration", "install")[0])

    def test_independent_worktrees_and_legacy_refusal(self):
        other = Path(self.temporary.name) / "other"
        git(self.root, "worktree", "add", "-qb", "other", str(other))
        self.call("integration", "install", root=other)
        self.open()
        self.assertIsNone(self.call("status", root=other)[1])
        self.assertNotEqual(current_operation_path(self.root), current_operation_path(other))
        self.call("post-abandon")
        legacy = self.root / ".git" / "boundary"
        legacy.mkdir()
        (legacy / "current.json").write_text("{}\n")
        code, _, err = self.call("status")
        self.assertEqual(2, code)
        self.assertIn("legacy", err)

    def test_distinct_task_reuse_requires_checkpoint(self):
        self.open()
        self.write("src/a.py")
        self.assertEqual(0, self.call("post-change")[0])
        code, blocked, _ = self.open("src/a.py", "task-b")
        self.assertEqual(2, code)
        self.assertEqual("DIRTY_TARGET_NOT_VERIFIED", blocked["code"])
        git(self.root, "add", "src/a.py")
        git(self.root, "commit", "-qm", "task checkpoint")
        self.assertEqual(0, self.open("src/a.py", "task-b")[0])

    def test_state_path_must_be_confined_and_untracked(self):
        external = Path(self.temporary.name) / "outside"
        external.mkdir()
        state = self.root / ".boundary-state"
        state.symlink_to(external, target_is_directory=True)
        code, blocked, _ = self.open()
        self.assertEqual(2, code)
        self.assertEqual("OPERATION_EVIDENCE_UNAVAILABLE", blocked["code"])
        state.unlink()
        state.mkdir()
        (state / "tracked.txt").write_text("tracked\n")
        git(self.root, "add", "-f", ".boundary-state/tracked.txt")
        code, blocked, _ = self.open()
        self.assertEqual(2, code)
        self.assertEqual("OPERATION_EVIDENCE_UNAVAILABLE", blocked["code"])

    def test_status_and_inspection_are_read_only_during_open_operation(self):
        self.open()
        before = current_operation_path(self.root).read_bytes()
        self.assertEqual("open", self.call("status")[1]["status"])
        code, inspected, _ = self.call("inspect", "--authorized")
        self.assertEqual(0, code)
        self.assertIn("src/a.py", inspected)
        self.assertEqual(before, current_operation_path(self.root).read_bytes())

    def test_contract_evolution_is_separate(self):
        target = "contracts/extra.contract.md"
        code, opened, _ = self.call("contracts", "pre-change", "--change", "contract-a", target)
        self.assertEqual(0, code)
        self.assertEqual("open", opened["status"])
        (self.root / target).write_text(
            "---\nschema: boundary.contract/v1\nid: extra\nowns:\n  - docs/**\n---\n\n# Extra\n\n## Purpose\n\nOwn docs.\n"
        )
        self.assertEqual(0, self.call("contracts", "check")[0])
        self.assertEqual("verified", self.call("post-change")[1]["status"])


if __name__ == "__main__":
    unittest.main()
