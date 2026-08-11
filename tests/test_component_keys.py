import unittest

from component_keys import safe_component_key


class ComponentKeyTests(unittest.TestCase):
    def test_problematic_filename_cannot_leak_reserved_delimiter(self):
        key = safe_component_key(
            "mastering_live_monitor_v10",
            "YouTube__master [FINAL] 🎵.mp3",
            123456,
        )
        self.assertNotIn("__", key)
        self.assertNotIn("YouTube", key)

    def test_key_is_deterministic_and_identity_sensitive(self):
        first = safe_component_key("monitor", "master.wav", 100)
        self.assertEqual(first, safe_component_key("monitor", "master.wav", 100))
        self.assertNotEqual(first, safe_component_key("monitor", "master.wav", 101))

    def test_prefix_is_sanitized(self):
        key = safe_component_key("unsafe__prefix /", "audio")
        self.assertNotIn("__", key)
        self.assertRegex(key, r"^[a-zA-Z0-9-]+$")
