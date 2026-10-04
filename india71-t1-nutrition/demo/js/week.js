/* Screens 5-6 (SIMULATED children, REAL district rates): this week's prevention slots, then the worker's SMS. */
(function () {
  "use strict";
  var PS = window.PS, D = PS.D, S = PS.S, esc = PS.esc;
  var SHOW = 10;

  function examples(co) { return [co.story.example].concat(co.examples || []); }

  function listHtml(ex, by, title, cls) {
    var kids = ex.children.slice().sort(function (a, b) { return a[by] - b[by]; });
    var rows = [];
    kids.slice(0, SHOW).forEach(function (k, i) {
      var r = k[by], slot = r <= S.K;
      if (i === S.K) rows.push('<li class="cut" aria-hidden="true"></li>');
      var feat = ex.featured_ref && k.ref === ex.featured_ref;
      var detail = "WHZ " + PS.fmt(k.whz, 2) + (k.dw1 === null ? "" : " · " + (k.dw1 > 0 ? "+" : "") + PS.fmt(k.dw1, 1) + " kg") +
        (by === "rank_rule" && k.no_gain_2m ? ' <span class="pill mam">no gain</span>' : "");
      rows.push('<li class="' + (slot ? "slot" : "") + (feat ? " featured" : "") + '"><span class="r num">' + (slot ? "#" + r : r) + '</span><span class="ref">' + esc(k.ref) +
        '</span><span class="num">' + detail + '</span><span class="ev">' + (S.reveal && k.onset_in ? "wasted in " + k.onset_in + " mo" : "") + "</span></li>");
    });
    var more = kids.length - SHOW;
    var caught = kids.filter(function (k) { return k[by] <= S.K && k.onset_in; }).length;
    return '<div class="list ' + cls + '"><h3>' + title + "</h3><ol>" + rows.join("") + "</ol>" +
      (more > 0 ? '<p class="label" style="margin:.25rem 0 0">+ ' + more + " more children further down the list</p>" : "") +
      '<p class="tally">' + (S.reveal ? "Listed and then wasted within 3 months: <b>" + caught + "</b>" : "&nbsp;") + "</p></div>";
  }

  function recallChart(wl) {
    var W = 470, H = 330, m = { l: 46, r: 16, t: 14, b: 46 };
    var X = PS.scale(1, 10, m.l, W - m.r), Y = PS.scale(0, 0.7, H - m.b, m.t);
    var series = [
      ["random_within_awc", "random", "#9aa3b2", "4 4"], ["rule_no_gain_2m", "programme rule", "#6f7888", ""],
      ["logistic_anthro_plus_linked_health", "model + linked health", "#6c4fa3", "7 4"], ["lowest_observed_whz", "lowest WHZ (ours)", "#0a6c8f", ""]
    ];
    var o = ['<svg viewBox="0 0 ' + W + " " + H + '" width="100%" role="img" aria-label="Episode recall by number of slots">'];
    [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7].forEach(function (v) {
      o.push('<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(v) + '" y2="' + Y(v) + '" stroke="#e3e7ee"></line>');
      o.push('<text x="' + (m.l - 6) + '" y="' + (Y(v) + 4) + '" font-size="12" text-anchor="end" fill="#4f5b70">' + Math.round(100 * v) + "%</text>");
    });
    wl.K_values.forEach(function (k) {
      o.push('<text x="' + X(k) + '" y="' + (H - m.b + 17) + '" font-size="12" text-anchor="middle" fill="#4f5b70">' + k + "</text>");
    });
    o.push('<line x1="' + X(S.K) + '" x2="' + X(S.K) + '" y1="' + m.t + '" y2="' + (H - m.b) + '" stroke="#e3a008" stroke-width="3" opacity=".75"></line>');
    o.push('<text x="' + ((m.l + W - m.r) / 2) + '" y="' + (H - 10) + '" font-size="13" text-anchor="middle" fill="#13213c">home-visit slots per AWC per month (K)</text>');
    series.forEach(function (s) {
      var ys = wl.recall[s[0]];
      o.push('<polyline points="' + ys.map(function (v, i) { return X(i + 1).toFixed(1) + "," + Y(v).toFixed(1); }).join(" ") + '" fill="none" stroke="' + s[2] +
        '" stroke-width="' + (s[0] === "lowest_observed_whz" ? 3.2 : 2.2) + '"' + (s[3] ? ' stroke-dasharray="' + s[3] + '"' : "") + "></polyline>");
      var v = ys[S.K - 1];
      o.push('<circle cx="' + X(S.K) + '" cy="' + Y(v) + '" r="4.5" fill="' + s[2] + '"></circle>');
    });
    o.push("</svg>");
    var leg = series.slice().reverse().map(function (s) {
      return '<span><span class="dot" style="display:inline-block;background:' + s[2] + '"></span> ' + s[1] + " <b class=\"num\">" + PS.pct(wl.recall[s[0]][S.K - 1]) + "</b></span>";
    }).join("");
    return o.join("") + '<div class="row label" style="gap:.4rem 1rem">' + leg + "</div>";
  }

  PS.register("week", function () {
    var co = PS.cohort();
    if (!co) return '<div class="panel"><h2>District cohorts not exported</h2></div>';
    var exs = examples(co), i = Math.max(0, Math.min(exs.length - 1, S.ex)), ex = exs[i], wl = co.worklist, ref = D.committed.early_warning_v1;
    var kSeg = wl.K_values.map(function (k) { return '<button data-k="' + k + '" aria-pressed="' + (k === S.K) + '">' + k + "</button>"; }).join("");
    var ci = wl.ci95.diff_whz_minus_rule[S.K - 1];
    var which = i === 0 ? "the example child's AWC-month" : "random AWC-month " + i + " of " + (exs.length - 1);
    return PS.banner() + PS.head("sim", "AWC " + esc(ex.awc) + ", " + PS.dmy(ex.date) + ": " + S.K + " home-visit slot" + (S.K === 1 ? "" : "s") + ". Who gets them?",
      ex.n_pool + " children measured normal, ranked two ways. " + ex.n_observed_sam_mam + " already measured SAM or MAM go to the protocol pathway, not to these slots.") +
      '<div class="grid g-week"><div class="panel">' +
      '<div class="row" style="margin-bottom:.6rem"><span class="label">Slots (K)</span><span class="seg" role="group" aria-label="Slots">' + kSeg + "</span>" +
      '<button class="btn' + (S.reveal ? " primary" : "") + '" data-reveal="1">' + (S.reveal ? "Hide" : "Reveal") + " the next 3 months</button></div>" +
      '<div class="row" style="margin-bottom:.6rem"><button class="btn" data-ex="-1" aria-label="Previous AWC-month">◀</button><button class="btn" data-ex="1" aria-label="Next AWC-month">▶</button>' +
      '<span class="label">Showing ' + which + (i === 0 ? " (" + esc(ex.featured_ref) + " underlined)" : "") + '. Random months are drawn with a fixed seed.</span></div>' +
      '<div class="lists">' + listHtml(ex, "rank_rule", "Programme rule: no weight gain in 2 months", "base") +
      listHtml(ex, "rank_whz", "Poshan Setu: closest to the MAM line (lowest WHZ)", "ours") + "</div>" +
      (S.reveal ? '<p class="note num">In this AWC-month ' + ex.n_onset_next3 + " of the " + ex.n_pool + " children became wasted within 3 months (simulator truth). One month is noisy: the chart on the right counts every episode.</p>" : "") +
      "</div>" +
      '<div class="panel"><h2>Every new wasting episode in the district cohort</h2>' + recallChart(wl) +
      '<p class="note num">Share of ' + PS.int(wl.n_episodes) + " new episodes listed 1–3 months before onset. At K = " + S.K + ": lowest WHZ minus programme rule = " +
      PS.pct(wl.recall.lowest_observed_whz[S.K - 1] - wl.recall.rule_no_gain_2m[S.K - 1]) + " (95% CI " + PS.pct(ci[0]) + " to " + PS.pct(ci[1]) + ", AWC bootstrap).</p>" +
      '<p class="note num">Reference synthetic district (committed, K = 5): lowest WHZ <b>' + ref.methods.lowest_observed_whz.episode_recall.toFixed(3) +
      "</b> (" + ref.bootstrap_95ci.lowest_observed_whz.join("–") + "), programme rule " + ref.methods.rule_no_gain_2m.episode_recall.toFixed(3) +
      ", random " + ref.methods.random_within_awc.episode_recall.toFixed(3) + ". A transparent rule ships; any model must beat it on real pilot data first (ADR 003).</p></div></div>" +
      PS.src("SIMULATED. Frozen protocol <code>components/early_warning/eval_v1.py</code> (train seeds 21–22, test 23–24) re-run by <code>demo/export.py</code> on the simulator calibrated to " +
        esc(co.district.district) + " (sim." + esc(S.cohort) + ".worklist); the same code reproduces the committed reference at K = 5. Lists: " + esc(co.example_rule) + ".");
  });
  PS.renderers.week.after = function (el) {
    el.querySelectorAll("[data-k]").forEach(function (b) { b.onclick = function () { S.K = Number(b.dataset.k); PS.render(); }; });
    el.querySelectorAll("[data-reveal]").forEach(function (b) { b.onclick = function () { S.reveal = !S.reveal; PS.render(); }; });
    el.querySelectorAll("[data-ex]").forEach(function (b) {
      b.onclick = function () {
        var n = examples(PS.cohort()).length;
        S.ex = (S.ex + Number(b.dataset.ex) + n) % n;
        PS.render();
      };
    });
  };

  /* ---------------------------------------------------------------- the worker's SMS */
  PS.register("sms", function () {
    var co = PS.cohort();
    if (!co) return '<div class="panel"><h2>District cohorts not exported</h2></div>';
    var sm = co.sms, ft = sm.featured_task, ab = sm.alerts_by_kind, dr = sm.district_run;
    var maxc = Math.max.apply(null, sm.messages.map(function (m) { return m.chars; }));
    var msgs = sm.messages.map(function (m) {
      var feat = m.text.indexOf(sm.featured_ref + " ") >= 0;
      return '<div class="sms' + (feat ? " featured" : "") + '">' + esc(m.text) + '<span class="c">' + m.chars + " chars</span></div>";
    }).join("");
    var inSms = sm.queue.filter(function (t) { return t.in_sms; });
    var cnt = function (kind) { return inSms.filter(function (t) { return t.kind === kind; }).length; };
    var q = '<tr><td class="num">1–' + inSms.length + '</td><td colspan="5"><b>on this week\'s SMS</b>: ' + cnt("sam") + " SAM (refer, share list with ASHA/ANM), " +
      cnt("mam") + " MAM (counselling)" + (cnt("risk_high") ? ", " + cnt("risk_high") + " prevention" : "") + "</td></tr>" +
      sm.queue.map(function (t, i) {
      if (t.in_sms) return "";
      var feat = t.ref === sm.featured_ref;
      return "<tr" + (feat ? ' style="background:#fbeec8;font-weight:700"' : "") + '><td class="num">' + (i + 1) + '</td><td><span class="pill ' + t.kind + '">' +
        { sam: "SAM", mam: "MAM", risk_high: "slot" }[t.kind] + '</span></td><td class="mono">' + esc(t.ref) + "</td><td>" + esc(PS.human(t.action)) +
        '</td><td class="num">' + PS.dmy(t.due_on) + "</td><td>" + (t.in_sms ? "SMS" : "<b>overflow</b>") + "</td></tr>";
    }).join("");
    var nx = sm.escalation.next[0];
    var ladder = sm.ladder_risk_high.map(function (s) {
      var ref = s.protocol_ref.split(":")[0];
      return "<b>" + esc(s.owner_role.toUpperCase()) + "</b> " + esc(PS.human(s.action)) + " (" + s.due_days + " d" + (ref === "DESIGN" ? ", ours" : ", " + esc(ref)) + ")";
    }).join(" → ");
    return PS.banner() + PS.head("sim", "What the worker receives: one SMS per task, at most " + maxc + " characters, no names.",
      "This week AWC " + esc(sm.awc) + " has " + ab.sam + " SAM and " + ab.mam + " MAM children plus " + ab.risk_high + " prevention slots: " + sm.queue.length +
      " tasks for one worker, whose weekly list holds " + sm.capacity + ". Protocol cases come first, so the prevention visits overflow.") +
      '<div class="grid g-sms"><div><div class="phone"><div class="screenp"><div class="who">Anganwadi worker · AWC ' + esc(sm.awc) + " · week of " + PS.dmy(sm.week_of) + "</div>" + msgs + "</div></div>" +
      '<p class="note" style="text-align:center">Only beneficiary numbers: names appear on the worker\'s own phone, from the app she already uses.</p></div>' +
      '<div class="panel queue"><h2>All ' + sm.queue.length + " tasks, in the order the worklist sorts them</h2><table><thead><tr><th>#</th><th>kind</th><th>child</th><th>action</th><th>due</th><th>this week</th></tr></thead><tbody>" + q + "</tbody></table>" +
      '<p class="note num"><b>' + esc(sm.featured_ref) + "</b>, our example child, is task " + ft.queue_position + " of " + sm.queue.length + (ft.in_sms ? ": on this week's SMS." : ": <b>not</b> on this week's SMS.") +
      (nx ? " If the visit is not done by " + PS.dmy(ft.due_on) + ", on " + PS.dmy(sm.escalation.checked_on) + " the task moves to the <b>" + esc(nx.owner_role.toUpperCase()) + "</b>: " +
        esc(PS.human(nx.action)) + " by " + PS.dmy(nx.due_on) + "." : "") + " Nothing is dropped silently.</p>" +
      '<p class="note"><b>Prevention-visit ladder:</b> ' + ladder + ". \"Ours\" marks Poshan Setu's own rules, not official norms.</p>" +
      '<p class="note">SAM: ' + esc(PS.human(sm.sam_step0.action)) + " within " + sm.sam_step0.due_days + " days (" + esc(sm.sam_step0.protocol_ref.split(":")[0]) + ").</p>" +
      "</div></div>" +
      PS.src("SIMULATED. Alerts for this AWC-month routed by <code>components/action_router</code> (protocol v0.2.0) and rendered by <code>components/frontline_worklist/render.py</code> " +
        "(capacity 10 per worker, as in <code>eval/run_pipeline.py</code>); escalation by <code>router.escalate</code>. Reference district run (committed, <code>eval/results/pipeline_demo.json</code>): " +
        PS.int(dr.tasks) + " tasks → " + dr.worklists + " worklists, SMS ≤ " + dr.sms_max_chars + " characters, " + dr.escalated_after_8_days + " escalated after 8 days (" +
        Math.round(100 * dr.assumed_on_time) + "% done on time assumed).");
  });
})();
