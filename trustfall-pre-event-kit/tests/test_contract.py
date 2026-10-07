import unittest

from smoke.smoke_app import process_request


class ContractTests(unittest.TestCase):
    def test_required_response_shape(self) -> None:
        response = process_request({"text": "readiness"})
        self.assertEqual(
            set(response), {"status", "answer", "claim_status", "citations", "tool_calls"}
        )
        self.assertIsInstance(response["status"], str)
        self.assertIsInstance(response["answer"], str)
        self.assertIsInstance(response["claim_status"], str)
        self.assertIsInstance(response["citations"], list)
        self.assertIsInstance(response["tool_calls"], list)


if __name__ == "__main__":
    unittest.main()
