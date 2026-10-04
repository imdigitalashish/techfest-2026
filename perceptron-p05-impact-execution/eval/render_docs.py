"""Render documents from templates with numbers from eval/claims.py (the only source of quoted numbers).

Templates use {{claim_id}} placeholders. Usage: .venv/bin/python eval/render_docs.py
Also writes eval/results/claims.json. Check without writing: eval/check_docs.py.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "eval"))
from claims import compute  # noqa: E402

MEMO = ("<!-- memo:begin (rendered from deliverables/selection-memo.template.md; edit the template) -->",
        "<!-- memo:end -->")
DOCS = [("deliverables/round1-abstract.template.md", "deliverables/round1-abstract.md", None),
        ("deliverables/architecture.template.md", "deliverables/architecture.md", None),
        ("deliverables/selection-memo.template.md", "thought_node.md", MEMO)]
PH = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")


def render(text, claims):
    missing = sorted({m for m in PH.findall(text) if m not in claims})
    if missing:
        raise KeyError(f"claims missing for placeholders: {missing}")
    return PH.sub(lambda m: claims[m.group(1)], text)


def target_text(full, markers):
    if markers is None:
        return full
    b, e = full.index(markers[0]) + len(markers[0]), full.index(markers[1])
    return full[b:e]


def write_target(path, rendered, markers):
    if markers is None:
        open(path, "w").write(rendered)
        return
    full = open(path).read()
    b, e = full.index(markers[0]) + len(markers[0]), full.index(markers[1])
    open(path, "w").write(full[:b] + rendered + full[e:])


def main():
    claims, missing = compute()
    if missing:
        print("WARNING missing sources:", missing)
    json.dump(claims, open(os.path.join(ROOT, "eval", "results", "claims.json"), "w"), indent=1, sort_keys=True)
    staged = []
    for tpl, tgt, markers in DOCS:        # render everything first; write only if all succeed (review sol #1)
        tp = os.path.join(ROOT, tpl)
        if not os.path.exists(tp):
            print("skip (no template):", tpl)
            continue
        r = render(open(tp).read(), claims)
        staged.append((tgt, "\n" + r.strip("\n") + "\n" if markers else r, markers))
    for tgt, text, markers in staged:
        write_target(os.path.join(ROOT, tgt), text, markers)
        print("rendered", tgt)


if __name__ == "__main__":
    main()
