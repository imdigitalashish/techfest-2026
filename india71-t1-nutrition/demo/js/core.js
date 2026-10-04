/* Poshan Setu demo: shared state, navigation, formatting and small SVG helpers. No network access anywhere. */
(function () {
  "use strict";
  var D = window.DEMO_DATA || {};
  var PS = (window.PS = { D: D, L: window.PoshanLedger, screens: [], renderers: {} });

  PS.SCREENS = [
    { id: "india", name: "India", kind: "real" },
    { id: "districts", name: "Districts", kind: "real" },
    { id: "find", name: "Find every child", kind: "synth" },
    { id: "child", name: "One child", kind: "sim" },
    { id: "week", name: "This week", kind: "sim" },
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
  PS.int = function (x) { return Number(x).toLocaleString("en-IN"); };
  PS.dmy = function (iso) {
    if (!iso) return "–";
    var m = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var p = iso.split("-");
    return Number(p[2]) + " " + m[Number(p[1]) - 1] + " " + p[0];
  };
  PS.human = function (action) { return String(action || "").replace(/_/g, " "); };
  PS.cohort = function () { return D.sim && D.sim[PS.S.cohort]; };
  PS.hasSim = function () { return !!(D.sim && D.sim.order && D.sim.order.length); };

  /* sequential wasting scale (percent): pale sand -> deep red */
  var STOPS = [[0, [251, 243, 213]], [8, [246, 210, 122]], [16, [236, 154, 60]], [24, [212, 81, 42]], [32, [143, 29, 20]]];
  PS.heat = function (v) {
    var x = Math.max(0, Math.min(32, v));
    for (var i = 1; i < STOPS.length; i++) {
      if (x <= STOPS[i][0]) {
        var a = STOPS[i - 1], b = STOPS[i], t = (x - a[0]) / (b[0] - a[0]);
        var c = a[1].map(function (u, j) { return Math.round(u + t * (b[1][j] - u)); });
        return "rgb(" + c.join(",") + ")";
      }
    }
    return "rgb(143,29,20)";
  };
  PS.inkOn = function (v) { return v >= 19 ? "#ffffff" : "#13213c"; };

  PS.scale = function (d0, d1, r0, r1) {
    return function (v) { return r0 + ((v - d0) / (d1 - d0)) * (r1 - r0); };
  };
  PS.ticks = function (lo, hi, step) {
    var out = [];
    for (var v = lo; v <= hi + 1e-9; v += step) out.push(Math.round(v * 1000) / 1000);
    return out;
  };

  PS.src = function (html) { return '<p class="src">' + html + "</p>"; };
  PS.stamp = function (kind) {
    var t = { real: "Real data", synth: "Synthetic", sim: "Simulated children" }[kind];
    return '<div class="stampwrap"><span class="stamp ' + kind + '">' + t + "</span></div>";
  };
  PS.head = function (kind, h1, lede) {
    return '<div class="head"><div><h1>' + h1 + "</h1>" + (lede ? '<p class="lede">' + lede + "</p>" : "") +
      "</div>" + PS.stamp(kind) + "</div>";
  };

  /* banner shown on every simulated-children screen */
  PS.banner = function () {
    var c = PS.cohort();
    if (!c) return "";
    var cal = c.calibration, d = c.district;
    var seg = (D.sim.order || []).map(function (pid) {
      var p = D.sim[pid].district;
      return '<button data-cohort="' + pid + '" aria-pressed="' + (pid === PS.S.cohort) + '">' + PS.esc(p.district) +
        (p.note ? " (Melghat)" : "") + "</button>";
    }).join("");
    return '<div class="banner"><b class="big">SIMULATED children · REAL district rates</b>' +
      '<span class="seg" role="group" aria-label="District">' + seg + "</span>" +
      '<span class="cal num">' +
      "<span>Wasted: NFHS-5 <b>" + cal.target_pct.wasted + "%</b> → simulated <b>" + cal.achieved_pct.wasted + "%</b></span>" +
      "<span>Stunted: <b>" + cal.target_pct.stunted + "%</b> → <b>" + cal.achieved_pct.stunted + "%</b></span>" +
      "<span>Severely wasted (not calibrated): <b>" + cal.target_pct.severe + "%</b> → <b>" + cal.achieved_pct.severe + "%</b></span>" +
      "</span></div>";
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

  PS.render = function () {
    var cur = PS.SCREENS[PS.S.screen];
    var el = document.getElementById("s-" + cur.id);
    var fn = PS.renderers[cur.id];
    try {
      el.innerHTML = fn ? fn() : "";
    } catch (err) {
      el.innerHTML = '<div class="panel"><h2>This screen could not render</h2><p class="note">' + PS.esc(err && err.message) +
        "</p><p class=\"note\">Run the exporter (see demo/README.md) or use the screenshots in demo/fallback/.</p></div>";
      if (window.console) console.error(err);
    }
    if (fn && fn.after) fn.after(el);
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
    if (location.hash.slice(1).split("&")[0] !== id) history.replaceState(null, "", "#" + id + PS.hashExtra());
    PS.render();
    window.scrollTo(0, 0);
  };

  PS.hashExtra = function () {
    return "&cohort=" + PS.S.cohort;
  };
})();
