import unittest

from mastering_monitor_component import MONITOR_CSS, MONITOR_HTML, MONITOR_JS


class MasteringMonitorComponentTests(unittest.TestCase):
    def test_vu_scale_uses_individually_positioned_labels(self):
        self.assertEqual(MONITOR_HTML.count('class="vu-scale"'), 2)
        self.assertNotIn('content:"−30', MONITOR_CSS)
        self.assertIn(".vu-scale i:nth-child(6)", MONITOR_CSS)

    def test_enhanced_live_stereo_instruments_are_present(self):
        self.assertIn('class="vectorscope"', MONITOR_HTML)
        self.assertIn('data-channel="left"', MONITOR_HTML)
        self.assertIn('data-channel="right"', MONITOR_HTML)
        self.assertIn('class="phase-status"', MONITOR_HTML)
        self.assertIn("PHASE CANCELLATION RISK", MONITOR_JS)

    def test_resize_observer_guards_its_target(self):
        self.assertIn("target instanceof Element", MONITOR_JS)

    def test_monitor_level_is_listening_only(self):
        self.assertIn("LISTENING ONLY · METERS UNAFFECTED", MONITOR_HTML)
        self.assertIn("normal.connect(output)", MONITOR_JS)
        self.assertIn("mono.connect(output)", MONITOR_JS)
        self.assertIn("output.connect(ctx.destination)", MONITOR_JS)
        self.assertNotIn("source.connect(output)", MONITOR_JS)


if __name__ == "__main__":
    unittest.main()
