# SCRIBE: Subtitles that Carry Real Integrals, Brackets and Equations

Formerly `maths-captions`.

Make SRT or WebVTT captions for a maths video from a script of timed lines.

## What it solves
A narration script knows how long each line lasts but not where to break it on screen. This splits each line into short caption pieces that fit a phone screen, shares the line's time between the pieces in proportion to their length, and writes the caption file. The pieces always join with no gap, and they add up to exactly the line's duration. Pure Python 3.10+, standard library only, integer milliseconds.

## Example
`script.txt` (seconds, then the words):
```
2.5 Add 3 to both sides of the equation
1 So x equals 4
```
```bash
python -m mathcaptions script.txt --max-chars 20
```
```
1
00:00:00,000 --> 00:00:01,397
Add 3 to both sides

2
00:00:01,397 --> 00:00:02,500
of the equation

3
00:00:02,500 --> 00:00:03,500
So x equals 4
```
(The first line's 2500 ms is shared 19 : 15 by length, 1397 and 1103; add `--vtt` for WebVTT.)

## The maths behind it
A line of `T` milliseconds with pieces of `c1, c2, ... cn` characters should give piece `i` the time `T * ci / (c1 + ... + cn)`. Those are rarely whole milliseconds, so the largest remainder method is used: every piece gets the whole-number part, and the leftover milliseconds go one each to the pieces with the biggest fractional parts. The result is whole milliseconds that add up to exactly `T`, so captions never drift against the voice over a long video. Durations are read as exact fractions of a second, so `2.5` is 2500 ms, never 2499.9999.

## Install and run
```bash
python -m pip install -e .
python -m mathcaptions script.txt
python -m pytest
```

## Licence
MIT. Made by Math & Myth (mathandmyth.ae): one to one maths mentoring, online, across the UAE.
