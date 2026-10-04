# Landscape — Perceptron P8: a tutor that finds the real reason you're stuck

*State of the art as of 4 Oct 2026. Every claim below comes from a source opened on 2026-10-04 by the lead or a research agent. The full citation trail (URL, access date, maturity) is in [`notes/`](notes/). Items we could not open are marked **UNVERIFIED**. An overnight network outage killed 5 of the 7 research agents, and three relaunched threads (Kaggle leaderboard details, verified-generation literature, specialist ed-tech/India) came back empty. They are listed under [Gaps](#7-gaps-to-close-before-31-oct).*

## 1. The problem, in the field's own terms

- **Eedi's definition**, which we adopt: a misconception is *"a flawed conceptual structure, or a gap in conceptual understanding, that manifests as a systematic and predictable error pattern across problems involving the same mathematical concept."* On Eedi, each multiple-choice Diagnostic Question has one key and three distractors, and **each distractor is tagged with the misconception it reveals** ([Eedi Misconceptions Graph card](https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph)).
- So the brief's crux, *"one specific misunderstanding producing the same class of mistake repeatedly"*, is something production systems already operationalise: wrong answers are evidence, and well-designed items make different misconceptions produce *different* wrong answers.

## 2. Misconception diagnosis from wrong answers

| Line of work | What it does | Evidence (as reported) | Source |
|---|---|---|---|
| Kaggle "Eedi – Mining Misconceptions in Mathematics" (2024) | Rank misconception descriptions for a (question, distractor); many test misconceptions unseen in training | Winning system: Qwen retrieval + rerank, LoRA/contrastive training on **10k synthetic + 1.8k real** examples, Claude-generated rationales for reranking | [Eedi blog](https://www.eedi.com/news/from-wrong-answers-to-real-insights-how-we-used-a-kaggle-challenge-to-map-student-misconceptions) |
| Math-misconception benchmark (Otero, Druga, Lan, 2024) | 55 middle-school algebra misconceptions, 220 diagnostic examples | LLM reaches **83.9%** precision/recall *with educator feedback and topic restriction* | [arXiv 2412.03765](https://arxiv.org/abs/2412.03765) |
| DiVERT (Fernandez et al., EMNLP 2024) | Learns text representations of the error behind each distractor | 1,434 real questions; a 7B open model beats GPT-4o-based methods on distractor generation | [arXiv 2406.19356](https://arxiv.org/abs/2406.19356) |
| UMass/Lan distractor studies (2024) | LLM distractor generation, overgenerate-and-rank | LLMs make valid distractors but are **weak at anticipating real students' errors** unless ranked against student data | [2404.02124](https://arxiv.org/abs/2404.02124), [2405.05144](https://arxiv.org/abs/2405.05144), [2405.00864](https://arxiv.org/abs/2405.00864) |
| Programming (Oli et al., 2025) | Gaps/misconceptions in students' code self-explanations | GPT-4 beats LLaMA3/Mistral; ORPO > SFT for spotting misconceptions | [arXiv 2501.10365](https://arxiv.org/abs/2501.10365) |
| Calibration / "slip vs misconception" | — | No targeted work found (arXiv query for uncertainty + knowledge tracing + LLM returned 0 results) | [notes/r1b](notes/r1b-papers-novelty.md) |

**Takeaway.** The frontier for *open-set* diagnosis is retrieval + LLM rerank trained with synthetic data. The weak spots are (a) anticipating *real* students' errors and (b) knowing when a wrong answer is just a slip. Both are places where an executable model of the misconception helps.

## 3. Executable misconceptions: the closest prior art (honest novelty check)

- **Classical mal-rules.** Sleeman's Leeds Modelling System diagnosed algebra errors from a database of correct and incorrect rules. It also failed on many errors from 24 students, which it attributed to mis-generalisation and parsing errors ([ERIC ED258845](https://eric.ed.gov/?id=ED258845)). BUGGY/DEBUGGY (Brown & Burton) and repair theory (VanLehn) are **UNVERIFIED** tonight; no primary page was opened.
- **MalAlgoPy** (Sonkar et al., 2024) generates misconception-consistent algebra solutions to train LLM "cognitive student models". Training on misconceptions hurts correct solving unless the correct-to-misconception ratio is tuned (e.g. 0.25) ([arXiv 2410.12294](https://arxiv.org/abs/2410.12294)).
- **MalruleLib** (Chen, Liu, Sonkar, ACL 2026) is the closest prior art. It translates documented misconceptions into executable procedures: **101 mal-rules over 498 parameterised templates, more than 1M instances**. It also defines Malrule Reasoning Accuracy. LLM accuracy drops from **66%** when solving directly to **40%** when predicting a misconception's answer across templates, and step traces add **3–15%** ([ACL 2026.acl-long.690](https://aclanthology.org/2026.acl-long.690/)).
- **What we therefore cannot claim:** "first executable misconception system", or "first to simulate misconceptions with LLMs".
- **What remains open** in the sources we opened: (1) validating executable misconceptions by **reproducing real students' labelled distractors** (Eedi data); (2) choosing problem parameters so that competing misconceptions give **pairwise-distinct wrong answers**, with keys verified by SymPy; (3) **joint** inference over *sets* of interacting misconceptions, with expected-information-gain item choice; (4) abstention between slip and systematic error. Our spike targets exactly these ([novelty verdict](notes/r1b-papers-novelty.md#novelty-verdict-for-our-spike-what-we-can-and-cannot-claim)).

## 4. Tracking a learner across sessions

- **pyKT** is the maintained deep-KT benchmark library: 441★, last push 2026-09-22, 30+ models from DKT to 2025-era UKT, RobustKT and DenoiseKT. It does not obviously ship BKT or logistic baselines ([repo](https://github.com/pykt-team/pykt-toolkit)).
- **Deep KT is not reliably better than logistic regression or BKT**: *"not necessarily by much and not always"* ([arXiv 2112.15072](https://arxiv.org/abs/2112.15072); also [2101.08349](https://arxiv.org/abs/2101.08349)). A transparent Bayesian model is a defensible choice.
- **Option-level tracing** (predicting *which* option a student picks) dates from 2021: Option Tracing ([2104.09043](https://arxiv.org/abs/2104.09043)) and DP-MTL ([2204.14006](https://arxiv.org/abs/2204.14006)). Incorrect options cluster by underlying error.
- **2026 trend: LLMs as the evidence function inside classic psychometric models.** CoLearn (EMNLP 2026) uses soft-evidence BKT with an LLM as the observation function and generates questions aimed at the weakest topics/misconceptions ([2609.21154](https://arxiv.org/abs/2609.21154)). PLCD ([2609.12403](https://arxiv.org/abs/2609.12403)), SLOW ([2603.28062](https://arxiv.org/abs/2603.28062)) and LT-MKT ([2608.24005](https://arxiv.org/abs/2608.24005)) are related. EduLoop-Agent closes the loop: cognitive diagnosis, then adaptive testing, then LLM feedback on ASSISTments ([2510.22559](https://arxiv.org/abs/2510.22559)).
- **Expected information gain for misconception diagnosis:** exact-phrase arXiv searches returned nothing. That is not proof of absence. MC-DINA and bug-based cognitive diagnosis models are **UNVERIFIED** (not opened).

## 5. Simulated learners and evidence that practice works

- **MathDial**: 2,861 released teacher–LLM-student dialogues; the LLM students were prompted with common errors ([repo](https://github.com/eth-nlped/mathdial), [ACL](https://aclanthology.org/2023.findings-emnlp.372/)).
- **Scarlatos et al. (AIED 2025)** train tutors (DPO, Llama 3.1 8B) to maximise student correctness, scored by an LLM-based student model (LLMKT) plus a GPT-4o pedagogy rubric ([2503.06424](https://arxiv.org/abs/2503.06424), [code](https://github.com/umass-ml4ed/tutorbot-dpo)).
- **Prompt-only LLM students don't stay wrong.** On 379 SAT-algebra items, three LLMs scored **96.8–100%** regardless of the low-mastery profile they were given. An explicit stochastic knowledge graph brought this down to 44.1–85.2% ([SSKG, 2608.21668](https://arxiv.org/abs/2608.21668v1)). Reasoning-level fidelity reaches only *"up to 57.9%"* ([INSIDE, 2608.10492](https://arxiv.org/abs/2608.10492v2)).
- **Implication:** our primary simulator is **program-based** (learners literally execute bug switches). LLM students are used only with a hidden, programmatic misconception state. Simulation shows the *policy logic* works under stated assumptions; a real pilot is needed for real learning claims.

## 6. What companies ship today

| Company | Product (what ships) | Explicit misconception diagnosis? | Targeted practice generation? | Cross-session learner model? | Verified generation? | Published evidence (as reported) |
|---|---|---|---|---|---|---|
| **Eedi** | Diagnostic Questions: 4 options, each distractor tied to one misconception. Misconception Graph released as a public good (8,000+ misconceptions informed by 200M responses, CC BY 4.0) | **Yes**, by item design (human-authored distractors) | Human-authored item bank | Platform-level (details not public) | Human-authored | Eedi × Google DeepMind exploratory classroom trial (Nov 2025): 165 students, 17 tutors. Human+AI vs human only: mistake fixing 93.0% vs 91.2%; misconception resolution 95.4% vs 94.9%; knowledge transfer +10 pp vs +4.5 pp; 0.1% factual inaccuracies; 82.3% of AI suggestions approved with no/minimal edits. Eedi also cites a 2023–24 RCT (2,901 students) with 2–4 extra months of maths gains ([1](https://www.eedi.com/news/new-exploratory-research-from-eedi-and-google-deepmind-reveals-human-in-the-loop-ai-tutoring-outperforms-human-only-support), [2](https://www.eedi.com/news/eedis-misconception-graph-is-now-a-public-good)) |
| **Google / DeepMind** | LearnLM; Gemini **Guided Learning** (Aug 2025: step-by-step, adaptive explanations) | Not as an explicit taxonomy (in opened sources) | — | — | — | LearnLM report: 2,360 conversations, 10,192 expert assessments; pedagogy experts preferred LearnLM over GPT-4o, Claude 3.5 Sonnet and Gemini 1.5 Pro ([2412.16429](https://ar5iv.labs.arxiv.org/html/2412.16429), [blog](https://blog.google/products-and-platforms/products/gemini/new-gemini-tools-students-august-2025/)) |
| **Anthropic** | Claude for Education **Learning mode**: guides rather than answers, Socratic questions | No | No | No | No | None found ([launch](https://www.anthropic.com/news/introducing-claude-for-education)) |
| **OpenAI** | ChatGPT Study Mode | **UNVERIFIED**: the launch page did not render cleanly | | | | |
| **Microsoft** | M365 Copilot for education (Oct 2025): *Teach* builds quizzes by difficulty/standards; *Study and Learn Agent* (adaptive practice, flashcards, quizzes); Learning Accelerators; **Math Progress** in Teams (problem generation, grading, progress insights) | No explicit misconception model in opened docs | Yes (practice generation) | Progress analytics | Not stated | None found ([blog](https://www.microsoft.com/en-us/education/blog/2025/10/designing-microsoft-365-copilot-to-empower-educators-students-and-staff/), [Learning Accelerators](https://learn.microsoft.com/en-us/training/educator-center/product-guides/learning-accelerators), [Math Progress](https://learn.microsoft.com/en-us/training/modules/support-building-mathematics-skills-math-progress/)) |
| **Khan Academy** | Khanmigo: backend **calculator** for numeric steps; regression tests of tutoring examples; *Practice My Knowledge* (teacher-generated targeted MCQs, teacher-reviewed) | Not explicit | Yes, with teacher review | Yes: feeding learning-history signals improved next-item correctness (+3.4% over 608k threads; +2.7% over 1.36M; +6.1% total over 20 A/B tests, >15M threads) | Calculator for arithmetic; items teacher-reviewed | Independent RCT (Oreopoulos & Low; 18 schools, ~6,900 students): **0.06 SD/yr**, 0.08 SD in year 2, 0.14 SD for active students. Students messaged Khanmigo in only **17%** of sessions with a mistake ([1](https://blog.khanacademy.org/what-i-found-compelling-in-a-new-randomized-trial-of-khan-academy-in-math-intervention/), [2](https://blog.khanacademy.org/how-khan-academy-is-building-a-better-ai-tutor-our-most-recent-learnings/), [3](https://blog.khanacademy.org/why-were-deeply-invested-in-making-ai-better-at-math-tutoring-and-what-weve-been-up-to-lately/), [4](https://blog.khanacademy.org/new-ai-tools-bring-interactive-diagrams-and-targeted-practice-thanks-to-khan-academys-partnership-with-google-org/)) |
| Carnegie Learning MATHia, ALEKS, Squirrel AI, Duolingo, PhysicsWallah, BYJU'S | — | **UNVERIFIED** (research thread died; to do) | | | | |

**Where we borrow, and where we go further than what's shipped:**
- *Borrow:* Eedi's diagnostic-distractor design and its CC-BY graph as our label space. Khan's "never trust the LLM's arithmetic" calculator principle and its A/B discipline. The Socratic "guide, don't answer" pattern from LearnLM and Claude for the feedback text. The teacher-in-the-loop framing that Eedi × DeepMind found safe.
- *Go further:* none of the opened product sources describes (1) items generated **automatically** whose distractors are the outputs of executable misconceptions, with keys and targeting **machine-verified** (Khan's targeted practice is teacher-reviewed; Eedi's is hand-authored); (2) a learner model over **sets of interacting misconceptions** that picks the most informative next item; (3) explicit **slip-vs-misconception** abstention.

## 7. Datasets (opened tonight)

| Dataset | Licence | What it gives us | Use |
|---|---|---|---|
| [Eedi Misconceptions Graph v1.0](https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph) (2026-09-16) | **CC BY 4.0** | 8,117 misconceptions × 2,258 constructs, 19,294 weighted edges; 4 subjects. No questions or responses | Open label space; links for our categories |
| Kaggle Eedi 2024 train data via HF mirror [`cdtmc/eedi-ir`](https://huggingface.co/datasets/cdtmc/eedi-ir) | None stated (Kaggle competition data); research use only, not redistributed; fidelity **UNVERIFIED** | 4,370 labelled (question, key, distractor → misconception) pairs; 2,587-misconception corpus; 1,604 distinct labels | Real-data diagnosis eval (open-set + our 5-category subset) |
| [Eedi Question-Anchored Tutoring Dialogues 2k](https://huggingface.co/datasets/Eedi/Question-Anchored-Tutoring-Dialogues-2k) | CC BY-NC (card text says BY-NC-SA) | 55,322 train / 13,395 test tutor–student messages anchored to Diagnostic Questions | Feedback-style reference; finals |
| [`rik1599/eedi-response-data`](https://huggingface.co/datasets/rik1599/eedi-response-data) | Not checked | 1.38M responses with `UserId`, `QuestionId`, `AnswerValue`, `CorrectAnswer` (looks like NeurIPS 2020 Eedi data; provenance **UNVERIFIED**) | Candidate for **real** option-level, multi-session tracking (finals) |
| MathDial ([repo](https://github.com/eth-nlped/mathdial)) | see repo | 2,861 tutoring dialogues with LLM students holding errors | Simulator / feedback reference |

Domain packs: [notes/r7](notes/r7-domain-taxonomies.md) gives cited, executable taxonomies for school maths, probability/expected value (the Optiver-relevant pack) and novice Python. Our MVP pack uses five school-maths misconceptions that share one expression family, so they **compete on the same items**. That is the property discriminative generation needs.

## 8. Implications for our design

1. **Novelty claim (narrow and defensible):** real-distractor validation + discriminative, verified generation + set-level Bayesian tracing with expected-information-gain item choice + slip abstention. *Not* "executable misconceptions" in general (MalruleLib, Sleeman).
2. **Diagnosis is hybrid.** Exact bug likelihood where the item is executable; Eedi-winner-style retrieval + rerank over the 2,587/8,117-misconception catalogue otherwise.
3. **Learner model.** A transparent Bayesian (BKT-family) model, generalised to sets of bugs; deep KT is not a guaranteed win.
4. **Evaluation.** Real Eedi distractors for diagnosis; machine-checked generation validity; program-based simulated learners in a factorial design for the stretch goal; a small real pilot before finals.
5. **Product.** Teacher-in-the-loop dashboard (Eedi × DeepMind evidence); Socratic feedback; never let an LLM state an unverified number (Khan).

## 9. Gaps to close before 31 Oct

- Kaggle Eedi 2024 / MAP 2025 leaderboard scores and top write-ups (Kaggle pages not opened).
- Verified-generation literature (GSM-Symbolic, MathCAMPS, NuminaMath-style verification pass rates).
- Specialist ITS (MATHia model tracing, ALEKS), Indian ed-tech (PhysicsWallah, BYJU'S), OpenAI Study Mode.
- RCTs: Bastani et al. (PNAS), Kestin et al. (Harvard physics), World Bank Nigeria, Tutor CoPilot.
- MC-DINA / bug-CDM primary sources; BUGGY/DEBUGGY primary sources.
- Independent re-verification of the top claims above by a fresh agent (PLAYBOOK Phase 1), once the network allows.
