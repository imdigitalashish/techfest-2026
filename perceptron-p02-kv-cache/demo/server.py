"""P2 demo backend: serves the offline page (demo/web/) and, for LIVE mode, runs the committed harness on this CPU.

Every live number is computed by eval/kvbench_torch.py: Engine.prefill/forward/answer, stream_idx, topk_idx,
window_scores, gather, rod_build, rod_answer, block_scores. Each method's store is built exactly as kvbench_torch.main()
builds it, BEFORE any question is seen. This file only assembles the document, calls those functions and reports bytes.
The X-ray heat replays rod_answer's own scoring lines (block_scores, softmax_lift on the 4-bit layer-5 sketch) and
is checked to select the same blocks rod_answer recalled.

Usage: nice -n 10 python3 demo/server.py [--port 8502] [--replay-only]
Env:   DEMO_MEM_MIN (default 30): load the model only while `sysctl kern.memorystatus_level` >= this
       DEMO_THREADS (default: torch's default)
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import common

MEM_MIN = int(os.environ.get("DEMO_MEM_MIN", "30"))
CFG_ROD = {"layer": 5, "bits": 4, "scorer": "softmax_lift", "lexical": False, "qsel": "content"}  # frozen config
CFG_LEX = {"layer": 5, "bits": 4, "scorer": "softmax_lift", "lexical": True, "qsel": "content"}   # --lex_qsel content
# same opening as kvbench_torch.make_sample, so live prompts have the evaluated format
INTRO = ("Below is a long text. Hidden in it are several special codes and numbers. Read carefully; "
         "you will be asked about them later.\n\n")
DEFAULTS = {"needle": "The judges' favourite dessert at Techfest 2026 is mango kulfi.", "expected": "mango kulfi",
            "question": "What is the judges' favourite dessert at Techfest 2026?",
            "paraphrase": "Which sweet do the Techfest judges like best?",
            "depth": 0.35, "doc_seed": 1, "ctx_tokens": 3000, "budget": 0.10}
LABELS = {"full": "Full cache", "streaming": "StreamingLLM (ours)", "h2o": "H2O-style (ours)",
          "snapkv": "SnapKV-variant (ours, +4 sinks)", "rod": "RoD (ours)", "rodlex": "RoD-lexical (control)"}


def mem_level():
    try:
        return int(subprocess.run(["sysctl", "-n", "kern.memorystatus_level"], capture_output=True, text=True, timeout=5).stdout)
    except Exception:
        return None


class Live:
    def __init__(self, replay_only=False):
        self.state, self.detail, self.load_s, self.err = "starting", "", None, None
        self.lock = threading.Lock()
        self.busy = None
        self.rate = 140.0  # prefill tokens/s on the M5 (4 threads, measured); updated after every prefill
        self.doc = None
        if replay_only:
            self.state, self.detail = "off", "replay-only mode (run.sh --replay)"
        else:
            threading.Thread(target=self._load, daemon=True).start()

    # ---------------- model ----------------
    def _load(self):
        try:
            ok, why = common.data_ready()
            if not ok:
                self.state, self.detail = "nodata", why
                return
            while True:
                lvl = mem_level()
                if lvl is None or lvl >= MEM_MIN:
                    break
                self.state, self.detail = "waiting", f"memory pressure: kern.memorystatus_level {lvl} < {MEM_MIN}; retrying"
                time.sleep(5)
            self.state, self.detail = "loading", "loading Llama-3.2-1B-Instruct (fp32, CPU)"
            t0 = time.time()
            import torch
            import torch.nn.functional as F
            import kvbench_torch as kb
            if os.environ.get("DEMO_THREADS"):
                torch.set_num_threads(int(os.environ["DEMO_THREADS"]))
            self.torch, self.F, self.kb = torch, F, kb
            self.tok = common.load_tokenizer()
            self.E = kb.Engine(kb.load_model(), self.tok)
            self.paras = (common.DATA / "haystack.txt").read_text(encoding="utf-8").split("\n")
            self.per_tok = 2 * self.E.nl * self.E.nkv * self.E.hd * 2
            self.load_s = round(time.time() - t0, 1)
            self.state, self.detail = "ready", f"Llama-3.2-1B-Instruct · fp32 on CPU · {torch.get_num_threads()} threads"
        except Exception as e:  # surfaced on the page
            self.state, self.detail, self.err = "error", f"{type(e).__name__}: {e}", traceback.format_exc()

    def status(self):
        b = None
        if self.busy:
            b = dict(self.busy, elapsed_s=round(time.time() - self.busy["t0"], 1))
        return {"state": self.state, "detail": self.detail, "load_s": self.load_s, "busy": b, "mem_level": mem_level(),
                "mem_min": MEM_MIN, "has_doc": self.doc is not None, "defaults": DEFAULTS}

    # ---------------- document ----------------
    def _build_doc(self, needle, depth, doc_seed, ctx_tokens):
        tok, rng = self.tok, random.Random(10_000 + doc_seed)
        i, body, n_tok = rng.randrange(0, len(self.paras) - 2000), [], 0
        while n_tok < ctx_tokens - 90 - 16:  # same length rule as make_sample with one needle
            body.append(self.paras[i])
            n_tok += len(tok.encode(self.paras[i], add_special_tokens=False)) + 1
            i += 1
        body.insert(round(depth * len(body)), needle)
        return INTRO + "\n".join(body)

    def _split(self, text, question):
        return self.kb.chat(self.tok, text + "\n\n@@SPLIT@@" + question).split("@@SPLIT@@")

    # ---------------- stores (built before any question exists) ----------------
    def _stores(self, f):
        kb, E, d = self.kb, self.E, self.doc
        Kf, Vf, acc, caps, ctx_ids = d["Kf"], d["Vf"], d["acc"], d["caps"], d["ctx_ids"]
        T = len(ctx_ids)
        B = max(kb.N_SINK + kb.N_RECENT + 1, round(f * T))
        t0 = time.time()
        idx = kb.stream_idx(T, B, E.nkv)
        h2o = [kb.topk_idx(acc[l], B, T, n_recent=B // 2) for l in range(E.nl)]
        snp = [kb.topk_idx(kb.window_scores(caps[l], Kf[l], E.scale, True), B, T) for l in range(E.nl)]
        S = {"full": kb.Cache(Kf, Vf),
             "streaming": kb.Cache([kb.gather(k, idx) for k in Kf], [kb.gather(v, idx) for v in Vf]),
             "h2o": kb.Cache([kb.gather(Kf[l], h2o[l]) for l in range(E.nl)], [kb.gather(Vf[l], h2o[l]) for l in range(E.nl)]),
             "snapkv": kb.Cache([kb.gather(Kf[l], snp[l]) for l in range(E.nl)], [kb.gather(Vf[l], snp[l]) for l in range(E.nl)]),
             "rod": kb.rod_build(E, Kf, Vf, ctx_ids, B, CFG_ROD, caps),
             "rodlex": kb.rod_build(E, Kf, Vf, ctx_ids, B, CFG_LEX, caps)}
        d.update(f=f, B=B, S=S, build_s=round(time.time() - t0, 3))
        return self._layout()

    def _rod_info(self, st):
        kb = self.kb
        res = sum(kb.nb(x) for x in st["Kr"] + st["Vr"])
        wq = kb.nb(st["wq"]) if st["wq"] is not None else 0
        return {"B_res": st["B_res"], "B_rec": st["B_rec"], "m": max(0, st["B_rec"] // kb.BLOCK), "ev0": st["ev0"], "ev1": st["ev1"],
                "nblk": -(-(st["ev1"] - st["ev0"]) // kb.BLOCK), "resident_bytes": res, "sketch_bytes": st["sketch_bytes"] - wq,
                "window_bytes": wq, "ids_bytes": kb.nb(st["ids"]), "stored_bytes": st["stored_bytes"]}

    def _layout(self):
        d, kb = self.doc, self.kb
        T, B = len(d["ctx_ids"]), d["B"]
        full_bytes = sum(kb.nb(x) for x in d["Kf"] + d["Vf"])
        assert full_bytes == T * self.per_tok
        S = d["S"]
        stored = {m: (S[m]["stored_bytes"] if isinstance(S[m], dict) else S[m].stored_bytes()) for m in LABELS}
        return {"T": T, "f": d["f"], "B": B, "budget_bytes": B * self.per_tok, "full_bytes": full_bytes, "per_tok": self.per_tok,
                "stored": stored, "build_s": d["build_s"], "stream_from": T - (B - kb.N_SINK), "rod": self._rod_info(S["rod"]),
                "rodlex": self._rod_info(S["rodlex"]), "needle_pos": d["needle_pos"], "needle_end": d["needle_end"],
                "nblocks": -(-(T - kb.N_SINK) // kb.BLOCK), "snips": d["snips"], "needle_context": d["needle_context"],
                "prefill_s": d["prefill_s"], "labels": LABELS}

    def compress(self, p):
        needle = str(p.get("needle") or DEFAULTS["needle"]).strip()[:400]
        expected = str(p.get("expected") or "").strip()[:80]
        depth = min(1.0, max(0.0, float(p.get("depth", DEFAULTS["depth"]))))
        doc_seed = int(p.get("doc_seed", DEFAULTS["doc_seed"])) % 100
        ctx_tokens = min(4096, max(1000, int(p.get("ctx_tokens", DEFAULTS["ctx_tokens"]))))
        f = min(0.5, max(0.1, float(p.get("budget", DEFAULTS["budget"]))))
        text = self._build_doc(needle, depth, doc_seed, ctx_tokens)
        pre, _ = self._split(text, "?")
        enc = self.tok(pre, add_special_tokens=False, return_offsets_mapping=True)
        ctx_ids = enc["input_ids"]
        assert ctx_ids == self.tok.encode(pre, add_special_tokens=False)
        c0 = pre.index(needle)
        a0 = c0 + (needle.find(expected) if expected and expected in needle else 0)
        offs = enc["offset_mapping"]
        tok_at = lambda c: next(i for i, (s, e) in enumerate(offs) if e > c)
        T = len(ctx_ids)
        self.busy = {"what": "prefill", "t0": time.time(), "eta_s": round(T / self.rate, 1), "T": T}
        t0 = time.time()
        Kf, Vf, acc, caps = self.E.prefill(ctx_ids)
        prefill_s = time.time() - t0
        self.rate = T / prefill_s
        kb = self.kb
        snips = [self.tok.decode(ctx_ids[s:s + kb.BLOCK], skip_special_tokens=True).replace("\n", " ").strip()[:48]
                 for s in range(kb.N_SINK, T, kb.BLOCK)]
        self.doc = {"text": text, "pre": pre, "ctx_ids": ctx_ids, "Kf": Kf, "Vf": Vf, "acc": acc, "caps": caps, "needle": needle,
                    "expected": expected, "needle_pos": tok_at(a0), "needle_end": tok_at(c0 + len(needle) - 1) + 1,
                    "prefill_s": round(prefill_s, 1), "snips": snips,
                    "needle_context": pre[max(0, c0 - 160):c0 + len(needle) + 160], "depth": depth, "doc_seed": doc_seed}
        return self._stores(f)

    def budget(self, p):
        if self.doc is None:
            raise ValueError("compress a document first")
        return self._stores(min(0.5, max(0.1, float(p.get("budget", 0.1)))))

    # ---------------- answering ----------------
    def _heat(self, st, q_ids, n_content):
        """rod_answer's scoring lines, verbatim, to expose the per-block scores it ranks."""
        kb, E, torch, F = self.kb, self.E, self.torch, self.F
        T, ev0, ev1, cfg = st["T"], st["ev0"], st["ev1"], st["cfg"]
        En = ev1 - ev0
        nblk, m = -(-En // kb.BLOCK), max(0, st["B_rec"] // kb.BLOCK)
        if m == 0 or En <= 0:
            return [], []
        _, caps = E.forward(q_ids, T, kb.Cache(st["Kr"], st["Vr"]), capture=len(q_ids))
        qq = caps[cfg["layer"]][:, :, :n_content].float()
        wq = st["wq"].float() if st["wq"] is not None else None
        r = kb.block_scores(qq, wq, st["sketch"].dense().float(), E.scale, cfg["scorer"], E.nkv)
        rb = F.pad(r, (0, nblk * kb.BLOCK - En), value=float("-inf")).view(nblk, kb.BLOCK).max(1).values
        order = torch.topk(rb, min(m, nblk)).indices.tolist()
        return [round(float(x), 6) for x in rb], sorted(order)

    def ask(self, p):
        if self.doc is None:
            raise ValueError("compress a document first")
        kb, E, d = self.kb, self.E, self.doc
        question = str(p.get("question") or DEFAULTS["question"]).strip()[:300]
        expected = str(p.get("expected", d["expected"]) or "").strip()[:80]
        pre, post = self._split(d["text"], question)
        assert pre == d["pre"], "context prefix changed with the question"
        q_ids = self.tok.encode(post, add_special_tokens=False)
        n_content = len(self.tok.encode(question, add_special_tokens=False))
        T, S = len(d["ctx_ids"]), d["S"]
        self.busy = {"what": "answer", "t0": time.time(), "eta_s": 8}
        ok = lambda txt: bool(expected) and expected.lower() in txt.replace(",", "").lower()
        out, rod = [], {}
        for m in ("full", "streaming", "h2o", "snapkv", "rod", "rodlex"):
            t0 = time.time()
            if m in ("rod", "rodlex"):
                st = S[m]
                text, chosen, rec = kb.rod_answer(E, st, q_ids, n_content, halo=0)
                sb = st["stored_bytes"]
                ab = sb + rec
                blk = (d["needle_pos"] - st["ev0"]) // kb.BLOCK if st["ev0"] <= d["needle_pos"] < st["ev1"] else None
                rod[m] = {"chosen": chosen, "recalled_bytes": rec, "needle_block": blk, "needle_evicted": blk is not None,
                          "hit": blk is not None and blk in chosen, "m": max(0, st["B_rec"] // kb.BLOCK)}
            else:
                text = E.answer(S[m], T, q_ids)
                sb = ab = S[m].stored_bytes()
            out.append({"method": m, "label": LABELS[m], "answer": text.strip()[:120], "correct": ok(text),
                        "stored_bytes": sb, "answer_time_bytes": ab, "s": round(time.time() - t0, 2)})
        t0 = time.time()
        heat, top = self._heat(S["rod"], q_ids, n_content)
        rod["rod"].update(heat=heat, heat_top=top, consistent=top == rod["rod"]["chosen"], heat_s=round(time.time() - t0, 2))
        return {"question": question, "expected": expected, "n_q_tokens": len(q_ids), "n_content": n_content, "answers": out,
                "rod": rod, "budget_bytes": d["B"] * self.per_tok, "f": d["f"], "B": d["B"], "T": T}

    # ---------------- reproduce committed rows (honesty check; used by smoke.sh) ----------------
    def reproduce(self, p):
        kb, E = self.kb, self.E
        run = str(p.get("run", "T1_literal_s0"))
        if not run.replace("_", "").isalnum():
            raise ValueError("bad run name")
        sample = int(p.get("sample", 0))
        methods = [m for m in p.get("methods", ["full", "streaming", "rod"]) if m in ("full", "streaming", "h2o", "snapkv", "knorm", "rod", "rodlex")]
        fracs = [float(x) for x in p.get("fracs", [0.1, 0.25])]
        res = common.ROOT / "eval" / "results"
        meta = json.loads((res / f"{run}.json").read_text())["meta"]
        rows = {(r["method"], r["frac"], r["q"]): r for r in map(json.loads, (res / f"{run}.rows.jsonl").read_text().splitlines())
                if r["sample"] == sample}
        rng = random.Random(meta["seed"])
        for _ in range(sample + 1):
            ctx_ids, qs = kb.make_sample(self.tok, self.paras, meta["ctx_target"], meta["needles"], rng, meta["style"])
        T = len(ctx_ids)
        self.busy = {"what": "reproduce", "t0": time.time(), "eta_s": round(T / self.rate + 30, 1), "T": T}
        Kf, Vf, acc, caps = E.prefill(ctx_ids)
        cmp = []
        for m in methods:
            for f in ([1.0] if m == "full" else fracs):
                B = max(kb.N_SINK + kb.N_RECENT + 1, round(f * T))
                st, store = None, None
                if m == "full":
                    store = kb.Cache(Kf, Vf)
                elif m in ("rod", "rodlex"):
                    cfg = {"layer": meta["rod_layer"], "bits": meta["rod_bits"], "scorer": meta["rod_scorer"], "lexical": m == "rodlex",
                           "qsel": meta["lex_qsel"] if m == "rodlex" else meta["rod_qsel"]}
                    st = kb.rod_build(E, Kf, Vf, ctx_ids, B, cfg, caps)
                else:
                    if m == "streaming":
                        idxs = [kb.stream_idx(T, B, E.nkv)] * E.nl
                    elif m == "h2o":
                        idxs = [kb.topk_idx(acc[l], B, T, n_recent=B // 2) for l in range(E.nl)]
                    elif m == "snapkv":
                        idxs = [kb.topk_idx(kb.window_scores(caps[l], Kf[l], E.scale, True), B, T) for l in range(E.nl)]
                    else:
                        idxs = [kb.topk_idx(-Kf[l][0].float().norm(dim=-1), B, T) for l in range(E.nl)]
                    store = kb.Cache([kb.gather(Kf[l], idxs[l]) for l in range(E.nl)], [kb.gather(Vf[l], idxs[l]) for l in range(E.nl)])
                for qi, (q_ids, nd) in enumerate(qs):
                    ref = rows.get((m, f, qi))
                    if ref is None:
                        continue
                    if st is not None:
                        text, chosen, rec = kb.rod_answer(E, st, q_ids, nd["n_q_content"], halo=meta.get("halo", 0))
                        kbytes, ab = st["stored_bytes"], st["stored_bytes"] + rec
                    else:
                        text, chosen = E.answer(store, T, q_ids), None
                        kbytes = ab = store.stored_bytes()
                    live = {"answer": text.strip()[:48], "correct": nd["value"] in text.replace(",", ""), "stored_bytes": kbytes,
                            "answer_time_bytes": ab, "recalled_blocks": chosen}
                    same = all(live[k] == ref.get(k) for k in live if not (k == "recalled_blocks" and chosen is None))
                    cmp.append({"method": m, "frac": f, "q": qi, "live": live["answer"], "committed": ref["answer"],
                                "correct": live["correct"], "same": same})
        return {"run": run, "sample": sample, "T": T, "n": len(cmp), "n_same": sum(c["same"] for c in cmp), "rows": cmp}

    def run(self, name, p):
        if self.state != "ready":
            raise RuntimeError(f"live engine not ready ({self.state}: {self.detail})")
        if not self.lock.acquire(blocking=False):
            raise BlockingIOError("busy with another live request")
        try:
            t0 = time.time()
            r = getattr(self, name)(p)
            r["wall_s"] = round(time.time() - t0, 2)
            return r
        finally:
            self.busy = None
            self.lock.release()


class Handler(BaseHTTPRequestHandler):
    live: Live = None
    STATIC = {"/": ("index.html", "text/html; charset=utf-8"), "/index.html": ("index.html", "text/html; charset=utf-8"),
              "/replay.js": ("replay.js", "text/javascript; charset=utf-8")}

    def log_message(self, fmt, *args):
        if "/api/status" not in (args[0] if args else ""):
            sys.stderr.write("[demo] " + fmt % args + "\n")

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/status":
            return self._send(200, self.live.status())
        if path in self.STATIC:
            fn, ctype = self.STATIC[path]
            return self._send(200, (common.WEB / fn).read_bytes(), ctype)
        self._send(404, {"error": "not found"})

    def do_POST(self):
        path = self.path.split("?")[0]
        name = {"/api/compress": "compress", "/api/budget": "budget", "/api/ask": "ask", "/api/reproduce": "reproduce"}.get(path)
        if name is None:
            return self._send(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            p = json.loads(self.rfile.read(min(n, 65536)) or b"{}")
            self._send(200, self.live.run(name, p))
        except BlockingIOError as e:
            self._send(409, {"error": str(e)})
        except RuntimeError as e:
            self._send(503, {"error": str(e)})
        except Exception as e:
            traceback.print_exc()
            self._send(400, {"error": f"{type(e).__name__}: {e}"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8502)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--replay-only", action="store_true")
    a = ap.parse_args()
    Handler.live = Live(replay_only=a.replay_only)
    srv = None
    for port in range(a.port, a.port + 20):
        try:
            srv = ThreadingHTTPServer((a.host, port), Handler)
            break
        except OSError:
            continue
    if srv is None:
        sys.exit(f"no free port in {a.port}..{a.port + 19}")
    print(f"DEMO_URL=http://{a.host}:{srv.server_address[1]}/", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
