"""Browser stage of the demo smoke test (headless Chromium via Python Playwright; no downloads).

    python demo/smoke_browser.py http://127.0.0.1:<port>/index.html

Checks the presentation contract a judge can break with clicks:
  * day identity: cached day switches and out-of-order (delayed) replay responses never attach one day's
    numbers or green checks to another day; the dial readout follows the displayed day;
  * splice identity: a delayed splice response is never shown for a different selection;
  * DPR 2: repeated control changes and viewport resizes keep every canvas's logical (CSS) height fixed;
  * layout: no horizontal overflow at 1280x720 and 1440x900;
  * failure states: a missing scoreboard and a missing replay produce visible errors with a fallback pointer,
    while the committed panels stay usable.
Exit 0 = pass, 1 = fail, 3 = Playwright unavailable (SKIPPED, printed loudly).
"""
from __future__ import annotations

import sys
import time

FAIL: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(("  ok   " if cond else "  FAIL ") + msg, flush=True)
    if not cond:
        FAIL.append(msg)


def main(url: str) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:  # fresh machines without Playwright
        print("\n" + "!" * 78 + f"\n!! BROWSER STAGE SKIPPED: python Playwright not importable ({e}).\n"
              "!! Install with: pip install playwright && playwright install chromium-headless-shell\n" + "!" * 78)
        return 3

    js_errors: list[str] = []

    def page_with(ctx):
        p = ctx.new_page()
        p.on("pageerror", lambda e: js_errors.append(str(e)))
        return p

    def wait_day(p, day: str, timeout: float = 20000) -> None:
        p.wait_for_function("d => { const t = document.querySelector('#rp-totals');"
                            " return t && t.dataset.payloadDay === d && document.querySelector('#rp-totals tbody').children.length === 5; }",
                            arg=day, timeout=timeout)

    def ident(p) -> dict:
        return p.evaluate("""() => { const t = document.querySelector('#rp-totals');
          const rows = [...document.querySelectorAll('#rp-totals tbody tr')].map(r => r.textContent);
          return {sel: DAY, shownSel: t.dataset.selectedDay, payload: t.dataset.payloadDay, ref: t.dataset.refDay,
                  showing: document.querySelector('#rp-showing').innerText, readout: document.querySelector('#dial-readout').innerText,
                  ok: rows.filter(r => r.includes('✓')).length, bad: rows.filter(r => r.includes('✗')).length,
                  stopAlarms: (dayData(DAY) && dayData(DAY).stops[STOP]) ? stopAlarmCount(dayData(DAY).stops[STOP]) : null}; }""")

    def set_stop(p, sid: str) -> None:
        p.evaluate("id => { const r = document.querySelector('#dial-range'); r.value = ORDER.indexOf(id); r.dispatchEvent(new Event('input')); }", sid)

    def click_day(p, day: str) -> None:
        p.locator("#day-tabs button", has_text=day).click()

    with sync_playwright() as pw:
        try:
            br = pw.chromium.launch(headless=True)
        except Exception as e:
            print("\n" + "!" * 78 + f"\n!! BROWSER STAGE SKIPPED: Chromium not installed ({str(e).splitlines()[0]}).\n" + "!" * 78)
            return 3

        print("[b1] day identity: cached switch")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        p = page_with(ctx)
        t0 = time.time()
        p.goto(url)
        p.wait_for_selector("body[data-ready='1']", timeout=10000)
        print(f"  info committed panels painted {1000 * (time.time() - t0):.0f} ms after navigation")
        days = p.evaluate("SB.replay_days.map(r => r.day)")
        dev, calm, med = days[0], days[1], days[2]
        wait_day(p, dev)
        click_day(p, calm)
        wait_day(p, calm)
        set_stop(p, "naive_30")
        a = ident(p)
        check(a["sel"] == a["shownSel"] == a["payload"] == a["ref"] == calm and a["ok"] == 5 and a["bad"] == 0,
              f"{calm} at 1e-30: selected/payload/reference day agree, 5/5 green checks")
        check(a["readout"].startswith(f"{a['stopAlarms']} alarms") and f"on {calm}" in a["readout"],
              f"dial readout says '{a['stopAlarms']} alarms' on {calm}")
        click_day(p, dev)  # cached
        b = ident(p)
        check(b["sel"] == b["shownSel"] == b["payload"] == b["ref"] == dev and b["ok"] == 0 and b["bad"] == 0,
              f"cached switch to {dev}: all day keys agree, no held-out checks shown on the dev day")
        check(f"on {dev}" in b["readout"] and f"on {calm}" not in b["readout"], f"dial readout follows the cached switch to {dev}")
        ctx.close()

        print("[b2] day identity: out-of-order delayed response")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        ctx.route(f"**/.cache/replay_{calm}.json", lambda r: (time.sleep(1.5), r.continue_()))
        p = page_with(ctx)
        p.goto(url)
        wait_day(p, dev)
        click_day(p, med)
        wait_day(p, med)
        click_day(p, calm)       # slow response
        click_day(p, med)        # user moves on before it arrives
        p.wait_for_timeout(2500)
        c = ident(p)
        com = p.evaluate("d => SB.rows.find(r => r.policy === 'regime_gated').per_day[d]", med)
        shown_gate = p.evaluate("() => dayData(DAY).policies.regime_gated.logloss")
        check(c["sel"] == c["shownSel"] == c["payload"] == c["ref"] == med and c["ok"] == 5 and c["bad"] == 0,
              f"late {calm} response did not replace {med}: day keys agree, 5/5 green")
        check(abs(shown_gate - com) < 1e-9, f"{med} gate loss shown {shown_gate:.6f} == committed {com:.6f}")
        check(p.evaluate("d => RP[d] && RP[d].day === d", calm), f"late {calm} payload stored under its own key")
        click_day(p, calm)
        d = ident(p)
        check(d["sel"] == d["payload"] == d["ref"] == calm and d["ok"] == 5, f"then selecting {calm} shows {calm} with 5/5 green")

        print("[b3] splice identity: delayed splice response")
        ctx.route("**/.cache/splice_volatile_to_calm_06.json", lambda r: (time.sleep(1.5), r.continue_()))
        p.wait_for_function("() => document.querySelector('#splice').dataset.shown", timeout=20000)
        p.locator("#sp-dir button", has_text="volatile → calm").click()
        p.locator("#sp-tau button", has_text="06:00").click()
        p.locator("#sp-tau button", has_text="18:00").click()
        p.wait_for_timeout(2500)
        shown = p.evaluate("() => document.querySelector('#splice').dataset.shown")
        check(shown == "splice_volatile_to_calm_18.json", f"splice panel shows the current selection ({shown})")
        ctx.close()

        print("[b4] DPR 2: canvas logical heights stay fixed through control changes and resizes")
        ctx = br.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        p = page_with(ctx)
        p.goto(url)
        wait_day(p, dev)
        p.wait_for_function("() => document.querySelector('#splice').dataset.shown", timeout=20000)
        p.evaluate("() => { document.querySelector('#details').open = true; document.querySelector('#heads-details').open = true; }")
        p.wait_for_timeout(300)
        h0 = p.evaluate("() => [...document.querySelectorAll('canvas')].filter(c => c.id).map(c => [c.id, c.getBoundingClientRect().height])")
        for sid in ("naive_30", "off", "naive_3", "naive_100", "naive_1"):
            set_stop(p, sid)
        for day in (calm, dev, calm, med):
            click_day(p, day)
            p.wait_for_timeout(150)
        for b_ in ("volatile → calm", "calm → volatile"):
            p.locator("#sp-dir button", has_text=b_).click()
            p.wait_for_timeout(150)
        p.set_viewport_size({"width": 1280, "height": 720})
        p.wait_for_timeout(300)
        p.set_viewport_size({"width": 1440, "height": 900})
        p.wait_for_timeout(300)
        h1 = dict(p.evaluate("() => [...document.querySelectorAll('canvas')].filter(c => c.id).map(c => [c.id, c.getBoundingClientRect().height])"))
        bad = [(k, v, h1.get(k)) for k, v in h0 if abs(v - h1.get(k, -1)) > 0.5]
        check(not bad, f"{len(h0)} canvases keep their logical height" + (f" (changed: {bad})" if bad else ""))
        back = p.evaluate("() => [...document.querySelectorAll('canvas')].filter(c => c.id).every(c => c.height === Math.round(+c.dataset.h * 2))")
        check(back, "backing store height == logical height x 2 for every canvas")
        ctx.close()

        print("[b8] stage: replay, dial, hero readout and 22-day verdict in one 1440x900 viewport; accessible dial")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        p = page_with(ctx)
        p.goto(url)
        wait_day(p, dev)
        click_day(p, calm)
        wait_day(p, calm)
        set_stop(p, "naive_30")
        p.evaluate("() => document.querySelector('#stage').scrollIntoView()")
        r = p.evaluate("""() => { const b = s => document.querySelector(s).getBoundingClientRect();
            return {top: b('#rp').top, bottom: Math.max(b('#rp').bottom, b('#dial-verdict').bottom), range: b('#dial-range').top,
                    readout: document.querySelector('#dial-readout').innerText,
                    aria: document.querySelector('#dial-range').getAttribute('aria-label'),
                    valuetext: document.querySelector('#dial-range').getAttribute('aria-valuetext')}; }""")
        check(r["top"] >= 0 and r["bottom"] <= 900 and 0 <= r["range"] <= 900,
              f"replay canvas, dial and verdict visible together (y {r['top']:.0f}…{r['bottom']:.0f} of 900)")
        check(r["readout"].startswith("26 alarms") and calm in r["readout"], f"hero readout: {r['readout'].splitlines()[0]!r} on {calm}")
        check(bool(r["aria"]) and "1e-30" in (r["valuetext"] or ""), f"dial has aria-label and alpha value text ({r['valuetext']!r})")
        check("live = committed" in p.locator("#stage-check").inner_text(), "stage shows the live = committed check for the held-out day")
        ctx.close()

        print("[b5] layout: no horizontal overflow")
        for w, h in ((1280, 720), (1440, 900)):
            ctx = br.new_context(viewport={"width": w, "height": h})
            p = page_with(ctx)
            p.goto(url)
            wait_day(p, dev)
            sw = p.evaluate("() => [document.documentElement.scrollWidth, window.innerWidth]")
            check(sw[0] <= sw[1], f"{w}x{h}: page width {sw[0]} <= viewport {sw[1]}")
            ctx.close()

        print("[b7] provenance follows the selected policy; disclosures visible")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        p = page_with(ctx)
        p.goto(url)
        p.wait_for_selector("body[data-ready='1']", timeout=10000)
        for name, want in (("One EWMA head", "post-hoc exploratory"), ("Gate + shrinkage", "post-dev secondary"),
                           ("Regime gate", "pre-registered secondary"), ("Static", "baseline")):
            p.locator("#k-pol button", has_text=name).first.click()
            prov = p.locator("#exec-prov").inner_text()
            check(want in prov and "metric" in prov, f"fee panel, {name}: policy chip '{want}'")
        dis = p.locator("#sb-disclose").inner_text()
        check("2025-08-01" in dis and "21 clean days" in dis and "ties" in dis, "disclosure: prior exposure, clean-21, tie scoring")
        wait_day(p, dev)
        check("ties" in p.locator("#rp-showing").inner_text(), "replay states the tie rate of the shown day")
        ctx.close()

        print("[b6] failure states are visible and committed panels survive")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        ctx.route("**/.cache/replay_*.json", lambda r: r.fulfill(status=404, body="missing"))
        p = page_with(ctx)
        p.goto(url)
        p.wait_for_selector("body[data-ready='1']", timeout=10000)
        p.wait_for_function("() => document.querySelector('#rp-error') && document.querySelector('#rp-error').innerText.length > 0", timeout=20000)
        txt = p.locator("#rp-error").inner_text()
        check("fallback" in txt, f"missing replay -> visible error with fallback pointer ({txt[:60]!r}…)")
        check(p.evaluate("() => document.querySelectorAll('#sb-table tbody tr').length") >= 5, "scoreboard still rendered")
        set_stop(p, "naive_30")
        check("alarms/day over 22 held-out days" in p.locator("#dial-readout").inner_text(), "dial still works without the replay")
        ctx.close()
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        ctx.route("**/results/scoreboard.json", lambda r: r.fulfill(status=404, body="missing"))
        p = page_with(ctx)
        p.goto(url)
        p.wait_for_function("() => document.querySelector('#boot-error') && !document.querySelector('#boot-error').hidden", timeout=10000)
        check("fallback" in p.locator("#boot-error").inner_text(), "missing scoreboard -> visible boot error with fallback pointer")
        ctx.close()
        br.close()

    unexpected = [e for e in js_errors if "missing" not in e and "404" not in e]
    check(not unexpected, f"no uncaught page errors ({unexpected[:2]})")
    print()
    if FAIL:
        print(f"BROWSER STAGE FAILED: {len(FAIL)} check(s)")
        return 1
    print("BROWSER STAGE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
