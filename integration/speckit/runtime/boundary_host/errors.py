"""Errors raised by the concrete installed Spec Kit integration."""


class SpecKitAdapterError(ValueError):
    """Raised when Spec Kit state cannot form one normalized change projection."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "INVALID_ADAPTER_STATE",
    ) -> None:
        self.code = code
        super().__init__(message)


class IntegrationError(RuntimeError):
    """Raised when Boundary-owned host integration cannot be maintained."""
