"""Product-level stereo/mono routing and export rules."""

from dataclasses import dataclass
from pathlib import Path

from audio_engine import (
    AudioProcessingError,
    AudioStreamInfo,
    merge_mono_channels,
    probe_audio_stream,
    split_stereo_channels,
)


SUPPORTED_MP3_BITRATES = (128, 192, 256, 320)


class StereoConverterError(RuntimeError):
    """Raised when stereo/mono routing cannot be completed safely."""


@dataclass(frozen=True)
class OutputSettings:
    format_name: str
    extension: str
    mime_type: str
    codec: str
    bitrate_kbps: int | None


def source_bitrate_kbps(info: AudioStreamInfo) -> int | None:
    if info.bit_rate is None:
        return None
    value = int(round(info.bit_rate / 1000))
    return min(SUPPORTED_MP3_BITRATES, key=lambda option: abs(option - value))


def resolve_output_settings(
    format_name: str,
    requested_bitrate_kbps: int | None,
    source_info: AudioStreamInfo | None = None,
) -> OutputSettings:
    normalized_format = str(format_name).upper()
    if normalized_format == "MP3":
        bitrate = requested_bitrate_kbps
        if bitrate is None and source_info is not None:
            bitrate = source_bitrate_kbps(source_info)
        if bitrate is None:
            bitrate = 192
        if bitrate not in SUPPORTED_MP3_BITRATES:
            raise StereoConverterError("Unsupported MP3 bitrate.")
        return OutputSettings("MP3", ".mp3", "audio/mpeg", "libmp3lame", bitrate)
    if normalized_format == "WAV":
        depth = source_info.bits_per_sample if source_info is not None else None
        codec = {16: "pcm_s16le", 24: "pcm_s24le", 32: "pcm_s32le"}.get(depth, "pcm_s24le")
        return OutputSettings("WAV", ".wav", "audio/wav", codec, None)
    raise StereoConverterError("Output format must be WAV or MP3.")


def inspect_audio(input_path: Path) -> AudioStreamInfo:
    try:
        return probe_audio_stream(input_path)
    except AudioProcessingError as error:
        raise StereoConverterError(str(error)) from error


def split_stereo(
    input_path: Path,
    left_output_path: Path,
    right_output_path: Path,
    settings: OutputSettings,
) -> tuple[Path, Path]:
    info = inspect_audio(input_path)
    if info.channels != 2:
        raise StereoConverterError("Stereo → L + R requires exactly two channels.")
    try:
        return split_stereo_channels(
            input_path, left_output_path, right_output_path,
            settings.codec, settings.bitrate_kbps,
        )
    except AudioProcessingError as error:
        raise StereoConverterError(str(error)) from error


def merge_mono(
    left_input_path: Path,
    right_input_path: Path,
    output_path: Path,
    settings: OutputSettings,
) -> Path:
    left_info = inspect_audio(left_input_path)
    right_info = inspect_audio(right_input_path)
    if left_info.channels != 1 or right_info.channels != 1:
        raise StereoConverterError("L + R → Stereo requires two mono files.")
    try:
        return merge_mono_channels(
            left_input_path, right_input_path, output_path, settings.codec,
            max(left_info.duration_seconds, right_info.duration_seconds),
            settings.bitrate_kbps,
        )
    except AudioProcessingError as error:
        raise StereoConverterError(str(error)) from error
