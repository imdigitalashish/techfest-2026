/* Screens 5-6 (SIMULATED children, REAL district rates): this month's prevention slots, then the worker's SMS. */
(function () {
  "use strict";
  var PS = window.PS, D = PS.D, S = PS.S, esc = PS.esc;

  function examples(co) { return [co.story.example].concat(co.examples || []); }
  function showRows() { return window.innerHeight < 820 ? 7 : 10; }

  function listHtml(ex, by, title, cls) {
    var kids = ex.children.slice().sort(function (a, b) { return a[by] - b[by]; });
    var n = Math.min(kids.length, showRows()), rows = ['<li class="lh"><span class="r">#</span><span>child</span><span class="num">WHZ</span><span class="num">Δ kg</span><span class="ev">next 3 mo</span></li>'];
    kids.slice(0, n).forEach(function (k, i) {
      var slot = k[by] <= S.K;
      if (i === S.K) rows.push('<li class="cut" aria-hidden="true"></li>');
      var feat = ex.featured_ref && k.ref === ex.featured_ref;
      rows.push('<li class="' + (slot ? "slot" : "") + (feat ? " featured" : "") + '"><span class="r num">' + (slot ? "#" + k[by] : k[by]) + '</span><span class="ref">' + esc(k.ref) +
        (by === "rank_rule" && k.no_gain_2m ? ' <span class="pill nogain">no gain</span>' : "") + '</span><span class="num">' + PS.fmt(k.whz, 2) + '</span><span class="num">' +
        (k.dw1 === null ? "–" : (k.dw1 > 0 ? "+" : "") + PS.fmt(k.dw1, 1)) + '</span><span class="ev">' + (S.reveal && k.onset_in ? "wasted in " + k.onset_in : "") + "</span></li>");
    });
    var hiddenSlots = Math.max(0, Math.min(S.K, kids.length) - n), more = kids.length - n - hiddenSlots;
    var caught = kids.filter(function (k) { return k[by] <= S.K && k.onset_in; }).length;
    return '<div class="list ' + cls + '"><h3>' + title + "</h3><ol>" + rows.join("") + "</ol>" +
      '<p class="tally">' + (hiddenSlots ? '<span class="label">+ ' + hiddenSlots + " more slot" + (hiddenSlots === 1 ? "" : "s") + " below · </span>" : "") +
      (more > 0 ? '<span class="label">' + more + " not listed · </span>" : "") +
      (S.reveal ? "listed, then wasted within 3 months: <b>" + caught + "</b>" : "") + "</p></div>";
  }

  var SERIES = [
    ["random_within_awc", "random", "#9aa3b2", "4 4"], ["rule_no_gain_2m", "programme rule", "#6f7888", ""],
    ["logistic_anthro_plus_linked_health", "model + linked health", "#6c4fa3", "7 4"], ["lowest_observed_whz", "lowest WHZ (ours)", "#0a6c8f", ""]
  ];
  function recallChart(wl) {
    var W = 470, H = 300, m = { l: 46, r: 14, t: 10, b: 42 };
    var X = PS.scale(1, 10, m.l, W - m.r), Y = PS.scale(0, 0.8, H - m.b, m.t);
    var o = ['<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Episode recall by number of slots">'];
    [0, 0.2, 0.4, 0.6, 0.8].forEach(function (v) {
      o.push('<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(v) + '" y2="' + Y(v) + '" stroke="#e3e7ee"></line><text x="' + (m.l - 6) + '" y="' + (Y(v) + 5) + '" font-size="13" text-anchor="end" fill="#4a566b">' + Math.round(100 * v) + "%</text>");
    });
    wl.K_values.forEach(function (k) { o.push('<text x="' + X(k) + '" y="' + (H - m.b + 17) + '" font-size="13" text-anchor="middle" fill="#4a566b">' + k + "</text>"); });
    o.push('<line x1="' + X(S.K) + '" x2="' + X(S.K) + '" y1="' + m.t + '" y2="' + (H - m.b) + '" stroke="#e3a008" stroke-width="3" opacity=".75"></line>');
    o.push('<text x="' + ((m.l + W - m.r) / 2) + '" y="' + (H - 8) + '" font-size="13.5" text-anchor="middle" fill="#13213c">home-visit slots per AWC per month (K)</text>');
    SERIES.forEach(function (s) {
      var ys = wl.recall[s[0]];
      o.push('<polyline points="' + ys.map(function (v, i) { return X(i + 1).toFixed(1) + "," + Y(v).toFixed(1); }).join(" ") + '" fill="none" stroke="' + s[2] +
        '" stroke-width="' + (s[0] === "lowest_observed_whz" ? 3.2 : 2.2) + '"' + (s[3] ? ' stroke-dasharray="' + s[3] + '"' : "") + "></polyline>");
      o.push('<circle cx="' + X(S.K) + '" cy="' + Y(ys[S.K - 1]) + '" r="4.5" fill="' + s[2] + '"></circle>');
    });
    o.push("</svg>");
    return o.join("");
  }

  function weekDetails(co, wl) {
    var ref = D.committed.early_warning_v2, v1 = D.committed.early_warning_v1;
    var tbl = SERIES.slice().reverse().map(function (s) {
      var ci = ref.bootstrap_95ci[s[0]];
      return "<tr><td>" + s[1] + '</td><td class="num">' + PS.pct(ref.methods[s[0]].episode_recall) + '</td><td class="num">' + (ci ? PS.pct(ci[0]) + "–" + PS.pct(ci[1]) : "") +
        '</td><td class="num">' + PS.pct(wl.recall[s[0]][S.K - 1]) + "</td></tr>";
    }).join("");
    return "<h3>What is counted</h3><p>A new wasting episode: true WLZ below −2 after two months at or above −2 (simulator truth). Counted as caught if the child was in the AWC's K slots 1–3 months before onset. Recall is over <b>rankable</b> episodes: the child was 6 months or older when that window opened (" +
      PS.int(wl.n_episodes) + " of " + PS.int(wl.n_episodes_all) + " here). The other " + PS.pct(wl.infant_pathway_share) + " start in infancy and go to the infant pathway; observed SAM/MAM go to the protocol pathway. Slots are per AWC per month.</p>" +
      "<h3>Committed reference (synthetic district, eval_v2) vs this cohort at K = " + S.K + "</h3><table><thead><tr><th>method</th><th>reference K = 5</th><th>95% CI</th><th>this cohort, K = " + S.K + "</th></tr></thead><tbody>" + tbl + "</tbody></table>" +
      "<p>A transparent rule ships; any model must beat it on real pilot data first (ADR 003). Linked health data add nothing to prediction (" + PS.pct(ref.methods.logistic_anthro.episode_recall) + " vs " +
      PS.pct(ref.methods.logistic_anthro_plus_linked_health.episode_recall) + "). eval_v1 (no infant gate, " + PS.pct(v1.methods.lowest_observed_whz.episode_recall) + ") is kept as history.</p>" +
      "<h3>Lists on the left</h3><p>" + esc(co.example_rule) + ". The first list is the example child's AWC-month.</p>";
  }

  PS.register("week", function () {
    var co = PS.cohort();
    if (!co) return '<div class="panel"><h2>District cohorts not exported</h2></div>';
    var exs = examples(co), i = Math.max(0, Math.min(exs.length - 1, S.ex)), ex = exs[i], wl = co.worklist, ref = D.committed.early_warning_v2;
    var kSeg = wl.K_values.map(function (k) { return '<button data-k="' + k + '" aria-pressed="' + (k === S.K) + '">' + k + "</button>"; }).join("");
    var ci = wl.ci95.diff_lowest_whz_vs_rule[S.K - 1], diff = wl.recall.lowest_observed_whz[S.K - 1] - wl.recall.rule_no_gain_2m[S.K - 1];
    var sig = ci[0] > 0 ? "" : " Not distinguishable from zero at this K.";
    var which = i === 0 ? "example child's AWC-month (" + esc(ex.featured_ref) + " underlined)" : "random AWC-month " + i + " of " + (exs.length - 1);
    var left = '<div class="panel">' +
      '<div class="row"><span class="label">Slots K</span><span class="seg" role="group" aria-label="Slots">' + kSeg + "</span>" +
      '<button class="btn' + (S.reveal ? " primary" : "") + '" data-reveal="1">' + (S.reveal ? "Hide" : "Reveal") + " next 3 months</button>" +
      '<button class="btn" data-ex="-1" aria-label="Previous AWC-month">◀</button><button class="btn" data-ex="1" aria-label="Next AWC-month">▶</button></div>' +
      '<p class="label">' + which + ". Not ranked: " + ex.n_infant_pathway + " infant" + (ex.n_infant_pathway === 1 ? "" : "s") + " under 6 months → infant pathway; " +
      ex.n_observed_sam_mam + " measured SAM/MAM → protocol pathway.</p>" +
      '<div class="lists">' + listHtml(ex, "rank_rule", "Programme rule: no weight gain in 2 months", "base") + listHtml(ex, "rank_whz", "Poshan Setu: closest to the MAM line", "ours") + "</div></div>";
    var right = '<div class="panel"><h2>Every new episode in the district cohort</h2><div class="fill">' + recallChart(wl) + "</div>" +
      '<div class="row label">' + SERIES.slice().reverse().map(function (s) { return '<span><span class="dot" style="background:' + s[2] + '"></span> ' + s[1] + ' <b class="num">' + PS.pct(wl.recall[s[0]][S.K - 1]) + "</b></span>"; }).join("") + "</div>" +
      '<p class="verdict num">K = ' + S.K + ": ours lists <b>" + PS.pct(wl.recall.lowest_observed_whz[S.K - 1]) + "</b> vs " + PS.pct(wl.recall.rule_no_gain_2m[S.K - 1]) +
      " of " + PS.int(wl.n_episodes) + " episodes: " + (diff >= 0 ? "+" : "−") + PS.pp(Math.abs(diff)) + " percentage points (95% CI " + PS.pp(ci[0]) + " to " + PS.pp(ci[1]) + ")." + sig + "</p>" +
      '<p class="note num">Committed reference (K = 5): ' + PS.pct(ref.methods.lowest_observed_whz.episode_recall) + " vs " + PS.pct(ref.methods.rule_no_gain_2m.episode_recall) + ".</p></div>";
    return PS.slide({
      kind: "sim", banner: true, bodyClass: "g-week",
      h1: "AWC " + esc(ex.awc) + ", " + PS.dmy(ex.date) + ": " + S.K + " prevention slot" + (S.K === 1 ? "" : "s") + " this month. Who gets them?",
      lede: ex.n_pool + " children aged 6 months or more, measured normal, ranked two ways. Reveal shows who became wasted in the next 3 months (simulator truth).",
      body: left + right,
      caveat: "<b>Simulated monthly slots;</b> most new episodes are still missed. Infants under 6 months (" + PS.pct(wl.infant_pathway_share) + " of episodes) and measured SAM/MAM bypass ranking.",
      src: "SIMULATED. Frozen protocol <code>components/early_warning/eval_v2.py</code> (infant gate) re-run by <code>demo/export.py</code> on the calibrated simulator; the same code reproduces <code>eval/results/early_warning_v2.json</code> at K = 5.",
      detailsTitle: "This month: definitions and reference", details: weekDetails(co, wl)
    });
  });
  PS.renderers.week.after = function (el) {
    el.querySelectorAll("[data-k]").forEach(function (b) { b.onclick = function () { S.K = Number(b.dataset.k); PS.render(); }; });
    el.querySelectorAll("[data-reveal]").forEach(function (b) { b.onclick = function () { S.reveal = !S.reveal; PS.render(); }; });
    el.querySelectorAll("[data-ex]").forEach(function (b) {
      b.onclick = function () { var n = examples(PS.cohort()).length; S.ex = (S.ex + Number(b.dataset.ex) + n) % n; PS.render(); };
    });
  };

  /* ---------------------------------------------------------------- the worker's SMS */
  PS.register("sms", function () {
    var co = PS.cohort();
    if (!co) return '<div class="panel"><h2>District cohorts not exported</h2></div>';
    var sm = co.sms, ft = sm.featured_task, ab = sm.alerts_by_kind, ex = sm.capacity_exception[0];
    var maxc = Math.max.apply(null, sm.messages.map(function (m) { return m.chars; }));
    var delivered = sm.queue.filter(function (t) { return t.delivered; });
    var blocked = sm.queue.filter(function (t) { return !t.delivered; });
    var cnt = function (list, kind) { return list.filter(function (t) { return t.kind === kind; }).length; };
    var msgs = sm.messages.map(function (m) { return '<div class="sms">' + esc(m.text) + '<span class="c">' + m.chars + " chars</span></div>"; }).join("");
    var label = { sam: "SAM", mam: "MAM", risk_high: "slot" };
    var rows = '<tr><td class="num">1–' + delivered.length + '</td><td colspan="4"><b>on the worker\'s SMS list</b>: ' + cnt(delivered, "sam") + " SAM (refer, share list with ASHA/ANM), " +
      cnt(delivered, "mam") + " MAM" + (cnt(delivered, "risk_high") ? ", " + cnt(delivered, "risk_high") + " prevention" : "") + "; her clock runs</td></tr>" +
      blocked.map(function (t) {
        var pos = sm.queue.indexOf(t) + 1, feat = t.ref === sm.featured_ref;
        return "<tr" + (feat ? ' class="feat"' : "") + '><td class="num">' + pos + '</td><td><span class="pill ' + t.kind + '">' + label[t.kind] + '</span></td><td class="mono">' + esc(t.ref) +
          "</td><td>" + esc(PS.human(t.action)) + "</td><td>retained, not delivered → capacity exception to LS</td></tr>";
      }).join("");
    var notice = (S.K !== sm.K || S.ex !== 0) ? '<p class="notice">Featured pipeline: the example child\'s AWC-month at K = ' + sm.K + ". Screen 5 is set to " +
      (S.K !== sm.K ? "K = " + S.K : "another AWC-month") + "; this screen's routing is precomputed only for the featured week.</p>"
      : '<p class="notice">Featured pipeline: the example child\'s AWC-month at K = ' + sm.K + " (routing precomputed by committed code).</p>";
    var right = '<div class="panel queue">' + notice + "<h2>" + sm.queue.length + " tasks for one worker; her list holds " + sm.capacity + "</h2>" +
      '<table><thead><tr><th>#</th><th>kind</th><th>child</th><th>action</th><th>status</th></tr></thead><tbody>' + rows + "</tbody></table>" +
      (ex ? '<p class="verdict"><b>Lady Supervisor (sector ' + esc(ex.owner_scope) + ')</b>: capacity exception, ' + esc(ex.action.split(": ")[1] || ex.action) + ", review due " + PS.dmy(ex.due_on) + ".</p>" : "") +
      '<p class="note">' + esc(ft.ref || sm.featured_ref) + " (our child) is task " + ft.queue_position + ": <b>" + (ft.delivered ? "delivered" : "not delivered") +
      "</b>, status " + esc(ft.status) + (ft.blocked_reason ? " (" + esc(ft.blocked_reason) + ")" : "") + ", " + (ft.worker_clock ? "worker clock running" : "no worker clock") +
      "; the child's clock has run since " + PS.dmy(ft.child_clock_started_on) + ". Day 8: " + (sm.day8.blocked_still_blocked ? "all " + sm.day8.n_blocked + " blocked tasks stay blocked; none is escalated against the worker." : "check failed") + "</p></div>";
    return PS.slide({
      kind: "sim", banner: true, bodyClass: "g-sms",
      h1: "What the worker receives: one SMS per task, no names, ≤ " + maxc + " characters",
      lede: "AWC " + esc(sm.awc) + ", week of " + PS.dmy(sm.week_of) + ": " + ab.sam + " SAM, " + ab.mam + " MAM and " + ab.risk_high + " prevention slots. Protocol cases fill the list first; what does not fit is not the worker's overdue task.",
      body: '<div class="phone"><div class="screenp"><div class="who">Anganwadi worker · AWC ' + esc(sm.awc) + "</div>" + msgs + "</div></div>" + right,
      caveat: "<b>Simulated week.</b> The capacity exception is our design rule (ADR 002), not an official norm. These exported messages are ≤ " + maxc + " characters; the renderer allows " + sm.render_limit_chars + ".",
      src: "SIMULATED. <code>action_router.route</code> + <code>mark_undelivered</code> (contract v0.3.0) and <code>frontline_worklist/render.py</code> (capacity 10, as in <code>eval/run_pipeline.py</code>); day-8 check by <code>router.escalate</code>.",
      detailsTitle: "SMS: full queue and protocol", details: smsDetails(co)
    });
  });

  function smsDetails(co) {
    var sm = co.sms, dr = sm.district_run;
    var q = sm.queue.map(function (t, i) {
      return '<tr><td class="num">' + (i + 1) + "</td><td>" + esc(t.kind) + '</td><td class="mono">' + esc(t.ref) + "</td><td>" + esc(PS.human(t.action)) + '</td><td class="num">' + t.due_on + "</td><td>" +
        (t.delivered ? "delivered" : "blocked (" + esc(t.blocked_reason) + ")") + "</td><td>" + (t.worker_clock || "none") + "</td></tr>";
    }).join("");
    return "<h3>All tasks after the capacity gate</h3><table><thead><tr><th>#</th><th>kind</th><th>child</th><th>action</th><th>due</th><th>status</th><th>worker clock from</th></tr></thead><tbody>" + q + "</tbody></table>" +
      "<p>Order: <code>frontline_worklist.build_worklists</code> (priority, due date, task id). Tasks off the delivered list become <code>blocked</code> (reason capacity) with no worker clock; one capacity-exception task goes to the Lady Supervisor. <code>escalate()</code> leaves blocked tasks alone.</p>" +
      "<p>" + sm.n_infant_pathway + " infant(s) under 6 months measured normal this month go to the infant pathway (ASHA home visits; not routed in this prototype).</p>" +
      "<p>SAM step 0: " + esc(PS.human(sm.sam_step0.action)) + " within " + sm.sam_step0.due_days + " days (" + esc(sm.sam_step0.protocol_ref) + ").</p>" +
      "<h3>Committed reference district run</h3><p><code>eval/results/pipeline_demo.json</code>: " + PS.int(dr.tasks) + " tasks → " + dr.worklists + " worklists, SMS ≤ " + dr.sms_max_chars + " characters, " +
      dr.escalated_after_8_days + " escalated after 8 days (" + Math.round(100 * dr.assumed_on_time) + "% done on time is an assumption; run before the capacity gate existed).</p>";
  }
})();
