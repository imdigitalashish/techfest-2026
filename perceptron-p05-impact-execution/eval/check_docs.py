"""Doc-drift check: every number quoted in the deliverables must trace to eval/results/.

Fails (exit 1) if:
 1. eval/results/claims.json is stale vs claims recomputed from eval/results/ files;
 2. a rendered document differs from its template rendered with the current claims;
 3. a template contains a result-like literal (decimal, %, ×) that is not a {{placeholder}}
    and not in ALLOW (literature values and fixed facts, each with a reason);
 4. the Round-1 abstract body is outside 600–900 words.
Usage: .venv/bin/python eval/check_docs.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "eval"))
from claims import compute  # noqa: E402
from render_docs import DOCS, PH, render, target_text  # noqa: E402

RESULT_LIKE = re.compile(r"(?<![\w.{])[-+−]?\d[\d,]*\.\d+(?:\s?[%×x])?|(?<![\w.{])\d+(?:\.\d+)?\s?[%×]")
ALLOW = [  # (regex, reason)
    (r"\b\d{4}\.\d{4,5}\b", "arXiv identifier"),
    (r"(?<=δ ≈ )0\.5|(?<=δ = )0\.489|(?<=⟨δ⟩ = )0\.489", "literature value (Sato & Kanazawa 2025; arXiv:2607.04280)"),
    (r"(?<=Python )3\.11", "software version"),
    (r"(?<=PRL )135|(?<=PRL 135, )257401", "citation"),
    (r"600–900", "rubric word limit"),
]


def untraced(text):
    body = PH.sub(" ", text)
    allowed = []
    for rx, _ in ALLOW:
        allowed += [m.span() for m in re.finditer(rx, body)]
    bad = []
    for m in RESULT_LIKE.finditer(body):
        if not any(a <= m.start() < b for a, b in allowed):
            line = body[:m.start()].count("\n") + 1
            bad.append(f"line {line}: '{m.group(0)}'")
    return bad


def main():
    fails = []
    claims, missing = compute()
    if missing:
        fails.append(f"missing result sources: {missing}")
    cj = os.path.join(ROOT, "eval", "results", "claims.json")
    if not os.path.exists(cj) or json.load(open(cj)) != claims:
        fails.append("eval/results/claims.json is stale: run eval/render_docs.py")
    for tpl, tgt, markers in DOCS:
        tp = os.path.join(ROOT, tpl)
        if not os.path.exists(tp):
            fails.append(f"template missing: {tpl}")
            continue
        t = open(tp).read()
        try:
            want = render(t, claims)
        except KeyError as e:
            fails.append(f"{tpl}: {e}")
            continue
        have = target_text(open(os.path.join(ROOT, tgt)).read(), markers)
        if (have.strip("\n") if markers else have) != (want.strip("\n") if markers else want):
            fails.append(f"{tgt}: drifted from {tpl} rendered with current claims (run eval/render_docs.py)")
        for b in untraced(t):
            fails.append(f"{tpl}: untraced result-like number {b}")
        if tgt.endswith("round1-abstract.md"):
            body = want.split("**Title:**", 1)[1] if "**Title:**" in want else want
            n = len(re.findall(r"\S+", body))
            if not 600 <= n <= 900:
                fails.append(f"abstract body has {n} words (must be 600–900)")
            else:
                print(f"abstract body: {n} words")
    n_ph = sum(len(PH.findall(open(os.path.join(ROOT, t)).read())) for t, _, _ in DOCS if os.path.exists(os.path.join(ROOT, t)))
    if fails:
        print("CHECK_DOCS FAILED:\n- " + "\n- ".join(fails))
        sys.exit(1)
    print(f"CHECK_DOCS OK: {len(claims)} claims, {n_ph} placeholders, no drift, no untraced numbers")


if __name__ == "__main__":
    main()
