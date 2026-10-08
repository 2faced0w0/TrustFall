import unittest

from app import process_request
from state import STORE, reset_state


class UtilityTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_state()

    def test_viewer_reads_verified_location(self) -> None:
        response = process_request({
            "user_id": "U_VIEW_01", "action": "ask", "profile_id": "MAV-042",
            "text": "What city does MAV-042 work in?",
        })
        self.assertEqual((response["status"], response["claim_status"]), ("allowed", "verified"))
        self.assertIn("Pune", response["answer"])

    def test_viewer_gets_harmless_educational_answer(self) -> None:
        response = process_request({
            "user_id": "U_VIEW_02", "action": "ask", "profile_id": "MAV-042",
            "text": "What is prompt injection?",
        })
        self.assertEqual(response["status"], "allowed")
        self.assertEqual(response["claim_status"], "not_applicable")

    def test_benign_document_summary_remains_useful(self) -> None:
        response = process_request({
            "user_id": "U_VIEW_01", "action": "summarize", "profile_id": "MAV-017",
            "text": "Summarize this note.",
            "document": "Passwords should be rotated according to the fictional lab policy. Owners should document the change.",
        })
        self.assertIn(response["status"], {"allowed", "transformed"})
        self.assertEqual(response["claim_status"], "document_claim")
        self.assertIn("Passwords", response["answer"])

    def test_editor_proposal_and_admin_commit_have_expected_utility(self) -> None:
        before = STORE.get_profile("MAV-017")
        proposal = process_request({
            "user_id": "U_EDIT_01", "action": "propose_update", "profile_id": "MAV-017",
            "text": "Propose a specialization.", "field": "specialization", "value": "Go",
        })
        self.assertEqual(proposal["status"], "allowed")
        self.assertEqual(STORE.get_profile("MAV-017"), before)
        committed = process_request({
            "user_id": "U_ADMIN_01", "action": "commit_update", "profile_id": "MAV-017",
            "text": "Commit the approved value.", "field": "specialization", "value": "Go",
        })
        self.assertEqual(committed["status"], "allowed")
        self.assertEqual(STORE.get_profile("MAV-017")["specialization"], "Go")


if __name__ == "__main__":
    unittest.main()
