// Captures demo/fallback/*.png along the SCRIPT.md path, through the page's normal controls (clicks, keys, scrolling;
// no deep links), for a Playwright `page` (e.g. the Playwright MCP's run-code tool, run from the repository root).
// Serve demo/ first: python3 -m http.server 8791 --bind 127.0.0.1 (inside demo/).
// Each file name encodes the state it must show (sheet, period, α, estimator, interval, endpoint, preset). The state
// actually on screen is checked against the name before the screenshot is saved; the recorded states are returned as
// JSON and saved as demo/fallback/states.json (with the sha256 of the index.html they show), which demo/smoke_check.py
// checks against the files and the committed page.
async (page) => {
  const BASE = 'http://127.0.0.1:8791/';
  const OUT = 'perceptron-p03-off-policy-eval/demo/fallback/';
  await page.setViewportSize({width: 1600, height: 900});
  await page.goto(BASE + 'index.html', {waitUntil: 'load'});
  const page_sha256 = await page.evaluate(async () => { const b = await (await fetch('/index.html', {cache: 'no-store'})).arrayBuffer();
    return [...new Uint8Array(await crypto.subtle.digest('SHA-256', b))].map(x => x.toString(16).padStart(2, '0')).join(''); });
  const settle = async () => {
    await page.evaluate(() => new Promise(res => { let last = -1, same = 0, n = 0;
      const tick = () => { const y = scrollY; same = y === last ? same + 1 : 0; last = y; if (same >= 6 || ++n > 240) res(); else requestAnimationFrame(tick); };
      requestAnimationFrame(tick); }));
    await page.waitForTimeout(1200);
  };
  const key = k => page.keyboard.press(k);
  const click = sel => page.locator(sel).first().click();
  const into = sel => page.locator(sel).first().scrollIntoViewIfNeeded();
  const shots = [
    ['01_b1_sheet1_top', 'page opened at the top of sheet 1', []],
    ['02_b2_sheet1_cant_tell', 'scroll down to the CAN\'T TELL stamp', [() => into('.verdict .stamp-cant')]],
    ['03_b3_sheet2', 'press 2', [() => key('2')]],
    ['04_b4_preset5_W2_a0.42_IPS_row_E1', 'press 5', [() => key('5')]],
    ['05_b5_preset6_W2_a0.43_IPS_row_E1', 'press 6', [() => key('6')]],
    ['06_b6_preset7_Nov26_a0.33_IPS_row_E1', 'press 7', [() => key('7')]],
    ['07_b7_Nov26_a0.33_IPS_cluster_E1', 'click hour-cluster', [() => click('.seg[data-k="iv"] button[data-v="cluster"]')]],
    ['08_b8_Nov26_a0.33_IPS_row_E1_strip', 'click row-level; scroll down to the strip', [() => click('.seg[data-k="iv"] button[data-v="row"]'), () => into('#strip')]],
    ['09_b9_sheet4', 'press 4', [() => key('4')]],
    ['10_qa_Nov25_a0.05_IPS_row_E1_z_refusal', 'press 3 twice; click Nov 25; Shift+← five times, ← three times',
      [() => key('3'), settle, () => key('3'), settle, () => click('#periods button[data-v="D25"]'),
       ...Array(5).fill(() => key('Shift+ArrowLeft')), ...Array(3).fill(() => key('ArrowLeft'))]],
    ['11_qa_Nov26_a0.33_IPS_cluster_E2_strip', 'press 7, c, e; scroll down to the strip', [() => key('7'), settle, () => key('c'), () => key('e'), () => into('#strip')]],
  ];
  const expectFromName = name => {
    const t = name.split('_'), x = {};
    for (const s of t) {
      let m;
      if ((m = s.match(/^sheet([1-4])$/))) x.sheet = Number(m[1]);
      else if ((m = s.match(/^preset([5-7])$/))) x.preset = String(Number(m[1]) - 4);
      else if ((m = s.match(/^Nov(2[4-6])$/))) x.p = 'D' + m[1];
      else if (/^W[12]?$/.test(s)) x.p = s;
      else if ((m = s.match(/^a(\d\.\d\d)$/))) x.a = Math.round(100 * Number(m[1]));
      else if (s === 'IPS' || s === 'SNIPS') x.e = s === 'IPS' ? 'IPW' : 'SNIPW';
      else if (s === 'row' || s === 'cluster') x.iv = s;
      else if (s === 'E1' || s === 'E2') x.ep = s;
      else if (s === 'strip') x.strip = true;
    }
    if (x.p) x.sheet = 3;
    return x;
  };
  const read = () => page.evaluate(() => {
    const st = window.__P3.st;
    const vis = el => { const r = el.getBoundingClientRect(); return r.top >= -1 && r.bottom <= innerHeight + 1; };
    const sheet = [1, 2, 3, 4].find(i => { const r = document.getElementById('sheet' + i).getBoundingClientRect(); return r.top <= innerHeight / 2 && r.bottom > innerHeight / 2; });
    const pressed = {};
    document.querySelectorAll('.seg[data-k]').forEach(s => { (pressed[s.dataset.k] ||= []).push([...s.querySelectorAll('button[aria-pressed="true"]')].map(b => b.dataset.v).join('+')); });
    const ro = document.getElementById('readout');
    const sb = ro.querySelector('.row.sb');
    return {sheet, scrollY: Math.round(scrollY), p: st.p, a: st.a, e: st.e, iv: st.iv, ep: st.ep, src: ['SB', 'SR'].filter(s => st.show[s]).join('+'),
      alpha_label: document.getElementById('alpha-val').textContent, pressed,
      presets: [...document.querySelectorAll('#presets button[aria-pressed="true"]')].map(b => b.dataset.preset),
      in_view: {stamp: vis(document.querySelector('.verdict .stamp-cant')), readout: vis(ro), strip: vis(document.getElementById('strip')), primary: vis(document.querySelector('.prim'))},
      readout_bts: sb ? sb.innerText.replace(/\s+/g, ' ').trim() : ''};
  });
  const records = [];
  for (const [name, did, acts] of shots) {
    for (const a of acts) await a();
    await settle();
    const s = await read(), x = expectFromName(name), bad = [];
    for (const k of ['sheet', 'p', 'a', 'e', 'iv', 'ep']) if (k in x && s[k] !== x[k]) bad.push(`${k}: ${s[k]} ≠ ${x[k]}`);
    if (x.sheet === 3) {
      for (const k of ['p', 'e', 'iv', 'ep']) if (!s.pressed[k].every(v => v === s[k])) bad.push(`pressed ${k}: ${s.pressed[k]} ≠ ${s[k]}`);
      if (s.alpha_label !== `α = ${(s.a / 100).toFixed(2)}`) bad.push(`alpha label ${s.alpha_label}`);
      if (!s.readout_bts.includes('BTS')) bad.push('BTS readout missing');
    }
    if ('preset' in x && !(s.presets.length === 1 && s.presets[0] === x.preset)) bad.push(`preset ${s.presets} ≠ ${x.preset}`);
    if (x.strip && !s.in_view.strip) bad.push('strip not in view');
    if (name.startsWith('02_') && !s.in_view.stamp) bad.push('stamp not in view');
    if (/^0[4-7]_/.test(name) && !s.in_view.readout) bad.push('readout not in view');
    if (bad.length) throw new Error(`${name}: ${bad.join('; ')}`);
    await page.screenshot({path: OUT + name + '.png'});
    records.push({file: name + '.png', did, state: {sheet: s.sheet, p: s.p, a: s.a, e: s.e, iv: s.iv, ep: s.ep, src: s.src, presets: s.presets,
      alpha_label: s.alpha_label, pressed: s.pressed, in_view: s.in_view}, readout_bts: x.sheet === 3 ? s.readout_bts : ''});
  }
  const out = JSON.stringify({captured_at: new Date().toISOString(), page_sha256, viewport: '1600x900', browser: 'Chromium (Playwright)',
    method: 'clicks, keys and scrolling only, in talk-track order; state checked against each file name before saving', shots: records});
  await page.evaluate(r => { window.__RESULT = r; }, out);  // save it with an evaluate call: () => JSON.parse(window.__RESULT)
  return out;
}
