// Timed rehearsal of the SCRIPT.md talk track, for a Playwright `page`, e.g. the Playwright MCP's run-code tool.
// Serve demo/ first (python3 -m http.server 8791 --bind 127.0.0.1, run inside demo/) and run demo/rehearsal/speech.py.
// Each beat: a 1 s presenter pause, then that beat's real clicks or keys in the browser, then a wait for the beat's
// speech time (macOS `say` at 150 wpm, from speech.json). The state each beat must show is asserted.
// The run-code tool has a request limit of about 3 minutes, so the run is split into segments: each call runs whole
// beats within SEGMENT_BUDGET_S and keeps its progress in the page, and the next call continues from that beat
// boundary. The clock stops only between a beat's speech and the next beat's pause, where nothing happens on screen;
// the total is the sum of the segments. Start from about:blank; call until it returns the final JSON (saved as
// demo/rehearsal/result.json, with the sha256 of the page it ran on).
async (page) => {
  const BASE = 'http://127.0.0.1:8791/';
  const PAUSE_MS = 1000, SEGMENT_BUDGET_S = 120;
  let R = await page.evaluate(() => window.__REH || null).catch(() => null);
  if (!R) {
    await page.setViewportSize({width: 1600, height: 900});
    await page.goto(BASE + 'index.html', {waitUntil: 'load'});
    const page_sha256 = await page.evaluate(async () => { const b = await (await fetch('/index.html', {cache: 'no-store'})).arrayBuffer();
      return [...new Uint8Array(await crypto.subtle.digest('SHA-256', b))].map(x => x.toString(16).padStart(2, '0')).join(''); });
    const speech = await page.evaluate(async () => (await fetch('/rehearsal/speech.json', {cache: 'no-store'})).json());
    R = {page_sha256, speech, next: 0, clock: 0, beats: [], segments: []};
  }
  const settle = () => page.evaluate(() => new Promise(res => { let last = -1, same = 0, n = 0;
    const tick = () => { const y = scrollY; same = y === last ? same + 1 : 0; last = y; if (same >= 6 || ++n > 180) res(); else requestAnimationFrame(tick); };
    requestAnimationFrame(tick); }));
  const state = () => page.evaluate(() => {
    const st = window.__P3.st;
    const inView = el => { const r = el.getBoundingClientRect(); return r.top >= -1 && r.bottom <= innerHeight + 1; };
    const pressed = k => [...document.querySelectorAll(`.seg[data-k="${k}"]`)].map(s => [...s.querySelectorAll('button[aria-pressed="true"]')].map(b => b.dataset.v).join('+'));
    const sheet = [1, 2, 3, 4].find(i => { const r = document.getElementById('sheet' + i).getBoundingClientRect(); return r.top <= innerHeight / 2 && r.bottom > innerHeight / 2; });
    return {sheet, a: st.a, p: st.p, e: st.e, iv: st.iv, ep: st.ep, src: ['SB', 'SR'].filter(s => st.show[s]).join('+'),
      pressed: {p: pressed('p'), e: pressed('e'), iv: pressed('iv'), ep: pressed('ep'), src: pressed('src')},
      stamp_in_view: inView(document.querySelector('.verdict .stamp-cant')),
      readout_in_view: inView(document.getElementById('readout')), strip_in_view: inView(document.getElementById('strip')),
      primary_in_view: inView(document.querySelector('.prim')),
      readout: document.getElementById('readout').innerText.replace(/\s+/g, ' ').trim()};
  });
  const beatActions = {
    2: async () => page.locator('.verdict .stamp-cant').scrollIntoViewIfNeeded(),
    3: async () => page.keyboard.press('2'),
    4: async () => page.keyboard.press('5'),
    5: async () => page.keyboard.press('6'),
    6: async () => page.keyboard.press('7'),
    7: async () => page.locator('.seg[data-k="iv"] button[data-v="cluster"]').first().click(),
    8: async () => { await page.locator('.seg[data-k="iv"] button[data-v="row"]').first().click(); await page.locator('#strip').scrollIntoViewIfNeeded(); },
    9: async () => page.keyboard.press('4'),
  };
  const expect = {
    1: s => s.sheet === 1,
    2: s => s.sheet === 1 && s.stamp_in_view,
    3: s => s.sheet === 2,
    4: s => s.sheet === 3 && s.p === 'W2' && s.a === 42 && s.e === 'IPW' && s.iv === 'row' && s.ep === 'E1' && s.src === 'SB+SR' && s.readout_in_view && /answers/.test(s.readout),
    5: s => s.sheet === 3 && s.p === 'W2' && s.a === 43 && s.readout_in_view && /Can.t tell/i.test(s.readout),
    6: s => s.sheet === 3 && s.p === 'D26' && s.a === 33 && s.iv === 'row' && /E1 outside by 0\.018; E2 rejects \(difference CI −0\.279 … −0\.018\)/.test(s.readout),
    7: s => s.p === 'D26' && s.a === 33 && s.iv === 'cluster' && s.pressed.iv.every(v => v === 'cluster') && /E1 inside; E2 still rejects \(difference CI −0\.290 … −0\.008\)/.test(s.readout),
    8: s => s.iv === 'row' && s.pressed.iv.every(v => v === 'row') && s.strip_in_view && s.primary_in_view,
    9: s => s.sheet === 4,
    10: s => s.sheet === 4,
  };
  const t0 = Date.now(), seg = {first_beat: R.speech.beats[R.next].beat}; let ran = 0;
  while (R.next < R.speech.beats.length) {
    const b = R.speech.beats[R.next], used = (Date.now() - t0) / 1000;
    if (ran > 0 && used + PAUSE_MS / 1000 + b.seconds + 3 > SEGMENT_BUDGET_S) break;
    const start_s = R.clock + used; let action_s = 0;
    if (beatActions[b.beat]) { await page.waitForTimeout(PAUSE_MS); const a = Date.now(); await beatActions[b.beat](); await settle(); action_s = (Date.now() - a) / 1000; }
    const s = await state();
    if (!expect[b.beat](s)) throw new Error(`beat ${b.beat}: unexpected state ${JSON.stringify(s)}`);
    await page.waitForTimeout(Math.round(b.seconds * 1000));
    R.beats.push({beat: b.beat, words: b.words, start_s: +start_s.toFixed(2), pause_s: beatActions[b.beat] ? PAUSE_MS / 1000 : 0, action_s: +action_s.toFixed(3), speech_s: b.seconds,
      state: {sheet: s.sheet, p: s.p, a: s.a, e: s.e, iv: s.iv, ep: s.ep, src: s.src}});
    R.next++; ran++;
  }
  const dur = (Date.now() - t0) / 1000;
  R.segments.push({beats: `${seg.first_beat}–${R.beats[R.beats.length - 1].beat}`, seconds: +dur.toFixed(2)});
  R.clock += dur;
  if (R.next < R.speech.beats.length) {
    await page.evaluate(r => { window.__REH = r; }, R);
    return `segment ${R.segments.length} done (beats ${R.segments[R.segments.length - 1].beats}, ${dur.toFixed(1)} s); call again to continue`;
  }
  const out = JSON.stringify({measured_at: new Date().toISOString(), page_sha256: R.page_sha256, browser: 'Chromium (Playwright)', viewport: '1600x900',
    method: `real clicks and keys in the browser; ${PAUSE_MS / 1000} s presenter pause before each action; speech = macOS say at ${R.speech.rate_wpm} wpm (default voice), waited in real time; `
      + `run in ${R.segments.length} segment(s) to fit the tool's request limit, the clock stopping only at beat boundaries`,
    spoken_words: R.speech.total_words, speech_s: R.speech.total_speech_seconds, total_s: +R.clock.toFixed(2), segments: R.segments, beats: R.beats}, null, 1);
  await page.evaluate(r => { window.__REH = null; window.__RESULT = r; }, out);  // save it with an evaluate call: () => JSON.parse(window.__RESULT)
  return out;
}
