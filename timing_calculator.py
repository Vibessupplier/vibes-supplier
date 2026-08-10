"""Tempo-synchronized delay and reverb timing calculations."""

from dataclasses import dataclass
import math


MIN_BPM = 20.0
MAX_BPM = 300.0


@dataclass(frozen=True)
class DelayTiming:
    label: str
    straight_ms: float
    dotted_ms: float
    triplet_ms: float


@dataclass(frozen=True)
class ReverbTiming:
    name: str
    predelay_ms: float
    decay_seconds: float
    character: str


def validate_bpm(bpm: float) -> float:
    value = float(bpm)
    if not math.isfinite(value) or not MIN_BPM <= value <= MAX_BPM:
        raise ValueError(f"BPM must be between {MIN_BPM:g} and {MAX_BPM:g}.")
    return value


def quarter_note_ms(bpm: float) -> float:
    return 60_000.0 / validate_bpm(bpm)


def delay_timings(bpm: float) -> tuple[DelayTiming, ...]:
    quarter = quarter_note_ms(bpm)
    notes = (("1/1", 4.0), ("1/2", 2.0), ("1/4", 1.0), ("1/8", .5), ("1/16", .25), ("1/32", .125))
    return tuple(
        DelayTiming(label, quarter * factor, quarter * factor * 1.5, quarter * factor * 2 / 3)
        for label, factor in notes
    )


def reverb_timings(bpm: float) -> tuple[ReverbTiming, ...]:
    quarter = quarter_note_ms(bpm)
    return (
        ReverbTiming("TIGHT ROOM", quarter / 16, quarter / 1000, "Short and controlled"),
        ReverbTiming("GROOVE ROOM", quarter / 8, quarter * 2 / 1000, "Natural rhythmic space"),
        ReverbTiming("PLATE", quarter / 4, quarter * 4 / 1000, "Open vocal or snare tail"),
        ReverbTiming("HALL", quarter / 2, quarter * 8 / 1000, "Long atmospheric tail"),
        ReverbTiming("DUB SPACE", quarter, quarter * 12 / 1000, "Very long creative send"),
    )
