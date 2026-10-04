(function () {
  'use strict';
  var I18N = {
    title: { en: 'Nullah outfall plastic interception — operations', mr: 'नाला मुखावरील प्लास्टिक अडवणूक — कामकाज', hi: 'नाला निकास पर प्लास्टिक अवरोधन — संचालन' },
    map: { en: 'Outfall sites', mr: 'नाला मुख ठिकाणे', hi: 'निकास स्थल' },
    risk: { en: 'Overflow risk', mr: 'ओव्हरफ्लोचा धोका', hi: 'ओवरफ्लो जोखिम' },
    rain_tide: { en: 'Rain and tide', mr: 'पाऊस आणि भरती-ओहोटी', hi: 'बारिश और ज्वार-भाटा' },
    fill: { en: 'Boom fill and escape', mr: 'बूम भराव आणि गळती', hi: 'बूम भराव और रिसाव' },
    forecast: { en: 'Forecast', mr: 'अंदाज', hi: 'पूर्वानुमान' },
    telemetry: { en: 'Edge node', mr: 'साइटवरील यंत्र', hi: 'साइट उपकरण' },
    plan: { en: "Today's dispatch plan", mr: 'आजचे कामाचे नियोजन', hi: 'आज की कार्य योजना' },
    ledger: { en: 'Clearance evidence records', mr: 'सफाई पुरावा नोंदी', hi: 'सफाई साक्ष्य रिकॉर्ड' },
    verify: { en: 'Verify chain', mr: 'साखळी तपासा', hi: 'श्रृंखला जाँचें' },
    detection: { en: 'Floating-plastic detection', mr: 'तरंगणारे प्लास्टिक शोध', hi: 'तैरते प्लास्टिक की पहचान' },
    metrics: { en: 'Component metrics', mr: 'घटकांचे मापदंड', hi: 'घटकों के मापदंड' }
  };
  var S = { bundle: null, aux: {}, site: null, entries: [], original: [], map: null, markers: {}, open: new Set(), rows: {} };
  var $ = function (s) { return document.querySelector(s); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var TZ = 'Asia/Kolkata';
  var fDT = new Intl.DateTimeFormat('en-IN', { timeZone: TZ, weekday: 'short', day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false });
  var fHM = new Intl.DateTimeFormat('en-IN', { timeZone: TZ, hour: '2-digit', minute: '2-digit', hour12: false });
  var fDay = new Intl.DateTimeFormat('en-IN', { timeZone: TZ, weekday: 'short', day: '2-digit' });
  var ist = function (t) { return fDT.format(new Date(t)) + ' IST'; };
  var hm = function (t) { return fHM.format(new Date(t)); };
  var num = function (v, d) { d = d == null ? 1 : d; return v == null || isNaN(v) ? '—' : Number(v).toLocaleString('en-IN', { maximumFractionDigits: d, minimumFractionDigits: d }); };
  var pct = function (v) { return v == null || isNaN(v) ? '—' : Math.round(v * 100) + '%'; };
  var REAL = ['observed', 'reanalysis', 'forecast', 'harmonic_prediction'];

  function badge(kind) {
    var cls = REAL.indexOf(kind) >= 0 ? 'real' : kind === 'simulated' ? 'simulated' : kind === 'synthetic' ? 'synthetic' : kind === 'model_output' ? 'model' : 'assumption';
    return '<span class="badge ' + cls + '">' + esc(String(kind).replace(/_/g, ' ')) + '</span>';
  }
  function prov(label, p, extra) {
    if (!p) return '';
    var when = p.retrieved_at ? ' · retrieved ' + ist(p.retrieved_at) : '';
    return '<span>' + esc(label) + '</span>' + badge(p.kind) + '<span title="' + esc(p.notes) + '">' + esc(p.source) + esc(extra || '') + esc(when) + '</span>';
  }
  function riskClass(p) { return p == null ? '' : p < 0.3 ? 'risk-low' : p < 0.6 ? 'risk-med' : 'risk-high'; }
  function riskColor(p) { return p == null ? '#6b7280' : p < 0.3 ? '#1d7445' : p < 0.6 ? '#b06a00' : '#b0261d'; }
  function bySite(list, id) { return (list || []).filter(function (x) { return x.site_id === id; }); }
  function fcs(id) {
    var by = {}; bySite(S.bundle.forecasts, id).forEach(function (f) { var o = by[f.horizon_h]; if (!o || f.issued_at > o.issued_at) by[f.horizon_h] = f; });
    return Object.keys(by).map(function (k) { return by[k]; }).sort(function (a, b) { return a.horizon_h - b.horizon_h; });
  }
  function forecast(id) { return fcs(id)[0]; }

  /* ---------------------------------------------------------------- i18n -- */
  function applyLang(l2) {
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var d = I18N[el.getAttribute('data-i18n')]; if (!d) return;
      el.innerHTML = esc(d.en) + (l2 !== 'none' && d[l2] ? '<span class="l2" lang="' + l2 + '">' + esc(d[l2]) + '</span>' : '');
    });
    document.querySelectorAll('[data-i18n-btn]').forEach(function (el) {
      var d = I18N[el.getAttribute('data-i18n-btn')];
      el.textContent = d.en + (l2 !== 'none' && d[l2] ? ' · ' + d[l2] : '');
    });
    document.querySelectorAll('.lang button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.lang === l2)); });
    try { localStorage.setItem('t3-lang2', l2); } catch (e) { /* private mode */ }
  }

  /* -------------------------------------------------------------- charts -- */
  function niceMax(v) { if (!(v > 0)) return 1; var p = Math.pow(10, Math.floor(Math.log10(v))), n = v / p; return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10) * p; }
  function fmtTick(v) { return Math.abs(v) >= 100 ? Math.round(v) : Math.round(v * 10) / 10; }

  function chart(el, o) {
    var W = Math.max(300, Math.round(el.clientWidth || 600)), H = o.height || 180, m = { l: 42, r: 46, t: 24, b: 24 };
    var ts = o.t.map(function (x) { return +new Date(x); }), x0 = ts[0], x1 = ts[ts.length - 1];
    var X = function (v) { return m.l + (W - m.l - m.r) * (v - x0) / Math.max(1, x1 - x0); };
    var sc = {}, out = [], uid = 'c' + Math.random().toString(36).slice(2, 8);
    ['left', 'right'].forEach(function (ax) {
      var ls = o.layers.filter(function (l) { return l.axis === ax; }); if (!ls.length) return;
      var vals = [].concat.apply([], ls.map(function (l) { return l.values.filter(function (v) { return v != null; }); }));
      var lo = ls[0].min != null ? ls[0].min : Math.min.apply(null, vals), hi = ls[0].max != null ? ls[0].max : Math.max.apply(null, vals);
      if (ls.some(function (l) { return l.type === 'bar'; })) { lo = 0; hi = niceMax(hi); }
      else if (ls[0].min == null) { var pad = (hi - lo) * 0.1 || 0.5; lo -= pad; hi += pad; }
      sc[ax] = { lo: lo, hi: hi, Y: function (v) { return m.t + (H - m.t - m.b) * (1 - (v - lo) / ((hi - lo) || 1)); }, unit: ls[0].unit };
    });
    out.push('<svg viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="' + esc(o.aria) + '">');
    if (o.hatch) {
      out.push('<defs><pattern id="' + uid + '" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="#ffffff"/><rect width="3" height="8" fill="#f1edf9"/></pattern></defs>');
      out.push('<rect x="' + m.l + '" y="' + m.t + '" width="' + (W - m.l - m.r) + '" height="' + (H - m.t - m.b) + '" fill="url(#' + uid + ')"/>');
    }
    var now = o.now ? +new Date(o.now) : null;
    if (now && now < x1) out.push('<rect x="' + X(now) + '" y="' + m.t + '" width="' + (W - m.r - X(now)) + '" height="' + (H - m.t - m.b) + '" fill="#0a5a68" opacity="0.06"/>');
    var L = sc.left || sc.right;
    [0, 0.5, 1].forEach(function (f) {
      var v = L.lo + (L.hi - L.lo) * f, y = L.Y(v);
      out.push('<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + y + '" y2="' + y + '" stroke="#d6d3cb" stroke-width="1"/>');
      if (sc.left) out.push('<text x="' + (m.l - 6) + '" y="' + (y + 4) + '" font-size="11" text-anchor="end">' + fmtTick(v) + '</text>');
      if (sc.right) { var r = sc.right, vr = r.lo + (r.hi - r.lo) * f; out.push('<text x="' + (W - m.r + 6) + '" y="' + (r.Y(vr) + 4) + '" font-size="11">' + fmtTick(vr) + '</text>'); }
    });
    for (var t = Math.ceil(x0 / 3600000) * 3600000; t <= x1; t += 3600000) {
      if ((t + 19800000) % 86400000 === 0) {
        out.push('<line x1="' + X(t) + '" x2="' + X(t) + '" y1="' + m.t + '" y2="' + (H - m.b) + '" stroke="#e6e3dc"/>');
        out.push('<text x="' + (X(t) + 3) + '" y="' + (H - 8) + '" font-size="11">' + esc(fDay.format(new Date(t))) + '</text>');
      }
    }
    var bw = Math.max(1, (W - m.l - m.r) / ts.length - 0.6);
    o.layers.forEach(function (l) {
      var s = sc[l.axis];
      if (l.type === 'bar') {
        l.values.forEach(function (v, i) { if (v > 0) out.push('<rect x="' + (X(ts[i]) - bw / 2) + '" y="' + s.Y(v) + '" width="' + bw + '" height="' + (s.Y(0) - s.Y(v)) + '" fill="' + l.color + '" opacity="' + (l.opacity || 0.75) + '"/>'); });
      } else {
        var d = l.values.map(function (v, i) { return (i ? 'L' : 'M') + X(ts[i]).toFixed(1) + ' ' + s.Y(v).toFixed(1); }).join('');
        out.push('<path d="' + d + '" fill="none" stroke="' + l.color + '" stroke-width="2"' + (l.dash ? ' stroke-dasharray="' + l.dash + '"' : '') + '/>');
      }
    });
    if (now && now >= x0 && now <= x1) {
      out.push('<line x1="' + X(now) + '" x2="' + X(now) + '" y1="' + (m.t - 4) + '" y2="' + (H - m.b) + '" stroke="#15191d" stroke-width="1.5"/>');
      out.push('<text x="' + (X(now) + 4) + '" y="' + (m.t + 8) + '" font-size="11" fill="#15191d">now ' + esc(hm(now)) + '</text>');
    }
    var lx = m.l;
    o.layers.forEach(function (l) {
      var label = l.label + ' (' + l.unit + ')';
      out.push('<rect x="' + lx + '" y="6" width="10" height="' + (l.type === 'bar' ? 10 : 3) + '" fill="' + l.color + '"' + (l.type === 'bar' ? '' : ' transform="translate(0 4)"') + '/>');
      out.push('<text x="' + (lx + 14) + '" y="15" font-size="11" fill="#15191d">' + esc(label) + '</text>');
      lx += 22 + label.length * 6.2;
    });
    out.push('</svg>');
    el.innerHTML = out.join('');
  }

  /* --------------------------------------------------------------- sites -- */
  function renderSites() {
    var sites = S.bundle.sites.slice().sort(function (a, b) { var fa = forecast(a.site_id), fb = forecast(b.site_id); return (fb ? fb.p_overflow : -1) - (fa ? fa.p_overflow : -1); });
    $('#sitelist').innerHTML = sites.map(function (s) {
      var f = forecast(s.site_id), p = f ? f.p_overflow : null;
      return '<li tabindex="0" data-site="' + esc(s.site_id) + '"><span class="nm">' + esc(s.name) + '</span><span class="wb">' + esc(s.waterbody) + ' · ' + esc(s.outfall_type.replace('_', ' ')) + '</span><span class="pv ' + riskClass(p) + '"><span class="dot"></span><strong>' + pct(p) + '</strong>' + (f ? '<br><span class="wb">next ' + f.horizon_h + ' h</span>' : '') + '</span></li>';
    }).join('');
    $('#sitelist').querySelectorAll('li').forEach(function (li) {
      li.addEventListener('click', function () { select(li.dataset.site, true); });
      li.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(li.dataset.site, true); } });
    });
    if (typeof L === 'undefined') { $('#map').innerHTML = '<p class="empty">Map library failed to load.</p>'; return; }
    S.map = L.map('map', { scrollWheelZoom: false, zoomSnap: 0.5 });
    var tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' });
    var errs = 0; tiles.on('tileerror', function () { if (++errs === 2) $('#tilenote').hidden = false; });
    tiles.addTo(S.map);
    var pts = [];
    S.bundle.sites.forEach(function (s) {
      var f = forecast(s.site_id), p = f ? f.p_overflow : null;
      var mk = L.circleMarker([s.lat, s.lon], { radius: 10, color: '#15191d', weight: 1.5, fillColor: riskColor(p), fillOpacity: 0.9 }).addTo(S.map);
      mk.bindTooltip(esc(s.name) + ' · ' + pct(p) + ' overflow risk' + (f ? ' (' + f.horizon_h + ' h)' : ''));
      mk.on('click', function () { select(s.site_id, false); });
      S.markers[s.site_id] = mk; pts.push([s.lat, s.lon]);
    });
    if (pts.length) S.map.fitBounds(pts, { padding: [30, 30], maxZoom: 13 });
  }

  function select(id, fromList) {
    S.site = id;
    $('#sitelist').querySelectorAll('li').forEach(function (li) { li.setAttribute('aria-current', String(li.dataset.site === id)); });
    Object.keys(S.markers).forEach(function (k) { S.markers[k].setStyle({ weight: k === id ? 4 : 1.5, radius: k === id ? 13 : 10 }); });
    if (S.map && S.markers[id] && fromList) S.map.panTo(S.markers[id].getLatLng());
    renderSite();
    if (fromList && window.matchMedia('(max-width: 900px)').matches) $('#site').scrollIntoView({ behavior: 'smooth' });
  }

  function renderSite() {
    var s = S.bundle.sites.filter(function (x) { return x.site_id === S.site; })[0]; if (!s) return;
    $('#sitename').textContent = s.name;
    $('#sitesub').textContent = [s.waterbody, s.outfall_type.replace('_', ' '), 'boom ' + num(s.boom_length_m, 0) + ' m / ' + num(s.boom_capacity_m3, 1) + ' m³', 'channel ' + num(s.channel_width_m, 0) + ' m', s.tidal ? 'tidal' : 'non-tidal'].join(' · ');
    var all = fcs(s.site_id), f24 = all[0], f48 = all[1];
    $('#riskbox').innerHTML = f24 ? '<div class="big ' + riskClass(f24.p_overflow) + '">' + pct(f24.p_overflow) + '</div><div class="lbl">overflow risk, next ' + f24.horizon_h + ' h</div>' + (f48 ? '<div class="lbl">' + f48.horizon_h + ' h: <strong class="' + riskClass(f48.p_overflow) + '">' + pct(f48.p_overflow) + '</strong></div>' : '') + '<div>' + badge(f24.provenance.kind) + '</div>' : '<div class="lbl">No forecast</div>';
    var now = f24 ? f24.issued_at : null;
    var fo = bySite(S.bundle.forcing, s.site_id)[0];
    if (fo) {
      $('#forcingprov').innerHTML = prov('Rain', fo.rain_provenance) + prov('Tide', fo.tide_provenance, ' (' + fo.tide_datum + ')');
      chart($('#chart-forcing'), { t: fo.t, now: now, aria: 'Hourly rain and tide', layers: [
        { values: fo.rain_mm_h, type: 'bar', axis: 'left', color: '#2f6db5', label: 'Rain', unit: 'mm/h' },
        { values: fo.tide_m, type: 'line', axis: 'right', color: '#0a5a68', label: 'Tide', unit: 'm ' + fo.tide_datum }] });
    } else { $('#chart-forcing').innerHTML = '<p class="empty">No forcing series for this site yet (C1).</p>'; $('#forcingprov').innerHTML = ''; }
    var it = bySite(S.bundle.interceptor, s.site_id)[0];
    if (it) {
      $('#interprov').innerHTML = prov('Fill and escape', it.provenance);
      var esc_kg = it.t.map(function (_, i) { return it.escaped_entrainment_kg[i] + it.escaped_overtopping_kg[i] + it.escaped_bypass_kg[i]; });
      chart($('#chart-inter'), { t: it.t, now: now, hatch: it.provenance.kind !== 'observed', aria: 'Boom fill fraction and escaped plastic', layers: [
        { values: esc_kg, type: 'bar', axis: 'right', color: '#b0261d', label: 'Escaped', unit: 'kg/h', opacity: 0.55 },
        { values: it.fill_fraction.map(function (v) { return v * 100; }), type: 'line', axis: 'left', color: '#553b9b', label: 'Boom fill', unit: '%', min: 0, max: 100 }] });
    } else { $('#chart-inter').innerHTML = '<p class="empty">No interceptor series for this site yet (C4).</p>'; $('#interprov').innerHTML = ''; }
    $('#forecast').innerHTML = all.map(function (f) {
      var dr = Object.keys(f.drivers || {}).map(function (k) { return '<dt>' + esc(k.replace(/_/g, ' ')) + '</dt><dd>' + num(f.drivers[k], 1) + '</dd>'; }).join('');
      return '<dl class="kv"><dt>Next ' + f.horizon_h + ' h · issued ' + esc(hm(f.issued_at)) + ' IST</dt><dd class="' + riskClass(f.p_overflow) + '">' + pct(f.p_overflow) + '</dd><dt>expected arrival</dt><dd>' + num(f.expected_arrival_kg, 0) + ' kg</dd><dt>peak fill</dt><dd>' + pct(f.expected_fill_fraction) + '</dd>' + dr + '</dl>';
    }).join('<hr>') || '<p class="empty">No forecast for this site (C9).</p>';
    var tel = bySite(S.bundle.telemetry, s.site_id).sort(function (a, b) { return a.t < b.t ? 1 : -1; })[0];
    $('#telemetry').innerHTML = tel ? '<p>' + (tel.simulated ? badge('simulated') : badge('observed')) + ' last message ' + esc(ist(tel.t)) + '</p><dl class="kv">' +
      '<dt>battery</dt><dd>' + num(tel.battery_v, 2) + ' V</dd><dt>solar</dt><dd>' + num(tel.solar_w, 0) + ' W</dd>' +
      '<dt>water level</dt><dd>' + num(tel.water_level_m, 2) + ' m</dd><dt>rain last hour</dt><dd>' + num(tel.rain_mm_last_h, 1) + ' mm</dd>' +
      (tel.fill ? '<dt>boom fill (' + esc(tel.fill.method) + ')</dt><dd>' + pct(tel.fill.fill_fraction) + '</dd>' : '') +
      '<dt>health</dt><dd>' + (tel.health.length ? esc(tel.health.join(', ')) : 'no faults') + '</dd></dl>' : '<p class="empty">No telemetry for this site (C8).</p>';
  }

  /* ---------------------------------------------------------------- plan -- */
  function renderPlan() {
    var ps = (S.bundle.plans || []).slice().sort(function (a, b) { return a.issued_at < b.issued_at ? 1 : -1; });
    if (!ps.length) { $('#planmeta').textContent = 'No dispatch plan in this bundle (C10).'; return; }
    var day = ps.filter(function (x) { return x.issued_at === ps[0].issued_at; }).sort(function (a, b) { return a.policy_id < b.policy_id ? 1 : -1; });
    if (!S.policy || !day.some(function (x) { return x.policy_id === S.policy; })) S.policy = day[0].policy_id;
    var p = day.filter(function (x) { return x.policy_id === S.policy; })[0];
    $('#policytabs').innerHTML = day.length > 1 ? day.map(function (x) { return '<button type="button" aria-pressed="' + (x.policy_id === S.policy) + '" data-pol="' + esc(x.policy_id) + '">Policy ' + esc(x.policy_id) + (x.policy_id === 'P0' ? ' (reference)' : '') + '</button>'; }).join('') : '';
    $('#policytabs').querySelectorAll('button').forEach(function (b) { b.addEventListener('click', function () { S.policy = b.dataset.pol; renderPlan(); }); });
    var names = {}; S.bundle.sites.forEach(function (s) { names[s.site_id] = s.name; });
    $('#planmeta').innerHTML = esc(p.plan_id) + ' · policy ' + esc(p.policy_id) + ' · issued ' + esc(ist(p.issued_at)) + Object.keys(p.objective || {}).map(function (k) { return ' · ' + esc(k.replace(/_/g, ' ')) + ' ' + num(p.objective[k], 0); }).join('');
    $('#plantable tbody').innerHTML = p.assignments.map(function (a) {
      return '<tr tabindex="0" data-site="' + esc(a.site_id) + '"><td>' + esc(a.crew_id) + '</td><td>' + esc(names[a.site_id] || a.site_id) + '</td><td>' + esc(hm(a.start)) + '–' + esc(hm(a.end)) + '</td><td class="num">' + num(a.expected_cleared_kg, 0) + '</td><td>' + esc(a.reason) + '</td></tr>';
    }).join('');
    $('#plantable tbody').querySelectorAll('tr').forEach(function (tr) { tr.addEventListener('click', function () { select(tr.dataset.site, true); }); });
  }

  /* -------------------------------------------------------------- ledger -- */
  function truthOf(seq) { return (S.aux.synthetic_truth || []).filter(function (x) { return x.seq === seq; })[0]; }
  function renderLedger(marks) {
    var names = {}; S.bundle.sites.forEach(function (s) { names[s.site_id] = s.name; });
    var rows = [];
    S.entries.forEach(function (e, i) {
      var r = e.record, c = e.reconciliation, mk = marks ? (marks.has(i) ? '<span class="chip reject">✗ broken</span>' : '<span class="chip ok">✓</span>') : '—';
      rows.push('<tr tabindex="0" data-i="' + i + '"' + (marks && marks.has(i) ? ' class="bad"' : '') + '><td class="num">' + e.seq + '</td><td>' + esc(names[r.site_id] || r.site_id) + '<br><span class="sub">' + esc(r.crew_id) + '</span></td><td>' + esc(ist(r.t_start)) + '<br><span class="sub">to ' + esc(hm(r.t_end)) + '</span></td><td class="num">' + num(r.claimed_wet_kg, 1) + '</td><td class="num">' + num(c.claimed_kg, 1) + '</td><td class="num">' + num(c.sensor_estimated_kg, 1) + '</td><td class="num">' + num(c.ratio, 2) + '</td><td><span class="chip ' + c.flag + '">' + c.flag + '</span></td><td class="hash" title="' + esc(e.hash) + '">' + esc(e.hash.slice(0, 10)) + '…</td><td>' + mk + '</td></tr>');
      if (S.open.has(i)) {
        var tr = truthOf(e.seq);
        rows.push('<tr class="detail"><td></td><td colspan="9"><ul>' + c.reasons.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
          'hash <span class="hash">' + esc(e.hash) + '</span><br>prev <span class="hash">' + esc(e.prev_hash) + '</span><br>' + r.photo_sha256.length + ' photo hash(es) · GPS track ' + (r.gps_track_sha256 ? 'hashed' : 'missing') +
          (tr ? '<br>' + badge('synthetic') + ' injected as <strong>' + esc(tr.kind) + (tr.kind === 'inflated' ? ' ×' + tr.factor : '') + '</strong> (true wet kg ' + num(tr.true_wet_kg, 1) + ')' : '') + '</td></tr>');
      }
    });
    $('#ledgertable tbody').innerHTML = rows.join('');
    $('#ledgertable tbody').querySelectorAll('tr[data-i]').forEach(function (tr) {
      var go = function () { var i = +tr.dataset.i; if (S.open.has(i)) S.open.delete(i); else S.open.add(i); renderLedger(S.marks); };
      tr.addEventListener('click', go);
      tr.addEventListener('keydown', function (e) { if (e.key === 'Enter') go(); });
    });
    var a = S.aux.anchor;
    $('#anchorline').innerHTML = a ? 'Published anchor: ' + a.length + ' records, head <span class="hash">' + esc(a.head_hash) + '</span>' : 'No published anchor in this bundle: truncation of the newest records cannot be detected.';
  }

  async function verify() {
    var st = $('#verifystatus'); st.className = 'status'; st.textContent = 'Verifying…';
    var t0 = performance.now();
    var r = await LedgerVerify.verifyChain(S.entries, S.aux.anchor);
    var sg = await LedgerVerify.verifySignatures(S.entries, S.aux.signatures || [], S.aux.key_registry || {});
    var ms = Math.round(performance.now() - t0);
    S.marks = new Set(r.badSeqs);
    var sigTxt = sg.supported ? ' · signatures ' + (sg.checked - sg.badSeqs.length) + '/' + sg.checked + ' valid (Ed25519)' : ' · Ed25519 signature check needs a newer browser (checked in the Python tests)';
    if (r.ok) { st.className = 'status ok'; st.textContent = '✓ ' + r.checked + ' records intact; head matches the published anchor · SHA-256 via ' + r.engine + sigTxt + ' · ' + ms + ' ms'; }
    else { st.className = 'status bad'; st.textContent = '✗ Tampering detected: ' + r.problems[0] + (r.problems.length > 1 ? ' (+' + (r.problems.length - 1) + ' more)' : '') + sigTxt; }
    renderLedger(S.marks);
  }

  function tamper() {
    var i = Math.min(S.entries.length - 1, Math.floor(S.entries.length / 2));
    var e = JSON.parse(JSON.stringify(S.entries[i]));
    e.record.claimed_wet_kg = Math.round(e.record.claimed_wet_kg * 1.25 * 10) / 10;
    S.entries = S.entries.slice(); S.entries[i] = e;
    $('#reset').disabled = false;
    $('#verifystatus').textContent = 'Record #' + i + ': claimed wet kg raised by 25% in this browser only.';
    verify();
  }

  /* ------------------------------------------------------ detection, metrics -- */
  function kv(obj, skip) {
    return '<dl class="kv">' + Object.keys(obj).filter(function (k) { return skip.indexOf(k) < 0; }).slice(0, 16).map(function (k) {
      var v = obj[k], isRate = typeof v === 'number' && v >= 0 && v <= 1 && /recall|precision|rate|auc|map|f1|accuracy|iou/i.test(k);
      return '<dt>' + esc(k.replace(/_/g, ' ')) + '</dt><dd>' + (typeof v === 'number' ? (isRate ? (v * 100).toFixed(1) + '%' : num(v, Math.abs(v) < 10 ? 3 : 1)) : esc(v)) + '</dd>';
    }).join('') + '</dl>';
  }
  function renderDetection() {
    var m = (S.bundle.metrics || {}).detection, smp = S.aux.detection_samples || [];
    if (!m) { $('#detbody').innerHTML = '<p class="empty">Waiting for C5 results: <code>components/detection/results/metrics.json</code> and sample detections are merged here by <code>build_bundle.py</code> once the detection session publishes them.</p>'; return; }
    var html = kv(m, ['reproduce']) + (m.reproduce ? '<pre>' + esc(m.reproduce) + '</pre>' : '');
    if (smp.length) {
      html += '<div class="detgrid">' + smp.map(function (f) {
        var wh = f.image_wh || [1, 1], boxes = (f.detections || []).map(function (d) { var b = d.bbox_xyxy; return '<rect x="' + b[0] + '" y="' + b[1] + '" width="' + (b[2] - b[0]) + '" height="' + (b[3] - b[1]) + '" fill="none" stroke="#f2b705" stroke-width="' + Math.max(2, wh[0] / 200) + '"/>'; }).join('');
        return '<figure><img src="' + esc(f.image) + '" alt="Sample frame ' + esc(f.frame_id) + '"><svg viewBox="0 0 ' + wh[0] + ' ' + wh[1] + '" preserveAspectRatio="none">' + boxes + '</svg><figcaption>' + esc(f.frame_id) + ' · ' + (f.detections || []).length + ' detections</figcaption></figure>';
      }).join('') + '</div>';
    }
    $('#detbody').innerHTML = html;
  }
  function renderMetrics() {
    var M = S.bundle.metrics || {};
    $('#metricsbody').innerHTML = Object.keys(M).map(function (k) {
      return '<div><h3>' + esc(k.replace(/_/g, ' ')) + '</h3>' + kv(M[k], ['reproduce']) + (M[k].reproduce ? '<pre>' + esc(M[k].reproduce) + '</pre>' : '') + '</div>';
    }).join('') || '<p class="empty">No component metrics in this bundle.</p>';
  }

  /* ---------------------------------------------------------------- boot -- */
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

  async function boot() {
    var l2 = 'mr'; try { l2 = localStorage.getItem('t3-lang2') || 'mr'; } catch (e) { /* ignore */ }
    applyLang(l2);
    document.querySelectorAll('.lang button').forEach(function (b) { b.addEventListener('click', function () { applyLang(b.dataset.lang); }); });
    var d;
    try { d = await load(); } catch (e) { $('#meta').textContent = 'Could not load dashboard_bundle.json. Run build_bundle.py, then serve this folder: python3 -m http.server'; return; }
    S.bundle = d.bundle; S.aux = d.aux; S.entries = S.bundle.ledger.slice(); S.original = S.entries;
    var f0 = (S.bundle.forcing || [])[0], win = f0 && f0.t.length ? 'data window ' + fDT.format(new Date(f0.t[0])) + ' → ' + fDT.format(new Date(f0.t[f0.t.length - 1])) + ' · ' : '';
    $('#meta').textContent = win + 'built ' + ist(S.bundle.generated_at) + ' · git ' + S.bundle.git_sha + ' · schema ' + S.bundle.schema_version + ' · all times IST';
    var mock = (S.bundle.disclaimers || []).filter(function (x) { return /^SYNTHETIC MOCK/.test(x); })[0];
    if (mock) { $('#mockstrip').hidden = false; $('#mockstrip').textContent = mock; }
    $('#disclaimers').innerHTML = (S.bundle.disclaimers || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('');
    $('#via').textContent = 'Loaded from ' + d.via + (S.aux.inputs ? ' · inputs: twin = ' + S.aux.inputs.twin + ' · reproduce: ' + S.aux.inputs.reproduce : '');
    renderSites(); renderPlan(); renderLedger(null); renderDetection(); renderMetrics();
    var top = S.bundle.sites.slice().sort(function (a, b) { var fa = forecast(a.site_id), fb = forecast(b.site_id); return (fb ? fb.p_overflow : -1) - (fa ? fa.p_overflow : -1); })[0];
    if (top) select(top.site_id, false);
    $('#verify').addEventListener('click', verify);
    $('#tamper').addEventListener('click', tamper);
    $('#reset').addEventListener('click', function () { S.entries = S.original; S.marks = null; $('#reset').disabled = true; verify(); });
    var tm; window.addEventListener('resize', function () { clearTimeout(tm); tm = setTimeout(renderSite, 150); });
    verify();
  }
  boot();
})();
