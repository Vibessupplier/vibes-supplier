import unittest

from speed_player_component import (
    SPEED_PLAYER_HTML,
    SPEED_PLAYER_JS,
    initial_speed_deck_settings,
)


class SpeedPlayerComponentTests(unittest.TestCase):
    def test_initial_settings_preserve_detected_speed(self):
        settings = initial_speed_deck_settings(127.84)

        self.assertEqual(settings["detected_bpm"], 127.8)
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
            "return {source_bpm:state.sourceBpm,detected_bpm:state.detectedBpm,"
            "target_bpm:state.targetBpm,"
            "pitch_mode:state.mode,pitch_semitones:state.pitch}",
            SPEED_PLAYER_JS,
        )

    def test_original_bpm_starts_locked_and_can_be_unlocked(self):
        self.assertIn("▣ LOCKED", SPEED_PLAYER_HTML)
        self.assertIn("sourceLocked: true", SPEED_PLAYER_JS)
        self.assertIn("sourceInput.disabled = state.sourceLocked", SPEED_PLAYER_JS)

    def test_reset_restores_detected_bpm_and_neutral_speed(self):
        self.assertIn("RESET TO DETECTED BPM", SPEED_PLAYER_HTML)
        self.assertIn("state.sourceBpm=state.detectedBpm", SPEED_PLAYER_JS)
        self.assertIn("state.targetBpm=state.detectedBpm", SPEED_PLAYER_JS)
        self.assertIn("setTriggerValue('reset',payload())", SPEED_PLAYER_JS)


if __name__ == "__main__":
    unittest.main()
