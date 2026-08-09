import unittest
from unittest.mock import MagicMock, patch

import analytics


class AnalyticsTest(unittest.TestCase):
    @patch("analytics._post_event", return_value=True)
    @patch("analytics._distinct_id", return_value="browser_test")
    @patch(
        "analytics._configuration",
        return_value=("phc_test", "https://eu.i.posthog.com"),
    )
    def test_sends_confirmed_event_immediately(
        self,
        configuration_mock,
        distinct_id_mock,
        post_event_mock,
    ):
        delivered = analytics.send_event_now(
            "feedback_submitted",
            {"rating": 5},
        )

        self.assertTrue(delivered)
        url, payload = post_event_mock.call_args.args
        self.assertEqual(url, "https://eu.i.posthog.com/capture/")
        self.assertEqual(payload["event"], "feedback_submitted")
        self.assertEqual(payload["properties"]["rating"], 5)
        self.assertTrue(payload["properties"]["$geoip_disable"])

    @patch("analytics.threading.Thread")
    @patch("analytics._distinct_id", return_value="browser_test")
    @patch(
        "analytics._configuration",
        return_value=("phc_test", "https://eu.i.posthog.com"),
    )
    def test_tracks_privacy_safe_event(
        self,
        configuration_mock,
        distinct_id_mock,
        thread_mock,
    ):
        thread = MagicMock()
        thread_mock.return_value = thread

        analytics.track_event("audio_analysis_completed", {"tool": "mastering"})

        _, keyword_arguments = thread_mock.call_args
        url, payload = keyword_arguments["args"]
        self.assertEqual(url, "https://eu.i.posthog.com/capture/")
        self.assertEqual(payload["api_key"], "phc_test")
        self.assertEqual(payload["event"], "audio_analysis_completed")
        self.assertEqual(payload["properties"]["distinct_id"], "browser_test")
        self.assertTrue(payload["properties"]["$geoip_disable"])
        self.assertNotIn("filename", payload["properties"])
        thread.start.assert_called_once_with()

    @patch("analytics.threading.Thread")
    @patch("analytics._configuration", return_value=None)
    def test_does_nothing_when_disabled(self, configuration_mock, thread_mock):
        analytics.track_event("$pageview", {"page": "home"})

        thread_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
