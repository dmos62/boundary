import tempfile
import unittest
from pathlib import Path

from native_contract_cli_test_support import (
    PAYMENTS,
    USERS,
    run_cli,
    write_file,
)


class NativeContractCliTests(unittest.TestCase):
    def test_contracts_check_reports_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_file(root, "contracts/payments.contract.md", PAYMENTS)
            write_file(root, "contracts/users.contract.md", USERS)

            code, output, errors = run_cli(
                root,
                "contracts",
                "check",
            )

            self.assertEqual(0, code)
            self.assertEqual(
                "contracts: ok (2 contracts)\n",
                output,
            )
            self.assertEqual("", errors)

    def test_contracts_check_reports_source_for_parse_diagnostics(self):
        source = """---
schema: boundary.contract/v1
id: broken
owns:
  - **
---
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_file(
                root,
                "contracts/broken.contract.md",
                source,
            )

            code, output, errors = run_cli(
                root,
                "contracts",
                "check",
            )

            self.assertEqual(2, code)
            self.assertEqual("", output)
            self.assertEqual(
                "boundary: error: contracts/broken.contract.md: "
                "repository-wide '**' scope is not supported\n",
                errors,
            )

    def test_contracts_check_reports_ambiguous_ownership_sources(self):
        alpha = PAYMENTS.replace(
            "id: payments",
            "id: alpha",
        ).replace(
            "src/payments/**",
            "src/shared/**",
        ).replace(
            "  - users\n",
            "",
        ).replace(
            "applies_to:\n  - src/api/payment-methods/**\n",
            "",
        )
        beta = alpha.replace(
            "id: alpha",
            "id: beta",
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_file(
                root,
                "contracts/a.contract.md",
                alpha,
            )
            write_file(
                root,
                "contracts/b.contract.md",
                beta,
            )

            code, output, errors = run_cli(
                root,
                "contracts",
                "check",
            )

            self.assertEqual(2, code)
            self.assertEqual("", output)
            self.assertIn(
                "contracts/a.contract.md",
                errors,
            )
            self.assertIn(
                "contracts/b.contract.md",
                errors,
            )
            self.assertIn(
                "ambiguous ownership",
                errors,
            )


if __name__ == "__main__":
    unittest.main()
