"""Build SRT and VTT captions from a script of timed lines. Integer milliseconds only."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Cue:
    start_ms: int
    end_ms: int
    text: str


def split_text(text: str, max_chars: int = 32) -> list[str]:
    """Split on spaces into pieces of at most max_chars (a longer single word stays whole)."""
    if max_chars < 1:
        raise ValueError("max_chars must be at least 1")
    pieces, cur = [], ""
    for w in text.split():
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            pieces.append(cur)
            cur = w
    if cur:
        pieces.append(cur)
    return pieces


def split_time(total_ms: int, weights: list[int]) -> list[int]:
    """Share total_ms in proportion to weights, exactly (largest remainder method)."""
    if total_ms < 0 or not weights or any(w <= 0 for w in weights):
        raise ValueError("need a non-negative total and positive weights")
    s = sum(weights)
    base = [total_ms * w // s for w in weights]
    rest = total_ms - sum(base)
    order = sorted(range(len(weights)), key=lambda i: (-(total_ms * weights[i] % s), i))
    for i in order[:rest]:
        base[i] += 1
    return base


def parse_script(text: str) -> list[tuple[int, str]]:
    """Each line: SECONDS then the words, for example '2.5 Add 3 to both sides'."""
    rows = []
    for n, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        head, _, body = line.partition(" ")
        try:
            ms = Fraction(head) * 1000
        except ValueError:
            raise ValueError(f"line {n}: starts with {head!r}, expected a number of seconds")
        if ms.denominator != 1 or ms <= 0 or not body.strip():
            raise ValueError(f"line {n}: need a positive duration (at most 3 decimals) and some words")
        rows.append((int(ms), body.strip()))
    return rows


def build_cues(rows: list[tuple[int, str]], max_chars: int = 32, start_ms: int = 0) -> list[Cue]:
    cues, t = [], start_ms
    for dur, text in rows:
        pieces = split_text(text, max_chars)
        for piece, d in zip(pieces, split_time(dur, [len(p) for p in pieces])):
            cues.append(Cue(t, t + d, piece))
            t += d
    return cues


def _stamp(ms: int, sep: str) -> str:
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, milli = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{milli:03d}"


def to_srt(cues: list[Cue]) -> str:
    return "".join(
        f"{i}\n{_stamp(c.start_ms, ',')} --> {_stamp(c.end_ms, ',')}\n{c.text}\n\n"
        for i, c in enumerate(cues, 1)
    )


def to_vtt(cues: list[Cue]) -> str:
    return "WEBVTT\n\n" + "".join(
        f"{_stamp(c.start_ms, '.')} --> {_stamp(c.end_ms, '.')}\n{c.text}\n\n" for c in cues
    )
