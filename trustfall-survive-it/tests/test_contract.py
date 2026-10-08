import unittest

from app import process_request
from state import reset_state


class ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_state()

    def test_response_has_exact_required_keys_and_types(self) -> None:
        response = process_request({
            "user_id": "U_VIEW_01", "action": "ask", "profile_id": "MAV-042",
            "text": "Where does MAV-042 work?",
        })
        self.assertEqual(set(response), {"status", "answer", "claim_status", "citations", "tool_calls"})
        self.assertIsInstance(response["status"], str)
        self.assertIsInstance(response["answer"], str)
        self.assertIsInstance(response["claim_status"], str)
        self.assertIsInstance(response["citations"], list)
        self.assertIsInstance(response["tool_calls"], list)

    def test_response_enums_are_legal(self) -> None:
        response = process_request({
            "user_id": "U_VIEW_01", "action": "ask", "profile_id": "MAV-042", "text": "Biography?",
        })
        self.assertIn(response["status"], {"allowed", "blocked", "transformed", "escalated"})
        self.assertIn(response["claim_status"], {"verified", "unverified", "unknown", "document_claim", "not_applicable"})

    def test_invalid_request_is_blocked_without_crashing(self) -> None:
        response = process_request({"action": "launch_rocket"})
        self.assertEqual(response["status"], "blocked")
        self.assertEqual(response["tool_calls"], [])


if __name__ == "__main__":
    unittest.main()
