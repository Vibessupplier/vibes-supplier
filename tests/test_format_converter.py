from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from format_converter import (
    FormatConverterError,
    convert_audio,
    inspect_source,
    matched_bitrate,
    resolve_conversion_settings,
)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class FormatConverterTests(unittest.TestCase):
    def make_source(self, path: Path, sample_rate: int = 48000):
        subprocess.run([
            shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration=0.2:sample_rate={sample_rate}",
            "-ac", "2", "-c:a", "pcm_s24le", str(path),
        ], check=True)

    def test_wav_settings_preserve_source_rate_and_requested_depth(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.wav"
            self.make_source(source)
            settings = resolve_conversion_settings("WAV", inspect_source(source), wav_bit_depth=16)
            self.assertEqual(settings.sample_rate, 48000)
            self.assertEqual(settings.codec, "pcm_s16le")

    def test_converts_to_all_supported_formats(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.wav"
            self.make_source(source)
            source_info = inspect_source(source)
            expected_codecs = {
                "MP3": "mp3",
                "WAV": "pcm_s24le",
                "FLAC": "flac",
                "M4A / AAC": "aac",
                "ALAC": "alac",
            }
            for format_name, expected_codec in expected_codecs.items():
                settings = resolve_conversion_settings(format_name, source_info, bitrate_kbps=192)
                output = root / f"output{settings.extension}"
                convert_audio(source, output, settings)
                output_info = inspect_source(output)
                self.assertEqual(output_info.channels, 2)
                self.assertEqual(output_info.sample_rate, 48000)
                self.assertEqual(output_info.codec_name, expected_codec)
                self.assertGreater(output.stat().st_size, 0)

    def test_resamples_when_requested(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "source.wav", root / "output.flac"
            self.make_source(source, sample_rate=48000)
            settings = resolve_conversion_settings("FLAC", inspect_source(source), sample_rate=44100)
            convert_audio(source, output, settings)
            self.assertEqual(inspect_source(output).sample_rate, 44100)

    def test_match_bitrate_chooses_nearest_supported_value(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.mp3"
            subprocess.run([
                shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=0.2", "-b:a", "128k", str(source),
            ], check=True)
            self.assertEqual(matched_bitrate(inspect_source(source)), 128)

    def test_rejects_invalid_format_and_quality(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.wav"
            self.make_source(source)
            info = inspect_source(source)
            with self.assertRaises(FormatConverterError):
                resolve_conversion_settings("WMA", info)
            with self.assertRaises(FormatConverterError):
                resolve_conversion_settings("MP3", info, bitrate_kbps=160)
