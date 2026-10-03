# R2B Simulation Evidence — Perceptron P08 Misconception Tutor

Access date for all opened sources: 2026-10-04.

## TL;DR

- LLM student simulation is useful but unsafe as the sole evidence source: MathDial used LLMs prompted with common errors to collect 3k tutoring dialogues, while a 2026 arXiv search result warns that prompt-only LLM students can answer correctly despite low-mastery prompts (96.8–100% accuracy across profiles on 379 SAT Algebra items), requiring programmatic/external misconception state for faithful errors ([MathDial arXiv/API](https://export.arxiv.org/api/query?id_list=2503.06424,2305.14536&max_results=2), [MathDial GitHub](https://github.com/eth-nlped/mathdial), [student-simulation arXiv API](https://export.arxiv.org/api/query?search_query=all:%22student%20simulation%22%20AND%20all:%22large%20language%20models%22&sortBy=submittedDate&sortOrder=descending&max_results=15); accessed 2026-10-04).
- Tutor evaluation can use simulated students as a training/evaluation signal, but should still report pedagogical quality and human/real-learner checks: Scarlatos et al. score candidate tutor turns with an LLM-based student model plus GPT-4o pedagogical rubric, then DPO-train Llama 3.1 8B; the paper is published at AIED 2025 ([arXiv/API](https://export.arxiv.org/api/query?id_list=2503.06424,2305.14536&max_results=2), [official code](https://github.com/umass-ml4ed/tutorbot-dpo); accessed 2026-10-04).

## Findings per item

### 1. LLM-simulated students holding specified misconceptions (2023–2026)

- **MathDial (2023, Findings of EMNLP).** The arXiv API abstract says the collection framework paired human teachers with an LLM “prompted to represent common student errors” and produced “3k one-to-one teacher-student tutoring dialogues” grounded in multi-step math reasoning. The official repo gives the exact released count as **2861 conversations** and includes fields for `student_incorrect_solution`, `student_profile`, `teacher_described_confusion`, end-of-dialogue `self-correctness`, and Likert ratings for typical confusion/interactions. Relevance: strong precedent for specified-misconception LLM students, but also a warning that GPT-3-style models can reveal answers too early or give factually incorrect feedback when used as tutors, so simulator and tutor roles should be separated. Sources: [arXiv/API](https://export.arxiv.org/api/query?id_list=2503.06424,2305.14536&max_results=2), [GitHub](https://github.com/eth-nlped/mathdial), [ACL metadata](https://aclanthology.org/2023.findings-emnlp.372/) (accessed 2026-10-04).
- **Scarlatos et al. (2025, AIED).** The arXiv API abstract describes training LLM tutors to maximize student correctness during dialogue by scoring candidate tutor utterances with **(1)** an LLM-based student model predicting chance of correct student responses and **(2)** a pedagogical rubric evaluated by GPT-4o, then DPO-training **Llama 3.1 8B**. The official repo identifies the venue as AIED 2025, pages **251--266**, and says the method relies on **LLMKT** trained on MathDial. Relevance: directly supports an A/B where simulated learners estimate whether targeted tutor turns/practice increase correctness, but the paper’s own design also keeps a pedagogical-quality check. Sources: [arXiv/API](https://export.arxiv.org/api/query?id_list=2503.06424,2305.14536&max_results=2), [official code](https://github.com/umass-ml4ed/tutorbot-dpo) (accessed 2026-10-04).
- **Recent simulator-fidelity warnings (2026 arXiv API search).** “From Mastery Profile to Simulated Response: Stochastic Student Knowledge Graphs (SSKG) for Faithful LLM Student Simulation” reports that prompt-based LLM student simulations on **379 College Board-calibrated SAT Algebra items** with five mastery profiles led three LLMs to achieve **96.8-100% accuracy across all profiles**, whereas SSKG reduced accuracy to **44.1-85.2% across profiles** and produced a monotone mastery gradient. “INSIDE the Student's Mind” argues action-only simulation misses latent reasoning; on code generation it reports highest reasoning alignment “up to **57.9%**.” Relevance: for our stretch goal, executable misconception/program-based students should be the primary simulator; LLM-simulated students should be constrained by hidden state and audited for staying wrong until remediation. Source: [arXiv API search](https://export.arxiv.org/api/query?search_query=all:%22student%20simulation%22%20AND%20all:%22large%20language%20models%22&sortBy=submittedDate&sortOrder=descending&max_results=15) (accessed 2026-10-04).

### 2. Accepted protocols to show learning

### 3. Learning-science evidence on remediating misconceptions

## Source table

| Title | Year | Venue | URL | Maturity | Relevance |
|---|---:|---|---|---|---|
| MathDial: A Dialogue Tutoring Dataset with Rich Pedagogical Properties Grounded in Math Reasoning Problems | 2023 | Findings of EMNLP | https://arxiv.org/abs/2305.14536; https://github.com/eth-nlped/mathdial | Peer-reviewed dataset + code | Human teachers tutoring LLM students prompted with common errors; 2861 released conversations. |
| Training LLM-based Tutors to Improve Student Learning Outcomes in Dialogues | 2025 | AIED 2025 | https://arxiv.org/abs/2503.06424; https://github.com/umass-ml4ed/tutorbot-dpo | Peer-reviewed conference + code | Uses LLM-based student model and DPO to optimize tutor utterances for student correctness and pedagogy. |
| From Mastery Profile to Simulated Response: Stochastic Student Knowledge Graphs (SSKG) for Faithful LLM Student Simulation | 2026 | arXiv | https://arxiv.org/abs/2608.21668v1 | Preprint/API abstract only | Shows prompt-only LLM students may not respect low mastery; proposes external stochastic mastery graph. |
| INSIDE the Student's Mind: Jointly Modeling Latent Reasoning and Action in LLM Student Simulators | 2026 | COLM 2026 per arXiv comment | https://arxiv.org/abs/2608.10492v2 | Accepted/preprint/API abstract only | Fidelity criterion includes latent reasoning, not just final answers/actions. |

## Recommended evaluation protocol for our stretch goal

Draft in progress.

## UNVERIFIED

- User-provided leads not yet opened in this session remain UNVERIFIED until cited above.
