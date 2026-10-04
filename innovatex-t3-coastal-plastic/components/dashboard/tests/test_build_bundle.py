import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

import build_bundle
from mrv_ledger import chain
from mrv_ledger._contracts import DashboardBundle

JS = Path(build_bundle.HERE) / "site" / "ledger_verify.js"
NOW = datetime(2026, 10, 4, 0, 30, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    r = build_bundle.build(mock=True, out_site=out, now=NOW)
    return out, r


def test_bundle_validates_and_files_written(built):
    out, r = built
    b = DashboardBundle.model_validate_json((out / "dashboard_bundle.json").read_text())
    assert len(b.sites) == 5 and b.ledger and b.forecasts and b.plans and b.telemetry
    assert (out / "data.js").read_text().startswith("window.DASHBOARD_BUNDLE=")
    aux = json.loads((out / "aux.json").read_text())
    assert chain.verify(b.ledger, aux["anchor"]).ok
    keys = aux["key_registry"]
    assert chain.verify_signatures(b.ledger, aux["signatures"], keys).ok


def test_mock_is_labelled_synthetic_everywhere(built):
    b = built[1]["bundle"]
    assert b.disclaimers[0].startswith("SYNTHETIC MOCK")
    kinds = {f.rain_provenance.kind for f in b.forcing} | {f.tide_provenance.kind for f in b.forcing}
    kinds |= {s.provenance.kind for s in b.interceptor} | {f.provenance.kind for f in b.forecasts}
    assert kinds == {"synthetic"}
    assert all(t.simulated for t in b.telemetry)
    assert all("(mock)" in s.name for s in b.sites)


def test_interceptor_mass_balance_holds(built):
    for s in built[1]["bundle"].interceptor:
        for i in range(len(s.t)):
            esc = s.escaped_entrainment_kg[i] + s.escaped_overtopping_kg[i] + s.escaped_bypass_kg[i]
            assert s.arrived_kg[i] == pytest.approx(s.captured_kg[i] + esc, abs=0.05)
            assert s.stored_kg[i] >= 0


def test_flatten_and_trim():
    f = build_bundle.flatten({"a": {"b": 1, "c": True}, "d": None, "e": [1, 2], "reproduce": "x"})
    assert f == {"a.b": 1.0, "a.c": 1.0, "d": "null", "e": "[1, 2]", "reproduce": "x"}
    part = {"forecasts": [{"site_id": "X", "horizon_h": 48, "issued_at": "2026-10-04T00:00:00Z"}], "telemetry": [],
            "forcing": [{"t": [f"2026-10-0{d}T00:00:00Z" for d in range(1, 8)], "rain_mm_h": list(range(7)), "tide_datum": "MSL"}]}
    s = build_bundle.trim(part, past_h=48)["forcing"][0]
    assert s["t"][0] == "2026-10-02T00:00:00Z" and s["rain_mm_h"] == [1, 2, 3, 4, 5] and s["tide_datum"] == "MSL"


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_browser_verifier_on_built_bundle(built, tmp_path):
    out = built[0]
    script = f"""
const L = require({json.dumps(str(JS))}); const b = require({json.dumps(str(out / 'dashboard_bundle.json'))});
const a = require({json.dumps(str(out / 'aux.json'))});
(async () => {{
  const ok = await L.verifyChain(b.ledger, a.anchor);
  const t = JSON.parse(JSON.stringify(b.ledger)); t[2].reconciliation.flag = 'ok'; t[2].record.claimed_wet_kg += 0.1;
  const bad = await L.verifyChain(t, a.anchor);
  const cut = await L.verifyChain(b.ledger.slice(0, -1), a.anchor);
  console.log(JSON.stringify({{ok: ok.ok, bad: bad.ok, badSeqs: bad.badSeqs, cut: cut.ok}}));
}})();"""
    r = json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)
    assert r == {"ok": True, "bad": False, "badSeqs": [2], "cut": False}
