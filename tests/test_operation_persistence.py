"""Focused tests for operation-evidence persistence readiness."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from boundary.authorization import (
    OPERATION_EVIDENCE_UNAVAILABLE,
    AuthorizationError,
    ChangeWriteSet,
    TaskWriteSet,
    authorize_implementation_operation,
    check_operation_evidence_persistence,
)
from boundary.outcomes import (
    MISSING_EXTERNAL_PREREQUISITE,
    classify_lifecycle_codes,
)
from boundary.verification import (
    VerificationError,
    finalize_operation_verification,
    verify_operation_authorization,
)


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout.strip()


class OperationPersistenceTests(unittest.TestCase):
    def initialize(self, root: Path) -> Path:
        run_git(root, "init", "-q")
        raw = Path(run_git(root, "rev-parse", "--git-dir"))
        if not raw.is_absolute():
            raw = root / raw
        return raw.resolve(strict=False)

    def test_probe_uses_git_metadata_and_cleans_up_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            git_dir = self.initialize(root)
            boundary_dir = git_dir / "boundary"

            result = check_operation_evidence_persistence(root)

            self.assertEqual(boundary_dir, result)
            self.assertFalse(boundary_dir.exists())

    def test_probe_does_not_modify_existing_current_operation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            git_dir = self.initialize(root)
            boundary_dir = git_dir / "boundary"
            boundary_dir.mkdir()
            current = boundary_dir / "current.json"
            current.write_text("sentinel\n", encoding="utf-8")

            check_operation_evidence_persistence(root)

            self.assertEqual(
                "sentinel\n",
                current.read_text(encoding="utf-8"),
            )
            self.assertEqual(
                ["current.json"],
                sorted(path.name for path in boundary_dir.iterdir()),
            )

    def test_probe_failure_has_stable_code_and_cleans_created_directory(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            git_dir = self.initialize(root)
            boundary_dir = git_dir / "boundary"

            with mock.patch(
                "boundary.authorization.storage.tempfile.mkstemp",
                side_effect=PermissionError("read-only metadata"),
            ):
                with self.assertRaises(AuthorizationError) as raised:
                    check_operation_evidence_persistence(root)

            self.assertEqual(
                OPERATION_EVIDENCE_UNAVAILABLE,
                raised.exception.code,
            )
            self.assertFalse(boundary_dir.exists())

    def test_authorization_checks_persistence_before_resolution_or_baseline(
        self,
    ) -> None:
        change = ChangeWriteSet(
            "001-example",
            (
                TaskWriteSet(
                    0,
                    "T001",
                    "US1",
                    ("src/app.py",),
                ),
            ),
        )
        error = AuthorizationError(
            "operation evidence is unavailable",
            code=OPERATION_EVIDENCE_UNAVAILABLE,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            with (
                mock.patch(
                    "boundary.authorization.service."
                    "check_operation_evidence_persistence",
                    side_effect=error,
                ),
                mock.patch(
                    "boundary.authorization.service.authorize_implementation"
                ) as resolve,
                mock.patch(
                    "boundary.authorization.service.capture_git_baseline"
                ) as baseline,
            ):
                with self.assertRaises(AuthorizationError) as raised:
                    authorize_implementation_operation(
                        root,
                        change,
                        selected_task_ids=("T001",),
                    )

        self.assertEqual(
            OPERATION_EVIDENCE_UNAVAILABLE,
            raised.exception.code,
        )
        resolve.assert_not_called()
        baseline.assert_not_called()

    def test_verification_checks_persistence_before_loading_operation(
        self,
    ) -> None:
        error = AuthorizationError(
            "operation evidence is unavailable",
            code=OPERATION_EVIDENCE_UNAVAILABLE,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            with (
                mock.patch(
                    "boundary.verification.service."
                    "check_operation_evidence_persistence",
                    side_effect=error,
                ),
                mock.patch(
                    "boundary.verification.service.read_current_operation"
                ) as read_current,
                mock.patch(
                    "boundary.verification.service.capture_git_delta"
                ) as delta,
            ):
                with self.assertRaises(VerificationError) as raised:
                    verify_operation_authorization(root)

        self.assertEqual(
            OPERATION_EVIDENCE_UNAVAILABLE,
            raised.exception.code,
        )
        read_current.assert_not_called()
        delta.assert_not_called()

    def test_verification_storage_failure_preserves_persistence_code(
        self,
    ) -> None:
        current = mock.Mock()
        current.status = "authorized"
        current.authorized_targets = ()
        verified = mock.Mock()
        current.mark_verified.return_value = verified

        result = mock.Mock()
        result.operation = current
        result.blocking = False
        result.dirty_path_states = ()

        error = AuthorizationError(
            "operation evidence cannot be stored",
            code=OPERATION_EVIDENCE_UNAVAILABLE,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            with (
                mock.patch(
                    "boundary.verification.service."
                    "verify_operation_authorization",
                    return_value=result,
                ),
                mock.patch(
                    "boundary.verification.service.write_current_operation",
                    side_effect=error,
                ),
            ):
                with self.assertRaises(VerificationError) as raised:
                    finalize_operation_verification(root)

        self.assertEqual(
            OPERATION_EVIDENCE_UNAVAILABLE,
            raised.exception.code,
        )
        current.mark_verified.assert_called_once_with(())

    def test_persistence_failure_is_missing_external_prerequisite(self) -> None:
        classification = classify_lifecycle_codes(
            (OPERATION_EVIDENCE_UNAVAILABLE,),
            stage="verify",
        )

        self.assertEqual(
            MISSING_EXTERNAL_PREREQUISITE,
            classification.category,
        )


if __name__ == "__main__":
    unittest.main()
