import unittest
from unittest.mock import patch

from feedback import FeedbackError, submit_feedback, validate_feedback


class FeedbackTest(unittest.TestCase):
    def test_validates_and_trims_feedback(self):
        result = validate_feedback("Bug report", 4, "  The player stopped working.  ")

        self.assertEqual(result.message, "The player stopped working.")
        self.assertEqual(result.rating, 4)

    def test_rejects_short_feedback(self):
        with self.assertRaisesRegex(FeedbackError, "at least"):
            validate_feedback("General feedback", 5, "Too short")

    @patch("feedback.send_event_now", return_value=True)
    def test_submits_only_validated_properties(self, send_mock):
        delivered = submit_feedback(
            "Feature request",
            5,
            "Please add keyboard shortcuts.",
        )

        self.assertTrue(delivered)
        send_mock.assert_called_once_with(
            "feedback_submitted",
            {
                "category": "Feature request",
                "rating": 5,
                "message": "Please add keyboard shortcuts.",
            },
        )


if __name__ == "__main__":
    unittest.main()
