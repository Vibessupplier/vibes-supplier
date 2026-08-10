import unittest

from mastering_ab_component import AB_CSS, AB_HTML, AB_JS


class MasteringAbComponentTests(unittest.TestCase):
    def test_player_has_synchronized_ab_controls(self):
        self.assertIn("PLAY BOTH", AB_HTML)
        self.assertIn('data-source="a"', AB_HTML)
        self.assertIn('data-source="b"', AB_HTML)
        self.assertIn("ONLY ONE SOURCE IS AUDIBLE", AB_HTML)
        self.assertIn("Promise.all([a.play(),b.play()])", AB_JS)

    def test_global_lufs_and_rms_are_present(self):
        self.assertIn("INTEGRATED LUFS", AB_HTML)
        self.assertIn("FULL-TRACK / FFmpeg", AB_HTML)
        self.assertIn("GLOBAL BAR / LIVE MARKER", AB_HTML)
        self.assertIn("a-rms-live", AB_HTML)
        self.assertIn(".meter-track em", AB_CSS)

    def test_only_selected_source_reaches_output(self):
        self.assertIn("analyserA.connect(gainA)", AB_JS)
        self.assertIn("analyserB.connect(gainB)", AB_JS)
        self.assertIn("aValue=source==='a'?1:0", AB_JS)
        self.assertIn("bValue=source==='b'?1:0", AB_JS)

    def test_monitor_level_is_after_ab_selection(self):
        self.assertIn("LISTENING ONLY · METERS UNAFFECTED", AB_HTML)
        self.assertIn("gainA.connect(output)", AB_JS)
        self.assertIn("gainB.connect(output)", AB_JS)
        self.assertIn("output.connect(ctx.destination)", AB_JS)
        self.assertNotIn("sourceA.connect(output)", AB_JS)


if __name__ == "__main__":
    unittest.main()
