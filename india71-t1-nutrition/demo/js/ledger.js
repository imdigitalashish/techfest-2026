/* Poshan Setu demo: the audit ledger, re-verified in the browser.
 * A line-by-line port of components/audit_ledger/ledger.py (hash = SHA-256 over Python's
 * json.dumps(entry_without_hash, sort_keys=True, separators=(",", ":")), ensure_ascii escaping).
 * The page and demo/smoke.sh (Node) load this same file; smoke checks every hash against Python's, byte for byte.
 */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.PoshanLedger = api;
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
  ];
  var ZERO_HASH = "0000000000000000000000000000000000000000000000000000000000000000";

  function utf8(str) {
    if (typeof TextEncoder !== "undefined") return new TextEncoder().encode(str);
    var out = [];
    for (var i = 0; i < str.length; i++) {
      var c = str.codePointAt(i);
      if (c > 0xffff) i++;
      if (c < 0x80) out.push(c);
      else if (c < 0x800) out.push(0xc0 | (c >> 6), 0x80 | (c & 63));
      else if (c < 0x10000) out.push(0xe0 | (c >> 12), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
      else out.push(0xf0 | (c >> 18), 0x80 | ((c >> 12) & 63), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
    }
    return new Uint8Array(out);
  }

  function sha256Hex(input) {
    var bytes = typeof input === "string" ? utf8(input) : input;
    var n = bytes.length;
    var withPad = ((n + 9 + 63) >> 6) << 6;
    var buf = new Uint8Array(withPad);
    buf.set(bytes);
    buf[n] = 0x80;
    var bitsHi = Math.floor(n / 0x20000000), bitsLo = (n << 3) >>> 0;
    buf[withPad - 8] = (bitsHi >>> 24) & 255; buf[withPad - 7] = (bitsHi >>> 16) & 255;
    buf[withPad - 6] = (bitsHi >>> 8) & 255; buf[withPad - 5] = bitsHi & 255;
    buf[withPad - 4] = (bitsLo >>> 24) & 255; buf[withPad - 3] = (bitsLo >>> 16) & 255;
    buf[withPad - 2] = (bitsLo >>> 8) & 255; buf[withPad - 1] = bitsLo & 255;
    var h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    var w = new Uint32Array(64);
    for (var off = 0; off < withPad; off += 64) {
      for (var t = 0; t < 16; t++) {
        var j = off + 4 * t;
        w[t] = ((buf[j] << 24) | (buf[j + 1] << 16) | (buf[j + 2] << 8) | buf[j + 3]) >>> 0;
      }
      for (t = 16; t < 64; t++) {
        var x = w[t - 15], y = w[t - 2];
        var s0 = ((x >>> 7) | (x << 25)) ^ ((x >>> 18) | (x << 14)) ^ (x >>> 3);
        var s1 = ((y >>> 17) | (y << 15)) ^ ((y >>> 19) | (y << 13)) ^ (y >>> 10);
        w[t] = (w[t - 16] + s0 + w[t - 7] + s1) >>> 0;
      }
      var a = h[0], b = h[1], c = h[2], d = h[3], e = h[4], f = h[5], g = h[6], hh = h[7];
      for (t = 0; t < 64; t++) {
        var S1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7));
        var ch = (e & f) ^ (~e & g);
        var t1 = (hh + S1 + ch + K[t] + w[t]) >>> 0;
        var S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
        var maj = (a & b) ^ (a & c) ^ (b & c);
        var t2 = (S0 + maj) >>> 0;
        hh = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
      }
      h[0] = (h[0] + a) >>> 0; h[1] = (h[1] + b) >>> 0; h[2] = (h[2] + c) >>> 0; h[3] = (h[3] + d) >>> 0;
      h[4] = (h[4] + e) >>> 0; h[5] = (h[5] + f) >>> 0; h[6] = (h[6] + g) >>> 0; h[7] = (h[7] + hh) >>> 0;
    }
    var hex = "";
    for (var i = 0; i < 8; i++) hex += ("00000000" + h[i].toString(16)).slice(-8);
    return hex;
  }

  /* Python json.dumps(..., ensure_ascii=True): escape " \ and \b\f\n\r\t; everything outside 0x20-0x7e as \uXXXX. */
  function pyString(s) {
    var out = '"';
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      if (c === 0x22) out += '\\"';
      else if (c === 0x5c) out += "\\\\";
      else if (c === 0x0a) out += "\\n";
      else if (c === 0x0d) out += "\\r";
      else if (c === 0x09) out += "\\t";
      else if (c === 0x08) out += "\\b";
      else if (c === 0x0c) out += "\\f";
      else if (c < 0x20 || c > 0x7e) out += "\\u" + ("0000" + c.toString(16)).slice(-4);
      else out += s.charAt(i);
    }
    return out + '"';
  }

  function canonical(value) {
    if (value === null || value === undefined) return "null";
    if (typeof value === "boolean") return value ? "true" : "false";
    if (typeof value === "number") {
      if (!Number.isInteger(value)) throw new Error("non-integer numbers are not used in audit entries");
      return String(value);
    }
    if (typeof value === "string") return pyString(value);
    if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
    return "{" + Object.keys(value).sort().map(function (k) { return pyString(k) + ":" + canonical(value[k]); }).join(",") + "}";
  }

  /* _canonical_payload: the entry without "hash", prev_hash as stored. */
  function payload(entry) {
    var data = {};
    Object.keys(entry).forEach(function (k) { if (k !== "hash") data[k] = entry[k]; });
    return canonical(data);
  }

  function hashEntry(entry) { return sha256Hex(payload(entry)); }

  /* Ledger.verify(checkpoint): [ok, first bad index or null]. */
  function verify(entries, checkpoint) {
    if (checkpoint) {
      var count = checkpoint[0], head = checkpoint[1];
      if (entries.length < count) return [false, entries.length];
      if (count && entries[count - 1].hash !== head) return [false, count - 1];
    }
    var prev = ZERO_HASH;
    for (var i = 0; i < entries.length; i++) {
      var e = entries[i];
      if (e.seq !== i || e.prev_hash !== prev) return [false, i];
      if (e.hash !== hashEntry(e)) return [false, i];
      prev = e.hash;
    }
    return [true, null];
  }

  function copy(entries) { return entries.map(function (e) { return Object.assign({}, e); }); }

  function flip(entries, k) { var es = copy(entries); es[k].action = "access_allow"; return es; }

  /* Re-seal entries [start, stop): recompute hashes (and prev links after the first), as an insider would. */
  function reseal(entries, start, stop) {
    var es = copy(entries);
    var end = stop === undefined || stop === null ? es.length : stop;
    for (var i = start; i < end; i++) {
      if (i > start) es[i].prev_hash = es[i - 1].hash;
      es[i].hash = hashEntry(es[i]);
    }
    return es;
  }

  function truncate(entries, n) { return copy(entries).slice(0, entries.length - n); }

  /* The same scenarios demo/export.py asks Python to judge. */
  function scenarios(entries, checkpoint, k) {
    function both(es) { return { no_checkpoint: verify(es), checkpoint: verify(es, checkpoint) }; }
    return {
      intact: both(entries),
      flip: both(flip(entries, k)),
      flip_reseal_one: both(reseal(flip(entries, k), k, k + 1)),
      flip_reseal_all: both(reseal(flip(entries, k), k)),
      truncate_3: both(truncate(entries, 3))
    };
  }

  return {
    ZERO_HASH: ZERO_HASH, sha256Hex: sha256Hex, canonical: canonical, payload: payload, hashEntry: hashEntry,
    verify: verify, flip: flip, reseal: reseal, truncate: truncate, scenarios: scenarios
  };
});
