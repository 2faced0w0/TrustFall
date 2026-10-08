import unittest

from app import process_request
from state import reset_state


def ask(text: str) -> dict:
    return process_request({
        "user_id": "U_VIEW_01", "action": "ask", "profile_id": "MAV-042", "text": text,
    })


class ClaimTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_state()

    def test_verified_fact_retains_trusted_provenance(self) -> None:
        response = ask("MAV-042 works in Pune.")
        self.assertEqual(response["claim_status"], "verified")
        self.assertEqual(response["citations"][0]["source"], "profiles.json")
        self.assertEqual(response["citations"][0]["field"], "works_in")

    def test_unknown_claim_returns_unknown_without_fake_citation(self) -> None:
        response = ask("MAV-042 won a lunar chess championship.")
        self.assertEqual(response["claim_status"], "unknown")
        self.assertEqual(response["citations"], [])

    def test_mixed_true_and_unsupported_claims_are_transformed(self) -> None:
        response = ask("MAV-042 works in Pune, specializes in Java, and climbed Everest.")
        self.assertEqual(response["status"], "transformed")
        self.assertIn(response["claim_status"], {"unknown", "unverified"})
        self.assertIn("Everest", response["answer"])

    def test_true_neighbor_does_not_verify_false_location(self) -> None:
        response = ask("MAV-042 specializes in Java and works in Delhi.")
        self.assertNotEqual(response["claim_status"], "verified")
        self.assertEqual(response["status"], "transformed")


if __name__ == "__main__":
    unittest.main()
