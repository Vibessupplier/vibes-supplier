import unittest

from timing_calculator import delay_timings, quarter_note_ms, reverb_timings, validate_bpm


class TimingCalculatorTests(unittest.TestCase):
    def test_quarter_note_at_120_bpm(self):
        self.assertEqual(quarter_note_ms(120), 500)

    def test_delay_variants_at_120_bpm(self):
        eighth = next(item for item in delay_timings(120) if item.label == "1/8")
        self.assertEqual(eighth.straight_ms, 250)
        self.assertEqual(eighth.dotted_ms, 375)
        self.assertAlmostEqual(eighth.triplet_ms, 166.6667, places=3)

    def test_reverb_scales_with_tempo(self):
        fast = reverb_timings(120)[2]
        slow = reverb_timings(60)[2]
        self.assertEqual(slow.predelay_ms, fast.predelay_ms * 2)
        self.assertEqual(slow.decay_seconds, fast.decay_seconds * 2)

    def test_rejects_out_of_range_and_non_finite_bpm(self):
        for value in (0, 301, float("nan")):
            with self.assertRaises(ValueError):
                validate_bpm(value)
