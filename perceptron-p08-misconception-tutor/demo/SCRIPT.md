# P8 demo: 3-minute talk track

**Before you start (2 minutes ahead)**
- Run `perceptron-p08-misconception-tutor/demo/run.sh`. The browser opens on tab 1.
- Check the two pills, top right: **No-text mode · engine live** and **LLM calls: 0 · $0**.
- Never start with `--local-text` in front of judges, in a recording or for a screenshot. Kaggle Eedi rules §7.B forbid it.
- Window at least 1,400 px wide. Use normal browser zoom, or one step larger on a projector. Keys **1–4** switch tabs.
- If anything fails, open `demo/fallback/` (numbered screenshots) or `fallback/p8_demo_offline.html` and talk over them.

## 0:00–0:15 · Hook (tab 1)
> "A student writes 1/8 + 1/8 = 2/16. That is not a random slip. It is exactly what 'add the tops, add the bottoms' produces. Our tutor turns each misconception into a rule it can execute. If a rule reproduces the student's exact wrong answer, the tutor issues a **certificate**. If no rule does, it claims nothing."

## 0:15–0:55 · Real data first (tab 1: Real answers)
1. Point at the left panel.
   > "These are 304 real wrong answers from Eedi. We pre-registered the test against three OpenAI models, and their answers are replayed from the committed runs. Nothing is called live."
2. Point at **Named a misconception that wasn't there**.
   > "152 of these wrong answers were caused by *other* misconceptions. GPT-4.1-mini blamed one of ours anyway, 24 times: 15.8%. Our engine did it 0 times, and so did GPT-5.5."
3. In the square grid, switch the colouring to **GPT-4.1-mini**, then back to **Our engine**. The red squares disappear.
4. Click the filter **Engine certificates**, then click square **1195_B**. The marking slip opens.
   > "Our engine re-ran 'thinks squaring means doubling' and got the student's exact answer. That is the certificate. GPT-5.5 agrees. GPT-4.1-mini said NONE, then changed its mind when asked again."
5. Say the honest line.
   > "GPT-5.5 diagnoses far more of these: 79.4% against our 19.1%. We claim no accuracy edge. So why have an engine at all?"

## 0:55–1:10 · Ask it again (tab 1)
With the colouring on **GPT-5.5**, click **Run 2**, then **Run 3**. Changed squares glow yellow.
> "Asked again, GPT-5.5 changed 2 of its 40 diagnoses. Both are questions our parser can't read, and we would still send those to GPT-5.5. Where our engine answers, it is identical every time: 304/304."

## 1:10–2:10 · The crazy element (tab 2: Predict my mistake)
1. Hand the keyboard to a judge.
   > "Answer 3 + 4 × 2 wrong, any way you like."

   If they hesitate, suggest working left to right, which gives 14.
2. Click **Mark it** and point at the two columns.
   > "Correct working on the left, the rule's working on the right. The highlighted step is where they part. It took a fraction of a millisecond on this laptop, with no LLM."
3. Click **Ask again × 1,000**.
   > "1,000 of 1,000 identical."
4. > "A certificate is evidence, not proof: one wrong answer could just be a slip. So the tutor makes a prediction you can check."

   Click **Seal a prediction**.
   > "It wrote a new question, had SymPy check the answer key, and committed to *your* answer before you give it. The hash is the commitment."
5. The judge answers the new question the same way, then clicks **Reveal**.
   > "Predicted. The hash is checked in this browser. Two answers, both reproduced by the same rule, so the tracer is now sure. It writes targeted practice, and SymPy checks every key."
6. Optional (5 s): click **New generated question** and type a random wrong answer.
   > "No claim. In the cascade, this one goes to the LLM."
7. Optional: click **Slip storm**.
   > "2,400 random slips: 2,379 get no claim, and 21 land on a rule's answer by chance, 0.9%. That is why we predict before we label."

## 2:10–2:45 · The knob (tab 3: Cascade & budget)
1. Ask: "Where should the engine stop and the LLM start?" Defaults: **Real Eedi**, **Engine first**, **GPT-5.5**. Point at **$6.10**, under it "LLM only: $6.50".
   > "On real Eedi the engine certifies only 26 of 304 answers, so the saving is small, and that analysis is post hoc."
2. Click **Tutor-native probability · 120**.
   > "On our own probability items, half are explainable by design. LLM calls halve, and GPT-5.5's cost per 1,000 diagnoses falls from $7.32 to $5.08."

   Add that routing is guaranteed by construction here.
3. Click **LLM unplugged**.
   > "Pull the plug. The engine still answers what it can certify, with no false claims and no network. The rest goes to a teacher."
4. Back on **Real Eedi** with **GPT-5.5**, drag **Budget squeeze** to between $6.10 and $6.50.
   > "At this budget, GPT-5.5 fits only with the engine first."

## 2:45–3:00 · Stress tests (tab 4, labelled SYNTHETIC) and close
> "These are labelled synthetic. At 4–8 operators, GPT-5.5 inverts every answer, 100.0%, but it spends 2,309 reasoning tokens per item; our engine is exact by construction. With simulated learners, 28.0% of misconceptions remain after four sessions, against 58.4% with random practice, at equal learning rates."

Close:
> "Name the rule, check it, verify the practice. An exact-first cascade answers what it can certify, instantly and identically, and hands the rest to a frontier LLM."

## Likely questions
- **"Isn't the LLM just better?"** On these real items, yes, for coverage. Say so. Our claims are determinism, certificates, latency, verified practice, and cost only where the engine certifies.
- **"Where are the questions?"** Kaggle's licence forbids showing Eedi text to non-participants (§7.B). The page shows derived outcomes only. The LIVE tab uses our own questions.
- **"Is the prediction rigged?"** The commitment hash is shown before you answer. Your browser recomputes SHA-256 over the revealed record. The prediction is conditional ("if you hold LTR"). When it fails, the tutor says so and lowers its belief.
