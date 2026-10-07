import sys
import unittest


class RuntimeTests(unittest.TestCase):
    def test_supported_python_version(self) -> None:
        self.assertIn(
            sys.version_info[:2],
            {(3, 11), (3, 12)},
            "Python 3.11 or 3.12 is required; "
            f"found {sys.version_info.major}.{sys.version_info.minor}",
        )


if __name__ == "__main__":
    unittest.main()
