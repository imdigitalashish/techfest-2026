/* P1 demo page. Committed numbers are read from window.P1 (demo/web/data.js, exported from eval/results by
   demo/export_replay.py) by key, and every one is printed next to its key. Live numbers arrive as events from
   demo/live_engine.py through demo/server.py; RECORDED numbers replay demo/fallback/recorded_live_s0.jsonl. */
(() => {
  'use strict';
  const D = window.P1;
  const STRATS = D.strategies;
  const DOMS = D.domains;
  const DEV = D.devices;
  const FEDS = ['fedavg_ab_homo', 'anchor_full'];
  const MINUS = '\u2212';
  const DOMNAME = { wiki: 'Wikipedia', pycode: 'Python code', cheaders: 'C/C++ headers', readmes: 'READMEs', manpages: 'man pages' };
  const DOMSHORT = { wiki: 'Wikipedia', pycode: 'Python', cheaders: 'C headers', readmes: 'READMEs', manpages: 'man pages' };
  const DEVBY = Object.fromEntries(DEV.map((d) => [d.id, d]));
  const COL = {
    fedavg_ab_homo: ['var(--starter)', 'var(--starter-fill)'], ffa_lora: ['var(--ffa)', 'var(--ffa-fill)'],
    flexlora: ['var(--flex)', 'var(--flex-fill)'], anchor_full: ['var(--anchor)', 'var(--anchor-fill)'],
  };
  const CCLASS = { fedavg_ab_homo: 'c-starter', ffa_lora: 'c-ffa', flexlora: 'c-flex', anchor_full: 'c-anchor' };
  const NS = 'http://www.w3.org/2000/svg';
  const $ = (s) => document.querySelector(s);

  // ---- tiny DOM helpers ------------------------------------------------------------------------------
  function el(tag, attrs, ...kids) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) if (v != null) e.setAttribute(k, v);
    for (const k of kids.flat()) if (k != null) e.append(k);
    return e;
  }
  function h(tag, attrs, ...kids) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null) continue;
      if (k === 'class') e.className = v; else if (k === 'html') e.innerHTML = v; else e.setAttribute(k, v);
    }
    for (const k of kids.flat()) if (k != null) e.append(k);
    return e;
  }
  const txt = (x, y, s, a) => el('text', Object.assign({ x, y }, a || {}), s);
  function fmt(v, nd = 3, signed = true) {
    if (v == null || !Number.isFinite(v)) return '–';
    const s = Math.abs(v).toFixed(nd);
    if (Number(s) === 0) return s;
    return (v < 0 ? MINUS : signed ? '+' : '') + s;
  }
  const ci = (lo, hi, nd = 3) => `[${fmt(lo, nd)}, ${fmt(hi, nd)}]`;

  // ---- committed numbers, always by key --------------------------------------------------------------
  function K(key) {
    const v = key in D.canonical ? D.canonical[key] : D.dropout_canonical[key];
    if (v === undefined) throw new Error('missing committed key ' + key);
    return v;
  }
  const fileOf = (key) => (key in D.canonical ? 'v2_canonical.json' : 'v2_dropout_canonical.json');
  function compressKeys(keys) {
    if (keys.length === 1) return keys[0];
    let p = keys[0];
    for (const k of keys) while (!k.startsWith(p)) p = p.slice(0, -1);
    p = p.slice(0, Math.max(p.lastIndexOf('.'), p.lastIndexOf('_')) + 1);
    return p ? `${p}{${keys.map((k) => k.slice(p.length)).join(',')}}` : keys.join(' / ');
  }
  const keyTag = (...keys) => h('span', { class: 'key', title: keys.join('\n') }, fileOf(keys[0]) + ' · ' + compressKeys(keys));
  // end labels of line charts: keep them at least `gap` apart vertically
  function spread(items, gap) {
    items.sort((a, b) => a.y - b.y);
    for (let i = 1; i < items.length; i += 1) if (items[i].y - items[i - 1].y < gap) items[i].y = items[i - 1].y + gap;
    return items;
  }

  function scale(d0, d1, r0, r1) { const k = (r1 - r0) / (d1 - d0); return (v) => r0 + (v - d0) * k; }
  function niceStep(range, n = 6) {
    const raw = range / n, p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    return (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p;
  }
  function yAxis(g, y, lo, hi, x0, x1, step, fmtTick) {
    for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) {
      const yy = y(v);
      g.append(el('line', { x1: x0, x2: x1, y1: yy, y2: yy, style: `stroke:${Math.abs(v) < 1e-9 ? 'var(--ink)' : 'var(--rule2)'};stroke-width:${Math.abs(v) < 1e-9 ? 1.6 : 1}` }));
      g.append(txt(x0 - 8, yy + 4, fmtTick(v), { 'text-anchor': 'end', 'font-size': 13 }));
    }
  }

  // ======================================================================================================
  // 1 · committed runs
  // ======================================================================================================
  function drawGains() {
    const host = $('#chart-gains');
    const W = 900, H = 430, m = { l: 62, r: 92, t: 18, b: 64 };
    const vals = [];
    for (const s of STRATS) for (const d of DOMS) vals.push(K(`dropout.${s}.${d}.gain_lo_bonf`), K(`dropout.${s}.${d}.gain_hi_bonf`));
    const lo = Math.min(0, ...vals) * 1.08, hi = Math.max(0, ...vals) * 1.08;
    const y = scale(lo, hi, H - m.b, m.t);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}` });
    const g = el('g');
    yAxis(g, y, lo, hi, m.l, W - m.r, niceStep(hi - lo), (v) => fmt(v, 1));
    g.append(txt(W - m.r + 6, y(0) + 4, 'untuned', { 'font-size': 13, 'font-weight': 700, style: 'fill:var(--ink)' }));
    g.append(txt(W - m.r + 6, y(0) - 12, '↑ better', { 'font-size': 12 }));
    g.append(txt(W - m.r + 6, y(0) + 22, '↓ forgot', { 'font-size': 12 }));
    const gw = (W - m.l - m.r) / DOMS.length, bw = gw / (STRATS.length + 1.4);
    DOMS.forEach((d, gi) => {
      const gx = m.l + gi * gw + bw * 0.7;
      STRATS.forEach((s, si) => {
        const v = K(`dropout.${s}.${d}.gain_mean`), l = K(`dropout.${s}.${d}.gain_lo_bonf`), u = K(`dropout.${s}.${d}.gain_hi_bonf`);
        const x = gx + si * bw;
        const y0 = y(0), yv = y(v);
        const r = el('rect', { x: x + 2, y: Math.min(y0, yv), width: bw - 4, height: Math.max(1, Math.abs(yv - y0)), rx: 2, style: `fill:${COL[s][1]}` });
        r.append(el('title', {}, `${D.short[s]} · ${DOMNAME[d]}: ${fmt(v)} [${fmt(l)}, ${fmt(u)}] (Bonferroni 95%)\nv2_canonical.json · dropout.${s}.${d}.gain_mean / gain_lo_bonf / gain_hi_bonf`));
        g.append(r);
        const cx = x + bw / 2;
        g.append(el('line', { x1: cx, x2: cx, y1: y(l), y2: y(u), style: `stroke:${COL[s][0]};stroke-width:1.6` }));
        g.append(el('line', { x1: cx - 4, x2: cx + 4, y1: y(l), y2: y(l), style: `stroke:${COL[s][0]};stroke-width:1.6` }));
        g.append(el('line', { x1: cx - 4, x2: cx + 4, y1: y(u), y2: y(u), style: `stroke:${COL[s][0]};stroke-width:1.6` }));
        if (s === 'anchor_full' || s === 'fedavg_ab_homo') {
          const above = v >= 0;
          g.append(txt(cx, above ? y(u) - 6 : y(l) + 16, fmt(v), { 'text-anchor': 'middle', 'font-size': 13.5, 'font-weight': 700, style: `fill:${COL[s][0]}` }));
        }
      });
      const dev = DEV.find((x) => x.domain === d);
      g.append(txt(m.l + gi * gw + gw / 2, H - m.b + 22, DOMNAME[d], { 'text-anchor': 'middle', 'font-size': 15, 'font-weight': 700, style: 'fill:var(--ink)' }));
      g.append(txt(m.l + gi * gw + gw / 2, H - m.b + 41, dev.cls + (d === 'wiki' ? ' · 8× data' : ''), { 'text-anchor': 'middle', 'font-size': 13.5 }));
    });
    g.append(txt(16, m.t + (H - m.t - m.b) / 2, 'nats/token', { transform: `rotate(-90 16 ${m.t + (H - m.t - m.b) / 2})`, 'text-anchor': 'middle', 'font-size': 12 }));
    svg.append(g);
    host.replaceChildren(svg);
    $('#legend-real').replaceChildren(...STRATS.map((s) => h('span', {}, h('i', { style: `background:${COL[s][1]}` }), D.labels[s])));
  }

  function drawLedger() {
    const box = $('#ledger');
    const rows = [['fedavg_ab_homo', 'spike_vs_fedavg_ab_homo'], ['ffa_lora', 'spike_vs_ffa_lora'], ['flexlora', 'spike_vs_flexlora']];
    const b1 = h('div', { class: 'ledger-block' }, h('h4', {}, 'AnchorLoRA minus each baseline: mean loss over the 5 domains, paired by seed, 95% CI (negative = AnchorLoRA lower)'));
    for (const [s, k] of rows) {
      const ks = [`dropout.${k}.macro_mean`, `dropout.${k}.macro_lo`, `dropout.${k}.macro_hi`];
      b1.append(h('div', { class: 'lrow' }, h('span', { class: 'who ' + CCLASS[s] }, `vs ${D.short[s]}`),
        h('span', { class: 'val' }, h('span', { class: 'big c-anchor' }, fmt(K(ks[0]))), ' ', h('span', { class: 'ci' }, ci(K(ks[1]), K(ks[2])))), keyTag(...ks)));
    }
    b1.append(h('p', { class: 'note' }, `Mean domain loss: untuned ${fmt(K('base.macro'), 3, false)} · AnchorLoRA ${fmt(K('dropout.anchor_full.macro_mean'), 3, false)} · starter ${fmt(K('dropout.fedavg_ab_homo.macro_mean'), 3, false)}`,
      keyTag('base.macro', 'dropout.anchor_full.macro_mean', 'dropout.fedavg_ab_homo.macro_mean')));

    const cells2 = h('div', { class: 'cells' });
    for (const s of ['anchor_full', 'fedavg_ab_homo', 'ffa_lora', 'flexlora']) {
      const kp = `dropout.${s}.domains_ci_pos_bonf`;
      const neg = DOMS.filter((d) => K(`dropout.${s}.${d}.gain_hi_bonf`) < 0).length;
      cells2.append(h('div', { class: 'cell', title: `${fileOf(kp)} · ${kp}\nworse: count of dropout.${s}.<domain>.gain_hi_bonf < 0` },
        h('span', { class: 'who ' + CCLASS[s] }, D.short[s]), h('span', { class: 'big' }, `${pos5(K(kp))}`), h('span', { class: 'sub2' }, `better; ${neg} worse`)));
    }
    const b2 = h('div', { class: 'ledger-block' }, h('h4', {}, 'Domains better / worse than untuned (Bonferroni 95% excludes 0)'), cells2,
      h('span', { class: 'key' }, 'v2_canonical.json · dropout.<strategy>.domains_ci_pos_bonf; worse = count of dropout.<strategy>.<domain>.gain_hi_bonf < 0'));

    const cells3 = h('div', { class: 'cells' });
    for (const s of ['fedavg_ab_homo', 'ffa_lora', 'flexlora', 'anchor_full']) {
      const k = `dropout.${s}.c0_norm_mean`;
      cells3.append(h('div', { class: 'cell', title: `${fileOf(k)} · ${k}` }, h('span', { class: 'who ' + CCLASS[s] }, D.short[s]), h('span', { class: 'big' }, fmt(K(k), 2, false))));
    }
    const b3 = h('div', { class: 'ledger-block' }, h('h4', {}, "Workstation's share of update magnitude: round-and-seed mean (norm share; a magnitude diagnostic, not a bound; equal share 0.20)"), cells3,
      h('span', { class: 'key' }, 'v2_canonical.json · dropout.<strategy>.c0_norm_mean'));
    box.replaceChildren(b1, b2, b3);
  }
  const pos5 = (v) => `${v}/5`;

  // ======================================================================================================
  // 2 · committed outage
  // ======================================================================================================
  const OUT = D.replay.outage;
  const GLYPH = { o: '●', p: '◐', x: '✕', '-': '–' };
  const GCLS = { o: 'g-o', p: 'g-p', x: 'g-x', '-': 'g-off' };
  let stripNow = 0, stripTimer = null;
  function manpSeries(s) {
    const base = D.untuned.manpages;
    const perSeed = D.seeds.map((seed) => {
      const pts = [[0, 0]];
      for (const r of D.replay.runs[s][String(seed)].rounds) if (r.eval) pts.push([r.round, base - r.eval.manpages]);
      return pts;
    });
    const mean = perSeed[0].map((p, i) => [p[0], perSeed.reduce((a, q) => a + q[i][1], 0) / perSeed.length]);
    return { perSeed, mean };
  }
  function drawOutageChart() {
    const host = $('#chart-outage');
    const W = 900, H = 372, m = { l: 62, r: 120, t: 26, b: 44 };
    const series = Object.fromEntries(STRATS.map((s) => [s, manpSeries(s)]));
    const all = STRATS.flatMap((s) => series[s].perSeed.flatMap((p) => p.map((q) => q[1])));
    const lo = Math.min(...all) * 1.12, hi = Math.max(0.02, ...all) * 1.6;
    const x = scale(0, 12, m.l, W - m.r), y = scale(lo, hi, H - m.b, m.t);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}` });
    svg.append(el('rect', { x: x(OUT.rounds[0] - 0.5), y: m.t, width: x(OUT.rounds.at(-1) + 0.5) - x(OUT.rounds[0] - 0.5), height: H - m.b - m.t, style: 'fill:#ece6f6' }));
    svg.append(txt(x((OUT.rounds[0] + OUT.rounds.at(-1)) / 2), m.t - 8, `tablet offline, rounds ${OUT.rounds[0]}–${OUT.rounds.at(-1)} (forced outage)`, { 'text-anchor': 'middle', 'font-size': 12.5, 'font-weight': 700, style: 'fill:var(--sim)' }));
    const g = el('g');
    yAxis(g, y, lo, hi, m.l, W - m.r, niceStep(hi - lo, 5), (v) => fmt(v, 2));
    for (let r = 0; r <= 12; r += 1) {
      g.append(txt(x(r), H - m.b + 18, String(r), { 'text-anchor': 'middle', 'font-size': 12, 'font-weight': [3, 6, 9, 12].includes(r) ? 700 : 400 }));
    }
    g.append(txt(x(6), H - 6, 'round (evaluated at 3, 6, 9, 12)', { 'text-anchor': 'middle', 'font-size': 12 }));
    g.append(txt(W - m.r + 8, y(0) + 4, 'untuned', { 'font-size': 13, 'font-weight': 700, style: 'fill:var(--ink)' }));
    svg.append(g);
    if (stripNow) {
      svg.append(el('line', { x1: x(stripNow), x2: x(stripNow), y1: m.t, y2: H - m.b, style: 'stroke:var(--ink);stroke-width:2;stroke-dasharray:3 3' }));
      svg.append(txt(x(stripNow) + 5, H - m.b - 6, `round ${stripNow}`, { 'font-size': 12, 'font-weight': 700, style: 'fill:var(--ink)' }));
    }
    const ends = [];
    for (const s of STRATS) {
      for (const pts of series[s].perSeed) for (const [r, v] of pts.slice(1)) svg.append(el('circle', { cx: x(r), cy: y(v), r: 3.2, style: `fill:${COL[s][1]};opacity:0.55` }));
      const d = series[s].mean.map(([r, v], i) => `${i ? 'L' : 'M'}${x(r).toFixed(1)},${y(v).toFixed(1)}`).join('');
      svg.append(el('path', { d, style: `fill:none;stroke:${COL[s][0]};stroke-width:3;stroke-linejoin:round` }));
      const [lr, lv] = series[s].mean.at(-1);
      ends.push({ s, x: x(lr) + 8, y: y(lv) + 4, v: lv });
    }
    for (const e of spread(ends, 15)) svg.append(txt(e.x, e.y, `${D.short[e.s]} ${fmt(e.v)}`, { 'font-size': 13, 'font-weight': 700, style: `fill:${COL[e.s][0]}` }));
    host.replaceChildren(svg);
    $('#legend-outage').replaceChildren(...STRATS.map((s) => h('span', {}, h('i', { class: 'line', style: `background:${COL[s][0]}` }), D.labels[s])),
      h('span', {}, '↑ better than untuned, ↓ worse'));
  }
  function drawOutageLedgers() {
    const pk = h('div', {});
    for (const s of ['fedavg_ab_homo', 'flexlora', 'ffa_lora', 'anchor_full']) {
      const a = `dropout.${s}.outage_peak_rise_mean`, b = `dropout.${s}.outage_peak_rise_max`;
      pk.append(h('div', { class: 'lrow three' }, h('span', { class: 'who ' + CCLASS[s] }, D.short[s]),
        h('span', { class: 'val' }, h('span', { class: 'big' }, fmt(K(a))), h('span', { class: 'ci' }, ' mean')),
        h('span', { class: 'val' }, fmt(K(b)), h('span', { class: 'ci' }, ' worst seed')), keyTag(a, b)));
    }
    const amax = K('dropout.anchor_full.outage_peak_rise_max');
    $('#peaks').replaceChildren(h('p', { class: 'note' }, 'Highest man-page loss at any evaluated round, trained − untuned: positive = worse (the opposite sign to the curve). Mean of 5 seeds and the worst seed.'), pk,
      h('p', { class: 'note' }, amax < 0
        ? `AnchorLoRA's worst seed peaks at ${fmt(amax)}: below the untuned model at every evaluated round in every seed.`
        : `AnchorLoRA's worst seed peaks at ${fmt(amax)}.`));
    const ur = h('table', { class: 'tbl' }, h('tr', {}, h('th', {}, 'device'), h('th', { class: 'num c-starter' }, 'Starter'), h('th', { class: 'num c-anchor' }, 'AnchorLoRA')));
    for (const d of DEV) {
      const cell = (s) => {
        const u = K(`dropout.${s}.${d.id}.rounds_used_mean`), mm = K(`dropout.${s}.${d.id}.rounds_memory_mean`);
        return h('td', { class: 'num', title: `v2_dropout_canonical.json · dropout.${s}.${d.id}.rounds_used_mean / rounds_memory_mean` }, fmt(u, 1, false), mm ? h('span', { class: 'ci' }, ` + ${fmt(mm, 1, false)} memory`) : null);
      };
      ur.append(h('tr', {}, h('td', {}, d.cls), cell('fedavg_ab_homo'), cell('anchor_full')));
    }
    $('#usedrounds').replaceChildren(h('h3', {}, "Rounds each device's work entered the aggregate"),
      h('p', { class: 'note' }, 'Out of 12, mean over seeds; "memory" = rounds its last update was reused while it was absent (not fresh computation).'), ur,
      h('span', { class: 'key' }, 'v2_dropout_canonical.json · dropout.<strategy>.<device>.rounds_used_mean / rounds_memory_mean'));
  }
  function stripCell(r, di, devId) {
    const st = r.status[di];
    const mem = r.memory.includes(devId);
    const [done, plan] = r.steps[di];
    const cls = ['c', mem ? 'g-m' : GCLS[st], stripNow === r.round ? 'now' : '', devId === OUT.device && OUT.rounds.includes(r.round) ? 'out' : ''].join(' ');
    const title = mem ? 'absent; its last update was reused (memory)' : { o: `full work ${done}/${plan} steps`, p: `partial work kept ${done}/${plan} steps`, x: 'cut off by the deadline, discarded', '-': 'offline' }[st];
    return h('td', { class: cls, title: `${DEVBY[devId].cls}, round ${r.round}: ${title}` }, mem ? '↺' : GLYPH[st]);
  }
  const roundHeads = () => Array.from({ length: 12 }, (_, i) => h('th', { class: 'r' + (stripNow === i + 1 ? ' now' : '') }, `r${i + 1}`));
  function drawTabletStrip() {
    const seed = $('#strip-seed').value;
    const di = DEV.findIndex((d) => d.id === OUT.device);
    const t = h('table', { class: 'rs compact' }, h('tr', {}, h('th', {}, ''), ...roundHeads()));
    for (const s of ['fedavg_ab_homo', 'anchor_full']) {
      t.append(h('tr', {}, h('th', { class: CCLASS[s] }, D.short[s]), ...D.replay.runs[s][seed].rounds.map((r) => stripCell(r, di, OUT.device))));
    }
    $('#tabletstrip').replaceChildren(t);
  }
  function drawStrip() {
    const seed = $('#strip-seed').value;
    const t = h('table', { class: 'rs' }, h('tr', {}, h('th', {}, ''), ...roundHeads()));
    for (const s of ['fedavg_ab_homo', 'anchor_full']) {
      const rounds = D.replay.runs[s][seed].rounds;
      t.append(h('tr', { class: 'grp' }, h('td', { class: CCLASS[s], colspan: 13 }, D.labels[s])));
      DEV.forEach((d, di) => t.append(h('tr', {}, h('th', {}, d.cls), ...rounds.map((r) => stripCell(r, di, d.id)))));
      t.append(h('tr', {}, h('th', { class: 'share' }, 'workstation share'), ...rounds.map((r) => h('td', { class: 'share', style: 'text-align:center' }, r.norm_share_c0 == null ? '–' : r.norm_share_c0.toFixed(2)))));
    }
    $('#roundstrip').replaceChildren(t);
    $('#strip-src').replaceChildren('"workstation share": its norm share of that round\'s update (magnitude diagnostic). Source ',
      h('code', {}, D.replay.runs.fedavg_ab_homo[seed].file), ', ', h('code', {}, D.replay.runs.anchor_full[seed].file));
  }
  function drawOutageStage() { drawOutageChart(); drawTabletStrip(); drawStrip(); }
  function playStrip() {
    if (stripTimer) { clearInterval(stripTimer); stripTimer = null; stripNow = 0; $('#strip-play').textContent = 'Play rounds'; drawOutageStage(); return; }
    stripNow = 0;
    $('#strip-play').textContent = 'Stop';
    stripTimer = setInterval(() => {
      stripNow += 1;
      if (stripNow > 12) { clearInterval(stripTimer); stripTimer = null; stripNow = 0; $('#strip-play').textContent = 'Play rounds'; }
      drawOutageStage();
    }, 750);
  }

  // ======================================================================================================
  // 3 · live: state
  // ======================================================================================================
  const VAL = D.validation;
  const REC = D.recorded;
  const SELFTEST = new URLSearchParams(location.search).has('selftest');
  const NUMW = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];
  function newState(kind) {
    return { kind, runId: null, seed: 0, rounds: 6, phase: 'idle', untuned: null, identical: null,
      recs: { fedavg_ab_homo: {}, anchor_full: {} }, out: new Set(), pending: {}, outRounds: {}, current: 0,
      training: null, mem: null, roundWall: {}, error: null, prov: null, loadS: null, done: false,
      pauseReq: false, holding: false, staged: false };
  }
  const ST = { live: newState('live'), recorded: newState('recorded') };
  let view = 'live'; // which run the live tab displays: the real process ('live') or the RECORDED file
  let avail = { checked: false, ok: false, why: [], memory: null };
  const proc = { running: false, state: 'idle', runId: null, exited: new Set() }; // the real engine process
  let busy = false; // a stop request is in flight
  let notice = null; // last refused command or stop failure, shown on the stage band
  const S = () => ST[view];

  function onEvent(st, ev) {
    switch (ev.ev) {
      case 'server_start': Object.assign(st, newState(st.kind), { runId: ev.run_id, seed: ev.seed, phase: 'starting' }); break;
      case 'hello': st.seed = ev.seed; st.rounds = ev.rounds; st.prov = ev.provenance; break;
      case 'loading': st.phase = 'loading'; break;
      case 'loaded': st.phase = 'loaded'; st.loadS = ev.load_s; break;
      case 'untuned': st.untuned = ev.per_domain; st.identical = ev.identical_start; st.phase = 'ready'; break;
      case 'cmd_ack':
        if (ev.cmd === 'unplug' || ev.cmd === 'replug') st.pending[ev.device] = { cmd: ev.cmd, eff: ev.effective_round };
        break;
      case 'round_start':
        st.current = ev.round; st.phase = 'round'; st.holding = false; st.out = new Set(ev.unplugged);
        for (const d of ev.unplugged) (st.outRounds[d] = st.outRounds[d] || []).push(ev.round);
        for (const [d, p] of Object.entries(st.pending)) if (p.eff <= ev.round) delete st.pending[d];
        break;
      case 'device_start': st.training = { fed: ev.fed, device: ev.device, steps: ev.steps, planned: ev.planned }; break;
      case 'device_done': st.training = null; break;
      case 'round': st.recs[ev.fed][ev.round] = ev; break;
      case 'round_end': st.roundWall[ev.round] = ev.wall_s; st.training = null; break;
      case 'paused': st.pauseReq = true; break;
      case 'stage_hold': st.holding = true; st.staged = !!ev.staged; break;
      case 'resumed': st.pauseReq = false; st.holding = false; break;
      case 'memory': st.mem = ev.paused ? ev : null; break;
      case 'done': st.done = true; st.phase = 'done'; st.holding = false; break;
      case 'engine_exit':
        if (!st.done) st.phase = ev.stopped ? 'stopped' : (ev.code === 0 ? 'done' : 'failed');
        st.training = null; st.mem = null; st.holding = false; st.pauseReq = false;
        break;
      case 'error': st.error = ev.message; break;
      default: break;
    }
  }
  function onLiveEvent(ev) {
    if (ev.ev === 'server_start') { proc.running = true; proc.state = 'running'; proc.runId = ev.run_id; notice = null; }
    if (ev.ev === 'engine_exit') { proc.running = false; proc.state = ev.stopped ? 'stopped' : (ev.code === 0 ? 'finished' : 'failed'); proc.exited.add(ev.run_id); }
    onEvent(ST.live, ev);
  }
  function applyStatus(s) {
    avail = { checked: true, ok: !!s.live_available, why: s.why || [], memory: s.memory_level };
    if (s.running && !proc.exited.has(s.run_id)) { proc.running = true; proc.runId = s.run_id; } else if (!s.running) proc.running = false;
    proc.state = s.state || proc.state;
    if (s.running && s.memory && !ST.live.mem) ST.live.mem = s.memory;
    if (!s.running) ST.live.mem = null;
  }

  // ---- history helpers ---------------------------------------------------------------------------------
  function pairedRound(st) { // last round finished by BOTH federations
    let pr = 0;
    for (const r of Object.keys(st.recs.anchor_full).map(Number)) if (st.recs.fedavg_ab_homo[r] && r > pr) pr = r;
    return pr;
  }
  function intervention(st) { // 'none' | 'tablet' (the pre-validated tablet-only outage from round 2) | 'custom'
    const devs = new Set([...Object.keys(st.outRounds), ...Object.keys(st.pending)]);
    if (!devs.size) return 'none';
    if (devs.size !== 1 || !devs.has('c4')) return 'custom';
    const rs = st.outRounds.c4 || [];
    const p = st.pending.c4;
    if (p && !(p.cmd === 'unplug' && p.eff === 2 && !rs.length)) return 'custom';
    if (rs.length && !(rs[0] === 2 && rs.every((r, i) => r === 2 + i) && rs.at(-1) === st.current)) return 'custom';
    return 'tablet';
  }
  function histText(st) {
    const parts = Object.entries(st.outRounds).map(([d, rs]) => `${DEVBY[d].cls} out in round${rs.length > 1 ? 's' : ''} ${rs.length > 1 ? `${rs[0]}–${rs.at(-1)}` : rs[0]}`);
    for (const [d, p] of Object.entries(st.pending)) parts.push(`${DEVBY[d].cls} ${p.cmd === 'unplug' ? 'out' : 'back'} from round ${p.eff}`);
    return parts.join(', ');
  }
  function lastFresh(st, dev, upto) { // last round AnchorLoRA received fresh work from `dev`
    let k = 0;
    for (let r = 1; r <= upto; r += 1) { const rec = st.recs.anchor_full[r]; if (rec && rec.devices[dev] && rec.devices[dev].state === 'fresh') k = r; }
    return k;
  }
  function projection(st, dev, from) { // what AnchorLoRA's memory will do if `dev` is out from round `from`; from the actual history
    const name = DEVBY[dev].cls, R = st.rounds, k = lastFresh(st, dev, pairedRound(st));
    if (!k) return `AnchorLoRA has no update from the ${name} yet: nothing to reuse.`;
    const a = Math.max(from, k + 1), b = Math.min(k + 4, R), exp = k + 5;
    const reuse = a <= b ? `reused in round${a === b ? '' : 's'} ${a === b ? a : `${a}–${b}`}` : 'not reused';
    return `AnchorLoRA's last ${name} update is from round ${k}: ${reuse}; it expires in round ${exp}${exp > R ? ' (after this run ends)' : ''}.`;
  }
  function holdProjection(st) {
    const pr = pairedRound(st);
    const sd = st.recs.fedavg_ab_homo[pr] && st.recs.fedavg_ab_homo[pr].devices.c4;
    const starter = !sd ? '' : sd.state === 'fresh' ? ` The starter used the tablet's round-${pr} work and keeps no memory.`
      : ` The starter ${sd.state === 'discarded' ? `discarded the tablet's late round-${pr} work` : `had no tablet update in round ${pr}`} and keeps no memory.`;
    return `If you unplug the tablet now (out from round ${pr + 1}): ${projection(st, 'c4', pr + 1)}${starter}`;
  }
  function outProjection(st) {
    const lines = [];
    for (const d of Object.keys(st.outRounds)) if (st.out.has(d)) lines.push(`${DEVBY[d].cls} unplugged since round ${st.outRounds[d][0]} · ${projection(st, d, st.outRounds[d][0])}`);
    return lines.slice(0, 2).join(' ');
  }
  function effectRange(key) {
    const rows = ((VAL && VAL.results && VAL.results.rows) || []).filter((r) => typeof r[key] === 'number');
    return rows.length ? [rows.length, Math.min(...rows.map((r) => r[key])), Math.max(...rows.map((r) => r[key]))] : null;
  }
  function validationSentence() { // the reviewers' wording; numbers from demo/validation/results.json
    const s = effectRange('effect_starter'), a = effectRange('effect_anchor');
    if (!s || !a) return null;
    return `Most of this gap exists even with nobody unplugged. In the ${NUMW[s[0]] || s[0]} validation seeds, removing the tablet changed the starter's final man-pages loss by ${fmt(s[1])} to ${fmt(s[2])} and AnchorLoRA's by ${fmt(a[1])} to ${fmt(a[2])}. The full system was less sensitive; this comparison does not isolate memory's contribution.`;
  }
  function ghostFor(seed) { return VAL && VAL.ghosts && VAL.ghosts[String(seed)]; }
  let LIVE_RANGE = 0.3;
  (function computeRange() {
    let mx = 0;
    if (VAL && VAL.ghosts) for (const g of Object.values(VAL.ghosts)) for (const f of FEDS) for (const r of Object.values(g[f] || {})) for (const v of Object.values(r)) mx = Math.max(mx, Math.abs(v));
    if (VAL && VAL.results && VAL.results.band) for (const b of Object.values(VAL.results.band)) for (const [lo, hi] of Object.values(b)) mx = Math.max(mx, Math.abs(lo), Math.abs(hi));
    if (REC) for (const e of REC.events) if (e.ev === 'round') for (const v of Object.values(e.delta)) mx = Math.max(mx, Math.abs(v));
    if (mx > 0) LIVE_RANGE = Math.max(0.1, mx * 1.15);
  })();

  // ======================================================================================================
  // 3 · live: rendering
  // ======================================================================================================
  function plugSvg() {
    return el('svg', { viewBox: '0 0 44 36', class: 'plug', 'aria-hidden': 'true' },
      el('path', { d: 'M1 18 H14', class: 'body', style: 'stroke:var(--ink3);stroke-width:3;fill:none;stroke-linecap:round' }),
      el('rect', { x: 12, y: 10, width: 13, height: 16, rx: 3, class: 'body', style: 'fill:var(--ink2)' }),
      el('rect', { x: 25, y: 13, width: 7, height: 2.6, rx: 1, class: 'prong', style: 'fill:var(--ink3)' }),
      el('rect', { x: 25, y: 20.4, width: 7, height: 2.6, rx: 1, class: 'prong', style: 'fill:var(--ink3)' }),
      el('rect', { x: 31, y: 5, width: 12, height: 26, rx: 4, style: 'fill:#fff;stroke:var(--ink3);stroke-width:1.5' }),
      el('circle', { cx: 37, cy: 14.3, r: 1.5, style: 'fill:var(--ink3)' }),
      el('circle', { cx: 37, cy: 21.7, r: 1.5, style: 'fill:var(--ink3)' }));
  }
  const NAME = { fedavg_ab_homo: 'Starter', anchor_full: 'AnchorLoRA' };
  function chipFor(st, fed, dev, pr) {
    const kc = fed === 'anchor_full' ? 'k-anchor' : 'k-starter';
    if (st.training && st.training.fed === fed && st.training.device === dev) {
      return h('span', { class: `chip ${kc} st-pending` }, `${NAME[fed]}: training now, ${st.training.steps}/${st.training.planned} steps`);
    }
    const rec = pr ? st.recs[fed][pr] : null;
    if (!rec) return h('span', { class: `chip ${kc}` }, `${NAME[fed]}: –`);
    const d = rec.devices[dev];
    const [done, plan] = d.steps;
    let label, cls;
    if (d.state === 'fresh') { label = done < plan ? `fresh, partial ${done}/${plan}` : `fresh ${done}/${plan}`; cls = 'st-fresh'; }
    else if (fed === 'anchor_full' && d.memory === 'reused') { label = `reusing last update · age ${d.memory_age}/4`; cls = 'st-reused'; }
    else if (fed === 'anchor_full' && d.memory === 'expired') { label = `memory expired · age ${d.memory_age} > 4`; cls = 'st-expired'; }
    else if (d.state === 'unplugged') { label = 'unplugged · nothing used'; cls = 'st-unplugged'; }
    else if (d.state === 'discarded') { label = `late: ${d.scheduled_steps}/${plan} steps, discarded`; cls = 'st-discarded'; }
    else { label = 'offline this round'; cls = 'st-unplugged'; }
    return h('span', { class: `chip ${kc} ${cls}`, title: `round ${rec.round}` }, h('b', {}, `${NAME[fed]}: `), label);
  }
  function plugsOpen() { // a plug change needs a later round to take effect
    const st = ST.live;
    return view === 'live' && proc.running && !busy && st.current >= 1 && st.current < st.rounds && !st.done;
  }
  function plugHint() {
    const st = ST.live;
    if (view === 'recorded') return 'RECORDED: plugs follow the recording';
    if (!proc.running) return st.phase === 'done' ? 'run finished: plug changes closed' : 'start the live run to use the plugs';
    if (st.current < 1) return 'plugs open once round 1 starts';
    if (st.current >= st.rounds) return `final round: no later round for a plug change`;
    return 'click to pull / restore a plug · T = tablet';
  }
  function renderSockets() {
    const st = S(), pr = pairedRound(st), open = plugsOpen();
    $('#strip-hint').textContent = plugHint();
    $('#sockets').replaceChildren(...DEV.map((d) => {
      const pend = st.pending[d.id];
      const out = st.out.has(d.id);
      const willOut = pend ? pend.cmd === 'unplug' : out;
      const b = h('button', { type: 'button', class: 'sock', 'data-dev': d.id, 'data-out': willOut ? '1' : '0',
        'data-training': st.training && st.training.device === d.id ? '1' : '0', 'aria-pressed': willOut ? 'true' : 'false',
        'aria-label': `${d.cls}: ${willOut ? 'plug pulled, click to restore' : 'plugged in, click to pull the plug'}` });
      if (!open) b.disabled = true;
      const info = h('div', {}, h('div', { class: 'dname' }, d.cls),
        h('div', { class: 'dsub' }, `${DOMNAME[d.domain]} · rank ${d.rank} · ${d.steps} steps${d.id === 'c0' ? ' · 8× data' : ''}`));
      const chips = h('div', { class: 'chips' });
      if (pend) chips.append(h('span', { class: 'chip st-pending' }, pend.cmd === 'unplug' ? `plug pulled · out from round ${pend.eff}` : `plugged back · in from round ${pend.eff}`));
      else if (out && st.outRounds[d.id]) chips.append(h('span', { class: 'chip st-unplugged' }, `unplugged since round ${st.outRounds[d.id][0]}`));
      for (const f of FEDS) chips.append(chipFor(st, f, d.id, pr));
      info.append(chips);
      b.append(plugSvg(), info);
      b.addEventListener('click', () => togglePlug(d.id, willOut));
      return h('li', {}, b);
    }));
  }
  function drawLiveBars(fed, pr) {
    const st = S();
    const W = 500, H = 166, m = { l: 48, r: 58, t: 12, b: 34 };
    const rr = LIVE_RANGE, y = scale(-rr, rr, H - m.b, m.t);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}` });
    const g = el('g');
    yAxis(g, y, -rr, rr, m.l, W - m.r, niceStep(2 * rr, 5), (v) => fmt(v, 2));
    const rec = pr ? st.recs[fed][pr] : null;
    const gh = ghostFor(st.seed);
    const gw = (W - m.l - m.r) / DOMS.length, bw = gw * 0.56;
    DOMS.forEach((d, i) => {
      const cx = m.l + gw * i + gw / 2;
      if (rec) {
        const v = -rec.delta[d], vv = Math.max(-rr, Math.min(rr, v));
        g.append(el('rect', { x: cx - bw / 2, y: Math.min(y(0), y(vv)), width: bw, height: Math.max(1, Math.abs(y(vv) - y(0))), rx: 3, style: `fill:${COL[fed][1]}` }));
        g.append(txt(cx, v >= 0 ? y(vv) - 5 : y(vv) + 14, fmt(v), { 'text-anchor': 'middle', 'font-size': 13, 'font-weight': 700, style: `fill:${COL[fed][0]}` }));
        const gr = gh && gh[fed] && gh[fed][String(pr)];
        if (gr) {
          const gv = Math.max(-rr, Math.min(rr, -gr[d]));
          g.append(el('line', { x1: cx - bw / 2 - 6, x2: cx + bw / 2 + 6, y1: y(gv), y2: y(gv), style: 'stroke:var(--ink);stroke-width:2;stroke-dasharray:4 3' }));
        }
      }
      g.append(txt(cx, H - m.b + 15, DOMSHORT[d], { 'text-anchor': 'middle', 'font-size': 13, 'font-weight': 700, style: d === 'manpages' ? 'fill:var(--sim)' : 'fill:var(--ink)' }));
      g.append(txt(cx, H - m.b + 29, DEV.find((x) => x.domain === d).cls, { 'text-anchor': 'middle', 'font-size': 11.5 }));
    });
    g.append(txt(W - m.r + 6, y(0) + 4, 'untuned', { 'font-size': 12.5, 'font-weight': 700, style: 'fill:var(--ink)' }));
    if (!rec) g.append(txt((W - m.r + m.l) / 2, y(0) - 14, st.untuned ? 'untuned model measured; waiting for round 1' : 'no round yet', { 'text-anchor': 'middle', 'font-size': 14 }));
    svg.append(g);
    $(`#live-bars-${fed}`).replaceChildren(svg);
    $(`#after-${fed}`).textContent = rec ? `after round ${pr}` : 'no round yet';
    const line = $(`#fedline-${fed}`);
    if (!rec) { line.textContent = '↑ better than untuned · dashed tick = ghost (same seed, nobody unplugged)'; return; }
    const parts = [`fresh updates ${rec.fresh}/5`];
    if (fed === 'anchor_full') {
      const reused = Object.entries(rec.devices).filter(([, d]) => d.memory === 'reused').map(([c, d]) => `${DEVBY[c].cls} (age ${d.memory_age}/4)`);
      const expired = Object.entries(rec.devices).filter(([, d]) => d.memory === 'expired').map(([c, d]) => `${DEVBY[c].cls} (age ${d.memory_age})`);
      parts.push(reused.length ? `reused: ${reused.join(', ')}` : 'no memory reused');
      if (expired.length) parts.push(`expired: ${expired.join(', ')}`);
    } else {
      const disc = Object.entries(rec.devices).filter(([, d]) => d.state === 'discarded').map(([c]) => DEVBY[c].cls);
      if (disc.length) parts.push(`late work discarded: ${disc.join(', ')}`);
    }
    parts.push(`workstation norm share ${rec.norm_share && rec.norm_share.c0 != null ? rec.norm_share.c0.toFixed(2) : '–'}`);
    line.textContent = parts.join(' · ');
  }
  function drawCurve(pr) {
    const st = S(), R = st.rounds || 6, gh = ghostFor(st.seed), band = VAL && VAL.results && VAL.results.band;
    const W = 660, H = 236, m = { l: 50, r: 142, t: 18, b: 30 };
    let mx = 0.05;
    for (const f of FEDS) {
      for (let r = 1; r <= pr; r += 1) mx = Math.max(mx, Math.abs(st.recs[f][r].delta.manpages));
      if (gh && gh[f]) for (const v of Object.values(gh[f])) mx = Math.max(mx, Math.abs(v.manpages));
      if (band && band[`unplug.${f}`]) for (const [a, b] of Object.values(band[`unplug.${f}`])) mx = Math.max(mx, Math.abs(a), Math.abs(b));
    }
    mx *= 1.15;
    const x = scale(0, R, m.l, W - m.r), y = scale(-mx, mx, H - m.b, m.t);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}` });
    const tabletOut = st.outRounds.c4 || [];
    for (const r of tabletOut) svg.append(el('rect', { x: x(r - 0.5), y: m.t, width: x(Math.min(r + 0.5, R)) - x(r - 0.5), height: H - m.b - m.t, style: 'fill:#ece6f6' }));
    if (tabletOut.length) svg.append(txt(x(tabletOut[0] - 0.5) + 4, m.t - 5, `tablet unplugged from round ${tabletOut[0]}`, { 'font-size': 12, 'font-weight': 700, style: 'fill:var(--sim)' }));
    const g = el('g');
    yAxis(g, y, -mx, mx, m.l, W - m.r, niceStep(2 * mx, 5), (v) => fmt(v, 2));
    for (let r = 0; r <= R; r += 1) g.append(txt(x(r), H - m.b + 17, String(r), { 'text-anchor': 'middle', 'font-size': 12 }));
    g.append(txt(W - m.r + 8, H - m.b + 17, 'round', { 'font-size': 12 }));
    g.append(txt(W - m.r + 8, y(0) + 4, 'untuned', { 'font-size': 13, 'font-weight': 700, style: 'fill:var(--ink)' }));
    svg.append(g);
    const ends = [];
    for (const f of FEDS) {
      if (band && band[`unplug.${f}`]) {
        const b = band[`unplug.${f}`], rs = Object.keys(b).map(Number).sort((p, q) => p - q);
        const top = rs.map((r) => `${x(r)},${y(-b[r][0])}`), bot = rs.slice().reverse().map((r) => `${x(r)},${y(-b[r][1])}`);
        svg.append(el('polygon', { points: top.concat(bot).join(' '), style: `fill:${COL[f][1]};opacity:0.16` }));
      }
      if (gh && gh[f]) {
        const pts = [[0, 0]].concat(Object.entries(gh[f]).map(([r, v]) => [Number(r), -v.manpages]).sort((p, q) => p[0] - q[0]));
        svg.append(el('path', { d: pts.map(([r, v], i) => `${i ? 'L' : 'M'}${x(r)},${y(v)}`).join(''), style: `fill:none;stroke:${COL[f][0]};stroke-width:2;stroke-dasharray:6 5;opacity:0.75` }));
      }
      const pts = [[0, 0]];
      for (let r = 1; r <= pr; r += 1) pts.push([r, -st.recs[f][r].delta.manpages]);
      if (pts.length > 1) {
        svg.append(el('path', { d: pts.map(([r, v], i) => `${i ? 'L' : 'M'}${x(r)},${y(v)}`).join(''), style: `fill:none;stroke:${COL[f][0]};stroke-width:3.5;stroke-linejoin:round` }));
        for (const [r, v] of pts.slice(1)) svg.append(el('circle', { cx: x(r), cy: y(v), r: 4.5, style: `fill:${COL[f][0]}` }));
        const [lr, lv] = pts.at(-1);
        ends.push({ f, x: x(lr) + 9, y: y(lv) + 4, v: lv });
      }
    }
    for (const e of spread(ends, 16)) svg.append(txt(e.x, e.y, `${NAME[e.f]} ${fmt(e.v)}`, { 'font-size': 13.5, 'font-weight': 700, style: `fill:${COL[e.f][0]}` }));
    $('#live-curve').replaceChildren(svg);
    $('#after-curve').textContent = pr ? `after round ${pr}` : '';
    $('#legend-curve').replaceChildren(
      h('span', {}, h('i', { class: 'line', style: 'background:var(--starter)' }), 'Starter'),
      h('span', {}, h('i', { class: 'line', style: 'background:var(--anchor)' }), 'AnchorLoRA'),
      h('span', {}, h('i', { class: 'dash', style: 'color:var(--ink2)' }), 'ghost: pre-recorded by this engine, same config and seed, nobody unplugged'),
      band ? h('span', {}, h('i', { class: 'band', style: 'background:var(--ink3)' }), 'band: reference for tablet-only outage from round 2 (5 validation seeds, min–max)') : '',
      h('span', {}, '↑ better than untuned'));
    $('#curve-src').replaceChildren('Values: man-page loss of the untuned model minus the current model\'s, on 8 held-out blocks × 64 tokens. ',
      gh ? h('span', {}, 'Ghost: ', h('code', {}, gh.file), '. ') : 'No ghost for this seed. ', VAL ? h('span', {}, 'Band and effect ranges: ', h('code', {}, VAL.file), '.') : '');
  }
  function renderEffect(pr) {
    const st = S(), gh = ghostFor(st.seed), kind = intervention(st), box = $('#effect');
    if (!pr) {
      box.replaceChildren(h('p', {}, h('span', { class: 'eh' }, 'Waiting for round 1 of both federations.')),
        h('p', {}, 'The run then holds: pull the tablet plug and resume. This panel compares the run with its ghost (same seed, nobody unplugged).'));
      return;
    }
    const L = (f) => st.recs[f][pr].delta.manpages;
    const G = (f) => (gh && gh[f] && gh[f][String(pr)] ? gh[f][String(pr)].manpages : null);
    const gapLive = L('fedavg_ab_homo') - L('anchor_full');
    const gapGhost = G('fedavg_ab_homo') != null && G('anchor_full') != null ? G('fedavg_ab_homo') - G('anchor_full') : null;
    const share = gapGhost == null || gapLive <= 0 || gapGhost <= 0 ? ''
      : gapGhost >= gapLive ? ' (all of it)' : ` (${Math.round((100 * gapGhost) / gapLive)}% of it)`;
    const parts = [h('p', {}, h('span', { class: 'eh' }, `Round ${pr}, both federations. `),
      `Man-pages loss gap, starter − AnchorLoRA: ${fmt(gapLive)} in this run` + (gapGhost != null ? `; ${fmt(gapGhost)} with nobody unplugged${share}.` : '.'))];
    const firstOut = Math.min(Infinity, ...Object.values(st.outRounds).map((rs) => rs[0]));
    let maxd = null, n = 0;
    if (gh) for (const f of FEDS) for (let r = 1; r <= pr && r < firstOut; r += 1) {
      const gr = gh[f] && gh[f][String(r)];
      if (gr) for (const d of DOMS) { maxd = Math.max(maxd || 0, Math.abs(st.recs[f][r].delta[d] - gr[d])); n += 1; }
    }
    const match = n ? `Before any plug was pulled, live = ghost: max |difference| ${maxd === 0 ? '0 (bit-identical)' : maxd.toExponential(1)} over ${n} values.` : '';
    if (kind === 'none') {
      parts.push(h('p', {}, h('span', { class: 'tag2 t-none' }, 'no plug pulled'), match || 'This run tracks its ghost.'));
    } else {
      const eff = (f) => (G(f) != null ? fmt(L(f) - G(f)) : '–');
      if (kind === 'tablet') {
        parts.push(h('p', {}, h('span', { class: 'tag2 t-valid' }, 'pre-validated scenario'),
          `Tablet unplugged from round 2. This run minus its ghost at round ${pr}: starter ${eff('fedavg_ab_homo')}, AnchorLoRA ${eff('anchor_full')} (positive = worse).`));
        const vs = validationSentence();
        if (vs) parts.push(h('p', { class: 'quote' }, vs));
      } else {
        parts.push(h('p', {}, h('span', { class: 'tag2 t-custom' }, 'not pre-validated'),
          `Combined intervention effect in this run (${histText(st)}), this run minus its ghost at round ${pr}: starter ${eff('fedavg_ab_homo')}, AnchorLoRA ${eff('anchor_full')} (positive = worse). The band is a reference for a tablet-only outage from round 2.`));
      }
      if (match) parts.push(h('p', {}, match));
    }
    box.replaceChildren(...parts);
  }
  function trainingText(st) {
    return st.training ? ` · ${NAME[st.training.fed]}: ${DEVBY[st.training.device].cls} training ${st.training.steps} steps` : '';
  }
  function renderStage() {
    const st = S(), stage = $('#stage');
    let state = 'idle', main = '', proj = '';
    if (view === 'recorded') {
      state = 'recorded';
      main = st.done ? 'RECORDED run finished (validation run, seed 0).' : `RECORDED playback · round ${st.current || 0} of ${st.rounds}${trainingText(st)}`;
      proj = outProjection(st);
    } else if (!avail.checked) {
      main = 'Checking the live engine…';
    } else if (!proc.running) {
      if (!avail.ok) { state = 'unavailable'; main = `Live engine unavailable here: ${avail.why.join('; ') || 'open the page through demo/run.sh'}. Use Play RECORDED run.`; }
      else if (st.phase === 'done') main = `Live run finished: ${st.rounds} rounds, seed ${st.seed}. Plug changes closed.`;
      else if (st.phase === 'stopped') main = 'Live run stopped.';
      else if (st.phase === 'failed') { state = 'error'; main = `Live engine failed${st.error ? `: ${st.error}` : ''} (log: demo/.live/engine.log).`; }
      else main = 'Press Start (S): loads SmolLM2-135M on this CPU, runs round 1 of both federations, then holds for your plug.';
    } else if (['starting', 'loading', 'loaded'].includes(st.phase)) {
      state = 'running'; main = `Loading the real SmolLM2-135M on CPU (one copy, nice 10)…${st.loadS ? ` ${st.loadS.toFixed(1)} s` : ''}`;
    } else if (st.phase === 'ready') {
      state = 'running'; main = `Untuned model measured${st.identical ? '; both federations start identical' : ''}. Round 1 starting…`;
    } else if (st.holding) {
      state = 'hold';
      main = st.staged ? `Round ${st.current} complete — pull the tablet plug, then Resume` : `Paused after round ${st.current} — Resume to continue`;
      proj = st.pending.c4 && st.pending.c4.cmd === 'unplug' ? `Tablet plug pulled: out from round ${st.pending.c4.eff}. ${projection(st, 'c4', st.pending.c4.eff)} Now press Resume (R).` : (st.staged ? holdProjection(st) : outProjection(st));
    } else {
      state = 'running';
      const final = st.current >= st.rounds;
      const lw = st.roundWall[st.current - 1];
      main = `Round ${st.current} of ${st.rounds}${final ? ' (final)' : ''} in progress${trainingText(st)}${st.pauseReq ? ` · the run holds after round ${st.current} for your plug` : ''}${final ? ' · plug changes closed: no later round' : ''}${lw ? ` · last round ${lw.toFixed(0)} s` : ''}`;
      proj = outProjection(st);
    }
    if (notice) main += ` · ${notice}`;
    if (st.error && view === 'live' && state !== 'error') main += ` · engine: ${st.error}`;
    stage.dataset.state = state;
    stage.dataset.mode = view;
    $('#stage-main').textContent = main;
    let pj = $('#stage-proj');
    if (!pj) { pj = h('p', { class: 'stage-proj', id: 'stage-proj' }); $('#stage-main').after(pj); }
    pj.textContent = proj;
    pj.hidden = !proj;
    $('#livelabel').textContent = view === 'recorded'
      ? `RECORDED, not live · validation run, seed 0, tablet unplugged by script from round 2 · ${REC ? REC.file : ''} · same reduced config · Δ vs untuned on the same eval subset`
      : 'LIVE · reduced config (batch 1×64, eval 8×64 tok/domain, 6 rounds) · Δ vs untuned on the same eval subset · not comparable in absolute terms to committed runs';
  }
  function renderMem() { // the real engine's memory guard, whatever the page displays
    const m = proc.running ? ST.live.mem : null, b = $('#membanner');
    b.hidden = !m;
    if (!m) return;
    const now = avail.memory != null && avail.memory !== m.level ? `now ${avail.memory}` : '';
    const text = m.reason === 'waiting_to_start' || m.where === 'start'
      ? `Waiting to start: level ${m.level}; requires ≥ ${m.requires != null ? m.requires : 30}`
      : `Paused during training: level ${m.level}; resumes at ${m.resumes_at != null ? m.resumes_at : 30}`;
    b.replaceChildren(text, h('small', {}, `this Mac's memory level${now ? ` (${now})` : ''}; the engine continues on its own`));
  }
  function renderPill() {
    const pill = $('#livepill'), st = ST.live;
    let s = 'idle', t;
    if (proc.running) {
      if (st.mem) { s = 'memory'; t = 'LIVE · paused for memory'; }
      else if (st.holding) { s = 'paused'; t = `LIVE · HOLD after round ${st.current}`; }
      else if (st.current >= 1) { s = 'running'; t = `LIVE · round ${st.current}/${st.rounds}`; }
      else { s = 'loading'; t = 'LIVE · loading'; }
    } else if (view === 'recorded') { s = 'recorded'; t = ST.recorded.done ? 'RECORDED · finished' : 'RECORDED playback'; }
    else t = !avail.checked ? 'LIVE · …' : !avail.ok ? 'LIVE · unavailable' : st.phase === 'done' ? 'LIVE · finished' : 'LIVE · ready';
    pill.dataset.state = s;
    pill.textContent = t;
  }
  function renderControls() {
    const st = ST.live;
    $('#btn-start').disabled = !avail.ok || proc.running || busy;
    const pb = $('#btn-pause');
    pb.classList.toggle('primary', proc.running && st.holding);
    if (proc.running && st.holding) { pb.disabled = busy; pb.textContent = 'Resume (R)'; }
    else if (proc.running && st.pauseReq) { pb.disabled = true; pb.textContent = `Holds after round ${st.current}`; }
    else if (proc.running && st.phase === 'round' && st.current < st.rounds) { pb.disabled = busy; pb.textContent = 'Pause after this round'; }
    else { pb.disabled = true; pb.textContent = 'Pause after this round'; }
    $('#btn-stop').disabled = !proc.running || busy;
    const rb = $('#btn-recorded');
    rb.disabled = !REC || busy;
    rb.textContent = proc.running ? 'Stop live and play RECORDED' : (view === 'recorded' && recTimer ? 'Stop RECORDED playback' : 'Play RECORDED run');
    $('#footstate').textContent = st.prov ? `engine commit ${st.prov.commit} · code_sha ${st.prov.code_sha}` : '';
  }
  function renderLive() {
    renderMem(); renderPill(); renderControls(); renderStage();
    if ($('#view-live').hidden && !SELFTEST) return;
    const pr = pairedRound(S());
    renderSockets();
    for (const f of FEDS) drawLiveBars(f, pr);
    drawCurve(pr);
    renderEffect(pr);
  }

  // ======================================================================================================
  // 3 · live: actions, RECORDED playback, server link
  // ======================================================================================================
  const NET = { // replaced by fakes in ?selftest=1
    async post(url, body) {
      const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
      return r.json().catch(() => ({ error: `HTTP ${r.status}` }));
    },
    async status() { const r = await fetch('api/status', { cache: 'no-store' }); return r.json(); },
  };
  async function togglePlug(dev, isOut) {
    if (!plugsOpen()) return;
    const r = await NET.post('api/cmd', { cmd: isOut ? 'replug' : 'unplug', device: dev });
    notice = r && r.error ? r.error : null;
    renderLive();
  }
  async function onPause() {
    const st = ST.live;
    if (!proc.running) return;
    const r = await NET.post('api/cmd', { cmd: st.holding ? 'resume' : 'pause' });
    notice = r && r.error ? r.error : null;
    renderLive();
  }
  async function onStart() {
    if (busy || proc.running || !avail.ok) return;
    stopRecorded();
    view = 'live';
    notice = null;
    const r = await NET.post('api/start', { seed: Number($('#live-seed').value) });
    if (r && r.error) notice = r.error + (r.why ? `: ${r.why.join('; ')}` : '');
    else if (r && r.run_id != null) { proc.running = true; proc.runId = r.run_id; }
    renderLive();
  }
  async function stopLive() { // resolves true only once the server reports no running engine
    busy = true; notice = 'stopping the live run…'; renderLive();
    let ok = false, err = null;
    try {
      const r = await NET.post('api/stop');
      const s = await NET.status();
      applyStatus(s);
      ok = !!(r && r.ok) && !s.running;
      if (!ok) err = (r && r.error) || 'the engine is still running';
    } catch (e) { err = String(e); }
    busy = false;
    notice = ok ? null : `could not stop the live run (${err}); it is still running`;
    renderLive();
    return ok;
  }
  async function onRecorded() {
    if (busy || !REC) return;
    if (view === 'recorded' && recTimer) { stopRecorded(); view = 'live'; renderLive(); return; }
    if (proc.running && !(await stopLive())) return;
    playRecorded();
  }
  let recTimer = null;
  function stopRecorded() { if (recTimer) { clearTimeout(recTimer); recTimer = null; } }
  function playRecorded() {
    stopRecorded();
    view = 'recorded';
    ST.recorded = newState('recorded');
    const evs = REC.events;
    let i = 0, vt = 0, last = performance.now();
    onEvent(ST.recorded, { ev: 'server_start', run_id: 'recorded', seed: 0 });
    const tick = () => {
      const now = performance.now();
      vt += ((now - last) / 1000) * Number($('#rec-speed').value);
      last = now;
      while (i < evs.length && evs[i].t_wall <= vt) onEvent(ST.recorded, evs[i++]);
      if (i < evs.length) recTimer = setTimeout(tick, 120); else { recTimer = null; ST.recorded.done = true; }
      renderLive();
    };
    tick();
  }
  async function poll() {
    if (SELFTEST) return;
    if (location.protocol === 'file:') {
      avail = { checked: true, ok: false, why: ['page opened as a file: run demo/run.sh for the live engine'], memory: null };
    } else {
      try { applyStatus(await NET.status()); } catch (e) { avail = { checked: true, ok: false, why: ['demo server not reachable'], memory: null }; }
    }
    renderLive();
  }
  function connect() {
    if (SELFTEST || location.protocol === 'file:' || !window.EventSource) return;
    const es = new EventSource('api/events');
    let queued = false;
    es.onmessage = (m) => {
      const ev = JSON.parse(m.data);
      if (ev.ev === 'server_start' || ST.live.runId == null || ev.run_id === ST.live.runId) onLiveEvent(ev);
      if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; renderLive(); }); }
    };
  }

  // ======================================================================================================
  // 4 · costs, provenance
  // ======================================================================================================
  function drawCosts() {
    const t = h('div', {});
    for (const [s, k] of [['fedavg_ab_homo', 'spike_vs_fedavg_ab_homo'], ['ffa_lora', 'spike_vs_ffa_lora'], ['flexlora', 'spike_vs_flexlora']]) {
      const mi = [`dropout.${k}.micro_mean`, `dropout.${k}.micro_lo`, `dropout.${k}.micro_hi`];
      const wo = [`dropout.${k}.worst_mean`, `dropout.${k}.worst_lo`, `dropout.${k}.worst_hi`];
      t.append(h('div', { class: 'lrow three' }, h('span', { class: 'who ' + CCLASS[s] }, `vs ${D.short[s]}`),
        h('span', { class: 'val' }, h('span', { class: 'big' }, fmt(K(mi[0]))), ' ', h('span', { class: 'ci' }, ci(K(mi[1]), K(mi[2])))),
        h('span', { class: 'val' }, h('span', { class: 'big' }, fmt(K(wo[0]))), ' ', h('span', { class: 'ci' }, ci(K(wo[1]), K(wo[2])))),
        keyTag(...mi), keyTag(...wo)));
    }
    $('#costs').replaceChildren(h('div', { class: 'lrow three' }, h('span', {}, ''), h('span', { class: 'val ci' }, 'sample-weighted loss (micro)'), h('span', { class: 'val ci' }, 'worst domain')), t,
      h('p', { class: 'note' }, 'Positive = AnchorLoRA worse. Equal weights per device trade the data-rich workstation\'s domain (Wikipedia: the hardest, with 8× the data) for the other four, so the sample-weighted loss (what n-weighted FedAvg optimises) and the worst domain both come out worse than under each baseline.'));
    const v = VAL && VAL.results;
    const vs = $('#valsummary');
    if (v && v.verdict) {
      vs.replaceChildren(...['P1', 'P2', 'P3'].map((k) => h('span', { class: v.verdict[k] ? 'pass' : v.verdict[k] === false ? 'fail' : '' }, `${k} ${v.verdict[k] ? 'PASS' : v.verdict[k] === false ? 'FAIL' : 'incomplete'}  `)), h('code', {}, 'demo/validation/RESULTS.md'));
    } else vs.textContent = 'validation results not exported yet (demo/validation).';
    const prov = h('table', { class: 'prov' });
    const add = (a, b) => prov.append(h('tr', {}, h('td', {}, a), h('td', {}, b)));
    add('Headline numbers', h('span', {}, h('code', {}, D.files.canonical), ', ', h('code', {}, D.files.dropout_canonical), ', ', h('code', {}, D.files.untuned)));
    add('Per-round replay', h('code', {}, D.replay.logs_glob));
    add('Token blocks (real text)', h('code', {}, 'eval/data/blocks_smollm2-135m_T128_N2400_E48.npz'));
    add('Live engine', h('span', {}, h('code', {}, 'demo/live_engine.py'), ' → ', h('code', {}, 'components/flower_adapter'), ' (FlowerLoraStrategy, LocalGrid, ClientApp) → ', h('code', {}, 'components/aggregator/strategies.py')));
    if (v && v.provenance) add('Validation runs', h('span', {}, h('code', {}, 'demo/validation/runs/'), ' · ', v.provenance.map((p) => `commit ${p.commit} · code_sha ${p.code_sha}${p.dirty ? ' (dirty)' : ''}`).join('; ')));
    if (REC) {
      const hello = REC.events.find((e) => e.ev === 'hello');
      add('RECORDED run', h('span', {}, h('code', {}, REC.file), hello ? ` · commit ${hello.provenance.commit} · code_sha ${hello.provenance.code_sha}` : ''));
    }
    add('This page', h('span', {}, h('code', {}, 'demo/web/data.js'), ' is generated by ', h('code', {}, 'demo/export_replay.py'), '; ', h('code', {}, 'demo/smoke.sh'), ' checks it against the sources.'));
    $('#provenance').replaceChildren(prov);
  }

  // ======================================================================================================
  // tabs and wiring
  // ======================================================================================================
  const TABS = ['real', 'outage', 'live', 'costs'];
  function show(name) {
    for (const t of TABS) {
      $(`#tab-${t}`).setAttribute('aria-selected', String(t === name));
      $(`#view-${t}`).hidden = t !== name;
    }
    if (name === 'live') renderLive();
    history.replaceState(null, '', `${location.search}#${name}`);
    window.scrollTo(0, 0); // every tab opens on its stage view (the first 1440x900 viewport)
  }
  for (const t of TABS) $(`#tab-${t}`).addEventListener('click', () => show(t));
  window.addEventListener('hashchange', () => { const n = location.hash.slice(1); if (TABS.includes(n)) show(n); });
  document.addEventListener('keydown', (e) => {
    if (e.target && (e.target.tagName === 'SELECT' || e.target.tagName === 'INPUT')) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const i = ['1', '2', '3', '4'].indexOf(e.key);
    if (i >= 0) show(TABS[i]);
    const k = e.key.toLowerCase();
    if (k === 's' && !$('#btn-start').disabled) { show('live'); onStart(); }
    if (k === 't') { const b = document.querySelector('.sock[data-dev="c4"]'); if (b && !b.disabled) b.click(); }
    if (k === 'r' && proc.running && ST.live.holding) onPause();
  });
  $('#livepill').addEventListener('click', () => show('live'));
  for (const sel of ['#strip-seed', '#live-seed']) $(sel).replaceChildren(...D.seeds.map((s) => h('option', { value: String(s) }, String(s))));
  $('#strip-seed').addEventListener('change', drawOutageStage);
  $('#strip-play').addEventListener('click', playStrip);
  $('#btn-start').addEventListener('click', onStart);
  $('#btn-pause').addEventListener('click', onPause);
  $('#btn-stop').addEventListener('click', () => { if (proc.running) stopLive(); });
  $('#btn-recorded').addEventListener('click', onRecorded);

  // ======================================================================================================
  // ?selftest=1: headless check of all four tabs and the stage flow from committed fixtures (demo/smoke.sh)
  // ======================================================================================================
  async function selftest() {
    const res = { ok: true, viewport: [window.innerWidth, window.innerHeight], checks: [] };
    const ck = (name, ok, detail) => { res.checks.push({ name, ok: !!ok, detail: detail == null ? null : String(detail).slice(0, 400) }); if (!ok) res.ok = false; };
    const tx = (sel) => { const e = document.querySelector(sel); return e ? e.textContent : ''; };
    const box = (sel) => { const e = document.querySelector(sel); if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
    // the layout depends on width only, so 'inside the 1440x900 stage' = inside this box at a 1440-px-wide viewport
    const inView = (sel) => { const b = box(sel); return !!b && b[2] > b[0] && b[3] > b[1] && b[0] >= 0 && b[1] >= 0 && b[2] <= 1440 && b[3] <= 900; };
    const allIn = (name, sels) => { const bad = sels.filter((s) => !inView(s)); ck(name, !bad.length, bad.map((s) => `${s} ${JSON.stringify(box(s))}`).join('; ')); };
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    const calls = [];
    const fake = { running: false, runId: 7, stopOk: true };
    NET.post = async (url, body) => {
      calls.push({ url, body: body || null, view });
      if (url === 'api/stop') {
        await sleep(40);
        calls.at(-1).viewAfterWait = view;
        if (!fake.stopOk) return { error: 'refused by the selftest fake' };
        fake.running = false;
        onLiveEvent({ ev: 'engine_exit', code: -15, stopped: true, run_id: fake.runId });
        return { ok: true, stopped: true };
      }
      return url === 'api/cmd' ? { ok: true } : { error: 'selftest: no engine' };
    };
    NET.status = async () => ({ live_available: true, why: [], running: fake.running, state: fake.running ? 'running' : 'stopped', run_id: fake.runId, memory_level: 41 });
    avail = { checked: true, ok: true, why: [], memory: 41 };
    const feed = (ev) => onLiveEvent(Object.assign({ run_id: fake.runId }, ev));
    try {
      ck('viewport is 1440 px wide (the stage layout)', window.innerWidth === 1440, window.innerWidth);
      // header + tab 1
      show('real');
      ck('header wording', tx('.pitch') === 'Federated LoRA with simulated weak-device budgets, live dropout handling, and transparent update-share diagnostics.', tx('.pitch'));
      ck('no "dominate" on the page', !document.body.textContent.includes('dominate'));
      ck('truth labels', ['SIMULATED device budgets (ranks/steps/availability)', 'real SmolLM2-135M', 'real text'].every((t) => tx('.truth').includes(t)), tx('.truth'));
      ck('tab 1 values', ['−0.081', '[−0.093, −0.070]', '−0.050', '−0.083', '5/5', '1/5', '0.88', '0.22'].every((t) => tx('#ledger').includes(t)), tx('#ledger').slice(0, 300));
      allIn('tab 1 stage in 1440x900', ['#chart-gains svg', '#ledger .ledger-block']);
      // tab 2
      show('outage');
      allIn('tab 2 stage in 1440x900', ['#chart-outage svg', '#tabletstrip table', '#strip-play', '#strip-note', '#peaks .lrow']);
      ck('tab 2 formula: untuned − trained', tx('#view-outage .chart-panel .src').includes('base_per_domain_smollm2-135m.json · manpages − eval/results/logs/'), tx('#view-outage .chart-panel .src'));
      ck('tab 2 values', ['+0.277', '−0.020', '+0.305', '−0.019'].every((t) => tx('#peaks').includes(t)), tx('#peaks').slice(0, 200));
      $('#strip-play').click(); await sleep(900);
      ck('Play rounds animates strip and curve', stripNow >= 1 && !!document.querySelector('#tabletstrip td.now'), stripNow);
      $('#strip-play').click();
      $('#drill').open = true; window.scrollTo(0, 600);
      show('live');
      ck('tab change opens the stage view (scroll 0)', window.scrollY === 0, window.scrollY);
      // tab 3: the RECORDED run's events fed as a live run, through the stage hold
      const evs = REC.events;
      const end1 = evs.findIndex((e) => e.ev === 'round_end' && e.round === 1);
      fake.running = true;
      feed({ ev: 'server_start', seed: 0, hold_after: 1 });
      for (let i = 0; i <= end1; i += 1) {
        feed(evs[i]);
        if (evs[i].ev === 'round_start' && evs[i].round === 1) feed({ ev: 'paused', after_round: 1 });
      }
      feed({ ev: 'stage_hold', after_round: 1, next_round: 2, rounds: 6, staged: true });
      renderLive();
      ck('hold message', tx('#stage-main').includes('Round 1 complete — pull the tablet plug, then Resume'), tx('#stage-main'));
      ck('hold projection from the actual history', tx('#stage-proj').includes('expires in round 6'), tx('#stage-proj'));
      ck('Resume offered at the hold', !$('#btn-pause').disabled && /Resume/.test($('#btn-pause').textContent), $('#btn-pause').textContent);
      const sock = () => document.querySelector('.sock[data-dev="c4"]');
      ck('tablet plug offered at the hold', !!sock() && !sock().disabled);
      allIn('live stage in 1440x900 (hold)', ['#btn-start', '#btn-pause', '#btn-stop', '#btn-recorded', '#stage', '.sock[data-dev="c4"]', '#live-bars-fedavg_ab_homo svg', '#live-bars-anchor_full svg', '#live-curve svg', '#effect']);
      const saved = ST.live.recs.anchor_full[1].devices.c4.state;
      ST.live.recs.anchor_full[1].devices.c4.state = 'offline'; renderLive();
      ck('no expiry promised without a cached update', !tx('#stage-proj').includes('expires') && tx('#stage-proj').includes('nothing to reuse'), tx('#stage-proj'));
      ST.live.recs.anchor_full[1].devices.c4.state = saved; renderLive();
      sock().click(); await sleep(5);
      ck('click sends unplug c4', calls.some((c) => c.url === 'api/cmd' && c.body && c.body.cmd === 'unplug' && c.body.device === 'c4'));
      feed({ ev: 'cmd_ack', cmd: 'unplug', device: 'c4', effective_round: 2 }); renderLive();
      ck('pending chip: out from round 2', sock().textContent.includes('out from round 2'), sock().textContent);
      $('#btn-pause').click(); await sleep(5);
      ck('Resume sends resume', calls.some((c) => c.url === 'api/cmd' && c.body && c.body.cmd === 'resume'));
      feed({ ev: 'resumed', round: 1 });
      let finalSeen = false;
      for (let i = end1 + 1; i < evs.length; i += 1) {
        const e = evs[i];
        feed(e);
        if (e.ev === 'round_start' && e.round === 5) { renderLive(); ck('plugs offered in round 5 (a later round remains)', !sock().disabled); }
        if (e.ev === 'round_start' && e.round === 6) { renderLive(); finalSeen = true; ck('plugs closed in the final round', sock().disabled && tx('#strip-hint').includes('no later round'), tx('#strip-hint')); }
        if (e.ev === 'round' && e.fed === 'fedavg_ab_homo' && e.round === 4) {
          renderLive();
          ck('panels show the last round BOTH federations finished', tx('#after-fedavg_ab_homo') === 'after round 3' && tx('#after-anchor_full') === 'after round 3', `${tx('#after-fedavg_ab_homo')} / ${tx('#after-anchor_full')}`);
        }
      }
      ck('final round reached', finalSeen);
      renderLive();
      ck('both panels after round 6', tx('#after-fedavg_ab_homo') === 'after round 6' && tx('#after-anchor_full') === 'after round 6');
      ck('memory expiry chip at round 6', sock().textContent.includes('memory expired · age 5 > 4'), sock().textContent);
      const vs = validationSentence();
      ck('validation sentence from results.json', !!vs && vs.includes('In the five validation seeds') && vs.includes('+0.009 to +0.029') && vs.includes('−0.002 to +0.008'), vs);
      ck('effect caption: pre-validated scenario + sentence', tx('#effect').includes('pre-validated scenario') && tx('#effect').includes(vs), tx('#effect'));
      ck('no "absorbs" wording', !document.body.textContent.includes('absorb'));
      ck('band labelled as a reference', tx('#legend-curve').includes('reference for tablet-only outage from round 2'), tx('#legend-curve'));
      allIn('live stage in 1440x900 (end of run)', ['#stage', '#effect', '#live-curve svg', '#btn-recorded']);
      const keep = ST.live.outRounds;
      ST.live.outRounds = { c4: [2, 3, 4, 5, 6], c0: [4, 5, 6] }; renderLive();
      ck('custom history: combined intervention effect', tx('#effect').includes('Combined intervention effect in this run') && !tx('#effect').includes('pre-validated scenario'), tx('#effect'));
      ST.live.outRounds = keep; renderLive();
      feed({ ev: 'memory', paused: true, level: 24, where: 'train', reason: 'paused_training', pause_below: 25, resumes_at: 30 }); renderLive();
      ck('memory banner: training', !$('#membanner').hidden && tx('#membanner').includes('Paused during training: level 24; resumes at 30'), tx('#membanner'));
      feed({ ev: 'memory', paused: true, level: 29, where: 'start', reason: 'waiting_to_start', requires: 30 }); renderLive();
      ck('memory banner: start', tx('#membanner').includes('Waiting to start: level 29; requires ≥ 30'), tx('#membanner'));
      ck('handoff button names the stop', $('#btn-recorded').textContent === 'Stop live and play RECORDED', $('#btn-recorded').textContent);
      ck('live controls truthful while live', !$('#btn-stop').disabled && $('#btn-start').disabled);
      fake.stopOk = false; await onRecorded();
      ck('refused stop: stays live and says so', view === 'live' && proc.running && !$('#btn-stop').disabled && tx('#stage-main').includes('could not stop'), tx('#stage-main'));
      fake.stopOk = true; await onRecorded();
      const stop = calls.filter((c) => c.url === 'api/stop').at(-1);
      ck('stop awaited before switching to RECORDED', !!stop && stop.view === 'live' && stop.viewAfterWait === 'live' && view === 'recorded', JSON.stringify(stop));
      renderLive();
      ck('after the handoff: no live process, controls truthful', !proc.running && $('#btn-stop').disabled && !$('#btn-start').disabled && $('#membanner').hidden);
      ck('RECORDED labelled', tx('#livelabel').includes('RECORDED, not live') && $('#stage').dataset.mode === 'recorded', tx('#livelabel'));
      await sleep(300);
      stopRecorded();
      ck('RECORDED fixture complete', REC.events.filter((e) => e.ev === 'round').length === 12);
    } catch (e) {
      ck('selftest ran without exceptions', false, `${e && e.stack ? e.stack : e}`);
    }
    const pre = h('pre', { id: 'selftest', hidden: '' });
    pre.textContent = JSON.stringify(res);
    document.body.append(pre);
    document.title = res.ok ? 'SELFTEST PASS' : 'SELFTEST FAIL';
  }

  drawGains();
  drawLedger();
  drawOutageStage();
  drawOutageLedgers();
  drawCosts();
  renderLive();
  if (SELFTEST) {
    selftest();
  } else {
    poll();
    setInterval(poll, 4000);
    connect();
    const start = (location.hash || '').slice(1);
    show(TABS.includes(start) ? start : 'real');
  }
  window.__P1_READY = true;
})();
