import unittest

from waveform_component import WAVEFORM_HTML, WAVEFORM_JS


class WaveformComponentTests(unittest.TestCase):
    def test_use_selection_commits_an_add_action(self):
        self.assertIn("commit_id: commitId", WAVEFORM_JS)
        self.assertIn("✓ ADDING TO TRAY", WAVEFORM_JS)
        self.assertIn("data.tray_full", WAVEFORM_JS)

    def test_monitor_level_is_listening_only(self):
        self.assertIn("LISTENING ONLY · EXPORT UNAFFECTED", WAVEFORM_HTML)
        self.assertIn("audio.volume = clamp(monitorGain() * fadeFactor", WAVEFORM_JS)
        self.assertIn("audio.muted = monitorState.muted", WAVEFORM_JS)

    def test_dragging_near_view_edges_auto_pans(self):
        self.assertIn("function autoPanVelocity()", WAVEFORM_JS)
        self.assertIn("requestAnimationFrame(runAutoPan)", WAVEFORM_JS)
        self.assertIn("dragMode === 'move' ? span * 0.48", WAVEFORM_JS)
        self.assertIn("dragMode = null; stopAutoPan()", WAVEFORM_JS)

    def test_edge_fade_is_auditioned_and_committed(self):
        self.assertIn("EDGE FADE / DE-CLICK", WAVEFORM_HTML)
        self.assertIn("fade_ms: monitorState.fadeMs", WAVEFORM_JS)
        self.assertIn("function applyAuditionGain()", WAVEFORM_JS)
        self.assertIn("fadeFactor = Math.min(fadeIn, fadeOut)", WAVEFORM_JS)
        self.assertIn("(end - start) / 4", WAVEFORM_JS)

    def test_use_selection_rearms_after_server_rerun(self):
        self.assertIn("applyButton.classList.remove('selection-applied')", WAVEFORM_JS)
        self.assertIn(":'USE SELECTION'", WAVEFORM_JS)


if __name__ == "__main__":
    unittest.main()
