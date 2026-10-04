"""Render every results-derived table and number-bearing sentence in research/components/twin.md and the
README headline from results/metrics.json + results/analysis.json, so the write-up cannot drift from the
committed runs. Blocks live between <!-- twin_sim.report:NAME --> and <!-- /twin_sim.report:NAME -->.

Run:   cd innovatex-t3-coastal-plastic/components && python -m twin_sim.report           # rewrite blocks
Check: python -m twin_sim.report --check     # exit 1 if any block is stale (tests call check())
Also prints the deck-statement checks (a)-(d)."""
from __future__ import annotations

import json
import sys

from ._paths import PKG, RESULTS, SLUG

DOC = SLUG / "research" / "components" / "twin.md"
README = PKG / "README.md"
NAMES = {"P0": "P0 assumed fixed roster", "P1": "P1 fill-fraction-ranked fixed-shift rule",
         "P2": "P2 mass/risk-ranked, tide- and forecast-timed", "P1m": "P1m sensor-only mass-ranked",
         "P2_notide": "P2_notide", "P2_nofc": "P2_nofc"}
ISOLATES = [("P1m_vs_P1", "mass vs fill-fraction ranking (sensor-only, fixed shift)"),
            ("P1m_vs_P0", "sensor-only mass ranking vs assumed fixed roster"),
            ("P2_vs_P1m", "everything P2 adds beyond mass-ranked sensors"),
            ("P2_vs_P2_notide", "tide-aware timing, within P2"),
            ("P2_vs_P2_nofc", "forecast terms, within P2"),
            ("P2_nofc_vs_P1m", "tide timing on top of mass ranking, no forecasts"),
            ("P2_notide_vs_P1m", "forecast/risk terms without timing"),
            ("P2_vs_P1", "the complete policy comparison")]
FUSE = [("a_current_release", "(a) current release"), ("b_fail_open_fuse", "(b) fuse"),
        ("c_fuse_refloat_x0.5", "(c) fuse + re-float × 0.5"), ("c_fuse_refloat_x0.2", "(c) fuse + re-float × 0.2")]


def _neg(s: str) -> str:
    return s.replace("-", "−")


def sp(v, nd=1):          # signed percent of a fraction
    return _neg(f"{v * 100:+.{nd}f}%")


def up(v, nd=1):          # unsigned percent of a fraction
    return f"{v * 100:.{nd}f}%"


def upx(v):               # percent with extra decimals for tiny shares
    return f"{v * 100:.2f}%" if v * 100 < 1 else f"{v * 100:.1f}%"


def pp(v):
    return _neg(f"{v:+.1f}")


def rs(d, f=sp):
    return f"[{f(d['p05'])}, {f(d['p95'])}]"


def kg(x):
    return f"{x:,.0f}"


def tn(x):
    return f"{x / 1e3:,.1f}"


def med_rng(d, f):
    return f"{f(d['median'])} [{f(d['p05'])}–{f(d['p95'])}]"


def excludes0(d) -> bool:
    return d["p05"] > 0 or d["p95"] < 0


def table(header: list, rows: list) -> str:
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
                     + ["| " + " | ".join(r) + " |" for r in rows])


def deck_checks(an: dict) -> dict:
    ab = an["ablations"]["paired_escaped_rel_diff"]
    es = an["escape_split"]
    ent = {p: es[p]["by_cause"]["entrainment"]["share_of_escaped"]["median"] for p in ("P0", "P1", "P2")}
    return {
        "a_full_policy_vs_fill_rule_clears_zero": excludes0(ab["P2_vs_P1"]),
        "b_tide_alone_includes_zero": not excludes0(ab["P2_vs_P2_notide"]),
        "b_forecasts_alone_include_zero": not excludes0(ab["P2_vs_P2_nofc"]),
        "b_kg_ranking_alone_includes_zero": not excludes0(ab["P1m_vs_P1"]),
        "c_P2_vs_P0_crosses_zero": not excludes0(an["paired_escaped_rel_diff"]["P2_vs_P0"]),
        "d_entrainment_dominant": all(v > 0.5 for v in ent.values()),
        "d_entrainment_share_of_escaped_median": {p: round(v, 3) for p, v in ent.items()},
    }


def doc_blocks(m: dict, an: dict) -> dict:
    H, T = m["heldout_2024_2025"], m["tuning_2019_2023"]
    es, pr, fw = an["escape_split"], an["paired_escaped_rel_diff"], an["fwce"]
    ab = an["ablations"]
    abp, fs = ab["paired_escaped_rel_diff"], an["fuse_sensitivity_P2"]
    sp7, ex, ang, mb = an["entrainment_split"], an["exposure_P2_nominal"], an["boom_angle_sensitivity_P2"], an["mass_boundary"]
    b = {}
    b["heldout_meta"] = (f"**Held-out Jun–Sep 2024 + 2025** (`results/metrics.json`). Crew-hours: "
                         f"{H['P0']['crew_hours']:,.0f} per policy. Load median {H['P0']['load_kg_median'] / 1e3:,.0f} t. "
                         f"Bypass {H['P0']['bypass_site_hours_median']:g} site-hours (median; policy-independent).")
    rows = [[NAMES["P0"], f"{kg(H['P0']['escaped_kg_median'])} ({kg(H['P0']['escaped_kg_p05'])}–{kg(H['P0']['escaped_kg_p95'])})",
             "—", "—", f"{H['P0']['captured_fraction_median']:.3f}", kg(H['P0']['cleared_kg_median']),
             f"{H['P0']['overflow_site_hours_median']:g}"]]
    for p in ("P1", "P2"):
        h = H[p]
        rows.append([NAMES[p], f"{kg(h['escaped_kg_median'])} ({kg(h['escaped_kg_p05'])}–{kg(h['escaped_kg_p95'])})",
                     f"**{sp(h['reduction_vs_P0_median'])}** [{sp(h['reduction_vs_P0_p05'])}, {sp(h['reduction_vs_P0_p95'])}]",
                     f"{h['draws_better_than_P0']}/40", f"{h['captured_fraction_median']:.3f}", kg(h["cleared_kg_median"]),
                     f"{h['overflow_site_hours_median']:g}"])
    b["heldout"] = table(["policy", "escaped kg, median (p05–p95)", "reduction vs P0, median [central 90% scenario range]",
                          "parameter settings (of 40) better than P0", "captured fraction", "cleared kg",
                          "overflow site-hours"], rows)
    b["tuning_line"] = (f"Tuning years 2019–2023, same 40 sampled parameter settings: P1 {sp(T['P1']['reduction_vs_P0_median'])} "
                        f"[{sp(T['P1']['reduction_vs_P0_p05'])}, {sp(T['P1']['reduction_vs_P0_p95'])}]; P2 "
                        f"{sp(T['P2']['reduction_vs_P0_median'])} [{sp(T['P2']['reduction_vs_P0_p05'])}, "
                        f"{sp(T['P2']['reduction_vs_P0_p95'])}], better than P0 in {T['P2']['draws_better_than_P0']} of 40 "
                        f"parameter settings.")
    clr = [ab["cleared_share_of_unique_input"][p]["median"] * 100 for p in ("P0", "P1", "P2")]
    levers = {"mass ranking (P1m vs P1)": abp["P1m_vs_P1"], "tide-aware timing (P2 vs P2_notide)": abp["P2_vs_P2_notide"],
              "day-ahead forecasts (P2 vs P2_nofc)": abp["P2_vs_P2_nofc"]}
    big = min(levers, key=lambda k: levers[k]["median"])
    excl = [k for k, v in levers.items() if excludes0(v)]
    comp = ("Each component's central 90% scenario range includes zero." if not excl
            else "Components whose range excludes zero: " + "; ".join(excl) + ".")
    full = abp["P2_vs_P1"]
    fulls = (f"The complete P2-vs-P1 comparison ({sp(full['median'])} {rs(full)}) "
             + ("excludes zero." if excludes0(full) else "also includes zero."))
    p1m0, p10, p20 = abp["P1m_vs_P0"], pr["P1_vs_P0"], pr["P2_vs_P0"]
    p1m_word = ("about level with the roster" if not excludes0(p1m0)
                else "better than the roster" if p1m0["median"] < 0 else "worse than the roster")
    b["reading"] = "\n".join([
        f"1. In this twin, crews are capacity-bound: they clear about {min(clr):.0f}–{max(clr):.0f}% of the unique input. "
        f"P2's full gain over P1 splits into mass ranking instead of fill fraction ({sp(abp['P1m_vs_P1']['median'])}, "
        f"P1m vs P1) and everything else P2 adds ({sp(abp['P2_vs_P1m']['median'])}, P2 vs P1m). Within P2, tide-aware "
        f"timing gives {sp(abp['P2_vs_P2_notide']['median'])} (vs P2_notide) and day-ahead forecasts "
        f"{sp(abp['P2_vs_P2_nofc']['median'])} (vs P2_nofc). The largest single lever by median is {big}. {comp} {fulls}",
        f"2. Fill-**fraction** ranking (P1) is {'worse' if p10['median'] > 0 else 'not worse'} than the assumed fixed roster "
        f"({sp(p10['median'])} {rs(p10)}), because it sends crews to small booms that look full but hold little mass. A "
        f"sensor-only **mass**-ranked rule (P1m) is {p1m_word}: {sp(p1m0['median'])} {rs(p1m0)}. The roster is itself "
        f"mass-aware, since one crew is at the largest site every day.",
        ("3. The P2 gain vs P0 is uncertain: its central 90% scenario range includes zero "
         f"({sp(p20['median'])} {rs(p20)}). Treat it as a design direction, not a demonstrated saving."
         if not excludes0(p20) else
         f"3. P2 vs P0 is {sp(p20['median'])} {rs(p20)}; the range excludes zero in this SIMULATED twin.")])
    cause = lambda w: f"{kg(w['kg']['median'])} [{kg(w['kg']['p05'])}–{kg(w['kg']['p95'])}]; {up(w['share_of_escaped']['median'])} / {up(w['share_of_arrived']['median'])}"  # noqa: E731
    b["causes"] = table(["policy", "entrainment", "overtopping", "bypass / release", "escaped total"],
                        [[p] + [cause(es[p]["by_cause"][c]) for c in ("entrainment", "overtopping", "bypass_release")]
                         + [med_rng(es[p]["escaped_kg"], kg)] for p in ("P0", "P1", "P2")])
    ent = [es[p]["by_cause"]["entrainment"]["share_of_escaped"] for p in ("P0", "P1", "P2")]
    b["causes_note"] = (f"The central 90% scenario ranges of the shares are in the JSON. For entrainment's share of escaped "
                        f"they span about [{min(e['p05'] for e in ent) * 100:.0f}–{max(e['p95'] for e in ent) * 100:.0f}%]. "
                        f"The P2 figure ({up(ent[2]['median'])}) is the P2 scenario with the current release behaviour and "
                        f"the boom normal to the flow (θ = 90°). \"Entrainment\" here includes the assumed slack-water floor "
                        f"(1 − e_max); §7 splits it.")
    rf = {p: es[p]["refloated_kg"] for p in ("P0", "P1", "P2")}
    b["refloat"] = (f"- Tidal re-float: " + ", ".join(
        f"{p} {kg(rf[p]['tidal_refloat']['median'])} kg ({up(rf[p]['tidal_refloat_share_of_arrived']['median'])} of arrived)"
        for p in rf) + ".\n- Flood release: " + ", ".join(kg(rf[p]["flood_release"]["median"]) for p in rf)
        + " kg respectively (P0, P1, P2).")
    b["paired"] = table(["comparison", "median", "central 90% scenario range",
                         "parameter settings (of 40) where the first is lower"],
                        [[lab, sp(pr[k]["median"]), rs(pr[k]), str(pr[k]["draws_a_lower"])] for k, lab in
                         (("P2_vs_P1", "P2 vs P1"), ("P2_vs_P0", "P2 vs P0 (matches §4)"), ("P1_vs_P0", "P1 vs P0"))])
    b["fwce"] = table(["policy", "FWCE", "for comparison: gross captured ÷ arrived"],
                      [[p, med_rng(fw[p]["fwce"], up), up(fw[p]["gross_captured_over_arrived"]["median"])]
                       for p in ("P0", "P1", "P2")])
    frows = []
    for v, lab in FUSE:
        f = fs[v]
        a = v == "a_current_release"
        frows.append([lab, med_rng(f["escaped_kg"], kg),
                      "—" if a else f"{sp(f['escaped_rel_vs_a']['median'])} {rs(f['escaped_rel_vs_a'])}",
                      "—" if a else str(f["escaped_rel_vs_a"]["draws_a_lower"]), med_rng(f["fwce"], up),
                      "—" if a else f"{pp(f['fwce_delta_pp_vs_a']['median'])} {rs(f['fwce_delta_pp_vs_a'], pp)}"])
    b["fuse"] = table(["variant", "escaped kg", "Δ escaped vs (a), paired", "settings (of 40) lower than (a)", "FWCE",
                       "Δ FWCE vs (a), pp"], frows)
    fb = fs["b_fail_open_fuse"]["escaped_rel_vs_a"]["median"]
    ov = [fs[v]["by_cause_kg"]["overtopping"]["median"] for v in ("a_current_release", "c_fuse_refloat_x0.5",
                                                                     "c_fuse_refloat_x0.2")]
    b["s6_caveats"] = "\n".join([
        "- **Circularity.** escaped_kg is computed by the same assumed process model that the policies act on. These "
        "results show relative value under the stated assumptions; they are not field evidence. Field calibration "
        "comes in Round 2.",
        "- **The cause split is set by assumptions.**",
        "  - \"Entrainment\" means every non-captured arrival outside bypass hours. That includes the (1 − e_max) share "
        "assumed to pass under the boom even at slack water.",
        "  - Overtopping depends on the assumed boom capacity and debris bulk density.",
        (f"- **The fuse {'matters little' if abs(fb) < 0.01 else 'matters'} here** ({sp(fb)} median). Release is "
         f"{'rare' if H['P0']['bypass_site_hours_median'] < 50 else 'frequent'}: on the ERA5 0.25° rain scale there are "
         f"{H['P0']['bypass_site_hours_median']:g} bypass site-hours in 2024–2025 (median). With gauge-scale rain peaks "
         f"the fuse could matter more (UNTESTED)."),
        (f"- **The pocket rows scale the assumed tidal re-float rate** (k_refloat 0.01–0.08 /h). Keeping more catch "
         f"changes overtopping (P2 median {tn(ov[0])} t → {tn(ov[1])} t → {tn(ov[2])} t), and the net figures above "
         f"include this."),
        "- **Still omitted from the twin:** travel time between sites, minimum clearance duration, gated (flap-gate) "
        "outfalls and a perfect-foresight oracle policy. Boom angle is covered only as a sensitivity (§7)."])
    srow = lambda w: f"{tn(w['kg']['median'])} t; {up(w['share_of_escaped']['median'])} [{w['share_of_escaped']['p05'] * 100:.1f}–{w['share_of_escaped']['p95'] * 100:.1f}]"  # noqa: E731
    b["split"] = table(["policy", "slack-water floor (1 − e_max)·arrived: kg; share of escaped",
                        "velocity-driven (e_max − e)·arrived: kg; share of escaped"],
                       [[p, srow(sp7[p]["floor_1_minus_emax"]), srow(sp7[p]["velocity_driven"])] for p in ("P0", "P1", "P2")])
    fl, vl = sp7["P2"]["floor_1_minus_emax"]["share_of_escaped"]["median"], sp7["P2"]["velocity_driven"]["share_of_escaped"]["median"]
    b["split_summary"] = (f"In this twin, {up(fl)} of what escapes (P2, median) is the assumed floor: items assumed to pass "
                          f"under the boom even at slack water (e_max 0.70–0.95, an ASSUMPTION). Velocity-driven entrainment "
                          f"is {up(vl)}. The deck should not present the {up(ent[2]['median'])} entrainment share as "
                          f"velocity entrainment.")
    b["exposure"] = table(["θ", "share of site-hours", "share of arrived kg"],
                          [[f"{a}°" + (" (current)" if a == 90 else ""), upx(ex[f"theta{a}"]["share_of_hours"]),
                            upx(ex[f"theta{a}"]["share_of_arrived_kg"])] for a in (90, 45, 30, 20)])
    short = {"mithi_mahim": "Mithi", "oshiwara_malad": "Oshiwara", "dahisar_mouth": "Dahisar", "trombay_mahul": "Trombay"}
    e90 = ex["theta90"]
    b["exposure_sites"] = ("By site at 90° (hours / kg): " + ", ".join(
        f"{short[k]} {up(v['share_of_hours'])} / {up(v['share_of_arrived_kg'])}" for k, v in e90["by_site"].items())
        + ". Velocity loss is not confined to |v| > v50: the assumed logistic curve already loses about 12% of e_max at "
        f"v50 − 2w, so the velocity-driven share of escape ({up(vl)}) is "
        + ("larger" if vl > e90["share_of_arrived_kg"] else "not larger")
        + f" than the exposure share of arrived kg ({up(e90['share_of_arrived_kg'])}).")
    arows = []
    for h, lab in (("a_current_release", "(a) current release"), ("c_fuse_refloat_x0.5", "(c) fuse + re-float ×0.5")):
        for a in (90, 45, 30, 20):
            g = ang[h][f"theta{a}"]
            base90 = a == 90
            vs_cur = ("—" if (h == "a_current_release" and base90) else
                      sp(g["escaped_rel_vs_current_a_theta90"]["median"]) if h == "a_current_release" else
                      f"{sp(g['escaped_rel_vs_current_a_theta90']['median'])} {rs(g['escaped_rel_vs_current_a_theta90'])}")
            arows.append([lab if base90 else "", f"{a}°", med_rng(g["escaped_kg"], tn),
                          "—" if base90 else f"{sp(g['escaped_rel_vs_theta90']['median'])} {rs(g['escaped_rel_vs_theta90'])}",
                          "—" if base90 else str(g["escaped_rel_vs_theta90"]["draws_a_lower"]), vs_cur,
                          med_rng(g["fwce"], up),
                          "—" if base90 else f"{pp(g['fwce_delta_pp_vs_theta90']['median'])} {rs(g['fwce_delta_pp_vs_theta90'], pp)}",
                          up(g["velocity_entrainment_share_of_escaped"]["median"])])
    b["angle"] = table(["hardware", "θ", "escaped (t)", "Δ escaped vs θ = 90°", "settings (of 40) lower",
                        "Δ escaped vs current boom (a, θ = 90°)", "FWCE", "Δ FWCE vs θ = 90° (pp)",
                        "velocity share of escaped"], arows)
    r45 = ang["a_current_release"]["theta45"]["escaped_rel_vs_theta90"]["median"]
    r20 = ang["a_current_release"]["theta20"]["escaped_rel_vs_theta90"]["median"]
    most = r20 < 0 and r45 / r20 >= 0.5
    b["s7_caveats"] = "\n".join([
        "- **Not independent confirmation.** Angle acts only through the same assumed capture curve e(|v|·sin θ). Its "
        "benefit is the velocity-driven share by construction, so it cannot confirm that mechanism.",
        "- **v50 is borrowed.** It is transferred from oil-boom practice (UNVERIFIED ASSUMPTION, 0.30–0.70 m/s).",
        (f"- **{'Diminishing returns' if most else 'Returns keep growing'}.** {sp(r45)} at 45° vs {sp(r20)} at 20° "
         f"(median, current hardware). Boom length grows as 1/sin θ (×1.41 at 45°, ×2 at 30°, ×2.92 at 20°). Capacity, "
         f"cost and mooring loads are held fixed or not modelled, and P2's forecaster still assumes θ = 90°."),
        "- **The floor is untouched.** The slack-water floor does not change with angle or dispatch. Testing e_max at "
        "slack water is the first field experiment.",
        "- **Circularity** (§6) applies."])
    b["ablations"] = table(["comparison", "isolates", "median", "central 90% scenario range",
                            "settings (of 40) where the first is lower"],
                           [[k.replace("_vs_", " vs "), lab, sp(abp[k]["median"]), rs(abp[k]), str(abp[k]["draws_a_lower"])]
                            for k, lab in ISOLATES])
    b["ablation_policies"] = table(["policy", "escaped (t)", "FWCE", "cleared share of unique input"],
                                   [[NAMES[n], med_rng(ab["escaped_kg"][n], tn), up(ab["fwce"][n]["median"]),
                                     up(ab["cleared_share_of_unique_input"][n]["median"])]
                                    for n in ("P0", "P1", "P1m", "P2_notide", "P2_nofc", "P2")])
    tide = abp["P2_vs_P2_notide"]
    b["claims"] = "\n".join([
        f"- The complete P2 policy vs the fill-fraction rule: {sp(full['median'])} {rs(full)}, lower in "
        f"{full['draws_a_lower']} of 40 settings; the range {'excludes' if excludes0(full) else 'includes'} zero.",
        f"- Against the assumed roster: {sp(p20['median'])} {rs(p20)}; the range "
        f"{'excludes zero' if excludes0(p20) else 'includes zero, so this is uncertain'}.",
        f"- The largest single held-out lever by median is {big}. Tide timing within P2: {sp(tide['median'])} {rs(tide)}, "
        f"lower in {tide['draws_a_lower']} of 40 settings; "
        + ("**not separately established** (range includes zero)." if not excludes0(tide) else "its range excludes zero."),
        f"- Sensors alone vs the assumed roster: ranked by fraction {sp(p10['median'])} {rs(p10)}, by mass "
        f"{sp(p1m0['median'])} {rs(p1m0)}. This may differ with more sites or a roster that is not mass-aware (UNTESTED)."])
    b["boundary"] = table(["policy", "unique input (t)", "cleared = removal (t)", "stored at 30 Sep = temporary retention (t)",
                           "held upstream at 30 Sep (t)", "escaped (t)"],
                          [[p] + [med_rng(mb[p][k], tn) for k in ("unique_input_kg", "cleared_kg", "stored_at_season_end_kg",
                                                                  "held_upstream_at_season_end_kg", "escaped_kg")]
                           for p in ("P0", "P1", "P2")])
    cs, ret = mb["P2"]["cleared_share"]["median"], mb["P2"]["retained_share"]["median"]
    b["boundary_notes"] = "\n".join([
        f"- FWCE (§6) = (cleared + stored) ÷ unique input. For P2 that is {up(cs)} removal plus {up(ret)} retention"
        + (", so FWCE here is almost entirely crew removal." if ret < 0.05 * (cs + ret) else "."),
        "- Removal is not final diversion. What happens to cleared material (sorting, recycling, landfill) is outside "
        "the twin.",
        "- Each monsoon starts with an empty boom and empty upstream pool. This is an ASSUMPTION: pre-monsoon clearance.",
        "- The twin's mass is generic floating debris, scaled from the brief's city-wide plastic figure. It is not "
        "specific to flexible packaging, and there is no moisture correction; the wet bulk density is used only for "
        "boom volume."])
    return b


def readme_blocks(m: dict) -> dict:
    H = m["heldout_2024_2025"]
    return {
        "headline": table(["policy", "median reduction", "central 90% scenario range",
                           "parameter settings (of 40) better than P0"],
                          [[{"P1": "P1 fill-fraction-ranked fixed-shift rule",
                             "P2": "P2 mass/risk-ranked, tide- and forecast-timed policy"}[p],
                            sp(H[p]["reduction_vs_P0_median"]),
                            f"[{sp(H[p]['reduction_vs_P0_p05'])}, {sp(H[p]['reduction_vs_P0_p95'])}]",
                            f"{H[p]['draws_better_than_P0']}/40"] for p in ("P1", "P2")]),
        "headline_note": (f"Captured fraction: " + ", ".join(f"{p} {H[p]['captured_fraction_median']:.3f}" for p in H)
                          + ". Tide: frozen UTide fit on 2022-11-23..2023-12-31 only (no held-out-year sea level); "
                          "see twin.md §1 and §4."),
    }


ANCHORS = {
    "twin.md": {"heldout_meta": "**Held-out Jun–Sep 2024 + 2025**", "heldout": "| policy | escaped kg, median (p05–p95)",
                "tuning_line": "Tuning years 2019–2023, same 40", "reading": "1. In this twin, crews are capacity-bound",
                "causes": "| policy | entrainment | overtopping |", "causes_note": "The central 90% scenario ranges of the shares",
                "refloat": "- Tidal re-float: P0", "paired": "| comparison | median | central 90% scenario range |",
                "fwce": "| policy | FWCE | for comparison", "fuse": "| variant | escaped kg | Δ escaped vs (a)",
                "s6_caveats": "- **Circularity.** escaped_kg is computed", "split": "| policy | slack-water floor",
                "split_summary": "About half of what escapes in this twin", "exposure": "| θ | share of site-hours",
                "exposure_sites": "By site at 90° (hours / kg):", "angle": "| hardware | θ | escaped (t)",
                "s7_caveats": "- **Not independent confirmation.**", "ablations": "| comparison | isolates | median",
                "ablation_policies": "| policy | escaped (t) | FWCE | cleared share", "claims": "- The complete P2 policy lets",
                "boundary": "| policy | unique input (t)", "boundary_notes": "- FWCE (§6) = (cleared + stored)"},
    "README.md": {"headline": "| policy | median reduction | central 90% scenario range",
                  "headline_note": "Captured fraction: P0"},
}


def put(text: str, name: str, body: str, anchor: str | None) -> str:
    a, z = f"<!-- twin_sim.report:{name} -->", f"<!-- /twin_sim.report:{name} -->"
    if a in text:
        i, j = text.index(a) + len(a), text.index(z)
        return text[:i] + "\n\n" + body + "\n\n" + text[j:]
    lines = text.split("\n")
    hits = [k for k, ln in enumerate(lines) if anchor and ln.startswith(anchor)]
    if len(hits) != 1:
        raise ValueError(f"block {name}: anchor found {len(hits)} times and no markers")
    k1 = hits[0]
    while k1 < len(lines) and lines[k1].strip():
        k1 += 1
    lines[hits[0]:k1] = [a, "", body, "", z]
    return "\n".join(lines)


def apply(check: bool = False) -> list:
    m = json.loads((RESULTS / "metrics.json").read_text())
    an = json.loads((RESULTS / "analysis.json").read_text())
    stale = []
    for path, blocks in ((DOC, doc_blocks(m, an)), (README, readme_blocks(m))):
        old = path.read_text()
        new = old
        for name, body in blocks.items():
            new = put(new, name, body, ANCHORS[path.name].get(name))
        if new != old:
            stale.append(path.name)
            if not check:
                path.write_text(new)
    return stale


def main():
    check = "--check" in sys.argv
    stale = apply(check)
    an = json.loads((RESULTS / "analysis.json").read_text())
    print(json.dumps(deck_checks(an)))
    print(("stale: " + ", ".join(stale)) if stale else "docs in sync")
    if check and stale:
        sys.exit(1)


if __name__ == "__main__":
    main()
