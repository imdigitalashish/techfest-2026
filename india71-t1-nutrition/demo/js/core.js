/* Poshan Setu demo: shared state, slide scaffold, details drawer, formatting, colour and contrast helpers.
 * No network access anywhere: everything comes from window.DEMO_DATA (demo/data/demo_data.js). */
(function () {
  "use strict";
  var D = window.DEMO_DATA || {};
  var PS = (window.PS = { D: D, L: window.PoshanLedger, renderers: {}, details: "", detailsTitle: "", detailsOpen: false });

  PS.SCREENS = [
    { id: "india", name: "India", kind: "real" },
    { id: "districts", name: "Districts", kind: "real" },
    { id: "find", name: "Find every child", kind: "synth" },
    { id: "child", name: "One child", kind: "sim" },
    { id: "week", name: "This month", kind: "sim" },
    { id: "sms", name: "SMS", kind: "sim" },
    { id: "break", name: "Break it", kind: "sim" }
  ];

  PS.S = {
    screen: 0, ind: "wasted", tileMode: "nfhs5", state: "MH", district: "Nandurbar", cohort: "nandurbar",
    cov: 0.35, noise: 0, K: 5, reveal: false, ex: 0, req: "cdpo_discipline", tamper: "intact"
  };

  PS.esc = function (s) {
    return String(s === null || s === undefined ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  PS.fmt = function (x, d) { return x === null || x === undefined ? "–" : Number(x).toFixed(d === undefined ? 1 : d); };
  PS.pct = function (x, d) { return x === null || x === undefined ? "–" : (100 * x).toFixed(d === undefined ? 1 : d) + "%"; };
  PS.pp = function (x, d) { return (100 * x).toFixed(d === undefined ? 1 : d); };
  PS.int = function (x) { return Number(x).toLocaleString("en-IN"); };
  PS.dmy = function (iso) {
    if (!iso) return "–";
    var m = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var p = String(iso).split("-");
    return Number(p[2]) + " " + m[Number(p[1]) - 1] + " " + p[0];
  };
  PS.human = function (action) { return String(action || "").replace(/_/g, " "); };
  PS.cohort = function () { return D.sim && D.sim[PS.S.cohort]; };
  /* highest score threshold chosen by the in-sample precision matching anywhere in the grid */
  PS.maxMatchedThreshold = function () {
    var m = 0;
    Object.keys((D.linkage && D.linkage.cells) || {}).forEach(function (k) {
      var pm = D.linkage.cells[k].pprl_bloom_precision_matched;
      if (pm && !pm.ids_only && pm.threshold > m) m = pm.threshold;
    });
    return m;
  };

  /* sequential wasting scale (percent): pale sand -> deep red */
  var STOPS = [[0, [251, 243, 213]], [8, [246, 210, 122]], [16, [236, 154, 60]], [24, [212, 81, 42]], [32, [143, 29, 20]]];
  PS.heatRGB = function (v) {
    var x = Math.max(0, Math.min(32, v));
    for (var i = 1; i < STOPS.length; i++) {
      if (x <= STOPS[i][0]) {
        var a = STOPS[i - 1], b = STOPS[i], t = (x - a[0]) / (b[0] - a[0]);
        return a[1].map(function (u, j) { return Math.round(u + t * (b[1][j] - u)); });
      }
    }
    return STOPS[STOPS.length - 1][1].slice();
  };
  PS.heat = function (v) { return "rgb(" + PS.heatRGB(v).join(",") + ")"; };
  function lum(rgb) {
    var c = rgb.map(function (u) { u /= 255; return u <= 0.03928 ? u / 12.92 : Math.pow((u + 0.055) / 1.055, 2.4); });
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  }
  PS.contrast = function (rgbA, rgbB) {
    var a = lum(rgbA), b = lum(rgbB);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  };
  /* label colour for a tile: white if it reaches 4.5:1, otherwise black (always >= 4.5:1 where white is not) */
  PS.inkRGB = function (v) {
    var bg = PS.heatRGB(v);
    return PS.contrast(bg, [255, 255, 255]) >= 4.5 ? [255, 255, 255] : [0, 0, 0];
  };
  PS.ink = function (v) { return "rgb(" + PS.inkRGB(v).join(",") + ")"; };

  PS.scale = function (d0, d1, r0, r1) { return function (v) { return r0 + ((v - d0) / (d1 - d0)) * (r1 - r0); }; };
  PS.ticks = function (lo, hi, step) {
    var out = [];
    for (var v = lo; v <= hi + 1e-9; v += step) out.push(Math.round(v * 1000) / 1000);
    return out;
  };
  /* approximate text box for collision checks in SVG user units */
  PS.textBox = function (x, y, text, size, anchor) {
    var w = String(text).length * size * 0.56, h = size * 1.1;
    var x0 = anchor === "end" ? x - w : anchor === "middle" ? x - w / 2 : x;
    return { x0: x0, x1: x0 + w, y0: y - h * 0.82, y1: y + h * 0.18 };
  };
  PS.overlaps = function (a, b) { return a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1; };

  PS.stamp = function (kind) {
    var t = { real: "Real data", synth: "Synthetic", sim: "Simulated children" }[kind];
    return '<div class="stampwrap"><span class="stamp ' + kind + '">' + t + "</span></div>";
  };

  /* banner on every simulated-children screen */
  PS.banner = function () {
    var c = PS.cohort();
    if (!c) return "";
    var cal = c.calibration;
    var seg = (D.sim.order || []).map(function (pid) {
      var p = D.sim[pid].district;
      return '<button data-cohort="' + pid + '" aria-pressed="' + (pid === PS.S.cohort) + '">' + PS.esc(p.district) + (p.note ? " (Melghat)" : "") + "</button>";
    }).join("");
    return '<div class="banner"><b class="big">SIMULATED children · REAL district rates</b>' +
      '<span class="seg" role="group" aria-label="District">' + seg + "</span>" +
      '<span class="num">wasted NFHS-5 <b>' + cal.target_pct.wasted + "%</b> → simulated <b>" + cal.achieved_pct.wasted + "%</b> · stunted <b>" +
      cal.target_pct.stunted + "%</b> → <b>" + cal.achieved_pct.stunted + "%</b> · severe <b>" + cal.target_pct.severe + "%</b> → <b>" +
      cal.achieved_pct.severe + "%</b> (not calibrated)</span></div>";
  };

  /* one slide: [banner] head, body (fills), foot (caveat + source + Details) */
  PS.slide = function (o) {
    PS.details = o.details || "";
    PS.detailsTitle = o.detailsTitle || "Details";
    return (o.banner ? PS.banner() : "") +
      '<div class="head"><div><h1>' + o.h1 + "</h1>" + (o.lede ? '<p class="lede">' + o.lede + "</p>" : "") + "</div>" + PS.stamp(o.kind) + "</div>" +
      '<div class="body ' + (o.bodyClass || "") + '">' + o.body + "</div>" +
      '<div class="foot"><div class="foot-text">' + (o.caveat ? '<p class="caveat">' + o.caveat + "</p>" : "") +
      '<p class="src">' + o.src + "</p></div>" +
      (PS.details ? '<button class="btn details-btn" data-details aria-expanded="' + PS.detailsOpen + '" aria-controls="details">Details<kbd>d</kbd></button>' : "") +
      "</div>";
  };

  /* tooltip */
  var tip;
  PS.showTip = function (ev, html) {
    tip = tip || document.getElementById("tip");
    tip.innerHTML = html;
    tip.style.display = "block";
    var x = ev.clientX + 14, y = ev.clientY + 14;
    var w = tip.offsetWidth, h = tip.offsetHeight;
    if (x + w > window.innerWidth - 8) x = ev.clientX - w - 14;
    if (y + h > window.innerHeight - 8) y = ev.clientY - h - 14;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  };
  PS.hideTip = function () { if (tip) tip.style.display = "none"; };

  PS.register = function (id, fn) { PS.renderers[id] = fn; };

  PS.setDetails = function (open) {
    PS.detailsOpen = !!open && !!PS.details;
    var dr = document.getElementById("details");
    document.getElementById("det-title").textContent = PS.detailsTitle;
    document.getElementById("det-body").innerHTML = PS.details;
    dr.hidden = !PS.detailsOpen;
    document.querySelectorAll("[data-details]").forEach(function (b) { b.setAttribute("aria-expanded", String(PS.detailsOpen)); });
  };

  PS.render = function () {
    var cur = PS.SCREENS[PS.S.screen];
    var el = document.getElementById("s-" + cur.id);
    var fn = PS.renderers[cur.id];
    try {
      el.innerHTML = fn ? fn() : "";
    } catch (err) {
      PS.details = "";
      el.innerHTML = '<div class="panel"><h2>This screen could not render</h2><p class="note">' + PS.esc(err && err.message) +
        '</p><p class="note">Run the exporter (see demo/README.md) or use the screenshots in demo/fallback/.</p></div>';
      if (window.console) console.error(err);
    }
    if (fn && fn.after) fn.after(el);
    PS.setDetails(PS.detailsOpen);
    PS.hideTip();
  };

  PS.go = function (i) {
    var n = PS.SCREENS.length;
    PS.S.screen = Math.max(0, Math.min(n - 1, i));
    document.querySelectorAll(".screen").forEach(function (s, j) { s.classList.toggle("active", j === PS.S.screen); });
    document.querySelectorAll("#steps button").forEach(function (b, j) {
      if (j === PS.S.screen) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current");
    });
    var id = PS.SCREENS[PS.S.screen].id;
    if (location.hash.slice(1).split("&")[0] !== id) history.replaceState(null, "", "#" + id + "&cohort=" + PS.S.cohort);
    PS.render();
    window.scrollTo(0, 0);
  };
})();
