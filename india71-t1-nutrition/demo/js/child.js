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
    var W = 940, H = 428, m = { l: 112, r: 70 };
    var dates = [t(c.dob_true)].concat(c.measurements.map(function (x) { return t(x.date); }), c.events.map(function (e) { return t(e.date); }));
    var x0 = Math.min.apply(null, dates) - 20 * 864e5, x1 = Math.max.apply(null, dates) + 25 * 864e5;
    var X = PS.scale(x0, x1, m.l, W - m.r);
    var zs = c.measurements.map(function (x) { return x.whz; }).concat(c.truth_wlz.map(function (x) { return x.wlz; }));
    var zmin = Math.min(-4, Math.floor(Math.min.apply(null, zs) * 2) / 2), zmax = 1;
    var gy0 = 104, gy1 = 345, Y = PS.scale(zmin, zmax, gy1, gy0);
    var o = ['<svg viewBox="0 0 ' + W + " " + H + '" width="100%" role="img" aria-label="Timeline of the example child" class="lanes">'];
    // lanes
    var lanes = [["RCH (MoHFW)", 24], ["U-WIN (MoHFW)", 60]];
    lanes.forEach(function (ln) {
      o.push('<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + ln[1] + '" y2="' + ln[1] + '" stroke="#d5dbe4"></line>');
      o.push('<text class="lane" x="0" y="' + (ln[1] + 4) + '">' + ln[0] + "</text>");
    });
    o.push('<text class="lane" x="0" y="' + (gy0 + 14) + '">Poshan Tracker</text><text x="0" y="' + (gy0 + 30) + '" font-size="12" fill="#4f5b70">(MWCD): weight-</text><text x="0" y="' + (gy0 + 45) + '" font-size="12" fill="#4f5b70">for-height z</text>');
    o.push('<text class="lane" x="0" y="' + (gy1 + 44) + '">Worklist</text>');
    // growth bands (MCP-card colours)
    o.push('<rect x="' + m.l + '" y="' + Y(zmax) + '" width="' + (W - m.r - m.l) + '" height="' + (Y(-2) - Y(zmax)) + '" fill="#dcefe3"></rect>');
    o.push('<rect x="' + m.l + '" y="' + Y(-2) + '" width="' + (W - m.r - m.l) + '" height="' + (Y(-3) - Y(-2)) + '" fill="#fbeec8"></rect>');
    o.push('<rect x="' + m.l + '" y="' + Y(-3) + '" width="' + (W - m.r - m.l) + '" height="' + (Y(zmin) - Y(-3)) + '" fill="#f8dcd8"></rect>');
    [["normal", (zmax - 2) / 2], ["MAM", -2.5], ["SAM", (zmin - 3) / 2]].forEach(function (b) {
      o.push('<text x="' + (W - m.r + 8) + '" y="' + (Y(b[1]) + 5) + '" font-size="13" font-weight="700" fill="#33415c">' + b[0] + "</text>");
    });
    PS.ticks(Math.ceil(zmin), zmax, 1).forEach(function (z) {
      o.push('<text x="' + (m.l - 6) + '" y="' + (Y(z) + 4) + '" font-size="12" text-anchor="end" fill="#4f5b70">' + (z > 0 ? "+" : "") + z + "</text>");
    });
    // x axis: every 3 months
    var d = new Date(x0); d.setUTCDate(1); d.setUTCMonth(d.getUTCMonth() + 1);
    while (d.getTime() < x1) {
      if (d.getUTCMonth() % 3 === 0) {
        var xx = X(d.getTime());
        o.push('<line x1="' + xx + '" x2="' + xx + '" y1="' + gy0 + '" y2="' + gy1 + '" stroke="#ffffff" stroke-width="1.2" opacity=".9"></line>');
        o.push('<text x="' + xx + '" y="' + (gy1 + 18) + '" font-size="12" text-anchor="middle" fill="#4f5b70">' + mon(d.getTime()) + "</text>");
      }
      d.setUTCMonth(d.getUTCMonth() + 1);
    }
    // onset
    var xo = X(t(c.onset.date));
    o.push('<line x1="' + xo + '" x2="' + xo + '" y1="' + (gy0 - 6) + '" y2="' + (gy1 + 30) + '" stroke="#b9261a" stroke-width="2.5"></line>');
    o.push('<text x="' + (xo + 6) + '" y="' + (gy0 - 10) + '" font-size="13" font-weight="800" fill="#b9261a">wasting begins (simulator truth)</text>');
    // truth line
    o.push('<polyline points="' + c.truth_wlz.map(function (p) { return X(t(p.date)).toFixed(1) + "," + Y(p.wlz).toFixed(1); }).join(" ") +
      '" fill="none" stroke="#6f7888" stroke-width="2" stroke-dasharray="5 5"></polyline>');
    // observed
    o.push('<polyline points="' + c.measurements.map(function (p) { return X(t(p.date)).toFixed(1) + "," + Y(p.whz).toFixed(1); }).join(" ") +
      '" fill="none" stroke="#13213c" stroke-width="2.4"></polyline>');
    c.measurements.forEach(function (p) {
      var fill = p.status === "sam" ? "#b9261a" : p.status === "mam" ? "#e3a008" : "#1b7443";
      o.push('<circle cx="' + X(t(p.date)).toFixed(1) + '" cy="' + Y(p.whz).toFixed(1) + '" r="5.5" fill="' + fill + '" stroke="#13213c" stroke-width="1.5"><title>' +
        esc(p.date + ": WHZ " + p.whz + " (" + p.status + "), " + p.weight_kg + " kg, " + p.height_cm + " cm") + "</title></circle>");
    });
    // events
    c.events.forEach(function (e) {
      var ex = X(t(e.date)), ly = e.system === "U-WIN" ? 60 : 24;
      var col = e.kind === "immunisation_missed" ? "#b9261a" : e.kind === "birth_weight" ? "#0a6c8f" : "#8a5a00";
      if (e.kind === "immunisation_missed") {
        o.push('<path d="M' + (ex - 6) + " " + (ly - 6) + " L" + (ex + 6) + " " + (ly + 6) + " M" + (ex + 6) + " " + (ly - 6) + " L" + (ex - 6) + " " + (ly + 6) + '" stroke="' + col + '" stroke-width="3"></path>');
      } else {
        o.push('<circle cx="' + ex + '" cy="' + ly + '" r="7" fill="' + col + '"></circle>');
      }
      var label = KIND[e.kind] + (e.value !== null && e.value !== undefined ? " " + e.value + " kg" + (e.value < 2.5 ? " (low)" : "") : "");
      o.push('<text x="' + (ex + 10) + '" y="' + (ly - 9) + '" font-size="12.5" fill="#13213c">' + esc(label) + "</text>");
    });
    // worklist flags
    c.flags.forEach(function (f) {
      var fx = X(t(f.date)), fy = gy1 + 40, first = f.month_index === c.first_flag_month;
      o.push('<rect x="' + (fx - 7) + '" y="' + (fy - 7) + '" width="14" height="14" fill="' + (first ? "#0a6c8f" : "#7fb3c7") + '" transform="rotate(45 ' + fx + " " + fy + ')"></rect>');
      o.push('<text x="' + fx + '" y="' + (fy + 26) + '" font-size="12" text-anchor="middle" fill="' + (first ? "#13213c" : "#4f5b70") + '"' + (first ? ' font-weight="800"' : "") + ">slot " + f.rank + "</text>");
    });
    o.push("</svg>");
    return o.join("");
  }

  PS.register("child", function () {
    var co = PS.cohort();
    if (!co) return '<div class="panel"><h2>District cohorts not exported</h2></div>';
    var st = co.story, c = st.child, lk = c.link, ref = D.committed.early_warning_v1;
    var bw = c.events.filter(function (e) { return e.kind === "birth_weight"; })[0];
    var miss = c.events.filter(function (e) { return e.kind === "immunisation_missed"; }).length;
    var lead = c.lead_months;
    var head = PS.head("sim", "Example child " + esc(c.ref) + ": Poshan Tracker, RCH and U-WIN records on one timeline.",
      "Born " + PS.dmy(c.dob_true) + (bw ? " at " + bw.value + " kg (RCH)" : "") + "; " + miss + " missed dose" + (miss === 1 ? "" : "s") +
      " in U-WIN. Listed for a home visit <b>" + lead + " month" + (lead === 1 ? "" : "s") + " before</b> wasting began, from Poshan Tracker measurements alone.");
    var prec = co.story.linkage;
    var right = '<div class="panel meet"><h2>How these records met</h2>' +
      '<div class="verdict"><span class="dot" style="background:#6f7888"></span><span><b>Shared-ID join: no link.</b> The Poshan Tracker record (' + esc(c.poshan_record.record_id) +
      ") carries no RCH ID.</span></div>" +
      '<div class="verdict"><span class="dot" style="background:#0a6c8f"></span><span><b>Bloom-filter linkage: joined</b> to ' + esc(c.health_record.record_id) +
      " (Dice " + lk.dice.toFixed(3) + " ≥ " + D.linkage.pprl_threshold + ")" + (lk.linked_correctly ? ", <b>correctly</b>: checked against simulator truth." : ".") + "</span></div>" +
      '<p class="note num">Across this simulated district (' + PS.int(st.n_children) + " children): Bloom-filter linkage re-joined <b>" + PS.pct(prec.pprl_bloom.recall) +
      "</b> of the " + PS.int(prec.gold_pairs) + " with a health record (precision " + PS.pct(prec.pprl_bloom.precision) + "); shared IDs alone " + PS.pct(prec.ids_only.recall) + ".</p>" +
      '<h3>Being listed early is not the norm</h3><p class="note num">The lowest-WHZ rule lists <b>' + PS.pct(co.worklist.recall.lowest_observed_whz[4]) +
      "</b> of new wasting episodes 1–3 months ahead in this district cohort (5 slots per AWC per month; reference synthetic district " +
      PS.pct(ref.methods.lowest_observed_whz.episode_recall) + "). Most episodes are still missed. This child is one of the listed ones.</p>" +
      '<h3>Why link at all</h3><p class="note num">Not for prediction: adding linked health data to a model changes nothing (' +
      ref.methods.logistic_anthro.episode_recall.toFixed(3) + " without vs " + ref.methods.logistic_anthro_plus_linked_health.episode_recall.toFixed(3) +
      " with, committed). For coordination: the SAM list must reach the ASHA and ANM within 2 days (CMAM 2023 p.20), and the same visit can catch up a missed dose.</p></div>";
    return PS.banner() + head + '<div class="grid g-child"><div class="panel">' + timeline(c) +
      '<div class="row label" style="gap:1.1rem"><span>● measured WHZ (normal / MAM / SAM)</span><span>- - - truth, hidden from the system</span><span>◆ listed in the 5 slots (rank)</span><span>✕ missed dose</span></div></div>' +
      right + "</div>" +
      PS.src("SIMULATED child from <code>components/cohort_simulator</code>, calibrated to " + esc(co.district.district) + "'s NFHS-5 wasting and stunting by <code>demo/calibrate_district.py</code>; " +
        "ranks from <code>components/early_warning/eval_v1.py</code> (flag, K = 5); identities from <code>identities_for_cohort</code>, linked by <code>link_pprl_bloom</code>. " +
        "Selection rule: " + esc(st.selection_rule) + " Exported by <code>demo/export.py</code> (sim." + esc(S.cohort) + ".story).");
  });
  PS.renderers.child.after = function () {};
})();
