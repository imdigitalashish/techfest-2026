/* Screen 7 (SIMULATED children, REAL district rates): purpose-bound access (recorded decisions) and a ledger you can
 * try to rewrite (hashes re-verified live in this browser against a simulated external checkpoint). */
(function () {
  "use strict";
  var PS = window.PS, D = PS.D, S = PS.S, esc = PS.esc, L = PS.L;
  var pressed = false;

  var TAMPER = [
    ["intact", "Untouched"],
    ["flip", "Change a deny to allow"],
    ["reseal1", "…and re-seal that entry"],
    ["resealall", "…and re-seal every later entry"],
    ["truncate", "Delete the last 3 entries"]
  ];

  function variant(entries, k) {
    switch (S.tamper) {
      case "flip": return L.flip(entries, k);
      case "reseal1": return L.reseal(L.flip(entries, k), k, k + 1);
      case "resealall": return L.reseal(L.flip(entries, k), k);
      case "truncate": return L.truncate(entries, 3);
      default: return entries.map(function (e) { return Object.assign({}, e); });
    }
  }

  function checkBox(title, res) {
    return '<div class="check ' + (res[0] ? "ok" : "bad") + '"><span class="label">' + title + "</span><b>" + (res[0] ? "✓ chain verifies" : "✗ broken at entry #" + res[1]) + "</b></div>";
  }

  function details(co) {
    var g = co.gate, pg = D.committed.policy_gate, al = D.committed.audit_ledger;
    var rows = g.requests.map(function (r) {
      return "<tr><td>" + esc(r.request_id) + "</td><td>" + esc(r.actor) + "</td><td>" + esc(PS.human(r.purpose)) + "</td><td>" + esc(r.decision) + "</td><td><code>" + esc(r.rule_id) + "</code></td></tr>";
    }).join("");
    var sel = g.requests.filter(function (r) { return r.id === S.req; })[0] || g.requests[0];
    return "<h3>What is live and what is recorded</h3><ul><li><b>Recorded:</b> the six decisions were made by <code>components/policy_gate/gate.py</code> (policy v" + esc(g.policy_version) +
      ") when the data were exported; picking one replays it, it does not call the gate or append a new entry.</li>" +
      "<li><b>Live:</b> every SHA-256 hash below is recomputed in this browser by <code>demo/js/ledger.js</code>, which <code>demo/smoke.sh</code> checks against Python byte for byte.</li>" +
      "<li><b>Simulated:</b> the external checkpoint (entry count + head hash, e.g. signed into the district review minutes) is a stored value here, not an integration.</li></ul>" +
      "<h3>Limits</h3><p>A hash chain detects edits; only a checkpoint outside the adversary's reach detects deletion or wholesale re-sealing. Anyone able to replace both the ledger and the checkpoint defeats this check. The gate can refuse a declared employment purpose; it cannot stop a reader with a legitimate purpose from misusing what they saw, so minimisation, worker participation, a contractual ban and appeals are still needed (ADR 002).</p>" +
      "<h3>Committed tests</h3><p>Red-team suite: " + (pg.n_cases - pg.false_allows) + "/" + pg.n_cases + " correct, " + pg.false_allows + " false allows (<code>eval/results/policy_gate.json</code>). Tamper detection: " +
      Math.round(al.tamper_detection_rate * al.n_mutations) + "/" + al.n_mutations + " mutations (<code>eval/results/audit_ledger.json</code>).</p>" +
      "<h3>The six requests</h3><table><thead><tr><th>id</th><th>who</th><th>purpose</th><th>decision</th><th>rule</th></tr></thead><tbody>" + rows + "</tbody></table>" +
      (sel.legal_basis ? "<h3>Legal basis cited for " + esc(sel.request_id) + "</h3><p>" + esc(sel.legal_basis) + "</p>" : "");
  }

  PS.register("break", function () {
    var co = PS.cohort();
    if (!co) return '<div class="panel"><h2>District cohorts not exported</h2></div>';
    var g = co.gate, led = co.ledger, child = co.story.child;
    var reqs = g.requests.map(function (r) {
      return '<button class="req" data-req="' + r.id + '" aria-pressed="' + (S.req === r.id) + '"><span>' + esc(r.label) + "<small>" + esc(r.actor) + " · " +
        esc(PS.human(r.purpose)) + " · " + esc(PS.human(r.data)) + '</small></span><span class="mini ' + (r.decision === "deny" ? "deny" : "allow") + '">' + (r.decision === "deny" ? "DENY" : "ALLOW") + "</span></button>";
    }).join("");
    var sel = g.requests.filter(function (r) { return r.id === S.req; })[0] || g.requests[0];
    var allow = sel.decision !== "deny";
    var card = '<div class="decision"><span class="bigstamp ' + (allow ? "allow" : "deny") + (pressed ? " press" : "") + '">' + (allow ? "ALLOWED" : "DENIED") + "</span><dl>" +
      "<dt>request</dt><dd>" + esc(sel.request_id) + " about child " + esc(child.child_key_hmac.slice(0, 10)) + "…</dd>" +
      "<dt>who</dt><dd>" + esc(sel.actor) + "</dd><dt>purpose</dt><dd>" + esc(PS.human(sel.purpose)) + "; " + esc(PS.human(sel.data)) + (sel.consent_id ? " (consent " + esc(sel.consent_id) + ")" : "") + "</dd>" +
      "<dt>rule</dt><dd><code>" + esc(sel.rule_id) + "</code></dd><dt>why</dt><dd>" + esc(sel.reason) + "</dd></dl></div>";

    var entries = led.entries, cp = [led.checkpoint.count, led.checkpoint.head], k = led.python_verdicts.flip_index;
    var shown = variant(entries, k);
    var h0 = L.counter.hashes, t0 = performance.now();
    var plain = L.verify(shown), withCp = L.verify(shown, cp);
    var ms = performance.now() - t0, nh = L.counter.hashes - h0;
    var badAt = withCp[0] ? (plain[0] ? -1 : plain[1]) : withCp[1];
    var rows = shown.map(function (e, i) {
      var changed = (S.tamper === "flip" || S.tamper === "reseal1" || S.tamper === "resealall") && i === k;
      return '<tr class="' + (i === badAt || (!plain[0] && i === plain[1]) ? "bad " : "") + (changed ? "changed" : "") + '"><td class="num">' + e.seq + "</td><td>" + esc(e.actor_id) +
        "</td><td>" + esc(e.action) + "</td><td>" + esc(e.object_ref.length > 26 ? e.object_ref.slice(0, 25) + "…" : e.object_ref) + '</td><td class="h">' + esc(e.hash.slice(0, 10)) + "…</td></tr>";
    });
    if (S.tamper === "truncate") rows.push('<tr class="bad"><td colspan="5"><b>3 entries deleted</b> (#' + (entries.length - 3) + "–#" + (entries.length - 1) + ")</td></tr>");
    var tb = TAMPER.map(function (t) { return '<button class="btn" data-tamper="' + t[0] + '" aria-pressed="' + (S.tamper === t[0]) + '">' + t[1] + "</button>"; }).join("");
    var lesson = {
      intact: "Every entry's SHA-256 covers the previous entry's hash.",
      flip: "Editing entry #" + k + " breaks its own hash.",
      reseal1: "Re-computing that one hash breaks the link to entry #" + (k + 1) + ".",
      resealall: "Re-sealing the whole tail gives a chain that verifies; only the checkpoint kept outside catches it.",
      truncate: "Deleting the tail leaves a valid chain; only the checkpoint kept outside catches it."
    }[S.tamper];
    var left = '<div class="panel"><h2>Six requests about the example child</h2><div class="reqs">' + reqs + "</div>" + card + "</div>";
    var right = '<div class="panel"><h2>The week\'s audit ledger (' + entries.length + ' entries): try to rewrite it</h2><div class="tamper" role="group" aria-label="Tamper">' + tb + "</div>" +
      '<div class="checks">' + checkBox("Hash chain alone", plain) + checkBox("Chain + external checkpoint (" + cp[0] + " entries, head " + cp[1].slice(0, 8) + "…)", withCp) + "</div>" +
      '<p class="note num">' + lesson + ' <span class="label">' + nh + " SHA-256 hashes recomputed in " + ms.toFixed(1) + " ms.</span></p>" +
      '<div class="ledger"><table><thead><tr><th>#</th><th>actor</th><th>action</th><th>object</th><th>hash</th></tr></thead><tbody>' + rows.join("") + "</tbody></table></div></div>";
    return PS.slide({
      kind: "sim", banner: true, bodyClass: "g-break",
      h1: "Try to break it: purpose-bound reads, tamper-evident history",
      lede: '<span class="modes"><span class="mode rec">recorded policy decisions (gate.py at export)</span><span class="mode live">live hash verification</span><span class="mode simx">simulated external checkpoint</span></span>',
      body: left + right,
      caveat: "<b>Limit:</b> anyone who can replace both the ledger and the checkpoint defeats this check. The gate refuses declared employment use; it cannot stop misuse by a reader with an allowed purpose.",
      src: "SIMULATED. Decisions: <code>policy_gate/gate.py</code> (policy v" + esc(g.policy_version) + ") at export; red-team suite " + (D.committed.policy_gate.n_cases - D.committed.policy_gate.false_allows) + "/" +
        D.committed.policy_gate.n_cases + ". Ledger: <code>audit_ledger/ledger.py</code>, re-verified by <code>demo/js/ledger.js</code> (checked against Python).",
      detailsTitle: "Break it: what is live, recorded, simulated", details: details(co)
    });
  });
  PS.renderers["break"].after = function (el) {
    pressed = false;
    el.querySelectorAll("[data-req]").forEach(function (b) { b.onclick = function () { S.req = b.dataset.req; pressed = true; PS.render(); }; });
    el.querySelectorAll("[data-tamper]").forEach(function (b) { b.onclick = function () { S.tamper = b.dataset.tamper; PS.render(); }; });
    var box = el.querySelector(".ledger"), bad = el.querySelector(".ledger tr.bad") || el.querySelector(".ledger tr.changed");
    if (box && bad) {  /* scroll to a row boundary so no row is half-hidden under the sticky header */
      var head = box.querySelector("thead"), hh = head ? head.offsetHeight : 0;
      var trs = [].slice.call(box.querySelectorAll("tbody tr")), bi = trs.indexOf(bad);
      var visible = Math.max(1, Math.floor((box.clientHeight - hh) / Math.max(1, bad.offsetHeight)));
      var first = Math.max(0, Math.min(bi - Math.floor(visible / 2), trs.length - visible));
      box.scrollTop = 0;
      box.scrollTop = Math.round(trs[first].getBoundingClientRect().top - box.getBoundingClientRect().top - hh);
    }
  };
})();
