"""Product-level audio format conversion and quality policy."""

from dataclasses import dataclass
from pathlib import Path

from audio_engine import (
    AudioProcessingError,
    AudioStreamInfo,
    encode_audio_file,
    probe_audio_stream,
)


OUTPUT_FORMATS = ("MP3", "WAV", "FLAC", "M4A / AAC", "ALAC")
LOSSY_FORMATS = {"MP3", "M4A / AAC"}
BITRATES = (128, 192, 256, 320)
SAMPLE_RATES = (44100, 48000, 88200, 96000)
WAV_DEPTHS = (16, 24, 32)


class FormatConverterError(RuntimeError):
    """Raised when an audio conversion request is invalid or fails."""


@dataclass(frozen=True)
class ConversionSettings:
    format_name: str
    extension: str
    mime_type: str
    codec: str
    bitrate_kbps: int | None
    sample_rate: int | None
    bit_depth: int | None


def inspect_source(input_path: Path) -> AudioStreamInfo:
    try:
        return probe_audio_stream(input_path)
    except AudioProcessingError as error:
        raise FormatConverterError(str(error)) from error


def matched_bitrate(info: AudioStreamInfo) -> int:
    if not info.bit_rate:
        return 192
    source_kbps = info.bit_rate / 1000
    return min(BITRATES, key=lambda option: abs(option - source_kbps))


def resolve_conversion_settings(
    format_name: str,
    source_info: AudioStreamInfo,
    *,
    bitrate_kbps: int | None = None,
    sample_rate: int | None = None,
    wav_bit_depth: int | None = None,
) -> ConversionSettings:
    output_format = str(format_name).upper()
    if output_format not in OUTPUT_FORMATS:
        raise FormatConverterError(
            "Output format must be MP3, WAV, FLAC, M4A / AAC, or ALAC."
        )
    resolved_rate = source_info.sample_rate if sample_rate is None else int(sample_rate)
    if sample_rate is not None and resolved_rate not in SAMPLE_RATES:
        raise FormatConverterError("Unsupported output sample rate.")
    if not 8000 <= resolved_rate <= 192000:
        raise FormatConverterError("Source sample rate is outside the supported range.")
    if output_format in LOSSY_FORMATS:
        bitrate = matched_bitrate(source_info) if bitrate_kbps is None else int(bitrate_kbps)
        if bitrate not in BITRATES:
            raise FormatConverterError("Unsupported lossy output bitrate.")
        if output_format == "MP3":
            return ConversionSettings("MP3", ".mp3", "audio/mpeg", "libmp3lame", bitrate, resolved_rate, None)
        return ConversionSettings("M4A / AAC", ".m4a", "audio/mp4", "aac", bitrate, resolved_rate, None)
    if output_format == "WAV":
        depth = wav_bit_depth or source_info.bits_per_sample or 24
        if depth not in WAV_DEPTHS:
            raise FormatConverterError("WAV depth must be 16, 24, or 32-bit PCM.")
        codec = {16: "pcm_s16le", 24: "pcm_s24le", 32: "pcm_s32le"}[depth]
        return ConversionSettings("WAV", ".wav", "audio/wav", codec, None, resolved_rate, depth)
    if output_format == "FLAC":
        return ConversionSettings("FLAC", ".flac", "audio/flac", "flac", None, resolved_rate, source_info.bits_per_sample)
    return ConversionSettings("ALAC", ".m4a", "audio/mp4", "alac", None, resolved_rate, source_info.bits_per_sample)


def convert_audio(
    input_path: Path,
    output_path: Path,
    settings: ConversionSettings,
) -> Path:
    try:
        return encode_audio_file(
            input_path,
            output_path,
            settings.codec,
            bitrate_kbps=settings.bitrate_kbps,
            sample_rate=settings.sample_rate,
        )
    except AudioProcessingError as error:
        raise FormatConverterError(str(error)) from error
