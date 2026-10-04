/* Screens 1-2 (REAL data): India state by state, then district by district. */
(function () {
  "use strict";
  var PS = window.PS, D = PS.D, S = PS.S, esc = PS.esc;

  var TILES = {
    JK: [2, 0], LA: [3, 0], PB: [2, 1], HP: [3, 1], UK: [4, 1], AR: [9, 1],
    CH: [1, 2], HR: [2, 2], DL: [3, 2], UP: [4, 2], BR: [5, 2], SK: [7, 2], AS: [8, 2], NL: [9, 2],
    RJ: [2, 3], MP: [3, 3], CG: [4, 3], JH: [5, 3], WB: [6, 3], ML: [8, 3], MN: [9, 3],
    GJ: [1, 4], DH: [2, 4], MH: [3, 4], TG: [4, 4], OD: [5, 4], TR: [8, 4], MZ: [9, 4],
    GA: [2, 5], KA: [3, 5], AP: [4, 5], LD: [1, 6], KL: [3, 6], TN: [4, 6], PY: [5, 6], AN: [8, 6]
  };
  var IND = { wasted: "Wasted", stunted: "Stunted", underweight: "Underweight" };

  function rows() { return (D.gap && D.gap.rows) || []; }
  function byCode(code) { return rows().filter(function (r) { return r.code === code; })[0]; }
  PS.tileValues = function () {  /* used by the smoke test's contrast check */
    var out = [];
    rows().forEach(function (r) { out.push(r.nfhs5.wasted, r.pt.wasted); });
    return out;
  };

  function tileSvg() {
    var T = 52, G = 5, W = 10 * (T + G), H = 7 * (T + G);
    var o = ['<svg viewBox="-4 -4 ' + (W + 8) + " " + (H + 52) + '" role="img" aria-label="Tile grid of States and UTs coloured by wasting">'];
    rows().forEach(function (r) {
      var p = TILES[r.code];
      if (!p) return;
      var v = S.tileMode === "pt" ? r.pt.wasted : r.nfhs5.wasted;
      var x = p[0] * (T + G), y = p[1] * (T + G), sel = r.code === S.state, ink = PS.ink(v);
      o.push('<g class="tile" data-code="' + r.code + '" data-v="' + v + '" style="cursor:pointer" tabindex="0" role="button" aria-label="' + esc(r.state) + " " + v + '%">' +
        '<rect x="' + x + '" y="' + y + '" width="' + T + '" height="' + T + '" rx="5" fill="' + PS.heat(v) + '"' +
        (sel ? ' stroke="#13213c" stroke-width="3.5"' : ' stroke="#ffffff" stroke-width="1"') + "></rect>" +
        '<text x="' + (x + T / 2) + '" y="' + (y + 23) + '" text-anchor="middle" font-size="17" font-weight="800" fill="' + ink + '">' + r.code + "</text>" +
        '<text x="' + (x + T / 2) + '" y="' + (y + 42) + '" text-anchor="middle" font-size="14" font-weight="600" fill="' + ink + '">' + PS.fmt(v, 1) + "</text></g>");
    });
    var lx = 18, ly = H + 12, lw = 300;
    for (var i = 0; i < 64; i++) o.push('<rect x="' + (lx + (i * lw) / 64) + '" y="' + ly + '" width="' + (lw / 64 + 0.6) + '" height="11" fill="' + PS.heat((i / 63) * 32) + '"></rect>');
    [0, 8, 16, 24, 32].forEach(function (t) {
      o.push('<text x="' + (lx + (t / 32) * lw) + '" y="' + (ly + 28) + '" font-size="14" text-anchor="middle" fill="#4a566b">' + t + "%</text>");
    });
    o.push('<text x="' + (lx + lw + 14) + '" y="' + (ly + 11) + '" font-size="15" fill="#33415c">% of children under five wasted</text>');
    o.push("</svg>");
    return o.join("");
  }

  /* place a label next to a marker: first candidate inside the plot that avoids every box in `avoid` */
  function place(x, y, text, size, avoid, bounds) {
    var cands = [[-12, -12, "end"], [12, -12, "start"], [-12, 22, "end"], [12, 22, "start"], [0, -16, "middle"], [0, 28, "middle"]];
    for (var i = 0; i < cands.length; i++) {
      var c = cands[i], bx = PS.textBox(x + c[0], y + c[1], text, size, c[2]);
      if (bx.x0 < bounds.x0 || bx.x1 > bounds.x1 || bx.y0 < bounds.y0 || bx.y1 > bounds.y1) continue;
      if (avoid.some(function (a) { return PS.overlaps(a, bx); })) continue;
      return { x: x + c[0], y: y + c[1], anchor: c[2], box: bx };
    }
    var f = cands[0];
    return { x: x + f[0], y: y + f[1], anchor: f[2], box: PS.textBox(x + f[0], y + f[1], text, size, f[2]) };
  }

  function scatterSvg() {
    var ind = S.ind, W = 620, H = 430, m = { l: 58, r: 16, t: 12, b: 50 };
    var max = 0;
    rows().forEach(function (r) { max = Math.max(max, r.nfhs5[ind], r.pt[ind]); });
    max = Math.ceil(max / 5) * 5;
    var X = PS.scale(0, max, m.l, W - m.r), Y = PS.scale(0, max, H - m.b, m.t);
    var o = ['<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Poshan Tracker vs NFHS-5 by State/UT">'];
    o.push('<polygon points="' + X(0) + "," + Y(0) + " " + X(max) + "," + Y(0) + " " + X(max) + "," + Y(max) + '" fill="#fbeec8" opacity=".55"></polygon>');
    PS.ticks(0, max, max > 30 ? 10 : 5).forEach(function (t) {
      o.push('<line x1="' + X(t) + '" x2="' + X(t) + '" y1="' + Y(0) + '" y2="' + Y(max) + '" stroke="#e3e7ee"></line>');
      o.push('<line x1="' + X(0) + '" x2="' + X(max) + '" y1="' + Y(t) + '" y2="' + Y(t) + '" stroke="#e3e7ee"></line>');
      o.push('<text x="' + X(t) + '" y="' + (H - m.b + 18) + '" font-size="14" text-anchor="middle" fill="#4a566b">' + t + "</text>");
      o.push('<text x="' + (m.l - 8) + '" y="' + (Y(t) + 5) + '" font-size="14" text-anchor="end" fill="#4a566b">' + t + "</text>");
    });
    o.push('<line x1="' + X(0) + '" y1="' + Y(0) + '" x2="' + X(max) + '" y2="' + Y(max) + '" stroke="#13213c" stroke-width="1.5" stroke-dasharray="6 5"></line>');
    o.push('<text class="halo" x="' + (X(max * 0.62) - 8) + '" y="' + (Y(max * 0.62) - 8) + '" font-size="14" text-anchor="end" fill="#13213c">reported = surveyed</text>');
    o.push('<text class="halo" x="' + (X(max) - 8) + '" y="' + Y(max * 0.47) + '" font-size="15" font-weight="700" text-anchor="end" fill="#7a4f00">reported lower than surveyed</text>');
    o.push('<text x="' + ((m.l + W - m.r) / 2) + '" y="' + (H - 8) + '" font-size="15" text-anchor="middle" fill="#13213c">NFHS-5 survey, 2019–21 (% of children under five)</text>');
    var cy = (m.t + H - m.b) / 2;
    o.push('<text x="16" y="' + cy + '" font-size="15" text-anchor="middle" fill="#13213c" transform="rotate(-90 16 ' + cy + ')">Poshan Tracker, June 2025 (%)</text>');
    var sel = null;
    rows().forEach(function (r) {
      var s = r.code === S.state;
      if (s) sel = r;
      o.push('<circle class="pt" data-code="' + r.code + '" cx="' + X(r.nfhs5[ind]) + '" cy="' + Y(r.pt[ind]) + '" r="' + (s ? 8 : 6) + '" fill="' +
        (s ? "#e3a008" : "#0a6c8f") + '" stroke="' + (s ? "#13213c" : "#ffffff") + '" stroke-width="' + (s ? 2.5 : 1.2) + '" style="cursor:pointer"></circle>');
    });
    var g = D.gap.india, ix = X(g.nfhs5[ind]), iy = Y(g.pt[ind]);
    o.push('<rect x="' + (ix - 7) + '" y="' + (iy - 7) + '" width="14" height="14" fill="#13213c" transform="rotate(45 ' + ix + " " + iy + ')"></rect>');
    var bounds = { x0: m.l + 2, x1: W - m.r, y0: m.t, y1: H - m.b - 2 };
    var iText = "India " + g.nfhs5[ind] + "% → " + g.pt[ind] + "%";
    var markerBox = function (x, y, pad) { pad = pad || 0; return { x0: x - 9 - pad, x1: x + 9 + pad, y0: y - 9, y1: y + 9 }; };
    var avoid = sel ? [markerBox(X(sel.nfhs5[ind]), Y(sel.pt[ind]))] : [];
    var il = place(ix, iy, iText, 15, avoid, bounds);
    o.push('<text class="halo" id="lbl-india" x="' + il.x + '" y="' + il.y + '" text-anchor="' + il.anchor + '" font-size="15" font-weight="800" fill="#13213c">' + esc(iText) + "</text>");
    if (sel) {
      var sx = X(sel.nfhs5[ind]), sy = Y(sel.pt[ind]);
      var sl = place(sx, sy, sel.state, 15, [il.box, markerBox(ix, iy, 34)], bounds);
      o.push('<text class="halo" id="lbl-state" x="' + sl.x + '" y="' + sl.y + '" text-anchor="' + sl.anchor + '" font-size="15" font-weight="700" fill="#13213c">' + esc(sel.state) + "</text>");
    }
    o.push("</svg>");
    return o.join("");
  }

  function gapDetails(g) {
    var disp = g.dispersion, cnt = g.counts;
    var line = function (k) {
      return "<li><b>" + IND[k] + ":</b> Poshan Tracker lower in " + cnt[k].pt_lower + " of " + cnt[k].n + "; median state-level difference " +
        disp[k].median_abs_diff_pp + " points; within 5 points in " + disp[k].within_5pp + " of " + disp[k].n + ".</li>";
    };
    var tbl = rows().slice().sort(function (a, b) { return b.nfhs5[S.ind] - a.nfhs5[S.ind]; }).map(function (r) {
      return "<tr><td>" + esc(r.state) + '</td><td class="num">' + r.nfhs5[S.ind] + '</td><td class="num">' + r.pt[S.ind] + "</td></tr>";
    }).join("");
    return "<h3>Sources (REAL)</h3><ul><li>NFHS-5 2019–21, children under 5, by State/UT: " + esc(g.nfhs5_source) + ".</li>" +
      "<li>Poshan Tracker June 2025, 0–5 years: " + esc(g.pt_source) + ".</li><li>Parsed into <code>" + esc(g.source_file) + "</code>; verification notes in V4.</li></ul>" +
      "<h3>How far apart, state by state</h3><ul>" + line("wasted") + line("underweight") + line("stunted") + "</ul>" +
      "<p>National stunting is close (" + g.india.nfhs5.stunted + "% vs " + g.india.pt.stunted + "%); state-level stunting is not.</p>" +
      "<h3>What the gap is not</h3><p>" + esc(g.caveat) + " The Ministry has said administrative data \u201csuffer from data gaps due to coverage, measurement, training etc.\u201d (Rajya Sabha reply, as reported by News18, 5 Dec 2025: a secondary source).</p>" +
      "<p>The tile grid is not a map: positions are approximate and no boundaries are drawn.</p>" +
      "<h3>" + IND[S.ind] + " by State/UT (%)</h3><table><thead><tr><th>State/UT</th><th>NFHS-5</th><th>Poshan Tracker</th></tr></thead><tbody>" + tbl + "</tbody></table>";
  }

  PS.register("india", function () {
    var g = D.gap;
    if (!g) return '<div class="panel"><h2>Missing data</h2></div>';
    var c = g.counts[S.ind], st = byCode(S.state);
    var seg = function (key, val, label) {
      return '<button data-' + key + '="' + val + '" aria-pressed="' + (S[key === "tile" ? "tileMode" : "ind"] === val) + '">' + label + "</button>";
    };
    var body = '<div class="panel"><div class="prow"><h2>Wasting by State/UT</h2><span class="seg" role="group" aria-label="Source">' +
      seg("tile", "nfhs5", "Surveyed: NFHS-5") + seg("tile", "pt", "Reported: Poshan Tracker") + "</span></div>" +
      '<div class="fill">' + tileSvg() + "</div></div>" +
      '<div class="panel"><div class="prow"><h2>Reported vs surveyed, each State/UT</h2><span class="seg" role="group" aria-label="Indicator">' +
      seg("ind", "wasted", "Wasted") + seg("ind", "stunted", "Stunted") + seg("ind", "underweight", "Underweight") + "</span></div>" +
      '<div class="fill">' + scatterSvg() + "</div>" +
      '<p class="verdict num"><b>' + IND[S.ind] + ":</b> Poshan Tracker lower than NFHS-5 in <b>" + c.pt_lower + " of " + c.n + "</b> States/UTs" +
      (st ? "; " + esc(st.state) + " " + st.nfhs5[S.ind] + "% → " + st.pt[S.ind] + "%." : ".") + "</p></div>";
    return PS.slide({
      kind: "real", bodyClass: "g-india",
      h1: "Reported wasting is below the national survey in all " + g.counts.wasted.n + " States and UTs",
      lede: "India: <b>" + g.india.nfhs5.wasted + "%</b> of children under five wasted in NFHS-5 (2019–21), <b>" + g.india.pt.wasted +
        "%</b> in Poshan Tracker (June 2025). Nationally, stunting is close (" + g.india.nfhs5.stunted + "% vs " + g.india.pt.stunted + "%).",
      body: body,
      caveat: "<b>Not like-for-like:</b> different years, ages and denominators. An unexplained discrepancy, not a measured under-detection rate and not evidence about any worker.",
      src: "REAL. NFHS-5: Lok Sabha USQ 2668 annexure (4 Aug 2023). Poshan Tracker: Rajya Sabha USQ 477 annexure I (23 Jul 2025). <code>research/sources/state_gap_verified.csv</code> (V4).",
      detailsTitle: "India: sources and spread", details: gapDetails(g)
    });
  });
  PS.renderers.india.after = function (el) {
    el.querySelectorAll("[data-tile]").forEach(function (b) { b.onclick = function () { S.tileMode = b.dataset.tile; PS.render(); }; });
    el.querySelectorAll("[data-ind]").forEach(function (b) { b.onclick = function () { S.ind = b.dataset.ind; PS.render(); }; });
    el.querySelectorAll("[data-code]").forEach(function (n) {
      var r = byCode(n.dataset.code);
      n.onmousemove = function (ev) {
        PS.showTip(ev, "<b>" + esc(r.state) + "</b><br>Wasted: NFHS-5 " + r.nfhs5.wasted + "% · Poshan Tracker " + r.pt.wasted +
          "%<br>Stunted: " + r.nfhs5.stunted + "% · " + r.pt.stunted + "%");
      };
      n.onmouseleave = PS.hideTip;
      var pick = function () { S.state = r.code; PS.pickDefaultDistrict(); PS.go(1); };
      n.onclick = pick;
      n.onkeydown = function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); pick(); } };
    });
  };

  /* ---------------------------------------------------------------- districts */
  function drows() { return (D.districts && D.districts.rows) || []; }
  PS.pickDefaultDistrict = function () {
    var inState = drows().filter(function (r) { return r.state_code === S.state; });
    if (!inState.some(function (r) { return r.district === S.district; })) {
      var presets = D.districts.presets, pick = null;
      Object.keys(presets).forEach(function (k) { if (!pick && presets[k].state_code === S.state) pick = presets[k].district; });
      if (!pick && inState.length) pick = inState.slice().sort(function (a, b) { return b.wasted - a.wasted; })[0].district;
      S.district = pick;
    }
  };

  var swarmCache = {};
  function swarm(ind, X, r) {
    var key = ind + "|" + r;
    if (swarmCache[key]) return swarmCache[key];
    var pts = drows().map(function (d, i) { return { i: i, x: X(d[ind]), y: 0 }; }).sort(function (a, b) { return a.x - b.x; });
    var placed = [], step = 2 * r + 0.6;
    pts.forEach(function (p) {
      var near = placed.filter(function (q) { return Math.abs(q.x - p.x) < step; });
      for (var k = 0; k < 80; k++) {
        var y = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * step * 0.5;
        if (near.every(function (q) { var dx = q.x - p.x, dy = q.y - y; return dx * dx + dy * dy >= step * step; })) { p.y = y; break; }
      }
      placed.push(p);
    });
    var out = {};
    pts.forEach(function (p) { out[p.i] = p; });
    return (swarmCache[key] = out);
  }

  function swarmSvg() {
    var W = 940, m = { l: 92, r: 18 }, r = 2.9, top = 0;
    drows().forEach(function (d) { top = Math.max(top, d.wasted, d.stunted); });
    top = Math.ceil(top / 5) * 5;
    var X = PS.scale(0, top, m.l, W - m.r), half = 0;
    ["wasted", "stunted"].forEach(function (ind) { var pos = swarm(ind, X, r); Object.keys(pos).forEach(function (k) { half = Math.max(half, Math.abs(pos[k].y)); }); });
    half += r + 4;
    var strip = 2 * half + 34;
    var o = ['<svg viewBox="0 0 ' + W + " " + (2 * strip + 8) + '" role="img" aria-label="NFHS-5 districts: wasting and stunting">'];
    [["wasted", "Wasted"], ["stunted", "Stunted"]].forEach(function (pair, si) {
      var ind = pair[0], cy = 4 + si * strip + half, pos = swarm(ind, X, r);
      o.push('<text x="0" y="' + (cy + 5) + '" font-size="16" font-weight="700" fill="#13213c">' + pair[1] + "</text>");
      o.push('<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + (cy + half + 2) + '" y2="' + (cy + half + 2) + '" stroke="#d5dbe4"></line>');
      PS.ticks(0, top, 10).forEach(function (t) {
        o.push('<text x="' + X(t) + '" y="' + (cy + half + 19) + '" font-size="14" text-anchor="middle" fill="#4a566b">' + t + "%</text>");
      });
      var later = [];
      drows().forEach(function (d, i) {
        var p = pos[i], inState = d.state_code === S.state, sel = inState && d.district === S.district;
        var c = '<circle class="dd" data-i="' + i + '" cx="' + p.x.toFixed(1) + '" cy="' + (cy + p.y).toFixed(1) + '" r="' + (sel ? 6.5 : inState ? r + 0.6 : r) + '" fill="' +
          (sel ? "#e3a008" : inState ? "#0a6c8f" : "#c3cad5") + '"' + (sel ? ' stroke="#13213c" stroke-width="2.2"' : "") + ' style="cursor:pointer"></circle>';
        if (inState) later.push(c); else o.push(c);
        if (sel) {
          var right = p.x < W - 220;
          later.push('<text class="halo" x="' + (p.x + (right ? 10 : -10)).toFixed(1) + '" y="' + (cy + p.y - 9).toFixed(1) + '" text-anchor="' + (right ? "start" : "end") +
            '" font-size="16" font-weight="800" fill="#13213c">' + esc(d.district) + " " + d[ind] + "%</text>");
        }
      });
      o.push(later.join(""));
    });
    o.push("</svg>");
    return o.join("");
  }

  PS.register("districts", function () {
    var dd = D.districts;
    if (!dd) return '<div class="panel"><h2>District data not exported</h2><p class="note">Run eval/fetch_nfhs5.py, then demo.export --only districts.</p></div>';
    PS.pickDefaultDistrict();
    var st = byCode(S.state) || { state: S.state, nfhs5: {}, pt: {} };
    var inState = drows().filter(function (r) { return r.state_code === S.state; });
    var d = inState.filter(function (r) { return r.district === S.district; })[0];
    var presetId = null;
    Object.keys(dd.presets).forEach(function (k) { if (dd.presets[k].district === S.district && dd.presets[k].state_code === S.state) presetId = k; });
    var opts = rows().slice().sort(function (a, b) { return a.state < b.state ? -1 : 1; }).map(function (r) {
      return '<option value="' + r.code + '"' + (r.code === S.state ? " selected" : "") + ">" + esc(r.state) + "</option>";
    }).join("");
    var pre = Object.keys(dd.presets).map(function (k) {
      var p = dd.presets[k];
      return '<button data-preset="' + k + '" aria-pressed="' + (presetId === k) + '">' + esc(p.district) + (p.note ? " (Melghat)" : "") + "</button>";
    }).join("");
    var card = d ? '<h2 style="font-size:1.25rem">' + esc(d.district) + "</h2>" +
      '<p class="label">' + esc(d.state) + (presetId && dd.presets[presetId].note ? " · " + esc(dd.presets[presetId].note) : "") + " · NFHS-5, children under five</p>" +
      '<div class="kpi num"><div><div class="v" style="color:#b9261a">' + d.wasted + '%</div><div class="k">wasted</div></div>' +
      '<div><div class="v">' + d.severe + '%</div><div class="k">severely wasted</div></div>' +
      '<div><div class="v">' + d.stunted + '%</div><div class="k">stunted</div></div>' +
      '<div><div class="v">' + d.underweight + '%</div><div class="k">underweight</div></div></div>' +
      '<p class="note num">India ' + D.gap.india.nfhs5.wasted + "% wasted (NFHS-5). " + esc(st.state) + ": " + st.nfhs5.wasted + "% surveyed; Poshan Tracker reported " + st.pt.wasted + "% (June 2025, whole state).</p>" +
      (presetId ? '<p><button class="btn primary" data-go-sim="' + presetId + '">Simulate ' + esc(d.district) + "'s children →</button></p>" +
        '<p class="note">Next screens: simulated children whose wasting and stunting are set to ' + esc(d.district) + "'s NFHS-5 values.</p>"
        : '<p class="note">Child-level simulation is precomputed for Nandurbar and Amravati (Melghat).</p>')
      : '<p class="note">Pick a district.</p>';
    var top = inState.slice().sort(function (a, b) { return b.wasted - a.wasted; }).map(function (r) {
      return "<tr><td>" + esc(r.district) + '</td><td class="num">' + r.wasted + '</td><td class="num">' + r.severe + '</td><td class="num">' + r.stunted + '</td><td class="num">' + r.underweight + "</td></tr>";
    }).join("");
    var details = "<h3>Source (REAL)</h3><p>" + esc(dd.source) + ". Data chain: <code>" + esc(dd.source_file) + "</code>. The compilation repository has no licence, so values are cited to the official fact sheets and only these four indicators are exported.</p>" +
      "<p>" + PS.int(dd.rows.length) + " of " + PS.int(dd.n_districts_source) + " districts shown. Excluded: " +
      dd.excluded.map(function (x) { return esc(x.district) + ", " + esc(x.state) + " (" + esc(x.reason) + ")"; }).join("; ") + ".</p>" +
      "<p>These are 2019–21 survey estimates, not current prevalence.</p>" +
      "<h3>" + esc(st.state) + ": all " + inState.length + " districts (%)</h3><table><thead><tr><th>District</th><th>Wasted</th><th>Severe</th><th>Stunted</th><th>Underweight</th></tr></thead><tbody>" + top + "</tbody></table>";
    return PS.slide({
      kind: "real", bodyClass: "g-dist",
      h1: d ? esc(st.state) + ": in " + esc(d.district) + ", " + d.wasted + "% of children under five are wasted" : esc(st.state) + ": " + inState.length + " districts",
      lede: "NFHS-5 district fact sheets. Every dot is a district: coloured in " + esc(st.state) + " (" + inState.length + "), grey for the rest of India.",
      body: '<div class="panel"><div class="row"><label class="label" for="statepick">State/UT</label><select id="statepick" style="font:inherit;padding:.2rem .35rem">' + opts + "</select>" +
        '<span class="label" style="margin-left:.6rem">Drill-down</span><span class="seg" role="group" aria-label="Preset districts">' + pre + "</span></div>" +
        '<div class="fill">' + swarmSvg() + "</div></div>" + '<div class="panel">' + card + "</div>",
      caveat: "<b>Survey estimates for 2019–21</b>, not today's prevalence. They set the level for the simulated children on the next screens; they say nothing about any Anganwadi.",
      src: "REAL. NFHS-5 District Fact Sheets (IIPS/MoHFW); 24/24 spot-checked (V5). " + PS.int(dd.rows.length) + " of " + PS.int(dd.n_districts_source) + " districts (Sahibganj excluded: conflicting rows).",
      detailsTitle: "Districts: source and table", details: details
    });
  });
  PS.renderers.districts.after = function (el) {
    var sel = el.querySelector("#statepick");
    if (sel) sel.onchange = function () { S.state = sel.value; S.district = null; PS.pickDefaultDistrict(); PS.render(); };
    el.querySelectorAll("[data-preset]").forEach(function (b) {
      b.onclick = function () { var p = D.districts.presets[b.dataset.preset]; S.state = p.state_code; S.district = p.district; if (D.sim && D.sim[b.dataset.preset]) S.cohort = b.dataset.preset; PS.render(); };
    });
    el.querySelectorAll("[data-go-sim]").forEach(function (b) {
      b.onclick = function () { if (D.sim && D.sim[b.dataset.goSim]) S.cohort = b.dataset.goSim; S.ex = 0; PS.go(2); };
    });
    el.querySelectorAll("circle.dd").forEach(function (c) {
      var d = drows()[Number(c.dataset.i)];
      c.onmousemove = function (ev) {
        PS.showTip(ev, "<b>" + esc(d.district) + "</b>, " + esc(d.state) + "<br>wasted " + d.wasted + "% · severely " + d.severe + "% · stunted " + d.stunted + "%");
      };
      c.onmouseleave = PS.hideTip;
      c.onclick = function () { S.state = d.state_code; S.district = d.district; PS.render(); };
    });
  };
})();
