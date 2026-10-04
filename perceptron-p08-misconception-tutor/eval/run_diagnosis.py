"""Diagnosis eval on real Eedi data (+ one synthetic identifiability check).

Run:  .venv/bin/python -m eval.run_diagnosis --llm-n 60
Out:  eval/results/diagnosis.json
A. Open-set (real): 4,370 Kaggle-2024 Eedi question/distractor pairs -> rank 2,587 misconceptions.
   Leakage-free split: questions hashed into test (20%) / train; unsupervised rankers use no training data.
B. MVP closed-set (real): Eedi distractors labelled with the misconceptions linked to our 5 categories.
   Executable reproduction (parse the LaTeX expression, run the bug programs, match the distractor),
   TF-IDF, LLM zero-shot, and hybrid (executable when it reproduces, else LLM).
C. Identifiability (synthetic): share of single-bug wrong answers that are uniquely attributable on
   uniform-random items vs on our discriminative items.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random
import re
from collections import Counter

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer

from architecture.contracts import GenerationRequest
from components.bugs.school_math import CODES, EEDI_LINKS, MISCONCEPTIONS, canon, mid, parse_dsl, predictions, safe_eval
from components.generator import TemplateGenerator, item_bank
from components.normalizer import NORMALIZER

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / ".data", pathlib.Path(__file__).parent / "results"
LLM_MODEL = "openai/gpt-4.1-mini"


def split_query(qtext: str) -> tuple[str, str, str]:
    m = re.match(r"### Question:(.*?)### Correct:(.*?)### Incorrect:(.*)", qtext, re.S)
    return tuple(x.strip() for x in m.groups()) if m else (qtext, "", "")  # type: ignore[return-value]


def ap_at(ranked: list[int], gold: int, k: int = 25) -> float:
    for i, r in enumerate(ranked[:k]):
        if r == gold:
            return 1.0 / (i + 1)
    return 0.0


def rank_metrics(score_rows: np.ndarray, golds: list[int], ids: np.ndarray) -> dict:
    top = np.argsort(-score_rows, axis=1)[:, :25]
    ranked = [[int(ids[j]) for j in row] for row in top]
    return {"MAP@25": float(np.mean([ap_at(r, g) for r, g in zip(ranked, golds)])),
            "Recall@25": float(np.mean([g in r for r, g in zip(ranked, golds)])),
            "Acc@1": float(np.mean([r[0] == g for r, g in zip(ranked, golds)])), "n": len(golds)}


def part_a(q: pd.DataFrame, c: pd.DataFrame) -> dict:
    tok = lambda s: re.findall(r"[a-z0-9]+", s.lower())
    q = q.copy()
    q["question"] = q["query"].map(lambda s: split_query(s)[0])
    q["test"] = q["question"].map(lambda s: int(hashlib.md5(s.encode()).hexdigest(), 16) % 5 == 0)
    te, tr = q[q.test], q[~q.test]
    ids, docs = c.id_.to_numpy(), c.text.tolist()
    golds = te.mid.tolist()
    res = {"n_test": len(te), "n_train": len(tr), "n_test_questions": te.question.nunique(),
           "test_misconceptions_unseen_in_train": float(np.mean([g not in set(tr.mid) for g in golds]))}
    bm = BM25Okapi([tok(d) for d in docs])
    res["bm25"] = rank_metrics(np.vstack([bm.get_scores(tok(s)) for s in te["query"]]), golds, ids)
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1).fit(docs + tr["query"].tolist())
    D, Qte, Qtr = vec.transform(docs), vec.transform(te["query"]), vec.transform(tr["query"])
    s_doc = (Qte @ D.T).toarray()
    res["tfidf"] = rank_metrics(s_doc, golds, ids)
    sim = (Qte @ Qtr.T).toarray()
    pos = {m: i for i, m in enumerate(ids)}
    s_knn = np.zeros_like(s_doc)
    trm = tr.mid.to_numpy()
    for j in range(sim.shape[1]):
        s_knn[:, pos[trm[j]]] = np.maximum(s_knn[:, pos[trm[j]]], sim[:, j])
    res["knn_train_labels"] = rank_metrics(s_knn, golds, ids)
    res["tfidf+knn"] = rank_metrics(s_doc + s_knn, golds, ids)
    return res


LATEX = [(r"\\left|\\right", ""), (r"\\times", "×"), (r"\\div", "÷"), (r"\\cdot", "×"), (r"\{\s*\}", ""),
         (r"\^\{\s*2\s*\}", "²"), (r"\^\s*2", "²")]


def latex_to_dsl(s: str) -> str:
    s = re.sub(r"\\[dt]?frac\s*\{\s*(\d+)\s*\}\s*\{\s*(\d+)\s*\}", r"\1/\2", s)
    for a, b in LATEX:
        s = re.sub(a, b, s)
    s = s.replace("−", "-").replace("\\", "").strip()
    s = re.sub(r"\(\s*-\s*(\d+(?:/\d+)?)\s*\)", r"(−\1)", s)
    s = re.sub(r"(^|[+×÷*/(])\s*-\s*(\d+)", r"\1(−\2)", s)  # leading/inner unary minus -> bracketed negative
    return s.replace("-", "−")


def math_segments(text: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r"\\[\(\[](.*?)\\[\)\]]", text, re.S)]


def executable_match(question: str, correct: str, incorrect: str):
    """Return (parsed, key_agrees, matched_codes) for the first parseable expression in the question."""
    wrong = NORMALIZER.normalize(latex_to_dsl(" ".join(math_segments(incorrect)) or incorrect).replace("−", "-")).value
    corr = NORMALIZER.normalize(latex_to_dsl(" ".join(math_segments(correct)) or correct).replace("−", "-")).value
    for seg in math_segments(question):
        try:
            toks = parse_dsl(latex_to_dsl(seg))
        except SyntaxError:
            continue
        key = safe_eval(toks)
        if key is None:
            continue
        preds = predictions(toks)
        matched = [cd for cd, v in preds.items() if v is not None and wrong is not None and canon(v) == wrong]
        return True, (corr == canon(key)), matched
    return False, False, []


def part_b(q: pd.DataFrame, llm_n: int) -> dict:
    link = {i: cd for cd in CODES for i in EEDI_LINKS[cd]["kaggle2024"]}
    q = q.copy()
    q["code"] = q.mid.map(link)
    pos = q[q.code.notna()]
    parts = pos["query"].map(split_query)
    rows = []
    for (qi, (question, correct, incorrect)), code in zip(parts.items(), pos.code):
        parsed, key_ok, matched = executable_match(question, correct, incorrect)
        rows.append({"qid": str(pos.loc[qi, "qid"]), "code": code, "parsed": parsed, "key_agrees": key_ok, "matched": matched,
                     "query": pos.loc[qi, "query"]})
    # negatives: arithmetic distractors labelled with other misconceptions -> false-claim rate
    rng = random.Random(0)
    neg_rows = []
    for qi in rng.sample(list(q[q.code.isna()].index), len(q[q.code.isna()])):
        question, correct, incorrect = split_query(q.loc[qi, "query"])
        parsed, key_ok, matched = executable_match(question, correct, incorrect)
        if parsed and key_ok:
            neg_rows.append({"mid": int(q.loc[qi, "mid"]), "name": q.loc[qi, "misconception_name"], "matched": matched})
    texts = {cd: f"{MISCONCEPTIONS[cd].name}. {MISCONCEPTIONS[cd].description} " + " ".join(EEDI_LINKS[cd]["kaggle2024"].values()) for cd in CODES}
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit(list(texts.values()) + [r["query"] for r in rows])
    S = (vec.transform([r["query"] for r in rows]) @ vec.transform(list(texts.values())).T).toarray()
    for r, srow in zip(rows, S):
        r["tfidf"] = CODES[int(np.argmax(srow))]
    llm_stats = {"calls": 0, "stopped_early": None}
    if llm_n:
        from components import llm

        prompt = ("A student answered a maths question incorrectly. Decide which ONE misconception most likely produced this exact wrong answer.\n\n"
                  "{q}\n\nMisconceptions:\n" + "\n".join(f"- {cd}: {MISCONCEPTIONS[cd].name}. {MISCONCEPTIONS[cd].description}" for cd in CODES)
                  + '\n\nReply with JSON only: {{"code": "<one code from the list>"}}')
        for r in rows[:llm_n]:
            try:
                txt = llm.chat([{"role": "user", "content": prompt.format(q=r["query"])}], model=LLM_MODEL, json_mode=True, max_tokens=30)
                r["llm"] = str(json.loads(txt).get("code", "")).strip()
                llm_stats["calls"] += 1
            except llm.RateLimited as exc:
                llm_stats["stopped_early"] = str(exc)
                break
            except (json.JSONDecodeError, AttributeError):
                r["llm"] = None
                llm_stats["calls"] += 1
    for r in rows:
        exe = r["matched"][0] if len(r["matched"]) == 1 else None
        r["hybrid"] = exe or r.get("llm")
    n = len(rows)
    acc = lambda key, sub: (sum(r.get(key) == r["code"] for r in sub) / len(sub)) if sub else None
    with_llm = [r for r in rows if "llm" in r]
    res = {
        "n_positive": n, "per_code_n": dict(Counter(r["code"] for r in rows)),
        "exec_parsed_rate": sum(r["parsed"] for r in rows) / n,
        "exec_key_agrees_rate_given_parsed": sum(r["key_agrees"] for r in rows if r["parsed"]) / max(1, sum(r["parsed"] for r in rows)),
        "exec_reproduced_rate": sum(r["code"] in r["matched"] for r in rows) / n,
        "exec_reproduced_rate_given_parsed": sum(r["code"] in r["matched"] for r in rows if r["parsed"]) / max(1, sum(r["parsed"] for r in rows)),
        "exec_wrong_attribution": sum(bool(r["matched"]) and r["code"] not in r["matched"] for r in rows) / n,
        "tfidf_acc": acc("tfidf", rows),
        "llm_acc": acc("llm", with_llm), "llm_n": len(with_llm),
        "hybrid_acc": acc("hybrid", with_llm), "tfidf_acc_on_llm_subset": acc("tfidf", with_llm),
        "negatives_parsed_with_key_agreement": len(neg_rows),
        "negatives_false_claim_rate": (sum(bool(r["matched"]) for r in neg_rows) / len(neg_rows)) if neg_rows else None,
        "negatives_false_claims": [r for r in neg_rows if r["matched"]][:15],
        "llm": llm_stats,
        "rows": [{k: v for k, v in r.items() if k != "query"} for r in rows],
    }
    return res


def part_c(n: int = 400) -> dict:
    bank = item_bank(n, seed=11)
    gen = TemplateGenerator()
    disc = []
    for i, cd in enumerate(CODES):
        disc += gen.generate(GenerationRequest(target_misconception_id=mid(cd), competitor_ids=[mid(x) for x in CODES if x != cd],
                                               n=n // len(CODES), seed=100 + i, as_mcq=False))

    def unique_share(items):
        tot = uniq = 0
        for g in items:
            vals = [p.value for p in g.predicted if p.value is not None]
            cnt = Counter(vals)
            tot += len(vals)
            uniq += sum(1 for v in vals if cnt[v] == 1)
        return uniq / max(1, tot), tot

    u_bank, t_bank = unique_share(bank)
    u_disc, t_disc = unique_share(disc)
    return {"random_items": {"n_items": len(bank), "bug_errors": t_bank, "uniquely_attributable": u_bank},
            "discriminative_items": {"n_items": len(disc), "bug_errors": t_disc, "uniquely_attributable": u_disc}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm-n", type=int, default=60)
    a = ap.parse_args()
    q = pd.read_parquet(DATA / "eedi2024/queries_w_rels.parquet")
    c = pd.read_parquet(DATA / "eedi2024/corpus.parquet")
    res = {"command": f"python -m eval.run_diagnosis --llm-n {a.llm_n}", "A_open_set": part_a(q, c),
           "B_mvp_closed_set": part_b(q, a.llm_n), "C_identifiability_synthetic": part_c()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "diagnosis.json").write_text(json.dumps(res, indent=1, default=str))
    A, B = res["A_open_set"], res["B_mvp_closed_set"]
    print(json.dumps({k: v for k, v in A.items()}, indent=None))
    print(json.dumps({k: v for k, v in B.items() if k not in ("rows", "negatives_false_claims")}, indent=None))
    print(json.dumps(res["C_identifiability_synthetic"]))


if __name__ == "__main__":
    main()
