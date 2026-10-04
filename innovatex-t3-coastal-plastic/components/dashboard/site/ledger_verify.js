/* Hash-chain verifier for C11 evidence records. Byte-identical to mrv_ledger/canonical.py + chain.py.
 * Works in the browser (window.LedgerVerify) and in node (module.exports) for cross-language tests.
 * SHA-256 uses WebCrypto when available (secure contexts) and a pure-JS fallback otherwise, so a phone
 * opening the dashboard over plain http on the LAN can still verify. */
(function (root) {
  'use strict';
  var GENESIS = '0000000000000000000000000000000000000000000000000000000000000000';

  function canonicalize(v) {
    if (v === null || typeof v !== 'object') {
      if (typeof v === 'number' && !isFinite(v)) throw new Error('non-finite number');
      return JSON.stringify(v);
    }
    if (Array.isArray(v)) return '[' + v.map(canonicalize).join(',') + ']';
    var keys = Object.keys(v).sort();
    return '{' + keys.map(function (k) { return JSON.stringify(k) + ':' + canonicalize(v[k]); }).join(',') + '}';
  }

  var K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2];

  function rotr(x, n) { return (x >>> n) | (x << (32 - n)); }

  function sha256HexSync(str) {
    var bytes = new TextEncoder().encode(str), l = bytes.length;
    var buf = new Uint8Array(((l + 9 + 63) >> 6) * 64);
    buf.set(bytes); buf[l] = 0x80;
    var dv = new DataView(buf.buffer), bits = l * 8;
    dv.setUint32(buf.length - 4, bits >>> 0);
    dv.setUint32(buf.length - 8, Math.floor(bits / 4294967296));
    var H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    var W = new Array(64);
    for (var off = 0; off < buf.length; off += 64) {
      for (var i = 0; i < 16; i++) W[i] = dv.getUint32(off + 4 * i);
      for (i = 16; i < 64; i++) {
        var s0 = rotr(W[i - 15], 7) ^ rotr(W[i - 15], 18) ^ (W[i - 15] >>> 3);
        var s1 = rotr(W[i - 2], 17) ^ rotr(W[i - 2], 19) ^ (W[i - 2] >>> 10);
        W[i] = (W[i - 16] + s0 + W[i - 7] + s1) >>> 0;
      }
      var a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
      for (i = 0; i < 64; i++) {
        var t1 = (h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + W[i]) >>> 0;
        var t2 = ((rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) >>> 0;
        h = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
      }
      H[0] = (H[0] + a) >>> 0; H[1] = (H[1] + b) >>> 0; H[2] = (H[2] + c) >>> 0; H[3] = (H[3] + d) >>> 0;
      H[4] = (H[4] + e) >>> 0; H[5] = (H[5] + f) >>> 0; H[6] = (H[6] + g) >>> 0; H[7] = (H[7] + h) >>> 0;
    }
    return H.map(function (x) { return ('00000000' + x.toString(16)).slice(-8); }).join('');
  }

  function hasSubtle() { return typeof crypto !== 'undefined' && crypto.subtle && typeof crypto.subtle.digest === 'function'; }

  function sha256Hex(str) {
    if (!hasSubtle()) return Promise.resolve(sha256HexSync(str));
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(str)).then(function (d) {
      return Array.from(new Uint8Array(d)).map(function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    });
  }

  function entryBody(e) {
    return canonicalize({ seq: e.seq, record: e.record, reconciliation: e.reconciliation, prev_hash: e.prev_hash });
  }

  /* Returns {ok, checked, problems[], badSeqs[], engine}. anchor = {length, head_hash} published elsewhere. */
  async function verifyChain(entries, anchor) {
    var problems = [], bad = new Set(), prev = GENESIS;
    for (var i = 0; i < entries.length; i++) {
      var e = entries[i];
      if (e.seq !== i) { problems.push('seq ' + i + ': position holds seq=' + e.seq + ' (deleted, inserted or reordered)'); bad.add(i); }
      if (e.prev_hash !== prev) { problems.push('seq ' + i + ': prev_hash does not link to the previous entry'); bad.add(i); }
      if ((await sha256Hex(entryBody(e))) !== e.hash) { problems.push('seq ' + i + ': content does not match its hash (edited)'); bad.add(i); }
      prev = e.hash;
    }
    if (anchor) {
      var head = entries.length ? entries[entries.length - 1].hash : GENESIS;
      if (entries.length !== anchor.length) problems.push('anchor: length ' + entries.length + ' != published ' + anchor.length);
      if (head !== anchor.head_hash) problems.push('anchor: head hash differs from the published head');
    }
    return { ok: problems.length === 0, checked: entries.length, problems: problems, badSeqs: Array.from(bad),
             engine: hasSubtle() ? 'WebCrypto' : 'pure-JS' };
  }

  function hexToBytes(h) { var o = new Uint8Array(h.length / 2); for (var i = 0; i < o.length; i++) o[i] = parseInt(h.substr(2 * i, 2), 16); return o; }

  /* Ed25519 via WebCrypto where the browser supports it; otherwise {supported:false}. */
  async function verifySignatures(entries, sigs, registry) {
    if (!hasSubtle()) return { supported: false };
    var bySeq = {}; sigs.forEach(function (s) { bySeq[s.seq] = s; });
    var bad = [];
    try {
      for (var i = 0; i < entries.length; i++) {
        var e = entries[i], s = bySeq[e.seq];
        if (!s || registry[s.signer_id] !== s.public_key_hex) { bad.push(e.seq); continue; }
        var key = await crypto.subtle.importKey('raw', hexToBytes(s.public_key_hex), { name: 'Ed25519' }, false, ['verify']);
        var ok = await crypto.subtle.verify({ name: 'Ed25519' }, key, hexToBytes(s.signature_hex), new TextEncoder().encode(e.hash));
        if (!ok) bad.push(e.seq);
      }
    } catch (err) { return { supported: false, error: String(err) }; }
    return { supported: true, ok: bad.length === 0, badSeqs: bad, checked: entries.length };
  }

  var api = { GENESIS: GENESIS, canonicalize: canonicalize, sha256Hex: sha256Hex, sha256HexSync: sha256HexSync,
              entryBody: entryBody, verifyChain: verifyChain, verifySignatures: verifySignatures };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LedgerVerify = api;
})(typeof window !== 'undefined' ? window : globalThis);
