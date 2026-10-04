"""Headless assertions for the P4 demo (called by demo/smoke.sh). Exits non-zero on the first failed group."""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

DEMO = Path(__file__).resolve().parent
ROOT = DEMO.parent
ER = ROOT / "eval" / "results"
FAIL: list[str] = []
TOL = 1e-9


def check(cond: bool, msg: str) -> None:
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


def max_list_len(o, skip=()) -> int:
    if isinstance(o, dict):
        return max([max_list_len(v, skip) for k, v in o.items() if k not in skip] or [0])
    if isinstance(o, list):
        return max([len(o)] + [max_list_len(v, skip) for v in o])
    return 0


def html_text() -> str:
    return (DEMO / "index.html").read_text()


DURATION_KEYS = {"bin_s", "wall_s", "runtime_s"}
FORBIDDEN_KEYS = {"alarm_s", "alarm_utc", "alarms", "alarm_times", "first_delay_min"}


def temporal_violations(o, path: str = "") -> list[str]:
    """Licence (Tardis ToS 9.2): market-derived timing must be aggregated at >= 10 minutes. Flags any forbidden
    per-event timing key, and any time-of-day value (keys ending in _s / _utc_s) that is not on a 600-s boundary."""
    bad = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k in FORBIDDEN_KEYS:
                bad.append(f"{path}/{k}")
            elif (k.endswith("_s") or k.endswith("utc_s")) and k not in DURATION_KEYS and isinstance(v, (int, float)) \
                    and not isinstance(v, bool) and v % 600:
                bad.append(f"{path}/{k}={v}")
            else:
                bad += temporal_violations(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o[:3]):
            bad += temporal_violations(v, f"{path}[{i}]")
    return bad


def series_lengths_ok(d: dict) -> bool:
    """Every per-bin series has exactly n_bins entries at bin_s >= 600."""
    nb, ok = d["n_bins"], d["bin_s"] >= 600
    for rec in list(d.get("policies", {}).values()) + list(d.get("stops", {}).values()):
        ok &= len(rec["loss_bins"]) == nb
        ab = rec.get("alarm_bins")
        for arr in (ab.values() if isinstance(ab, dict) else [ab] if ab is not None else []):
            ok &= len(arr) == nb
    ok &= len(d["candles"]) == nb and all(len(r) == nb for r in d["regime_share"])
    return bool(ok)


def main() -> int:
    hold = json.loads((ER / "v2_holdout.json").read_text())
    abl = json.loads((ER / "v2_holdout_posthoc_ablation.json").read_text())
    days = hold["meta"]["eval_days"]

    print("[1] committed sweep: present, expected keys, anchors over all 22 held-out days")
    sw = json.loads((DEMO / "results" / "alarm_dial_sweep.json").read_text())
    for k in ("status", "meta", "separation", "null_train", "holdout_windows", "refs", "stops"):
        check(k in sw, f"sweep has key '{k}'")
    S = {s["id"]: s for s in sw["stops"]}
    check(set(sw["meta"]["days"]) == set(days) and len(days) == 22, "sweep covers exactly the 22 held-out days")
    anchors = [("naive_3", hold["per_day"]["ks_refit"], "α = 1e-3 == committed ks_refit"),
               ("off", abl["per_day"]["static_enorm"], "off (α = 0) == committed static_enorm"),
               ("cal_0.999", hold["per_day"]["ksc_refit"], "calibrated q = 0.999 == committed ksc_refit")]
    for sid, com, label in anchors:
        bad = [d for d in days if abs(S[sid]["per_day"][d]["logloss"] - com[d]["logloss"]) > TOL]
        check(not bad, f"{label} on 22/22 days" + (f" (mismatch: {bad})" if bad else ""))
    for r in ("static_snorm", "regime_gated"):
        bad = [d for d in days if abs(sw["refs"][r]["per_day"][d] - hold["per_day"][r][d]["logloss"]) > TOL]
        check(not bad, f"sweep reference {r} == committed per-day log-loss on 22/22 days")
    bad = [d for d in days if S["naive_3"]["per_day"][d]["n_alarms"] != hold["per_day"]["ks_refit"][d]["alarms_by_detector"].get("rolling_ks", 0)]
    check(not bad, "α = 1e-3 alarm counts == committed ks_refit alarm counts on 22/22 days")
    dc_c, dc_s = hold["summary"]["ks_refit"]["vs_static_snorm"]["day_cluster"], S["naive_3"]["vs_static_snorm"]
    check(abs(dc_c["mean"] - dc_s["mean"]) < TOL and all(abs(a - b) < 1e-6 for a, b in zip(dc_c["ci97.5"], dc_s["ci97.5"])),
          f"α = 1e-3 22-day Δ vs static and 97.5% CI == committed ({dc_s['mean']:+.4f} [{dc_s['ci97.5'][0]:+.4f}, {dc_s['ci97.5'][1]:+.4f}])")
    m, n = sw["separation"]["m"], sw["separation"]["n_ref"]
    exact = (math.log(2) - (math.lgamma(m + n + 1) - math.lgamma(m + 1) - math.lgamma(n + 1))) / math.log(10)
    check(abs(exact - sw["separation"]["log10_prob"]) < 1e-9, f"exact D=1 probability 10^{exact:.1f} recomputed")
    for s in sw["stops"]:
        if s["kind"] == "naive":
            check(s["below_separation"] == (s["log10_alpha"] < exact), f"below-separation flag correct for {s['id']}") if s["log10_alpha"] in (-200, -250) else None
    gate_beaten = [s["id"] for s in sw["stops"] if s["vs_regime_gated"]["mean"] < 0]
    print(f"  info dial stops whose 22-day mean beats the regime gate: {gate_beaten or 'none'}")

    print("[2] scoreboard export == committed results")
    r = subprocess.run([sys.executable, str(DEMO / "build_scoreboard.py")], capture_output=True, text=True)
    check(r.returncode == 0, "build_scoreboard.py runs")
    diff = subprocess.run(["git", "diff", "--quiet", "--", str(DEMO / "results" / "scoreboard.json")], cwd=ROOT)
    check(diff.returncode == 0, "regenerated demo/results/scoreboard.json is identical to the committed file")
    sb = json.loads((DEMO / "results" / "scoreboard.json").read_text())
    rows = {x["policy"]: x for x in sb["rows"]}
    check(abs(rows["regime_gated"]["vs_static"]["mean"] - (-0.0099)) < 5e-5, "regime gate Δ vs static = -0.0099")
    check(abs(rows["static_enorm"]["vs_regime_gated"]["mean"] - 0.0083) < 5e-5, "one EWMA head vs gate = +0.0083")
    check(sb["head_usage"]["low"] == 20.7 and sb["head_usage"]["high"] == 46.0, "head usage 20.7/33.2/46.0 parsed")

    print("[3] live replay cache: live-computed == committed")
    for rd in sb["replay_days"]:
        d = rd["day"]
        p = DEMO / ".cache" / f"replay_{d}.json"
        check(p.exists(), f"replay cache for {d} built")
        if not p.exists():
            continue
        rp = json.loads(p.read_text())
        if d in days:
            for pol, rec in rp["policies"].items():
                check(rec.get("match") is True, f"{d} {pol}: live {rec['logloss']:.9f} == committed {rec.get('committed', float('nan')):.9f}")
            bad = [st for st, rec in rp["stops"].items() if rec.get("match") is not True]
            check(not bad, f"{d}: all {len(rp['stops'])} dial stops live == committed sweep" + (f" (bad: {bad})" if bad else ""))
        else:
            check(all("committed" not in rec for rec in rp["policies"].values()), f"{d} is a dev day: no held-out claim attached")
        check(rp["bin_s"] >= 600 and rp["n_bins"] <= 145, f"{d}: time series binned at >= 10 min ({rp['n_bins']} bins)")
        longest = max_list_len(rp)
        check(longest <= 145, f"{d}: no series longer than one value per 10 minutes (longest {longest})")
        tv = temporal_violations(rp)
        check(not tv, f"{d}: no sub-10-minute event timing (alarms are 10-minute counts)" + (f" {tv[:3]}" if tv else ""))
        check(series_lengths_ok(rp), f"{d}: every series (losses, alarm counts, candles, heads) has one value per 10-min bin")

    print("[4] licence: committed demo outputs are aggregates only")
    tracked = subprocess.run(["git", "ls-files", "demo"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    check(not [t for t in tracked if ".cache" in t or ".data" in t], "no cache or data files tracked under demo/")
    big = [t for t in tracked if (ROOT / t).exists() and (ROOT / t).stat().st_size > 5_000_000]
    check(not big, "no tracked demo file > 5 MB")
    for t in tracked:
        if t.endswith(".json"):
            o = json.loads((ROOT / t).read_text())
            check(max_list_len(o) <= 200, f"{t}: no per-second arrays")
            tv = temporal_violations(o)
            check(not tv, f"{t}: no sub-10-minute timing fields" + (f" {tv[:3]}" if tv else ""))

    print("[6] Act 2 splice (SEMI-SYNTHETIC): integrity checks")
    si = DEMO / ".cache" / "splice_index.json"
    check(si.exists(), "splice index built")
    if si.exists():
        idx = json.loads(si.read_text())
        check(idx.get("status") == "SEMI-SYNTHETIC" and len(idx["splices"]) == 10, "10 splices, labelled SEMI-SYNTHETIC")
        for sp in idx["splices"]:
            d = json.loads((DEMO / ".cache" / sp["file"]).read_text())
            c = d["checks"]
            check(d["status"] == "SEMI-SYNTHETIC" and c["causal_features_pre"] and c["causal_labels_pre"],
                  f"{sp['file']}: features and labels before the splice == unspliced day A")
            check(c["labels_shift_invariant_post"] and c["n_post_labels_compared"] > 20000 and c["n_post_unmatched"] <= 1,
                  f"{sp['file']}: labels after the splice == day B's own labels on every real move "
                  f"(additive shift {d['shift_ticks']} ticks; {c['n_post_labels_compared']} steps)")
            check(c["n_float_noise_ties_flipped"] <= 2, f"{sp['file']}: float-noise ties flipped = {c['n_float_noise_ties_flipped']} (<= 2)")
            check(max_list_len(d) <= 145 and series_lengths_ok(d) and not temporal_violations(d),
                  f"{sp['file']}: 10-minute aggregates only (no event times; alarm counts per bin)")
    for needle in ('id="splice"', "SEMI-SYNTHETIC", "additively"):
        check(needle in html_text(), f"index.html contains {needle!r}")

    print("[7] fallback deck = the talk-track story order (capture_fallback.py)")
    import importlib.util
    spec = importlib.util.spec_from_file_location("cf", DEMO / "capture_fallback.py")
    cf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cf)
    deck = [x[0] for x in cf.DECK]
    have = sorted(p.name for p in (DEMO / "fallback").glob("*.png"))
    check(have == sorted(deck), f"fallback/ holds exactly the {len(deck)} deck images")
    script = (DEMO / "SCRIPT.md").read_text()
    main_deck = [n for n in deck if n[0].isdigit()]
    pos = [script.find(n.split("_")[0] + "_") for n in main_deck]
    check(all(p_ >= 0 for p_ in pos) and pos == sorted(pos), "SCRIPT.md cites the main deck in story order")

    print("[5] page references every panel and data file")
    html = (DEMO / "index.html").read_text()
    for needle in ('id="scoreboard"', 'id="replay"', 'id="dial"', 'id="exec"', 'id="sweep"', 'id="why"', 'id="rp"',
                   'id="dial-range"', "results/scoreboard.json", "results/alarm_dial_sweep.json", ".cache/replay_",
                   ".cache/status.json", "Not tradable as a taker after fees", "optimistic", "other eleven",
                   "live-computed", "post-hoc demo sweep", "pre-registered primary", "never beats the state gate",
                   "not a ground-truth false-alarm rate", "does not mean refitting helps"):
        check(needle in html, f"index.html contains {needle!r}")
    for banned in ("The i.i.d. null is the problem", "No setting of the dial", "at any sensitivity"):
        check(banned not in html and banned not in (DEMO / "SCRIPT.md").read_text(), f"overshooting wording absent: {banned!r}")
    check("http://" not in html.replace("http://127.0.0.1", "") and "https://" not in html, "index.html loads nothing from the network")
    print()
    if FAIL:
        print(f"SMOKE FAILED: {len(FAIL)} check(s)")
        return 1
    print("SMOKE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
