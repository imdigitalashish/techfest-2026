/* Screen 3 (SYNTHETIC benchmark): find every child across departments; knobs for ID coverage and typos. */
(function () {
  "use strict";
  var PS = window.PS, D = PS.D, S = PS.S, esc = PS.esc;
  var METHODS = [
    { id: "ids_only", name: "Shared-ID join", sub: "today: works only where the RCH ID was copied", color: "#6f7888" },
    { id: "plaintext_probabilistic", name: "Name matching, pooled", sub: "one side must see the other's names", color: "#6c4fa3" },
    { id: "pprl_bloom", name: "Bloom-filter linkage", sub: "Poshan Setu: names never leave each department", color: "#0a6c8f" }
  ];

  function key(c, n) { return String(c) + "|" + String(n); }
  function cell(c, n) { return D.linkage.cells[key(c, n)]; }

  function trend(axis) {
    var L = D.linkage, W = 330, H = 188, m = { l: 40, r: 12, t: 8, b: 40 };
    var xs = axis === "cov" ? L.coverage_levels : L.noise_levels;
    var xmax = axis === "cov" ? 1 : 0.4;
    var X = PS.scale(0, xmax, m.l, W - m.r), Y = PS.scale(0, 1, H - m.b, m.t);
    var cur = axis === "cov" ? S.cov : S.noise;
    var o = ['<svg viewBox="0 0 ' + W + " " + H + '" width="100%" role="img" aria-label="F1 trend">'];
    [0, 0.25, 0.5, 0.75, 1].forEach(function (t) {
      o.push('<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(t) + '" y2="' + Y(t) + '" stroke="#e3e7ee"></line>');
      o.push('<text x="' + (m.l - 6) + '" y="' + (Y(t) + 4) + '" font-size="12" text-anchor="end" fill="#4f5b70">' + t.toFixed(2) + "</text>");
    });
    xs.forEach(function (x) {
      o.push('<text x="' + X(x) + '" y="' + (H - m.b + 16) + '" font-size="11.5" text-anchor="middle" fill="#4f5b70">' +
        (axis === "cov" ? Math.round(100 * x) : "+" + Math.round(100 * x)) + "</text>");
    });
    o.push('<line x1="' + X(cur) + '" x2="' + X(cur) + '" y1="' + m.t + '" y2="' + (H - m.b) + '" stroke="#e3a008" stroke-width="3" opacity=".7"></line>');
    o.push('<text x="' + ((m.l + W - m.r) / 2) + '" y="' + (H - 8) + '" font-size="12.5" text-anchor="middle" fill="#13213c">' +
      (axis === "cov" ? "% of Poshan Tracker records with the RCH ID" : "extra typos per field (%)") + "</text>");
    METHODS.forEach(function (mm) {
      var pts = xs.map(function (x) {
        var c = axis === "cov" ? cell(x, S.noise) : cell(S.cov, x);
        return [X(x), Y(c[mm.id].f1)];
      });
      o.push('<polyline points="' + pts.map(function (p) { return p[0].toFixed(1) + "," + p[1].toFixed(1); }).join(" ") +
        '" fill="none" stroke="' + mm.color + '" stroke-width="2.5"></polyline>');
      pts.forEach(function (p) { o.push('<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="3.4" fill="' + mm.color + '"></circle>'); });
    });
    o.push("</svg>");
    return o.join("");
  }

  function bitGrid(hexA, hexB, own) {
    var cols = 50, sz = 6, g = 1, W = cols * (sz + g), H = 20 * (sz + g);
    function bit(hex, i) {
      var pos = 999 - i, nib = parseInt(hex.charAt(hex.length - 1 - (pos >> 2)), 16);
      return (nib >> (pos & 3)) & 1;
    }
    var o = ['<svg viewBox="0 0 ' + W + " " + H + '" width="100%" role="img" aria-label="1,000-bit Bloom filter">',
      '<rect x="0" y="0" width="' + W + '" height="' + H + '" fill="#e6eaf0" rx="3"></rect>'];
    for (var i = 0; i < 1000; i++) {
      var a = bit(own === "a" ? hexA : hexB, i);
      if (!a) continue;
      var both = bit(hexA, i) && bit(hexB, i);
      o.push('<rect x="' + ((i % cols) * (sz + g)) + '" y="' + (Math.floor(i / cols) * (sz + g)) + '" width="' + sz + '" height="' + sz + '" fill="' + (both ? "#1b7443" : "#b9261a") + '"></rect>');
    }
    o.push("</svg>");
    return o.join("");
  }

  function recCard(r, idsLabel) {
    function row(k, v) { return "<dt>" + k + "</dt><dd>" + esc(v === null || v === undefined ? "—" : v) + "</dd>"; }
    return '<div class="rec"><div class="sys">' + esc(r.system) + "</div><dl>" +
      row("child", r.child_name) + row("mother", r.mother_name) + row("father", r.father_name) + row("born", r.dob + " · " + (r.sex || "–")) +
      row(idsLabel, Object.values(r.shared_ids).join(", ")) + "</dl></div>";
  }

  PS.register("find", function () {
    var L = D.linkage;
    if (!L) return '<div class="panel"><h2>Linkage grid not exported</h2></div>';
    var c = cell(S.cov, S.noise), c0 = cell(S.cov, 0);
    var covSeg = L.coverage_levels.map(function (v) {
      return '<button data-cov="' + v + '" aria-pressed="' + (v === S.cov) + '">' + Math.round(100 * v) + "%" + (v === 0.35 ? '<span class="star">*</span>' : "") + "</button>";
    }).join("");
    var noiseSeg = L.noise_levels.map(function (v) {
      return '<button data-noise="' + v + '" aria-pressed="' + (v === S.noise) + '">+' + Math.round(100 * v) + "%</button>";
    }).join("");
    var bars = METHODS.map(function (mm) {
      var r = c[mm.id];
      return '<div class="bar"><div class="name">' + mm.name + "<small>" + mm.sub + "</small></div>" +
        '<div class="track"><div class="fill" style="background:' + mm.color + ";transform:scaleX(" + Math.max(0.004, r.f1).toFixed(4) + ')"></div></div>' +
        '<div class="val num" style="color:' + mm.color + '">' + r.f1.toFixed(2) + "</div>" +
        '<div class="sub num">re-joined <b>' + PS.int(r.true_links) + "</b> of " + PS.int(c.gold_pairs) + " children · precision " +
        r.precision.toFixed(2) + " · recall " + r.recall.toFixed(2) + (r.clerical_review_share ? " · " + PS.pct(r.clerical_review_share) + " to clerical review" : "") + "</div></div>";
    }).join("");
    var notes = [];
    if (S.cov === 0) notes.push("With no shared IDs the ID join finds nobody. That is true by definition, not a finding.");
    if (S.cov === 0.35) notes.push("35% is a <b>simulation assumption</b>: the share of Poshan Tracker records that carry the RCH ID is not published.");
    if (S.cov === 1) notes.push("With every ID present the ID join is perfect; Bloom-filter linkage is slightly lower because it also tries to match children who are in only one registry.");
    var pp = c.pprl_bloom.f1, pt = c.plaintext_probabilistic.f1;
    notes.push("Bloom-filter linkage F1 <b>" + pp.toFixed(3) + "</b>" + (S.noise ? " with +" + Math.round(100 * S.noise) + "% typos (" + c0.pprl_bloom.f1.toFixed(3) + " without)" : "") +
      "; pooled name matching " + pt.toFixed(3) + "." + (S.noise >= 0.3 ? " Both degrade as typing gets worse; Bloom-filter linkage degrades less." : ""));

    var priv = "";
    var co = PS.cohort();
    if (co) {
      var ch = co.story.child, lk = ch.link;
      priv = '<h2 style="margin-top:1rem">What crosses the department boundary</h2>' +
        '<div class="records">' + recCard(ch.poshan_record, "IDs") + recCard(ch.health_record, "IDs") + "</div>" +
        '<div class="bits"><figure>' + bitGrid(lk.bits_poshan, lk.bits_health, "a") + "<figcaption>Poshan Tracker side: " + lk.set_poshan + " of 1,000 bits set</figcaption></figure>" +
        "<figure>" + bitGrid(lk.bits_poshan, lk.bits_health, "b") + "<figcaption>RCH side: " + lk.set_health + " bits set. Green = set in both.</figcaption></figure></div>" +
        '<p class="note num">Only bit-strings leave each department (keyed hashes of name, DOB, sex and village). Dice = 2 × ' + lk.set_both + " / (" + lk.set_poshan + " + " + lk.set_health +
        ") = <b>" + lk.dice.toFixed(3) + "</b> ≥ threshold " + D.linkage.pprl_threshold + " → <b>linked</b>" + (lk.linked_correctly ? ", and correctly (checked against simulator truth)" : "") +
        ". Shared-ID join: " + (lk.ids_only_linked ? "linked" : "<b>no link</b> (no common ID)") + ".</p>" +
        '<p class="src">Example pair: the simulated ' + esc(co.district.district) + " child of the next screen. Bloom filters can be attacked (pattern mining, graph matching): linkage stays inside the state vault; hardening is a pilot item.</p>";
    }
    return PS.head("synth", "Find every child's records across departments, without pooling names.",
      "Turn the knobs: fewer records carry the RCH ID; names and birth dates are typed worse. Three ways to re-join a child's records.") +
      '<div class="grid g-link"><div class="panel">' +
      '<div class="knob"><span class="label">Poshan Tracker records that carry the child\'s RCH ID <span class="label">(* simulation assumption)</span></span><span class="seg" role="group">' + covSeg + "</span></div>" +
      '<div class="knob"><span class="label">Extra typing errors per name and date-of-birth field</span><span class="seg" role="group">' + noiseSeg + "</span></div>" +
      '<div class="row" style="margin-bottom:.9rem"><span class="label">Presets</span>' +
      '<button class="btn" data-preset-l="0.35|0">As simulated</button><button class="btn" data-preset-l="0|0">No shared IDs</button><button class="btn" data-preset-l="0|0.4">No IDs, +40% typos</button></div>' +
      '<div class="bars">' + bars + "</div>" +
      '<div class="callout">' + notes.join("<br>") + "</div></div>" +
      '<div class="panel"><h2>F1 across the grid <span class="label">(each dot is a run; lines join runs)</span></h2>' +
      '<div class="row" style="flex-wrap:nowrap;align-items:flex-start"><div style="flex:1">' + trend("cov") + '</div><div style="flex:1">' + trend("noise") + "</div></div>" +
      '<div class="row label" style="gap:1rem">' + METHODS.map(function (mm) { return '<span><span class="dot" style="display:inline-block;background:' + mm.color + '"></span> ' + mm.name + "</span>"; }).join("") + "</div>" +
      priv + "</div></div>" +
      PS.src("SYNTHETIC dual registry: " + PS.int(L.n_children) + " children, seed " + L.seed + " (<code>components/identity_linkage/synth_registries.py</code>), linked by <code>link.py</code>; " +
        "35 runs (7 × 5 grid, no interpolation) by <code>demo/export.py</code>. The 35% / +0% run reproduces <code>eval/results/identity_linkage.json</code> exactly: F1 " +
        D.committed.identity_linkage.ids_only.f1.toFixed(3) + " / " + D.committed.identity_linkage.plaintext_probabilistic.f1.toFixed(3) + " / " + D.committed.identity_linkage.pprl_bloom.f1.toFixed(3) + ".");
  });
  PS.renderers.find.after = function (el) {
    el.querySelectorAll("[data-cov]").forEach(function (b) { b.onclick = function () { S.cov = Number(b.dataset.cov); PS.render(); }; });
    el.querySelectorAll("[data-noise]").forEach(function (b) { b.onclick = function () { S.noise = Number(b.dataset.noise); PS.render(); }; });
    el.querySelectorAll("[data-preset-l]").forEach(function (b) {
      b.onclick = function () { var p = b.dataset.presetL.split("|"); S.cov = Number(p[0]); S.noise = Number(p[1]); PS.render(); };
    });
  };
})();
