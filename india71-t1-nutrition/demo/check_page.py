"""Headless checks of the offline demo page (step 5 of demo/smoke.sh). Needs Python Playwright + Chromium.

At the projector size 1280x720 (and 1440x900) every screen and key state must fit without scrolling, with sources at
>= 13 px, tile labels at >= 4.5:1 contrast, no overlapping chart labels, no half-hidden ledger rows, a working Details
drawer, the key values on screen, no page errors and no request that is not file://. Run: python3 demo/check_page.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = (Path(__file__).resolve().parent / "index.html").as_uri()
FIT_STATES = [
    "india", "india&tileMode=pt&ind=underweight", "districts&state=MH&district=Nandurbar", "districts&state=UP",
    "find&cov=0.35&noise=0", "find&cov=0&noise=0.4", "find&cov=1&noise=0.4",
    "child&cohort=nandurbar", "child&cohort=amravati",
    "week&cohort=nandurbar&K=5&reveal=1", "week&cohort=amravati&K=10&reveal=1", "week&cohort=nandurbar&K=1&ex=7",
    "sms&cohort=nandurbar", "sms&cohort=amravati&K=3",
    "break&cohort=nandurbar&tamper=intact", "break&cohort=nandurbar&tamper=truncate&req=own_aww",
    "break&cohort=amravati&tamper=resealall&req=fake_consent", "break&cohort=amravati&tamper=flip",
]
EXPECT = [
    ("india", ["all 36 States and UTs", "19.3%", "5.46%", "Not like-for-like", "REAL DATA"]),
    ("districts&state=MH&district=Nandurbar&cohort=nandurbar", ["in Nandurbar, 30.7%", "13.5%", "45.8%", "706 of 707 districts"]),
    ("find&cov=0&noise=0.4", ["true by definition", "3,907", "366 false", "2,456", "34 false", "2,250", "without pooling names", "Fixed illustration"]),
    ("find&cov=0.35&noise=0", ["simulation assumption", "realised 32.8%", "4,394", "151 false"]),
    ("find&cov=1&noise=0.4", ["unchanged", "IDs only: no score-based link accepted", "reached only by accepting keyed-ID links alone", "4,531"]),
    ("find&cov=0&noise=0.4&x=1", ["in-sample comparison", "proposed policy", "default threshold, used on screens 4–7"]),
    ("child&cohort=nandurbar", ["SIMULATED children · REAL district rates", "first wasting", "infant pathway", "correctly", "not evidence that most children are caught"]),
    ("week&cohort=nandurbar&K=5&reveal=1", ["Who gets them?", "infant pathway", "percentage points", "47.3%"]),
    ("week&cohort=nandurbar&K=1", ["Not distinguishable from zero"]),
    ("sms&cohort=nandurbar", ["Featured pipeline", "K = 5", "retained, not delivered → capacity exception to LS", "no worker clock", "none is escalated against the worker"]),
    ("sms&cohort=nandurbar&K=3", ["Screen 5 is set to K = 3"]),
    ("break&cohort=nandurbar&req=cdpo_discipline&tamper=truncate", ["DENIED", "deny-employment-action", "recorded policy decisions", "live hash verification",
                                                                      "simulated external checkpoint", "replace both", "broken at entry", "chain verifies"]),
]

JS_METRICS = """() => {
  const d = document.documentElement, scr = document.querySelector('.screen.active');
  const src = [...scr.querySelectorAll('.src')].map(e => parseFloat(getComputedStyle(e).fontSize));
  const overflowing = [...scr.querySelectorAll('.panel')].map(p => p.scrollHeight - p.clientHeight).filter(x => x > 1);
  const foot = scr.querySelector('.foot').getBoundingClientRect();
  const boxes = sel => [...scr.querySelectorAll(sel)].map(e => e.getBoundingClientRect()).filter(r => r.width > 0);
  const hit = (a, b) => a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1;
  const pairs = list => { let n = 0; for (let i = 0; i < list.length; i++) for (let j = i + 1; j < list.length; j++) if (hit(list[i], list[j])) n++; return n; };
  const labels = boxes('#lbl-india, #lbl-state');
  const events = boxes('text.evlbl');
  const infant = boxes('#lbl-infant'), diamonds = boxes('.lanes rect[transform]');
  let infantHits = 0; infant.forEach(a => diamonds.forEach(b => { if (hit(a, b)) infantHits++; }));
  let partial = 0; const led = scr.querySelector('.ledger');
  if (led) { const hb = led.querySelector('thead').getBoundingClientRect();
    led.querySelectorAll('tbody tr').forEach(t => { const r = t.getBoundingClientRect(); if (r.top < hb.bottom - 1 && r.bottom > hb.bottom + 1) partial++; }); }
  return {sh: d.scrollHeight, sw: d.scrollWidth, src: Math.min(...src), overflowing, footBottom: foot.bottom,
          labelOverlaps: pairs(labels), eventOverlaps: pairs(events), infantHits, partial};
}"""

BARS_JS = """() => {
  const out = [];
  document.querySelectorAll('.screen.active .bar').forEach(bar => {
    const track = bar.querySelector('.track').getBoundingClientRect();
    const t = bar.querySelector('.seg-true').getBoundingClientRect(), f = bar.querySelector('.seg-false');
    const name = bar.dataset.method;
    if (f) {
      const fr = f.getBoundingClientRect(), n = Number(f.dataset.false);
      if (n > 0 && fr.width < 2.9) out.push(name + ': ' + n + ' false links but red width ' + fr.width.toFixed(2) + 'px');
      if (fr.right > track.right + 0.5) out.push(name + ': red segment outside the track');
    }
    if (t.right > track.right + 0.5) out.push(name + ': bar outside the track');
  });
  return out;
}"""

CONTRAST_JS = """() => { const vals = PS.tileValues(); let worst = 99, worstV = null;
  vals.forEach(v => { const c = PS.contrast(PS.heatRGB(v), PS.inkRGB(v)); if (c < worst) { worst = c; worstV = v; } });
  return {n: vals.length, worst, worstV}; }"""


def main() -> int:
    errors: list[str] = []
    foreign: list[str] = []
    failures = 0

    def report(ok: bool, msg: str) -> None:
        nonlocal failures
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {msg}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720}, reduced_motion="reduce")
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("request", lambda r: foreign.append(r.url) if not r.url.startswith(("file:", "data:", "about:")) else None)

        def load(fragment: str) -> None:
            page.goto("about:blank")
            page.goto(f"{URL}#{fragment}")
            page.wait_for_selector("html[data-ready='1']", timeout=60000)

        t0 = time.perf_counter()
        load("india")
        first = time.perf_counter() - t0
        report(first < 60, f"first visual ready in {first:.2f} s (bar: 60 s)")

        for vw, vh in [(1280, 720), (1440, 900)]:
            page.set_viewport_size({"width": vw, "height": vh})
            bad = []
            worst_src = 99.0
            for st in FIT_STATES:
                load(st)
                page.wait_for_timeout(120)
                m = page.evaluate(JS_METRICS)
                worst_src = min(worst_src, m["src"])
                problems = []
                if m["sh"] > vh or m["sw"] > vw:
                    problems.append(f"scrolls ({m['sw']}x{m['sh']})")
                if m["overflowing"]:
                    problems.append(f"panel content cut {m['overflowing']}")
                if m["src"] < 13:
                    problems.append(f"source text {m['src']:.1f}px")
                if m["labelOverlaps"] or m["eventOverlaps"] or m["infantHits"]:
                    problems.append(f"overlapping labels {m['labelOverlaps']}/{m['eventOverlaps']}/{m['infantHits']}")
                if m["partial"]:
                    problems.append(f"{m['partial']} ledger row(s) half under the header")
                if problems:
                    bad.append(f"{st}: {'; '.join(problems)}")
            report(not bad, f"{vw}x{vh}: {len(FIT_STATES)} screen states fit without scrolling, sources >= 13 px (min {worst_src:.1f}), no label overlaps, no half-hidden rows"
                   + ("" if not bad else "\n        " + "\n        ".join(bad)))
        page.set_viewport_size({"width": 1280, "height": 720})

        load("india")
        c = page.evaluate(CONTRAST_JS)
        report(c["worst"] >= 4.5, f"tile labels: worst contrast {c['worst']:.2f}:1 over {c['n']} tiles (both modes) (bar: 4.5:1)")

        bar_bad = []
        for cov in ["0", "0.1", "0.2", "0.35", "0.5", "0.75", "1"]:
            for noise in ["0", "0.4"]:
                load(f"find&cov={cov}&noise={noise}")
                res = page.evaluate(BARS_JS)
                bar_bad += [f"{cov}|{noise} {r}" for r in res]
        report(not bar_bad, "linkage bars: every false-link count > 0 draws a visible red segment (>= 3 px), on one count axis inside the track (100% IDs included)"
               + ("" if not bar_bad else "\n        " + "\n        ".join(bar_bad[:8])))

        page.set_viewport_size({"width": 1280, "height": 720})
        load("week&cohort=amravati&K=10&reveal=1")
        text = page.inner_text("main")
        page.keyboard.press("d")
        roster = page.inner_text("#details")
        page.keyboard.press("Escape")
        report("not shown (full list: Details)" in text and "below" not in text and "Full list: AWC" in roster and roster.count("PT-") >= 10,
               "K = 10 at 1280x720: unlisted-row note says 'not shown' and the full roster is in Details (review R4)")

        load("find&cov=0&noise=0.4")
        page.keyboard.press("d")
        opened = page.is_visible("#details") and "department boundary" in page.inner_text("#details").lower()
        page.keyboard.press("Escape")
        report(opened and not page.is_visible("#details"), "Details drawer opens with 'd' (secondary evidence) and closes with Esc")

        for fragment, needles in EXPECT:
            load(fragment)
            text = page.inner_text("main")
            missing = [n for n in needles if n not in text]
            report(not missing, f"#{fragment.split('&')[0]:<9} " + (", ".join(needles) if not missing else "missing: " + ", ".join(missing)))
        browser.close()
    if errors:
        report(False, "page errors:\n    " + "\n    ".join(errors))
    if foreign:
        report(False, "non-file requests:\n    " + "\n    ".join(foreign))
    if not errors and not foreign:
        print("  ok   no page errors; no network requests (file:// only)")
    print("check_page:", f"{failures} FAILED" if failures else "all checks pass")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
