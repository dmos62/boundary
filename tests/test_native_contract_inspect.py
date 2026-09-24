import tempfile
import unittest
from pathlib import Path

from native_contract_cli_test_support import (
    PAYMENTS,
    STRIPE,
    USERS,
    expected_inspection,
    file_paths,
    run_cli,
    write_file,
)


class NativeContractInspectTests(unittest.TestCase):
    def test_inspect_is_stable_multi_target_and_transient(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_file(
                root,
                "contracts/payments.contract.md",
                PAYMENTS,
            )
            write_file(
                root,
                "contracts/stripe.contract.md",
                STRIPE,
            )
            write_file(
                root,
                "contracts/users.contract.md",
                USERS,
            )
            before = file_paths(root)

            arguments = (
                "inspect",
                "src/payments/providers/stripe/client.py",
                "src/api/payment-methods/card.py",
            )
            first = run_cli(root, *arguments)
            second = run_cli(root, *arguments)

            self.assertEqual(first, second)
            self.assertEqual(0, first[0])
            self.assertEqual("", first[2])
            self.assertEqual(before, file_paths(root))
            self.assertFalse((root / "src").exists())
            self.assertEqual(
                expected_inspection(),
                first[1],
            )


if __name__ == "__main__":
    unittest.main()
