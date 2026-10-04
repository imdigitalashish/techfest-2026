"""C8 Runner: assess every document in a folder, offline; one Assessment JSON per input.

Usage (from apctt-trl-assessor/):
  python -m components.skeleton.runner --train            # fit the v0 model on the TechPort train split
  python -m components.skeleton.runner --in DIR --out DIR [--rule median]
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from . import decode, doctype, emit, evidence, gap, ingest, ordinal

SUFFIXES = {".txt", ".md", ".pdf", ".html", ".htm", ".xml"}


def assess(path: Path, model: ordinal.Model, rule: str, schema: dict) -> dict:
    t0 = time.perf_counter()
    doc = ingest.parse(path)
    dt = doctype.classify(doc)
    ev = evidence.extract(doc)
    text = " \n".join(s["text"] for s in doc["sections"])
    dist = model.predict(text)
    dec = decode.decide(dist, rule=rule, n_chars=doc["n_chars"])
    ga = gap.analyse(dec, dist, ev)
    a = emit.assemble(doc, dt, dec, dist, ev, ga, 1000 * (time.perf_counter() - t0),
                      {"pipeline": "skeleton-v0", "model": dist["model_id"], "rubric": "eu_annex_g+nasa_v0"},
                      error=None if doc["n_chars"] else f"no text extracted ({doc['parser']})")
    errs = emit.check_assessment(a, schema)
    if errs:
        raise ValueError(f"{path.name}: schema violations: {errs[:5]}")
    return a


def network_off() -> None:
    """Fail loudly if anything tries to use the network (offline guarantee for the dry run)."""
    import socket

    def _blocked(*_a, **_k):
        raise RuntimeError("network access attempted while --offline")

    socket.socket.connect = _blocked  # type: ignore[method-assign]
    socket.create_connection = _blocked  # type: ignore[assignment]
    socket.getaddrinfo = _blocked  # type: ignore[assignment]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp"); ap.add_argument("--out"); ap.add_argument("--rule", default="median")
    ap.add_argument("--train", action="store_true"); ap.add_argument("--offline", action="store_true"); ap.add_argument("--model", default=str(ordinal.DEFAULT_MODEL))
    a = ap.parse_args()
    if a.offline:
        network_off()
    if a.train:
        t0 = time.time(); out = ordinal.train(out=Path(a.model)); print(f"trained -> {out} in {time.time()-t0:.1f}s")
        if not a.inp:
            return
    model, schema = ordinal.Model(Path(a.model)), emit.load_schema()
    files = sorted(p for p in Path(a.inp).iterdir() if p.suffix.lower() in SUFFIXES)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for f in files:
        res = assess(f, model, a.rule, schema)
        (Path(a.out) / f"{f.stem}.assessment.json").write_text(json.dumps(res, indent=1))
        print(f"{f.name}: TRL {res['decision']['trl']} (80% {res['decision']['interval80']}), "
              f"{len(res['evidence'])} evidence, {res['runtime_ms']:.0f} ms")
    dt = time.time() - t0
    print(f"{len(files)} docs in {dt:.2f}s ({len(files)/max(dt,1e-9):.1f} docs/s)")


if __name__ == "__main__":
    main()
