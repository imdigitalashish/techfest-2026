"""Headless smoke test for the P8 demo: no browser, no LLM, no network. Exit 0 = pass.

    demo/smoke.sh                  (= .venv/bin/python -m demo.smoke)

1. data.js is derived-only (strict schema for real items: ids, codes, flags, costs; no text fields) and its embedded
   claims equal a fresh eval.numbers.claims() (no drift from the committed results).
2. Every aggregate is re-derived here from the per-item rows and compared with the committed result files
   (independently of export.py's own checks), including the headline numbers on screen.
3. The server starts headless (python -m demo.server, no-text mode): static files are served, /api/real/* is refused,
   and the live engine gives the expected certificates, abstentions, pair certificates, 1,000 identical re-asks, a
   sealed prediction that the reveal verifies by sha256, one-time reveal tokens, and a deterministic slip storm.
4. Result-like numbers ($, %, x/y) in demo/SCRIPT.md and demo/README.md come from committed results or the live run.
5. If the local .data/ copy exists: a --local-text server re-derives the engine's code for all 304 real items
   (must equal the export, identical over two passes), and a leak guard checks that no Eedi question text or math
   expression appears in any file under demo/.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
DATA = ROOT / ".data"
RES = ROOT / "eval" / "results"
MODELS = ("gpt-5.5", "gpt-5.4-mini", "gpt-4.1-mini")
CODES = ("LTR", "SQ_DOUBLE", "SUB_NEG", "FRAC_ADD", "NEG_TIMES_NEG")
REAL_KEYS = {"id", "g", "gold", "rel", "ev", "nm", "eng", "llm", "usd", "rt"}

FAILS: list[str] = []
PASSES = 0


def check(cond: bool, label: str) -> None:
    global PASSES
    if cond:
        PASSES += 1
        print(f"ok    {label}", flush=True)
    else:
        FAILS.append(label)
        print(f"FAIL  {label}", flush=True)


def load_data() -> dict:
    txt = (DEMO / "web" / "data.js").read_text(encoding="utf-8")
    assert txt.startswith("window.P8 = ")
    return json.loads(txt[len("window.P8 = "):].rstrip().rstrip(";"))


def committed(name: str) -> dict:
    return json.loads((RES / name).read_text())


# ---- 1 + 2: data -------------------------------------------------------------------------------------------------------
def check_data(d: dict) -> None:
    from eval import numbers

    check(d["claims"] == numbers.claims(), "embedded claims == fresh eval.numbers.claims()")
    rows = d["real"]["items"]
    check(len(rows) == 304 and len({r["id"] for r in rows}) == 304, "304 distinct real items")
    vocab = set(CODES) | {"NONE"}
    for r in rows:
        ok = (set(r) == REAL_KEYS and re.fullmatch(r"\d+_[A-D]", r["id"]) and r["g"] in ("P", "N", "S")
              and r["gold"] in vocab and r["eng"] in vocab and (r["rel"] is None or r["rel"] in CODES)
              and isinstance(r["ev"], bool) and isinstance(r["nm"], int)
              and set(r["llm"]) == set(MODELS) and all(v in vocab for v in r["llm"].values())
              and all(isinstance(v, (int, float)) for v in list(r["usd"].values()) + list(r["rt"].values())))
        if not ok:
            check(False, f"real item {r.get('id')} has only derived fields")
            break
    else:
        check(True, "real items: derived fields only (strict schema)")
    for iid, runs in d["real"]["consistency"].items():
        if not (iid in {r["id"] for r in rows} and all(all(c in vocab for c in runs[m]["codes"]) for m in MODELS)):
            check(False, f"consistency {iid}: codes only")
            break
    else:
        check(True, "re-asked runs: codes only")

    real = committed("llm_gaps_real_negatives.json")
    P = [r for r in rows if r["g"] == "P"]
    N = [r for r in rows if r["g"] == "N"]
    check((len(P), len(N)) == (131, 152) == (real["counts"]["P"], real["counts"]["N"]), "131 positives, 152 negatives")
    acc = lambda pred: sum(pred(r) == r["gold"] for r in P) / len(P)  # noqa: E731
    fc = lambda pred: sum(pred(r) != "NONE" for r in N)  # noqa: E731
    check(fc(lambda r: r["eng"]) == 0, "engine: 0/152 false claims")
    check(round(acc(lambda r: r["eng"]), 4) == real["methods"]["EXEC"]["acc_P"] == 0.1908, "engine: 19.1% of positives")
    check(round(acc(lambda r: r["llm"]["gpt-5.5"]), 4) == real["methods"]["LLM:gpt-5.5"]["acc_P"] == 0.7939, "GPT-5.5: 79.4% of positives")
    check(fc(lambda r: r["llm"]["gpt-5.5"]) == 0, "GPT-5.5: 0/152 false claims")
    check(fc(lambda r: r["llm"]["gpt-4.1-mini"]) == 24 and d["claims"]["real.gpt-4.1-mini.fcr"] == "15.8%", "GPT-4.1-mini: 24/152 = 15.8%")
    for m in MODELS:
        hyb = lambda r, m=m: r["eng"] if r["eng"] != "NONE" else r["llm"][m]  # noqa: E731
        check(round(acc(hyb), 4) == real["methods"][f"HYB:{m}"]["acc_P"], f"cascade {m}: positives match committed HYB")
    casc = committed("cascade_real.json")
    for m in MODELS:
        llm = 1000 * sum(r["usd"][m] for r in rows) / len(rows)
        cas = 1000 * sum(r["usd"][m] for r in rows if r["eng"] == "NONE") / len(rows)
        check(abs(llm - casc["models"][m]["cost_usd_per_1000_llm_only"]) < 5e-4 and
              abs(cas - casc["models"][m]["cost_usd_per_1000_cascade"]) < 5e-4, f"real cost per 1,000 {m} re-derived")
    check((d["claims"]["casc.real.gpt-5.5.cost1000_llm"], d["claims"]["casc.real.gpt-5.5.cost1000_cascade"]) == ("$6.50", "$6.10"),
          "real cascade GPT-5.5: $6.50 -> $6.10")
    check(sum(r["eng"] != "NONE" for r in rows) == casc["engine_answers"] == 26, "engine certifies 26 of 304")
    pr = d["prob"]["items"]
    diag = committed("llm_gaps_prob_diag.json")
    for m in MODELS:
        llm = 1000 * sum(r["usd"][m] for r in pr) / len(pr)
        cas = 1000 * sum(r["usd"][m] for r in pr if r["eng"] == "NONE") / len(pr)
        check(abs(llm - diag["decisions"][m]["cost_usd_per_1000_llm_only"]) < 5e-4 and
              abs(cas - diag["decisions"][m]["cost_usd_per_1000_cascade"]) < 5e-4, f"tutor-native cost per 1,000 {m} re-derived")
    check((d["claims"]["diag.gpt-5.5.cost1000_llm"], d["claims"]["diag.gpt-5.5.cost1000_cascade"]) == ("$7.32", "$5.08"),
          "tutor-native cascade GPT-5.5: $7.32 -> $5.08")
    cons = committed("llm_consistency.json")
    for m in MODELS:
        n_dis = sum(len(set(v[m]["codes"])) > 1 for v in d["real"]["consistency"].values())
        check(n_dis == cons["models"][m]["n_disagree"], f"{m} changed {n_dis}/40 on re-ask (committed)")
    check(d["claims"]["cons.gpt-5.5.disagree"] == "2", "GPT-5.5 changed 2 of 40")
    check(d["claims"]["ph.engine_identical"] == "304/304", "engine identical 304/304 (committed)")
    for c in d["grid"]:
        ok = True
        if c["workload"] == "real":
            key = {"llm": f"LLM:{c['model']}", "cascade": f"HYB:{c['model']}", "gated": f"GATED:{c['model']}", "engine": "EXEC"}[c["routing"]]
            ok = c["acc_pos"] == real["methods"][key]["acc_P"] and c["fcr"] == real["methods"][key]["fcr_N"] and c["ba"] == real["methods"][key]["ba"]
        else:
            key = {"llm": f"LLM:{c['model']}", "cascade": f"CASCADE:{c['model']}", "engine": "ENGINE(abstain->NONE)"}[c["routing"]]
            ok = c["ba"] == diag["methods"][key]["acc_all"] and c["fcr"] == diag["methods"][key]["false_attribution_slip"]
        if not ok:
            check(False, f"grid {c['workload']} {c['model']} {c['routing']} == committed {key}")
            break
    else:
        check(True, f"all {len(d['grid'])} knob settings equal the committed aggregates")


# ---- 3: server ------------------------------------------------------------------------------------------------------------
class Server:
    def __init__(self, *extra: str):
        self.p = subprocess.Popen([sys.executable, "-m", "demo.server", "--no-browser", "--port", "8890", *extra],
                                  cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        line = self.p.stdout.readline()
        m = re.search(r"http://127\.0\.0\.1:(\d+)/", line)
        if not m:
            self.p.kill()
            raise RuntimeError(f"server did not start: {line}{self.p.stdout.read()[:2000]}")
        self.base = f"http://127.0.0.1:{m.group(1)}"
        t0 = time.time()
        while time.time() - t0 < 30:
            try:
                self.get("/api/health")
                break
            except (urllib.error.URLError, ConnectionError):
                time.sleep(0.2)

    def req(self, path: str, body=None):
        data = None if body is None else json.dumps(body).encode()
        r = urllib.request.Request(self.base + path, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def get(self, path: str):
        code, raw = self.req(path)
        return code, json.loads(raw) if raw[:1] in (b"{", b"[") else raw

    def post(self, path: str, body: dict):
        code, raw = self.req(path, body)
        return code, json.loads(raw)

    def close(self):
        self.p.terminate()
        try:
            self.p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.p.kill()


def check_server_notext(d: dict) -> dict:
    t0 = time.time()
    s = Server()
    live_numbers: dict = {}
    try:
        check(time.time() - t0 < 60, f"server up in {time.time() - t0:.1f} s (bar: first visual within 60 s)")
        code, h = s.get("/api/health")
        check(code == 200 and h["mode"] == "no-text" and h["llm_calls"] == 0, "health: no-text mode, 0 LLM calls")
        code, raw = s.req("/")
        check(code == 200 and b"P8" in raw and b"data.js" in raw, "index.html served")
        code, raw = s.req("/data.js")
        check(code == 200 and raw.startswith(b"window.P8 = "), "data.js served")
        code, j = s.get("/api/real/1195_B")
        check(code == 403 and "question" not in j, "no-text mode refuses /api/real (no item text)")
        q = {"expr": "3 + 4 × 2"}
        _, c = s.post("/api/certify", {**q, "answer": "14"})
        cert = (c.get("certificates") or [{}])[0]
        check(c["verdict"] == "certificate" and cert.get("rules") == ["LTR"] and cert.get("value") == "14"
              and [x["status"] for x in cert["steps"]] == ["order", "after"], "3 + 4 × 2 = 14: LTR certificate with trace")
        _, c = s.post("/api/certify", {**q, "answer": "12"})
        check(c["verdict"] == "abstain" and "LLM" in c["route"], "3 + 4 × 2 = 12 (slip): no claim, would route to the LLM")
        _, c = s.post("/api/certify", {**q, "answer": "11"})
        check(c["verdict"] == "correct", "3 + 4 × 2 = 11: correct")
        _, c = s.post("/api/certify", {"expr": "1/8 + 1/8", "answer": "2/16"})
        check(c["verdict"] == "certificate" and c["certificates"][0]["rules"] == ["FRAC_ADD"], "1/8 + 1/8 = 2/16: FRAC_ADD")
        _, c = s.post("/api/certify", {"expr": "2 + 3 × 4²", "answer": "40"})
        check(c["verdict"] == "certificate" and c["certificates"][0]["rules"] == ["LTR", "SQ_DOUBLE"], "2 + 3 × 4² = 40: pair LTR + SQ_DOUBLE")
        _, r = s.post("/api/rerun", {**q, "answer": "14", "n": 1000})
        check(r["n"] == 1000 and r["identical"] == 1000, f"ask again ×1000: {r['identical']}/1000 identical (median {r['median_ms']} ms)")
        live_numbers["rerun_median_ms"] = r["median_ms"]
        _, p = s.post("/api/predict", {**q, "answer": "14"})
        check(p.get("ok") and len(p["hash"]) == 64 and p["verification"]["key_verified"] and p["lead"] == "LTR",
              "predict: SymPy-verified follow-up, sealed sha256")
        _, p2 = s.post("/api/predict", {**q, "answer": "14"})
        check(p2["question"] == p["question"] and p2["hash"] != p["hash"], "ask again: same follow-up, fresh nonce")
        from demo import live  # the conditional prediction, recomputed independently from the question's tokens

        toks = live.tokens_from(tokens=p["question"]["tokens"])
        predicted = live.LIB.predict_set(live.build_item(toks, as_mcq=False), ["pack:LTR"])
        _, rv = s.post("/api/reveal", {"token": p["token"], "answer": predicted})
        check(rv["ok"] and rv["verdict"] == "match" and hashlib.sha256(rv["committed"].encode()).hexdigest() == p["hash"],
              "reveal: predicted answer matches; sha256(committed) == sealed hash")
        check(rv["posterior"]["map_set"] == ["LTR"] and rv["posterior"]["marginals"]["LTR"] > 0.99 and rv.get("practice"),
              "tracer: LTR after two answers; targeted practice generated")
        _, again = s.post("/api/reveal", {"token": p["token"], "answer": predicted})
        check(again.get("ok") is False, "reveal tokens are one-time")
        _, rv2 = s.post("/api/reveal", {"token": p2["token"], "answer": json.loads(rv["committed"])["if_you_hold"]["slip"]})
        check(rv2["verdict"] == "correct", "reveal with the correct answer: 'may have been a slip'")
        _, st = s.post("/api/slipstorm", {})
        _, st2 = s.post("/api/slipstorm", {})
        check(st["slips"] == 2400 and st["abstain"] + st["collide"] == 2400 and st == {**st2, "ms": st["ms"]},
              f"slip storm deterministic: {st['abstain']} no claim, {st['collide']} collide")
        live_numbers.update(slips=st["slips"], collide=st["collide"], abstain=st["abstain"], share=st["collide_share"])
        code, e = s.post("/api/certify", {"expr": "3 + + 4", "answer": "1"})
        check(code == 400 and "cannot read" in e["error"], "bad expression: clear 400 error")
    finally:
        s.close()
    return live_numbers


# ---- 4: docs ----------------------------------------------------------------------------------------------------------------
def check_docs(d: dict, live_numbers: dict) -> None:
    from eval import numbers

    allowed = numbers.allowed() | {v.strip("$%") for v in d["claims"].values()}
    allowed |= {f"{100 * live_numbers['share']:.1f}", f"{live_numbers['collide']}", f"{live_numbers['abstain']:,}",
                f"{live_numbers['slips']:,}"}
    for name in ("SCRIPT.md", "README.md"):
        f = DEMO / name
        if not f.exists():
            check(False, f"demo/{name} exists")
            continue
        bad = []
        for m in re.finditer(r"\$(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)%", f.read_text(encoding="utf-8")):
            v = m.group(1) or m.group(2)
            if v not in allowed and v not in ("0", "100"):
                bad.append(m.group(0))
        check(not bad, f"demo/{name}: every $ and % number is a committed result or live output" + (f" (unknown: {bad})" if bad else ""))


# ---- 5: local text (internal verification) + leak guard ------------------------------------------------------------------
def check_local(d: dict) -> None:
    if not (DATA / "eedi2024" / "queries_w_rels.parquet").exists():
        print("SKIP  local-text checks: no .data/ copy (optional: demo/run.sh --fetch)", flush=True)
        return
    s = Server("--local-text")
    try:
        code, h = s.get("/api/health")
        check(h["mode"] == "local-text", "local-text mode starts when explicitly asked")
        code, r = s.post("/api/real/rerun", {"n": 2})
        check(r["items"] == 304 and r["identical"] == 304 and r["matches_export"] == 304,
              f"live engine on 304 real items: {r['matches_export']}/304 equal the export, {r['identical']}/304 identical over 2 passes")
        code, it = s.get("/api/real/1195_B")
        check(code == 200 and it["engine"] == it["export_engine"] == "SQ_DOUBLE" and it.get("certificate"),
              "local text: live certificate for 1195_B equals the export")
    finally:
        s.close()
    leak_guard()


def leak_guard() -> None:
    import pandas as pd

    from components.bugs.eedi_parse import latex_to_dsl, math_segments
    from components.bugs.school_math import parse_dsl, show
    from eval.run_llm_gaps import split_query

    data = load_data()
    ids = {r["id"] for r in data["real"]["items"]}
    q = pd.read_parquet(DATA / "eedi2024" / "queries_w_rels.parquet")
    needles: set[str] = set()
    for qid, query in zip(q.qid.astype(str), q["query"]):
        if qid not in ids:
            continue
        question, correct, incorrect = split_query(query)
        needles.add(" ".join(question.split())[:60])
        for seg in math_segments(question):
            if len(seg.strip()) >= 8:
                needles.add(seg.strip())
            try:
                expr = show(parse_dsl(latex_to_dsl(seg)))
            except SyntaxError:
                continue
            if len(expr) >= 12:  # short expressions such as "3 + 4 × 2" also occur in our own examples
                needles.add(expr)
    needles = {n for n in needles if len(n) >= 8}
    files = [p for p in DEMO.rglob("*") if p.is_file() and p.suffix in (".py", ".js", ".html", ".md", ".sh", ".json", ".txt")]
    hits = []
    for f in files:
        txt = " ".join(f.read_text(encoding="utf-8", errors="ignore").split())
        hits += [f"{f.relative_to(ROOT)}" for n in needles if n in txt]
    check(not hits, f"leak guard: none of {len(needles)} Eedi question snippets/expressions in {len(files)} demo files"
          + (f" (found in {sorted(set(hits))})" if hits else ""))


def main() -> int:
    t0 = time.time()
    d = load_data()
    check_data(d)
    live_numbers = check_server_notext(d)
    check_docs(d, live_numbers)
    check_local(d)
    print(f"\n{PASSES} passed, {len(FAILS)} failed in {time.time() - t0:.1f} s", flush=True)
    for f in FAILS:
        print(f"  FAILED: {f}")
    print("SMOKE PASS" if not FAILS else "SMOKE FAIL")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
