from __future__ import annotations

from datetime import date
from typing import Iterable

import numpy as np
import pandas as pd
from architecture.contracts.fln_contracts import ChildDiagnosis, MasteryEstimate, Subject
from components.canonical import pseudonymise

READ_CODES = ["L.LETTER", "L.WORD", "L.PARA", "L.STORY"]
MATH_CODES = ["M.NUM1_9", "M.NUM11_99", "M.SUB", "M.DIV"]


def _codes(subject: str) -> list[str]:
    return READ_CODES if subject == "language" else MATH_CODES


def _goal_level(subject: str) -> int:
    return 4 if subject == "language" else 3


def aser_rule(student_raw_id: str, udise_code: str, grade: int, subject: str, responses: pd.DataFrame, item_bank: pd.DataFrame, salt: str = "demo", as_of: date | None = None) -> ChildDiagnosis:
    rb = responses.merge(item_bank[["item_id", "level", "competency_code"]], on="item_id")
    rb = rb[(rb.student_raw_id == student_raw_id) & (rb.subject == subject)]
    level = 0
    mastery = []
    for lvl, code in enumerate(_codes(subject), start=1):
        scores = rb[rb.level == lvl].score
        p = float(scores.mean()) if len(scores) else 0.0
        mastery.append(MasteryEstimate(competency_code=code, p_mastery=p, n_items=int(len(scores))))
        if len(scores) and p >= 0.75:
            level = lvl
    return ChildDiagnosis(student=pseudonymise(student_raw_id, salt), udise_code=udise_code, grade=grade, subject=Subject(subject), level=level,
                          level_confidence=1.0, mastery=mastery, next_competency=_next_comp(level, subject),
                          meets_grade_goal=float(level >= _goal_level(subject)), method="aser_rule", as_of=as_of or date.today())


def _posterior(resp: pd.DataFrame, bank: pd.DataFrame, grid: np.ndarray) -> np.ndarray:
    logp = -0.5 * grid**2
    merged = resp.merge(bank[["item_id", "irt_a", "irt_b"]], on="item_id")
    for _, r in merged.iterrows():
        p = 1 / (1 + np.exp(-float(r.irt_a) * (grid - float(r.irt_b))))
        p = np.clip(p, 1e-6, 1 - 1e-6)
        logp += float(r.score) * np.log(p) + (1 - float(r.score)) * np.log(1 - p)
    post = np.exp(logp - logp.max())
    return post / post.sum()


def _level_probs(post: np.ndarray, grid: np.ndarray, thresholds: Iterable[float]) -> np.ndarray:
    bins = np.digitize(grid, np.array(list(thresholds), dtype=float))
    return np.array([post[bins == i].sum() for i in range(5)])


def _next_comp(level: int, subject: str) -> str | None:
    codes = _codes(subject)
    return codes[level] if level < 4 else None


def bayes_irt(student_raw_id: str, udise_code: str, grade: int, subject: str, responses: pd.DataFrame, item_bank: pd.DataFrame,
              thresholds: Iterable[float], salt: str = "demo", as_of: date | None = None, method: str = "bayes_irt") -> ChildDiagnosis:
    grid = np.linspace(-4, 4, 321)
    resp = responses[(responses.student_raw_id == student_raw_id) & (responses.subject == subject)]
    bank = item_bank[item_bank.subject == subject]
    post = _posterior(resp, bank, grid)
    probs = _level_probs(post, grid, thresholds)
    level = int(probs.argmax())
    codes = _codes(subject)
    mastery = []
    for lvl, code in enumerate(codes, start=1):
        mastery.append(MasteryEstimate(competency_code=code, p_mastery=float(probs[lvl:].sum()), n_items=int((resp.item_id.isin(bank[bank.level == lvl].item_id)).sum())))
    return ChildDiagnosis(student=pseudonymise(student_raw_id, salt), udise_code=udise_code, grade=grade, subject=Subject(subject), level=level,
                          level_confidence=float(probs[level]), mastery=mastery, next_competency=_next_comp(level, subject),
                          meets_grade_goal=float(probs[_goal_level(subject):].sum()), method=method, as_of=as_of or date.today())


def adaptive_test(student_raw_id: str, udise_code: str, grade: int, subject: str, full_responses: pd.DataFrame, item_bank: pd.DataFrame,
                  thresholds: Iterable[float], max_items: int = 8, salt: str = "demo", as_of: date | None = None) -> tuple[ChildDiagnosis, list[str]]:
    grid = np.linspace(-4, 4, 321)
    bank = item_bank[item_bank.subject == subject].copy().reset_index(drop=True)
    available = set(bank.item_id)
    used: list[str] = []
    administered = []
    post = np.exp(-0.5 * grid**2); post /= post.sum()
    truth_resp = full_responses[(full_responses.student_raw_id == student_raw_id) & (full_responses.subject == subject)]
    truth = dict(zip(truth_resp.item_id, truth_resp.score))
    for _ in range(max_items):
        mean = float((grid * post).sum())
        cand = bank[bank.item_id.isin(available)].copy()
        cand["info"] = cand.apply(
            lambda r: (float(r.irt_a) ** 2)
            * (p := 1 / (1 + np.exp(-float(r.irt_a) * (mean - float(r.irt_b)))))
            * (1 - p),
            axis=1,
        )
        item = str(cand.sort_values("info", ascending=False).iloc[0].item_id)
        available.remove(item); used.append(item)
        administered.append({"student_raw_id": student_raw_id, "udise_code": udise_code, "grade": grade, "item_id": item, "subject": subject, "score": float(truth[item])})
        resp_df = pd.DataFrame(administered)
        post = _posterior(resp_df, bank, grid)
        if _level_probs(post, grid, thresholds).max() >= 0.90 or not available:
            break
    diag = bayes_irt(student_raw_id, udise_code, grade, subject, pd.DataFrame(administered), item_bank, thresholds, salt, as_of, method="adaptive_bayes_irt")
    return diag, used
