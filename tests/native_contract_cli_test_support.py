"""Shared fixtures for native contract CLI tests."""

from hashlib import sha256
from io import StringIO
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from boundary.cli import main


PAYMENTS = """---
schema: boundary.contract/v1
id: payments
owns:
  - src/payments/**
applies_to:
  - src/api/payment-methods/**
depends_on:
  - users
---

# Payments

## Purpose

Process payments.

## Invariants

- Never persist card data.

## Prohibitions

- Keep providers isolated.
"""

STRIPE = """---
schema: boundary.contract/v1
id: stripe
owns:
  - src/payments/providers/stripe/**
---

# Stripe

## Invariants

- Use Stripe adapters.
"""

USERS = """---
schema: boundary.contract/v1
id: users
owns:
  - src/users/**
---

# Users

## Interfaces

- Use UserIdentity.
"""


def run_cli(
    root: Path,
    *arguments: str,
) -> tuple[int, str, str]:
    output = StringIO()
    errors = StringIO()
    code = main(
        arguments,
        repository_root=root,
        stdout=output,
        stderr=errors,
    )
    return code, output.getvalue(), errors.getvalue()


def write_file(
    root: Path,
    path: str,
    source: str,
) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        source,
        encoding="utf-8",
    )


def file_paths(root: Path) -> tuple[str, ...]:
    return tuple(
        sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        )
    )


def expected_inspection() -> str:
    payments = identity(PAYMENTS)
    stripe = identity(STRIPE)
    users = identity(USERS)
    return f"""target: src/payments/providers/stripe/client.py
owner: stripe
applicable: payments, stripe
sources:
  payments: contracts/payments.contract.md @ {payments}
  stripe: contracts/stripe.contract.md @ {stripe}
  users: contracts/users.contract.md @ {users}
purpose:
  - payments: Process payments.
invariants:
  - payments: Never persist card data.
  - stripe: Use Stripe adapters.
prohibitions:
  - payments: Keep providers isolated.
dependency-interfaces:
  - users: Use UserIdentity.

target: src/api/payment-methods/card.py
owner: -
applicable: payments
sources:
  payments: contracts/payments.contract.md @ {payments}
  users: contracts/users.contract.md @ {users}
purpose:
  - payments: Process payments.
invariants:
  - payments: Never persist card data.
prohibitions:
  - payments: Keep providers isolated.
dependency-interfaces:
  - users: Use UserIdentity.
"""


def identity(source: str) -> str:
    digest = sha256(source.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"
