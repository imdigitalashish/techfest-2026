# R1B papers novelty — Perceptron P08 misconception tutor

Access date: 2026-10-04 IST

## TL;DR (cited bullets)

_Working skeleton created first; cited findings appended below as sources are opened._

## Findings per item

### 1. LLM-based misconception identification/diagnosis from wrong answers or explanations

### 2. Novelty check: executable misconceptions / bug programs

### 3. Programming-misconception diagnosis with LLMs (2023–2026)

### 4. Calibration / abstention: slip vs systematic misconception

## Table

| Title | Year | Venue | URL | Maturity | Relevance |
|---|---:|---|---|---|---|

## Novelty verdict for our spike (what we can and cannot claim)

_To be completed after source review._

## UNVERIFIED

- Items in the user brief are treated as search targets until opened and verified in this session.

<!-- checkpoint: opened arXiv API search for math misconception benchmark and Andrew Lan misconception papers; appended first-source findings. -->

### Source notes batch 1

- **A Benchmark for Math Misconceptions: Bridging Gaps in Middle School Algebra with AI-Supported Instruction** (Otero Nancy, Stefania Druga, Andrew Lan, arXiv 2024). The arXiv API abstract says the benchmark contains **55 misconceptions/common errors** and **220 diagnostic examples** from prior peer-reviewed studies; LLM example application reached **83.9% precision/recall** when educator feedback was included and testing was topic-restricted; **5 middle-school math educators** reviewed it, **80% or more** said they encounter these misconceptions, and **4/5** expressed interest in using the dataset with AI. URL: https://arxiv.org/abs/2412.03765 (opened via arXiv API and abstract page; accessed 2026-10-04). Maturity: paper/benchmark described; code not verified.
- **Exploring Knowledge Tracing in Tutor-Student Dialogues using LLMs** (Scarlatos, Baker, Lan, LAK 2025). The arXiv API abstract frames LLMs as labelers for knowledge components/skills in tutor/student utterances, correctness evaluation with human expert annotations, and KT over full dialogues; it reports **LLMKT significantly outperforms existing KT methods** on two tutoring dialogue datasets, but no exact numeric results were opened. URL: https://arxiv.org/abs/2409.16490 (opened via arXiv API; accessed 2026-10-04). Maturity: paper-only from opened source.
- **DiVERT: Distractor Generation with Variational Errors Represented as Text for Math Multiple-choice Questions** (Fernandez, Scarlatos, Feng, Woodhead, Lan, EMNLP 2024). The arXiv API abstract says DiVERT learns interpretable text representations of errors behind math MCQ distractors, uses a real-world dataset of **1,434 questions used by hundreds of thousands of students**, and with a **7B open-source LLM** outperforms state-of-the-art approaches using **GPT-4o** for downstream distractor generation; educator human evaluation found DiVERT error labels comparable to human-authored labels. URL: https://arxiv.org/abs/2406.19356 (opened via arXiv API; accessed 2026-10-04). Maturity: paper-only from opened source.

### Source notes batch 2

- **LLM-based Cognitive Models of Students with Misconceptions** (Shashank Sonkar, Xinghe Chen, Naiming Liu, Richard G. Baraniuk, Mrinmaya Sachan, arXiv 2024). The arXiv API/Stanford SCALE page says the work instruction-tunes LLM cognitive student models to (1) replicate specific algebra misconceptions and (2) still solve problems correctly where the misconception does not apply. It introduces **MalAlgoPy**, a Python library generating datasets of authentic student solution patterns via a graph-based representation of algebraic problem solving. Key opened-source claim: misconception-only training can replicate errors but hurts correct solving; calibrating the correct:misconception training ratio, **sometimes as low as 0.25**, can satisfy both properties. URLs: https://arxiv.org/abs/2410.12294 and https://scale.stanford.edu/ai/repository/llm-based-cognitive-models-students-misconceptions (accessed 2026-10-04). Maturity: paper + library described; public code repository not found in opened GitHub search (`total_count:0` for MalAlgoPy).
- **Eedi data and competitions.** Eedi’s first-party data page lists **7 individual sets** of misconception data, including **Eedi - Mining Misconceptions in Mathematics** (competition), **MAP - Charting Student Math Misunderstandings** (competition), **Question-Anchored-Tutoring-Dialogues-2k** (public Hugging Face), **Trace the Ace** (competition), and **Misconception Graph** (public Hugging Face). Eedi defines a misconception as a flawed conceptual structure/gap that shows as a systematic, predictable error pattern across problems. URL: https://www.eedi.com/data-and-competitions (accessed 2026-10-04). Maturity: production dataset provider + competitions.
- **Eedi Kaggle challenge writeup.** Eedi’s first-party blog says distractors are crafted to reveal specific misconceptions, but labels linking distractors to misconceptions were missing and manual tagging was slow/inconsistent; the competition task was: given a distractor and misconception descriptions, predict matches, with many test misconceptions unseen. It reports the winning approach used multi-stage retrieve/rerank with Qwen models, LoRA/contrastive learning on **10k synthetic + 1.8k real examples**, and Claude-generated student rationales for reranking; efficiency winners used Qwen2.5-0.5B or all-MiniLM-L6-v2. URL: https://www.eedi.com/news/from-wrong-answers-to-real-insights-how-we-used-a-kaggle-challenge-to-map-student-misconceptions (accessed 2026-10-04). Maturity: production/competition writeup; no peer-reviewed metrics opened.
