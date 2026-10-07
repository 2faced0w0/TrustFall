import unittest

from models.mock import MockAdapter


class MockModelTests(unittest.TestCase):
    def test_mock_is_deterministic(self) -> None:
        adapter = MockAdapter()
        messages = [{"role": "user", "content": "Explain readiness."}]
        first = adapter.generate(messages)
        second = adapter.generate(messages)
        self.assertEqual(first, second)
        self.assertEqual(first.provider, "mock")


if __name__ == "__main__":
    unittest.main()
