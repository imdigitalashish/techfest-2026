/* Screen 4 (SIMULATED children, REAL district rates): one example child, three registries, one timeline. */
(function () {
  "use strict";
  var PS = window.PS, D = PS.D, S = PS.S, esc = PS.esc;
  var KIND = { birth_weight: "birth weight", illness_diarrhoea: "diarrhoea (ASHA)", immunisation_missed: "dose missed" };

  function t(iso) { return Date.parse(iso + "T00:00:00Z"); }
  function mon(ms) {
    var d = new Date(ms), m = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return m[d.getUTCMonth()] + " " + d.getUTCFullYear();
  }

  function timeline(c) {
    var W = 940, H = 420, m = { l: 118, r: 66 };
    var dates = [t(c.dob_true)].concat(c.measurements.map(function (x) { return t(x.date); }), c.events.map(function (e) { return t(e.date); }));
    var x0 = Math.min.apply(null, dates) - 20 * 864e5, x1 = Math.max.apply(null, dates) + 25 * 864e5;
    var X = PS.scale(x0, x1, m.l, W - m.r);
    var zs = c.measurements.map(function (x) { return x.whz; }).concat(c.truth_wlz.map(function (x) { return x.wlz; }));
    var zmin = Math.min(-4, Math.floor(Math.min.apply(null, zs) * 2) / 2), zmax = 1;
    var gy0 = 104, gy1 = 340, Y = PS.scale(zmin, zmax, gy1, gy0), wy = gy1 + 38;
    var o = ['<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Timeline of the example child" class="lanes">'];
    var lanes = [["RCH (MoHFW)", 24, "RCH"], ["U-WIN (MoHFW)", 62, "U-WIN"]];
    lanes.forEach(function (ln) {
      o.push('<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + ln[1] + '" y2="' + ln[1] + '" stroke="#d5dbe4"></line>');
      o.push('<text x="0" y="' + (ln[1] + 5) + '" font-size="14" font-weight="700" fill="#33415c">' + ln[0] + "</text>");
      if (!c.events.some(function (e) { return e.system === ln[2]; })) {
        o.push('<text x="' + (m.l + 8) + '" y="' + (ln[1] - 7) + '" font-size="13" fill="#4a566b">no record in this window</text>');
      }
    });
    o.push('<text x="0" y="' + (gy0 + 16) + '" font-size="14" font-weight="700" fill="#33415c">Poshan Tracker</text><text x="0" y="' + (gy0 + 33) +
      '" font-size="13" fill="#4a566b">weight-for-</text><text x="0" y="' + (gy0 + 49) + '" font-size="13" fill="#4a566b">height z (WHZ)</text>');
    o.push('<text x="0" y="' + (wy + 5) + '" font-size="14" font-weight="700" fill="#33415c">Worklist</text>');
    o.push('<rect x="' + m.l + '" y="' + Y(zmax) + '" width="' + (W - m.r - m.l) + '" height="' + (Y(-2) - Y(zmax)) + '" fill="#dcefe3"></rect>');
    o.push('<rect x="' + m.l + '" y="' + Y(-2) + '" width="' + (W - m.r - m.l) + '" height="' + (Y(-3) - Y(-2)) + '" fill="#fbeec8"></rect>');
    o.push('<rect x="' + m.l + '" y="' + Y(-3) + '" width="' + (W - m.r - m.l) + '" height="' + (Y(zmin) - Y(-3)) + '" fill="#f8dcd8"></rect>');
    [["normal", (zmax - 2) / 2], ["MAM", -2.5], ["SAM", (zmin - 3) / 2]].forEach(function (b) {
      o.push('<text x="' + (W - m.r + 8) + '" y="' + (Y(b[1]) + 5) + '" font-size="14" font-weight="700" fill="#33415c">' + b[0] + "</text>");
    });
    PS.ticks(Math.ceil(zmin), zmax, 1).forEach(function (z) {
      o.push('<text x="' + (m.l - 6) + '" y="' + (Y(z) + 5) + '" font-size="13" text-anchor="end" fill="#4a566b">' + (z > 0 ? "+" : "") + z + "</text>");
    });
    var d = new Date(x0); d.setUTCDate(1); d.setUTCMonth(d.getUTCMonth() + 1);
    while (d.getTime() < x1) {
      if (d.getUTCMonth() % 3 === 0) {
        var xx = X(d.getTime());
        o.push('<line x1="' + xx + '" x2="' + xx + '" y1="' + gy0 + '" y2="' + gy1 + '" stroke="#ffffff" stroke-width="1.2"></line>');
        o.push('<text x="' + xx + '" y="' + (gy1 + 17) + '" font-size="13" text-anchor="middle" fill="#4a566b">' + mon(d.getTime()) + "</text>");
      }
      d.setUTCMonth(d.getUTCMonth() + 1);
    }
    var xo = X(t(c.onset.date));
    o.push('<line x1="' + xo + '" x2="' + xo + '" y1="' + (gy0 - 4) + '" y2="' + (wy + 14) + '" stroke="#b9261a" stroke-width="2.5"></line>');
    var lbl = "first wasting (simulator truth)", right = xo < W - m.r - 220;
    o.push('<text class="halo" x="' + (xo + (right ? 6 : -6)) + '" y="' + (gy0 - 8) + '" text-anchor="' + (right ? "start" : "end") + '" font-size="14" font-weight="800" fill="#b9261a">' + lbl + "</text>");
    o.push('<polyline points="' + c.truth_wlz.map(function (p) { return X(t(p.date)).toFixed(1) + "," + Y(p.wlz).toFixed(1); }).join(" ") +
      '" fill="none" stroke="#6f7888" stroke-width="2" stroke-dasharray="5 5"></polyline>');
    o.push('<polyline points="' + c.measurements.map(function (p) { return X(t(p.date)).toFixed(1) + "," + Y(p.whz).toFixed(1); }).join(" ") +
      '" fill="none" stroke="#13213c" stroke-width="2.4"></polyline>');
    c.measurements.forEach(function (p) {
      var fill = p.status === "sam" ? "#b9261a" : p.status === "mam" ? "#e3a008" : "#1b7443";
      o.push('<circle cx="' + X(t(p.date)).toFixed(1) + '" cy="' + Y(p.whz).toFixed(1) + '" r="5.5" fill="' + fill + '" stroke="#13213c" stroke-width="1.5"><title>' +
        esc(p.date + ": WHZ " + p.whz + " (" + p.status + "), " + p.weight_kg + " kg, " + p.height_cm + " cm, age " + p.age_m + " months") + "</title></circle>");
      if (p.age_days < 183) {
        o.push('<rect x="' + (X(t(p.date)) - 5).toFixed(1) + '" y="' + (wy - 5) + '" width="10" height="10" rx="2" fill="#c3cad5"><title>under 6 months: infant pathway, not ranked</title></rect>');
      }
    });
    var infants = c.measurements.filter(function (p) { return p.age_days < 183; });
    if (infants.length) {
      o.push('<text id="lbl-infant" x="' + (X(t(infants[0].date)) - 5) + '" y="' + (wy + 27) + '" font-size="13" fill="#4a566b">infant pathway (&lt; 6 months, not ranked)</text>');
    }
    var placed = { RCH: [], "U-WIN": [] };
    c.events.forEach(function (e) {
      var ex = X(t(e.date)), ly = e.system === "U-WIN" ? 62 : 24;
      var col = e.kind === "immunisation_missed" ? "#b9261a" : e.kind === "birth_weight" ? "#0a6c8f" : "#7a4f00";
      if (e.kind === "immunisation_missed") {
        o.push('<path d="M' + (ex - 6) + " " + (ly - 6) + " L" + (ex + 6) + " " + (ly + 6) + " M" + (ex + 6) + " " + (ly - 6) + " L" + (ex - 6) + " " + (ly + 6) + '" stroke="' + col + '" stroke-width="3"></path>');
      } else {
        o.push('<circle cx="' + ex + '" cy="' + ly + '" r="7" fill="' + col + '"></circle>');
      }
      var text = KIND[e.kind] + (e.value !== null && e.value !== undefined ? " " + e.value + " kg" + (e.value < 2.5 ? " (low)" : "") : "");
      var cands = [[10, ly - 9, "start"], [10, ly + 19, "start"], [-10, ly - 9, "end"], [-10, ly + 19, "end"]];
      for (var i = 0; i < cands.length; i++) {
        var bx = PS.textBox(ex + cands[i][0], cands[i][1], text, 13, cands[i][2]);
        if (bx.x1 > W - 2 || bx.x0 < m.l) continue;
        if (placed[e.system].some(function (b) { return PS.overlaps(b, bx); })) continue;
        placed[e.system].push(bx);
        o.push('<text class="halo evlbl" x="' + (ex + cands[i][0]) + '" y="' + cands[i][1] + '" text-anchor="' + cands[i][2] + '" font-size="13" fill="#13213c">' + esc(text) + "</text>");
        break;
      }
    });
    c.flags.forEach(function (f) {
      var fx = X(t(f.date)), first = f.month_index === c.first_flag_month;
      o.push('<rect x="' + (fx - 10) + '" y="' + (wy - 10) + '" width="20" height="20" fill="' + (first ? "#0a6c8f" : "#7fb3c7") + '" transform="rotate(45 ' + fx + " " + wy + ')"><title>listed in slot ' + f.rank + " on " + f.date + "</title></rect>");
      o.push('<text x="' + fx + '" y="' + (wy + 5) + '" text-anchor="middle" font-size="13" font-weight="800" fill="#ffffff">' + f.rank + "</text>");
    });
    o.push("</svg>");
    return o.join("");
  }

  function detailsHtml(co) {
    var st = co.story, c = st.child, cal = co.calibration;
    var meas = c.measurements.map(function (p) {
      return '<tr><td class="num">' + p.date + '</td><td class="num">' + p.age_m + '</td><td class="num">' + p.weight_kg + '</td><td class="num">' + p.height_cm + '</td><td class="num">' + p.whz +
        "</td><td>" + p.status + "</td><td>" + (p.age_days < 183 ? "infant pathway" : p.rankable ? "ranked" : "protocol pathway") + "</td></tr>";
    }).join("");
    var ev = c.events.map(function (e) { return "<li>" + e.date + ": " + esc(KIND[e.kind]) + (e.value ? " " + e.value + " kg" : "") + " (" + e.system + " record " + esc(e.record_id) + ")</li>"; }).join("");
    return "<h3>How this child was chosen</h3><p>" + esc(st.selection_rule) + "</p>" +
      "<h3>Records each department keeps</h3><ul><li>" + esc(c.poshan_record.system) + " " + esc(c.poshan_record.record_id) + ": IDs " + esc(Object.values(c.poshan_record.shared_ids).join(", ")) + "</li>" +
      "<li>" + esc(c.health_record.system) + " " + esc(c.health_record.record_id) + ": IDs " + esc(Object.values(c.health_record.shared_ids).join(", ")) + "</li></ul>" +
      "<p>Encoded link: Dice " + c.link.dice.toFixed(3) + " (" + c.link.method + "), checked against simulator truth: " + (c.link.linked_correctly ? "correct" : "wrong") + ". " +
      "Cohort linkage through the encoded boundary: recall " + PS.pct(st.linkage.pprl_bloom.recall) + ", precision " + PS.pct(st.linkage.pprl_bloom.precision) + "; shared IDs alone recall " + PS.pct(st.linkage.ids_only.recall) + ".</p>" +
      "<h3>Health-system records</h3><ul>" + ev + "</ul>" +
      "<h3>Measurements (Poshan Tracker)</h3><table><thead><tr><th>date</th><th>age (m)</th><th>kg</th><th>cm</th><th>WHZ</th><th>status</th><th>pathway</th></tr></thead><tbody>" + meas + "</tbody></table>" +
      "<h3>Calibration</h3><p>" + esc(cal.method) + ". Simulator WLZ mean " + cal.reference.wlz_mean + " → " + cal.overrides.wlz_mean + "; LAZ at birth " + cal.reference.laz_mean_birth + " → " + cal.overrides.laz_mean_birth +
      ". Fitting prevalence does not validate trajectories, care or predictive value.</p>";
  }

  PS.register("child", function () {
    var co = PS.cohort();
    if (!co) return '<div class="panel"><h2>District cohorts not exported</h2></div>';
    var st = co.story, c = st.child, lk = c.link, ref = D.committed.early_warning_v2, wl = co.worklist;
    var bw = c.events.filter(function (e) { return e.kind === "birth_weight"; })[0];
    var later = c.events.filter(function (e) { return e.kind !== "birth_weight"; });
    var lead = c.lead_months;
    var side = '<div class="panel meet"><h2>How these records met</h2>' +
      '<div class="vrow"><span class="dot" style="background:#6f7888"></span><span><b>Shared-ID join: no link.</b> The Poshan Tracker record carries no RCH ID.</span></div>' +
      '<div class="vrow"><span class="dot" style="background:#0a6c8f"></span><span><b>Encoded linkage: joined</b> (Dice ' + lk.dice.toFixed(3) + ")" + (lk.linked_correctly ? ", <b>correctly</b> (checked against simulator truth)." : ".") + "</span></div>" +
      "<h3>Listed early is not the norm</h3><p class=\"note num\">In this district cohort the rule lists <b>" + PS.pct(wl.recall.lowest_observed_whz[4]) + "</b> of new wasting episodes in children 6 months or older, 1–3 months ahead (5 slots per AWC per month; reference " +
      PS.pct(ref.methods.lowest_observed_whz.episode_recall) + "). Most are missed; this child is one of the listed ones.</p>" +
      "<h3>Why link at all</h3><p class=\"note num\">Not prediction: linked health data leave the model unchanged (" + ref.methods.logistic_anthro.episode_recall.toFixed(3) + " vs " +
      ref.methods.logistic_anthro_plus_linked_health.episode_recall.toFixed(3) + ", committed). Coordination: the SAM list must reach the ASHA and ANM within 2 days (CMAM 2023 p.20); the ASHA's records reach the Anganwadi.</p></div>";
    return PS.slide({
      kind: "sim", banner: true, bodyClass: "g-child",
      h1: "Example child " + esc(c.ref) + ": listed " + lead + " month" + (lead === 1 ? "" : "s") + " before " + (c.sex === "M" ? "his" : "her") + " first wasting episode",
      lede: "Born " + PS.dmy(c.dob_true) + (bw ? " at " + bw.value + " kg (RCH)" : "") + (later.length ? "; " + later.length + " later health record" + (later.length === 1 ? "" : "s") +
        " (" + later.map(function (e) { return e.system; }).filter(function (v, i, a) { return a.indexOf(v) === i; }).join(", ") + ")" : "") +
        ". Never wasted before; under 6 months " + (c.sex === "M" ? "he" : "she") + " was on the infant pathway, not ranked. Listed from Poshan Tracker measurements alone.",
      body: '<div class="panel"><div class="fill">' + timeline(c) + '</div><p class="label">● measured WHZ (normal / MAM / SAM) · - - - truth, hidden from the system · ◆ listed in the 5 slots (rank inside) · ■ infant pathway</p></div>' + side,
      caveat: "<b>One simulated child</b>, chosen by a stated rule (Details) for a first-ever episode that was listed in time. It illustrates the pipeline; it is not evidence that most children are caught.",
      src: "SIMULATED. <code>cohort_simulator</code> calibrated to " + esc(co.district.district) + " (<code>demo/calibrate_district.py</code>); ranks <code>eval_v2</code> (K = 5, infant gate); identities <code>identities_for_cohort</code>, linked by <code>pprl.match_encoded</code>.",
      detailsTitle: "One child: selection rule and records", details: detailsHtml(co)
    });
  });
})();
