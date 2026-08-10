import unittest

from speed_player_component import (
    SPEED_PLAYER_HTML,
    SPEED_PLAYER_JS,
    initial_speed_deck_settings,
)


class SpeedPlayerComponentTests(unittest.TestCase):
    def test_initial_settings_preserve_detected_speed(self):
        settings = initial_speed_deck_settings(127.84)

        self.assertEqual(settings["source_bpm"], 127.8)
        self.assertEqual(settings["target_bpm"], 127.8)
        self.assertEqual(settings["pitch_mode"], "Follow speed")
        self.assertEqual(settings["pitch_semitones"], 0.0)

    def test_correcting_source_bpm_resets_target_to_same_speed(self):
        self.assertIn("state.targetBpm=state.sourceBpm", SPEED_PLAYER_JS)

    def test_monitor_level_changes_listening_only(self):
        self.assertIn("LISTENING ONLY · EXPORT UNAFFECTED", SPEED_PLAYER_HTML)
        self.assertIn("audio.volume = monitorGain()", SPEED_PLAYER_JS)
        self.assertIn("audio.muted = state.muted", SPEED_PLAYER_JS)
        self.assertIn(
            "return {source_bpm:state.sourceBpm,target_bpm:state.targetBpm,"
            "pitch_mode:state.mode,pitch_semitones:state.pitch}",
            SPEED_PLAYER_JS,
        )


if __name__ == "__main__":
    unittest.main()
