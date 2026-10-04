# Pre-registration — where does the LLM baseline fail? (P8)

- **Registered:** 2026-10-04 15:21 IST — this file and `eval/run_llm_gaps.py` are committed together, *before any main-run API call*. The commit is the evidence of the time. Later changes are appended under *Deviations* with their own timestamps; registered text is never edited.
- **Author:** P8 lead (Claude Opus 5.5). **Requested by:** Supervisor, 14:58 IST, 4 Oct 2026.
- **What was known before registering:**
  - Earlier committed results (`eval/results/diagnosis.json`): gpt-4.1-mini zero-shot 86.0% vs executable→TF-IDF 45.7% on 129 real Eedi distractors, 5 categories, no NONE option.
  - Dry runs of this protocol (no API calls) revealed the executable side's own numbers. EXEC on real data: accuracy on P 0.1908, false-claim rate on N 0.0 (152 items). TRACER on synthetic learners: exact-set accuracy 0.64. INVERSION EXEC: 1.0 by construction.
  - **No LLM output for any item in this protocol had been seen.**

## 1. Question
On which inputs that matter to a tutor does an LLM misconception classifier fail, where an executable misconception library (or a hybrid of the two) does not? If no such gap exists for the strongest model tested, the memo says so plainly.

## 2. Parts, data and methods
Models (Azure OpenAI `tf26-p08-aoai-1004`, Global Standard, JSON mode, one query per item and model, 4 concurrent requests). The first stored response counts.

| Model | Version | Settings | Price in/out (USD per 1M tokens) |
|---|---|---|---|
| gpt-4.1-mini | 2025-04-14 | temperature 0, seed 0, max_tokens 300 | 0.40 / 1.60 |
| gpt-5.4-mini | 2026-03-17 | reasoning_effort medium, max_completion_tokens 8000 | 0.75 / 4.50 |
| gpt-5.5 | 2026-04-24 | reasoning_effort high, max_completion_tokens 16000 | 5.00 / 30.00 |

Price source: Azure Retail Prices API, serviceName 'Foundry Models', swedencentral, Global meters (gpt 4.1 mini Inp/Outp glbl; 5.4 mini Inp/Opt Gl; 5.5 ShortCo inp/opt Gl), accessed 2026-10-04. Reasoning tokens are assumed to be billed as output tokens (assumption).

### 2.1 `real_negatives` — REAL data (primary, decisive)
- **Data:** Kaggle "Eedi – Mining Misconceptions in Mathematics" (2024) training pairs via HF mirror `cdtmc/eedi-ir` (4,370 question/correct/distractor → misconception pairs). For each pair, `components/bugs/eedi_parse.py` (version in this commit) tries to parse an arithmetic expression from the question. **Evaluable** = parsed *and* our clean evaluation equals Eedi's correct answer.
- **Groups:**
  - **P (positives, n=131):** pairs labelled with one of the 8 Eedi ids linked to our 5 categories ([217, 1005, 1507, 1597, 1805, 2175, 2316, 2566]). Plus evaluable pairs labelled with an id in **S_equiv** = {1072: 'SQ_DOUBLE'} ("Multiplies by the index" equals doubling on a square), mapped to SQ_DOUBLE. Of these, 29 are evaluable.
  - **N (same-domain negatives, n=152):** evaluable pairs labelled with any other misconception, excluding S_related.
  - **S_related (n=21; sensitivity only):** evaluable pairs whose label is a close relative or special case of one of our rules, so a claim of the related code is arguably not false. The ids are {15: 'LTR', 328: 'LTR', 1862: 'LTR', 2532: 'LTR', 27: 'SQ_DOUBLE', 1282: 'SUB_NEG', 1400: 'NEG_TIMES_NEG', 172: 'FRAC_ADD', 1909: 'FRAC_ADD', 1980: 'FRAC_ADD', 907: 'FRAC_ADD'}: addition before division or multiplication, "order of operations does not affect the answer", doubling both parts when squaring a fraction, "subtracting a negative makes the answer negative", negative ÷ negative is negative, componentwise subtraction or multiplication of fractions, no common denominator. This list was fixed from the label *names* only.
- **Methods:**
  - **EXEC:** claim code c iff the item is evaluable and exactly one pack bug reproduces the distractor; otherwise NONE.
  - **LLM:m:** prompt P_REAL below.
  - **GATED:m:** EXEC on evaluable items, LLM:m on the rest.
  - **HYB:m (secondary):** EXEC if it claims, else LLM:m.

### 2.2 `inversion` — SYNTHETIC items (secondary)
- 180 items. Three target depths: L1 = 3 operators, L2 = 5–6, L3 = 7–8; actual counts after trigger injection are 1–4, 2–6 and 4–8 (means 2.7, 4.7, 6.7).
- Each depth has 20 items in each of three conditions:
  - *single:* one pack bug produced the answer;
  - *pair:* two bugs applied together;
  - *slip:* the answer is key + δ, δ ∈ {−10, −3, −2, −1, 1, 2, 3, 10}, and no subset of the 5 bugs reproduces it.
- Expressions are random over integers, negative literals, fraction literals and squares, with one injected trigger sub-expression per generating bug. They are kept only if the key is "nice" (denominator ≤ 60, |key| ≤ 1000) and the generating set is the **unique minimal** set of size 1–2 that reproduces the answer. So EXEC (enumerating subsets) is correct by construction. This part measures the LLM's error rate on an inversion task with a unique, machine-checkable answer.
- Pairs {SQ_DOUBLE, NEG_TIMES_NEG} on expressions with a squared negative are excluded, because the composition is ambiguous. Fraction literals are shown bracketed, e.g. (1/4). Seed 2026.

### 2.3 `tracing` — SYNTHETIC learners (secondary)
- **Learners:** 100 simulated learners (`components/simulator`, seed 2026). Each misconception is held with base rate 0.35 (at least 1; mean 1.75 held). Consistency ~ Beta(8,2); slip ~ U(0.03, 0.15).
- **Items:** each learner answers 12 items sampled from an untargeted item bank (`item_bank(300, seed=2026)`). No feedback, no learning.
- **TRACER:** the set-Bayes tracer with its default, untuned parameters (c=0.8, s=0.1, base 0.3), which differ from the simulator's per-learner parameters.
- **LLM:m:** prompt P_TRACE.
- **Caveat:** the simulator and the tracer share the generative family. This is a home-field advantage, so the result is an *upper bound* on the tracer's advantage.

### 2.4 gpt-5.5 subsets (cost)
- real_negatives: all items;
- inversion: L3 only (60 items);
- tracing: first 50 learners.

## 3. Metrics, hypotheses and decision rules
- **Statistics:** percentile bootstrap, 2,000 resamples, seed 0. Paired where methods share items; stratified over P and N for balanced accuracy.
- **Real:** acc_P; false-claim rate FCR_N (claims any code on N); balanced accuracy BA = (acc_P + 1 − FCR_N)/2; claim precision on P∪N; macro-F1 over the 6 labels; FCR and related-code rate on S_related.
- **Inversion:** exact-set accuracy (prediction = minimal generating set; [] for slips); slip false-attribution rate (claims a set on a slip item); claim consistency (the claimed set, executed, reproduces the answer).
- **Tracing:** exact-set accuracy (codes with p ≥ 0.5 = true held set); Brier over 5 codes; macro-F1.

| Id | Hypothesis | Decision rule ("gap" for model m) | Weight |
|---|---|---|---|
| H1 | LLM:m makes more false claims than EXEC on real same-domain negatives | 95% paired CI of FCR(LLM:m) − FCR(EXEC) on N lies above 0 (statistical gap). The gap is called *practical* if the point estimate is ≥ 0.05 | **primary** |
| H2 | The hybrid beats the LLM alone on real data | 95% stratified CI of BA(GATED:m) − BA(LLM:m) lies above 0 | **primary** |
| H3 | LLM:m cannot reliably invert deep expressions | 95% CI upper bound of exact-set accuracy at L3 < 0.95 | secondary (synthetic) |
| H4 | LLM:m attributes slips to misconceptions | 95% CI lower bound of slip false-attribution rate (all depths) > 0.05 | secondary (synthetic) |
| H5 | TRACER identifies held sets better than LLM:m | 95% paired CI of exact-set acc(TRACER) − acc(LLM:m) lies above 0 | secondary (synthetic) |
| H6 | TRACER is better calibrated than LLM:m | 95% paired CI of Brier(LLM:m) − Brier(TRACER) lies above 0 | secondary (synthetic) |

**What we will conclude:**
- **H1 or H2 holds for gpt-5.5** → "even the strongest model tested over-claims on real data; the executable path or the hybrid fixes it".
- **They hold only for smaller models** → "a gap against small/cheap models only". That is still relevant for an offline or low-cost tutor, but the claim is stated as such.
- **Neither H1 nor H2 holds for gpt-5.5** → the memo states plainly that *on real data we found no weakness of the strongest LLM that the executable approach fixes*. P8's remaining edge is then synthetic-only (H3–H6), cost, or latency, and it is scored accordingly.

## 4. Procedures fixed in advance
- **Invalid or empty responses:** retried once with double the token budget. If still invalid, then:
  - real → scored as NONE (no claim; conservative toward the LLM on H1);
  - inversion → scored wrong;
  - tracing → p = 0.5 for every code.
  - Invalid counts are reported.
- **Smoke tests:** `--limit 3` per part and model to check plumbing. Their stored responses are reused by the main run (same item, same prompt).
- **Spend cap:** USD 60 total estimated cost across all parts. Tokens and cost are logged per part and model.
- **Deviations:**
  - Any change to prompts, items, parsing or scoring after the first main-run call is appended below with a timestamp and reason.
  - All affected methods are re-scored.
  - No items are excluded after outputs are seen.
- **Reproduction without API calls:** `python -m eval.run_llm_gaps --part <part> --offline` re-scores from the committed `eval/results/llm_gaps_<part>_responses.jsonl`.

## 5. Prompts (verbatim from `eval/run_llm_gaps.py`)
P_REAL (`{query}` = the Eedi pair text `### Question … ### Correct … ### Incorrect …`):
```
A student answered a maths question incorrectly. Decide whether ONE of the five misconceptions below explains this exact wrong answer. If none of them explains it, answer NONE.

{query}

Misconceptions (each is a precise rule):
- LTR: evaluates +, −, ×, ÷ strictly from left to right, ignoring that × and ÷ come before + and − (brackets and squares are still done first).
- SQ_DOUBLE: computes x² as 2 × x.
- SUB_NEG: when a negative number written in the question is subtracted, computes a − (−n) as a − n.
- FRAC_ADD: when two fractions written in the question are added directly, computes a/b + c/d as (a + c)/(b + d).
- NEG_TIMES_NEG: when both factors are negative, gives a negative product: (−a) × (−b) = −ab and (−a)² = −a².
- NONE: none of the five explains this exact wrong answer (it comes from a different misconception or a careless slip).

Reply with JSON only: {"code": "<LTR|SQ_DOUBLE|SUB_NEG|FRAC_ADD|NEG_TIMES_NEG|NONE>"}
```
P_INV:
```
A student evaluated an arithmetic expression and got a wrong answer. The student may hold one or two of the five misconceptions below (applied consistently and together), or may have made a careless slip that none of them explains.

Expression: {expr}
Correct answer: {key}
Student's answer: {answer}

Misconceptions (each is a precise rule):
- LTR: evaluates +, −, ×, ÷ strictly from left to right, ignoring that × and ÷ come before + and − (brackets and squares are still done first).
- SQ_DOUBLE: computes x² as 2 × x.
- SUB_NEG: when a negative number written in the question is subtracted, computes a − (−n) as a − n.
- FRAC_ADD: when two fractions written in the question are added directly, computes a/b + c/d as (a + c)/(b + d).
- NEG_TIMES_NEG: when both factors are negative, gives a negative product: (−a) × (−b) = −ab and (−a)² = −a².

Which misconception(s) produced exactly the student's answer? Give the smallest set that explains it. Reply with JSON only: {"codes": [...]} listing one or two codes, or [] if it is a careless slip that no one or two of these rules explain.
```
P_TRACE (`{lines}` = `k. expression | correct answer | student's answer`, 12 lines):
```
A student answered the arithmetic questions below in one session. The student may hold any number of the five misconceptions listed. A student who holds a misconception applies it on most, but not all, questions where it changes the answer, and may also make occasional careless slips.

Misconceptions (each is a precise rule):
- LTR: evaluates +, −, ×, ÷ strictly from left to right, ignoring that × and ÷ come before + and − (brackets and squares are still done first).
- SQ_DOUBLE: computes x² as 2 × x.
- SUB_NEG: when a negative number written in the question is subtracted, computes a − (−n) as a − n.
- FRAC_ADD: when two fractions written in the question are added directly, computes a/b + c/d as (a + c)/(b + d).
- NEG_TIMES_NEG: when both factors are negative, gives a negative product: (−a) × (−b) = −ab and (−a)² = −a².

Questions (expression | correct answer | student's answer):
{lines}

For each misconception, estimate the probability that this student holds it. Reply with JSON only: {"LTR": p, "SQ_DOUBLE": p, "SUB_NEG": p, "FRAC_ADD": p, "NEG_TIMES_NEG": p} with each p between 0 and 1.
```

## Deviations
_(none yet)_

## Addendum A — Part 4 `prob_pack` (registered 2026-10-04 15:29 IST, before any prob_pack API call)
- **Why:** this is the probability / expected-value domain relevant to Optiver. The question is whether an LLM-only generator would ship wrong answer keys or wrong distractors for misconception-targeted practice problems.
- **Items:** 60 SYNTHETIC problems from `components/bugs/probability.py` (seed 2026), 12 per misconception. Each misconception has one family:
  - EQUIPROB → two-dice totals;
  - INDEP → two draws without replacement;
  - ADD_PROB → at least one success in k independent attempts;
  - INVERSE → diagnostic test with a base rate;
  - JENSEN → expected value of the square of a die.
  - Keys are exact Fractions (enumeration or closed form). The misconception's answer is given by its executable rule. Several of these misconceptions rest on secondary or unverified sources (see the module docstring and `research/notes/r7-domain-taxonomies.md`).
- **Task:** given the problem and a one-sentence description of the targeted misconception, the LLM returns the exact correct answer and the answer a student holding the misconception would give (prompt below, verbatim from `eval/run_prob_pack.py`).
- **Models:** all three, all 60 items, settings as in §2. 4 concurrent requests; started only after parts 1–3 finish.
- **Scoring:** exact Fraction equality for (a) the key, (b) the misconception answer, (c) both. EXEC is exact by construction, so this measures what an LLM-only generator would get wrong.
- **H7 (secondary, synthetic):** gap for model m if the 95% CI upper bound of the both-correct rate is < 0.95.
- **Validity note:** a description can be read differently from our rule. For example, EQUIPROB over the totals 2..2n gives 1/(2n−1). Misconception-answer disagreements are therefore reported per misconception; key accuracy is unambiguous.
- Invalid/empty responses: same procedure as §4 (one retry with double budget; then scored wrong).

Descriptions used: EQUIPROB: Thinks every possible total is equally likely.; INDEP: Ignores that the first counter is not put back, treating both draws as having the same probability.; ADD_PROB: Adds the probabilities of the separate attempts to get the probability of at least one success.; INVERSE: Confuses P(positive test | has condition) with P(has condition | positive test), so answers with the test's detection rate.; JENSEN: Squares the expected value of the number shown instead of finding the expected value of the square.

P_PROB:
```
You are writing the answer key for a probability practice problem that targets a known misconception.

Problem: {stem}
Misconception: {desc}

Give (1) the exact correct answer and (2) the exact answer that a student holding this misconception would give. Write each as an integer or a fraction a/b in lowest terms.
Reply with JSON only: {"correct": "...", "misconception_answer": "..."}
```
