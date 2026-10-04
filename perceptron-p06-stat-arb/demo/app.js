/* P6 demo page. Renders from assets/data.js alone (OFFLINE: precomputed grid exported by demo/build_assets.py) and
   upgrades to LIVE when the backend (demo/server.py) answers: then the window numbers are recomputed by committed
   code on every change and checked against the exported grid. No network beyond 127.0.0.1. */
"use strict";
(() => {
  const P = window.P6_DATA;
  if (!P) { document.body.innerHTML = "<p style='padding:24px'>demo/assets/data.js is missing: run demo/build_assets.py.</p>"; return; }
  const M = P.meta, C = P.committed, H = C.headline;
  const LEGS = M.legs, DELTAS = M.deltas_ms, RTS = M.rts_ms, MACH_D = M.machine_D_us;
  const NAME = { "binance:BTCUSDT": "Binance spot", "binance-futures:BTCUSDT": "Binance perp", "coinbase:BTC-USD": "Coinbase",
    "okex:BTC-USDT": "OKX spot", "okex-swap:BTC-USDT-SWAP": "OKX perp" };
  const QUOTE_CCY = l => (l.startsWith("coinbase") ? "USD" : "USDT");
  const fileKey = l => l.replace(":", "_");
  const cadence = l => (C.cadence[fileKey(l)] || {}).median_gap_ms;
  const $ = id => document.getElementById(id);
  const W_MS = (M.w1_us - M.w0_us) / 1000;
  const fmtUsd = (x, d = 0) => (x < 0 ? "−$" : "+$") + Math.abs(x).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  const fmtMs = ms => (ms < 0.1 ? `${(ms * 1000).toFixed(0)} µs` : ms < 10 ? `${+ms.toPrecision(2)} ms` : `${ms.toFixed(0)} ms`);
  const pygKey = k => { const [s, f, d, D] = k.split("|"); return `${s}|${+f.slice(1)}|${+d.slice(1)}|${+D.slice(1)}`; };
  const key = (sim, fee, d, Dus) => `${sim}|${fee}|${d}|${Dus}`;
  const GW = new Map(Object.entries(P.grid_window).map(([k, v]) => [pygKey(k), v]));
  const GD = new Map(Object.entries(P.grid_day).map(([k, v]) => [pygKey(k), v]));
  const utc = us => new Date(us / 1000).toISOString().slice(11, 23);

  // ---------------------------------------------------------------- data decoding
  const Q = LEGS.map(l => {
    const q = P.quotes[l], n = q.t_us_delta.length, t = new Float64Array(n), bid = new Float64Array(n), ask = new Float64Array(n);
    let tt = 0, bb = 0, aa = 0;
    for (let i = 0; i < n; i++) { tt += q.t_us_delta[i]; bb += q.bid_c_delta[i]; aa += q.ask_c_delta[i]; t[i] = tt / 1000; bid[i] = bb / 100; ask[i] = aa / 100; }
    return { t, bid, ask, n, last: -1, pulse: 0 };
  });
  const E = P.episodes, NE = E.t_us.length;
  const eS = Float64Array.from(E.t_us, x => x / 1000), eE = Float64Array.from(E.t_us.map((x, i) => (x + E.dur_us[i]) / 1000));
  const CAND = {}, CIDX = {};
  for (const f of M.fees) {
    const c = P.cands[String(f)]; CAND[f] = c; CIDX[f] = new Map(c.opp_id.map((o, i) => [o, i]));
  }
  const nearestIdx = (grid, x) => grid.reduce((bi, g, i) => (Math.abs(Math.log(g) - Math.log(x)) < Math.abs(Math.log(grid[bi]) - Math.log(x)) ? i : bi), 0);
  const kmS = (curve, tms) => { let lo = 0, hi = curve.t_ms.length - 1, j = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (curve.t_ms[m] <= tms) { j = m; lo = m + 1; } else hi = m - 1; } return j < 0 ? 1 : curve.S[j]; };

  // ---------------------------------------------------------------- state
  const S = { sim: "frozen", fee: 1, di: DELTAS.indexOf(1), playing: false, speed: 1, t: 0, live: false, ready: false, api: null,
    timing: null, liveRes: null, liveKey: "", race: null, linger: new Map(), probes: 0 };
  const delta = () => DELTAS[S.di];
  const machineL = () => 2 * delta() + MACH_D / 1000;
  const levInRange = () => delta() >= M.lev_delta_range_ms[0] && delta() <= M.lev_delta_range_ms[1];

  // ---------------------------------------------------------------- canvases (crisp on retina)
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  const CV = {};
  function fit(id, aspect) {
    const c = $(id), w = c.parentElement.clientWidth - (id === "scrub" ? 260 : 0);
    const W = Math.max(200, id === "scrub" ? c.getBoundingClientRect().width || w : c.parentElement.clientWidth - 24), Hh = Math.round(W * aspect);
    c.width = Math.round(W * dpr); c.height = Math.round(Hh * dpr); c.style.height = Hh + "px";
    const ctx = c.getContext("2d"); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    CV[id] = { c, ctx, W, H: Hh };
  }
  function layout() { fit("pent", 0.56); fit("clocks", 0.27); fit("front", 0.46); fit("scrub", 0.07); drawScrub(); drawFront(); }

  // ---------------------------------------------------------------- honesty strip, presets, notes
  const w0 = utc(M.w0_us).slice(0, 5), w1 = utc(M.w1_us).slice(0, 5);
  $("honesty").innerHTML = `Replay of <b>recorded</b> Tardis quotes · ${M.test_day} (held-out test day) ${w0}–${w1} UTC · 5 BTC legs · window = ${M.window_rule} ·
    every $ is <b>SIMULATED execution surplus</b> (basis-adjusted, ≤ ${M.q_max_btc} BTC per opportunity, inventory assumed pre-positioned), <b>not earned P&amp;L</b> ·
    not a live trading system: the detector ran in batch, open-time features are causal.`;
  const feed = C.feed_tardis_ms, mac = C.feed_mac_india_p05_ms;
  const macOkx = mac["okex:BTC-USDT"], macCb = mac["coinbase:BTC-USD"];
  const presets = [
    { lab: "colo-style", v: 0.01, note: "hypothetical" },
    { lab: "Binance perp feed p50", v: feed["binance-futures:BTCUSDT"].p50, note: "Tardis collector" },
    { lab: "OKX spot feed p50", v: feed["okex:BTC-USDT"].p50, note: "Tardis collector" },
    { lab: "Coinbase feed p50", v: feed["coinbase:BTC-USD"].p50, note: "Tardis collector" },
    { lab: "this laptop (India) → OKX, p05", v: macOkx, note: "measured" },
    { lab: "this laptop (India) → Coinbase, p05", v: macCb, note: "measured" },
  ];
  $("presets").innerHTML = presets.map((p, i) => `<button class="chip" data-i="${i}">${p.lab} <small>${fmtMs(p.v)} · ${p.note}</small></button>`).join("");
  $("presets").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    S.di = nearestIdx(DELTAS, presets[+b.dataset.i].v); $("delta").value = S.di; changed();
  });
  $("delta").max = DELTAS.length - 1; $("delta").value = S.di;
  $("delta").addEventListener("input", e => { S.di = +e.target.value; changed(); });
  for (const [id, prop, parse] of [["fee", "fee", Number], ["sim", "sim", String], ["speed", "speed", Number]]) {
    $(id).addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b || (S.race && S.race.running)) return;
      for (const x of $(id).children) x.classList.toggle("on", x === b);
      S[prop] = parse(b.dataset.v); if (prop !== "speed") changed();
    });
  }
  $("play").addEventListener("click", () => { if (S.race && S.race.running) return; if (S.t >= W_MS) S.t = 0; S.playing = !S.playing; rebuildActive(); updatePlay(); });
  const updatePlay = () => { $("play").textContent = S.playing ? "❚❚ Pause" : "▶ Play"; };

  // ---------------------------------------------------------------- live backend
  const API = location.protocol.startsWith("http") ? "" : "http://127.0.0.1:8766";
  async function api(path) { const r = await fetch(API + path, { cache: "no-store" }); if (!r.ok) throw new Error(r.status); return r.json(); }
  async function pollStatus() {
    try {
      const s = await api("/api/status");
      S.live = true; S.ready = s.ready; S.timing = s.timing || S.timing;
      setMode(s.ready ? "live" : "warming", s.ready ? "LIVE · committed code recomputing on this machine" : `LIVE (warming) · ${s.stage}`);
      if (!S.liveRes) refreshLive();
      if (!s.ready) setTimeout(pollStatus, 700); else { refreshLive(); renderEvidence(); renderRaceRule(); }
    } catch (e) {
      S.live = false; setMode("offline", "OFFLINE · precomputed grid (same code, exported)");
      if (++S.probes < 24) setTimeout(pollStatus, 5000);   // a backend started up to 2 min after the page still upgrades it
    }
  }
  function setMode(cls, txt) { const m = $("mode"); m.className = "mode " + cls; m.textContent = txt; }
  let liveSeq = 0;
  async function refreshLive() {
    if (!S.live) return;
    const k = key(S.sim, S.fee, delta(), MACH_D), seq = ++liveSeq;
    try {
      const r = await api(`/api/eval?sim=${S.sim}&fee=${S.fee}&delta=${delta()}`);
      if (seq !== liveSeq) return;
      S.liveRes = r; S.liveKey = k; renderCounters();
    } catch (e) { /* stay on the exported grid */ }
  }

  // ---------------------------------------------------------------- per-config results (live when available, else exported)
  function winRec(sim, fee, d, Dus) { return GW.get(key(sim, fee, d, Dus)); }
  function current() {
    const k = key(S.sim, S.fee, delta(), MACH_D), g = GW.get(k);
    if (S.live && S.liveRes && S.liveKey === k) return { src: "live", tot: S.liveRes.tot, oc: S.liveRes.oc, pnl: S.liveRes.pnl, g, r: S.liveRes };
    return { src: "grid", tot: g.tot, oc: g.oc, pnlc: g.pnl_c, g };
  }
  function candOutcome(fee, oppId) {
    const i = CIDX[fee].get(oppId); if (i === undefined) return null;
    const cur = current();
    const oc = cur.src === "live" ? cur.oc[i] : (cur.g.oc[i] === "-" ? -1 : +cur.g.oc[i]);
    const pnl = cur.src === "live" ? cur.pnl[i] : cur.g.pnl_c[i] / 100;
    return { oc, pnl };
  }

  function changed() {
    const d = delta();
    $("deltaRead").innerHTML = `<span class="big">${fmtMs(d)}</span><span class="small">one-way · L = 2δ + 7 µs = ${fmtMs(machineL())} end-to-end</span>`;
    $("simnote").innerHTML = S.sim === "frozen"
      ? "<b>Frozen</b> (the pre-registered primary): each IOC leg fills against the <b>last published</b> quote at arrival, up to its displayed size."
      : "<b>Strict V1</b> (Amendment 1): each leg fills against the <b>next published</b> quote after arrival; size-0 intents are not sent; threshold and LEV are <b>refit on strict 09-01 labels</b>.";
    S.liveRes = null; renderCounters(); drawFront(); drawScrub(); refreshLive();
    if (S.race && S.race.result && !S.race.running) scoreRace(false);   // same reaction times, new δ / simulator
    if (S.race !== undefined) renderRaceRule();
  }

  // ---------------------------------------------------------------- counters
  function renderCounters() {
    const cur = current(), dayk = GD.get(key(S.sim, S.fee, delta(), MACH_D));
    const rows = [["naive", "naive", "act on every mispricing whose edge beats both fees", "var(--naive)"],
      ["thr", "tuned threshold", `per-pair θ re-tuned on ${M.train_day} at this δ`, "var(--thr)"],
      ["lev", "LEV", `learned E[surplus | x, L]; trained on ${M.train_day} at δ = 1/5/20 ms`, "var(--lev)"]];
    const tb = $("ctab").querySelector("tbody"); tb.innerHTML = "";
    for (const [p, name, sub, col] of rows) {
      const w = cur.tot[p], dd = dayk[p];
      const tr = document.createElement("tr");
      if (p === "lev" && !levInRange()) tr.className = "hatched";
      const cls = x => (x > 0.005 ? "pos" : x < -0.005 ? "neg" : "");
      tr.innerHTML = `<td><span class="pol" style="background:${col}"></span>${name}<small>${sub}</small></td>
        <td class="${cls(w.usd)}">${fmtUsd(w.usd, 2)}</td><td>${w.n} · ${w.n_both}<small>${w.n ? fmtUsd(w.usd / w.n, 3) + " / trade" : "no trades"}</small></td>
        <td class="${cls(dd.usd)}">${fmtUsd(dd.usd)}<small>${dd.n.toLocaleString()} trades</small></td>`;
      tb.appendChild(tr);
    }
    $("levnote").innerHTML = (levInRange() ? "" : `<b>LEV hatched:</b> δ = ${fmtMs(delta())} is outside the latencies LEV was trained on (1–20 ms one-way); its value here is shown for reference only. `) +
      `Window: ${CAND[S.fee].opp_id.length} opportunities with net edge &gt; 0 at ${S.fee} bp/leg (of ${M.window_episodes.toLocaleString()} detected); day: ${M.day_candidates[String(S.fee)].toLocaleString()} (of ${M.day_episodes.toLocaleString()}).`;
    if (cur.src === "live") {
      const g = cur.g; let same = true;
      for (const p of ["naive", "thr", "lev"]) if (Math.abs(g.tot[p].usd - cur.tot[p].usd) > 1e-6 || g.tot[p].n !== cur.tot[p].n) same = false;
      for (let i = 0; i < cur.oc.length && same; i++) {
        const go = g.oc[i] === "-" ? -1 : +g.oc[i];
        if (go !== cur.oc[i] || Math.abs(g.pnl_c[i] / 100 - cur.pnl[i]) > 0.0051) same = false;
      }
      $("liveok").innerHTML = (same ? `<span style="color:var(--mach)">✓ recomputed live (${cur.r.elapsed_ms.toFixed(0)} ms) = exported grid</span>` : `<span style="color:var(--neg)">⚠ live ≠ exported grid</span>`) +
        ` · LEV via ${cur.r.lev_engine.split(" ")[0]}`;
    } else $("liveok").textContent = S.live ? "waiting for live recompute…" : "exported grid (backend off)";
  }

  // ---------------------------------------------------------------- frontier (day scope)
  const asinhY = v => Math.asinh(v / 100);
  function drawFront() {
    const cv = CV.front; if (!cv) return; const { ctx, W, H: Hh } = cv;
    ctx.clearRect(0, 0, W, Hh);
    const padL = 54, padR = 10, padT = 12, padB = 30;
    const xmin = Math.log10(0.015), xmax = Math.log10(3000);
    const series = { naive: [], thr: [], lev: [] };
    for (const d of DELTAS) { const g = GD.get(key(S.sim, S.fee, d, MACH_D)); for (const p in series) series[p].push([2 * d + MACH_D / 1000, g[p].usd, d]); }
    const human = S.fee === M.race_fee ? RTS.map(rt => { const g = GD.get(key(S.sim, S.fee, delta(), rt * 1000)); return [2 * delta() + rt, g.naive.usd, g.thr.usd]; }) : [];
    const allY = [...series.naive, ...series.thr, ...series.lev].map(p => p[1]).concat(human.flatMap(h => [h[1], h[2]]));
    const ymin = asinhY(Math.min(-1000, ...allY)), ymax = asinhY(Math.max(1000, ...allY));
    const X = l => padL + (Math.log10(l) - xmin) / (xmax - xmin) * (W - padL - padR);
    const Y = v => padT + (ymax - asinhY(v)) / (ymax - ymin) * (Hh - padT - padB);
    ctx.font = "11px -apple-system, sans-serif"; ctx.fillStyle = "#5b6886"; ctx.strokeStyle = "#23304d"; ctx.lineWidth = 1;
    for (const v of [-10000, -1000, -100, 0, 100, 1000]) {
      if (asinhY(v) < ymin || asinhY(v) > ymax) continue;
      ctx.beginPath(); ctx.moveTo(padL, Y(v)); ctx.lineTo(W - padR, Y(v)); ctx.strokeStyle = v === 0 ? "#6b7aa0" : "#1c2742"; ctx.stroke();
      ctx.fillText(v === 0 ? "$0" : (v > 0 ? "+" : "−") + "$" + Math.abs(v).toLocaleString(), 4, Y(v) + 4);
    }
    for (const l of [0.01, 0.1, 1, 10, 100, 1000]) { ctx.fillText(fmtMs(l), X(l) - 12, Hh - 14); ctx.beginPath(); ctx.moveTo(X(l), padT); ctx.lineTo(X(l), Hh - padB); ctx.strokeStyle = "#1c2742"; ctx.stroke(); }
    ctx.fillText("end-to-end latency L = feed + decision + order (log)", W / 2 - 120, Hh - 2);
    // machine series
    const col = { naive: "#ff6b6b", thr: "#4aa8ff", lev: "#b58bff" };
    for (const p of ["naive", "thr", "lev"]) {
      const pts = series[p];
      for (let i = 1; i < pts.length; i++) {
        const out = p === "lev" && (pts[i][2] > M.lev_delta_range_ms[1] || pts[i - 1][2] < M.lev_delta_range_ms[0]);
        ctx.setLineDash(out ? [3, 4] : []); ctx.globalAlpha = out ? 0.45 : 1;
        ctx.beginPath(); ctx.moveTo(X(pts[i - 1][0]), Y(pts[i - 1][1])); ctx.lineTo(X(pts[i][0]), Y(pts[i][1])); ctx.strokeStyle = col[p]; ctx.lineWidth = 2; ctx.stroke();
      }
      ctx.setLineDash([]); ctx.globalAlpha = 1;
    }
    for (const pt of series.lev) if (M.reg_deltas_ms.includes(pt[2])) dot(ctx, X(pt[0]), Y(pt[1]), 3.5, "#b58bff");
    [["naive", "#ff6b6b"], ["tuned threshold", "#4aa8ff"], ["LEV (● trained latencies; dashed = outside)", "#b58bff"]].forEach(([t, c], k) => {
      const lx = padL + 8 + [0, 62, 175][k]; ctx.fillStyle = c; ctx.fillRect(lx, Hh - padB - 34, 14, 3); ctx.fillText(t, lx + 18, Hh - padB - 30);
    });
    // human (reaction-time) points at the current δ
    if (human.length) {
      ctx.fillStyle = "rgba(255,210,63,.18)"; ctx.fillRect(X(2 * delta() + RTS[0]), padT, X(2 * delta() + RTS[RTS.length - 1]) - X(2 * delta() + RTS[0]), Hh - padT - padB);
      for (const [l, n, t] of human) { dot(ctx, X(l), Y(n), 2.5, "#ff6b6b"); dot(ctx, X(l), Y(t), 2.5, "#4aa8ff"); }
      ctx.fillStyle = "#ffd23f"; ctx.fillText("human RTs", X(2 * delta() + RTS[0]) + 3, padT + 10); ctx.fillText("100 ms–2 s", X(2 * delta() + RTS[0]) + 3, padT + 23);
    }
    // current machine L and the race result
    ctx.strokeStyle = "#ffd23f"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(X(machineL()), padT); ctx.lineTo(X(machineL()), Hh - padB); ctx.stroke();
    ctx.fillStyle = "#ffd23f"; ctx.fillText("machine", X(machineL()) + 3, Hh - padB - 4);
    const R = S.race;
    if (R && R.result) {
      const l = 2 * delta() + R.result.rtGrid, g = GD.get(key(S.sim, S.fee, delta(), R.result.rtGrid * 1000));
      if (g) { ctx.strokeStyle = "#ffd23f"; ctx.setLineDash([2, 3]); ctx.beginPath(); ctx.moveTo(X(l), padT); ctx.lineTo(X(l), Hh - padB); ctx.stroke(); ctx.setLineDash([]);
        dot(ctx, X(l), Y(g.naive.usd), 6, "#ffd23f"); ctx.fillText("YOU", X(l) - 34, Y(g.naive.usd) + 4); }
    }
    // zero-crossing note (no interpolation: report the bracketing grid points)
    const nv = series.naive; let cross = "";
    for (let i = 1; i < nv.length; i++) if (nv[i - 1][1] > 0 && nv[i][1] <= 0) { cross = `between δ = ${fmtMs(nv[i - 1][2])} and ${fmtMs(nv[i][2])} one-way`; break; }
    $("frontnote").innerHTML = `Full held-out day, ${S.fee} bp/leg, ${S.sim === "frozen" ? "frozen" : "strict V1"}: naive's day total ${cross ? "first turns negative " + cross : nv[0][1] <= 0 ? "is negative at every latency" : "stays positive on this grid"}; ` +
      `tuned threshold at the machine's L: ${fmtUsd(GD.get(key(S.sim, S.fee, delta(), MACH_D)).thr.usd)}. Yellow band = human reaction times (naive red, threshold blue; the threshold re-tuned at human speed trades nothing).`;
  }
  function dot(ctx, x, y, r, c) { ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = c; ctx.fill(); }

  // ---------------------------------------------------------------- replay: active episodes
  let active = [], ePtr = 0;
  function rebuildActive() {
    active = []; let lo = 0, hi = NE; while (lo < hi) { const m = (lo + hi) >> 1; if (eS[m] <= S.t) lo = m + 1; else hi = m; }
    ePtr = lo; for (let i = 0; i < lo; i++) if (eE[i] + 150 > S.t) active.push(i);
    for (const q of Q) q.last = -1;
  }
  function advanceActive() {
    while (ePtr < NE && eS[ePtr] <= S.t) active.push(ePtr++);
    active = active.filter(i => eE[i] + 150 > S.t);
  }
  const lastIdx = (q, t) => { let lo = 0, hi = q.n - 1, j = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (q.t[m] <= t) { j = m; lo = m + 1; } else hi = m - 1; } return j; };

  // pentagon layout: Coinbase on top; same-exchange legs adjacent
  const NR = 46;
  const ORDER = ["coinbase:BTC-USD", "binance:BTCUSDT", "binance-futures:BTCUSDT", "okex-swap:BTC-USDT-SWAP", "okex:BTC-USDT"];
  function nodePos(W, Hh) {
    const cx = W * 0.5, cy = Hh * 0.5 + 6, r = Math.min(W * 0.34, Hh * 0.36);
    const pos = {}; ORDER.forEach((l, k) => { const a = -Math.PI / 2 + k * 2 * Math.PI / 5; pos[LEGS.indexOf(l)] = [cx + r * Math.cos(a), cy + r * Math.sin(a)]; });
    return pos;
  }
  function drawPent(now) {
    const cv = CV.pent; if (!cv) return; const { ctx, W, H: Hh } = cv; ctx.clearRect(0, 0, W, Hh);
    const pos = nodePos(W, Hh), candSet = CIDX[S.fee], tgt = S.race && S.race.target;
    // arcs: buy venue -> sell venue
    for (const i of active) {
      const isC = candSet.has(E.opp_id[i]), open = S.t < eE[i], isT = tgt && tgt.opp === E.opp_id[i] && S.race.state === "flash";
      if (S.race && S.race.running && !isT && S.race.state === "flash") continue;
      const a = pos[E.b[i]], b = pos[E.s[i]], e = E.edge0[i];
      const fade = open ? 1 : Math.max(0, 1 - (S.t - eE[i]) / 150);
      const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, cx = W * 0.5, cy = Hh * 0.5 + 6;
      const bend = 0.25, qx = mx + (mx - cx) * bend, qy = my + (my - cy) * bend;
      ctx.globalAlpha = fade * (isC ? 0.95 : 0.35);
      ctx.strokeStyle = isT ? "#ffd23f" : isC ? "#ffb347" : "#5f72a8"; ctx.lineWidth = isT ? 7 : Math.min(1 + e * 0.9, 9);
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.quadraticCurveTo(qx, qy, b[0], b[1]); ctx.stroke();
      arrowHead(ctx, qx, qy, b[0], b[1], ctx.strokeStyle, isT ? 16 : 9);
      if (isC || isT) { ctx.globalAlpha = fade; ctx.fillStyle = isT ? "#ffd23f" : "#ffcf8a"; ctx.font = "bold 12px -apple-system, sans-serif"; ctx.fillText(`+${e.toFixed(1)} bp`, qx - 18, qy - 4); }
      ctx.globalAlpha = 1;
    }
    // nodes with publication heartbeat
    ctx.font = "600 13px -apple-system, sans-serif";
    LEGS.forEach((l, i) => {
      const q = Q[i], j = lastIdx(q, S.t);
      if (j !== q.last) { if (j > q.last && q.last >= 0) q.pulse = 1; q.last = j; }
      const [x, y] = pos[i], perp = l.includes("futures") || l.includes("SWAP");
      if (q.pulse > 0.02) { ctx.beginPath(); ctx.arc(x, y, NR + 2 + 10 * (1 - q.pulse), 0, Math.PI * 2); ctx.strokeStyle = `rgba(62,230,160,${q.pulse})`; ctx.lineWidth = 2; ctx.stroke(); q.pulse *= 0.86; }
      ctx.beginPath(); ctx.arc(x, y, NR, 0, Math.PI * 2); ctx.fillStyle = "#0f1628"; ctx.fill(); ctx.strokeStyle = perp ? "#b58bff" : "#4aa8ff"; ctx.lineWidth = 2; ctx.stroke();
      ctx.fillStyle = "#e8edf7"; ctx.textAlign = "center"; ctx.fillText(NAME[l], x, y - 6);
      ctx.font = "12px -apple-system, sans-serif"; ctx.fillStyle = "#93a1bd";
      ctx.fillText(j >= 0 ? ((q.bid[j] + q.ask[j]) / 2).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "—", x, y + 10);
      ctx.fillStyle = "#5b6886"; ctx.font = "11px -apple-system, sans-serif"; ctx.fillText(QUOTE_CCY(l), x, y + 24);
      ctx.fillText(`publishes every ~${cadence(l) >= 10 ? cadence(l).toFixed(0) : cadence(l).toFixed(1)} ms`, x, y + NR + 14);
      ctx.textAlign = "left"; ctx.font = "600 13px -apple-system, sans-serif";
    });
    ctx.fillStyle = "#5b6886"; ctx.font = "11px -apple-system, sans-serif";
    ctx.fillText("arrow = buy at the tail venue, sell at the head venue · orange = net edge > 0 after fees · ring = a quote was published", 10, Hh - 8);
    ctx.fillText(`${active.filter(i => S.t < eE[i]).length} open now`, 10, 16);
  }
  function arrowHead(ctx, fx, fy, x, y, c, s) {
    const a = Math.atan2(y - fy, x - fx), bx = x - Math.cos(a) * (NR + 2), by = y - Math.sin(a) * (NR + 2);
    ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(bx - s * Math.cos(a - 0.4), by - s * Math.sin(a - 0.4)); ctx.lineTo(bx - s * Math.cos(a + 0.4), by - s * Math.sin(a + 0.4)); ctx.closePath(); ctx.fillStyle = c; ctx.fill();
  }

  // ---------------------------------------------------------------- decay clocks
  const OCG = { "-1": ["not sent (size 0)", "#5b6886"], 0: ["✗ both legs missed", "#93a1bd"], 1: ["½ sell leg only, unwound", "#ffb347"], 2: ["½ buy leg only, unwound", "#ffb347"], 3: ["✓ both legs filled", "#3ee6a0"] };
  function drawClocks(now) {
    const cv = CV.clocks; if (!cv) return; const { ctx, W, H: Hh } = cv; ctx.clearRect(0, 0, W, Hh);
    const candSet = CIDX[S.fee];
    for (const i of active) if (candSet.has(E.opp_id[i]) && !S.linger.has(i)) S.linger.set(i, null);
    for (const [i, closedAt] of S.linger) {
      if (S.t >= eE[i] && closedAt === null) S.linger.set(i, now);
      if (closedAt !== null && now - closedAt > 1600) S.linger.delete(i);
      if (eS[i] > S.t) S.linger.delete(i);
    }
    const rows = [...S.linger.keys()].sort((a, b) => eS[b] - eS[a]).slice(0, 6);
    const x0 = 250, x1 = W - 165, lmin = Math.log10(0.3), lmax = Math.log10(3000), X = ms => x0 + (Math.log10(Math.max(ms, 0.3)) - lmin) / (lmax - lmin) * (x1 - x0);
    ctx.font = "11px -apple-system, sans-serif"; ctx.fillStyle = "#5b6886";
    for (const ms of [1, 10, 100, 1000]) { ctx.fillText(fmtMs(ms), X(ms) - 10, 12); ctx.fillRect(X(ms), 16, 1, Hh - 20); }
    const L = machineL(), rowH = (Hh - 22) / 6;
    ctx.fillStyle = "#ffd23f"; ctx.fillText("▼ machine order lands", X(L) - 50, Hh - 2);
    rows.forEach((i, r) => {
      const y = 22 + r * rowH, s = LEGS[E.s[i]], b = LEGS[E.b[i]];
      const floor = Math.max(cadence(s) || 0, cadence(b) || 0);
      ctx.fillStyle = "#1a2440"; ctx.fillRect(x0, y + 4, x1 - x0, rowH - 10);
      ctx.fillStyle = "rgba(147,161,189,.18)"; ctx.fillRect(x0, y + 4, X(floor) - x0, rowH - 10);
      const open = S.t < eE[i], el = Math.max(0.3, (open ? S.t : eE[i]) - eS[i]);
      ctx.fillStyle = open ? "#ffb347" : "#7d6a4d"; ctx.fillRect(x0, y + 7, X(el) - x0, rowH - 16);
      ctx.fillStyle = "#ffd23f"; ctx.fillRect(X(L) - 1, y + 2, 2, rowH - 6);
      ctx.fillStyle = "#e8edf7"; ctx.font = "12px -apple-system, sans-serif";
      ctx.fillText(`buy ${NAME[b]} → sell ${NAME[s]}`, 6, y + rowH / 2 - 1);
      ctx.fillStyle = "#93a1bd"; ctx.font = "11px -apple-system, sans-serif";
      ctx.fillText(`+${E.edge0[i].toFixed(2)} bp · ${open ? "open " + fmtMs(el) : E.dur_us[i] === 0 ? "closed within the same exchange timestamp" : "closed after " + fmtMs(E.dur_us[i] / 1000)}`, 6, y + rowH / 2 + 12);
      if (S.t - eS[i] >= L || !open) {
        const o = candOutcome(S.fee, E.opp_id[i]);
        if (o) { const [txt, c] = OCG[o.oc]; ctx.fillStyle = c; ctx.font = "12px -apple-system, sans-serif"; ctx.fillText(txt, x1 + 6, y + rowH / 2 - 1); ctx.fillStyle = o.pnl >= 0 ? "#3ee6a0" : "#ff6b6b"; ctx.fillText(fmtUsd(o.pnl, 2), x1 + 6, y + rowH / 2 + 12); }
      }
    });
    if (!rows.length) { ctx.fillStyle = "#5b6886"; ctx.font = "13px -apple-system, sans-serif"; ctx.fillText("press ▶ — clocks start when a mispricing beats fees at the chosen fee", x0, Hh / 2); }
  }

  // ---------------------------------------------------------------- scrubber
  function drawScrub() {
    const cv = CV.scrub; if (!cv) return; const { ctx, W, H: Hh } = cv; ctx.clearRect(0, 0, W, Hh);
    const bins = 90, cnt = new Array(bins).fill(0), c = CAND[S.fee];
    for (const t of c.t_start_us) cnt[Math.min(bins - 1, Math.floor((t - M.w0_us) / 1000 / W_MS * bins))]++;
    const mx = Math.max(...cnt, 1);
    cnt.forEach((n, i) => { ctx.fillStyle = "#2b3a60"; const h = (Hh - 6) * n / mx; ctx.fillRect(i * W / bins, Hh - h, W / bins - 1, h); });
    ctx.fillStyle = "#ffd23f"; ctx.fillRect(S.t / W_MS * W - 1, 0, 2, Hh);
  }
  $("scrub").addEventListener("click", e => {
    if (S.race && S.race.running) return;
    const r = e.target.getBoundingClientRect(); S.t = (e.clientX - r.left) / r.width * W_MS; rebuildActive(); S.linger.clear();
  });

  // ---------------------------------------------------------------- race the machine
  function renderRaceRule() {
    const p50 = S.timing && S.timing.p50_us ? `${S.timing.p50_us.toFixed(1)} µs (live p50, this machine)` : `${(C.decision_timing.in_kernel_ns.p50 / 1e3).toFixed(2)} µs (committed decision_timing.json p50; backend off)`;
    $("raceRule").innerHTML = `<b>Rule, fixed before the trials:</b> the replay jumps to a random moment of the window and plays at <b>1× wall clock</b> (speed and scrubbing locked).
      After a random 1.5–4 s wait, the <b>next mispricing with net edge &gt; 0 at ${M.race_fee} bp/leg</b> flashes yellow (no repeats within a race). Press <b>SPACE</b> (or click the replay) as soon as you see it.
      Your reaction time includes this screen's display lag and your keyboard's input lag; a feed handler's latency includes its own, so yours counts too.
      Every trial is reported (false starts are listed and re-armed; no press within 2 s counts as 2 s). Your order then leaves at δ + RT and lands at δ + RT + δ;
      the machine's leaves at δ + ${p50}. Same opportunities, same simulator (${S.sim === "frozen" ? "frozen" : "strict V1"}), δ = ${fmtMs(delta())}.`;
  }
  $("raceBtn").addEventListener("click", () => {
    if (S.race && S.race.running) return;
    S.race = { running: true, trials: [], log: [], state: "idle", target: null, used: new Set() };
    document.querySelector(".replay").scrollIntoView({ behavior: "instant", block: "start" });
    for (const x of document.querySelectorAll("#speed button")) x.classList.toggle("on", x.dataset.v === "1");
    S.speed = 1; armTrial(); renderTrials();
  });
  function armTrial() {
    const R = S.race, c = CAND[M.race_fee];
    for (let tries = 0; tries < 200; tries++) {
      const s = Math.random() * (W_MS - 45000), fp = 1500 + Math.random() * 2500;
      const j = c.t_start_us.findIndex((t, i) => (t - M.w0_us) / 1000 >= s + fp && !R.used.has(c.opp_id[i]));
      if (j >= 0 && (c.t_start_us[j] - M.w0_us) / 1000 - (s + fp) < 30000) {
        R.used.add(c.opp_id[j]);
        R.target = { opp: c.opp_id[j], t: (c.t_start_us[j] - M.w0_us) / 1000, s: LEGS.indexOf(c.sell_venue[j]), b: LEGS.indexOf(c.buy_venue[j]), edge: c.edge0_bps[j],
          net: c.net0_bps[j], dur: c.duration_us[j] / 1000 };
        S.t = s; rebuildActive(); S.linger.clear(); S.playing = true; updatePlay(); R.state = "wait"; R.flashAt = null;
        showFlash("wait", `Trial ${R.trials.length + 1} of 5 · watch for the yellow flash · replay at 1×`);
        $("raceStatus").textContent = `trial ${R.trials.length + 1}/5 armed`;
        return;
      }
    }
  }
  function showFlash(kind, html) { const f = $("flash"); f.className = "flash" + (kind === "wait" ? " wait" : ""); f.innerHTML = html; }
  function raceTick(now) {
    const R = S.race; if (!R || !R.running) return;
    if (R.state === "wait" && S.t >= R.target.t) {
      R.state = "flash"; R.flashAt = now;
      document.querySelector(".replay").classList.add("flashing");
      showFlash("flash", `NOW · buy ${NAME[LEGS[R.target.b]]} / sell ${NAME[LEGS[R.target.s]]} · +${R.target.edge.toFixed(2)} bp`);
    } else if (R.state === "flash" && now - R.flashAt > 2000) record(2000, true);
  }
  function onPress(ev) {
    const R = S.race; if (!R || !R.running) return;
    if (ev.type === "keydown" && ev.code !== "Space" && ev.code !== "Enter") return;
    ev.preventDefault();
    if (R.state === "wait") { R.log.push({ falseStart: true }); renderTrials(); showFlash("wait", "False start (pressed before the flash) · re-arming…"); R.state = "pause"; setTimeout(armTrial, 900); }
    else if (R.state === "flash") record(Math.max(1, ev.timeStamp - R.flashAt), false);
  }
  document.addEventListener("keydown", onPress);
  $("pent").addEventListener("pointerdown", onPress);
  function record(rt, timeout) {
    const R = S.race; R.state = "pause"; document.querySelector(".replay").classList.remove("flashing");
    const tr = { ...R.target, rt, timeout }; R.trials.push(tr); R.log.push(tr);
    showFlash("wait", timeout ? "No press within 2 s · counted as 2,000 ms" : `Your reaction time: ${rt.toFixed(0)} ms`);
    renderTrials();
    if (R.trials.length < 5) setTimeout(armTrial, 1300); else setTimeout(finishRace, 900);
  }
  function median(a) { const s = [...a].sort((x, y) => x - y), n = s.length; return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2; }
  async function finishRace() {
    const R = S.race; R.running = false; S.playing = false; updatePlay(); $("flash").className = "flash hidden";
    await scoreRace(true);
  }
  let raceSeq = 0;
  async function scoreRace(scroll) {
    const R = S.race, seq = ++raceSeq;
    const rts = R.trials.map(t => t.rt), rtMed = median(rts), rtGrid = RTS[nearestIdx(RTS, rtMed)];
    const fee = M.race_fee, d = delta(), ids = R.trials.map(t => t.opp);
    const res = { rtMed, rtGrid, d, sim: S.sim, src: "grid" };
    const gY = winRec(S.sim, fee, d, rtGrid * 1000), gM = winRec(S.sim, fee, d, MACH_D), iOf = o => CIDX[fee].get(o);
    res.you = { naive: gY.tot.naive, thr: gY.tot.thr, L: 2 * d + rtGrid };
    res.mach = { naive: gM.tot.naive, thr: gM.tot.thr, L: 2 * d + MACH_D / 1000, D_us: MACH_D, D_src: `${(C.decision_timing.in_kernel_ns.p50 / 1e3).toFixed(2)} µs committed p50 (decision_timing.json); offline replay uses the walk-forward's 7 µs compute allowance` };
    res.trials = R.trials.map(t => {
      const gk = winRec(S.sim, fee, d, RTS[nearestIdx(RTS, t.rt)] * 1000), i = iOf(t.opp);
      const oc = c => (c === "-" ? -1 : +c);
      return { you: { oc: oc(gk.oc[i]), pnl: gk.pnl_c[i] / 100, note: `RT snapped to ${RTS[nearestIdx(RTS, t.rt)]} ms grid` }, mach: { oc: oc(gM.oc[i]), pnl: gM.pnl_c[i] / 100 } };
    });
    if (S.live) {
      try {
        const all = await api(`/api/race?rt=${rtMed.toFixed(1)}&delta=${d}&sim=${S.sim}&ids=${ids.join(",")}`);
        res.src = "live"; res.you = { naive: all.you.naive, thr: all.you.thr, L: all.you.L_ms }; res.rtGrid = all.rt_threshold_grid_ms;
        res.mach = { naive: all.machine.naive, thr: all.machine.thr, L: all.machine.L_ms, D_us: all.machine_D_us, D_src: `${all.machine_D_us.toFixed(2)} µs = ${all.machine_D_source}` };
        const ocMap = { none: 0, sell_only: 1, buy_only: 2, both: 3, "not sent": -1 };
        res.trials = await Promise.all(R.trials.map(async (t, k) => {
          const one = await api(`/api/race?rt=${t.rt.toFixed(1)}&delta=${d}&sim=${S.sim}&ids=${t.opp}`);
          const y = one.you.trials[0], m = one.machine.trials[0];
          return { you: { oc: ocMap[y.outcome], pnl: y.pnl_usd, note: "exact RT, live" }, mach: { oc: ocMap[m.outcome], pnl: m.pnl_usd } };
        }));
      } catch (e) { res.src = "grid"; }
    }
    if (seq !== raceSeq) return;
    R.result = res; renderTrials(); renderTwo(); drawFront();
    if (scroll) document.querySelector("section.race").scrollIntoView({ behavior: "smooth", block: "start" });
    $("raceStatus").textContent = res.src === "live" ? "computed live by committed code" : "offline: exported grid (RT snapped)";
  }
  function renderTrials() {
    const R = S.race, tb = $("trials").querySelector("tbody"); tb.innerHTML = ""; if (!R) return;
    let k = 0;
    R.log.forEach(t => {
      const tr = document.createElement("tr");
      if (t.falseStart) { tr.innerHTML = `<td>—</td><td colspan="4" style="text-align:left;color:var(--warn)">false start (pressed before the flash), re-armed</td>`; tb.appendChild(tr); return; }
      const idx = k++, res = R.result && R.result.trials[idx];
      const L = 2 * delta() + t.rt, gone = t.dur < L;
      const cell = o => (o ? `<span style="color:${OCG[o.oc][1]}">${OCG[o.oc][0]}</span> <b class="${o.pnl >= 0 ? "pos" : "neg"}">${fmtUsd(o.pnl, 2)}</b>` : "…");
      tr.innerHTML = `<td>${idx + 1}</td><td>buy ${NAME[LEGS[t.b]]} / sell ${NAME[LEGS[t.s]]} · +${t.edge.toFixed(2)} bp<br><small style="color:var(--dim)">${t.dur === 0 ? "closed within the same exchange timestamp" : "lived " + fmtMs(t.dur)}${gone ? " · gone before your order landed" : ""}</small></td>
        <td><b>${t.timeout ? "≥ 2,000" : t.rt.toFixed(0)} ms</b></td><td>${res ? cell(res.you) : "…"}</td><td>${res ? cell(res.mach) : "…"}</td>`;
      tb.appendChild(tr);
    });
  }
  function renderTwo() {
    const r = S.race.result, tb = $("two").querySelector("tbody"), cls = x => (x > 0.005 ? "pos" : x < -0.005 ? "neg" : "");
    const cell = a => `<td class="${cls(a.usd)}">${fmtUsd(a.usd, 2)}<small>${a.n} trades · ${a.n_both} both legs</small></td>`;
    tb.innerHTML = `<tr><td style="color:var(--you)"><b>you</b><small>δ + ${r.rtMed.toFixed(0)} ms + δ</small></td>${cell(r.you.naive)}${cell(r.you.thr)}</tr>
      <tr><td style="color:var(--mach)"><b>machine</b><small>δ + ${r.mach.D_us.toFixed(1)} µs + δ</small></td>${cell(r.mach.naive)}${cell(r.mach.thr)}</tr>`;
    const km = P.km.cands_f1, goneY = 1 - kmS(km, r.you.L), goneM = 1 - kmS(km, r.mach.L);
    const ratio = r.rtMed * 1000 / r.mach.D_us;
    $("raceSummary").innerHTML = `This 15-min window, ${M.race_fee} bp/leg, δ = ${fmtMs(r.d)}, ${r.sim === "frozen" ? "frozen" : "strict V1"} simulator. Your median RT <b>${r.rtMed.toFixed(0)} ms</b> is <b>${Math.round(ratio).toLocaleString()}×</b> the machine's decision step (${r.mach.D_src}).
      When your order landed (L ≈ ${fmtMs(r.you.L)}), <b>${(100 * goneY).toFixed(0)}%</b> of this window's mispricings with net edge &gt; 0 had already closed; at the machine's L (${fmtMs(r.mach.L)}): <b>${(100 * goneM).toFixed(0)}%</b>
      (Kaplan–Meier on the window's ${km.n} such episodes; closed = edge back within 1 bp of the fair basis).
      The selector is re-tuned on ${M.train_day} at your speed (grid ${r.rtGrid} ms): it ${r.you.thr.n ? "trades " + r.you.thr.n + " times" : "declines to trade"}.
      ${r.src === "live" ? "Computed live by the committed simulator at your exact RT." : "Offline: RT snapped to the exported grid."} Change δ or the simulator: your reaction times stay and the table is rescored.`;
  }

  // ---------------------------------------------------------------- committed evidence
  function renderEvidence() {
    const f1 = x => fmtUsd(x, Math.abs(x) < 10 ? 1 : 0);
    const wf = C.walkforward_v0, v1 = C.v1, v2 = C.v2, ci = c => `[${f1(c[0])}, ${f1(c[1])}]`;
    const tn0 = wf["threshold_pair - naive"], tn1 = v1["threshold_pair - naive"], lt0 = wf["lev - threshold_pair"], lt1 = v1["lev - threshold_pair"], lt2 = v2["lev - threshold_pair"], s3 = C.s3_v2;
    const dt = C.decision_timing.in_kernel_ns, live = S.timing && S.timing.p50_us;
    const cards = [
      ["Robust: latency-aware selection beats naive", `Tuned threshold − naive, pre-registered 12-month walk-forward: <b>${fmtUsd(tn0.mean_usd_per_day)}/day</b>, t-CI ${ci(tn0.t_ci95)}, ${tn0.days_positive}/${tn0.n_days} days (frozen); under strict fills <b>${fmtUsd(tn1.mean_usd_per_day)}/day</b>, ${tn1.days_positive}/${tn1.n_days}. Naive's held-out-day surplus turns negative at <b>${H.be_naive} ms</b> one-way (1 bp/leg, 9 legs).`, "falsification_walkforward_12d_prereg.json · sensitivity_amendment1.json · latency_budget.json"],
      ["LEV vs threshold: a benchmark, not a validated edge", `Frozen (pre-registered): <b>${fmtUsd(lt0.mean_usd_per_day)}/day</b>, t-CI ${ci(lt0.t_ci95)}, ${lt0.days_positive}/${lt0.n_days}. Strict next-quote fills: <b>${fmtUsd(lt1.mean_usd_per_day)}</b> ${ci(lt1.t_ci95)} (${H.v1_share}); + 1 s markout: ${fmtUsd(lt2.mean_usd_per_day)} ${ci(lt2.t_ci95)}; shared-liquidity collisions dropped: <b>${fmtUsd(s3.mean_usd_per_day)}</b> ${ci(s3.t_ci95)}, within noise.`, "sensitivity_amendment1.json"],
      ["How fast mispricings decay, and what we can't see", `Median lifetime <b>${H.median_life_ms} ms</b> (9 legs, KM, hour-block CI ${H.median_ci_lo}–${H.median_ci_hi}), bounded to ${H.med_lo}–${H.med_hi} ms by publication times; this window: ${P.km.episodes.median_ms.toFixed(1)} ms. Cadence floor: Binance spot and OKX publish on a <b>100 ms grid</b>, Binance perp every <b>26 ms</b> in these samples, so shorter lifetimes are unobservable. Our own recorder sees Binance perp every ${H.live_bnf_ms} ms.`, "decay_report.md · update_cadence.json · live_cadence.json"],
      ["The budget is distance, not compute", `Compiled decision step (features + LEV + act): <b>${(dt.p50 / 1e3).toFixed(1)} µs p50 / ${(dt.p99 / 1e3).toFixed(1)} µs p99</b> committed${live ? `; <b>${S.timing.p50_us.toFixed(1)} / ${S.timing.p99_us.toFixed(1)} µs measured now on this machine</b> (${S.timing.n_calls.toLocaleString()} calls, exact vs sklearn: ${S.timing.exact_max_abs_err_bps.toExponential(0)} bp)` : ""}. Detector ${H.det_ns_event} ns/event. Feed one-way p50: ${H.feed_fast_ms}–${H.feed_slow_ms} ms (Tardis collector); from this laptop in India, p05 floors of ${C.feed_mac_india_p05_ms["okex-swap:BTC-USDT-SWAP"].toFixed(0)} ms (OKX perp) to ${C.feed_mac_india_p05_ms["coinbase:BTC-USD"].toFixed(0)} ms (Coinbase).`, "decision_timing.json · latency_budget.json"],
    ];
    $("cards").innerHTML = cards.map(([h, b, s]) => `<div class="card"><h3>${h}</h3>${b}<div class="src">eval/results/${s.split(" · ").join(" · eval/results/")}</div></div>`).join("");
    const ok = P.checks.filter(c => c.ok === true).length;
    $("foot").innerHTML = `Assets built by demo/build_assets.py from raw Tardis quotes (${M.train_day} train, ${M.test_day} test): ${ok}/${P.checks.length} reproduction checks passed. At δ = 1/5/20 ms the day-scope grid reproduces the committed 2026-10-01 totals for V0 (walk-forward) and V1 (strict). ` +
      `Strict V1 fills are a stress scenario; neither simulator is a fill model calibrated on our own orders. Paper trading is a stretch goal. Exact provenance: demo/assets/provenance.json.`;
  }

  // ---------------------------------------------------------------- main loop
  let lastNow = performance.now(), scrubTick = 0;
  function frame(now) {
    const dt = Math.min(now - lastNow, 250); lastNow = now;
    if (S.playing) { S.t += dt * S.speed; if (S.t >= W_MS) { S.t = W_MS; S.playing = false; updatePlay(); } }
    advanceActive(); drawPent(now); drawClocks(now); raceTick(now);
    $("clock").textContent = utc(M.w0_us + S.t * 1000) + " UTC";
    if (++scrubTick % 6 === 0) drawScrub();
    requestAnimationFrame(frame);
  }
  window.addEventListener("resize", layout);
  {
    const ts = CAND[M.race_fee].t_start_us.map(t => (t - M.w0_us) / 1000); let best = 0, bi = 0, j = 0;
    for (let i = 0; i < ts.length; i++) { while (ts[j] < ts[i] - 30000) j++; if (i - j + 1 > best) { best = i - j + 1; bi = j; } }
    S.t = Math.max(0, ts[bi] - 300);
  }
  layout(); changed(); renderEvidence(); renderRaceRule(); rebuildActive();
  requestAnimationFrame(frame);
  pollStatus();
  window.P6_STATE = S;   // for the headless smoke test and screenshots
})();
