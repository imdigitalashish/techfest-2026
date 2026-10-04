/* NullahNet operations dashboard: an actionable overview of a DashboardBundle (contracts/dashboard_bundle).
   Plain JS, no build step. Design notes: ../PRODUCT.md and ../DESIGN.md.
   Every number on screen comes from dashboard_bundle.json / aux.json; nothing is typed in by hand. */
(function () {
  'use strict';

  var I18N = {
    brief: { en: 'Morning brief', mr: 'सकाळचा आढावा', hi: 'सुबह का सार' },
    actions: { en: 'Actions', mr: 'करावयाची कामे', hi: 'करने योग्य कार्य' },
    map: { en: 'Outfall sites', mr: 'नाला मुख ठिकाणे', hi: 'निकास स्थल' },
    records: { en: 'Clearance claims', mr: 'सफाई दावे', hi: 'सफाई दावे' },
    plans: { en: 'Plan comparison', mr: 'नियोजनांची तुलना', hi: 'योजनाओं की तुलना' },
    detection: { en: 'Camera check', mr: 'कॅमेरा तपासणी', hi: 'कैमरा जाँच' },
    sources: { en: 'Data sources and honesty notes', mr: 'माहितीचे स्रोत', hi: 'डेटा स्रोत' }
  };
  var CREW_MSG = {
    en: function (m) { return 'NullahNet dispatch, ' + m.date + '\n' + m.crew + ': ' + m.site + '\n' + m.start + '–' + m.end + ' IST\nExpected catch about ' + m.kg + ' kg. Photograph the boom before and after clearing and record the weight.'; },
    mr: function (m) { return 'NullahNet कामाचा आदेश, ' + m.date + '\n' + m.crew + ': ' + m.site + '\n' + m.start + '–' + m.end + ' IST\nअंदाजे ' + m.kg + ' किलो कचरा. सफाईपूर्वी व नंतर बूमचे फोटो घ्या आणि वजन नोंदवा.'; },
    hi: function (m) { return 'NullahNet कार्य आदेश, ' + m.date + '\n' + m.crew + ': ' + m.site + '\n' + m.start + '–' + m.end + ' IST\nअनुमानित ' + m.kg + ' किलो कचरा। सफाई से पहले और बाद में बूम की फोटो लें और वज़न दर्ज करें।'; }
  };
  var SHORT = { mithi_mahim: 'Mithi → Mahim Creek', oshiwara_malad: 'Oshiwara → Malad Creek', dahisar_mouth: 'Dahisar mouth', trombay_mahul: 'Trombay nullah' };
  var POLICY = { P2: 'Tide-aware plan', P1: 'Fill-threshold rule', P0: 'Fixed roster (assumed)' };
  var KIND = { dispatch: 'Dispatch', watch: 'Watch', review: 'Check claims' };
  var WATCH = 0.05, HIGH = 0.25; // display thresholds on 24 h overflow/bypass risk: our choice, not calibrated
  var LV = { high: '#b23c17', med: '#8a5a00', low: '#0b6a8c' };

  var S = { B: null, A: {}, via: '', day: null, site: null, l2: 'none', st: {}, acts: {}, entries: [], original: [], bad: new Set(), verified: null, sigProblems: [], all: false, map: null, markers: {} };
  var X = { site: {}, sites: [], days: {}, dayKeys: [], dm: {} };

  /* ------------------------------------------------------------- helpers -- */
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  var IST_MS = 19800000, DAY_MS = 86400000;
  var WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], MO = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function ms(t) { return typeof t === 'number' ? t : Date.parse(t); }
  function ist(t) { return new Date(ms(t) + IST_MS); }
  function hm(t) { var d = ist(t); return pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes()); }
  function dlabel(t, year) { var d = ist(t); return WD[d.getUTCDay()] + ' ' + d.getUTCDate() + ' ' + MO[d.getUTCMonth()] + (year ? ' ' + d.getUTCFullYear() : ''); }
  function dkey(t) { var d = ist(t); return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate()); }
  function num(x, dp) { return x == null || isNaN(x) ? '—' : Number(x).toLocaleString('en-IN', { minimumFractionDigits: dp || 0, maximumFractionDigits: dp || 0 }); }
  function kg(x) { if (x == null || isNaN(x)) return '—'; return x >= 1000 ? num(x / 1000, x >= 10000 ? 0 : 1) + ' t' : num(x) + ' kg'; }
  function pct(p) { if (p == null || isNaN(p)) return '—'; var v = p * 100; return v > 0 && v < 1 ? '<1%' : num(v) + '%'; }
  function mm(x) { return x == null || isNaN(x) ? '—' : num(x, x < 10 ? 1 : 0) + ' mm'; }
  function metres(x) { return x == null || isNaN(x) ? '—' : num(x, 2) + ' m'; }
  function rel(v) { return v == null || isNaN(v) ? '—' : num(Math.abs(v) * 100, 1) + '% ' + (v >= 0 ? 'less' : 'more'); }
  function short(id) { return SHORT[id] || ((X.site[id] || {}).name || id); }
  function crew(id) { return String(id || '').replace(/^crew-?/i, 'Crew '); }
  function toast(t) { var el = $('#toast'); el.textContent = t; el.hidden = false; clearTimeout(toast.h); toast.h = setTimeout(function () { el.hidden = true; }, 3000); }
  function sum(a, f) { return a.reduce(function (s, x) { return s + (f(x) || 0); }, 0); }

  /* ---------------------------------------------------------------- data -- */
  function prep() {
    var B = S.B;
    X.sites = B.sites || []; X.site = {};
    X.sites.forEach(function (s) { X.site[s.site_id] = s; });
    X.forcing = byId(B.forcing); X.inter = byId(B.interceptor);
    X.telem = {};
    (B.telemetry || []).forEach(function (m) { (X.telem[m.site_id] = X.telem[m.site_id] || []).push(m); });
    Object.keys(X.telem).forEach(function (k) { X.telem[k].sort(function (a, b) { return ms(a.t) - ms(b.t); }); });
    X.days = {};
    function day(iso) { var k = dkey(iso); return X.days[k] || (X.days[k] = { key: k, issued: iso, plans: {}, fc: {} }); }
    (B.plans || []).forEach(function (p) { day(p.issued_at).plans[p.policy_id] = p; });
    (B.forecasts || []).forEach(function (f) { var d = day(f.issued_at); (d.fc[f.site_id] = d.fc[f.site_id] || {})[f.horizon_h] = f; });
    X.dayKeys = Object.keys(X.days).sort();
    X.dm = (B.metrics || {})['twin_sim.dispatch'] || {};
  }
  function byId(a) { var o = {}; (a || []).forEach(function (r) { o[r.site_id] = r; }); return o; }
  function today() { return X.days[S.day]; }
  function fc(d, sid, h) { var f = d && d.fc[sid]; return f ? (f[h || 24] || null) : null; }
  function drv(f) { return (f && f.drivers) || {}; }
  function risk(f) { return f ? Math.max(f.p_overflow || 0, drv(f).p_bypass_24h || drv(f).p_bypass_48h || 0) : 0; }
  function level(f) { var p = risk(f); return p >= HIGH ? 'high' : p >= WATCH ? 'med' : 'low'; }
  function assigns(d, pol, sid) { var p = d && d.plans[pol]; return p ? p.assignments.filter(function (a) { return !sid || a.site_id === sid; }) : []; }
  function asOf(e) { var d = today(); return !d || ms(e.record.t_end) <= ms(d.issued) + DAY_MS; }
  function attention() { return S.entries.filter(function (e) { return asOf(e) && (e.reconciliation.flag !== 'ok' || S.bad.has(e.seq)); }); }
  function sev(e) { return S.bad.has(e.seq) ? 3 : e.reconciliation.flag === 'reject' ? 2 : e.reconciliation.flag === 'review' ? 1 : 0; }

  /* ------------------------------------------------------------ language -- */
  function setLang(l2) {
    S.l2 = I18N.brief[l2] || l2 === 'none' ? l2 : 'none';
    $$('[data-i18n]').forEach(function (el) {
      var d = I18N[el.getAttribute('data-i18n')]; if (!d) return;
      el.innerHTML = esc(d.en) + (S.l2 !== 'none' && d[S.l2] ? '<span class="l2" lang="' + S.l2 + '">' + esc(d[S.l2]) + '</span>' : '');
    });
    $$('.lang button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.lang === S.l2)); });
    try { localStorage.setItem('nullahnet-lang2', S.l2); } catch (e) { /* private mode */ }
    if (S.day) renderActions();
  }

  /* --------------------------------------------------------------- days -- */
  function setDay(k) {
    S.day = k;
    var i = X.dayKeys.indexOf(k), d = today();
    $('#daylabel').textContent = dlabel(d.issued, true);
    $('#daysub').textContent = 'plan issued ' + hm(d.issued) + ' IST' + (X.dayKeys.length > 1 ? ' · replay day ' + (i + 1) + ' of ' + X.dayKeys.length : '');
    $('#dayprev').disabled = i <= 0; $('#daynext').disabled = i >= X.dayKeys.length - 1;
    if (!S.site || !X.site[S.site]) S.site = defaultSite(d);
    renderAll();
  }
  function step(k) { var i = X.dayKeys.indexOf(S.day) + k; if (i >= 0 && i < X.dayKeys.length) setDay(X.dayKeys[i]); }
  function defaultSite(d) {
    var a = assigns(d, 'P2')[0]; if (a) return a.site_id;
    var best = X.sites.slice().sort(function (p, q) { return risk(fc(d, q.site_id)) - risk(fc(d, p.site_id)); })[0];
    return best ? best.site_id : null;
  }
  function renderAll() { renderBrief(); renderPipeline(); renderActions(); renderSites(); renderDetail(); renderRecords(); renderPlans(); }

  /* -------------------------------------------------------------- brief -- */
  function siteLink(sid) { return '<a href="#detail" data-site="' + esc(sid) + '">' + esc(short(sid)) + '</a>'; }
  function renderBrief() {
    var d = today(), parts = [];
    var fcs = X.sites.map(function (s) { return { sid: s.site_id, f: fc(d, s.site_id) }; }).filter(function (x) { return x.f; });
    if (fcs.length) {
      var wet = fcs.slice().sort(function (a, b) { return (drv(b.f).rain_mm_next_24h_fc || 0) - (drv(a.f).rain_mm_next_24h_fc || 0); })[0];
      var top = fcs.slice().sort(function (a, b) { return risk(b.f) - risk(a.f); })[0];
      var r = drv(wet.f).rain_mm_next_24h_fc;
      parts.push(r >= 1 ? 'Up to <b>' + mm(r) + '</b> of rain is forecast in the next 24 h, most at ' + siteLink(wet.sid) + '.' : 'Almost no rain is forecast for the next 24 h (at most ' + mm(r) + ').');
      var tide = drv(top.f).max_tide_m_next_24h;
      parts.push((risk(top.f) >= WATCH ? 'Highest overflow risk: ' : 'Overflow risk is low everywhere; highest at ') + siteLink(top.sid) + ', <b>' + pct(risk(top.f)) + '</b> in 24 h' + (tide != null ? ' with the tide up to ' + metres(tide) + ' above mean sea level' : '') + '.');
    }
    var as = assigns(d, 'P2').slice().sort(function (a, b) { return ms(a.start) - ms(b.start); });
    if (as.length) {
      parts.push('Send <b>' + as.length + ' crew' + (as.length > 1 ? 's' : '') + '</b>: ' + as.map(function (a) { return crew(a.crew_id) + ' to ' + siteLink(a.site_id) + ' at ' + hm(a.start); }).join(', ') +
        '. Together they should clear about <b>' + kg(sum(as, function (a) { return a.expected_cleared_kg; })) + '</b> <span class="tag">SIMULATED</span>.');
    } else parts.push('No crews are planned for this day.');
    var at = attention();
    if (at.length) {
      var rj = at.filter(function (e) { return e.reconciliation.flag === 'reject'; }).length;
      parts.push('<a href="#records" data-goto="records"><b>' + at.length + ' clearance claim' + (at.length > 1 ? 's' : '') + '</b></a> need' + (at.length > 1 ? '' : 's') + ' checking before payment' + (rj ? ' (' + rj + ' over the reject threshold)' : '') + '.');
    }
    $('#briefbody').innerHTML = '<p>' + parts.join(' ') + '</p>';
    $('#briefnote').textContent = 'Written by a fixed template from the ' + hm(d.issued) + ' IST forecast, the tide-aware plan and the claims ledger. No language model is involved, and every number appears again below.';
  }
  function renderPipeline() {
    var det = (S.B.metrics || {}).detection, d = today(), items = [];
    items.push(det ? ['ok', 'Camera detector', 'mAP50 ' + num(det.mAP50, 2) + ' on held-out images'] : ['wait', 'Camera detector', 'no results yet']);
    items.push(Object.keys(d.fc).length ? ['ok', 'Forecast', 'issued ' + hm(d.issued) + ' IST for ' + Object.keys(d.fc).length + ' sites'] : ['warn', 'Forecast', 'none for this day']);
    items.push(d.plans.P2 ? ['ok', 'Planner', assigns(d, 'P2').length + ' crews scheduled'] : ['warn', 'Planner', 'no plan']);
    items.push(S.verified == null ? ['wait', 'Claims ledger', 'checking…'] : S.verified.ok ? ['ok', 'Claims ledger', S.verified.checked + ' records intact'] : ['bad', 'Claims ledger', 'tampering detected']);
    $('#pipeline').innerHTML = items.map(function (x) { return '<li class="' + x[0] + '"><b>' + esc(x[1]) + '</b> ' + esc(x[2]) + '</li>'; }).join('');
  }

  /* ------------------------------------------------------------ actions -- */
  function stKey() { return 'nullahnet-actions:' + (S.B.generated_at || ''); }
  function loadState() { try { S.st = JSON.parse(localStorage.getItem(stKey()) || '{}') || {}; } catch (e) { S.st = {}; } }
  function saveState() { try { localStorage.setItem(stKey(), JSON.stringify(S.st)); } catch (e) { /* private mode */ } }

  function buildActions() {
    var d = today(), out = [], p2 = d.plans.P2;
    assigns(d, 'P2').slice().sort(function (a, b) { return ms(a.start) - ms(b.start); }).forEach(function (a) {
      var f = fc(d, a.site_id), dr = drv(f);
      out.push({ id: 'dispatch|' + p2.plan_id + '|' + a.crew_id + '|' + a.site_id, kind: 'dispatch', site: a.site_id, a: a, f: f,
        title: 'Send ' + crew(a.crew_id) + ' to ' + short(a.site_id), when: hm(a.start) + '–' + hm(a.end) + ' IST',
        facts: ['about ' + kg(a.expected_cleared_kg) + ' to clear', dr.sensed_fill != null ? 'boom ' + pct(dr.sensed_fill) + ' full' : null,
          f ? pct(risk(f)) + ' overflow risk in 24 h' : null, dr.rain_mm_next_24h_fc != null ? mm(dr.rain_mm_next_24h_fc) + ' rain in 24 h' : null].filter(Boolean) });
    });
    // sites with a crew already planned carry their risk on the dispatch row; watch rows are for uncovered sites
    X.sites.slice().sort(function (p, q) { return risk(fc(d, q.site_id)) - risk(fc(d, p.site_id)); }).forEach(function (s) {
      var f = fc(d, s.site_id), f48 = fc(d, s.site_id, 48), dr = drv(f);
      if (!f || assigns(d, 'P2', s.site_id).length || (level(f) === 'low' && level(f48) === 'low')) return;
      out.push({ id: 'watch|' + d.key + '|' + s.site_id, kind: 'watch', site: s.site_id, f: f, f48: f48,
        title: short(s.site_id) + ': ' + pct(risk(f)) + ' overflow risk in 24 h' + (f48 ? ', ' + pct(risk(f48)) + ' in 48 h' : '') + ', no crew planned',
        facts: [mm(dr.rain_mm_next_24h_fc) + ' rain forecast', 'tide up to ' + metres(dr.max_tide_m_next_24h), 'boom ' + pct(dr.sensed_fill) + ' full'] });
    });
    var at = attention();
    if (at.length) {
      var tp = at.filter(function (e) { return S.bad.has(e.seq); }).length;
      var rj = at.filter(function (e) { return !S.bad.has(e.seq) && e.reconciliation.flag === 'reject'; }).length, rv = at.length - tp - rj;
      out.push({ id: 'review|' + d.key + '|' + at.length + '|' + tp, kind: 'review', title: 'Check ' + at.length + ' clearance claim' + (at.length > 1 ? 's' : '') + ' before payment', when: '',
        facts: [tp ? tp + ' changed after signing' : null, rj ? rj + ' over the reject threshold' : null, rv ? rv + ' to review' : null].filter(Boolean) });
    }
    return out;
  }

  function whyHTML(x) {
    var d = today(), li = [];
    if (x.kind === 'dispatch') {
      var dr = drv(x.f);
      li.push('Inputs at ' + hm(d.issued) + ' IST: boom ' + pct(dr.sensed_fill) + ' full <span class="tag">SIMULATED sensor</span>, ' + mm(dr.rain_mm_next_24h_fc) + ' of rain forecast for 24 h (archived JMA GSM run), tide up to ' + metres(dr.max_tide_m_next_24h) + ' above mean sea level (harmonic model), overflow risk ' + pct(risk(x.f)) + '.');
      if (x.a.reason) li.push('Planner note: <code>' + esc(x.a.reason) + '</code>');
      ['P1', 'P0'].forEach(function (p) {
        var alt = assigns(d, p).filter(function (a) { return a.crew_id === x.a.crew_id; })[0];
        if (alt) li.push(POLICY[p] + ' (' + p + ') would send ' + crew(alt.crew_id) + ' to ' + esc(short(alt.site_id)) + ' ' + hm(alt.start) + '–' + hm(alt.end) + ' (about ' + kg(alt.expected_cleared_kg) + ').');
      });
      li.push(evidence());
      li.push('<details><summary>Crew message (' + (S.l2 === 'none' ? 'English' : S.l2 === 'mr' ? 'Marathi, draft' : 'Hindi, draft') + ')</summary><pre>' + esc(crewMsg(x.a)) + '</pre></details>');
    } else if (x.kind === 'watch') {
      var w = drv(x.f), w48 = drv(x.f48);
      li.push('Shown because the 24 h or 48 h overflow or bypass risk is at least ' + pct(WATCH) + '. That threshold is a display choice, not a calibrated alarm level.');
      li.push('Inputs: ' + mm(w.rain_mm_next_24h_fc) + ' of rain in 24 h' + (w48.rain_mm_next_48h_fc != null ? ' and ' + mm(w48.rain_mm_next_48h_fc) + ' in 48 h' : '') + ' (archived JMA GSM runs), tide up to ' + metres(w.max_tide_m_next_24h) + ', boom ' + pct(w.sensed_fill) + ' full <span class="tag">SIMULATED sensor</span>.');
      li.push('Risk model: the twin\'s forecaster with nominal parameters <span class="tag">SIMULATED</span>. Bypass risk: ' + pct(w.p_bypass_24h) + ' in 24 h.');
      var c = assigns(d, 'P2', x.site);
      li.push(c.length ? 'Already covered: ' + c.map(function (a) { return crew(a.crew_id) + ' ' + hm(a.start) + '–' + hm(a.end); }).join(', ') + '.' : 'No crew is planned here today. Consider moving one if the risk rises at the next forecast.');
    } else {
      var z = (S.A.reconcile_z_review || [])[0];
      li.push('The checker compares each claimed weight with what the boom sensors and inflow counts can support (dry-equivalent kg with ASSUMED density and moisture).' + (z ? ' Review above z = ' + num(z, 2) + ', calibrated on separate SYNTHETIC trips.' : ''));
      li.push('A flag means "get a second check" (weighbridge slip, photos), not proof of fraud. Errors in debris density raise false flags.');
      li.push('All claims on this page are SYNTHETIC, generated to test the checker.');
    }
    return '<ul><li>' + li.join('</li><li>') + '</li></ul>';
  }
  function evidence() {
    var m = X.dm;
    if (m.P2_reduction_vs_P0_median == null) return 'No simulation evidence in this bundle.';
    return 'Evidence <span class="tag">SIMULATED</span>: in held-out runs (' + esc(String(m.heldout || '').replace(/\s*\(.*\)$/, '')) + ') the tide-aware plan let a median <b>' + rel(m.P2_reduction_vs_P0_median) + '</b> plastic escape than the assumed fixed roster with the same crew-hours (central 90% of ' + num(m.n_draws) + ' parameter draws: ' + rel(m.P2_reduction_vs_P0_p05) + ' to ' + rel(m.P2_reduction_vs_P0_p95) + '). Not field-tested.';
  }
  function crewMsg(a) {
    var L = CREW_MSG[S.l2] ? S.l2 : 'en';
    return CREW_MSG[L]({ date: dlabel(a.start), crew: crew(a.crew_id), site: (X.site[a.site_id] || {}).name || a.site_id, start: hm(a.start), end: hm(a.end), kg: num(Math.round((a.expected_cleared_kg || 0) / 10) * 10) });
  }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text).then(function () { return true; }, function () { return legacyCopy(text); });
    return Promise.resolve(legacyCopy(text));
  }
  function legacyCopy(text) {
    var t = document.createElement('textarea'); t.value = text; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.opacity = '0';
    document.body.appendChild(t); t.select(); var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(t); return ok;
  }

  function actHTML(x) {
    var done = !!S.st[x.id], b = [];
    if (x.kind === 'dispatch' && !done) b.push('<button type="button" class="btn primary" data-do="copy">Copy crew message</button>');
    if (x.kind === 'watch') b.push('<button type="button" class="btn" data-do="show">Show site</button>');
    if (x.kind === 'review') b.push('<button type="button" class="btn" data-do="claims">Open claims</button>');
    b.push(done ? '<button type="button" class="btn" data-do="undo">Undo</button>' : '<button type="button" class="btn" data-do="done">' + (x.kind === 'dispatch' ? 'Mark sent' : 'Acknowledge') + '</button>');
    return '<li class="act" data-id="' + esc(x.id) + '"><div class="actrow">' +
      '<span class="badge b-' + x.kind + '">' + KIND[x.kind] + '</span>' +
      '<div><p class="acttitle">' + esc(x.title) + (x.when ? ' <span class="when">' + esc(x.when) + '</span>' : '') + '</p>' +
      '<p class="actfacts">' + x.facts.map(esc).join(' · ') + '</p></div>' +
      '<div class="actbtns">' + b.join('') + '</div>' +
      '<details class="why"><summary>Why?</summary>' + whyHTML(x) + '</details></div></li>';
  }
  function renderActions() {
    var acts = buildActions(), open = [], done = [];
    S.acts = {};
    acts.forEach(function (a) { S.acts[a.id] = a; (S.st[a.id] ? done : open).push(a); });
    $('#actcount').textContent = acts.length ? (open.length ? open.length + ' open' : 'all done') + (done.length ? ' · ' + done.length + ' done' : '') : '';
    $('#actionlist').innerHTML = open.map(actHTML).join('');
    var calm = $('#calm'), d = today(), anyWatch = acts.some(function (a) { return a.kind === 'watch'; });
    var anyRisky = X.sites.some(function (s) { return level(fc(d, s.site_id)) !== 'low' || level(fc(d, s.site_id, 48)) !== 'low'; });
    calm.hidden = anyWatch;
    calm.textContent = anyRisky ? 'Every site at ' + pct(WATCH) + ' or more overflow or bypass risk in the next 48 h already has a crew planned.' : 'No site is at ' + pct(WATCH) + ' or more overflow or bypass risk in the next 48 h.';
    $('#donebox').hidden = !done.length; $('#donesum').textContent = 'Done (' + done.length + ')';
    $('#donelist').innerHTML = done.map(actHTML).join('');
  }
  function onAction(e) {
    var b = e.target.closest('[data-do]'); if (!b) return;
    var li = b.closest('.act'), id = li && li.dataset.id, x = S.acts[id]; if (!x) return;
    var what = b.dataset.do;
    if (what === 'copy') copyText(crewMsg(x.a)).then(function (ok) { toast(ok ? 'Crew message copied: paste it into WhatsApp or SMS.' : 'Copy failed: open "Why?" to see the message.'); });
    else if (what === 'show') selectSite(x.site, true);
    else if (what === 'claims') $('#records').scrollIntoView({ behavior: 'smooth', block: 'start' });
    else if (what === 'done') { S.st[id] = Date.now(); saveState(); renderActions(); }
    else if (what === 'undo') { delete S.st[id]; saveState(); renderActions(); }
  }

  /* -------------------------------------------------------------- sites -- */
  function renderSites() {
    var d = today();
    $('#sitelist').innerHTML = X.sites.map(function (s) {
      var f = fc(d, s.site_id), as = assigns(d, 'P2', s.site_id);
      return '<li><button type="button" class="site" data-site="' + esc(s.site_id) + '" aria-pressed="' + (s.site_id === S.site) + '">' +
        '<span class="dot lv-' + level(f) + '"></span><span class="sname">' + esc(short(s.site_id)) + '</span>' +
        '<span class="smeta">risk ' + pct(risk(f)) + ' · boom ' + pct(drv(f).sensed_fill) + ' full · ' +
        (as.length ? as.map(function (a) { return crew(a.crew_id) + ' at ' + hm(a.start); }).join(', ') : 'no crew') + '</span></button></li>';
    }).join('');
    renderMap();
  }
  function renderMap() {
    if (typeof L === 'undefined') { $('#map').hidden = true; return; }
    var d = today();
    if (!S.map) {
      S.map = L.map('map', { scrollWheelZoom: false });
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap contributors' }).addTo(S.map);
      var pts = [];
      X.sites.forEach(function (s) {
        var m = L.circleMarker([s.lat, s.lon], { radius: 8, weight: 2, color: '#fff', fillOpacity: 1 }).addTo(S.map);
        m.on('click', function () { selectSite(s.site_id, false); });
        m.bindTooltip(short(s.site_id));
        S.markers[s.site_id] = m; pts.push([s.lat, s.lon]);
      });
      if (pts.length) S.map.fitBounds(pts, { padding: [28, 28] });
    }
    X.sites.forEach(function (s) {
      var on = s.site_id === S.site, m = S.markers[s.site_id];
      m.setStyle({ fillColor: LV[level(fc(d, s.site_id))], radius: on ? 11 : 8, color: on ? '#152028' : '#fff', weight: on ? 3 : 2 });
      if (on) m.bringToFront();
    });
  }
  function selectSite(sid, scroll) {
    S.site = sid; renderSites(); renderDetail();
    if (scroll) $('#detail').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ------------------------------------------------------------- detail -- */
  function renderDetail() {
    var d = today(), s = X.site[S.site] || {}, f = fc(d, S.site), f48 = fc(d, S.site, 48), dr = drv(f), as = assigns(d, 'P2', S.site);
    $('#h-detail').textContent = s.name || S.site || 'Site';
    var facts = [['Overflow risk', pct(risk(f)) + ' in 24 h' + (f48 ? ', ' + pct(risk(f48)) + ' in 48 h' : '')], ['Boom', pct(dr.sensed_fill) + ' full (sim.)'],
      ['Rain forecast', mm(dr.rain_mm_next_24h_fc) + ' in 24 h'], ['Tide up to', metres(dr.max_tide_m_next_24h)],
      ['Crew', as.length ? as.map(function (a) { return crew(a.crew_id) + ' ' + hm(a.start) + '–' + hm(a.end); }).join(', ') : 'none planned']];
    $('#facts').innerHTML = facts.map(function (x) { return '<div><dt>' + esc(x[0]) + '</dt><dd>' + esc(x[1]) + '</dd></div>'; }).join('');
    drawChart();
    $('#chartnote').textContent = 'Black line: when the plan was issued. Hours to its right are shown only because this is a replay; the planner could not see them. Blue band: the crew\'s planned time on site. Hatched rows are SIMULATED; in the fill row the area is the sensor reading and the dark line is the twin\'s true fill.';
  }
  function nearest(a, v) { var b = -1, bd = Infinity; for (var i = 0; i < a.length; i++) { var dd = Math.abs(a[i] - v); if (dd < bd) { bd = dd; b = i; } } return b; }
  function tick(v) { return Math.abs(v) >= 10 ? num(v) : num(v, 1); }
  function seriesFor(sid) {
    var F = X.forcing[sid], I = X.inter[sid], T = X.telem[sid] || [];
    if (!F || !F.t || !F.t.length) return null;
    return {
      t: F.t.map(ms), rain: F.rain_mm_h, tide: F.tide_m,
      it: I ? I.t.map(ms) : [], truth: I ? I.fill_fraction.map(function (v) { return v * 100; }) : [],
      esc: I ? I.t.map(function (_, i) { return (I.escaped_entrainment_kg[i] || 0) + (I.escaped_overtopping_kg[i] || 0) + (I.escaped_bypass_kg[i] || 0); }) : [],
      st: T.filter(function (m) { return m.fill && m.fill.fill_fraction != null; }).map(function (m) { return ms(m.t); }),
      sensed: T.filter(function (m) { return m.fill && m.fill.fill_fraction != null; }).map(function (m) { return m.fill.fill_fraction * 100; })
    };
  }
  function drawChart() {
    var box = $('#chart'), sid = S.site, z = seriesFor(sid), d = today();
    if (!z) { box.innerHTML = '<p class="empty">No rain or tide series for this site.</p>'; return; }
    var W = Math.max(300, Math.floor(box.clientWidth || 800)), narrow = W < 600;
    var L0 = narrow ? 34 : 44, R0 = 8, PW = W - L0 - R0;
    var t0 = z.t[0], t1 = z.t[z.t.length - 1];
    var XS = function (v) { return L0 + PW * (v - t0) / ((t1 - t0) || 1); };
    var rows = [
      { label: narrow ? 'Rain mm/h' : 'Rain, mm/h', src: narrow ? 'ERA5' : 'ERA5 reanalysis', t: z.t, v: z.rain, kind: 'bar', cls: 'c-rain', lo: 0 },
      { label: narrow ? 'Tide m' : 'Tide, m vs mean sea level', src: narrow ? 'harmonic' : 'harmonic model', t: z.t, v: z.tide, kind: 'line', cls: 'c-tide' },
      { label: narrow ? 'Boom fill %' : 'Boom fill, %', src: 'SIMULATED', t: z.st.length ? z.st : z.it, v: z.st.length ? z.sensed : z.truth, kind: 'area', cls: 'c-fill', lo: 0, hi: 100, sim: true, line: z.st.length ? { t: z.it, v: z.truth } : null },
      { label: narrow ? 'Escaping kg/h' : 'Plastic escaping the boom, kg/h', src: 'SIMULATED', t: z.it, v: z.esc, kind: 'bar', cls: 'c-esc', lo: 0, sim: true }
    ];
    var H = narrow ? 50 : 58, LAB = 18, GAP = 12, y = 4, out = [];
    out.push('<defs><pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3" height="7" fill="rgba(86,100,110,.10)"/></pattern></defs>');
    rows.forEach(function (r) {
      if (!r.v || !r.v.length) return;
      var vals = r.v.filter(function (v) { return v != null && !isNaN(v); });
      var lo = r.lo != null ? r.lo : Math.min.apply(null, vals), hi = r.hi != null ? r.hi : Math.max.apply(null, vals);
      if (hi - lo < 1e-9) hi = lo + 1;
      var top = y + LAB, bot = top + H, Y = function (v) { return bot - (bot - top) * (Math.max(lo, Math.min(hi, v)) - lo) / (hi - lo); };
      out.push('<text class="rowlabel" x="' + L0 + '" y="' + (y + 11) + '">' + esc(r.label) + '</text><text class="' + (r.sim ? 'simtag' : '') + '" x="' + (W - R0) + '" y="' + (y + 11) + '" text-anchor="end">' + esc(r.src) + '</text>');
      if (r.sim) out.push('<rect x="' + L0 + '" y="' + top + '" width="' + PW + '" height="' + H + '" fill="url(#hatch)"/>');
      out.push('<line class="grid" x1="' + L0 + '" x2="' + (W - R0) + '" y1="' + bot + '" y2="' + bot + '"/>');
      out.push('<text x="' + (L0 - 5) + '" y="' + (top + 9) + '" text-anchor="end">' + tick(hi) + '</text><text x="' + (L0 - 5) + '" y="' + bot + '" text-anchor="end">' + tick(lo) + '</text>');
      if (lo < 0 && hi > 0) out.push('<line class="zero" x1="' + L0 + '" x2="' + (W - R0) + '" y1="' + Y(0).toFixed(1) + '" y2="' + Y(0).toFixed(1) + '"/>');
      var inWin = function (t) { return t >= t0 && t <= t1; };
      if (r.kind === 'bar') {
        var bw = Math.max(1, PW / Math.max(1, r.t.length) * 0.8);
        out.push('<g class="' + r.cls + '">' + r.t.map(function (t, i) { var v = r.v[i]; if (!v || !inWin(t)) return ''; var yy = Y(v); return '<rect x="' + (XS(t) - bw / 2).toFixed(1) + '" y="' + yy.toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + Math.max(0.5, bot - yy).toFixed(1) + '"/>'; }).join('') + '</g>');
      } else {
        var idx = r.t.map(function (t, i) { return i; }).filter(function (i) { return inWin(r.t[i]) && r.v[i] != null; });
        var pts = idx.map(function (i) { return XS(r.t[i]).toFixed(1) + ',' + Y(r.v[i]).toFixed(1); });
        if (pts.length && r.kind === 'area') out.push('<path class="' + r.cls + '" d="M' + XS(r.t[idx[0]]).toFixed(1) + ',' + bot + ' L' + pts.join(' L') + ' L' + XS(r.t[idx[idx.length - 1]]).toFixed(1) + ',' + bot + ' Z"/>');
        else if (pts.length) out.push('<polyline class="' + r.cls + '" points="' + pts.join(' ') + '"/>');
        if (r.line) out.push('<polyline fill="none" stroke="#152028" stroke-width="1.2" points="' + r.line.t.map(function (t, i) { return inWin(t) ? XS(t).toFixed(1) + ',' + Y(r.line.v[i]).toFixed(1) : null; }).filter(Boolean).join(' ') + '"/>');
      }
      y = bot + GAP;
    });
    var pTop = 4 + LAB, pBot = y - GAP;
    assigns(d, 'P2', sid).forEach(function (a) {
      var a0 = Math.max(t0, ms(a.start)), a1 = Math.min(t1, ms(a.end));
      if (a1 > a0) out.push('<rect class="crewband" x="' + XS(a0).toFixed(1) + '" y="' + pTop + '" width="' + (XS(a1) - XS(a0)).toFixed(1) + '" height="' + (pBot - pTop) + '"><title>' + esc(crew(a.crew_id)) + ' on site (plan)</title></rect>');
    });
    for (var dt = Math.ceil((t0 + IST_MS) / DAY_MS) * DAY_MS - IST_MS; dt <= t1; dt += DAY_MS) {
      out.push('<line class="grid" x1="' + XS(dt).toFixed(1) + '" x2="' + XS(dt).toFixed(1) + '" y1="' + pTop + '" y2="' + pBot + '"/>');
      if (XS(dt) + (narrow ? 44 : 72) < W) out.push('<text x="' + (XS(dt) + 3).toFixed(1) + '" y="' + (pBot + 14) + '">' + esc(narrow ? String(ist(dt).getUTCDate()) + ' ' + MO[ist(dt).getUTCMonth()] : dlabel(dt)) + '</text>');
    }
    var now = ms(d.issued);
    if (now >= t0 && now <= t1) {
      out.push('<rect class="after" x="' + XS(now).toFixed(1) + '" y="' + pTop + '" width="' + (XS(t1) - XS(now)).toFixed(1) + '" height="' + (pBot - pTop) + '"/>');
      out.push('<line class="nowline" x1="' + XS(now).toFixed(1) + '" x2="' + XS(now).toFixed(1) + '" y1="' + (pTop - 4) + '" y2="' + pBot + '"/>');
    }
    out.push('<line id="hovline" class="hoverline" x1="0" x2="0" y1="' + pTop + '" y2="' + pBot + '" visibility="hidden"/>');
    var Ht = pBot + 22;
    box.innerHTML = '<svg viewBox="0 0 ' + W + ' ' + Ht + '" width="' + W + '" height="' + Ht + '" role="img" aria-label="' + esc('Rain, tide, boom fill and escaping plastic at ' + short(sid) + ' over the replay week') + '">' + out.join('') + '</svg><div class="tip" id="tip" hidden></div>';
    var svg = box.querySelector('svg'), tip = $('#tip'), hl = $('#hovline');
    function hide() { tip.hidden = true; hl.setAttribute('visibility', 'hidden'); }
    function move(ev) {
      var rc = svg.getBoundingClientRect(), x = (ev.clientX - rc.left) * (W / rc.width), t = t0 + (x - L0) / PW * (t1 - t0);
      if (t < t0 || t > t1) return hide();
      var i = nearest(z.t, t), j = nearest(z.it, t), k = nearest(z.st, t), xx = XS(z.t[i]);
      hl.setAttribute('x1', xx); hl.setAttribute('x2', xx); hl.setAttribute('visibility', 'visible');
      tip.innerHTML = '<b>' + esc(dlabel(z.t[i]) + ' ' + hm(z.t[i])) + ' IST</b><br>Rain ' + num(z.rain[i], 1) + ' mm/h · tide ' + num(z.tide[i], 2) + ' m' +
        (j >= 0 ? '<br>Boom ' + (k >= 0 ? num(z.sensed[k]) + '% (sensor) · ' : '') + num(z.truth[j]) + '% (twin) · escaping ' + num(z.esc[j], 1) + ' kg/h (sim.)' : '');
      tip.hidden = false;
      var px = xx * (rc.width / W), half = tip.offsetWidth / 2 + 4;
      tip.style.left = Math.min(Math.max(px, half), rc.width - half) + 'px';
    }
    svg.addEventListener('mousemove', move); svg.addEventListener('mouseleave', hide);
    svg.addEventListener('touchstart', function (ev) { if (ev.touches[0]) move(ev.touches[0]); }, { passive: true });
  }

  /* ------------------------------------------------------------- claims -- */
  function recWhen(e) { return dlabel(e.record.t_start) + ', ' + hm(e.record.t_start) + '–' + hm(e.record.t_end) + ' IST'; }
  function recHTML(e) {
    var r = e.reconciliation, rec = e.record, bad = S.bad.has(e.seq), fl = bad ? 'tampered' : r.flag;
    var label = { tampered: 'Changed after signing', reject: 'Reject', review: 'Review', ok: 'OK' }[fl] || fl;
    var share = r.claimed_kg > 0 ? Math.max(0, Math.min(1, r.sensor_estimated_kg / r.claimed_kg)) : 1;
    var orig = bad ? S.original.filter(function (o) { return o.seq === e.seq; })[0] : null;
    var body = orig && orig.record.claimed_wet_kg !== rec.claimed_wet_kg
      ? '<p class="recline">The claimed weight now reads <b>' + kg(rec.claimed_wet_kg) + '</b> wet, but the signed record says <b>' + kg(orig.record.claimed_wet_kg) + '</b>. The record no longer matches its hash, so the edit is caught.</p>'
      : '<p class="recline">Claimed <b>' + kg(rec.claimed_wet_kg) + '</b> wet (about ' + kg(r.claimed_kg) + ' dry); sensors support about <b>' + kg(r.sensor_estimated_kg) + '</b> dry, so the claim is <b>' + num(r.ratio, 1) + '×</b> the evidence.</p>' +
        '<div class="bar" aria-hidden="true"><span style="width:' + (share * 100).toFixed(1) + '%"></span></div><div class="barlabels"><span>supported by sensors</span><span>claimed</span></div>';
    return '<li class="rec' + (bad ? ' tampered' : '') + '"><div class="rechead"><span class="badge f-' + fl + '">' + esc(label) + '</span>' +
      '<span class="recwho">' + esc(short(rec.site_id)) + ' · ' + esc(crew(rec.crew_id)) + '</span><span class="recwhen">' + esc(recWhen(e)) + ' · #' + e.seq + '</span></div>' + body +
      '<details><summary>Checker reasons</summary><ul>' + (r.reasons || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') +
      '<li>record hash <span class="hash">' + esc(String(e.hash).slice(0, 16)) + '…</span></li></ul></details></li>';
  }
  function tableHTML(list) {
    return '<table><thead><tr><th>#</th><th>Start (IST)</th><th>Site</th><th>Crew</th><th class="num">Claimed wet kg</th><th class="num">Supported dry kg</th><th class="num">Ratio</th><th>Check</th><th>Hash</th></tr></thead><tbody>' +
      list.map(function (e) {
        var r = e.reconciliation, bad = S.bad.has(e.seq);
        return '<tr' + (bad ? ' class="badrow"' : '') + '><td>' + e.seq + '</td><td>' + esc(dlabel(e.record.t_start) + ' ' + hm(e.record.t_start)) + '</td><td>' + esc(short(e.record.site_id)) + '</td><td>' + esc(crew(e.record.crew_id)) +
          '</td><td class="num">' + num(e.record.claimed_wet_kg) + '</td><td class="num">' + num(r.sensor_estimated_kg) + '</td><td class="num">' + num(r.ratio, 2) + '</td><td>' + (bad ? 'changed' : esc(r.flag)) + '</td><td class="hash">' + esc(String(e.hash).slice(0, 10)) + '…</td></tr>';
      }).join('') + '</tbody></table>';
  }
  function renderRecords() {
    var all = S.entries, seen = all.filter(asOf), at = attention().sort(function (a, b) { return sev(b) - sev(a) || ms(b.record.t_start) - ms(a.record.t_start); });
    $('#reccount').textContent = at.length + ' of ' + seen.length + ' need attention';
    $('#recintro').innerHTML = '<span class="tag">SYNTHETIC</span> ' + seen.length + ' claims ' + (seen.length ? 'from ' + esc(dlabel(seen[0].record.t_start)) + ' to ' + esc(dlabel(seen[seen.length - 1].record.t_end, true)) : '') +
      ', up to the end of the replay day: honest trips plus injected inflated and phantom ones, to test the checker. "Supported" kg uses ASSUMED debris density and moisture until weighed samples calibrate them.';
    $('#reclist').innerHTML = at.map(recHTML).join('') || '<li class="empty">No claims need attention.</li>';
    $('#allrec').textContent = S.all ? 'Hide the full table' : 'Show all ' + all.length + ' records in the ledger';
    $('#allrec').setAttribute('aria-expanded', String(S.all));
    $('#alltable').hidden = !S.all;
    if (S.all) $('#alltable').innerHTML = tableHTML(all);
    var a = S.A.anchor;
    $('#anchorline').innerHTML = a ? 'Published anchor: ' + a.length + ' records, head hash <span class="hash">' + esc(String(a.head_hash).slice(0, 16)) + '…</span>. Each record is hashed (SHA-256 over canonical JSON) into a chain and signed by its crew (Ed25519); this page re-checks both.' : 'No published anchor in this bundle, so deleting the newest records cannot be detected.';
  }
  async function verify() {
    var st = $('#verifystatus');
    st.className = 'status'; st.textContent = 'Checking ' + S.entries.length + ' records…';
    var t0 = performance.now();
    var r = await LedgerVerify.verifyChain(S.entries, S.A.anchor);
    var sg = await LedgerVerify.verifySignatures(S.entries, S.A.signatures || [], S.A.key_registry || {}, S.A.delegations || {});
    var took = Math.round(performance.now() - t0);
    S.bad = new Set(r.badSeqs || []);
    if (sg.supported && sg.badSeqs) sg.badSeqs.forEach(function (q) { S.bad.add(q); });
    var sigOk = !sg.supported || sg.ok;
    S.verified = { ok: r.ok && sigOk, checked: r.checked };
    var sigTxt = sg.supported ? 'crew signatures ' + (sg.checked - sg.badSeqs.length) + '/' + sg.checked + ' valid' : 'signature check needs a newer browser';
    if (r.ok && sigOk) { st.className = 'status ok'; st.textContent = '✓ All ' + r.checked + ' records intact and matching the published anchor · ' + sigTxt + ' · checked in this browser in ' + took + ' ms'; }
    else {
      var p = (r.problems || []).concat(sg.problems || []);
      st.className = 'status bad'; st.textContent = '✗ Tampering detected: ' + (p[0] || 'signature mismatch') + (p.length > 1 ? ' (+' + (p.length - 1) + ' more)' : '') + ' · ' + sigTxt;
    }
    renderRecords(); renderActions(); renderBrief(); renderPipeline();
  }
  function tamper() {
    var i = Math.min(S.entries.length - 1, 3);
    var e = JSON.parse(JSON.stringify(S.entries[i]));
    e.record.claimed_wet_kg = Math.round(e.record.claimed_wet_kg * 1.25 * 10) / 10;
    S.entries = S.entries.slice(); S.entries[i] = e;
    $('#reset').disabled = false;
    toast('Record #' + e.seq + ': claimed weight raised 25% in this browser only. Re-checking…');
    verify();
  }
  function reset() { S.entries = S.original.slice(); $('#reset').disabled = true; verify(); }

  /* -------------------------------------------------------------- plans -- */
  function renderPlans() {
    var d = today(), order = ['P2', 'P1', 'P0'].filter(function (p) { return d.plans[p]; });
    $('#plancols').innerHTML = order.map(function (p) {
      var as = assigns(d, p).slice().sort(function (a, b) { return ms(a.start) - ms(b.start); });
      return '<div class="plancol"><h3>' + esc(POLICY[p] || p) + ' <span class="count">' + p + '</span>' + (p === 'P2' ? ' <span class="rec-tag">recommended</span>' : '') + '</h3><ul>' +
        as.map(function (a) { return '<li>' + esc(crew(a.crew_id)) + ' → ' + esc(short(a.site_id)) + ' <span class="when">' + hm(a.start) + '–' + hm(a.end) + '</span></li>'; }).join('') +
        '</ul><p class="tot">about ' + kg(sum(as, function (a) { return a.expected_cleared_kg; })) + ' to clear (SIMULATED)</p></div>';
    }).join('') || '<p class="empty">No plans for this day.</p>';
    var m = X.dm, P = ['P2', 'P1', 'P0'];
    $('#planevidence').innerHTML = m.P0_escaped_kg_median == null ? '' :
      'Held-out simulation <span class="tag">SIMULATED</span>, ' + esc(String(m.heldout || '').replace(/\s*\(.*\)$/, '')) + ', ' + num(m.n_draws) + ' parameter draws, equal crew-hours. Median plastic escaping: ' +
      P.map(function (p) { return p + ' ' + kg(m[p + '_escaped_kg_median']); }).join(', ') + '. Share of arriving plastic captured: ' + P.map(function (p) { return p + ' ' + pct(m[p + '_captured_fraction_median']); }).join(', ') + '.' +
      '<details><summary>Reproduce</summary><pre>' + esc(m.reproduce || '') + '</pre></details>';
  }

  /* ---------------------------------------------------------- detection -- */
  function renderDetection() {
    var m = (S.B.metrics || {}).detection, smp = S.A.detection_samples || [];
    if (!m) { $('#detbody').innerHTML = '<p class="empty">No detector results in this bundle yet.</p>'; return; }
    var kv = [['Held-out test mAP50', num(m.mAP50, 2) + ' (' + num(m.n_test_images) + ' images)'], ['Precision / recall', num(m.precision, 2) + ' / ' + num(m.recall, 2)]];
    if (m['other_splits.groningen.mAP50'] != null) kv.push(['Another site (Groningen)', 'mAP50 ' + num(m['other_splits.groningen.mAP50'], 2)]);
    var html = '<p>A YOLO11n model finds floating litter in camera frames. Its counts are evidence for boom fill and inflow; when the camera cannot see, fill is reported as unknown.</p>' +
      '<dl class="kpis">' + kv.map(function (x) { return '<div><dt>' + esc(x[0]) + '</dt><dd>' + esc(x[1]) + '</dd></div>'; }).join('') + '</dl>' +
      '<p class="note">Frames from the public TUD-GV dataset (CC BY 4.0), not Mumbai cameras. Accuracy drops at a second site, so a Mumbai pilot needs locally labelled images first.</p>';
    if (smp.length) {
      html += '<div class="detgrid">' + smp.map(function (f) {
        var wh = f.image_wh || [1, 1], boxes = (f.detections || []).map(function (q) { var b = q.bbox_xyxy; return '<rect x="' + b[0] + '" y="' + b[1] + '" width="' + (b[2] - b[0]) + '" height="' + (b[3] - b[1]) + '" fill="none" stroke="#f2b705" stroke-width="' + Math.max(3, wh[0] / 180) + '"/>'; }).join('');
        return '<figure><img src="' + esc(f.image) + '" alt="Public dataset frame ' + esc(f.frame_id) + ' with detected litter boxed" loading="lazy"><svg viewBox="0 0 ' + wh[0] + ' ' + wh[1] + '" preserveAspectRatio="none" aria-hidden="true">' + boxes + '</svg><figcaption>' + (f.detections || []).length + ' detections · ' + esc(String(f.frame_id).split('/').pop()) + '</figcaption></figure>';
      }).join('') + '</div>';
    }
    if (m.reproduce) html += '<details><summary class="note">Reproduce</summary><pre>' + esc(m.reproduce) + '</pre></details>';
    $('#detbody').innerHTML = html;
  }

  /* ------------------------------------------------------------ sources -- */
  function prov(p) { return p ? (p.source || '') + (p.retrieved_at ? ' (retrieved ' + String(p.retrieved_at).slice(0, 10) + ')' : '') : '—'; }
  function col(title, items) { return '<div><h3>' + esc(title) + '</h3><ul>' + items.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul></div>'; }
  function renderSources() {
    var B = S.B, F = (B.forcing || [])[0] || {}, f0 = (B.forecasts || [])[0] || {}, fm = (B.metrics || {})['twin_sim.forcing'] || {}, w = (B.metrics || {})['twin_sim.window'] || {};
    var ve = Object.keys(fm).filter(function (k) { return /^tide_fit_var_expl_/.test(k); }).map(function (k) { return fm[k]; });
    var real = ['Rain, hourly: ' + esc(prov(F.rain_provenance)),
      'Tide: ' + esc(prov(F.tide_provenance)) + (ve.length ? '. The fit explains ' + num(Math.min.apply(null, ve) * 100, 1) + '–' + num(Math.max.apply(null, ve) * 100, 1) + '% of sea-level variance in its fitting period.' : ''),
      'Forecast inputs: ' + esc(prov(f0.provenance)),
      'Site coordinates: OpenStreetMap (ODbL). Catchment figures are ASSUMPTIONS (research/components/twin.md).'];
    if (w.selection) real.push('Replay week: ' + esc(w.selection) + (w.rain_mm_7d_mean_of_4_sites != null ? ', ' + mm(w.rain_mm_7d_mean_of_4_sites) + ' mean over the four sites' : '') + '.');
    var sim = ['Boom fill, plastic arrival and escape, flux counts and edge-node telemetry come from the digital twin with nominal parameters, not from field hardware.',
      'Expected kilograms in plans and crew messages are twin outputs.', 'Overflow and bypass risks come from the twin\'s forecaster fed with archived real rain forecasts.'];
    var syn = ['Clearance claims are SYNTHETIC: honest trips plus injected inflated and phantom ones. The demo signing keys come from public seeds and are for the demo only.'].concat((B.disclaimers || []).map(esc));
    $('#sourcebody').innerHTML = col('Real data', real) + col('Simulated', sim) + col('Synthetic and assumed', syn);
    $('#via').textContent = 'Bundle schema ' + (B.schema_version || '?') + ', generated ' + (B.generated_at || '?') + ' at commit ' + (B.git_sha || '?') + ', loaded from ' + S.via + '.';
  }

  /* --------------------------------------------------------------- boot -- */
  function loadScript(src) { return new Promise(function (res, rej) { var s = document.createElement('script'); s.src = src; s.onload = res; s.onerror = rej; document.head.appendChild(s); }); }
  async function load() {
    try {
      var b = await fetch('dashboard_bundle.json', { cache: 'no-cache' }); if (!b.ok) throw new Error(b.status);
      var a = await fetch('aux.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; });
      return { bundle: await b.json(), aux: a, via: 'dashboard_bundle.json + aux.json' };
    } catch (e) {
      await loadScript('data.js');
      return { bundle: window.DASHBOARD_BUNDLE, aux: window.DASHBOARD_AUX || {}, via: 'data.js (file:// fallback)' };
    }
  }
  function wire() {
    $('#dayprev').addEventListener('click', function () { step(-1); });
    $('#daynext').addEventListener('click', function () { step(1); });
    document.addEventListener('keydown', function (e) { if (/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return; if (e.key === '[') step(-1); if (e.key === ']') step(1); });
    $$('.lang button').forEach(function (b) { b.addEventListener('click', function () { setLang(b.dataset.lang); }); });
    $('#honesty').addEventListener('click', function () { var s = $('#sources'); s.open = true; s.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    $('#sitelist').addEventListener('click', function (e) { var b = e.target.closest('[data-site]'); if (b) selectSite(b.dataset.site, false); });
    $('#briefbody').addEventListener('click', function (e) {
      var a = e.target.closest('a'); if (!a) return;
      if (a.dataset.site) { e.preventDefault(); selectSite(a.dataset.site, true); }
      else if (a.dataset.goto) { e.preventDefault(); $('#' + a.dataset.goto).scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
    $('#actions').addEventListener('click', onAction);
    $('#reverify').addEventListener('click', verify); $('#tamper').addEventListener('click', tamper); $('#reset').addEventListener('click', reset);
    $('#allrec').addEventListener('click', function () { S.all = !S.all; renderRecords(); });
    var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { drawChart(); if (S.map) S.map.invalidateSize(); }, 150); });
  }
  async function boot() {
    var l2 = 'none'; try { l2 = localStorage.getItem('nullahnet-lang2') || 'none'; } catch (e) { /* private mode */ }
    var got;
    try { got = await load(); } catch (e) { $('main').innerHTML = '<p class="panel">Could not load the dashboard data: ' + esc(e) + '</p>'; return; }
    S.B = got.bundle; S.A = got.aux || {}; S.via = got.via;
    S.entries = (S.B.ledger || []).slice(); S.original = S.entries.slice();
    prep(); loadState(); wire(); setLang(l2);
    if (!X.dayKeys.length) { $('#briefbody').innerHTML = '<p>No forecasts or plans in this bundle.</p>'; return; }
    setDay(X.dayKeys[X.dayKeys.length - 1]);
    renderDetection(); renderSources();
    verify();
  }
  boot();
})();
