/* Node check used by demo/smoke.sh: the page's ledger.js must reproduce Python's audit ledger byte for byte.
 * 1. SHA-256 known-answer tests.  2. Every exported entry's hash recomputed in JS equals the hash Python wrote.
 * 3. The JS verdicts on the tamper scenarios equal Python's (components/audit_ledger/ledger.py via demo/export.py).
 * Usage: node demo/js/check_ledger.cjs   (exit 1 on any mismatch)
 */
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const L = require("./ledger.js");

let failures = 0;
function check(ok, msg) {
  console.log((ok ? "  ok   " : "  FAIL ") + msg);
  if (!ok) failures++;
}

const KAT = {
  "": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  abc: "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
  "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq": "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1",
};
for (const [msg, want] of Object.entries(KAT)) check(L.sha256Hex(msg) === want, `SHA-256 known answer (${msg.length} chars)`);
check(L.sha256Hex("a".repeat(1000000)) === "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0", "SHA-256 known answer (1,000,000 x 'a')");
check(L.canonical({ b: 1, a: "é\"\\\n", c: null }) === '{"a":"\\u00e9\\"\\\\\\n","b":1,"c":null}', "canonical JSON escapes like Python ensure_ascii");

const src = fs.readFileSync(path.join(__dirname, "..", "data", "demo_data.js"), "utf8");
const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(src, sandbox);
const D = sandbox.window.DEMO_DATA;
const order = (D.sim && D.sim.order) || [];
check(order.length > 0, `district cohorts with a ledger: ${order.join(", ")}`);
for (const pid of order) {
  const led = D.sim[pid].ledger;
  const entries = led.entries;
  const cp = [led.checkpoint.count, led.checkpoint.head];
  const bad = entries.filter((e) => L.hashEntry(e) !== e.hash).map((e) => e.seq);
  check(bad.length === 0, `[${pid}] ${entries.length} entry hashes recomputed in JS == Python's${bad.length ? " (bad: " + bad + ")" : ""}`);
  check(JSON.stringify(L.verify(entries, cp)) === "[true,null]", `[${pid}] JS verify(checkpoint) accepts the exported chain`);
  const js = L.scenarios(entries, cp, led.python_verdicts.flip_index);
  for (const name of Object.keys(js)) {
    for (const mode of ["no_checkpoint", "checkpoint"]) {
      const a = JSON.stringify(js[name][mode]);
      const b = JSON.stringify(led.python_verdicts[name][mode]);
      check(a === b, `[${pid}] ${name} / ${mode}: JS ${a} == Python ${b}`);
    }
  }
}
console.log(failures ? `ledger parity: ${failures} FAILED` : "ledger parity: JS == Python");
process.exit(failures ? 1 : 0);
