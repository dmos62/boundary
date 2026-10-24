"""Provider-neutral actual-write verification boundary."""

from .errors import PostChangeError
from .model import (
    PostChangeDiagnostic,
    PostChangeResult,
)
from .service import (
    close_verified_operation,
    check_operation_writes,
    abandon_operation,
)

__all__ = [
    "PostChangeDiagnostic",
    "PostChangeError",
    "PostChangeResult",
    "close_verified_operation",
    "check_operation_writes",
    "abandon_operation",
]
