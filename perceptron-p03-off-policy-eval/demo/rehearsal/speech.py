"""Rehearsal tooling for demo/SCRIPT.md. macOS only (uses `say` and `afinfo`); not needed to run the demo.

  python3 demo/rehearsal/speech.py     # parse the talk track, count spoken words, time each beat's speech, write demo/rehearsal/speech.json

Speech time per beat = the duration of macOS `say -r 150` (150 words per minute, default system voice) rendered to a file;
nothing is played aloud. demo/rehearsal/drive.js then performs the talk track's clicks in a real browser and waits each
beat's speech time, giving the measured rehearsal recorded in SCRIPT.md. parse_script() is also used by demo/smoke_check.py.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "SCRIPT.md"
RATE_WPM = 150


def parse_script(path: Path = SCRIPT) -> list[dict]:
    """Beats of the '## Talk track' table: number, start, clicks, spoken text (one quoted string), its word count, fallback."""
    beats, in_track = [], False
    for ln in Path(path).read_text().splitlines():
        if ln.startswith("## "):
            in_track = ln.strip() == "## Talk track"
            continue
        if not (in_track and ln.startswith("| ")):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not cells[0].isdigit():
            continue
        m = re.fullmatch(r'"(.*)"', cells[3])
        assert m, f"beat {cells[0]}: the say column must be a single quoted string"
        beats.append({"beat": int(cells[0]), "start": cells[1], "do": cells[2], "say": m.group(1), "words": len(m.group(1).split()),
                      "fallback": cells[4] if len(cells) > 4 else ""})
    assert beats, "no talk-track beats found"
    return beats


def speech_seconds(text: str) -> float:
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "beat.aiff"
        subprocess.run(["say", "-r", str(RATE_WPM), "-o", str(f), text], check=True)
        info = subprocess.run(["afinfo", str(f)], capture_output=True, text=True, check=True).stdout
    return float(re.search(r"estimated duration: ([\d.]+) sec", info).group(1))


def main():
    beats = parse_script()
    out = {"rate_wpm": RATE_WPM, "voice": "macOS say, default system voice", "beats": []}
    for b in beats:
        sec = speech_seconds(b["say"])
        out["beats"].append({"beat": b["beat"], "words": b["words"], "seconds": round(sec, 2)})
        print(f"beat {b['beat']:>2}: {b['words']:>3} words, {sec:5.1f} s", file=sys.stderr)
    out["total_words"] = sum(b["words"] for b in beats)
    out["total_speech_seconds"] = round(sum(b["seconds"] for b in out["beats"]), 2)
    (HERE / "speech.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{out['total_words']} spoken words; speech {out['total_speech_seconds']:.1f} s at {RATE_WPM} wpm")


if __name__ == "__main__":
    main()
