# R7 Domain Taxonomies — Executable Misconception Tutor

Today / access date for every cited source: **2026-10-04 IST**. Scope: MVP misconception categories that are (a) common enough to be useful, (b) expressible as deterministic malrules over parameterised problems, and (c) grounded in sources opened in this session. For paywalled/classic work, I cite open abstract/landing pages or open secondary pages opened here and mark limitations.

## TL;DR (recommended categories per domain)

### School math MVP pack

1. **Subtraction as “smaller-from-larger” / subtraction commutativity** — columnwise `|top_digit-bottom_digit|` or swap operands if needed.
2. **Fraction componentwise operations** — especially `a/b + c/d -> (a+c)/(b+d)` or related denominator-addition variants.
3. **Decimal string/place-value misconceptions** — compare or operate on decimals as digit strings, e.g. longer decimal part means larger.
4. **Order-of-operations malrules** — left-to-right, or “multiplication before division” instead of equal-precedence left-to-right.
5. **Linear-equation/algebra transformation malrules** — sign/inverse operation omitted or applied to one side only.

### Probability / expected-value MVP pack

1. **Equiprobability bias** — treat listed or salient outcomes as equally likely.
2. **Outcome approach / deterministic single-trial prediction** — answer “will it happen?” rather than compute a probability or expected value.
3. **Representativeness / gambler’s fallacy** — after streaks, force short-run balancing.
4. **Base-rate neglect / confusion of inverse** — use `P(test+ | disease)` as `P(disease | test+)`, or ignore priors.
5. **Event/expectation algebra malrules** — add non-exclusive probabilities, assume independence, or use `E[f(X)] = f(E[X])`.

### Novice Python MVP pack

1. **Assignment as algebra / permanent binding** — `y = x + 1` updates when `x` later changes; `a = b` is symmetric or linked.
2. **Sequentiality/control-flow misconceptions** — lines or branches run simultaneously; `if` repeats like `while`.
3. **Type coercion misconception** — numeric strings behave like numbers, or `+` always means arithmetic addition.
4. **Indexing/collection misconceptions** — 1-based indexing; list assignment copies instead of aliases; dict iteration yields values.
5. **Function I/O misconceptions** — `print` is `return`; local assignment changes a global.

## School math table

| Misconception | Rule / malrule | Example -> wrong answer | Executable? | Evidence | Source |
|---|---|---|---|---|---|
| Subtraction “smaller-from-larger” / commutative subtraction | For each column, output `abs(top_digit-bottom_digit)`; ignore borrowing. Variant: if `a-b` negative-looking, compute `b-a`. | `602 - 178`: hundreds `6-1=5`, tens `|0-7|=7`, ones `|2-8|=6` -> **576** (correct 424). | Yes: digitwise deterministic with base-10 parameters. | Brown & Burton’s ERIC abstract describes diagnostic models that synthesize deep-structure models of students’ misconceptions/bugs in basic mathematics skills. Eedi CSV has misconception names such as “Believes subtraction is commutative.” | https://eric.ed.gov/?id=ED159036; https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph/resolve/main/data/misconception-map.csv (accessed 2026-10-04) |
| Fraction componentwise addition | `a/b + c/d -> (a+c)/(b+d)`. Related Eedi variant: after first common-denominator step, add denominators in final step. | `2/3 + 3/5 -> (2+3)/(3+5)=5/8` (correct `19/15`). | Yes: pure function over integer parameters. | Eedi CSV grep found “When adding fractions with unlike denominators, completes the first step correctly, but then adds the denominators in the final step.” MalruleLib lists executable fractions malrules. | https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph/resolve/main/data/misconception-map.csv; https://github.com/sonkar-lab/malrulelib (accessed 2026-10-04) |
| Decimal longer-is-larger / string comparison | To compare `0.x` and `0.y`, compare length or integer value of decimal tail, not place value. | Choose larger of `0.62` and `0.7`: tail `62 > 7`, so answer **0.62** (correct 0.7). | Yes for comparison tasks; deterministic string rule. | Steinle & Stacey’s ERIC record says decimal misconceptions led students to select as larger “decimals that look smaller,” with a longitudinal study of about 900 students. | https://eric.ed.gov/?id=ED489646 (accessed 2026-10-04) |
| Order of operations: multiplication before division, or left-to-right over precedence | Variant A: evaluate all multiplications before divisions. Variant B: evaluate strictly left-to-right. | `8 / 2 * 4`: multiplication-first gives `8/(2*4)=1` (correct left-to-right 16). `3+4*5`: left-to-right gives `(3+4)*5=35` (correct 23). | Yes: expression-tree rewrite/evaluation strategy. | Eedi CSV grep found “Performs multiplication ahead of division” in BIDMAS/order-of-operations constructs; MaE covers order of operations; MalruleLib has `order_of_operations`. | https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph/resolve/main/data/misconception-map.csv; https://huggingface.co/datasets/nanote/algebra_misconceptions; https://github.com/sonkar-lab/malrulelib (accessed 2026-10-04) |
| Linear-equation inverse/sign malrule | Move a term across `=` without changing sign, or apply inverse operation to only one side. | `3x + 5 = 20`: move `+5` as `+5`, so `3x=25`, `x=25/3` (correct 5). | Yes for constrained equation templates. | Sleeman’s ERIC record says Leeds Modelling System used incorrect/buggy/mal-rules and found manipulative and parsing algebra mal-rules; MaE includes linear equations and variables/expressions categories. | https://eric.ed.gov/?id=ED258845; https://huggingface.co/datasets/nanote/algebra_misconceptions (accessed 2026-10-04) |
| Percentage “percent as raw number” | Treat `p% of n` as `p*n`, or use `p/10` instead of `p/100`. | `15% of 80 -> 15*80=1200` or `1.5*80=120` (correct 12). | Yes. | Eedi CSV grep found percentage constructs, including “Calculate percentage of an amount mentally”; MalruleLib lists `percentages`. | https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph/resolve/main/data/misconception-map.csv; https://github.com/sonkar-lab/malrulelib (accessed 2026-10-04) |

## Probability / expected value table

| Misconception | Rule / malrule | Example -> wrong answer | Executable? | Evidence | Source |
|---|---|---|---|---|---|
| Equiprobability bias | If a problem lists `k` salient outcomes/classes, set each to `1/k`, ignoring multiplicity. | Three coins; probability of exactly two heads. Salient counts `{0H,1H,2H,3H}` -> **1/4** (correct `3/8`). | Yes for sample-space templates. | Opened source leads identify Lecoutre/equiprobability; direct JSTOR page opened but content did not load. Treat this named source as source-limited; the rule itself is also illustrated by an opened outcome/sample-space page showing three-coin counts are not equally likely. | https://www.jstor.org/stable/3482885; https://docslib.org/doc/9447092/outcome-orientation-a-misconception-of-probability (accessed 2026-10-04) |
| Outcome approach / deterministic single-trial prediction | Convert probability question into yes/no prediction: if `p >= 0.5`, answer event happens / probability 1; else 0. | Bag has 7 red, 3 blue. “Probability next is red?” -> **1** or “red for sure” (correct 0.7). | Yes, but output type may be categorical or numeric. | Konold’s ERIC abstract defines the “outcome approach”: goal is predicting an individual trial with yes/no decisions, evaluated as right/wrong, often with deterministic models. | https://eric.ed.gov/?id=ED287703 (accessed 2026-10-04) |
| Gambler’s fallacy / representativeness | After streak of `r` same outcomes, increase probability of opposite to force balance; simple MVP: choose opposite as more likely / probability 1. | Fair coin after `HHHH`: predict **T more likely** or `P(T)=1` (correct 0.5). | Yes for streak templates. | Opened gambler’s fallacy page says people expect streaks to even out and after long run of red believe black is more representative; opened representativeness page links representativeness to base-rate neglect and inverse-probability errors. | https://en.wikipedia.org/wiki/Gambler%27s_fallacy; https://en.wikipedia.org/wiki/Representativeness_heuristic (accessed 2026-10-04) |
| Base-rate neglect / confusion of inverse | Return `P(+|D)` or `1 - false_negative` as `P(D|+)`, ignoring prevalence and false positives. | Prevalence 2%, sensitivity 100%, false-positive 5%. Wrong **100%** or **95%**; correct `20/(20+49)=29%` per 1000. | Yes for diagnostic-test templates. | Opened base-rate page gives high/low prevalence examples and shows many estimate 95% where correct is about 2% in a low-base-rate breathalyzer example; representativeness page states inverse probabilities are equated and base rate ignored. | https://en.wikipedia.org/wiki/Base_rate_fallacy; https://en.wikipedia.org/wiki/Representativeness_heuristic (accessed 2026-10-04) |
| Addition of non-exclusive probabilities | `P(A ∪ B) = P(A)+P(B)` even when overlap exists. | `P(A)=0.6`, `P(B)=0.5`, `P(A∩B)=0.2`: wrong **1.1** or clipped **1.0**; correct `0.6+0.5-0.2=0.9`. | Yes. | This is a formal event-algebra malrule; opened probability pages document formal probability constraints and expected-value weighting, but I did not open a misconception-specific primary source for this exact novice error. | https://en.wikipedia.org/wiki/Expected_value (accessed 2026-10-04); see UNVERIFIED |
| Assuming independence | `P(A∩B)=P(A)P(B)` or `P(A|B)=P(A)` despite stated dependence. | `P(A)=0.6`, `P(B)=0.5`, `P(A∩B)=0.4`: wrong intersection **0.3** (correct 0.4). | Yes. | Formal probability rule is executable; a misconception-specific education source was not opened. | https://en.wikipedia.org/wiki/Conjunction_fallacy (accessed 2026-10-04); see UNVERIFIED |
| `E[f(X)] = f(E[X])` | Compute mean first, then transform, regardless of nonlinearity. | Fair die payout `X^2`: wrong `(E[X])^2=(3.5)^2=12.25`; correct `(1+4+9+16+25+36)/6=91/6≈15.17`. | Yes for random-variable templates. | Opened expected-value page defines expectation as weighted average; Jensen’s inequality page states convex `φ(E[X]) ≤ E[φ(X)]`, so equality is not generally valid. | https://en.wikipedia.org/wiki/Expected_value; https://en.wikipedia.org/wiki/Jensen%27s_inequality (accessed 2026-10-04) |

## Novice Python table

| Misconception | Rule / malrule | Example -> wrong answer | Executable? | Evidence | Source |
|---|---|---|---|---|---|
| Assignment as algebra / permanent binding | Store expression dependency instead of current value; or make `a=b` a live link for primitives. | `x=2; y=x+3; x=10; print(y)` -> **13** (correct 5). | Yes for predict-output traces. | Python question bank lists V1 inverse assignment, V2 permanent binding, V5-like assignment-as-formula in examples; IntroCS page states assignment evaluates the right side first and is not a mathematical equation. | https://github.com/Cam1loadg/Programming-Misconceptions-Question-Bank; https://introcs-python.cs.luc.edu/data/variables.html (accessed 2026-10-04) |
| Sequentiality / branch simultaneity | Execute later assignments too early, or execute both `if` and `else`. | `x=1; if x>0: x=2; else: x=3; print(x)` -> **3** if both branches run (correct 2). | Yes for small-step interpreter variants. | Question bank lists S1 sequentiality failure and S2 simultaneous `if/else`; Sorva’s Aalto page says program-execution reasoning is a major challenge and visual simulation has learners act as the computer. | https://github.com/Cam1loadg/Programming-Misconceptions-Question-Bank; https://research.aalto.fi/en/publications/visual-program-simulation-in-introductory-programming-education/ (accessed 2026-10-04) |
| `if` repeats like `while` / loop stopping magic | Treat `if condition:` as repeated until false, or assume loops stop when “done” without condition update. | `x=0; if x<3: x=x+1; print(x)` -> **3** under if-as-while (correct 1). | Yes, bounded interpreter variant. | Question bank lists S3 `if/while` confusion and S4 magic/abrupt loop; PD4CS loops page lists variable values, flow of execution, conditionals, infinite loops as loop misconceptions/challenges. | https://github.com/Cam1loadg/Programming-Misconceptions-Question-Bank; https://www.pd4cs.org/loops-student-misconceptions-and-challenges/ (accessed 2026-10-04) |
| Numeric/text type confusion | Coerce numeric strings to numbers for `+`, or treat all `+` as concatenation. | `print("2" + "3")` -> **5** (correct `23`). | Yes for expression evaluator. | Question bank lists C2 numeric/text types: numeric strings behave like numbers. | https://github.com/Cam1loadg/Programming-Misconceptions-Question-Bank (accessed 2026-10-04) |
| 1-based indexing | Interpret `lst[1]` as first element. | `a=[10,20,30]; print(a[1])` -> **10** (correct 20). | Yes. | Question bank lists R1 1-based indexing; PD4CS MC index states misconceptions often involve interactions between concepts such as list element values and loops. | https://github.com/Cam1loadg/Programming-Misconceptions-Question-Bank; https://www.pd4cs.org/mc-index/ (accessed 2026-10-04) |
| List assignment copies instead of aliases | `b=a` creates independent copy for lists. | `a=[1]; b=a; b.append(2); print(a)` -> **[1]** (correct `[1, 2]`). | Yes. | Question bank lists R2 “assigning a list to another variable creates an independent copy.” | https://github.com/Cam1loadg/Programming-Misconceptions-Question-Bank (accessed 2026-10-04) |
| `print` equals `return` / local mutates global | Treat printed value as function return; or local assignment as global mutation. | `def f(): print(4); x=f(); print(x)` -> **4 then 4** (correct `4` then `None`). | Yes. | Question bank lists F1 print vs return and F2 local/global scope. | https://github.com/Cam1loadg/Programming-Misconceptions-Question-Bank (accessed 2026-10-04) |

## Discriminating problem families

### School math

**Family S1 — “same symbols, different structural malrules” diagnostic bundle.** Generate a 5-item bundle from parameters chosen to avoid accidental collisions: `a,b,c,d,e,f,g,h,p,n`.

1. Fraction item: `a/b + c/d`, with `b,d` coprime and `a/b+c/d` not equal to `(a+c)/(b+d)`. Example `2/3 + 3/5`: correct `19/15`; componentwise wrong `(2+3)/(3+5)=5/8`; denominator-add-after-common-denominator wrong `10/8` if student computes `10/15+9/15 -> 19/30` or other instrumented variant. Use answer options from the specific malrule implementation.
2. Decimal comparison item: choose larger of `0.62` and `0.7`: correct `0.7`; longer-is-larger wrong `0.62`.
3. Subtraction item: `602-178`: correct `424`; smaller-from-larger wrong `576`; commutative-swap wrong `-424` or `424` depending representation, so instrument as digitwise to distinguish.
4. BIDMAS item: `8/2*4`: correct `16`; multiplication-before-division wrong `1`.
5. Equation item: `3x+5=20`: correct `5`; sign-not-changed wrong `25/3`; divide-before-subtract wrong `3x=20/5=4 -> x=4/3`.

These wrong answers are pairwise distinct within their item, and the item labels distinguish the malrule class. For a single-score MVP, score the bundle rather than forcing all categories into one expression.

**Family S2 — Mixed arithmetic word problems with one latent category each.** Parameter constraints: use values that make correct and malrule outputs integer or simple fraction, and check `wrong_i != correct_i`.

- Percentage: `p% of n` with `p=15,n=80`: correct `12`; raw-percent wrong `1200`; divide-by-10 wrong `120`.
- Fraction: `1/2 + 1/3`: correct `5/6`; tops-and-bottoms wrong `2/5`.
- Negative/order: `-3^2` if convention taught as `-(3^2)`: correct `-9`; “negative squared first” wrong `9`. Or `3+4*5`: correct `23`; left-to-right wrong `35`.
- Equation: `2(x-3)=10`: correct `8`; distribute-only-left/wrong inverse variants can produce `2x-3=10 -> 6.5` or `x-3=20 -> 23`.
- Decimal: order `0.4, 0.35, 0.308`: correct `0.308 < 0.35 < 0.4`; longer-is-larger ranks `0.308` as largest.

### Probability / expected value

**Family P1 — Small finite random experiment bundle.** Parameters: `n` fair coins/dice plus event definitions that create unequal multiplicities.

1. Equiprobability bias: three coins, `P(exactly 2 heads)`: correct `3/8`; count-outcomes-as-counts wrong `1/4` over `{0,1,2,3 heads}`.
2. Outcome approach: urn `7 red, 3 blue`, ask probability next red: correct `7/10`; deterministic majority wrong `1` (or categorical “red for sure”).
3. Gambler’s fallacy: fair coin after `HHHH`, ask `P(T next)`: correct `1/2`; balancing wrong `>1/2` or MVP categorical “T more likely”; use numeric option `3/4` for deterministic classifier.
4. Non-exclusive addition: `P(A)=0.6, P(B)=0.5, P(A∩B)=0.2`: correct `0.9`; add-only wrong `1.1` (or clipped `1.0`, decide in malrule).
5. Jensen/expectation: fair die payout `X^2`: correct `91/6≈15.17`; `f(E[X])` wrong `12.25`.

All numeric wrong answers above are distinct: `0.25`, `1`, `0.75`, `1.1`, `12.25` (with correct answers also distinct).

**Family P2 — Bayesian/dependence/trading-style expected value bundle.** Parameter constraints: choose prevalence low enough and false-positive high enough to separate inverse/base-rate answers.

1. Base-rate neglect: prevalence `2%`, sensitivity `100%`, false positive `5%`, population `1000`: true positives `20`, false positives `49`; correct `20/(20+49)=29%`; inverse/sensitivity wrong `100%`; “95% accurate” wrong `95%`.
2. Assuming independence: `P(up)=0.6`, `P(signal)=0.5`, stated `P(up∩signal)=0.4`; correct `0.4`; independence wrong `0.3`.
3. Confusion of inverse: `P(signal|up)=2/3`, `P(up)=0.6`, `P(signal)=0.5`; correct `P(up|signal)=0.8`; inverse wrong `2/3`.
4. Permutations vs combinations: choose unordered pair from 5 assets: correct `C(5,2)=10`; permutation wrong `5P2=20`.
5. Expected-value thresholding/outcome approach: bet pays `+10` with `0.4`, `-5` with `0.6`: correct EV `4-3=1`; outcome approach says “loss likely” or numeric `-5`; expected payoff by most likely outcome wrong `-5`.

Wrong outputs `100/95`, `0.3`, `2/3`, `20`, `-5` are separable by item and category.

### Novice Python

**Family Py1 — Assignment, sequence, indexing, type bundle.** Generate short predict-output snippets with one target misconception each.

1. Assignment binding:
   ```python
   x = 2
   y = x + 3
   x = 10
   print(y)
   ```
   Correct `5`; formula/permanent-binding wrong `13`.
2. Sequentiality / both branches:
   ```python
   x = 1
   if x > 0:
       x = 2
   else:
       x = 3
   print(x)
   ```
   Correct `2`; both-branches wrong `3`.
3. 1-based indexing:
   ```python
   a = [10, 20, 30]
   print(a[1])
   ```
   Correct `20`; 1-based wrong `10`.
4. Numeric string:
   ```python
   print("2" + "3")
   ```
   Correct `23`; numeric-string wrong `5`.
5. Print vs return:
   ```python
   def f():
       print(4)
   x = f()
   print(x)
   ```
   Correct output `4\nNone`; print-as-return wrong `4\n4`.

Target wrong answers are distinct and executable with small interpreter patches.

**Family Py2 — Collections/functions bundle.**

1. List aliasing:
   ```python
   a = [1]
   b = a
   b.append(2)
   print(a)
   ```
   Correct `[1, 2]`; copy-on-assignment wrong `[1]`.
2. Dict iteration:
   ```python
   d = {"a": 2, "b": 3}
   s = 0
   for x in d:
       s = s + len(x)
   print(s)
   ```
   Correct `2` (keys `a`,`b`); values-iteration wrong type/error or `5` if summing values in a numeric variant.
3. Local/global scope:
   ```python
   x = 1
   def f():
       x = 2
   f()
   print(x)
   ```
   Correct `1`; local-changes-global wrong `2`.
4. If-as-while:
   ```python
   x = 0
   if x < 3:
       x = x + 1
   print(x)
   ```
   Correct `1`; if-repeats wrong `3`.
5. Auto-initialization:
   ```python
   total = total + 1
   print(total)
   ```
   Correct `NameError`; default-zero wrong `1`.

Use categorical scoring for exceptions (`NameError`) so wrong predictions remain distinguishable.

## UNVERIFIED

- I did **not** open full PDFs, per instruction. Where a classic source was paywalled or blocked, I cited only an opened landing/abstract/secondary page and marked source limits.
- Brown & Burton’s exact named bug inventory (e.g. the label “smaller-from-larger”) is treated as classic background but the opened ERIC abstract only verifies the diagnostic-bug framework, not every named bug.
- Lecoutre equiprobability: JSTOR landing page opened but did not expose article content. The equiprobability-bias rule is included because it was requested and source leads identify it, but its detailed empirical claims need a directly accessible abstract/source before production citation.
- Qian & Lehman 2017 ACM DOI was attempted but ACM returned 403 and Crossref produced no output in this environment. Therefore Qian & Lehman-specific claims are not used as evidence rows; novice Python recommendations rely on Sorva/Sirkiä, the opened Python misconception question bank, PD4CS, and IntroCS pages.
- Misconception-specific research sources were not opened for non-exclusive addition, independence-vs-dependence, and permutations-vs-combinations errors; they are included as executable probability malrules because they are standard formal-error patterns and Optiver-relevant, but should be sourced from probability-education literature before external publication.
- MalAlgoPy arXiv page was opened via curl and title/landing metadata were visible, but I did not use detailed claims beyond the title-level fact because the web_fetch transport failed.
