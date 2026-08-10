"""Reusable waveform and sample extraction for the Audio Chopper."""

from dataclasses import dataclass
from io import BytesIO
import math
from pathlib import Path
import re
import tempfile
from typing import Sequence
from zipfile import ZIP_STORED, ZipFile

import numpy as np
import soundfile as sf

from audio_engine import AudioProcessingError, transform_audio


WAVEFORM_POINTS = 12_000
CHOPPER_PREVIEW_SECONDS = 30.0
MIN_CLIP_SECONDS = 0.1
SAMPLE_TRAY_LIMIT = 4
PRO_SAMPLE_LIMIT = 10


class AudioChopperError(RuntimeError):
    """Raised when waveform analysis or sample extraction fails."""


@dataclass(frozen=True)
class WaveformData:
    duration_seconds: float
    peaks: tuple[float, ...]


def _extract_wav_waveform(wav_path: Path, points: int) -> WaveformData:
    if points < 16 or points > 20_000:
        raise AudioChopperError("Waveform resolution must be between 16 and 20000.")

    with sf.SoundFile(wav_path) as audio_file:
        if audio_file.frames <= 0 or audio_file.samplerate <= 0:
            raise AudioChopperError("The audio file contains no samples.")

        duration = audio_file.frames / audio_file.samplerate
        samples_per_bin = max(1, math.ceil(audio_file.frames / points))
        peaks = np.zeros(points, dtype=np.float64)
        sample_offset = 0

        for block in audio_file.blocks(
            blocksize=65536,
            dtype="float32",
            always_2d=True,
        ):
            mono_peaks = np.max(np.abs(block), axis=1)
            bin_indices = (
                sample_offset + np.arange(len(mono_peaks), dtype=np.int64)
            ) // samples_per_bin
            valid = bin_indices < points
            valid_bins = bin_indices[valid]
            valid_peaks = mono_peaks[valid]
            if len(valid_bins):
                group_starts = np.concatenate(
                    (
                        np.array([0], dtype=np.int64),
                        np.flatnonzero(np.diff(valid_bins)) + 1,
                    )
                )
                grouped_peaks = np.maximum.reduceat(valid_peaks, group_starts)
                grouped_bins = valid_bins[group_starts]
                peaks[grouped_bins] = np.maximum(
                    peaks[grouped_bins],
                    grouped_peaks,
                )
            sample_offset += len(block)

    maximum = float(peaks.max())
    if maximum > 1e-12:
        peaks /= maximum

    return WaveformData(
        duration_seconds=duration,
        peaks=tuple(float(value) for value in peaks),
    )


def extract_waveform(
    input_path: Path,
    points: int = WAVEFORM_POINTS,
) -> WaveformData:
    """Decode audio safely and return a normalized static peak envelope."""
    try:
        with tempfile.TemporaryDirectory() as temp_directory:
            decoded_path = Path(temp_directory) / "waveform.wav"
            transform_audio(input_path, decoded_path)
            return _extract_wav_waveform(decoded_path, points)
    except (AudioProcessingError, sf.LibsndfileError) as error:
        raise AudioChopperError(str(error)) from error


def validate_clip_range(
    start_seconds: float,
    end_seconds: float,
    duration_seconds: float,
) -> float:
    """Validate a user-selected range and return its duration."""
    values = (start_seconds, end_seconds, duration_seconds)
    if not all(math.isfinite(value) for value in values):
        raise AudioChopperError("Clip times must be finite values.")
    if duration_seconds <= 0:
        raise AudioChopperError("Audio duration must be greater than zero.")
    if start_seconds < 0 or end_seconds > duration_seconds:
        raise AudioChopperError("The selected clip must stay inside the audio.")
    clip_duration = end_seconds - start_seconds
    if clip_duration < MIN_CLIP_SECONDS:
        raise AudioChopperError(
            f"The selected clip must be at least {MIN_CLIP_SECONDS:.1f} seconds."
        )
    return clip_duration


def create_audio_clip(
    input_path: Path,
    output_path: Path,
    start_seconds: float,
    end_seconds: float,
    source_duration_seconds: float,
    maximum_duration_seconds: float | None = None,
    edge_fade_seconds: float = 0.0,
) -> Path:
    """Export a selected range, optionally limiting a listening preview."""
    clip_duration = validate_clip_range(
        start_seconds,
        end_seconds,
        source_duration_seconds,
    )
    if maximum_duration_seconds is not None:
        if maximum_duration_seconds <= 0:
            raise AudioChopperError("Maximum duration must be greater than zero.")
        clip_duration = min(clip_duration, maximum_duration_seconds)
    if not math.isfinite(edge_fade_seconds) or edge_fade_seconds < 0:
        raise AudioChopperError("Edge fade must be a finite non-negative duration.")
    applied_fade = min(edge_fade_seconds, clip_duration / 4.0)

    try:
        if applied_fade > 0:
            fade_out_start = clip_duration - applied_fade
            return transform_audio(
                input_path,
                output_path,
                filters=[
                    f"afade=t=in:st=0:d={applied_fade:.6f}",
                    (
                        "afade=t=out:"
                        f"st={fade_out_start:.6f}:d={applied_fade:.6f}"
                    ),
                ],
                input_start_seconds=start_seconds,
                output_duration_seconds=clip_duration,
            )
        return transform_audio(
            input_path,
            output_path,
            input_start_seconds=start_seconds,
            output_duration_seconds=clip_duration,
        )
    except AudioProcessingError as error:
        raise AudioChopperError(str(error)) from error


def safe_sample_filename(name: str, fallback_index: int) -> str:
    """Return a short, archive-safe MP3 filename for a saved sample."""
    cleaned = Path(str(name).strip()).stem
    cleaned = re.sub(r"[^\w -]+", "", cleaned, flags=re.UNICODE)
    cleaned = re.sub(r"[\s_-]+", "_", cleaned).strip("_")[:64]
    if not cleaned:
        cleaned = f"sample_{fallback_index:02d}"
    return f"{cleaned}.mp3"


def build_sample_archive(samples: Sequence[tuple[str, bytes]]) -> bytes:
    """Package saved MP3 samples into a deterministic in-memory ZIP archive."""
    if not samples:
        raise AudioChopperError("At least one saved sample is required.")
    if len(samples) > PRO_SAMPLE_LIMIT:
        raise AudioChopperError(
            f"A sample archive can contain at most {PRO_SAMPLE_LIMIT} files."
        )

    archive_buffer = BytesIO()
    used_names: set[str] = set()
    with ZipFile(archive_buffer, "w", compression=ZIP_STORED) as archive:
        for index, (name, audio_data) in enumerate(samples, start=1):
            if not isinstance(audio_data, bytes) or not audio_data:
                raise AudioChopperError("Saved samples must contain MP3 audio data.")
            filename = safe_sample_filename(name, index)
            stem = Path(filename).stem
            candidate = filename
            duplicate_index = 2
            while candidate.casefold() in used_names:
                candidate = f"{stem}_{duplicate_index:02d}.mp3"
                duplicate_index += 1
            used_names.add(candidate.casefold())
            archive.writestr(candidate, audio_data)
    return archive_buffer.getvalue()
