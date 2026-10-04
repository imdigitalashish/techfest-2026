# Tool-Call Hallucination: Primary-Source Research Notes
Compiled 2026-10-04 for Perceptron P9 (Techfest 2026) agent guardrail project.
Rule: every entry below cites only pages opened this session. Numbers are verbatim quotes from the fetched page. Unconfirmed/inferred items marked UNVERIFIED.

---

## [2024-06] τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains
- **Authors**: Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan (Sierra)
- **Date/venue**: arXiv:2406.12045 (June 2024); accepted ICLR 2025 (per search lead, unverified on this fetch)
- **URL**: https://huggingface.co/papers/2406.12045 (mirrors https://arxiv.org/abs/2406.12045) — accessed 2026-10-04
- **Key definitions**: Benchmark emulates dynamic conversations between a simulated user (LM) and a language agent with domain-specific API tools + policy guidelines. Evaluation compares final database state to an annotated goal state (outcome-based, not step-based). Introduces **pass^k** metric: reliability of agent behavior across k repeated trials on the same task.
- **Numbers quoted exactly**: "even state-of-the-art function calling agents (like gpt-4o) succeed on $< 50\%$ of the tasks, and are quite inconsistent (pass$^8$ $< 25\%$ in retail)."
- **Method**: Two domains at time of this abstract (retail, airline); agent must gather info conversationally + call APIs under policy constraints; faithful DB-state-diff evaluation instead of exact-match transcripts.
- **Limitations (as stated in abstract/intro)**: Points to "need for methods that can improve the ability of agents to act consistently and follow rules reliably" — i.e. paper documents the failure, does not yet solve it. Full error-type taxonomy (wrong tool vs wrong args vs policy violation) not yet confirmed from this fetch — truncated at source; follow-up fetch planned for the analysis section.
- **Status**: fetched abstract + intro only (page truncated by fetch tool at ~3000 chars). Error-type breakdown not yet found — see follow-up below.

---

## [2024-06] ToolBeHonest (ToolBH): A Multi-level Hallucination Diagnostic Benchmark for Tool-Augmented Large Language Models
- **Authors**: Yuxiang Zhang, Jing Chen, Junjie Wang, Yaxin Liu, Cheng Yang, Chufan Shi, Xinyu Zhu, Zihao Lin, Hanwen Wan, Yujiu Yang, Tetsuya Sakai, Tian Feng, Hayato Yamana (Waseda Univ., Zhejiang Univ., Tsinghua Univ., CUHK, Virginia Tech, CUHK-Shenzhen)
- **Date/venue**: arXiv:2406.20015 (June 2024); EMNLP 2024 (per earlier search lead; not yet independently confirmed on fetched page)
- **URL**: https://huggingface.co/papers/2406.20015 (mirrors https://arxiv.org/html/2406.20015) — accessed 2026-10-04
- **Key definitions**: Diagnoses hallucination along two axes:
  - **Depth** (multi-level diagnostic process): (1) solvability detection — can the problem be solved with the given toolset?; (2) solution planning; (3) missing-tool analysis.
  - **Breadth** (toolset characteristics): missing necessary tools, potential (but unsuitable) tools, limited-functionality tools.
- **Numbers quoted exactly**: "we developed seven tasks and collected 700 evaluation samples through multiple rounds of manual annotation." (Abstract was truncated by fetch tool before the results/score numbers — e.g. Gemini-1.5-Pro 45.3, GPT-4o 37.0 reported by web_search lead are UNVERIFIED on this fetch; not yet confirmed directly from the primary source text.)
- **Method**: Seven-task diagnostic suite, 700 manually annotated samples, scenario-based toolset manipulation (remove/limit/distract tools) to force the model to reveal hallucination vs honest refusal/clarification.
- **Limitations**: Not yet confirmed from fetched text (truncated). Relevance to our guardrail: directly models "wrong tool" and "missing-tool" hallucination classes named in our taxonomy.
- **Status**: fetched abstract only (truncated ~3000 chars); numeric results need follow-up fetch if time allows.

