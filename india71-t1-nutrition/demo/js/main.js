/* Boot: navigation, keyboard, details drawer, deep links (#screen&key=value, used for the fallback screenshots). */
(function () {
  "use strict";
  var PS = window.PS, S = PS.S;

  var steps = document.getElementById("steps");
  steps.innerHTML = PS.SCREENS.map(function (s, i) {
    var tag = { real: "REAL", synth: "SYNTH", sim: "SIM" }[s.kind];
    return '<button data-step="' + i + '"><span class="num">' + (i + 1) + "</span> " + s.name + '<span class="tag">' + tag + "</span></button>";
  }).join("");
  steps.addEventListener("click", function (ev) {
    var b = ev.target.closest("[data-step]");
    if (b) PS.go(Number(b.dataset.step));
  });

  document.getElementById("main").addEventListener("click", function (ev) {
    var b = ev.target.closest("[data-cohort]");
    if (b && PS.D.sim && PS.D.sim[b.dataset.cohort]) {
      S.cohort = b.dataset.cohort;
      S.ex = 0;
      var p = PS.D.sim[S.cohort].district;
      S.state = p.state_code;
      S.district = p.district;
      PS.go(S.screen);
      return;
    }
    if (ev.target.closest("[data-details]")) PS.setDetails(!PS.detailsOpen);
  });
  document.getElementById("det-close").addEventListener("click", function () { PS.setDetails(false); });

  document.addEventListener("keydown", function (ev) {
    if (ev.target && /input|select|textarea/i.test(ev.target.tagName)) return;
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    var id = PS.SCREENS[S.screen].id;
    if (ev.key === "Escape") { PS.setDetails(false); }
    else if (ev.key.toLowerCase() === "d") { PS.setDetails(!PS.detailsOpen); }
    else if (ev.key === "ArrowRight" || ev.key === "PageDown") { PS.go(S.screen + 1); ev.preventDefault(); }
    else if (ev.key === "ArrowLeft" || ev.key === "PageUp") { PS.go(S.screen - 1); ev.preventDefault(); }
    else if (/^[1-7]$/.test(ev.key)) { PS.go(Number(ev.key) - 1); }
    else if (id === "week" && (ev.key === "+" || ev.key === "=")) { S.K = Math.min(10, S.K + 1); PS.render(); }
    else if (id === "week" && ev.key === "-") { S.K = Math.max(1, S.K - 1); PS.render(); }
    else if (id === "week" && ev.key.toLowerCase() === "r") { S.reveal = !S.reveal; PS.render(); }
  });

  function fromHash() {
    var parts = location.hash.replace(/^#/, "").split("&");
    var idx = 0, details = false;
    PS.SCREENS.forEach(function (s, i) { if (s.id === parts[0]) idx = i; });
    parts.slice(1).forEach(function (kv) {
      var p = kv.split("="), k = decodeURIComponent(p[0] || ""), v = decodeURIComponent(p[1] || "");
      if (k === "details") { details = v === "1" || v === "true"; return; }
      if (!(k in S) || k === "screen") return;
      if (typeof S[k] === "number") S[k] = Number(v);
      else if (typeof S[k] === "boolean") S[k] = v === "1" || v === "true";
      else S[k] = v;
    });
    if (PS.D.sim && !PS.D.sim[S.cohort] && PS.D.sim.order) S.cohort = PS.D.sim.order[0];
    PS.detailsOpen = details;
    return idx;
  }
  window.addEventListener("hashchange", function () { PS.go(fromHash()); });
  window.addEventListener("resize", function () { PS.render(); });

  if (!window.DEMO_DATA) {
    document.getElementById("main").innerHTML = '<div class="panel"><h2>demo/data/demo_data.js is missing</h2><p class="note">Run the exporter (demo/README.md).</p></div>';
    return;
  }
  PS.go(fromHash());
  document.documentElement.setAttribute("data-ready", "1");
})();
