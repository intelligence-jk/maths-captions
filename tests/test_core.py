import random

import pytest

from mathcaptions import build_cues, parse_script, split_text, split_time, to_srt, to_vtt
from mathcaptions.__main__ import main


def test_split_text():
    assert split_text("Add 3 to both sides of the equation", 16) == ["Add 3 to both", "sides of the", "equation"]
    assert split_text("short", 32) == ["short"]
    assert split_text("unbreakable-long-word", 5) == ["unbreakable-long-word"]


def test_split_time_exact_and_proportional():
    assert split_time(1000, [1, 1, 1]) == [334, 333, 333]
    assert split_time(100, [3, 1]) == [75, 25]
    rng = random.Random(1)
    for _ in range(300):
        w = [rng.randint(1, 40) for _ in range(rng.randint(1, 6))]
        total = rng.randint(0, 9000)
        parts = split_time(total, w)
        assert sum(parts) == total and all(p >= 0 for p in parts)


def test_cues_contiguous_and_total_kept():
    rows = parse_script("2.5 Add 3 to both sides of the equation\n1 So x equals 4\n")
    cues = build_cues(rows, 20)
    assert cues[0].start_ms == 0
    for a, b in zip(cues, cues[1:]):
        assert a.end_ms == b.start_ms
    assert cues[-1].end_ms == 3500
    assert all(len(c.text) <= 20 for c in cues)


def test_srt_and_vtt_format():
    cues = build_cues([(1500, "Hello"), (61_000, "Next")])
    assert to_srt(cues) == (
        "1\n00:00:00,000 --> 00:00:01,500\nHello\n\n2\n00:00:01,500 --> 00:01:02,500\nNext\n\n"
    )
    assert to_vtt(cues).startswith("WEBVTT\n\n00:00:00.000 --> 00:00:01.500\nHello")


def test_hour_stamp():
    assert to_srt(build_cues([(3_723_004, "x")])).count("01:02:03,004") == 1


@pytest.mark.parametrize("bad", ["abc words", "0 words", "2.5", "1.2345 words"])
def test_bad_script(bad):
    with pytest.raises(ValueError):
        parse_script(bad)


def test_comments_and_blank_lines():
    assert parse_script("# note\n\n1 Hi\n") == [(1000, "Hi")]


def test_cli(tmp_path, capsys):
    f = tmp_path / "s.txt"
    f.write_text("2 Hello there\n")
    assert main([str(f)]) == 0
    assert "00:00:00,000 --> 00:00:02,000" in capsys.readouterr().out
    assert main([str(f), "--vtt"]) == 0
    assert capsys.readouterr().out.startswith("WEBVTT")
