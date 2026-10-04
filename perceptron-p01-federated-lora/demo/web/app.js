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
    const b3 = h('div', { class: 'ledger-block' }, h('h4', {}, "Workstation's share of update magnitude (norm share; magnitude diagnostic; equal share 0.20)"), cells3,
      h('span', { class: 'key' }, 'v2_canonical.json · dropout.<strategy>.c0_norm_mean'));
    box.replaceChildren(b1, b2, b3);
  }
  const pos5 = (v) => `${v}/5`;

  // ======================================================================================================
  // 2 · committed outage
  // ======================================================================================================
  const OUT = D.replay.outage;
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
  function drawOutage() {
    const host = $('#chart-outage');
    const W = 900, H = 400, m = { l: 62, r: 120, t: 26, b: 44 };
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

    const pk = h('div', {});
    for (const s of ['fedavg_ab_homo', 'flexlora', 'ffa_lora', 'anchor_full']) {
      const a = `dropout.${s}.outage_peak_rise_mean`, b = `dropout.${s}.outage_peak_rise_max`;
      pk.append(h('div', { class: 'lrow three' }, h('span', { class: 'who ' + CCLASS[s] }, D.short[s]),
        h('span', { class: 'val' }, h('span', { class: 'big' }, fmt(K(a))), h('span', { class: 'ci' }, ' mean')),
        h('span', { class: 'val' }, fmt(K(b)), h('span', { class: 'ci' }, ' worst seed')), keyTag(a, b)));
    }
    const amax = K('dropout.anchor_full.outage_peak_rise_max');
    $('#peaks').replaceChildren(h('p', { class: 'note' }, 'Highest man-page loss at any evaluated round minus the untuned model; positive = worse than untuned. Mean of 5 seeds and the worst seed.'), pk,
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
    $('#usedrounds').replaceChildren(h('p', { class: 'note' }, 'Out of 12, mean over seeds; "memory" = rounds its last update was reused while it was absent.'), ur,
      h('span', { class: 'key' }, 'v2_dropout_canonical.json · dropout.<strategy>.<device>.rounds_used_mean / rounds_memory_mean'));
  }

  const GLYPH = { o: '●', p: '◐', x: '✕', '-': '–' };
  const GCLS = { o: 'g-o', p: 'g-p', x: 'g-x', '-': 'g-off' };
  let stripNow = 0, stripTimer = null;
  function drawStrip() {
    const seed = $('#strip-seed').value;
    const t = h('table', { class: 'rs' });
    t.append(h('tr', {}, h('th', {}, ''), ...Array.from({ length: 12 }, (_, i) => h('th', { class: 'r' + (stripNow === i + 1 ? ' now' : '') }, `r${i + 1}`))));
    for (const s of ['fedavg_ab_homo', 'anchor_full']) {
      const rounds = D.replay.runs[s][seed].rounds;
      t.append(h('tr', { class: 'grp' }, h('td', { class: CCLASS[s], colspan: 13 }, D.labels[s])));
      DEV.forEach((d, di) => {
        t.append(h('tr', {}, h('th', {}, `${d.cls}`), ...rounds.map((r) => {
          const st = r.status[di];
          const mem = r.memory.includes(d.id);
          const cls = ['c', mem ? 'g-m' : GCLS[st], stripNow === r.round ? 'now' : '', d.id === OUT.device && OUT.rounds.includes(r.round) ? 'out' : ''].join(' ');
          const [done, plan] = r.steps[di];
          const title = mem ? 'absent; its last update was reused (memory)' : { o: `full work ${done}/${plan} steps`, p: `partial work kept ${done}/${plan} steps`, x: 'cut off by the deadline, discarded', '-': 'offline' }[st];
          return h('td', { class: cls, title: `${d.cls}, round ${r.round}: ${title}` }, mem ? '↺' : GLYPH[st]);
        })));
      });
      t.append(h('tr', {}, h('th', { class: 'share' }, 'workstation share'), ...rounds.map((r) => h('td', { class: 'share', style: 'text-align:center' }, r.norm_share_c0 == null ? '–' : r.norm_share_c0.toFixed(2)))));
    }
    $('#roundstrip').replaceChildren(t);
    $('#strip-src').replaceChildren('Cells: ● full work · ◐ partial work kept · ✕ cut off by the deadline and discarded · – offline · ↺ absent, last update reused (memory). Purple underline: forced tablet outage. "workstation share": its norm share of that round\'s update (magnitude diagnostic). Source ',
      h('code', {}, D.replay.runs.fedavg_ab_homo[seed].file), ', ', h('code', {}, D.replay.runs.anchor_full[seed].file));
  }
  function playStrip() {
    if (stripTimer) { clearInterval(stripTimer); stripTimer = null; $('#strip-play').textContent = 'Play rounds'; return; }
    stripNow = 0;
    $('#strip-play').textContent = 'Stop';
    stripTimer = setInterval(() => {
      stripNow += 1;
      if (stripNow > 12) { clearInterval(stripTimer); stripTimer = null; stripNow = 0; $('#strip-play').textContent = 'Play rounds'; }
      drawStrip();
    }, 750);
  }

  // ======================================================================================================
  // 3 · live
  // ======================================================================================================
  const VAL = D.validation;
  const REC = D.recorded;
  function newState(kind) {
    return { kind, runId: null, seed: 0, rounds: 6, phase: 'idle', untuned: null, identical: null, recs: { fedavg_ab_homo: {}, anchor_full: {} },
      out: new Set(), pending: {}, outRounds: {}, current: 0, training: null, memPaused: null, roundWall: {}, error: null, prov: null, loadS: null, done: false };
  }
  const ST = { live: newState('live'), recorded: newState('recorded') };
  let view = 'live';
  let avail = { checked: false, ok: false, why: [], memory: null, state: 'idle' };
  const S = () => ST[view];

  function onEvent(st, ev) {
    switch (ev.ev) {
      case 'server_start': Object.assign(st, newState(st.kind), { runId: ev.run_id, seed: ev.seed, phase: 'starting' }); break;
      case 'hello': st.seed = ev.seed; st.rounds = ev.rounds; st.prov = ev.provenance; st.phase = 'starting'; break;
      case 'loading': st.phase = 'loading'; break;
      case 'loaded': st.phase = 'loaded'; st.loadS = ev.load_s; break;
      case 'untuned': st.untuned = ev.per_domain; st.identical = ev.identical_start; st.phase = 'ready'; break;
      case 'cmd_ack':
        if (ev.cmd === 'unplug' || ev.cmd === 'replug') st.pending[ev.device] = { cmd: ev.cmd, eff: ev.effective_round };
        break;
      case 'round_start':
        st.current = ev.round; st.phase = 'round'; st.out = new Set(ev.unplugged);
        for (const d of ev.unplugged) (st.outRounds[d] = st.outRounds[d] || []).push(ev.round);
        for (const [d, p] of Object.entries(st.pending)) if (p.eff <= ev.round) delete st.pending[d];
        break;
      case 'device_start': st.training = { fed: ev.fed, device: ev.device, steps: ev.steps, planned: ev.planned }; break;
      case 'device_done': st.training = null; break;
      case 'round': st.recs[ev.fed][ev.round] = ev; break;
      case 'round_end': st.roundWall[ev.round] = ev.wall_s; st.training = null; break;
      case 'memory': st.memPaused = ev.paused ? ev.level : null; break;
      case 'paused': st.phase = 'paused'; break;
      case 'resumed': st.phase = 'round'; break;
      case 'done': st.done = true; st.phase = 'done'; break;
      case 'engine_exit': if (!st.done) { st.phase = ev.code === 0 ? 'done' : 'stopped'; } st.training = null; break;
      case 'error': st.error = ev.message; break;
      default: break;
    }
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

  function plugSvg() {
    const s = el('svg', { viewBox: '0 0 44 36', class: 'plug', 'aria-hidden': 'true' },
      el('path', { d: 'M1 18 H14', class: 'body', style: 'stroke:var(--ink3);stroke-width:3;fill:none;stroke-linecap:round' }),
      el('rect', { x: 12, y: 10, width: 13, height: 16, rx: 3, class: 'body', style: 'fill:var(--ink2)' }),
      el('rect', { x: 25, y: 13, width: 7, height: 2.6, rx: 1, class: 'prong', style: 'fill:var(--ink3)' }),
      el('rect', { x: 25, y: 20.4, width: 7, height: 2.6, rx: 1, class: 'prong', style: 'fill:var(--ink3)' }),
      el('rect', { x: 31, y: 5, width: 12, height: 26, rx: 4, style: 'fill:#fff;stroke:var(--ink3);stroke-width:1.5' }),
      el('circle', { cx: 37, cy: 14.3, r: 1.5, style: 'fill:var(--ink3)' }),
      el('circle', { cx: 37, cy: 21.7, r: 1.5, style: 'fill:var(--ink3)' }));
    return s;
  }

  function chipFor(st, fed, dev) {
    const kc = fed === 'anchor_full' ? 'k-anchor' : 'k-starter';
    const nm = fed === 'anchor_full' ? 'AnchorLoRA' : 'Starter';
    if (st.training && st.training.fed === fed && st.training.device === dev) {
      return h('span', { class: `chip ${kc} st-pending` }, `${nm}: training ${st.training.steps}/${st.training.planned} steps…`);
    }
    const last = st.recs[fed][st.current] || st.recs[fed][st.current - 1];
    if (!last) return h('span', { class: `chip ${kc}` }, `${nm}: –`);
    const d = last.devices[dev];
    const [done, plan] = d.steps;
    let label, cls;
    if (d.state === 'fresh') { label = done < plan ? `fresh, partial ${done}/${plan}` : `fresh ${done}/${plan}`; cls = 'st-fresh'; }
    else if (fed === 'anchor_full' && d.memory === 'reused') { label = `reusing last update · age ${d.memory_age}/4`; cls = 'st-reused'; }
    else if (fed === 'anchor_full' && d.memory === 'expired') { label = `memory expired · age ${d.memory_age} > 4`; cls = 'st-expired'; }
    else if (d.state === 'unplugged') { label = 'unplugged · nothing used'; cls = 'st-unplugged'; }
    else if (d.state === 'discarded') { label = `late: ${d.scheduled_steps}/${plan} steps, discarded`; cls = 'st-discarded'; }
    else { label = 'offline this round'; cls = 'st-unplugged'; }
    return h('span', { class: `chip ${kc} ${cls}`, title: `round ${last.round}` }, h('b', {}, `${nm}: `), label);
  }

  function renderSockets() {
    const st = S();
    const running = view === 'live' && ['starting', 'loading', 'loaded', 'ready', 'round', 'paused'].includes(st.phase);
    const ul = $('#sockets');
    ul.replaceChildren(...DEV.map((d) => {
      const pend = st.pending[d.id];
      const out = st.out.has(d.id);
      const willOut = pend ? pend.cmd === 'unplug' : out;
      const b = h('button', { type: 'button', class: 'sock', 'data-dev': d.id, 'data-out': willOut ? '1' : '0',
        'data-training': st.training && st.training.device === d.id ? '1' : '0',
        'aria-pressed': willOut ? 'true' : 'false',
        'aria-label': `${d.cls}: ${willOut ? 'plug pulled, click to restore' : 'plugged in, click to pull the plug'}` });
      if (!running) b.disabled = true;
      const sub = `${DOMNAME[d.domain]} · rank ${d.rank} · ${d.steps} steps${d.id === 'c0' ? ' · 8× data' : ''}`;
      const info = h('div', {}, h('div', { class: 'dname' }, d.cls), h('div', { class: 'dsub' }, sub));
      const chips = h('div', { class: 'chips' });
      if (pend) chips.append(h('span', { class: 'chip st-pending' }, pend.cmd === 'unplug' ? `plug pulled · out from round ${pend.eff}` : `plugged back · in from round ${pend.eff}`));
      else if (out && st.outRounds[d.id]) chips.append(h('span', { class: 'chip st-unplugged' }, `unplugged since round ${st.outRounds[d.id][0]}`));
      for (const f of FEDS) chips.append(chipFor(st, f, d.id));
      info.append(chips);
      b.append(plugSvg(), info);
      b.addEventListener('click', () => togglePlug(d.id, willOut));
      return h('li', {}, b);
    }));
  }

  async function post(url, body) {
    const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
    return r.json().catch(() => ({}));
  }
  function togglePlug(dev, isOut) {
    if (view !== 'live') return;
    post('api/cmd', { cmd: isOut ? 'replug' : 'unplug', device: dev });
  }

  function drawLiveBars(fed) {
    const st = S();
    const host = $(`#live-bars-${fed}`);
    const W = 500, H = 214, m = { l: 48, r: 58, t: 12, b: 38 };
    const rr = LIVE_RANGE, y = scale(-rr, rr, H - m.b, m.t);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}` });
    const g = el('g');
    yAxis(g, y, -rr, rr, m.l, W - m.r, niceStep(2 * rr, 6), (v) => fmt(v, 2));
    const rec = st.recs[fed][st.current] || st.recs[fed][st.current - 1];
    const gh = ghostFor(st.seed);
    const gw = (W - m.l - m.r) / DOMS.length, bw = gw * 0.56;
    DOMS.forEach((d, i) => {
      const cx = m.l + gw * i + gw / 2;
      if (rec) {
        const v = -rec.delta[d];
        const vv = Math.max(-rr, Math.min(rr, v));
        g.append(el('rect', { x: cx - bw / 2, y: Math.min(y(0), y(vv)), width: bw, height: Math.max(1, Math.abs(y(vv) - y(0))), rx: 3,
          style: `fill:${COL[fed][1]};transition:all 300ms` }));
        g.append(txt(cx, v >= 0 ? y(vv) - 6 : y(vv) + 15, fmt(v), { 'text-anchor': 'middle', 'font-size': 13, 'font-weight': 700, style: `fill:${COL[fed][0]}` }));
        const gr = gh && gh[fed] && gh[fed][String(rec.round)];
        if (gr) {
          const gv = Math.max(-rr, Math.min(rr, -gr[d]));
          g.append(el('line', { x1: cx - bw / 2 - 6, x2: cx + bw / 2 + 6, y1: y(gv), y2: y(gv), style: 'stroke:var(--ink);stroke-width:2;stroke-dasharray:4 3' }));
        }
      }
      const dev = DEV.find((x) => x.domain === d);
      g.append(txt(cx, H - m.b + 17, DOMSHORT[d], { 'text-anchor': 'middle', 'font-size': 13, 'font-weight': 700, style: d === 'manpages' ? 'fill:var(--sim)' : 'fill:var(--ink)' }));
      g.append(txt(cx, H - m.b + 32, dev.cls, { 'text-anchor': 'middle', 'font-size': 11.5 }));
    });
    g.append(txt(W - m.r + 6, y(0) + 4, 'untuned', { 'font-size': 12.5, 'font-weight': 700, style: 'fill:var(--ink)' }));
    if (!rec) g.append(txt((W - m.r + m.l) / 2, y(0) - 14, st.untuned ? 'untuned model measured; waiting for round 1' : 'no round yet', { 'text-anchor': 'middle', 'font-size': 14 }));
    svg.append(g);
    host.replaceChildren(svg);
    const line = $(`#fedline-${fed}`);
    if (!rec) { line.textContent = '↑ better than the untuned model, ↓ worse · dashed tick = ghost (nobody unplugged)'; return; }
    const parts = [`Round ${rec.round}: fresh updates ${rec.fresh}/5`];
    if (fed === 'anchor_full') {
      const reused = Object.entries(rec.devices).filter(([, d]) => d.memory === 'reused').map(([c, d]) => `${DEVBY[c].cls} (age ${d.memory_age}/4)`);
      const expired = Object.entries(rec.devices).filter(([, d]) => d.memory === 'expired').map(([c, d]) => `${DEVBY[c].cls} (age ${d.memory_age})`);
      parts.push(reused.length ? `reused memory: ${reused.join(', ')}` : 'no memory reused');
      if (expired.length) parts.push(`memory expired: ${expired.join(', ')}`);
    } else {
      const disc = Object.entries(rec.devices).filter(([, d]) => d.state === 'discarded').map(([c]) => DEVBY[c].cls);
      if (disc.length) parts.push(`late work discarded: ${disc.join(', ')}`);
    }
    parts.push(`workstation norm share ${rec.norm_share && rec.norm_share.c0 != null ? rec.norm_share.c0.toFixed(2) : '–'}`);
    parts.push(`train ${rec.train_s.toFixed(1)} s · eval ${rec.eval_s.toFixed(1)} s`);
    line.textContent = parts.join(' · ');
  }

  function drawCurve() {
    const st = S();
    const host = $('#live-curve');
    const R = st.rounds || 6;
    const W = 960, H = 200, m = { l: 54, r: 150, t: 18, b: 34 };
    const gh = ghostFor(st.seed);
    const band = VAL && VAL.results && VAL.results.band;
    let mx = 0.05;
    for (const f of FEDS) {
      for (const r of Object.values(st.recs[f])) mx = Math.max(mx, Math.abs(r.delta.manpages));
      if (gh && gh[f]) for (const v of Object.values(gh[f])) mx = Math.max(mx, Math.abs(v.manpages));
      if (band && band[`unplug.${f}`]) for (const [a, b] of Object.values(band[`unplug.${f}`])) mx = Math.max(mx, Math.abs(a), Math.abs(b));
    }
    mx *= 1.15;
    const x = scale(0, R, m.l, W - m.r), y = scale(-mx, mx, H - m.b, m.t);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}` });
    const tabletOut = st.outRounds.c4 || [];
    for (const r of tabletOut) svg.append(el('rect', { x: x(r - 0.5), y: m.t, width: x(Math.min(r + 0.5, R)) - x(r - 0.5), height: H - m.b - m.t, style: 'fill:#ece6f6' }));
    if (tabletOut.length) svg.append(txt(x(tabletOut[0] - 0.5) + 4, m.t - 5, `tablet unplugged from round ${tabletOut[0]}`, { 'font-size': 12, 'font-weight': 700, style: 'fill:var(--sim)' }));
    const others = Object.entries(st.outRounds).filter(([d]) => d !== 'c4');
    others.forEach(([d, rs], i) => svg.append(txt(x(rs[0] - 0.5) + 4, H - m.b - 6 - 14 * i, `${DEVBY[d].cls} unplugged from round ${rs[0]}`, { 'font-size': 11.5 })));
    const g = el('g');
    yAxis(g, y, -mx, mx, m.l, W - m.r, niceStep(2 * mx, 6), (v) => fmt(v, 2));
    for (let r = 0; r <= R; r += 1) g.append(txt(x(r), H - m.b + 18, String(r), { 'text-anchor': 'middle', 'font-size': 12 }));
    g.append(txt(W - m.r + 8, H - m.b + 18, 'round', { 'font-size': 12 }));
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
      const pts = [[0, 0]].concat(Object.values(st.recs[f]).map((r) => [r.round, -r.delta.manpages]).sort((p, q) => p[0] - q[0]));
      if (pts.length > 1) {
        svg.append(el('path', { d: pts.map(([r, v], i) => `${i ? 'L' : 'M'}${x(r)},${y(v)}`).join(''), style: `fill:none;stroke:${COL[f][0]};stroke-width:3.5;stroke-linejoin:round` }));
        for (const [r, v] of pts.slice(1)) svg.append(el('circle', { cx: x(r), cy: y(v), r: 4.5, style: `fill:${COL[f][0]}` }));
        const [lr, lv] = pts.at(-1);
        ends.push({ f, x: x(lr) + 9, y: y(lv) + 4, v: lv });
      }
    }
    for (const e of spread(ends, 16)) svg.append(txt(e.x, e.y, `${e.f === 'anchor_full' ? 'AnchorLoRA' : 'Starter'} ${fmt(e.v)}`, { 'font-size': 14, 'font-weight': 700, style: `fill:${COL[e.f][0]}` }));
    host.replaceChildren(svg);
    $('#legend-curve').replaceChildren(
      h('span', {}, h('i', { class: 'line', style: 'background:var(--starter)' }), 'Starter'),
      h('span', {}, h('i', { class: 'line', style: 'background:var(--anchor)' }), 'AnchorLoRA'),
      h('span', {}, h('i', { class: 'dash', style: 'color:var(--ink2)' }), 'ghost: pre-recorded by this engine, same config and seed, nobody unplugged (demo/validation)'),
      band ? h('span', {}, h('i', { class: 'band', style: 'background:var(--ink3)' }), 'range over 5 seeds, scripted unplug of the tablet from round 2 (pre-registered validation)') : '',
      h('span', {}, '↑ better than untuned'));
    // live vs ghost before the first unplug: computed here, on screen
    const firstOut = Math.min(Infinity, ...Object.values(st.outRounds).map((rs) => rs[0]));
    let maxd = null, n = 0;
    if (gh) for (const f of FEDS) for (const r of Object.values(st.recs[f])) {
      if (r.round >= firstOut || !gh[f] || !gh[f][String(r.round)]) continue;
      for (const d of DOMS) { const dd = Math.abs(r.delta[d] - gh[f][String(r.round)][d]); maxd = Math.max(maxd || 0, dd); n += 1; }
    }
    const src = $('#curve-src');
    let effect = '';
    const lastR = Math.max(0, ...Object.keys(st.recs.anchor_full).map(Number));
    if (gh && tabletOut.length && lastR >= tabletOut[0] && st.recs.fedavg_ab_homo[lastR] && gh.anchor_full && gh.anchor_full[String(lastR)]) {
      const eff = (f) => st.recs[f][lastR].delta.manpages - gh[f][String(lastR)].manpages;
      const p3 = VAL && VAL.results && VAL.results.verdict && VAL.results.verdict.P3;
      effect = `The unplug's own effect on man pages at round ${lastR} (this run − ghost; positive = worse): Starter ${fmt(eff('fedavg_ab_homo'))}, AnchorLoRA ${fmt(eff('anchor_full'))}.`
        + (p3 ? ' Pre-registered check P3 (round 6, tablet out from round 2): larger for the starter in all 5 validation seeds. ' : ' ');
    }
    src.replaceChildren(
      n ? `Before the first unplug this run matches its ghost: max |live − ghost| = ${maxd === 0 ? '0 (bit-identical)' : maxd.toExponential(1)} over ${n} values. ` : '',
      effect,
      gh ? h('span', {}, 'Ghost: ', h('code', {}, gh.file), '. ') : 'No ghost for this seed yet. ',
      VAL ? h('span', {}, 'Band: ', h('code', {}, VAL.file), '. ') : '',
      `Values: man-page loss of the untuned model minus the current model's, on 8 held-out blocks × 64 tokens.`);
  }

  function renderStatus() {
    const st = S();
    const pill = $('#livepill');
    const label = $('#livelabel');
    let text, pstate = 'idle';
    if (view === 'recorded') {
      label.dataset.mode = 'recorded';
      label.textContent = `RECORDED, not live · validation run, seed 0, tablet unplugged by script from round 2 · ${REC ? REC.file : ''} · same reduced config · Δ vs untuned on the same eval subset`;
      pstate = 'recorded';
      text = st.done ? 'RECORDED run finished.' : `RECORDED playback · round ${st.current || 0}/${st.rounds}`;
    } else {
      label.dataset.mode = 'live';
      label.textContent = 'LIVE · reduced config (batch 1×64, eval 8×64 tok/domain, 6 rounds) · Δ vs untuned on the same eval subset · not comparable in absolute terms to committed runs';
      const ph = st.phase;
      if (!avail.checked) text = 'Checking the live engine…';
      else if (!avail.ok && ph === 'idle') { text = `Live engine unavailable here: ${avail.why.join('; ') || 'open the page through demo/run.sh'}. Use "Play RECORDED run".`; pstate = 'failed'; }
      else if (ph === 'idle') text = `Ready. Starting loads SmolLM2-135M on this CPU (one copy, nice 10, 4 threads), then trains both federations side by side.`;
      else if (ph === 'starting' || ph === 'loading' || ph === 'loaded') { text = `Loading the real SmolLM2-135M on CPU…${st.loadS ? ` (${st.loadS.toFixed(1)} s)` : ''}`; pstate = 'loading'; }
      else if (ph === 'ready') { text = `Untuned model measured${st.identical ? ' (both federations start identical)' : ''}. Round 1 starting.`; pstate = 'running'; }
      else if (ph === 'round' || ph === 'paused') {
        const tr = st.training ? ` · ${st.training.fed === 'anchor_full' ? 'AnchorLoRA' : 'Starter'}: ${DEVBY[st.training.device].cls} training ${st.training.steps} steps` : '';
        const lw = st.roundWall[st.current - 1];
        text = `Round ${st.current}/${st.rounds}${tr}${lw ? ` · last round ${lw.toFixed(0)} s` : ''}${ph === 'paused' ? ' · will pause after this round' : ''}`;
        pstate = ph === 'paused' ? 'paused' : 'running';
      } else if (ph === 'done') text = `Live run finished: ${st.rounds} rounds, seed ${st.seed}.`;
      else if (ph === 'stopped') text = 'Live run stopped.';
      if (st.error) text += ` Error: ${st.error}`;
      if (avail.memory != null) text += ` · memory level ${avail.memory}`;
    }
    if (st.memPaused != null) pstate = 'memory';
    $('#livestatus').textContent = text;
    const mb = $('#membanner');
    mb.hidden = st.memPaused == null;
    if (st.memPaused != null) $('#memlvl').textContent = String(st.memPaused);
    pill.dataset.state = pstate;
    pill.textContent = view === 'recorded' ? 'RECORDED' : `LIVE · ${pstate === 'running' ? `round ${st.current || 0}/${st.rounds}` : pstate === 'memory' ? 'paused for memory' : pstate === 'loading' ? 'loading' : st.phase === 'done' ? 'finished' : avail.ok ? 'ready' : 'unavailable'}`;
    const running = view === 'live' && ['starting', 'loading', 'loaded', 'ready', 'round', 'paused'].includes(st.phase);
    $('#btn-start').disabled = !avail.ok || running;
    $('#btn-pause').disabled = !running;
    $('#btn-pause').textContent = st.phase === 'paused' ? 'Resume' : 'Pause after this round';
    $('#btn-stop').disabled = !running;
    $('#btn-recorded').disabled = !REC;
    $('#btn-recorded').textContent = view === 'recorded' && !st.done ? 'Stop RECORDED playback' : 'Play RECORDED run';
    $('#footstate').textContent = st.prov ? `engine commit ${st.prov.commit} · code_sha ${st.prov.code_sha}` : '';
  }

  function renderLive() { renderSockets(); for (const f of FEDS) drawLiveBars(f); drawCurve(); renderStatus(); }

  // ---- RECORDED playback ------------------------------------------------------------------------------
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
      renderLive();
      if (i < evs.length) recTimer = setTimeout(tick, 120); else { recTimer = null; ST.recorded.done = true; renderLive(); }
    };
    tick();
  }

  // ---- server link ------------------------------------------------------------------------------------
  async function poll() {
    if (location.protocol === 'file:') { avail = { checked: true, ok: false, why: ['page opened as a file: run demo/run.sh for the live engine'], memory: null }; renderStatus(); return; }
    try {
      const r = await fetch('api/status', { cache: 'no-store' });
      const s = await r.json();
      avail = { checked: true, ok: s.live_available, why: s.why || [], memory: s.memory_level, state: s.state };
    } catch (e) {
      avail = { checked: true, ok: false, why: ['demo server not reachable'], memory: null };
    }
    renderStatus();
  }
  function connect() {
    if (location.protocol === 'file:' || !window.EventSource) return;
    const es = new EventSource('api/events');
    let queued = false;
    es.onmessage = (m) => {
      const ev = JSON.parse(m.data);
      if (ev.ev === 'server_start' || ST.live.runId == null || ev.run_id === ST.live.runId) onEvent(ST.live, ev);
      if (view === 'live' && !queued) { queued = true; requestAnimationFrame(() => { queued = false; renderLive(); }); }
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
    history.replaceState(null, '', `#${name}`);
  }
  for (const t of TABS) $(`#tab-${t}`).addEventListener('click', () => show(t));
  window.addEventListener('hashchange', () => { const n = location.hash.slice(1); if (TABS.includes(n)) show(n); });
  document.addEventListener('keydown', (e) => {
    if (e.target && (e.target.tagName === 'SELECT' || e.target.tagName === 'INPUT')) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const i = ['1', '2', '3', '4'].indexOf(e.key);
    if (i >= 0) show(TABS[i]);
    if ((e.key === 's' || e.key === 'S') && !$('#btn-start').disabled) { show('live'); $('#btn-start').click(); }
    if (e.key === 't' || e.key === 'T') { const b = document.querySelector('.sock[data-dev="c4"]'); if (b && !b.disabled) b.click(); }
  });
  $('#livepill').addEventListener('click', () => show('live'));
  for (const sel of ['#strip-seed', '#live-seed']) $(sel).replaceChildren(...D.seeds.map((s) => h('option', { value: String(s) }, String(s))));
  $('#strip-seed').addEventListener('change', drawStrip);
  $('#strip-play').addEventListener('click', playStrip);
  $('#btn-start').addEventListener('click', async () => {
    stopRecorded();
    view = 'live';
    const r = await post('api/start', { seed: Number($('#live-seed').value) });
    if (r.error) { ST.live.error = r.error + (r.why ? `: ${r.why.join('; ')}` : ''); }
    renderLive();
  });
  $('#btn-pause').addEventListener('click', () => post('api/cmd', { cmd: S().phase === 'paused' ? 'resume' : 'pause' }));
  $('#btn-stop').addEventListener('click', () => post('api/stop'));
  $('#btn-recorded').addEventListener('click', () => {
    if (view === 'recorded' && !ST.recorded.done && recTimer) { stopRecorded(); view = 'live'; renderLive(); return; }
    playRecorded();
  });
  $('#legend-strip').textContent = '● full · ◐ partial kept · ✕ discarded · – offline · ↺ memory';

  drawGains();
  drawLedger();
  drawOutage();
  drawStrip();
  drawCosts();
  renderLive();
  poll();
  setInterval(poll, 4000);
  connect();
  const start = (location.hash || '').slice(1);
  show(TABS.includes(start) ? start : 'real');
  window.__P1_READY = true;
})();
