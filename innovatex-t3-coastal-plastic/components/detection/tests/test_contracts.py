"""Contract tests for C5/C6 outputs against architecture/contracts/contracts.py.

    cd components/detection && python3.11 -m pytest -q tests
Output-file tests skip if the file has not been produced yet; logic tests always run (no GPU, no weights).
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pytest

from t3det._contracts import FluxEstimate, FrameDetections, Provenance
from t3det.flux import SAIGON_VISUAL_COUNT, CountingLine, LineCrossingCounter, MassModel, count_error_pct
from t3det.paths import RESULTS, SPLITS

METRICS = RESULTS / "metrics.json"
SAMPLES = RESULTS / "sample_detections.json"
FLUX = RESULTS / "flux_synthetic.json"


def _need(p: Path):
    if not p.exists():
        pytest.skip(f"{p.name} not produced yet")
    return json.loads(p.read_text())


def test_sample_detections_match_contract():
    frames = [FrameDetections.model_validate(f) for f in _need(SAMPLES)]
    assert 1 <= len(frames) <= 5
    for f in frames:
        w, h = f.image_wh
        assert f.model_id and f.latency_ms is not None and f.latency_ms > 0
        for d in f.detections:
            x1, y1, x2, y2 = d.bbox_xyxy
            assert 0 <= x1 < x2 <= w + 1 and 0 <= y1 < y2 <= h + 1
            assert 0 <= d.score <= 1 and d.label == "litter"


def test_sample_images_small():
    imgs = list((RESULTS / "samples").glob("*.jpg"))
    if not imgs:
        pytest.skip("no sample images yet")
    assert len(imgs) <= 5 and all(p.stat().st_size <= 200_000 for p in imgs)


def test_metrics_json_shape():
    m = _need(METRICS)
    for k in ("dataset", "split", "n_test_images", "mAP50", "mAP50_95", "precision", "recall", "per_class",
              "latency_ms_mps", "model_id", "reproduce"):
        assert k in m, k
    assert m["n_test_images"] == len((SPLITS / "test.txt").read_text().split())
    for k in ("mAP50", "mAP50_95", "precision", "recall"):
        assert 0 <= m[k] <= 1
    assert m["mAP50_95"] <= m["mAP50"]
    assert "litter" in m["per_class"]


def test_flux_output_matches_contract():
    f = _need(FLUX)
    est = FluxEstimate.model_validate(f["flux_estimate"])
    assert f["label"] == "SYNTHETIC" and est.provenance.kind == "synthetic"
    assert est.items_crossed == f["items_crossed"]
    lo, hi = est.est_kg_ci90
    assert lo <= est.est_kg <= hi
    assert math.isclose(f["count_error_pct"], count_error_pct(f["items_crossed"], f["gt_crossings"]), abs_tol=0.01)


def test_splits_disjoint_and_grouped():
    s = {k: set((SPLITS / f"{k}.txt").read_text().split()) for k in ("train", "val", "test")}
    assert not (s["train"] & s["val"]) and not (s["train"] & s["test"]) and not (s["val"] & s["test"])
    exp = {k: {n.split("_")[0] for n in v} for k, v in s.items()}
    assert not (exp["train"] & exp["test"]) and not (exp["val"] & exp["test"]) and not (exp["train"] & exp["val"])


def test_line_crossing_counts_each_track_once():
    c = LineCrossingCounter(CountingLine((100, 0), (100, 200)))
    for x in (80, 95, 105, 98, 110, 120):  # jitter around the line must count once
        c.update(1, x, 50)
    for x in (150, 140):  # never crosses
        c.update(2, x, 60)
    c.update(3, 90, 10)
    c.update(3, 110, 10)
    assert c.count == 2 and c.by_label["litter"] == 2


def test_direction_filter():
    c = LineCrossingCounter(CountingLine((100, 0), (100, 200)), direction=-1)
    c.update(1, 90, 50)
    c.update(1, 110, 50)  # left -> right: side +1 -> -1, matches direction -1 -> counted
    c.update(2, 110, 50)
    c.update(2, 90, 50)  # right -> left: side -1 -> +1 -> rejected
    assert c.count == 1 and 1 in c.counted


def test_mass_model_ci():
    est, (lo, hi) = SAIGON_VISUAL_COUNT.kg(100)
    assert math.isclose(est, 1.9) and lo < est < hi and lo >= 0
    assert MassModel(10, 0, "assumption", "x").kg(3) == (0.03, (0.03, 0.03))


def test_flux_estimate_constructs():
    est = FluxEstimate(site_id="s", t_start=datetime(2026, 10, 4, tzinfo=timezone.utc),
                       t_end=datetime(2026, 10, 4, 0, 1, tzinfo=timezone.utc), items_crossed=3, items_per_min=3.0,
                       by_label={"litter": 3}, est_kg=0.057, est_kg_ci90=(0.0, 0.16), method="test",
                       provenance=Provenance(kind="synthetic", source="test"))
    assert est.items_crossed == 3
