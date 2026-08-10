"""Reusable FFmpeg-based audio transformation engine."""

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
from typing import Iterable, Optional


class AudioProcessingError(RuntimeError):
    """Raised when an audio transformation cannot be completed."""


@dataclass(frozen=True)
class AudioStreamInfo:
    """Basic properties of the first audio stream reported by FFprobe."""

    codec_name: str
    channels: int
    sample_rate: int
    bit_rate: int | None
    bits_per_sample: int | None
    duration_seconds: float


def _ffmpeg_executable() -> str:
    executable = shutil.which("ffmpeg")

    if executable is None:
        raise AudioProcessingError(
            "FFmpeg is not installed or is not available on PATH."
        )

    return executable


def _ffprobe_executable() -> str:
    executable = shutil.which("ffprobe")

    if executable is None:
        raise AudioProcessingError(
            "FFprobe is not installed or is not available on PATH."
        )

    return executable


def probe_audio_duration(input_path: Path) -> float:
    """Return an audio file's duration in seconds using FFprobe."""
    input_path = Path(input_path)
    if not input_path.is_file():
        raise AudioProcessingError(f"Input audio does not exist: {input_path}")

    command = [
        _ffprobe_executable(),
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(input_path),
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        duration = float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError) as error:
        details = getattr(error, "stderr", "") or "Invalid audio duration."
        raise AudioProcessingError(details.strip()) from error

    if duration <= 0:
        raise AudioProcessingError("Audio duration must be greater than zero.")

    return duration


def probe_audio_stream(input_path: Path) -> AudioStreamInfo:
    """Return reusable codec, channel, rate, depth, bitrate, and duration data."""
    input_path = Path(input_path)
    if not input_path.is_file():
        raise AudioProcessingError(f"Input audio does not exist: {input_path}")

    command = [
        _ffprobe_executable(), "-v", "error", "-select_streams", "a:0",
        "-show_entries",
        "stream=codec_name,channels,sample_rate,bit_rate,bits_per_sample,bits_per_raw_sample,duration:format=duration,bit_rate",
        "-of", "json", str(input_path),
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        payload = json.loads(result.stdout)
        stream = payload["streams"][0]
        file_format = payload.get("format", {})
        duration = float(stream.get("duration") or file_format.get("duration"))
        bit_rate_value = stream.get("bit_rate") or file_format.get("bit_rate")
        depth_value = stream.get("bits_per_raw_sample") or stream.get("bits_per_sample")
        return AudioStreamInfo(
            codec_name=str(stream.get("codec_name") or "unknown"),
            channels=int(stream["channels"]),
            sample_rate=int(stream["sample_rate"]),
            bit_rate=int(bit_rate_value) if bit_rate_value else None,
            bits_per_sample=int(depth_value) if depth_value and int(depth_value) > 0 else None,
            duration_seconds=duration,
        )
    except (subprocess.CalledProcessError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as error:
        details = getattr(error, "stderr", "") or "Invalid or unsupported audio stream."
        raise AudioProcessingError(str(details).strip()) from error


def _run_ffmpeg(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or "Unknown FFmpeg error"
        raise AudioProcessingError(details) from error


def split_stereo_channels(
    input_path: Path,
    left_output_path: Path,
    right_output_path: Path,
    codec: str,
    bitrate_kbps: int | None = None,
) -> tuple[Path, Path]:
    """Split one stereo stream into independent mono L and R outputs."""
    input_path = Path(input_path)
    outputs = (Path(left_output_path), Path(right_output_path))
    if not input_path.is_file():
        raise AudioProcessingError(f"Input audio does not exist: {input_path}")
    if codec not in {"libmp3lame", "pcm_s16le", "pcm_s24le", "pcm_s32le"}:
        raise AudioProcessingError("Unsupported output codec.")
    if bitrate_kbps is not None and bitrate_kbps not in {128, 192, 256, 320}:
        raise AudioProcessingError("MP3 bitrate must be 128, 192, 256, or 320 kbps.")
    for output in outputs:
        output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        _ffmpeg_executable(), "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(input_path), "-filter_complex",
        "[0:a]channelsplit=channel_layout=stereo[left][right]",
    ]
    for label, output in zip(("[left]", "[right]"), outputs):
        command.extend(["-map", label, "-c:a", codec])
        if codec == "libmp3lame" and bitrate_kbps is not None:
            command.extend(["-b:a", f"{bitrate_kbps}k"])
        command.append(str(output))
    _run_ffmpeg(command)
    return outputs


def merge_mono_channels(
    left_input_path: Path,
    right_input_path: Path,
    output_path: Path,
    codec: str,
    duration_seconds: float,
    bitrate_kbps: int | None = None,
) -> Path:
    """Interleave mono inputs as stereo L/R, padding the shorter source."""
    inputs = (Path(left_input_path), Path(right_input_path))
    output_path = Path(output_path)
    if not all(path.is_file() for path in inputs):
        raise AudioProcessingError("Both mono input files are required.")
    if duration_seconds <= 0:
        raise AudioProcessingError("Output duration must be greater than zero.")
    if codec not in {"libmp3lame", "pcm_s16le", "pcm_s24le", "pcm_s32le"}:
        raise AudioProcessingError("Unsupported output codec.")
    if bitrate_kbps is not None and bitrate_kbps not in {128, 192, 256, 320}:
        raise AudioProcessingError("MP3 bitrate must be 128, 192, 256, or 320 kbps.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        _ffmpeg_executable(), "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(inputs[0]), "-i", str(inputs[1]), "-filter_complex",
        "[0:a]aformat=channel_layouts=mono,apad[l];[1:a]aformat=channel_layouts=mono,apad[r];[l][r]amerge=inputs=2[out]",
        "-map", "[out]", "-t", f"{duration_seconds:.6f}", "-c:a", codec,
    ]
    if codec == "libmp3lame" and bitrate_kbps is not None:
        command.extend(["-b:a", f"{bitrate_kbps}k"])
    command.append(str(output_path))
    _run_ffmpeg(command)
    return output_path


def analyze_audio_filter(input_path: Path, audio_filter: str) -> str:
    """Run a read-only FFmpeg audio filter and return its diagnostic output."""
    input_path = Path(input_path)
    if not input_path.is_file():
        raise AudioProcessingError(f"Input audio does not exist: {input_path}")
    if not audio_filter or not audio_filter.strip():
        raise AudioProcessingError("An audio analysis filter is required.")

    command = [
        _ffmpeg_executable(),
        "-hide_banner",
        "-nostats",
        "-i",
        str(input_path),
        "-vn",
        "-af",
        audio_filter,
        "-f",
        "null",
        "-",
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or "Unknown FFmpeg analysis error"
        raise AudioProcessingError(details) from error

    return result.stderr


def transform_audio(
    input_path: Path,
    output_path: Path,
    filters: Optional[Iterable[str]] = None,
    output_duration_seconds: Optional[float] = None,
    input_start_seconds: Optional[float] = None,
) -> Path:
    """Transform an audio file with FFmpeg and return the output path."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.is_file():
        raise AudioProcessingError(f"Input audio does not exist: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        _ffmpeg_executable(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
    ]

    if input_start_seconds is not None:
        if input_start_seconds < 0:
            raise AudioProcessingError("Input start time cannot be negative.")
        command.extend(["-ss", str(input_start_seconds)])

    command.extend(["-i", str(input_path), "-vn"])

    audio_filters = list(filters or [])
    if audio_filters:
        command.extend(["-af", ",".join(audio_filters)])

    if output_duration_seconds is not None:
        if output_duration_seconds <= 0:
            raise AudioProcessingError(
                "Output duration must be greater than zero."
            )
        command.extend(["-t", str(output_duration_seconds)])

    command.append(str(output_path))

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or "Unknown FFmpeg error"
        raise AudioProcessingError(details) from error

    return output_path
