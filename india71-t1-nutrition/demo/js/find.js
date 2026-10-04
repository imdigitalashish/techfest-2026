/* Screen 3 (SYNTHETIC benchmark): re-join a child's records across departments; knobs for ID coverage and typos.
 * Bars show correct (method colour) and false (red) accepted links out of the children truly in both registries. */
(function () {
  "use strict";
  var PS = window.PS, D = PS.D, S = PS.S, esc = PS.esc;
  var METHODS = [
    { id: "ids_only", name: "Shared-ID join", sub: "today: needs the RCH ID copied into Poshan Tracker", color: "#6f7888" },
    { id: "plaintext_probabilistic", name: "Pooled name matching", sub: "names leave the department", color: "#6c4fa3" },
    { id: "pprl_bloom", name: "Encoded linkage, threshold 0.91", sub: "names stay; most children, most false links", color: "#0a6c8f" },
    { id: "pprl_bloom_precision_matched", name: "Encoded linkage, same precision", sub: "threshold raised to pooled matching's precision", color: "#0a6c8f", matched: true }
  ];

  function key(c, n) { return String(c) + "|" + String(n); }
  function cell(c, n) { return D.linkage.cells[key(c, n)]; }

  function barRow(c, mm) {
    var r = c[mm.id], gold = c.gold_pairs;
    var tw = r.true_links / gold, fw = r.false_links / gold;
    var thr = mm.matched ? " (t = " + PS.fmt(r.threshold, 3) + (r.reached ? "" : ", target not reachable") + ")" : "";
    return '<div class="bar' + (mm.matched ? " matched" : "") + '"><div class="name">' + mm.name + "<small>" + mm.sub + "</small></div>" +
      '<div class="track"><div class="fillbar" style="background:' + mm.color + (mm.matched ? ";opacity:.72" : "") + ";transform:scaleX(" + Math.max(0.003, tw).toFixed(4) + ')"></div>' +
      '<div class="fillbar" style="background:#b9261a;left:' + (100 * tw).toFixed(2) + "%;transform:scaleX(" + Math.max(0, Math.min(1 - tw, fw) / Math.max(1e-9, 1 - tw)).toFixed(4) + ')"></div></div>' +
      '<div class="val num" style="color:' + mm.color + '">' + PS.int(r.true_links) + "</div>" +
      '<div class="sub num"><span class="good">' + PS.int(r.true_links) + " correct</span> · <span class=\"bad\">" + PS.int(r.false_links) + " false</span> · precision " +
      PS.pct(r.precision) + " · F1 " + r.f1.toFixed(2) + thr + "</div></div>";
  }

  function verdict(c, c0) {
    var ids = c.ids_only, pl = c.plaintext_probabilistic, bl = c.pprl_bloom, pm = c.pprl_bloom_precision_matched;
    var out = [];
    if (S.cov === 0) out.push("With no shared IDs the ID join finds nobody: true by definition, not a finding.");
    if (pm.reached) {
      out.push("At pooled matching's precision (" + PS.pct(pl.precision) + "), encoded linkage re-joins <b>" + PS.int(pm.true_links) + "</b> children (" +
        PS.int(pm.false_links) + " false) without pooling names; pooled matching " + PS.int(pl.true_links) + " (" + PS.int(pl.false_links) +
        " false); shared IDs " + PS.int(ids.true_links) + ".");
    } else {
      out.push("Pooled matching is perfect here (" + PS.int(pl.false_links) + " false links); encoded linkage cannot reach that precision (best: " +
        PS.int(pm.false_links) + " false at threshold " + PS.fmt(pm.threshold, 3) + ").");
    }
    out.push("Its default threshold re-joins " + PS.int(bl.true_links) + " but accepts <b>" + PS.int(bl.false_links) + " false links</b>: a wrong link misroutes care, so operation needs the higher threshold plus clerical review.");
    if (S.noise > 0) {
      var deg = function (m) { return c[m].f1 - c0[m].f1; };
      var parts = [["pooled matching", "plaintext_probabilistic"], ["encoded linkage", "pprl_bloom"]].map(function (p) {
        var dlt = deg(p[1]);
        return p[0] + (Math.abs(dlt) < 0.005 ? " unchanged" : (dlt < 0 ? " F1 −" : " F1 +") + Math.abs(dlt).toFixed(3));
      });
      out.push("+" + Math.round(100 * S.noise) + "% typos vs none: " + parts.join(", ") + ".");
    }
    return out.join(" ");
  }

  function bitGrid(hexA, hexB, own) {
    var cols = 50, sz = 6, g = 1, W = cols * (sz + g), H = 20 * (sz + g);
    function bit(hex, i) {
      var pos = 999 - i, nib = parseInt(hex.charAt(hex.length - 1 - (pos >> 2)), 16);
      return (nib >> (pos & 3)) & 1;
    }
    var o = ['<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="1,000-bit Bloom filter">', '<rect x="0" y="0" width="' + W + '" height="' + H + '" fill="#e6eaf0" rx="3"></rect>'];
    for (var i = 0; i < 1000; i++) {
      if (!bit(own === "a" ? hexA : hexB, i)) continue;
      var both = bit(hexA, i) && bit(hexB, i);
      o.push('<rect x="' + ((i % cols) * (sz + g)) + '" y="' + (Math.floor(i / cols) * (sz + g)) + '" width="' + sz + '" height="' + sz + '" fill="' + (both ? "#1b7443" : "#b9261a") + '"></rect>');
    }
    o.push("</svg>");
    return o.join("");
  }

  function dept(r, enc) {
    var row = function (k, v) { return "<dt>" + k + "</dt><dd>" + esc(v === null || v === undefined || v === "" ? "—" : v) + "</dd>"; };
    return '<div class="dept"><div class="sys">' + esc(r.system) + '</div><div class="stay">stays inside the department</div><dl>' +
      row("child", r.child_name) + row("mother", r.mother_name) + row("born", r.dob) + row("village", r.village) + "</dl></div>";
  }
  function crossing(enc) {
    return '<div class="tokens">blocking ' + enc.block_tokens.map(function (t) { return t.slice(0, 6); }).join(" ") + " · ID " +
      enc.id_tokens.map(function (t) { return t.slice(0, 6); }).join(" ") + " · sex " + (enc.sex_token ? enc.sex_token.slice(0, 6) : "—") + " …</div>";
  }

  function trend(axis) {
    var L = D.linkage, W = 330, H = 190, m = { l: 40, r: 12, t: 8, b: 40 };
    var xs = axis === "cov" ? L.coverage_levels : L.noise_levels, xmax = axis === "cov" ? 1 : 0.4;
    var X = PS.scale(0, xmax, m.l, W - m.r), Y = PS.scale(0, 1, H - m.b, m.t), cur = axis === "cov" ? S.cov : S.noise;
    var o = ['<svg viewBox="0 0 ' + W + " " + H + '" width="100%" role="img" aria-label="F1 trend">'];
    [0, 0.25, 0.5, 0.75, 1].forEach(function (t) {
      o.push('<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(t) + '" y2="' + Y(t) + '" stroke="#e3e7ee"></line><text x="' + (m.l - 6) + '" y="' + (Y(t) + 4) + '" font-size="12" text-anchor="end" fill="#4a566b">' + t.toFixed(2) + "</text>");
    });
    xs.forEach(function (x) { o.push('<text x="' + X(x) + '" y="' + (H - m.b + 15) + '" font-size="12" text-anchor="middle" fill="#4a566b">' + (axis === "cov" ? Math.round(100 * x) : "+" + Math.round(100 * x)) + "</text>"); });
    o.push('<line x1="' + X(cur) + '" x2="' + X(cur) + '" y1="' + m.t + '" y2="' + (H - m.b) + '" stroke="#e3a008" stroke-width="3" opacity=".7"></line>');
    o.push('<text x="' + ((m.l + W - m.r) / 2) + '" y="' + (H - 8) + '" font-size="12.5" text-anchor="middle" fill="#13213c">' + (axis === "cov" ? "nominal RCH-ID coverage (%)" : "extra error probability per field (%)") + "</text>");
    METHODS.slice(0, 3).forEach(function (mm) {
      var pts = xs.map(function (x) { var c = axis === "cov" ? cell(x, S.noise) : cell(S.cov, x); return [X(x), Y(c[mm.id].f1)]; });
      o.push('<polyline points="' + pts.map(function (p) { return p[0].toFixed(1) + "," + p[1].toFixed(1); }).join(" ") + '" fill="none" stroke="' + mm.color + '" stroke-width="2.5"></polyline>');
      pts.forEach(function (p) { o.push('<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="3.2" fill="' + mm.color + '"></circle>'); });
    });
    o.push("</svg>");
    return o.join("");
  }

  function detailsHtml(c) {
    var L = D.linkage, lk = D.committed.identity_linkage;
    var rows = L.coverage_levels.map(function (cv) {
      var x = cell(cv, S.noise);
      return '<tr><td class="num">' + Math.round(100 * cv) + "% (" + PS.pct(x.poshan_with_rch_id / x.poshan_records) + ')</td>' +
        ["ids_only", "plaintext_probabilistic", "pprl_bloom", "pprl_bloom_precision_matched"].map(function (m) {
          return '<td class="num">' + PS.int(x[m].true_links) + " / " + PS.int(x[m].false_links) + "</td>";
        }).join("") + "</tr>";
    }).join("");
    return "<h3>The department boundary (implemented)</h3><p>Each department runs <code>pprl.encode_department</code> on its own records with a secret key the two departments share and the matcher never receives. Only these columns cross: <code>" +
      L.boundary_columns.join(", ") + "</code>. <code>pprl.match_encoded</code> refuses anything else and reproduces <code>link.link_pprl_bloom</code> decision for decision (tests: <code>components/identity_linkage/test_pprl.py</code>).</p>" +
      "<p>The matcher still learns which records share a blocking, ID or sex token. Bloom-filter encodings are open to published frequency and pattern-mining attacks; keyed hashing is not anonymisation. Hardening (salting, balancing, key rotation) is a pilot item.</p>" +
      "<h3>Correct / false accepted links at +" + Math.round(100 * S.noise) + "% typos</h3><table><thead><tr><th>RCH-ID coverage (realised)</th><th>Shared IDs</th><th>Pooled names</th><th>Encoded 0.91</th><th>Encoded, same precision</th></tr></thead><tbody>" + rows + "</tbody></table>" +
      "<p>Coverage is the generator's probability that a child in both registries has the RCH ID on its Poshan Tracker record; in brackets, the realised share of all Poshan Tracker records. 35% is a simulation assumption. Typos: the generator's extra probability of one entry error per name and date-of-birth field, not a measured Indian error rate.</p>" +
      "<h3>F1 across the grid (35 runs, no interpolation)</h3><div class=\"row\" style=\"flex-wrap:nowrap\"><div style=\"flex:1\">" + trend("cov") + "</div><div style=\"flex:1\">" + trend("noise") + "</div></div>" +
      '<p class="num">Grey: shared IDs · purple: pooled names · blue: encoded linkage at 0.91. The 35% / +0% run reproduces <code>eval/results/identity_linkage.json</code> exactly (F1 ' +
      lk.ids_only.f1.toFixed(3) + " / " + lk.plaintext_probabilistic.f1.toFixed(3) + " / " + lk.pprl_bloom.f1.toFixed(3) + ").</p>" +
      "<h3>Same precision</h3><p>The encoded matcher's one-to-one assignment does not depend on the acceptance threshold (<code>pprl.accept_at</code>), so raising the threshold until precision reaches pooled matching's precision is exact, not interpolated. Where pooled matching is perfect (100% coverage), encoded linkage cannot match it and the row says so.</p>";
  }

  PS.register("find", function () {
    var L = D.linkage;
    if (!L) return '<div class="panel"><h2>Linkage grid not exported</h2></div>';
    var c = cell(S.cov, S.noise), c0 = cell(S.cov, 0);
    var covSeg = L.coverage_levels.map(function (v) {
      return '<button data-cov="' + v + '" aria-pressed="' + (v === S.cov) + '">' + Math.round(100 * v) + "%" + (v === 0.35 ? '<span class="star">*</span>' : "") + "</button>";
    }).join("");
    var noiseSeg = L.noise_levels.map(function (v) { return '<button data-noise="' + v + '" aria-pressed="' + (v === S.noise) + '">+' + Math.round(100 * v) + "%</button>"; }).join("");
    var left = '<div class="panel">' +
      '<div class="knob"><span class="label">Children in both registries whose Poshan Tracker record has the RCH ID <span class="num">(nominal; * simulation assumption; realised ' +
      PS.pct(c.poshan_with_rch_id / c.poshan_records) + " of all records)</span></span><span class=\"seg\" role=\"group\">" + covSeg + "</span></div>" +
      '<div class="knob"><span class="label">Extra typing errors per name and date-of-birth field (generator parameter)</span><span class="seg" role="group">' + noiseSeg + "</span>" +
      ' <span class="label" style="display:inline;margin-left:.5rem">Presets</span> <button class="btn" data-preset-l="0.35|0">As simulated</button> <button class="btn" data-preset-l="0|0.4">No IDs, +40%</button></div>' +
      '<div class="bars">' + METHODS.map(function (mm) { return barRow(c, mm); }).join("") + "</div>" +
      '<p class="callout num">' + verdict(c, c0) + "</p></div>";
    var co = PS.cohort(), right = '<div class="panel"><h2>The boundary: each department encodes on its own side</h2>';
    if (co) {
      var ch = co.story.child, lk = ch.link;
      right += '<div class="boundary">' + dept(ch.poshan_record) + dept(ch.health_record) +
        '<div class="crossing">↓ encoded with a key shared by the two departments; the matcher sees only bit-strings and keyed blocking hashes ↓</div>' +
        '<div class="bitbox">' + bitGrid(lk.bits_poshan, lk.bits_health, "a") + '<div class="cap num">' + lk.set_poshan + " of 1,000 bits set</div>" + crossing(ch.poshan_encoded) + "</div>" +
        '<div class="bitbox">' + bitGrid(lk.bits_poshan, lk.bits_health, "b") + '<div class="cap num">' + lk.set_health + " bits set; green = set in both</div>" + crossing(ch.health_encoded) + "</div>" +
        "</div>" +
        '<p class="note num">Matcher: Dice = 2 × ' + lk.set_both + " / (" + lk.set_poshan + " + " + lk.set_health + ") = <b>" + lk.dice.toFixed(3) + "</b> ≥ " + D.linkage.pprl_threshold +
        " → linked" + (lk.linked_correctly ? ", correctly (checked against simulator truth)" : "") + ". Shared-ID join: no common ID, no link.</p>" +
        '<p class="label">Fixed illustration: the simulated ' + esc(co.district.district) + " child of the next screen, not the grid cell selected on the left.</p>";
    }
    right += "</div>";
    return PS.slide({
      kind: "synth", bodyClass: "g-link",
      h1: "Find a child's records across departments without pooling names",
      lede: "Turn the knobs: fewer Poshan Tracker records carry the RCH ID; names and birth dates are typed worse. Out of " + PS.int(c.gold_pairs) + " children in both registries:",
      body: left + right,
      caveat: "<b>Synthetic benchmark</b> (5,000 children). F1 hides the cost of wrong links: compare correct and false links. Bloom filters can be attacked; the key must stay with the departments.",
      src: "SYNTHETIC. <code>components/identity_linkage</code>: <code>synth_registries.py</code>, <code>link.py</code>, <code>pprl.py</code> (encoded boundary); 35 runs by <code>demo/export.py</code>. 35% / +0% reproduces <code>eval/results/identity_linkage.json</code>.",
      detailsTitle: "Find every child: boundary, grid, definitions", details: detailsHtml(c)
    });
  });
  PS.renderers.find.after = function (el) {
    el.querySelectorAll("[data-cov]").forEach(function (b) { b.onclick = function () { S.cov = Number(b.dataset.cov); PS.render(); }; });
    el.querySelectorAll("[data-noise]").forEach(function (b) { b.onclick = function () { S.noise = Number(b.dataset.noise); PS.render(); }; });
    el.querySelectorAll("[data-preset-l]").forEach(function (b) {
      b.onclick = function () { var p = b.dataset.presetL.split("|"); S.cov = Number(p[0]); S.noise = Number(p[1]); PS.render(); };
    });
  };
})();
