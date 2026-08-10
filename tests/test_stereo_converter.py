from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from stereo_converter import (
    StereoConverterError,
    inspect_audio,
    merge_mono,
    resolve_output_settings,
    split_stereo,
)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class StereoConverterTests(unittest.TestCase):
    def make_tone(self, path: Path, frequency: int, channels: int = 1, duration: float = 0.25):
        subprocess.run([
            shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"sine=frequency={frequency}:duration={duration}:sample_rate=48000",
            "-ac", str(channels), str(path),
        ], check=True)

    def test_split_and_merge_preserve_channel_structure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            left_source, right_source = root / "left.wav", root / "right.wav"
            stereo, left, right, rebuilt = root / "stereo.wav", root / "L.wav", root / "R.wav", root / "rebuilt.wav"
            self.make_tone(left_source, 440)
            self.make_tone(right_source, 880)
            settings = resolve_output_settings("WAV", None)
            merge_mono(left_source, right_source, stereo, settings)
            split_stereo(stereo, left, right, settings)
            merge_mono(left, right, rebuilt, settings)
            self.assertEqual(inspect_audio(left).channels, 1)
            self.assertEqual(inspect_audio(right).channels, 1)
            self.assertEqual(inspect_audio(rebuilt).channels, 2)
            self.assertEqual(inspect_audio(rebuilt).sample_rate, 48000)

    def test_merge_pads_to_longer_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            left, right, output = root / "left.wav", root / "right.wav", root / "out.wav"
            self.make_tone(left, 440, duration=0.2)
            self.make_tone(right, 880, duration=0.4)
            merge_mono(left, right, output, resolve_output_settings("WAV", None))
            self.assertAlmostEqual(inspect_audio(output).duration_seconds, 0.4, places=2)

    def test_mp3_bitrate_selection(self):
        settings = resolve_output_settings("MP3", 320)
        self.assertEqual(settings.codec, "libmp3lame")
        self.assertEqual(settings.bitrate_kbps, 320)

    def test_rejects_invalid_mp3_bitrate(self):
        with self.assertRaises(StereoConverterError):
            resolve_output_settings("MP3", 160)
