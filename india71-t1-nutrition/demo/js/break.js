/* Screen 7 (SIMULATED children, REAL district rates): purpose-bound access and a ledger you can try to rewrite. */
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

  function checkBox(title, res, extra) {
    var ok = res[0];
    return '<div class="check ' + (ok ? "ok" : "bad") + '"><span class="label">' + title + "</span><b>" +
      (ok ? "✓ chain verifies" : "✗ broken at entry #" + res[1]) + "</b>" + (extra ? '<span class="label">' + extra + "</span>" : "") + "</div>";
  }

  PS.register("break", function () {
    var co = PS.cohort();
    if (!co) return '<div class="panel"><h2>District cohorts not exported</h2></div>';
    var g = co.gate, led = co.ledger, child = co.story.child;
    var reqs = g.requests.map(function (r) {
      return '<button class="req" data-req="' + r.id + '" aria-pressed="' + (S.req === r.id) + '"><span>' + esc(r.label) + "<small>" + esc(r.actor) + " · " +
        esc(PS.human(r.purpose)) + " · " + esc(PS.human(r.data)) + '</small></span><span class="mini ' + (r.decision === "deny" ? "deny" : "allow") + '">' +
        (r.decision === "deny" ? "DENY" : "ALLOW") + "</span></button>";
    }).join("");
    var sel = g.requests.filter(function (r) { return r.id === S.req; })[0] || g.requests[0];
    var allow = sel.decision !== "deny";
    var card = '<div class="decision"><span class="bigstamp ' + (allow ? "allow" : "deny") + (pressed ? " press" : "") + '">' + (allow ? "ALLOWED" : "DENIED") + "</span><dl>" +
      "<dt>request</dt><dd>" + esc(sel.request_id) + " about child " + esc(child.child_key_hmac.slice(0, 12)) + "…</dd>" +
      "<dt>who</dt><dd>" + esc(sel.actor) + "</dd><dt>purpose</dt><dd>" + esc(PS.human(sel.purpose)) + "</dd><dt>data</dt><dd>" + esc(PS.human(sel.data)) +
      (sel.consent_id ? " (consent ID " + esc(sel.consent_id) + ")" : "") + "</dd>" +
      "<dt>rule</dt><dd><code>" + esc(sel.rule_id) + "</code></dd><dt>why</dt><dd>" + esc(sel.reason) + "</dd>" +
      (sel.legal_basis ? '<dt>basis</dt><dd class="label" style="font-size:.8rem" title="' + esc(sel.legal_basis) + '">' + esc(sel.legal_basis.length > 118 ? sel.legal_basis.slice(0, 115) + "…" : sel.legal_basis) + "</dd>" : "") +
      "</dl></div>";

    var entries = led.entries, cp = [led.checkpoint.count, led.checkpoint.head], k = led.python_verdicts.flip_index;
    var shown = variant(entries, k);
    var t0 = performance.now();
    var plain = L.verify(shown), withCp = L.verify(shown, cp);
    var ms = performance.now() - t0;
    var badAt = withCp[0] ? -1 : withCp[1];
    var rows = shown.map(function (e, i) {
      var changed = (S.tamper === "flip" || S.tamper === "reseal1" || S.tamper === "resealall") && i === k;
      return '<tr class="' + (i === badAt || (!plain[0] && i === plain[1]) ? "bad " : "") + (changed ? "changed" : "") + '"><td class="num">' + e.seq + "</td><td>" + esc(e.actor_id) +
        "</td><td>" + esc(e.action) + "</td><td>" + esc(e.object_ref.length > 30 ? e.object_ref.slice(0, 29) + "…" : e.object_ref) + "</td><td>" + esc(e.decision_ref || "") +
        '</td><td class="h">' + esc(e.hash.slice(0, 10)) + "…</td></tr>";
    });
    if (S.tamper === "truncate") rows.push('<tr class="bad"><td colspan="6"><b>3 entries deleted</b> (#' + (entries.length - 3) + "–#" + (entries.length - 1) + ")</td></tr>");
    var tb = TAMPER.map(function (t) { return '<button class="btn" data-tamper="' + t[0] + '" aria-pressed="' + (S.tamper === t[0]) + '">' + t[1] + "</button>"; }).join("");
    var lesson = {
      intact: "Every entry's SHA-256 covers the previous entry's hash.",
      flip: "Editing entry #" + k + " breaks its own hash.",
      reseal1: "Re-computing that one hash breaks the link to entry #" + (k + 1) + ".",
      resealall: "An insider who re-seals the whole tail gets a chain that verifies. Only the checkpoint kept outside the system catches it.",
      truncate: "Deleting the tail leaves a valid chain. Only the checkpoint kept outside the system catches it."
    }[S.tamper];
    var pg = D.committed.policy_gate, al = D.committed.audit_ledger;
    return PS.banner() + PS.head("sim", "Try to break it: every read is purpose-bound, and every action is sealed.",
      "Pick a request: the policy gate decides and the decision lands in a hash-chained ledger. Then try to rewrite history. The hashes are recomputed live in this browser.") +
      '<div class="grid g-break"><div class="panel"><h2>Six requests about the example child</h2><div class="reqs">' + reqs + "</div>" + card + "</div>" +
      '<div class="panel"><h2>The week\'s audit ledger (' + entries.length + " entries)</h2>" +
      '<div class="tamper" role="group" aria-label="Tamper">' + tb + "</div>" +
      '<div class="checks">' + checkBox("Hash chain alone", plain) + checkBox("Chain + checkpoint kept outside (" + cp[0] + " entries, head " + cp[1].slice(0, 8) + "…)", withCp) + "</div>" +
      '<p class="note">' + lesson + ' <span class="label num">(' + shown.length + " SHA-256 hashes checked in " + ms.toFixed(1) + " ms)</span></p>" +
      '<div class="ledger"><table><thead><tr><th>#</th><th>actor</th><th>action</th><th>object</th><th>rule</th><th>hash</th></tr></thead><tbody>' + rows.join("") + "</tbody></table></div></div></div>" +
      PS.src("Decisions by <code>components/policy_gate/gate.py</code> (policy v" + esc(g.policy_version) + ") at export; committed red-team suite " + (pg.n_cases - pg.false_allows) + "/" + pg.n_cases +
        ", " + pg.false_allows + " false allows (<code>eval/results/policy_gate.json</code>). Ledger written by <code>components/audit_ledger/ledger.py</code>; committed tamper detection " +
        Math.round(al.tamper_detection_rate * al.n_mutations) + "/" + al.n_mutations + ". This page re-verifies with <code>demo/js/ledger.js</code>, which <code>demo/smoke.sh</code> checks against Python byte for byte. " +
        "Employment use is denied by policy and must also be barred in the data-sharing agreement (ADR 002).");
  });
  PS.renderers["break"].after = function (el) {
    pressed = false;
    el.querySelectorAll("[data-req]").forEach(function (b) { b.onclick = function () { S.req = b.dataset.req; pressed = true; PS.render(); }; });
    el.querySelectorAll("[data-tamper]").forEach(function (b) { b.onclick = function () { S.tamper = b.dataset.tamper; PS.render(); }; });
    var box = el.querySelector(".ledger"), bad = el.querySelector(".ledger tr.bad") || el.querySelector(".ledger tr.changed");
    if (box && bad) box.scrollTop = Math.max(0, bad.offsetTop - box.clientHeight / 2);
  };
})();
