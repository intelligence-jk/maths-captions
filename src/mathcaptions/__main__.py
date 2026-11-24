"""python -m mathcaptions script.txt [--vtt] [--max-chars 32]"""
import argparse
import sys

from .core import build_cues, parse_script, to_srt, to_vtt


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m mathcaptions")
    p.add_argument("script")
    p.add_argument("--vtt", action="store_true", help="write WebVTT instead of SRT")
    p.add_argument("--max-chars", type=int, default=32)
    a = p.parse_args(argv)
    try:
        cues = build_cues(parse_script(open(a.script).read()), a.max_chars)
    except ValueError as e:
        print(f"Cannot build captions: {e}", file=sys.stderr)
        return 1
    sys.stdout.write((to_vtt if a.vtt else to_srt)(cues))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
