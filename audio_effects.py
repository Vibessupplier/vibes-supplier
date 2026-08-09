"""Product-level audio effects built on top of the FFmpeg engine."""

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Optional

from audio_engine import AudioProcessingError, transform_audio


MIN_SPEED_FACTOR = 0.50
MAX_SPEED_FACTOR = 2.00
MIN_PITCH_SEMITONES = -12.0
MAX_PITCH_SEMITONES = 12.0
OUTPUT_SAMPLE_RATE = 48_000
SPEED_PREVIEW_SECONDS = 20.0
PITCH_MODES = ("Follow speed", "Keep original", "Custom")


@dataclass(frozen=True)
class SpeedSettings:
    source_bpm: float
    target_bpm: float
    speed: float
    pitch_mode: str
    pitch_semitones: float
    processing_pitch_semitones: Optional[float]


def _validate_speed_factor(speed: float) -> None:
    if not MIN_SPEED_FACTOR <= speed <= MAX_SPEED_FACTOR:
        raise AudioProcessingError(
            f"Speed factor must be between "
            f"{MIN_SPEED_FACTOR} and {MAX_SPEED_FACTOR}."
        )


def calculate_speed_factor(source_bpm: float, target_bpm: float) -> float:
    """Calculate and validate the playback speed for two BPM values."""
    if source_bpm <= 0:
        raise AudioProcessingError("Original BPM must be greater than zero.")

    speed = target_bpm / source_bpm
    _validate_speed_factor(speed)

    return speed


def resolve_speed_settings(
    source_bpm: float,
    target_bpm: float,
    pitch_mode: str,
    custom_pitch_semitones: float = 0.0,
) -> SpeedSettings:
    """Validate browser controls and resolve authoritative export settings."""
    values = (source_bpm, target_bpm, custom_pitch_semitones)
    if not all(math.isfinite(value) for value in values):
        raise AudioProcessingError("Speed settings must contain finite values.")
    if not 40.0 <= source_bpm <= 250.0:
        raise AudioProcessingError("Original BPM must be between 40 and 250.")
    if not 20.0 <= target_bpm <= 300.0:
        raise AudioProcessingError("Target BPM must be between 20 and 300.")
    if pitch_mode not in PITCH_MODES:
        raise AudioProcessingError("Unknown pitch mode.")

    speed = calculate_speed_factor(source_bpm, target_bpm)
    if pitch_mode == "Follow speed":
        pitch_semitones = 12 * math.log2(speed)
        processing_pitch = None
    elif pitch_mode == "Keep original":
        pitch_semitones = 0.0
        processing_pitch = 0.0
    else:
        if not MIN_PITCH_SEMITONES <= custom_pitch_semitones <= MAX_PITCH_SEMITONES:
            raise AudioProcessingError(
                f"Pitch must be between {MIN_PITCH_SEMITONES} and "
                f"{MAX_PITCH_SEMITONES} semitones."
            )
        pitch_semitones = custom_pitch_semitones
        processing_pitch = custom_pitch_semitones

    return SpeedSettings(
        source_bpm=source_bpm,
        target_bpm=target_bpm,
        speed=speed,
        pitch_mode=pitch_mode,
        pitch_semitones=pitch_semitones,
        processing_pitch_semitones=processing_pitch,
    )


def _atempo_filters(factor: float) -> list[str]:
    """Split a tempo factor into high-quality FFmpeg atempo stages."""
    filters = []

    while factor < 0.50:
        filters.append("atempo=0.5")
        factor /= 0.50

    while factor > 2.00:
        filters.append("atempo=2.0")
        factor /= 2.00

    if not math.isclose(factor, 1.0):
        filters.append(f"atempo={factor}")

    return filters


def change_speed(
    input_path: Path,
    output_path: Path,
    speed: float = 1.20,
    pitch_semitones: Optional[float] = None,
    output_duration_seconds: Optional[float] = None,
) -> Path:
    """Change speed and optionally control pitch independently."""
    _validate_speed_factor(speed)

    if pitch_semitones is None:
        pitch_factor = speed
    else:
        if not MIN_PITCH_SEMITONES <= pitch_semitones <= MAX_PITCH_SEMITONES:
            raise AudioProcessingError(
                f"Pitch must be between {MIN_PITCH_SEMITONES} and "
                f"{MAX_PITCH_SEMITONES} semitones."
            )
        pitch_factor = 2 ** (pitch_semitones / 12)

    filters = [
        f"aresample={OUTPUT_SAMPLE_RATE}",
        f"asetrate={OUTPUT_SAMPLE_RATE}*{pitch_factor}",
        f"aresample={OUTPUT_SAMPLE_RATE}",
    ]
    filters.extend(_atempo_filters(speed / pitch_factor))

    return transform_audio(
        input_path,
        output_path,
        filters=filters,
        output_duration_seconds=output_duration_seconds,
    )


def create_speed_preview(
    input_path: Path,
    output_path: Path,
    speed: float,
    pitch_semitones: Optional[float] = None,
) -> Path:
    """Create a processed Speed Changer preview of up to 20 seconds."""
    return change_speed(
        input_path,
        output_path,
        speed=speed,
        pitch_semitones=pitch_semitones,
        output_duration_seconds=SPEED_PREVIEW_SECONDS,
    )


def create_speed_player_audio(input_path: Path, output_path: Path) -> Path:
    """Create one browser-compatible listening copy for live speed audition."""
    return transform_audio(input_path, output_path)
