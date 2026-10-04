// Headless state check for demo/web/index.html (run by demo/smoke.sh; needs node, no browser).
// Renders every REPLAY state (run x budget x question) with the page's own code against a minimal DOM stub, plus the
// LIVE evidence table at every budget (10..50%), and asserts the copy rules from the 4 Oct demo review:
//   - T2 states show only the amendment-5/E6 caveat (32-token figures first) and never the withdrawn look-alike reading;
//   - every state where RoD beats the full cache shows a caveat; no "memory actually used"; no empty quantiser clause;
//   - the compact Full / RoD / best-baseline row is present; the token map has a description and a block summary.
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const web = path.join(__dirname, "web");
const app = fs.readFileSync(path.join(web, "index.html"), "utf8").split("<script>")[1].split("</script>")[0];

class El {
  constructor(tag = "div") {
    Object.assign(this, {tag, attrs: {}, children: [], _html: "", textContent: "", style: {}, dataset: {}, hidden: false, value: "", _q: {}});
    this.classList = {add() {}, remove() {}, toggle() {}};
  }
  set innerHTML(v) { this._html = String(v); this.children = []; }
  get innerHTML() { return this._html; }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  getAttribute(k) { return k in this.attrs ? this.attrs[k] : null; }
  appendChild(c) { this.children.push(c); return c; }
  replaceChildren(...c) { this.children = c; this._html = ""; }
  addEventListener() {}
  querySelector(s) { return this._q[s] || (this._q[s] = new El()); }
  querySelectorAll() { return []; }
  get previousElementSibling() { return this._prev || (this._prev = new El()); }
  get parentElement() { return this._par || (this._par = new El()); }
  get clientWidth() { return 900; }
  get offsetWidth() { return 120; }
  getBoundingClientRect() { return {left: 0, top: 0, width: 900, height: 300}; }
  scrollIntoView() {}
  focus() {}
  text() { return [this._html, this.textContent, this.attrs["aria-label"] || "", ...this.children.map(c => c.text())].join(" "); }
}
const els = {};
const document = {querySelector: s => els[s] || (els[s] = new El()), querySelectorAll: () => [], createElementNS: (ns, t) => new El(t), activeElement: null};
const ctx = {document, location: {hash: ""}, history: {replaceState() {}}, addEventListener() {}, setTimeout: () => 0, clearTimeout() {},
  fetch: () => Promise.reject(new Error("offline")), innerWidth: 1440, innerHeight: 900, URLSearchParams, console};
ctx.window = ctx;
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(web, "replay.js"), "utf8"), ctx);
vm.runInContext(app, ctx);
const R = ctx.REPLAY, E6 = R.e6, $ = s => document.querySelector(s);
const plain = el => el.text().replace(/<[^>]+>/g, " ").replace(/&[a-z#0-9]+;/g, " ").replace(/\s+/g, " ");
const KEYS = ["#thesis", "#runnote", "#qcard", "#tracks", "#blk", "#compact", "#board", "#boardnote", "#chart", "#chartlegend", "#mech", "#prov"];
const fails = [], fail = (st, msg) => { if (fails.length < 25) fails.push(`${st}: ${msg}`); };
let n = 0, nT2 = 0;
R.runs.forEach((rn, i) => {
  if (!rn.methods.includes("full")) return;
  const full = rn.table.find(t => t.m === "full");
  for (const b of rn.fracs) rn.contexts.forEach((c, s) => c.needles.forEach((nd, q) => {
    vm.runInContext(`ST.run = ${i}; ST.b = ${JSON.stringify(b)}; ST.s = ${s}; ST.q = ${q}; render();`, ctx);
    const st = `${rn.key} ${b}% c${s + 1} q${q + 1}`, all = KEYS.map(k => plain($(k))).join(" | "), note = plain($("#runnote"));
    n++;
    if (/memory actually used/i.test(all)) fail(st, 'shows "memory actually used"');
    if (/instead:\s*\./.test(all)) fail(st, "empty quantiser clause");
    if (!/logical context state/.test(all)) fail(st, 'no "logical context state" wording');
    const rod = rn.table.find(t => t.m === "rod" && Math.abs(t.f * 100 - b) < 1e-6);
    if (rod && rod.acc > full.acc && !/caveat/i.test(note)) fail(st, "RoD beats the full cache but no caveat is shown");
    if (rn.key === "T2") {
      nT2++;
      if (/look-alike/i.test(all)) fail(st, "T2 shows the withdrawn look-alike explanation");
      if (E6 && !(note.includes(`${E6.full_k}/${E6.n}`) && note.includes(`${E6.rod_k}/${E6.n}`) && note.includes(`${E6.d_s} (95% CI ${E6.lo_s} to ${E6.hi_s})`)
                  && /superiority not established/.test(note) && /amendment 5; E6 sensitivity/.test(note)))
        fail(st, "T2 note does not lead with the E6 caveat");
      if (note.replace(/Caveat, with 32-token answers.*$/, "").trim()) fail(st, "T2 note shows more than the E6/amendment-5 caveat");
    }
    const cards = ($("#compact").innerHTML.match(/class="cmp/g) || []).length;
    const want = b === "100" ? ["full", "int4", "int2"].filter(m => rn.methods.includes(m)).length : 3;  // T3 ran no quantisers
    if (cards !== want) fail(st, `compact comparison row has ${cards} cards, want ${want}`);
    if (!/Token map of context/.test($("#tracks").text()) || !/tokens/.test(plain($("#blk")))) fail(st, "token map lacks a description or block summary");
  }));
});
vm.runInContext("liveInit();", ctx);
let nLive = 0;
for (let bv = 10; bv <= 50; bv += 5) {
  $("#lb").value = String(bv);
  vm.runInContext("evidence();", ctx);
  const t = plain($("#levid"));
  nLive++;
  if (/fewer look-alike|hid(e|ing) look-alike/i.test(t)) fail(`live ${bv}%`, "evidence table shows the withdrawn look-alike explanation");
  if (/T2 · paraphrased/.test(t) && E6 && !(t.includes(`${E6.full_k}/${E6.n}`) && /superiority not established/.test(t))) fail(`live ${bv}%`, "T2 evidence row lacks the E6 caveat");
}
if (fails.length) {
  for (const f of fails) console.log("FAIL  " + f);
  process.exit(1);
}
console.log(`PASS  page states: ${n} replay states (${nT2} T2) + ${nLive} live budgets rendered by the page's own code; T2 shows only the E6/amendment-5 caveat `
  + `(full ${E6 ? E6.full_k : "?"}/${E6 ? E6.n : "?"} vs RoD ${E6 ? E6.rod_k : "?"}/${E6 ? E6.n : "?"}, ${E6 ? E6.d_s : "?"}) and never "look-alike"; caveat wherever RoD beats full; no "memory actually used"`);
