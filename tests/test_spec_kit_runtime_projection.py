"""Focused tests for current packaged Spec Kit projection behavior."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from boundary_host.adapter import preflight_declared_scope, project_change
from boundary_host.discovery import active_feature
from boundary_host.errors import SpecKitAdapterError
from boundary_host.tasks import parse_tasks


class SpecKitRuntimeProjectionTests(unittest.TestCase):
    def test_tasks_use_only_directly_attached_writes_metadata(self) -> None:
        tasks = parse_tasks(
            "# Tasks\n\n"
            "- [ ] T001 [US1] Update app mentioning `ignored.py`\n"
            "  Writes: `src/app.py`, `src/config.py`\n"
            "- [ ] T002 [P] [US1] Update docs\n"
            "  Writes: `docs/app.md`\n"
        )
        self.assertEqual(("T001", "T002"), tuple(task.task_id for task in tasks))
        self.assertEqual(("src/app.py", "src/config.py"), tasks[0].writes)
        self.assertEqual("US1", tasks[0].story)
        self.assertEqual(("docs/app.md",), tasks[1].writes)

    def test_writes_metadata_must_be_directly_attached(self) -> None:
        with self.assertRaisesRegex(
            SpecKitAdapterError,
            "directly attached",
        ):
            parse_tasks(
                "- [ ] T001 Update app\n"
                "  explanatory prose\n"
                "  Writes: `src/app.py`\n"
            )

    def test_project_change_and_preflight_use_declared_union(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            feature = root / "specs" / "001-example"
            feature.mkdir(parents=True)
            (feature / "tasks.md").write_text(
                "- [ ] T001 [US1] Update app\n"
                "  Writes: `src/app.py`\n"
                "- [ ] T002 [US1] Update config\n"
                "  Writes: `src/config.py`\n",
                encoding="utf-8",
            )
            contracts = root / "contracts"
            contracts.mkdir()
            (contracts / "app.contract.md").write_text(
                "---\n"
                "schema: boundary.contract/v1\n"
                "id: app\n"
                "owns:\n"
                "  - src/**\n"
                "---\n\n"
                "## Invariants\n\n"
                "- Application source remains owned.\n",
                encoding="utf-8",
            )

            change = project_change(root, feature)
            self.assertEqual("001-example", change.change_id)
            self.assertEqual(("src/app.py", "src/config.py"), change.writes)
            selected = change.select_tasks(("T002",))
            self.assertEqual(("T002",), tuple(task.task_id for task in selected))
            self.assertEqual(("src/config.py",), selected[0].writes)

            contexts = preflight_declared_scope(root, feature)
            self.assertEqual(("app", "app"), tuple(item.owner_id for item in contexts))

    def test_preflight_rejects_unowned_declared_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            feature = root / "specs" / "001-example"
            feature.mkdir(parents=True)
            (feature / "tasks.md").write_text(
                "- [ ] T001 Update app\n"
                "  Writes: `src/app.py`\n",
                encoding="utf-8",
            )
            contracts = root / "contracts"
            contracts.mkdir()
            (contracts / "docs.contract.md").write_text(
                "---\n"
                "schema: boundary.contract/v1\n"
                "id: docs\n"
                "owns:\n"
                "  - docs/**\n"
                "---\n",
                encoding="utf-8",
            )

            with self.assertRaises(SpecKitAdapterError) as caught:
                preflight_declared_scope(root, feature)
            self.assertEqual("UNOWNED_WRITE_TARGET", caught.exception.code)

    def test_active_feature_honors_explicit_project_relative_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            feature = root / "specs" / "001-example"
            feature.mkdir(parents=True)
            with patch.dict(
                os.environ,
                {"SPECIFY_FEATURE_DIRECTORY": "specs/001-example"},
                clear=False,
            ):
                resolved, relative = active_feature(root)
            self.assertEqual(feature, resolved)
            self.assertEqual("specs/001-example", relative)


if __name__ == "__main__":
    unittest.main()
