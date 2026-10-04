"""C8 Runner: assess every document in a folder, offline; one Assessment JSON per input file.

Usage (from apctt-trl-assessor/):
  python -m components.skeleton.runner --train            # fit the v0 model on the TechPort train split
  python -m components.skeleton.runner --in DIR --out DIR [--rule median] [--offline] [--timeout 60]
Each input `name.ext` produces `name.ext.assessment.json`. A failure or timeout on one document yields a
schema-valid fallback record (training prior, abstain, error text) and the batch continues.
"""
from __future__ import annotations

import argparse
import json
import signal
import time
from pathlib import Path

from . import decode, doctype, emit, evidence, gap, ingest, ordinal

SUFFIXES = {".txt", ".md", ".pdf", ".html", ".htm", ".xml", ".docx"}
VERSIONS = {"pipeline": "skeleton-v0.1", "rubric": "eu_annex_g+nasa_v0"}


class DocTimeout(Exception):
    pass


def network_off() -> None:
    """Fail loudly if anything tries to use the network (a tripwire, not an OS sandbox)."""
    import socket

    def _blocked(*_a, **_k):
        raise RuntimeError("network access attempted while --offline")

    socket.socket.connect = _blocked  # type: ignore[method-assign]
    socket.create_connection = _blocked  # type: ignore[assignment]
    socket.getaddrinfo = _blocked  # type: ignore[assignment]


def assess(path: Path, model: ordinal.Model, rule: str, schema: dict) -> dict:
    t0 = time.perf_counter()
    doc = ingest.parse(path)
    dt = doctype.classify(doc)
    ev = evidence.extract(doc)
    text = " \n".join(s["text"] for s in doc["sections"])
    dist = model.predict(text) if doc["n_chars"] >= 200 else model.prior_distribution()
    dec = decode.decide(dist, rule=rule, n_chars=doc["n_chars"])
    ga = gap.analyse(dec, dist, ev)
    err = None if doc["n_chars"] else f"no text extracted ({doc['parser']})"
    a = emit.assemble(doc, dt, dec, dist, ev, ga, 1000 * (time.perf_counter() - t0),
                      {**VERSIONS, "model": dist["model_id"]}, error=err)
    errs = emit.check_assessment(a, schema)
    if errs:
        raise ValueError(f"schema violations: {errs[:5]}")
    return a


def fallback(path: Path, model: ordinal.Model, rule: str, schema: dict, why: str) -> dict:
    dist = model.prior_distribution()
    dec = decode.decide(dist, rule=rule, n_chars=0)
    doc = {"doc_id": path.name}
    a = emit.assemble(doc, {"type": "other", "confidence": 0.0}, dec, dist, [], gap.analyse(dec, dist, []), 0.0,
                      {**VERSIONS, "model": dist["model_id"]}, error=why[:500])
    assert not emit.check_assessment(a, schema)
    return a


def assess_safe(path: Path, model, rule, schema, timeout_s: int) -> dict:
    has_alarm = hasattr(signal, "SIGALRM")
    if has_alarm and timeout_s > 0:
        def _raise(*_):
            raise DocTimeout(f"timeout after {timeout_s}s")
        old = signal.signal(signal.SIGALRM, _raise)
        signal.alarm(timeout_s)
    try:
        return assess(path, model, rule, schema)
    except Exception as e:  # fail closed, keep the batch alive
        return fallback(path, model, rule, schema, f"{type(e).__name__}: {e}")
    finally:
        if has_alarm and timeout_s > 0:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp"); ap.add_argument("--out"); ap.add_argument("--rule", default="median")
    ap.add_argument("--train", action="store_true"); ap.add_argument("--offline", action="store_true")
    ap.add_argument("--timeout", type=int, default=60); ap.add_argument("--model", default=str(ordinal.DEFAULT_MODEL))
    a = ap.parse_args()
    if a.offline:
        network_off()
    if a.train:
        t0 = time.time(); out = ordinal.train(out=Path(a.model)); print(f"trained -> {out} in {time.time()-t0:.1f}s")
        if not a.inp:
            return
    model, schema = ordinal.Model(Path(a.model)), emit.load_schema()
    files = sorted(p for p in Path(a.inp).iterdir() if p.is_file() and p.suffix.lower() in SUFFIXES)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    t0, n_err = time.time(), 0
    for f in files:
        res = assess_safe(f, model, a.rule, schema, a.timeout)
        n_err += res["error"] is not None
        (Path(a.out) / f"{f.name}.assessment.json").write_text(json.dumps(res, indent=1))
        print(f"{f.name}: TRL {res['decision']['trl']} (80% {res['decision']['interval80']}), "
              f"{len(res['evidence'])} evidence, {res['runtime_ms']:.0f} ms{'  [error: ' + res['error'][:60] + ']' if res['error'] else ''}")
    dt = time.time() - t0
    print(f"{len(files)} docs in {dt:.2f}s ({len(files)/max(dt,1e-9):.1f} docs/s), {n_err} with errors")


if __name__ == "__main__":
    main()
