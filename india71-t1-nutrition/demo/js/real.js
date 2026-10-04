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

  function tileSvg() {
    var T = 52, G = 5, W = 10 * (T + G), H = 7 * (T + G);
    var out = ['<svg viewBox="0 0 ' + W + " " + (H + 46) + '" width="100%" style="max-height:25.5rem;display:block;margin:0 auto" role="img" aria-label="Tile grid of States and UTs coloured by wasting">'];
    rows().forEach(function (r) {
      var p = TILES[r.code];
      if (!p) return;
      var v = S.tileMode === "pt" ? r.pt.wasted : r.nfhs5.wasted;
      var x = p[0] * (T + G), y = p[1] * (T + G), sel = r.code === S.state;
      out.push('<g class="tile" data-code="' + r.code + '" style="cursor:pointer" tabindex="0">' +
        '<rect x="' + x + '" y="' + y + '" width="' + T + '" height="' + T + '" rx="5" fill="' + PS.heat(v) + '"' +
        (sel ? ' stroke="#13213c" stroke-width="3.5"' : ' stroke="#ffffff" stroke-width="1"') + "></rect>" +
        '<text x="' + (x + T / 2) + '" y="' + (y + 23) + '" text-anchor="middle" font-size="16" font-weight="800" fill="' + PS.inkOn(v) + '">' + r.code + "</text>" +
        '<text x="' + (x + T / 2) + '" y="' + (y + 40) + '" text-anchor="middle" font-size="12.5" fill="' + PS.inkOn(v) + '" class="num">' + PS.fmt(v, 1) + "</text></g>");
    });
    var lx = 14, ly = H + 14, lw = 300;
    for (var i = 0; i < 64; i++) {
      out.push('<rect x="' + (lx + (i * lw) / 64) + '" y="' + ly + '" width="' + (lw / 64 + 0.6) + '" height="10" fill="' + PS.heat((i / 63) * 32) + '"></rect>');
    }
    [0, 8, 16, 24, 32].forEach(function (t) {
      out.push('<text x="' + (lx + (t / 32) * lw) + '" y="' + (ly + 26) + '" font-size="12" text-anchor="middle" fill="#4f5b70">' + t + "%</text>");
    });
    out.push('<text x="' + (lx + lw + 14) + '" y="' + (ly + 10) + '" font-size="13" fill="#33415c">% of children under five wasted</text>');
    out.push("</svg>");
    return out.join("");
  }

  function scatterSvg() {
    var ind = S.ind, W = 600, H = 378, m = { l: 58, r: 18, t: 14, b: 52 };
    var max = 0;
    rows().forEach(function (r) { max = Math.max(max, r.nfhs5[ind], r.pt[ind]); });
    max = Math.ceil(max / 5) * 5;
    var X = PS.scale(0, max, m.l, W - m.r), Y = PS.scale(0, max, H - m.b, m.t);
    var o = ['<svg viewBox="0 0 ' + W + " " + H + '" width="100%" role="img" aria-label="Poshan Tracker vs NFHS-5 by State/UT">'];
    o.push('<polygon points="' + X(0) + "," + Y(0) + " " + X(max) + "," + Y(0) + " " + X(max) + "," + Y(max) + '" fill="#fbeec8" opacity=".55"></polygon>');
    PS.ticks(0, max, max > 30 ? 10 : 5).forEach(function (t) {
      o.push('<line x1="' + X(t) + '" x2="' + X(t) + '" y1="' + Y(0) + '" y2="' + Y(max) + '" stroke="#e3e7ee"></line>');
      o.push('<line x1="' + X(0) + '" x2="' + X(max) + '" y1="' + Y(t) + '" y2="' + Y(t) + '" stroke="#e3e7ee"></line>');
      o.push('<text x="' + X(t) + '" y="' + (H - m.b + 18) + '" font-size="13" text-anchor="middle" fill="#4f5b70">' + t + "</text>");
      o.push('<text x="' + (m.l - 8) + '" y="' + (Y(t) + 4) + '" font-size="13" text-anchor="end" fill="#4f5b70">' + t + "</text>");
    });
    o.push('<line x1="' + X(0) + '" y1="' + Y(0) + '" x2="' + X(max) + '" y2="' + Y(max) + '" stroke="#13213c" stroke-width="1.5" stroke-dasharray="6 5"></line>');
    o.push('<text x="' + (X(max) - 6) + '" y="' + (Y(max) + 16) + '" font-size="13" text-anchor="end" fill="#13213c" transform="rotate(0)">reported = surveyed</text>');
    o.push('<text class="halo" x="' + (X(max) - 8) + '" y="' + Y(max * 0.5) + '" font-size="14" font-weight="700" text-anchor="end" fill="#8a5a00">reported lower than surveyed</text>');
    o.push('<text x="' + ((m.l + W - m.r) / 2) + '" y="' + (H - 10) + '" font-size="14" text-anchor="middle" fill="#13213c">NFHS-5 survey, 2019–21 (% of children under five)</text>');
    o.push('<text x="16" y="' + ((m.t + H - m.b) / 2) + '" font-size="14" text-anchor="middle" fill="#13213c" transform="rotate(-90 16 ' + ((m.t + H - m.b) / 2) + ')">Poshan Tracker, June 2025 (%)</text>');
    rows().forEach(function (r) {
      var sel = r.code === S.state;
      o.push('<circle class="pt" data-code="' + r.code + '" cx="' + X(r.nfhs5[ind]) + '" cy="' + Y(r.pt[ind]) + '" r="' + (sel ? 8 : 6) + '" fill="' +
        (sel ? "#e3a008" : "#0a6c8f") + '" stroke="' + (sel ? "#13213c" : "#ffffff") + '" stroke-width="' + (sel ? 2.5 : 1.2) + '" style="cursor:pointer"></circle>');
      if (sel) { var right = X(r.nfhs5[ind]) > W * 0.68; o.push('<text class="halo" x="' + (X(r.nfhs5[ind]) + (right ? -11 : 11)) + '" y="' + (Y(r.pt[ind]) - 10) + '" text-anchor="' + (right ? "end" : "start") + '" font-size="14" font-weight="700" fill="#13213c">' + esc(r.state) + "</text>"); }
    });
    var ind0 = D.gap.india;
    o.push('<rect x="' + (X(ind0.nfhs5[ind]) - 7) + '" y="' + (Y(ind0.pt[ind]) - 7) + '" width="14" height="14" fill="#13213c" transform="rotate(45 ' + X(ind0.nfhs5[ind]) + " " + Y(ind0.pt[ind]) + ')"></rect>');
    o.push('<text class="halo" x="' + (X(ind0.nfhs5[ind]) - 12) + '" y="' + (Y(ind0.pt[ind]) - 14) + '" text-anchor="end" font-size="14" font-weight="800" fill="#13213c">India ' + ind0.nfhs5[ind] + "% → " + ind0.pt[ind] + "%</text>");
    o.push("</svg>");
    return o.join("");
  }

  PS.register("india", function () {
    var g = D.gap;
    if (!g) return '<div class="panel"><h2>Missing data</h2></div>';
    var c = g.counts[S.ind], st = byCode(S.state);
    var seg = function (key, val, label) {
      return '<button data-' + key + '="' + val + '" aria-pressed="' + (S[key === "tile" ? "tileMode" : "ind"] === val) + '">' + label + "</button>";
    };
    return PS.head("real", "Poshan Tracker reports less wasting than the national survey in all " + g.counts.wasted.n + " States and UTs.",
      "India: <b>" + g.india.nfhs5.wasted + "%</b> of children under five wasted in NFHS-5 (2019–21), <b>" + g.india.pt.wasted +
      "%</b> in Poshan Tracker (June 2025). Stunting roughly agrees (" + g.india.nfhs5.stunted + "% vs " + g.india.pt.stunted + "%); the weight-based indicators do not.") +
      '<div class="grid g-india">' +
      '<div class="panel"><div class="row" style="justify-content:space-between"><h2>Wasting by State/UT</h2>' +
      '<span class="seg" role="group" aria-label="Source">' + seg("tile", "nfhs5", "Surveyed: NFHS-5") + seg("tile", "pt", "Reported: Poshan Tracker") + "</span></div>" +
      tileSvg() +
      '<p class="note">Tile grid, not a map: approximate positions, no boundaries. Click a state for its districts.</p></div>' +
      '<div class="panel"><div class="row" style="justify-content:space-between"><h2>Reported vs surveyed, each State/UT</h2>' +
      '<span class="seg" role="group" aria-label="Indicator">' + seg("ind", "wasted", "Wasted") + seg("ind", "stunted", "Stunted") + seg("ind", "underweight", "Underweight") + "</span></div>" +
      scatterSvg() +
      '<p class="note num"><b>' + IND[S.ind] + ":</b> Poshan Tracker lower than NFHS-5 in <b>" + c.pt_lower + " of " + c.n + "</b> States/UTs." +
      (st ? " Selected: " + esc(st.state) + " — NFHS-5 " + st.nfhs5[S.ind] + "%, Poshan Tracker " + st.pt[S.ind] + "%." : "") + "</p></div></div>" +
      '<div class="caveat"><b>Not a like-for-like comparison.</b> ' + esc(g.caveat) + " The Ministry has said administrative data \u201csuffer from data gaps due to coverage, measurement, training etc.\u201d (Rajya Sabha reply, as reported by News18, 5 Dec 2025).</div>" +
      PS.src("REAL. NFHS-5: " + esc(g.nfhs5_source) + ". Poshan Tracker: " + esc(g.pt_source) + ". File: <code>" + esc(g.source_file) + "</code>.");
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
      var near = placed.filter(function (q) { return Math.abs(q.x - p.x) < 2 * r + 0.6; });
      for (var k = 0; k < 60; k++) {
        var y = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * step * 0.5;
        var ok = near.every(function (q) { var dx = q.x - p.x, dy = q.y - y; return dx * dx + dy * dy >= step * step; });
        if (ok) { p.y = y; break; }
      }
      placed.push(p);
    });
    var out = {};
    pts.forEach(function (p) { out[p.i] = p; });
    return (swarmCache[key] = out);
  }

  function swarmSvg() {
    var W = 940, m = { l: 92, r: 18 }, r = 2.9;
    var top = 0;
    drows().forEach(function (d) { top = Math.max(top, d.wasted, d.stunted); });
    top = Math.ceil(top / 5) * 5;
    var X = PS.scale(0, top, m.l, W - m.r);
    var half = 0;
    ["wasted", "stunted"].forEach(function (ind) { var pos = swarm(ind, X, r); Object.keys(pos).forEach(function (k) { half = Math.max(half, Math.abs(pos[k].y)); }); });
    half += r + 4;
    var strip = 2 * half + 34;
    var o = ['<svg viewBox="0 0 ' + W + " " + (2 * strip + 8) + '" width="100%" role="img" aria-label="NFHS-5 districts: wasting and stunting">'];
    [["wasted", "Wasted"], ["stunted", "Stunted"]].forEach(function (pair, si) {
      var ind = pair[0], cy = 4 + si * strip + half, pos = swarm(ind, X, r);
      o.push('<text x="0" y="' + (cy + 5) + '" font-size="15" font-weight="700" fill="#13213c">' + pair[1] + "</text>");
      o.push('<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + (cy + half + 2) + '" y2="' + (cy + half + 2) + '" stroke="#d5dbe4"></line>');
      PS.ticks(0, top, 10).forEach(function (t) {
        o.push('<text x="' + X(t) + '" y="' + (cy + half + 18) + '" font-size="12" text-anchor="middle" fill="#4f5b70">' + t + "%</text>");
      });
      var later = [];
      drows().forEach(function (d, i) {
        var p = pos[i], inState = d.state_code === S.state, sel = inState && d.district === S.district;
        var c = '<circle class="dd" data-i="' + i + '" cx="' + p.x.toFixed(1) + '" cy="' + (cy + p.y).toFixed(1) + '" r="' + (sel ? 6.5 : inState ? r + 0.6 : r) + '" fill="' +
          (sel ? "#e3a008" : inState ? "#0a6c8f" : "#c3cad5") + '"' + (sel ? ' stroke="#13213c" stroke-width="2.2"' : "") + ' style="cursor:pointer"></circle>';
        if (inState) later.push(c); else o.push(c);
        if (sel) later.push('<text class="halo" x="' + (p.x + 10).toFixed(1) + '" y="' + (cy + p.y - 9).toFixed(1) + '" font-size="14" font-weight="800" fill="#13213c">' + esc(d.district) + " " + d[ind] + "%</text>");
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
    var h1 = d ? esc(st.state) + ": " + inState.length + " districts. In " + esc(d.district) + ", " + d.wasted + "% of children under five are wasted."
      : esc(st.state) + ": " + inState.length + " districts.";
    var card = d ? '<h2 style="font-size:1.35rem;margin-bottom:.1rem">' + esc(d.district) + "</h2>" +
      '<p class="label" style="margin:0 0 .6rem">' + esc(d.state) + (presetId && dd.presets[presetId].note ? " · " + esc(dd.presets[presetId].note) : "") + " · NFHS-5, children under five</p>" +
      '<div class="kpi num"><div><div class="v" style="color:#b9261a">' + d.wasted + '%</div><div class="k">wasted</div></div>' +
      '<div><div class="v">' + d.severe + '%</div><div class="k">severely wasted</div></div>' +
      '<div><div class="v">' + d.stunted + '%</div><div class="k">stunted</div></div>' +
      '<div><div class="v">' + d.underweight + '%</div><div class="k">underweight</div></div></div>' +
      '<p class="note num">India (NFHS-5): ' + D.gap.india.nfhs5.wasted + "% wasted. " + esc(st.state) + ": " + st.nfhs5.wasted +
      "% in NFHS-5; Poshan Tracker reported " + st.pt.wasted + "% for the whole state in June 2025.</p>" +
      (presetId ? '<p style="margin:.9rem 0 0"><button class="btn primary" data-go-sim="' + presetId + '">Simulate ' + esc(d.district) + "'s children →</button></p>" +
        '<p class="note">Next screens: simulated children whose wasting and stunting rates are set to ' + esc(d.district) + "'s NFHS-5 values.</p>"
        : '<p class="note" style="margin-top:.9rem">Child-level simulation is precomputed for Nandurbar and Amravati (Melghat). Pick one to continue.</p>')
      : '<p class="note">Pick a district.</p>';
    return PS.head("real", h1, "NFHS-5 district fact sheets: every dot is one district. Coloured dots are in " + esc(st.state) + "; grey dots are the rest of India.") +
      '<div class="grid g-dist"><div class="panel">' +
      '<div class="row" style="margin-bottom:.4rem"><label class="label" for="statepick">State/UT</label><select id="statepick" style="font:inherit;padding:.3rem .4rem">' + opts + "</select>" +
      '<span class="label" style="margin-left:.8rem">Drill-down</span><span class="seg" role="group" aria-label="Preset districts">' + pre + "</span></div>" +
      swarmSvg() + "</div>" +
      '<div class="panel">' + card + "</div></div>" +
      PS.src("REAL. " + esc(dd.source) + ". " + PS.int(dd.rows.length) + " of " + PS.int(dd.n_districts_source) + " districts shown" +
        (dd.excluded.length ? " (" + dd.excluded.map(function (x) { return esc(x.district) + ", " + esc(x.state) + ": " + esc(x.reason); }).join("; ") + ")" : "") +
        ". Data: <code>" + esc(dd.source_file) + "</code>.");
  });
  PS.renderers.districts.after = function (el) {
    var sel = el.querySelector("#statepick");
    if (sel) sel.onchange = function () { S.state = sel.value; S.district = null; PS.pickDefaultDistrict(); PS.render(); };
    el.querySelectorAll("[data-preset]").forEach(function (b) {
      b.onclick = function () { var p = D.districts.presets[b.dataset.preset]; S.state = p.state_code; S.district = p.district; S.cohort = b.dataset.preset; PS.render(); };
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
