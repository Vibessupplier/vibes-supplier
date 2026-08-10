import unittest

from sample_tray_component import TRAY_CSS, TRAY_HTML, TRAY_JS


class SampleTrayComponentTests(unittest.TestCase):
    def test_lcd_memory_has_four_compact_slots(self):
        self.assertIn("VS SAMPLE MEMORY / 4 SLOT", TRAY_HTML)
        self.assertIn("for(let index=0;index<4;index++)", TRAY_JS)
        self.assertIn("— EMPTY —", TRAY_JS)
        self.assertIn(".lcd-glass", TRAY_CSS)

    def test_tray_uses_one_browser_audio_player(self):
        self.assertEqual(TRAY_HTML.count("<audio"), 1)
        self.assertIn("state.activeId", TRAY_JS)
        self.assertIn("audio.ontimeupdate", TRAY_JS)

    def test_tray_emits_rename_and_remove_actions(self):
        self.assertIn("type:'remove'", TRAY_JS)
        self.assertIn("type:'rename'", TRAY_JS)
        self.assertIn("setTriggerValue('action'", TRAY_JS)


if __name__ == "__main__":
    unittest.main()
