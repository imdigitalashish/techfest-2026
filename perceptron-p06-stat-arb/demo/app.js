/* P6 demo page.
   OFFLINE: renders from assets/data.js alone (the grid exported by demo/build_assets.py with the committed code).
   LIVE: when the backend (demo/server.py) answers, the window numbers are recomputed by committed code on every change and
   checked against the exported grid. If the backend stops answering, every label says so and the page uses the grid.
   Views: a 3-step stage view for the talk (#stage-1..3, default) and the full dashboard for Q&A (#dashboard).
   No network beyond 127.0.0.1. */
"use strict";
window.__p6errors = [];   // read by demo/browser_check.py
window.addEventListener("error", e => window.__p6errors.push(String(e.message)));
window.addEventListener("unhandledrejection", e => window.__p6errors.push(String(e.reason)));
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
  const wallClock = () => new Date().toTimeString().slice(0, 8);
  const cls = x => (x > 0.005 ? "pos" : x < -0.005 ? "neg" : "");
  const simName = s => (s === "frozen" ? "frozen fills" : "strict V1 fills");
  const P50_COMMITTED_US = C.decision_timing.in_kernel_ns.p50 / 1e3;
  const SCEN_N = `${M.fees.length * M.reg_deltas_ms.length} fee/latency scenarios`;
  const SCEN = `${SCEN_N} (${M.fees.join(" and ")} bp/leg × δ ${M.reg_deltas_ms.join(", ")} ms)`;
  const RACE = { sim: "frozen", fee: M.race_fee, delta: 1, n: 5, deadlineS: 45, lead: [1500, 4000], timeoutMs: 2000 };

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
  for (const f of M.fees) { const c = P.cands[String(f)]; CAND[f] = c; CIDX[f] = new Map(c.opp_id.map((o, i) => [o, i])); }
  const nearestIdx = (grid, x) => grid.reduce((bi, g, i) => (Math.abs(Math.log(g) - Math.log(x)) < Math.abs(Math.log(grid[bi]) - Math.log(x)) ? i : bi), 0);
  const kmS = (curve, tms) => { let lo = 0, hi = curve.t_ms.length - 1, j = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (curve.t_ms[m] <= tms) { j = m; lo = m + 1; } else hi = m - 1; } return j < 0 ? 1 : curve.S[j]; };
  const median = a => { const s = [...a].sort((x, y) => x - y), n = s.length; return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2; };

  // ---------------------------------------------------------------- state
  const S = { sim: "frozen", fee: 1, di: DELTAS.indexOf(1), playing: false, speed: 1, t: 0,
    conn: "probing", connDetail: "", lostAt: "", timing: null, liveRes: null, liveKey: "", liveSeq: 0,
    race: null, linger: new Map(), preset: null, view: "stage", step: 1 };
  const delta = () => DELTAS[S.di];
  const isLive = () => S.conn === "live";
  const racing = () => !!(S.race && S.race.running);
  const machineL = () => 2 * delta() + MACH_D / 1000;
  const levInRange = () => delta() >= M.lev_delta_range_ms[0] && delta() <= M.lev_delta_range_ms[1];
  const cfgText = () => `${simName(S.sim)} · ${S.fee} bp/leg · δ ${fmtMs(delta())} one-way`;

  // ---------------------------------------------------------------- canvases (crisp on retina)
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  const CV = {};
  function fit(id, aspect) {
    const c = $(id);
    const W = Math.max(200, id === "scrub" ? c.getBoundingClientRect().width || 300 : c.parentElement.clientWidth - 24), Hh = Math.round(W * aspect);
    c.width = Math.round(W * dpr); c.height = Math.round(Hh * dpr); c.style.height = Hh + "px";
    const ctx = c.getContext("2d"); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    CV[id] = { c, ctx, W, H: Hh };
  }
  function layout() {
    const st = S.view === "stage", a = st ? { pent: S.step === 2 ? 0.49 : 0.46, clocks: 0.22, front: 0.52 } : { pent: 0.56, clocks: 0.27, front: 0.46 };
    fit("pent", a.pent); fit("clocks", a.clocks); fit("front", a.front); fit("scrub", 0.07); drawScrub(); drawFront();
  }

  // ---------------------------------------------------------------- static copy, presets, controls
  const w0 = utc(M.w0_us).slice(0, 5), w1 = utc(M.w1_us).slice(0, 5);
  const feed = C.feed_tardis_ms, mac = C.feed_mac_india_p05_ms;
  const MAC_NOTE = "receive−venue timestamp p05, clock offset unresolved";
  const presets = [
    { lab: "colo-style", v: 0.01, note: "hypothetical" },
    { lab: "Binance perp feed p50", v: feed["binance-futures:BTCUSDT"].p50, note: "venue → Tardis collector" },
    { lab: "OKX spot feed p50", v: feed["okex:BTC-USDT"].p50, note: "venue → Tardis collector" },
    { lab: "Coinbase feed p50", v: feed["coinbase:BTC-USD"].p50, note: "venue → Tardis collector" },
    { lab: "this Mac (India), OKX spot", v: mac["okex:BTC-USDT"], note: MAC_NOTE },
    { lab: "this Mac (India), Coinbase", v: mac["coinbase:BTC-USD"], note: MAC_NOTE },
  ];
  $("presets").innerHTML = presets.map((p, i) => `<button class="chip" data-i="${i}">${p.lab} <small>${fmtMs(p.v)} · ${p.note} · snaps to δ ${fmtMs(DELTAS[nearestIdx(DELTAS, p.v)])}</small></button>`).join("");
  const setSeg = (id, v) => { for (const x of $(id).children) x.classList.toggle("on", x.dataset.v === String(v)); };
  $("presets").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b || racing()) return;
    const p = presets[+b.dataset.i]; S.di = nearestIdx(DELTAS, p.v); $("delta").value = S.di; S.preset = p; changed();
  });
  $("delta").max = DELTAS.length - 1; $("delta").value = S.di;
  $("delta").addEventListener("input", e => { if (racing()) { e.target.value = S.di; return; } S.di = +e.target.value; S.preset = null; changed(); });
  for (const [id, prop, parse] of [["fee", "fee", Number], ["sim", "sim", String], ["speed", "speed", Number]]) {
    $(id).addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b || racing()) return;
      setSeg(id, b.dataset.v); S[prop] = parse(b.dataset.v); if (prop !== "speed") changed();
    });
  }
  $("play").addEventListener("click", () => { if (racing()) return; if (S.t >= W_MS) S.t = 0; S.playing = !S.playing; rebuildActive(); updatePlay(); });
  const updatePlay = () => { $("play").textContent = S.playing ? "❚❚ Pause" : "▶ Play"; };

  function renderStrips() {
    $("honesty").innerHTML = `Replay of <b>recorded</b> Tardis quotes · ${M.test_day} ${w0}–${w1} UTC (window rule: ${M.window_rule}) ·
      ${M.test_day} is held out from fitting (policies fitted on ${M.train_day}) but was one of the ${H.wf_inspected} previously inspected test days · 5 BTC legs ·
      every $ is <b>SIMULATED execution surplus</b> (basis-adjusted, ≤ ${M.q_max_btc} BTC per opportunity, inventory assumed pre-positioned), <b>not earned P&amp;L</b> ·
      not a live trading system: the detector ran in batch; open-time features are causal.`;
    const src = srcText(), live = src.startsWith("LIVE");
    $("scope").innerHTML = `<b>SIMULATED execution surplus, not P&amp;L</b> · recorded quotes ${M.test_day} ${w0}–${w1} UTC (densest 15 min by episode count), 5 BTC legs ·
      <span class="cfg">${cfgText()}</span> · <span class="src ${live ? "live" : "grid"}">${src}</span>`;
  }
  function srcText() {
    if (isLive()) return S.liveRes && S.liveKey === key(S.sim, S.fee, delta(), MACH_D) ? "LIVE recompute by committed code" : "LIVE · recomputing (exported grid meanwhile)";
    return { probing: "exported grid", offline: "exported grid (no backend)", warming: "exported grid (backend starting)",
      lost: `exported grid (backend lost at ${S.lostAt})`, error: "exported grid (backend error)" }[S.conn];
  }

  // ---------------------------------------------------------------- live backend: probe, heartbeat, timeouts, loss
  const API = location.protocol.startsWith("http") ? "" : "http://127.0.0.1:8766";
  async function api(path, ms) {
    const ac = new AbortController(), to = setTimeout(() => ac.abort(), ms);
    try {
      const r = await fetch(API + path, { cache: "no-store", signal: ac.signal });
      if (!r.ok) throw new Error("HTTP " + r.status);
      return await r.json();
    } catch (e) { throw new Error(e.name === "AbortError" ? `no answer within ${ms / 1000} s` : e.message); } finally { clearTimeout(to); }
  }
  let pollTimer = null, failures = 0;
  const pollLater = ms => { clearTimeout(pollTimer); pollTimer = setTimeout(pollStatus, ms); };
  async function pollStatus() {
    let s;
    try { s = await api("/api/status", 3000); } catch (e) {
      if (S.conn === "live" || S.conn === "warming") backendLost(`status check failed: ${e.message}`);
      else if (S.conn === "probing") setConn("offline");
      failures++; pollLater(failures < 24 ? 5000 : 15000); return;
    }
    failures = 0;
    if (s.error) { setConn("error", s.error); pollLater(15000); return; }
    if (s.ready) {
      S.timing = s.timing;
      if (!isLive()) { setConn("live"); refreshLive(); if (S.race && S.race.result && !racing()) scoreRace(false); }
      pollLater(5000);                                         // heartbeat: a dead backend is noticed within ~8 s
    } else { setConn("warming", s.stage); pollLater(700); }
  }
  function backendLost(reason) {
    if (!(S.conn === "live" || S.conn === "warming")) return;
    S.lostAt = wallClock(); S.liveRes = null; S.timing = null; S.liveSeq++;
    setConn("lost", reason); pollLater(5000);
  }
  function setConn(state, detail = "") {
    const was = S.conn + "|" + S.connDetail;
    S.conn = state; S.connDetail = detail;
    const txt = { probing: "checking for a live backend…", offline: "OFFLINE · exported grid (precomputed by the same committed code)",
      warming: "STARTING · backend warming up · exported grid meanwhile", live: "LIVE · committed code recomputing on this machine",
      lost: `OFFLINE · backend lost at ${S.lostAt} · exported grid · retrying`, error: "OFFLINE · backend error · exported grid" }[state];
    const m = $("mode");
    m.className = "mode " + ({ live: "live", warming: "warming", probing: "warming" }[state] || "offline");
    m.textContent = txt; m.title = detail;
    if (was !== state + "|" + detail) renderAll();
  }
  async function refreshLive() {
    if (!isLive()) return;
    const k = key(S.sim, S.fee, delta(), MACH_D), seq = ++S.liveSeq;
    try {
      const r = await api(`/api/eval?sim=${S.sim}&fee=${S.fee}&delta=${delta()}`, 10000);
      if (seq !== S.liveSeq || !isLive()) return;
      S.liveRes = r; S.liveKey = k; renderCounters(); renderBig(); renderStrips();
    } catch (e) { if (seq === S.liveSeq) backendLost(`live recompute failed: ${e.message}`); }
  }

  // ---------------------------------------------------------------- per-config results (live when available, else exported)
  function current() {
    const k = key(S.sim, S.fee, delta(), MACH_D), g = GW.get(k);
    if (isLive() && S.liveRes && S.liveKey === k) return { src: "live", tot: S.liveRes.tot, oc: S.liveRes.oc, pnl: S.liveRes.pnl, g, r: S.liveRes };
    return { src: "grid", tot: g.tot, g };
  }
  function candOutcome(fee, oppId) {
    const i = CIDX[fee].get(oppId); if (i === undefined) return null;
    const cur = current();
    if (cur.src === "live") return { oc: cur.oc[i], pnl: cur.pnl[i] };
    return { oc: cur.g.oc[i] === "-" ? -1 : +cur.g.oc[i], pnl: cur.g.pnl_c[i] / 100 };
  }
  function changed() {
    $("deltaRead").innerHTML = `<span class="big">${fmtMs(delta())}</span><span class="small">one-way · L = 2δ + 7 µs = ${fmtMs(machineL())} end-to-end</span>` +
      (S.preset ? `<span class="small">preset ${S.preset.lab}: ${fmtMs(S.preset.v)} (${S.preset.note}), snapped to the nearest grid δ</span>` : "");
    $("simnote").innerHTML = S.sim === "frozen"
      ? "<b>Frozen</b> (the pre-registered primary): each IOC leg fills against the <b>last published</b> quote at arrival, up to its displayed size."
      : "<b>Strict V1</b> (Amendment 1): each leg fills against the <b>next published</b> quote after arrival; size-0 intents are not sent; threshold and LEV are <b>refit on strict 09-01 labels</b>.";
    S.liveRes = null; renderAll(); drawScrub(); refreshLive();
    if (S.race && S.race.result && !racing()) scoreRace(false);     // same reaction times, rescored at the new δ / simulator
  }
  function renderAll() { renderStrips(); renderCounters(); renderBig(); renderRaceRule(); renderRaceSetup(); renderRaceStatus(); renderEvidence(); drawFront(); }

  // ---------------------------------------------------------------- counters and the one signed comparison
  function renderCounters() {
    const cur = current(), dayk = GD.get(key(S.sim, S.fee, delta(), MACH_D));
    const rows = [["naive", "naive", "act on every mispricing whose edge beats both fees", "var(--naive)"],
      ["thr", "tuned threshold", `per-pair θ re-tuned on ${M.train_day} at this δ`, "var(--thr)"],
      ["lev", "LEV", `learned E[surplus | x, L]; trained on ${M.train_day} at δ = ${M.reg_deltas_ms.join("/")} ms`, "var(--lev)"]];
    const tb = $("ctab").querySelector("tbody"); tb.innerHTML = "";
    for (const [p, name, sub, col] of rows) {
      const w = cur.tot[p], dd = dayk[p], tr = document.createElement("tr");
      if (p === "lev" && !levInRange()) tr.className = "hatched";
      tr.innerHTML = `<td><span class="pol" style="background:${col}"></span>${name}<small>${sub}</small></td>
        <td class="${cls(w.usd)}">${fmtUsd(w.usd, 2)}</td><td>${w.n} · ${w.n_both}<small>${w.n ? fmtUsd(w.usd / w.n, 3) + " / trade" : "no trades"}</small></td>
        <td class="${cls(dd.usd)}">${fmtUsd(dd.usd)}<small>${dd.n.toLocaleString()} trades</small></td>`;
      tb.appendChild(tr);
    }
    $("levnote").innerHTML = (levInRange() ? "" : `<b>LEV hatched:</b> δ = ${fmtMs(delta())} is outside the latencies LEV was trained on (${M.lev_delta_range_ms.join("–")} ms one-way); shown for reference only. `) +
      `Window: ${CAND[S.fee].opp_id.length} opportunities with net edge &gt; 0 at ${S.fee} bp/leg (of ${M.window_episodes.toLocaleString()} detected); day: ${M.day_candidates[String(S.fee)].toLocaleString()} (of ${M.day_episodes.toLocaleString()}). The day column is this one setup, not the multi-scenario score on the evidence cards.`;
    if (cur.src === "live") {
      const g = cur.g; let same = true;
      for (const p of ["naive", "thr", "lev"]) if (Math.abs(g.tot[p].usd - cur.tot[p].usd) > 1e-6 || g.tot[p].n !== cur.tot[p].n) same = false;
      for (let i = 0; i < cur.oc.length && same; i++) {
        const go = g.oc[i] === "-" ? -1 : +g.oc[i];
        if (go !== cur.oc[i] || Math.abs(g.pnl_c[i] / 100 - cur.pnl[i]) > 0.0051) same = false;
      }
      $("liveok").innerHTML = (same ? `<span style="color:var(--mach)">✓ recomputed live (${cur.r.elapsed_ms.toFixed(0)} ms) = exported grid</span>` : `<span style="color:var(--neg)">⚠ live ≠ exported grid</span>`) +
        ` · LEV via ${cur.r.lev_engine.split(" ")[0]}`;
    } else $("liveok").innerHTML = `<span style="color:var(--warn)">${srcText()}</span>`;
  }
  function renderBig() {
    const cur = current(), dayk = GD.get(key(S.sim, S.fee, delta(), MACH_D));
    const w = cur.tot.thr.usd - cur.tot.naive.usd, d = dayk.thr.usd - dayk.naive.usd;
    const tn0 = C.walkforward_v0["threshold_pair - naive"], tn1 = C.v1["threshold_pair - naive"];
    $("bigcmp").innerHTML = `<div class="ptitle"><span>Tuned threshold − naive · same opportunities</span><span class="hint">${cfgText()}</span></div>
      <div class="bigrow"><div><div class="kpi ${cls(w)}">${fmtUsd(w, 2)}</div><small>this 15-min window (${cur.src === "live" ? "live" : "exported grid"})</small></div>
      <div><div class="kpi ${cls(d)}">${fmtUsd(d)}</div><small>full held-out day, this one setup</small></div></div>
      <div class="note">Across <b>12 sampled first-of-month test days</b> (${H.wf_inspected} previously inspected): <b>${fmtUsd(tn0.mean_usd_per_day)}</b> frozen and <b>${fmtUsd(tn1.mean_usd_per_day)}</b> strict,
      <b>mean day-level uplift summed over ${SCEN}</b>; ${tn0.days_positive}/${tn0.n_days} and ${tn1.days_positive}/${tn1.n_days} days positive.</div>`;
  }

  // ---------------------------------------------------------------- frontier (day scope, 5 walk-forward legs)
  const asinhY = v => Math.asinh(v / 100);
  function drawFront() {
    const cv = CV.front; if (!cv) return; const { ctx, W, H: Hh } = cv;
    ctx.clearRect(0, 0, W, Hh);
    const padL = 54, padR = 10, padT = 12, padB = 30;
    const xmin = Math.log10(0.015), xmax = Math.log10(3000);
    const series = { naive: [], thr: [], lev: [] };
    for (const d of DELTAS) { const g = GD.get(key(S.sim, S.fee, d, MACH_D)); for (const p in series) series[p].push([2 * d + MACH_D / 1000, g[p].usd, d]); }
    const human = S.fee === M.race_fee ? RTS.map(rt => { const g = GD.get(key(S.sim, S.fee, delta(), rt * 1000)); return { l: 2 * delta() + rt, n: g.naive.usd, t: g.thr.usd, tn: g.thr.n }; }) : [];
    const allY = [...series.naive, ...series.thr, ...series.lev].map(p => p[1]).concat(human.flatMap(h => [h.n, h.t]));
    const ymin = asinhY(Math.min(-1000, ...allY)), ymax = asinhY(Math.max(1000, ...allY));
    const X = l => padL + (Math.log10(l) - xmin) / (xmax - xmin) * (W - padL - padR);
    const Y = v => padT + (ymax - asinhY(v)) / (ymax - ymin) * (Hh - padT - padB);
    ctx.font = "11px -apple-system, sans-serif"; ctx.fillStyle = "#5b6886"; ctx.lineWidth = 1;
    for (const v of [-10000, -1000, -100, 0, 100, 1000]) {
      if (asinhY(v) < ymin || asinhY(v) > ymax) continue;
      ctx.beginPath(); ctx.moveTo(padL, Y(v)); ctx.lineTo(W - padR, Y(v)); ctx.strokeStyle = v === 0 ? "#6b7aa0" : "#1c2742"; ctx.stroke();
      ctx.fillText(v === 0 ? "$0" : (v > 0 ? "+" : "−") + "$" + Math.abs(v).toLocaleString(), 4, Y(v) + 4);
    }
    for (const l of [0.01, 0.1, 1, 10, 100, 1000]) { ctx.fillText(fmtMs(l), X(l) - 12, Hh - 14); ctx.beginPath(); ctx.moveTo(X(l), padT); ctx.lineTo(X(l), Hh - padB); ctx.strokeStyle = "#1c2742"; ctx.stroke(); }
    ctx.fillText("end-to-end latency L = feed + decision + order (log)", W / 2 - 120, Hh - 2);
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
    if (human.length) {
      ctx.fillStyle = "rgba(255,210,63,.18)"; ctx.fillRect(X(human[0].l), padT, X(human[human.length - 1].l) - X(human[0].l), Hh - padT - padB);
      for (const h of human) { dot(ctx, X(h.l), Y(h.n), 2.5, "#ff6b6b"); dot(ctx, X(h.l), Y(h.t), 2.5, "#4aa8ff"); }
      ctx.fillStyle = "#ffd23f"; ctx.fillText("human RTs", X(human[0].l) + 3, padT + 10); ctx.fillText(`${RTS[0]} ms–${RTS[RTS.length - 1] / 1000} s`, X(human[0].l) + 3, padT + 23);
    }
    ctx.strokeStyle = "#ffd23f"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(X(machineL()), padT); ctx.lineTo(X(machineL()), Hh - padB); ctx.stroke();
    ctx.fillStyle = "#ffd23f"; ctx.fillText("machine", X(machineL()) + 3, Hh - padB - 4);
    const R = S.race;
    if (R && R.result && R.result.sim === S.sim && R.result.d === delta() && S.fee === RACE.fee) {
      const g = GD.get(key(S.sim, S.fee, delta(), R.result.rtGrid * 1000)), l = 2 * delta() + R.result.rtGrid;
      if (g) { ctx.strokeStyle = "#ffd23f"; ctx.setLineDash([2, 3]); ctx.beginPath(); ctx.moveTo(X(l), padT); ctx.lineTo(X(l), Hh - padB); ctx.stroke(); ctx.setLineDash([]);
        dot(ctx, X(l), Y(g.naive.usd), 6, "#ffd23f"); ctx.fillText("YOU", X(l) - 34, Y(g.naive.usd) + 4); }
    }
    // zero crossing: the bracketing grid points, no interpolation; the leg set is named because the 9-leg baseline differs
    const nv = series.naive; let cross = "";
    for (let i = 1; i < nv.length; i++) if (nv[i - 1][1] > 0 && nv[i][1] <= 0) { cross = `first turns negative between δ = ${fmtMs(nv[i - 1][2])} and ${fmtMs(nv[i][2])} one-way`; break; }
    let note = `Full held-out day, <b>5 walk-forward legs</b>, ${S.fee} bp/leg, ${simName(S.sim)}, one setup per point: naive's day total ${cross || (nv[0][1] <= 0 ? "is negative at every latency on this grid" : "stays positive on this grid")}` +
      (S.fee === 1 && S.sim === "frozen" ? ` (on the 9-leg baseline day it crosses at ${H.be_naive} ms; latency_budget.md)` : "") +
      `; tuned threshold at the machine's L: ${fmtUsd(GD.get(key(S.sim, S.fee, delta(), MACH_D)).thr.usd)}.`;
    if (human.length) {
      const maxN = Math.max(...human.map(h => h.tn)), worst = Math.max(...human.map(h => Math.abs(h.t)));
      note += ` Yellow band = human reaction times at δ = ${fmtMs(delta())} (naive red, re-tuned threshold blue): on the full day the threshold re-tuned at human speeds ` +
        (maxN === 0 ? "selects no trades." : `selects at most ${maxN} trades at any reaction-time point (largest |day surplus| ${fmtUsd(worst, 2).slice(1)}).`);
    }
    $("frontnote").innerHTML = note;
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
  let NR = 46;   // node radius; scaled with the canvas height in drawPent
  const ORDER = ["coinbase:BTC-USD", "binance:BTCUSDT", "binance-futures:BTCUSDT", "okex-swap:BTC-USDT-SWAP", "okex:BTC-USDT"];
  function nodePos(W, Hh) {
    const cx = W * 0.5, cy = Hh * 0.48, r = Math.min(W * 0.34, Hh * 0.33);
    const pos = {}; ORDER.forEach((l, k) => { const a = -Math.PI / 2 + k * 2 * Math.PI / 5; pos[LEGS.indexOf(l)] = [cx + r * Math.cos(a), cy + r * Math.sin(a)]; });
    return pos;
  }
  function drawPent() {
    const cv = CV.pent; if (!cv) return; const { ctx, W, H: Hh } = cv; ctx.clearRect(0, 0, W, Hh);
    NR = Math.max(30, Math.min(46, Hh * 0.115));
    const fs = k => `${Math.round(NR * k)}px -apple-system, sans-serif`;
    const pos = nodePos(W, Hh), candSet = CIDX[S.fee], R = S.race, inRace = racing(), tgt = inRace && R.target;
    for (const i of active) {
      const isT = tgt && tgt.opp === E.opp_id[i] && R.state === "flash";
      if (inRace && R.state === "flash" && !isT) continue;            // during a flash only the target is drawn
      const isC = !inRace && candSet.has(E.opp_id[i]), open = S.t < eE[i];   // during a race nothing else is orange
      const a = pos[E.b[i]], b = pos[E.s[i]], e = E.edge0[i];
      const fade = open ? 1 : Math.max(0, 1 - (S.t - eE[i]) / 150);
      const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, cx = W * 0.5, cy = Hh * 0.48;
      const bend = 0.25, qx = mx + (mx - cx) * bend, qy = my + (my - cy) * bend;
      ctx.globalAlpha = fade * (isT || isC ? 0.95 : 0.35);
      ctx.strokeStyle = isT ? "#ffd23f" : isC ? "#ffb347" : "#5f72a8"; ctx.lineWidth = isT ? 7 : Math.min(1 + e * 0.9, 9);
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.quadraticCurveTo(qx, qy, b[0], b[1]); ctx.stroke();
      arrowHead(ctx, qx, qy, b[0], b[1], ctx.strokeStyle, isT ? 16 : 9);
      if (isC || isT) { ctx.globalAlpha = fade; ctx.fillStyle = isT ? "#ffd23f" : "#ffcf8a"; ctx.font = "bold 12px -apple-system, sans-serif"; ctx.fillText(`+${e.toFixed(1)} bp`, qx - 18, qy - 4); }
      ctx.globalAlpha = 1;
    }
    LEGS.forEach((l, i) => {
      const q = Q[i], j = lastIdx(q, S.t);
      if (j !== q.last) { if (j > q.last && q.last >= 0) q.pulse = 1; q.last = j; }
      const [x, y] = pos[i], perp = l.includes("futures") || l.includes("SWAP");
      if (q.pulse > 0.02) { ctx.beginPath(); ctx.arc(x, y, NR + 2 + 10 * (1 - q.pulse), 0, Math.PI * 2); ctx.strokeStyle = `rgba(62,230,160,${q.pulse})`; ctx.lineWidth = 2; ctx.stroke(); q.pulse *= 0.86; }
      ctx.beginPath(); ctx.arc(x, y, NR, 0, Math.PI * 2); ctx.fillStyle = "#0f1628"; ctx.fill(); ctx.strokeStyle = perp ? "#b58bff" : "#4aa8ff"; ctx.lineWidth = 2; ctx.stroke();
      ctx.fillStyle = "#e8edf7"; ctx.textAlign = "center"; ctx.font = "600 " + fs(0.28); ctx.fillText(NAME[l], x, y - NR * 0.13);
      ctx.font = fs(0.26); ctx.fillStyle = "#93a1bd";
      ctx.fillText(j >= 0 ? ((q.bid[j] + q.ask[j]) / 2).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "—", x, y + NR * 0.22);
      ctx.fillStyle = "#5b6886"; ctx.font = fs(0.24); ctx.fillText(QUOTE_CCY(l), x, y + NR * 0.52);
      ctx.font = "11px -apple-system, sans-serif";
      ctx.fillText(`every ~${cadence(l) >= 10 ? cadence(l).toFixed(0) : cadence(l).toFixed(1)} ms`, x, y + NR + 13);
      ctx.textAlign = "left";
    });
    ctx.fillStyle = "#5b6886"; ctx.font = "11px -apple-system, sans-serif";
    const legend = ["arrow = buy at the tail venue, sell at the head · orange = net edge > 0 after fees · ring = a quote was published · every ~N ms = median publication gap",
      "arrow: buy tail, sell head · orange: beats fees · ring: quote published · every ~N ms: median gap"].find(t => ctx.measureText(t).width < W - 20) || "orange: beats fees · ring: quote published";
    ctx.fillText(inRace ? "race: press SPACE when the yellow flash appears" : legend, 10, Hh - 8);
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
    const nRows = S.view === "stage" ? 4 : 6;
    const rows = [...S.linger.keys()].sort((a, b) => eS[b] - eS[a]).slice(0, nRows);
    const x0 = 250, x1 = W - 165, lmin = Math.log10(0.3), lmax = Math.log10(3000), X = ms => x0 + (Math.log10(Math.max(ms, 0.3)) - lmin) / (lmax - lmin) * (x1 - x0);
    ctx.font = "11px -apple-system, sans-serif"; ctx.fillStyle = "#5b6886";
    for (const ms of [1, 10, 100, 1000]) { ctx.fillText(fmtMs(ms), X(ms) - 10, 12); ctx.fillRect(X(ms), 16, 1, Hh - 20); }
    const L = machineL(), rowH = (Hh - 22) / nRows;
    ctx.fillStyle = "#ffd23f"; ctx.fillText("▼ machine order lands", X(L) - 50, Hh - 2);
    rows.forEach((i, r) => {
      const y = 22 + r * rowH, s = LEGS[E.s[i]], b = LEGS[E.b[i]];
      const unresolved = Math.max(cadence(s) || 0, cadence(b) || 0);
      ctx.fillStyle = "#1a2440"; ctx.fillRect(x0, y + 4, x1 - x0, rowH - 10);
      ctx.fillStyle = "rgba(147,161,189,.18)"; ctx.fillRect(x0, y + 4, X(unresolved) - x0, rowH - 10);
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
    if (racing()) return;
    const r = e.target.getBoundingClientRect(); S.t = (e.clientX - r.left) / r.width * W_MS; rebuildActive(); S.linger.clear();
  });

  // ---------------------------------------------------------------- race the machine
  // Rule (shown before the trials): each trial draws one opportunity uniformly at random from the window's candidates at the
  // race fee (no repeats) BEFORE anything about it is shown; the replay then starts 1.5–4 s before it opens, at 1× wall clock.
  const ELIG = (() => { const c = CAND[RACE.fee], out = []; for (let i = 0; i < c.opp_id.length; i++) if ((c.t_start_us[i] - M.w0_us) / 1000 >= RACE.lead[1]) out.push(i); return out; })();
  let raceSeq = 0;
  function applyRaceSetup() {
    S.sim = RACE.sim; S.fee = RACE.fee; S.di = DELTAS.indexOf(RACE.delta); S.speed = 1; S.preset = null;
    setSeg("sim", S.sim); setSeg("fee", S.fee); setSeg("speed", 1); $("delta").value = S.di;
    changed();
  }
  function startRace() {
    if (racing()) return;
    if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
    const t0 = performance.now();
    S.race = { running: true, trials: [], log: [], state: "idle", target: null, used: new Set(), t0, deadlineAt: t0 + RACE.deadlineS * 1000,
      result: null, stopReason: "", finishedAt: 0 };
    applyRaceSetup();
    $("raceStop").disabled = false; $("raceBtn").disabled = true; for (const b of $("steps").children) b.disabled = true; $("viewToggle").disabled = true;
    if (S.view === "dashboard") document.querySelector(".panel.replay").scrollIntoView({ block: "nearest" });
    renderTrials(); renderTwo(); renderRaceSetup(); renderRaceRule(); armTrial();
  }
  function armTrial() {
    const R = S.race; if (!R || !R.running) return;
    if (R.trials.length >= RACE.n) { finishRace(`${RACE.n} trials completed`); return; }
    const c = CAND[RACE.fee], pool = ELIG.filter(i => !R.used.has(c.opp_id[i]));
    if (!pool.length) { finishRace("no unused opportunities left"); return; }
    const j = pool[Math.floor(Math.random() * pool.length)];
    const lead = RACE.lead[0] + Math.random() * (RACE.lead[1] - RACE.lead[0]);
    R.used.add(c.opp_id[j]);
    R.target = { opp: c.opp_id[j], t: (c.t_start_us[j] - M.w0_us) / 1000, s: LEGS.indexOf(c.sell_venue[j]), b: LEGS.indexOf(c.buy_venue[j]),
      edge: c.edge0_bps[j], dur: c.duration_us[j] / 1000, lead };
    S.t = R.target.t - lead; S.speed = 1; rebuildActive(); S.linger.clear(); S.playing = true; updatePlay();
    R.state = "wait";
    showFlash("wait", `Trial ${R.trials.length + 1} of ${RACE.n} · watch for the yellow flash`);
    renderRaceStatus();
  }
  function showFlash(kind, html) { const f = $("flash"); f.className = "flash" + (kind === "wait" ? " wait" : ""); f.innerHTML = html; }
  function raceTick(now) {
    const R = S.race; if (!R || !R.running) return;
    if (now >= R.deadlineAt) { finishRace(`presenter deadline (${RACE.deadlineS} s) reached`); return; }
    if (R.state === "wait" && S.t >= R.target.t) {
      R.state = "flash"; R.flashAt = now;
      document.querySelector(".panel.replay").classList.add("flashing");
      showFlash("flash", `NOW · buy ${NAME[LEGS[R.target.b]]} / sell ${NAME[LEGS[R.target.s]]} · +${R.target.edge.toFixed(2)} bp`);
    } else if (R.state === "flash" && now - R.flashAt > RACE.timeoutMs) record(RACE.timeoutMs, true);
    const txt = `race clock ${((now - R.t0) / 1000).toFixed(0)} s of ${RACE.deadlineS} s · trial ${Math.min(R.trials.length + 1, RACE.n)}/${RACE.n}`;
    $("raceClock").textContent = txt;
  }
  function press(ts) {
    const R = S.race;
    if (R.state === "wait") {
      R.log.push({ kind: "false", target: R.target }); R.state = "pause";
      showFlash("wait", "False start (pressed before the flash) · logged · re-arming with a new opportunity…"); renderTrials();
      setTimeout(() => { if (S.race === R && R.running) armTrial(); }, 900);
    } else if (R.state === "flash") record(Math.max(1, ts - R.flashAt), false);
  }
  function record(rt, timeout) {
    const R = S.race; R.state = "pause"; document.querySelector(".panel.replay").classList.remove("flashing");
    const tr = { ...R.target, rt, timeout, kind: "trial" }; R.trials.push(tr); R.log.push(tr);
    showFlash("wait", timeout ? `No press within ${RACE.timeoutMs / 1000} s · counted as ${RACE.timeoutMs.toLocaleString()} ms` : `Your reaction time: ${rt.toFixed(0)} ms`);
    renderTrials(); renderRaceStatus();
    setTimeout(() => { if (S.race === R && R.running) armTrial(); }, 1000);
  }
  async function finishRace(reason) {
    const R = S.race; if (!R || !R.running) return;
    if (R.state === "wait" || R.state === "flash") R.log.push({ kind: "abandoned", reason, n: R.trials.length + 1 });
    R.running = false; R.state = "done"; R.stopReason = reason; R.finishedAt = performance.now(); R.wallS = (R.finishedAt - R.t0) / 1000;
    S.playing = false; updatePlay();
    $("flash").className = "flash hidden"; document.querySelector(".panel.replay").classList.remove("flashing");
    $("raceStop").disabled = true; $("raceBtn").disabled = false; $("raceBtn").textContent = "Start a new race (5 trials)";
    for (const b of $("steps").children) b.disabled = false; $("viewToggle").disabled = false;
    $("raceClock").textContent = `finished in ${R.wallS.toFixed(1)} s · ${reason}`;
    renderTrials(); renderRaceSetup(); renderRaceStatus();
    if (R.trials.length) await scoreRace(true);
    else { renderTwo(); $("raceSummary").innerHTML = "No completed trials, so there is nothing to score."; }
  }
  const OCMAP = { none: 0, sell_only: 1, buy_only: 2, both: 3, "not sent": -1 };
  function gridRace(sim, fee, d, rtMed, rtGrid, trials) {
    const gY = GW.get(key(sim, fee, d, rtGrid * 1000)), gM = GW.get(key(sim, fee, d, MACH_D)), idx = CIDX[fee];
    const oc = ch => (ch === "-" ? -1 : +ch);
    return { src: "grid", at: wallClock(), sim, fee, d, rtMed, rtGrid, n: CAND[fee].opp_id.length,
      you: { naive: gY.tot.naive, thr: gY.tot.thr, L: 2 * d + rtGrid, lab: `δ + ${rtGrid} ms + δ (your median ${rtMed.toFixed(0)} ms, snapped to the grid)` },
      mach: { naive: gM.tot.naive, thr: gM.tot.thr, L: 2 * d + MACH_D / 1000, lab: `δ + ${MACH_D} µs + δ (the walk-forward's compute allowance)` },
      ratioBase: P50_COMMITTED_US, ratioLab: `the committed decision-step p50 (${P50_COMMITTED_US.toFixed(2)} µs, decision_timing.json)`,
      trials: trials.map(t => {
        const rg = RTS[nearestIdx(RTS, t.rt)], g = GW.get(key(sim, fee, d, rg * 1000)), i = idx.get(t.opp);
        return { you: { oc: oc(g.oc[i]), pnl: g.pnl_c[i] / 100, note: `RT snapped to ${rg} ms` }, mach: { oc: oc(gM.oc[i]), pnl: gM.pnl_c[i] / 100 } };
      }) };
  }
  async function liveRace(sim, fee, d, rtMed, trials) {
    const all = await api(`/api/race?rt=${rtMed.toFixed(1)}&delta=${d}&sim=${sim}&ids=${trials.map(t => t.opp).join(",")}`, 15000);
    const per = [];
    for (const t of trials) per.push(await api(`/api/race?rt=${t.rt.toFixed(1)}&delta=${d}&sim=${sim}&ids=${t.opp}`, 15000));
    const D = all.machine_D_us;
    return { src: "live", at: wallClock(), sim, fee, d, rtMed, rtGrid: all.rt_threshold_grid_ms, n: CAND[fee].opp_id.length,
      you: { naive: all.you.naive, thr: all.you.thr, L: all.you.L_ms, lab: `δ + ${rtMed.toFixed(0)} ms + δ (your median, exact)` },
      mach: { naive: all.machine.naive, thr: all.machine.thr, L: all.machine.L_ms, lab: `δ + ${D.toFixed(1)} µs + δ (${all.machine_D_source})` },
      ratioBase: D, ratioLab: `the decision-step p50 measured live on this machine (${D.toFixed(2)} µs)`,
      trials: per.map(p => ({ you: { oc: OCMAP[p.you.trials[0].outcome], pnl: p.you.trials[0].pnl_usd, note: "exact RT" },
        mach: { oc: OCMAP[p.machine.trials[0].outcome], pnl: p.machine.trials[0].pnl_usd } })) };
  }
  async function scoreRace(scroll) {
    const R = S.race; if (!R || !R.trials.length) return;
    const seq = ++raceSeq, sim = S.sim, d = delta(), fee = RACE.fee;
    const rtMed = median(R.trials.map(t => t.rt)), rtGrid = RTS[nearestIdx(RTS, rtMed)];
    let res = gridRace(sim, fee, d, rtMed, rtGrid, R.trials);
    if (isLive()) {
      try { const lv = await liveRace(sim, fee, d, rtMed, R.trials); if (seq !== raceSeq) return; if (isLive()) res = lv; }
      catch (e) { if (seq !== raceSeq) return; backendLost(`race recompute failed: ${e.message}`); }
    }
    if (seq !== raceSeq) return;
    R.result = res; renderTrials(); renderTwo(); renderRaceSetup(); renderRaceStatus(); drawFront();
    if (scroll && S.view === "dashboard") $("racePanel").scrollIntoView({ behavior: "smooth", block: "start" });
  }
  function renderRaceRule() {
    const mach = isLive() && S.timing ? `${S.timing.p50_us.toFixed(1)} µs (decision-step p50 measured live on this machine)`
      : `${MACH_D} µs (the walk-forward's compute allowance; committed decision-step p50 ${P50_COMMITTED_US.toFixed(2)} µs)`;
    const full = `<b>Rule, fixed before the trials.</b> Each trial draws one opportunity <b>uniformly at random</b> from this window's ${ELIG.length} with net edge &gt; 0 at ${RACE.fee} bp/leg (no repeats), before anything about it is shown.
      The replay jumps to a random point 1.5–4 s before it opens and plays at <b>1× wall clock</b>; it flashes yellow when it opens. Press <b>SPACE</b> (or click the replay).
      Your reaction time includes this screen's display lag and your keyboard's input lag, as a feed handler's latency includes its own.
      Every trial is reported: false starts are listed and re-armed; no press within ${RACE.timeoutMs / 1000} s counts as ${RACE.timeoutMs.toLocaleString()} ms.
      ${RACE.n} trials or ${RACE.deadlineS} s, whichever comes first; Stop scores the completed trials. Your order lands at δ + RT + δ; the machine's at δ + ${mach} + δ.`;
    const open = $("raceRule").querySelector("details") && $("raceRule").querySelector("details").open;
    $("raceRule").innerHTML = !S.race ? full : `<details${open ? " open" : ""}><summary><b>Rule (fixed before the trials):</b> one of ${ELIG.length} opportunities drawn uniformly at random, no repeats · 1.5–4 s lead-in at 1× · SPACE · false starts re-armed · ${RACE.timeoutMs / 1000} s timeout · ${RACE.n} trials or ${RACE.deadlineS} s · full rule ▸</summary>${full}</details>`;
  }
  function renderRaceSetup() {
    const R = S.race, named = `${simName(RACE.sim)} · ${RACE.fee} bp/leg · δ ${fmtMs(RACE.delta)} one-way`;
    let h = `<b>Race setup</b> (applied on Start): ${named} · 1× wall clock`;
    if (racing()) h = `<b>Racing at the race setup:</b> ${named} · 1× wall clock · controls locked`;
    else if (R && R.result) {
      const r = R.result;
      h = r.sim === RACE.sim && r.d === RACE.delta ? `<b>Scored at the race setup:</b> ${named}`
        : `<b>Rescored at the current setup:</b> ${simName(r.sim)} · ${r.fee} bp/leg · δ ${fmtMs(r.d)} one-way <span class="warn">(race setup: ${named})</span> <button id="raceRestore" class="chip">↺ back to the race setup</button>`;
    }
    if (S.fee !== RACE.fee) h += ` <span class="warn">· the race fee is fixed at ${RACE.fee} bp/leg; other panels now show ${S.fee} bp/leg</span>`;
    $("raceSetup").innerHTML = h;
    const rb = $("raceRestore"); if (rb) rb.onclick = () => applyRaceSetup();
  }
  function renderRaceStatus() {
    const R = S.race; let t = "";
    if (racing()) t = `trial ${Math.min(R.trials.length + 1, RACE.n)} of ${RACE.n}`;
    else if (R && R.result) t = R.result.src === "live" ? `live · ${R.result.at}` : `offline grid · ${R.result.at}`;
    $("raceStatus").textContent = t;
  }
  function renderTrials() {
    const R = S.race, tb = $("trials").querySelector("tbody"); tb.innerHTML = ""; if (!R) return;
    const SHORT = { "-1": "not sent", 0: "✗ missed", 1: "½ sell leg only", 2: "½ buy leg only", 3: "✓ both filled" };
    const cell = o => `<span style="color:${OCG[o.oc][1]}">${SHORT[o.oc]}</span> <b class="${o.pnl >= 0 ? "pos" : "neg"}">${fmtUsd(o.pnl, 2)}</b>`;
    let k = 0;
    for (const t of R.log) {
      const tr = document.createElement("tr");
      if (t.kind === "false") tr.innerHTML = `<td>—</td><td colspan="4" class="warn">false start (pressed before the flash): logged, re-armed with a new opportunity</td>`;
      else if (t.kind === "abandoned") tr.innerHTML = `<td>${t.n}</td><td colspan="4" class="warn">trial not completed: ${t.reason}</td>`;
      else {
        const i = k++, res = R.result && R.result.trials[i], d = R.result ? R.result.d : delta(), gone = t.dur < 2 * d + t.rt;
        tr.innerHTML = `<td>${i + 1}</td><td>${NAME[LEGS[t.b]]} → ${NAME[LEGS[t.s]]} · +${t.edge.toFixed(2)} bp<br><small>${t.dur === 0 ? "closed within one exchange timestamp" : "lived " + fmtMs(t.dur)}${gone ? " · gone before yours landed" : ""}</small></td>
          <td><b>${t.timeout ? "≥ 2,000" : t.rt.toFixed(0)} ms</b>${t.timeout ? "<br><small>timeout</small>" : ""}</td><td>${res ? cell(res.you) : "…"}</td><td>${res ? cell(res.mach) : "…"}</td>`;
      }
      tb.appendChild(tr);
    }
  }
  function renderTwo() {
    const R = S.race, tb = $("two").querySelector("tbody");
    if (!R || !R.result) { tb.innerHTML = ""; $("raceSummary").innerHTML = R && R.running ? "Racing… the 2×2 appears when the trials are scored." : "Run a race: the 2×2 appears here."; return; }
    const r = R.result;
    const cell = a => `<td class="${cls(a.usd)}">${fmtUsd(a.usd, 2)}<small>${a.n} trades · ${a.n_both} both legs</small></td>`;
    tb.innerHTML = `<tr><td style="color:var(--you)"><b>you</b><small>${r.you.lab}</small></td>${cell(r.you.naive)}${cell(r.you.thr)}</tr>
      <tr><td style="color:var(--mach)"><b>machine</b><small>${r.mach.lab}</small></td>${cell(r.mach.naive)}${cell(r.mach.thr)}</tr>`;
    const km = P.km.cands_f1, goneY = 1 - kmS(km, r.you.L), goneM = 1 - kmS(km, r.mach.L), k = R.trials.length;
    $("raceSummary").innerHTML = `All ${r.n} opportunities with net edge &gt; 0 at ${r.fee} bp/leg in this window, ${simName(r.sim)}, δ = ${fmtMs(r.d)}, simulated at your median RT of <b>${r.rtMed.toFixed(0)} ms</b> (${k} completed trial${k === 1 ? "" : "s"}); trial fates are in the table.
      Your median RT is <b>${Math.round(r.rtMed * 1000 / r.ratioBase).toLocaleString()}×</b> ${r.ratioLab}.
      By the time your order landed (L ≈ ${fmtMs(r.you.L)}), <b>${(100 * goneY).toFixed(0)}%</b> of them had closed; at the machine's L (${fmtMs(r.mach.L)}): <b>${(100 * goneM).toFixed(0)}%</b> (Kaplan–Meier, window episodes; closed = edge back within 1 bp of the fair basis).
      The threshold re-tuned on ${M.train_day} at your speed (${r.rtGrid} ms grid point) ${r.you.thr.n ? `selects ${r.you.thr.n} trades` : "selects no trades"}.
      ${r.src === "live" ? "Live: committed simulator at your exact RT." : `Offline: exported grid, your RT snapped to ${r.rtGrid} ms, machine at the ${MACH_D} µs allowance.`} Changing δ or the simulator rescores the same RTs.`;
  }
  $("raceBtn").addEventListener("click", startRace);
  $("raceStop").addEventListener("click", () => finishRace("stopped by the presenter"));
  const justFinished = () => S.race && S.race.finishedAt && performance.now() - S.race.finishedAt < 1500;
  document.addEventListener("keydown", ev => {
    const isPress = ev.code === "Space" || ev.code === "Enter";
    if (racing() && isPress) { ev.preventDefault(); if (!ev.repeat) press(ev.timeStamp); return; }
    if (isPress && justFinished()) { ev.preventDefault(); return; }      // a late press must not restart the race
    if (S.view === "stage" && !racing() && !(ev.target && ev.target.tagName === "INPUT")) {
      if (ev.code === "ArrowRight" || ev.code === "PageDown") { ev.preventDefault(); setView("stage", Math.min(3, S.step + 1)); }
      else if (ev.code === "ArrowLeft" || ev.code === "PageUp") { ev.preventDefault(); setView("stage", Math.max(1, S.step - 1)); }
    }
  });
  document.addEventListener("keyup", ev => { if ((ev.code === "Space" || ev.code === "Enter") && (racing() || justFinished())) ev.preventDefault(); });
  $("pent").addEventListener("pointerdown", ev => { if (racing()) { ev.preventDefault(); press(ev.timeStamp); } });

  // ---------------------------------------------------------------- committed evidence
  function renderEvidence() {
    const f1 = x => fmtUsd(x, Math.abs(x) < 10 ? 1 : 0);
    const wf = C.walkforward_v0, v1 = C.v1, v2 = C.v2, ci = c => `[${f1(c[0])}, ${f1(c[1])}]`;
    const tn0 = wf["threshold_pair - naive"], tn1 = v1["threshold_pair - naive"], lt0 = wf["lev - threshold_pair"], lt1 = v1["lev - threshold_pair"], lt2 = v2["lev - threshold_pair"], s3 = C.s3_v2;
    const dt = C.decision_timing.in_kernel_ns, live = isLive() && S.timing;
    const cadMs = l => Math.round(C.cadence[l].median_gap_ms);
    const cards = [
      ["Robust: latency-aware selection beats naive",
        `Walk-forward on <b>${H.wf_n} sampled first-of-month test days, ${H.wf_inspected} previously inspected</b> (this comparison is a pre-registered secondary analysis). Tuned threshold − naive: <b>${fmtUsd(tn0.mean_usd_per_day)}</b> mean day-level uplift, <b>summed over ${SCEN}</b>, t-CI ${ci(tn0.t_ci95)}, ${tn0.days_positive}/${tn0.n_days} days (frozen fills); with strict next-quote fills <b>${fmtUsd(tn1.mean_usd_per_day)}</b>, ${tn1.days_positive}/${tn1.n_days}. One setup (1 bp/leg) on the <b>9-leg</b> baseline day: naive's surplus turns negative at <b>${H.be_naive} ms</b> one-way.`,
        "falsification_walkforward_12d_prereg.json · sensitivity_amendment1.json · latency_budget.json"],
      ["LEV vs threshold: a benchmark, not a validated edge",
        `Pre-registered primary on the same ${H.wf_n} days, same day score (summed over ${SCEN_N}): <b>${fmtUsd(lt0.mean_usd_per_day)}</b> mean day-level uplift, t-CI ${ci(lt0.t_ci95)}, ${lt0.days_positive}/${lt0.n_days}; on the <b>${H.unseen_n} never-inspected days</b>: <b>${H.unseen_mean}</b> ${H.unseen_tci}, ${H.unseen_pos}/${H.unseen_n}. Strict next-quote fills: <b>${fmtUsd(lt1.mean_usd_per_day)}</b> ${ci(lt1.t_ci95)} (${H.v1_share} of the frozen gain); + 1 s markout: ${fmtUsd(lt2.mean_usd_per_day)} ${ci(lt2.t_ci95)}; shared-liquidity collisions dropped: <b>${fmtUsd(s3.mean_usd_per_day)}</b> ${ci(s3.t_ci95)}, within noise.`,
        "falsification_walkforward_12d_prereg.json · sensitivity_amendment1.json · headline.json"],
      ["How fast mispricings decay, and what quotes cannot resolve",
        `Median observed lifetime <b>${H.median_life_ms} ms</b> (9 legs, Kaplan–Meier, hour-block CI ${H.median_ci_lo}–${H.median_ci_hi}); this window (5 legs): ${P.km.episodes.median_ms.toFixed(1)} ms. Shifting episode endpoints within publication intervals gives an <b>illustrative ${H.med_lo}–${H.med_hi} ms sensitivity range, not a bound on executable lifetime</b>. In these samples the median publication gap is ${cadMs("binance_BTCUSDT")} ms for Binance spot, ${cadMs("okex_BTC-USDT")} ms for OKX spot, ${cadMs("okex-swap_BTC-USDT-SWAP")} ms for OKX perp and ${cadMs("binance-futures_BTCUSDT")} ms for Binance perp, so faster closes are not resolvable (shaded on the clocks). Our own recorder sees Binance perp every ${H.live_bnf_ms} ms.`,
        "decay_report.md · update_cadence.json · live_cadence.json"],
      ["The budget is distance, not compute",
        `Compiled decision step (features + LEV + act): <b>${(dt.p50 / 1e3).toFixed(1)} µs p50 / ${(dt.p99 / 1e3).toFixed(1)} µs p99</b> committed${live ? `; <b>${S.timing.p50_us.toFixed(1)} / ${S.timing.p99_us.toFixed(1)} µs measured live on this machine at ${S.timing.measured_at}</b> (${S.timing.n_calls.toLocaleString()} calls, exact vs sklearn)` : ""}. Detector ${H.det_ns_event} ns/event. Feed p50, venue → Tardis collector: ${H.feed_fast_ms}–${H.feed_slow_ms} ms. This Mac (India), receive − venue timestamp p05: ${Math.round(mac["okex-swap:BTC-USDT-SWAP"])}–${Math.round(mac["coinbase:BTC-USD"])} ms with the <b>clock offset unresolved</b>, so not a latency bound. Order latency is not measured: the simulator assumes order = feed = δ.`,
        "decision_timing.json · latency_budget.json · live_latency.md"],
    ];
    $("cards").innerHTML = cards.map(([h, b, s]) => `<div class="card"><h3>${h}</h3>${b}<div class="src">eval/results/${s.split(" · ").join(" · eval/results/")}</div></div>`).join("");
    const ok = P.checks.filter(c => c.ok === true).length;
    $("foot").innerHTML = `Assets built by demo/build_assets.py from raw Tardis quotes (${M.train_day} train, ${M.test_day} test): ${ok}/${P.checks.length} reproduction checks passed. At δ = ${M.reg_deltas_ms.join("/")} ms the day grid reproduces the committed ${M.test_day} totals for V0 (walk-forward) and V1 (strict). ` +
      `Strict V1 fills are a stress scenario; neither simulator is a fill model calibrated on our own orders. Paper trading is a stretch goal. Exact provenance: demo/assets/provenance.json.`;
  }

  // ---------------------------------------------------------------- views: 3-step stage view and the Q&A dashboard
  const PANEL = { replay: document.querySelector(".panel.replay"), clocks: document.querySelector(".panel.clocks"), knob: document.querySelector(".panel.knob"),
    bigcmp: $("bigcmp"), counters: document.querySelector(".panel.counters"), frontier: document.querySelector(".panel.frontier"),
    race: $("racePanel"), raceres: $("raceResPanel"), evidence: $("evidencePanel"), foot: $("foot") };
  const HOMES = [document.querySelector("section.left"), document.querySelector("section.right"), $("raceWrap"), $("dash")].map(p => [p, Array.from(p.children)]);
  const STEPS = { 1: [["replay", "clocks"], ["knob", "bigcmp", "counters"]], 2: [["replay", "raceres"], ["race"]], 3: [["frontier"], ["evidence", "foot"]] };
  function setView(view, step) {
    if (racing()) return;
    S.view = view; if (step) S.step = step;
    for (const [p, kids] of HOMES) for (const el of kids) p.appendChild(el);
    document.body.classList.toggle("stage", view === "stage");
    const st = $("stage"); st.className = "stage-grid s" + S.step;
    if (view === "stage") STEPS[S.step].forEach((col, c) => { for (const k of col) st.children[c].appendChild(PANEL[k]); });
    for (const b of $("steps").children) b.classList.toggle("on", +b.dataset.step === S.step);
    $("viewToggle").textContent = view === "stage" ? "Dashboard (Q&A)" : "Stage view (talk)";
    try { history.replaceState(null, "", view === "stage" ? `#stage-${S.step}` : "#dashboard"); } catch (e) { /* file:// may refuse */ }
    layout(); rebuildActive(); renderAll();
  }
  $("steps").addEventListener("click", e => { const b = e.target.closest("button"); if (b) setView("stage", +b.dataset.step); });
  $("viewToggle").addEventListener("click", () => setView(S.view === "stage" ? "dashboard" : "stage"));

  // ---------------------------------------------------------------- main loop
  let lastNow = performance.now(), scrubTick = 0;
  function frame(now) {
    const dt = Math.min(now - lastNow, 250); lastNow = now;
    if (S.playing) { S.t += dt * S.speed; if (S.t >= W_MS) { S.t = W_MS; S.playing = false; updatePlay(); } }
    advanceActive(); drawPent(); drawClocks(now); raceTick(now);
    $("clock").textContent = utc(M.w0_us + S.t * 1000) + " UTC";
    if (++scrubTick % 6 === 0) drawScrub();
    requestAnimationFrame(frame);
  }
  window.addEventListener("resize", layout);
  {   // open just before the busiest 30 s of candidates at the race fee
    const ts = CAND[RACE.fee].t_start_us.map(t => (t - M.w0_us) / 1000); let best = 0, bi = 0, j = 0;
    for (let i = 0; i < ts.length; i++) { while (ts[j] < ts[i] - 30000) j++; if (i - j + 1 > best) { best = i - j + 1; bi = j; } }
    S.t = Math.max(0, ts[bi] - 300);
  }
  const h = location.hash.match(/^#(stage)-?([123])?$|^#(dashboard)$/);
  setView(h && h[3] ? "dashboard" : "stage", h && h[2] ? +h[2] : 1);
  changed();
  requestAnimationFrame(frame);
  pollStatus();
  window.P6_STATE = S;   // for the headless smoke test and screenshots
})();
