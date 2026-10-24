"""Provider-neutral results and path classification for native verification."""

from dataclasses import dataclass

from boundary.operation.record import DirtyPathState, OperationRecord

@dataclass(frozen=True, slots=True)
class PostChangeDiagnostic:
    """One provider-neutral authorization-verification finding."""

    code: str
    message: str
    paths: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PostChangeResult:
    """Deterministic verification projection before epoch closure."""

    operation: OperationRecord
    actual_paths: tuple[str, ...] = ()
    checked_writes: tuple[str, ...] = ()
    dirty_path_states: tuple[DirtyPathState, ...] = ()
    diagnostics: tuple[PostChangeDiagnostic, ...] = ()

    @property
    def blocking(self) -> bool:
        """Return whether authorization verification found any violation."""

        return bool(self.diagnostics)
