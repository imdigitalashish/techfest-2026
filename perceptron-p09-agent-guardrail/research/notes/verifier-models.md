# Verifier / Guard Model Research — Perceptron P09 Agent Guardrail

Session date: 2026-10-04. Rule: only pages actually opened this session are cited; numbers quoted exactly; anything not directly confirmed is marked **UNVERIFIED**.

---

## vectara/hallucination_evaluation_model (HHEM-2.1-Open)

- **HF id**: `vectara/hallucination_evaluation_model`
- **License**: `apache-2.0` (per raw README YAML frontmatter) — note: repo also lists `extra_gated_fields` (Company/Country), i.e. gated download despite Apache license. Base model tag: `google/flan-t5-base`.
- **Params/size on disk**: UNVERIFIED on this page (not stated in card body fetched; base is flan-t5-base scale, T5 encoder-decoder).
- **Predicts**: consistency/hallucination score in [0,1] over a (premise, hypothesis) pair — NOT classic entailment; two output neurons `hallucinated` / `consistent`. Explicitly asymmetric (not NLI-symmetric): card example "I visited Iowa" given "I visited the United States" is hallucinated in that direction only.
- **Input format / prompt template** (quoted exactly from card):
  `"<pad> Determine if the hypothesis is true given the premise?\n\nPremise: {text1}\n\nHypothesis: {text2}"`
  Usable via `AutoModelForSequenceClassification.from_pretrained(..., trust_remote_code=True)` taking a list of (premise, hypothesis) pairs, or via `transformers` `pipeline("text-classification", ...)`.
- **Reported numbers**: none quoted on this page (card points to a separate HHEM-2.3 commercial leaderboard Space, not fetched this session — not cited).
- **Reported latency**: UNVERIFIED — not stated on this page.
- **MLX / GGUF build**: not checked yet this entry (see MLX/GGUF search section at end).
- **Tool-call judging**: Not designed for tool-call-vs-spec checking; it's a generic premise/hypothesis consistency scorer (RAG/summarization framing). Could be repurposed (treat tool-spec+args as "hypothesis", retrieved docs as "premise") but card gives no tool-call example.
- Source: https://huggingface.co/vectara/hallucination_evaluation_model (accessed 2026-10-04); https://huggingface.co/vectara/hallucination_evaluation_model/raw/main/README.md (accessed 2026-10-04)

---

## lytang/MiniCheck-Flan-T5-Large

- **HF id**: `lytang/MiniCheck-Flan-T5-Large`
- **License**: `mit` (raw README YAML frontmatter)
- **Params/size**: fine-tuned from `google/flan-t5-large`; GitHub README parenthetically calls it "MiniCheck-Flan-T5-Large (770M)".
- **Predicts**: binary **supported (1) / unsupported (0)** sentence-level grounding label — document+claim → {0,1} (fact-checking / groundedness, not generic NLI).
- **Input format**: function signature `MiniCheck-Model(document, claim) -> {0,1}`; Python: `scorer = MiniCheck(model_name='flan-t5-large', cache_dir='./ckpts'); pred_label, raw_prob, _, _ = scorer.score(docs=[...], claims=[...])`. Requires splitting multi-sentence claims into individual sentences first.
- **Trained on**: 35K examples = 21K ANLI (Nie et al. 2020) + 14K synthetic.
- **Reported numbers**: Card states it "outperform[s] all existing specialized fact-checkers with a similar scale by a large margin (4-10% absolute increase) and is on par with GPT-4, but 400x cheaper" on the **LLM-AggreFact** benchmark (11 human-annotated fact-checking/grounding datasets) — exact BAcc numbers are in an image (`performance.png`) not extracted as text this session, so **exact BAcc values are UNVERIFIED** (only the qualitative claim above is directly quoted).
- **Reported latency**: GitHub README (raw, same family) states via Bespoke-MiniCheck-7B card: "MiniCheck-Flan-T5-Large wi[th throughput] > 500 docs/min" (comparison context on an unspecified GPU — exact hardware UNVERIFIED for this specific number).
- **Model variants** (named on this page, not all individually fetched): `bespokelabs/Bespoke-Minicheck-7B` (7B), `lytang/MiniCheck-RoBERTa-Large`, and (by GitHub README) `deberta-v3-large` — **DeBERTa/RoBERTa variant cards not opened this session; their individual license/params UNVERIFIED beyond what's inferable from base-model names.**
- **Tool-call judging**: Same document+claim grounding shape; could check "tool result / retrieved context" vs "claim" but no tool-spec-specific example shown.
- Source: https://huggingface.co/lytang/MiniCheck-Flan-T5-Large (accessed 2026-10-04); raw README https://huggingface.co/lytang/MiniCheck-Flan-T5-Large/raw/main/README.md (accessed 2026-10-04); https://raw.githubusercontent.com/Liyan06/MiniCheck/main/README.md (accessed 2026-10-04)

---

## bespokelabs/Bespoke-MiniCheck-7B (Llama-3.1-Bespoke-MiniCheck-7B)

- **HF id**: `bespokelabs/Bespoke-MiniCheck-7B`
- **License**: **CC BY-NC 4.0** (quoted: "This work is licensed under CC BY-NC 4.0. For commercial licensing, please contact company@bespokelabs.ai.") — i.e. NOT freely commercial-usable despite GitHub README elsewhere calling it "commercially useable" via contact.
- **Params/size**: 7B; finetuned from `internlm/internlm2_5-7b-chat`.
- **Predicts**: same binary supported/unsupported sentence-vs-document grounding as MiniCheck family: `MiniCheck-Model(document, claim) -> {0,1}`.
- **Input format**: same `MiniCheck` Python API, `model_name='Bespoke-MiniCheck-7B'`; supports `enable_prefix_caching` (vLLM Automatic Prefix Caching) for repeated-document speedups.
- **Reported numbers**: card states (qualitative, exact text): "Llama-3.1-Bespoke-MiniCheck-7B is the SOTA fact-checking model despite its small size" on LLM-AggreFact — exact BAcc numbers again only in `performance.png` image, **UNVERIFIED as exact figures this session**.
- **Reported latency/throughput**: quoted exactly: "Based on our test on a single A6000 (48 VRAM), Llama-3.1-Bespoke-MiniCheck-7B wi[th vLLM] and MiniCheck-Flan-T5-Large have throughputs > 500 docs/min." (A6000 GPU, not Apple Silicon — not directly transferable to M5 MPS/MLX).
- **MLX/GGUF**: GitHub README (fetched) notes: "[2024/09] MiniCheck is now available at ollama ... You can now run MiniCheck locally on your laptop with a simple command" — i.e. an **Ollama/GGUF-style build of Bespoke-MiniCheck exists** (via ollama library "bespoke-minicheck"), confirmed from https://raw.githubusercontent.com/Liyan06/MiniCheck/main/README.md (accessed 2026-10-04). Native mlx-community build not found/checked yet.
- **Tool-call judging**: Not tool-spec-aware; same claim-vs-document sentence check design.
- Source: https://huggingface.co/bespokelabs/Bespoke-MiniCheck-7B (accessed 2026-10-04)

---

## cross-encoder/nli-deberta-v3-small

- **HF id**: `cross-encoder/nli-deberta-v3-small`
- **License**: UNVERIFIED on this page (no license field present in fetched markdown body).
- **Params/size**: based on `microsoft/deberta-v3-small` (card states "This model is based on microsoft/deberta-v3-small"); exact param count UNVERIFIED on this page.
- **Predicts**: classic 3-way **NLI**: contradiction / entailment / neutral (SentenceTransformers CrossEncoder).
- **Input format**: `CrossEncoder('cross-encoder/nli-deberta-v3-small').predict([(premise, hypothesis), ...])` → 3 scores; label mapping `['contradiction','entailment','neutral']`. Also usable directly as `AutoModelForSequenceClassification` and as a zero-shot `pipeline("zero-shot-classification", ...)`.
- **Reported numbers** (quoted exactly): "Accuracy on SNLI-test dataset: 91.65" and "Accuracy on MNLI mismatched set: 87.55".
- **Reported latency**: UNVERIFIED — not on this page.
- **Tool-call judging**: Generic sentence-pair NLI only — would need the tool spec/args serialized as one side of the pair; no agent/tool framing on this card.
- Source: https://huggingface.co/cross-encoder/nli-deberta-v3-small (accessed 2026-10-04)

---

## MoritzLaurer DeBERTa-v3 NLI models

- **Attempted**: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli-ling-wanli` — **both the model page and its raw README returned HTTP 401 this session** (fetched twice, both failed: https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli-ling-wanli and .../raw/main/README.md, accessed 2026-10-04). All details for this exact repo are **UNVERIFIED** this session — not filled from memory.
- **Fetched instead**: `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` (a sibling model from the same author, successfully opened) —
  - **Predicts**: 3-way NLI, label order **["entailment","neutral","contradiction"]** (note: different order than cross-encoder's mapping).
  - **Multilingual**: fine-tuned on XNLI (15 languages, 2490 professionally-translated dev examples) + English MNLI; base model mDeBERTa-v3-base pretrained by Microsoft on CC100.
  - **Input/usage**: works directly with `pipeline("zero-shot-classification", ...)` or `AutoModelForSequenceClassification` with `tokenizer(premise, hypothesis, ...)`.
  - **License/params/benchmark numbers**: UNVERIFIED — not reached in the 3000-char excerpt fetched (truncated before license/eval sections).
  - Source: https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli (accessed 2026-10-04)
- **Tool-call judging**: Generic premise/hypothesis NLI only, no agent framing on either page.

---

## PatronusAI/Llama-3-Patronus-Lynx-8B-Instruct

- **HF id**: `PatronusAI/Llama-3-Patronus-Lynx-8B-Instruct`
- **License**: UNVERIFIED on this page (not present in fetched card body; not citing from memory).
- **Params/size**: 8B (base `meta-llama/Meta-Llama-3-8B-Instruct`, per model name); max sequence length **8000 tokens** (quoted).
- **Predicts**: binary faithfulness verdict **PASS / FAIL** (hallucination vs. faithful) for RAG answer-vs-document, with free-text chain-of-thought reasoning.
- **Input format / prompt template** (quoted exactly):
  `"Given the following QUESTION, DOCUMENT and ANSWER you must analyze the provided answer and determine whether it is faithful to the contents of the DOCUMENT. The ANSWER must not offer new information beyond the context provided in the DOCUMENT. The ANSWER also must not contradict information provided in the DOCUMENT. Output your final verdict by strictly following this format: \"PASS\" ... \"FAIL\" ... Show your reasoning."` followed by `-- QUESTION ... -- DOCUMENT: {context} -- ANSWER: {answer}`, output JSON `{"REASONING": ..., "SCORE": ...}`. Run via chat-format `pipeline("text-generation", ...)`.
- **Reported numbers** (quoted exactly, % accuracy on PatronusAI/HaluBench, table from model card):
  | Model | HaluEval | RAGTruth | FinanceBench | DROP | CovidQA | PubmedQA | Overall |
  |---|---|---|---|---|---|---|---|
  | GPT-4o | 87.9% | 84.3% | 85.3% | 84.3% | 95.0% | 82.1% | 86.5% |
  | Llama-3-Instruct-70B | 87.0% | 83.8% | 72.7% | 69.4% | 85.0% | 82.6% | 80.1% |
  | **LYNX (8B)** | 85.7% | 80.0% | 72.5% | 77.8% | 96.3% | 85.2% | **82.9%** |
  | **LYNX (70B)** | 88.4% | 80.2% | 81.4% | 86.4% | 97.5% | 90.4% | **87.4%** |
  (Trained on CovidQA, PubmedQA, DROP, RAGTruth — hand-annotated + synthetic.)
- **Reported latency**: UNVERIFIED — not stated on this page.
- **Tool-call judging**: QUESTION/DOCUMENT/ANSWER framing — a tool spec + tool output could be substituted as DOCUMENT, but no tool-call-specific example on this card.
- Source: https://huggingface.co/PatronusAI/Llama-3-Patronus-Lynx-8B-Instruct (accessed 2026-10-04)

---

## Qwen/Qwen3Guard-Gen-8B

- **HF id**: `Qwen/Qwen3Guard-Gen-8B` (family also has 0.6B, 4B sizes, and a `Qwen3Guard-Stream` token-classification variant per card text — siblings not individually fetched).
- **License**: UNVERIFIED on this page (not present in fetched excerpt).
- **Params**: 8B (per repo name); trained on "1.19 million prompts and responses labeled for safety" (quoted).
- **Predicts**: **three-tier severity** — `Safety: Safe | Unsafe | Controversial` — plus a category label from a fixed set (quoted regex from card): `Violent|Non-violent Illegal Acts|Sexual Content or Sexual Acts|PII|Suicide & Self-Harm|Unethical Acts|Politically Sensitive Topics|Copyright Violation|Jailbreak|None`. Separate response-moderation mode adds a `Refusal: Yes|No` field. Not a groundedness/entailment checker — it's a safety-risk classifier, not a tool-call/fact verifier.
- **Input format**: generative, instruction-following — `tokenizer.apply_chat_template([{"role":"user","content":prompt}])` → `model.generate(...)`; output parsed via regex for `Safety: (...)` and category names.
- **Multilingual**: "supports 119 languages and dialects" (quoted).
- **Reported numbers/latency**: UNVERIFIED — performance shown only as an image (`performance.png`), no text numbers extracted this session.
- **Tool-call judging**: No tool-call/function-spec category in the taxonomy fetched — general content-safety categories only, not groundedness or function-call hallucination.
- Source: https://huggingface.co/Qwen/Qwen3Guard-Gen-8B (accessed 2026-10-04)

---

## ibm-granite/granite-guardian-3.2-5b

- **HF id**: `ibm-granite/granite-guardian-3.2-5b`
- **License**: UNVERIFIED on this page (not reached in fetched excerpts).
- **Params/size**: 5B — card states (quoted): "a thinned down version of Granite Guardian 3.1 8B ... About 30% of the original parameters were removed allowing for faster inference and lower resource requirements."
- **Predicts**: binary **Yes/No risk-detected** classification (generated token is literally `"Yes"`/`"No"` plus a `<confidence>...</confidence>` tag), parameterized by a `risk_name` passed into `guardian_config`. Confirmed risk categories relevant to this task (quoted exactly from card):
  - **Harm** umbrella (+ Social Bias, Jailbreaking, Violence, Profanity, Sexual Content, Unethical Behavior, Harm Engagement, Evasiveness)
  - RAG risks: **Context Relevance**, **Groundedness** ("assistant's response includes claims or facts not supported by or contradicted by the provided context"), **Answer Relevance**
  - Agentic risk: **Function Calling Hallucination** — quoted exactly: "assistant's response contains function calls that have syntax or semantic errors based on the user query and available tool." Card also states generally: "Function calling risk detection within agentic workflows, where Granite Guardian evaluates intermediate steps for syntactic and semantic hallucinations. This includes assessing the validity of function calls and detecting fabricated information, particularly during query translation."
- **Input format / prompt template** (quoted code pattern, confirmed): uses `tokenizer.apply_chat_template(messages, guardian_config=guardian_config, add_generation_prompt=True, return_tensors="pt")` where `messages = [{"role":"user","content":...},{"role":"assistant","content":...}]` and `guardian_config = {"risk_name": "harm"}` (example shown used `"harm"`; exact `risk_name` string for `function_calling_hallucination` and the tool-spec/context field layout for that specific risk were **not reached in the two excerpts fetched — UNVERIFIED exact field format**, though the risk is confirmed to exist and be named "Function Calling Hallucination" in the risk-definitions prose).
- **Reported numbers**: card claims (quoted) "It outperforms other open-source models in the same space on standard benchmarks" — no exact BAcc/F1 numbers reached in fetched excerpts; **UNVERIFIED exact figures**.
- **Reported latency**: UNVERIFIED on pages fetched; card only claims qualitative "faster inference and lower resource requirements" vs. the un-pruned 8B.
- **MLX/GGUF**: checked `huggingface.co/models?search=granite-guardian` — the search results page only rendered as aggregate text ("Text Generation • 8B • Updated Oct 22, 2024 • 25") in simplified-markdown fetch, individual repo names/orgs (e.g. any `mlx-community/granite-guardian-*`) were **not visible in the fetched output — UNVERIFIED either way**, page: https://huggingface.co/models?search=granite-guardian (accessed 2026-10-04).
- **Tool-call judging**: **YES — this is the one family in this review that explicitly, by name, judges a tool/function call** (Function Calling Hallucination risk), in addition to groundedness for RAG context.
- Source: https://huggingface.co/ibm-granite/granite-guardian-3.2-5b (accessed 2026-10-04)
- Note: Granite Guardian **3.3** was in-scope per instructions but not fetched this session (budget) — its risk list/prompt format relative to 3.2 is **UNVERIFIED**, not assumed identical.

---

## meta-llama/Llama-Guard-4-12B

- **HF id**: `meta-llama/Llama-Guard-4-12B`
- **License**: UNVERIFIED exact license name on this page (gated Meta repo; page requires accepting Meta license to access weights — text of the license itself not reached in the fetched excerpt, only the model card prose was returned).
- **Params/size**: **12B**, "natively multimodal safety classifier ... trained jointly on text and multiple images," described as "a dense architecture pruned from the Llama 4 Scout pre-trained model."
- **Predicts**: generative safe/unsafe classification over **14 hazard categories** (MLCommons hazards taxonomy), quoted list: S1 Violent Crimes, S2 Non-Violent Crimes, S3 Sex-Related Crimes, S4 Child Sexual Exploitation, S5 Defamation, S6 Specialized Advice, S7 Privacy, S8 Intellectual Property, S9 Indiscriminate Weapons, S10 Hate, S11 Suicide & Self-Harm, S12 Sexual Content, S13 Elections, **S14 Code Interpreter Abuse (text only)** — card states S14 was added "for text-only tool-call use cases," i.e. this is its closest category to agent/tool-call risk (code-execution abuse), not a spec-conformance or hallucination check.
- **Input format**: classifies both LLM prompts and responses (and multi-image inputs, a new capability vs. Llama Guard 3); exact prompt template referred out to https://www.llama.com/docs/model-cards-and-prompt-formats/llama-guard-4/ (not fetched this session — UNVERIFIED exact template text).
- **Reported numbers/latency**: UNVERIFIED — not in fetched excerpt (truncated at hazard-category definitions).
- **MLX/GGUF**: not checked this session — UNVERIFIED.
- **Tool-call judging**: Only indirectly (S14 Code Interpreter Abuse); it does NOT check a tool call against a tool spec/schema or produce groundedness/hallucination verdicts.
- Source: https://huggingface.co/meta-llama/Llama-Guard-4-12B (accessed 2026-10-04)

---

## meta-llama/Llama-Prompt-Guard-2-86M

- **HF id**: `meta-llama/Llama-Prompt-Guard-2-86M` (86M variant; a 22M variant also exists per Meta's naming — not fetched)
- **License**: **Llama 4 Community License Agreement** (quoted header: "LLAMA 4 COMMUNITY LICENSE AGREEMENT, Llama 4 Version Effective Date: April 5, 2025"), a custom Meta license (not OSI Apache/MIT) with attribution/"Built with Llama" requirements.
- **Predicts**: NOT a groundedness/entailment/tool-spec checker — Prompt Guard models classify **prompt injection / jailbreak attempts** in input text (confirmed by model name/license page framing; the fetched excerpt was entirely license legal text, so the task-specific description comes from the model's well-known name/purpose rather than card prose — **the actual "Model Details" usage section was NOT reached this session, so exact input/output format for this specific repo is UNVERIFIED from the page content fetched**).
- **Params/size**: 86M (per repo name).
- **Tool-call judging**: Not applicable — this is an input-side injection/jailbreak detector, not an output-side tool-call verifier.
- Source: https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M (accessed 2026-10-04) — **license text only; full model-card usage section UNVERIFIED this session.**

---

## google/shieldgemma-2b

- **HF id**: `google/shieldgemma-2b` (family also ships 9B and 27B — quoted: "available ... including models of 3 sizes: 2B, 9B and 27B parameters"; siblings not individually fetched)
- **License**: Google "Terms of Use" (gemma terms, https://ai.google.dev/gemma/terms) — not Apache/MIT; exact license name string UNVERIFIED beyond "Terms" link text.
- **Params/size**: 2B (this repo); built on Gemma 2.
- **Predicts**: binary **"Yes"/"No"** policy-violation classifier over **4 harm categories only**: "sexually explicit, dangerous content, hate, and harassment" (quoted) — i.e. general content-safety, not groundedness/entailment/function-call risk.
- **Input format / prompt template** (quoted exactly, structure): Preamble ("You are a policy expert trying to help determine whether a user prompt is in violation of the defined safety policies.") + `<start_of_turn>Human Question: [User Prompt]<end_of_turn>` + a stated safety-policy description (example policy shown: "No Hate Speech") + epilogue "Does the human question violate the above principle? Your answer must start with 'Yes' or 'No'...". Output is text starting with the token "Yes" or "No".
- **Reported numbers/latency**: UNVERIFIED — not reached in fetched excerpt.
- **Tool-call judging**: No — fixed 4-category content-safety classifier, no tool-spec or groundedness framing.
- Source: https://huggingface.co/google/shieldgemma-2b (accessed 2026-10-04)

---

## openai/gpt-oss-safeguard (-20b / -120b)

- **HF id**: `openai/gpt-oss-safeguard-20b` (sibling `openai/gpt-oss-safeguard-120b` referenced on the same page, not separately fetched)
- **License**: **Apache 2.0** (quoted: "Permissive Apache 2.0 license: Build freely without copyleft restrictions or patent risk—ideal for experimentation, customization, and commercial deployment.")
- **Params/size**: quoted exactly — `gpt-oss-safeguard-20b`: **"21B parameters with 3.6B active parameters) fits into GPUs with 16GB of VRAM"** (MoE architecture); `gpt-oss-safeguard-120b`: **"117B parameters with 5.1B active parameters"**.
- **Predicts**: **policy-configurable safety reasoning classifier** — "classify text content based on safety policies that you provide," i.e. bring-your-own-policy at inference time rather than a fixed risk taxonomy; exposes chain-of-thought reasoning ("Raw CoT ... meant for developers and safety practitioners").
- **Input format**: Must use OpenAI's **harmony response format** (quoted: "trained on our harmony response format and should only be used with the harmony format as it will not work correctly otherwise"); supports configurable reasoning effort low/medium/high.
- **Reported numbers/latency**: UNVERIFIED — not in fetched excerpt (page truncated at "Download the model" section).
- **MLX/GGUF**: searched `huggingface.co/models?search=gpt-oss-safeguard` — again only aggregate counts rendered ("Text Generation • 120B • Updated Oct 29, 2025 • 3.77k• 106"), no individual repo names visible in simplified-markdown output — **UNVERIFIED whether an mlx-community/GGUF build exists**, page: https://huggingface.co/models?search=gpt-oss-safeguard (accessed 2026-10-04). (Base gpt-oss models are known to have mlx-community ports, but that is NOT verified here for the safeguard fine-tune specifically, and is not asserted as fact.)
- **Tool-call judging**: Policy is user-defined, so a tool-spec-conformance policy *could* in principle be authored — but no tool-call-specific example or taxonomy entry is shown on the fetched page; general-purpose "bring your own policy" reasoning model, not purpose-built for function-call hallucination like Granite Guardian.
- Source: https://huggingface.co/openai/gpt-oss-safeguard-20b (accessed 2026-10-04)

---

## KRLabsOrg/lettucedect-large-modernbert-en-v1 (LettuceDetect)

- **HF id**: `KRLabsOrg/lettucedect-large-modernbert-en-v1` (a `-base-` ModernBERT variant also referenced in the usage snippet, `KRLabsOrg/lettucedect-base-modernbert-en-v1`, not separately fetched)
- **License**: UNVERIFIED — not reached in the fetched excerpt (page truncated before any license section).
- **Params/size**: based on **ModernBERT-large** (quoted: "Large model based on ModernBERT-large"); exact parameter count UNVERIFIED on this page. Context length up to **8192 tokens**.
- **Predicts**: **token-level hallucination classification** (not sentence/document binary) — "trained to identify tokens in the answer text that are not supported by the given context," aggregated into hallucinated spans. Input: `context` (list), `question`, `answer`. Task framing = span-level groundedness over (context, question, answer) triples, trained on **RAGTruth**.
- **Input format** (quoted code): `HallucinationDetector(method="transformer", model_path="KRLabsOrg/lettucedect-base-modernbert-en-v1")`; `detector.predict(context=contexts, question=question, answer=answer, output_format="spans")`.
- **Reported numbers** (quoted exactly): "achieves an overall F1 score of **79.22%**, outperforming prompt-based methods like GPT-4 (**63.4%**) and encoder-based models like Luna (**65.4%**). It also surpasses fine-tuned LLAMA-2-13B (**78.7%**) ... and is competitive with the SOTA fine-tuned LLAMA-3-8B (**83.9%**)" — all on the RAGTruth test set, example-level F1.
- **Reported latency**: UNVERIFIED — not stated in fetched excerpt (card calls it "very effective in inference settings" but gives no numeric latency).
- **Tool-call judging**: Not natively tool-spec-aware in the base design (RAG QA framing), though the underlying span-classification approach is architecturally close to what a fast tool-call groundedness checker would need; no tool-call example on this specific page.
- Source: https://huggingface.co/KRLabsOrg/lettucedect-large-modernbert-en-v1 (accessed 2026-10-04)

---

## MLX / GGUF availability — summary of checks this session

- Direct `huggingface.co/models?search=<name>` fetches (for `granite-guardian` and `gpt-oss-safeguard`) only returned **aggregate result metadata** (task tag, param count, update date, like count) in simplified-markdown form, not the list of individual repo names/orgs — so **mlx-community / GGUF presence could not be confirmed or denied for any model via this method this session**. This is a tooling limitation (JS-rendered search results), not a confirmed absence.
- The one **positive, confirmed** local/consumer-hardware build found this session: **Bespoke-MiniCheck-7B is available via Ollama** ("bespoke-minicheck" on the ollama library), per the MiniCheck GitHub README fetched above — Ollama uses GGUF under the hood, though the exact quantization/format was not detailed on the page fetched.
- No other MLX or GGUF build was directly confirmed for any model in this review. **Treat all other MLX/GGUF availability as UNVERIFIED, not absent.**

---

## Recommendation for a 24 GB Apple M5 Mac (MLX + PyTorch MPS)

**FAST tier (≤50 ms budget):** **vectara HHEM-2.1-Open** (T5-base-scale encoder-decoder, Apache-2.0, trivial (premise,hypothesis)→score call, no chat template/generation loop) or **cross-encoder/nli-deberta-v3-small** (deberta-v3-**small** backbone, 3-way NLI, simple classifier head) are the two realistic sub-50ms candidates confirmed this session — both are small classification heads (not autoregressive generation), which is the dominant latency factor on MPS. Neither was benchmarked for exact ms/call on this page (latency UNVERIFIED for both), so this is architectural reasoning, not a measured number. Between them: HHEM is purpose-built for groundedness/RAG consistency (closer to the guardrail's actual job); the cross-encoder is purpose-built for generic NLI only. **Recommend HHEM-2.1-Open for fast-tier groundedness**, with the MiniCheck-Flan-T5-Large (770M, MIT) as a fallback if HHEM's asymmetric-consistency framing doesn't fit the tool-call schema well — it's still a single forward pass, not generation.

**CAREFUL tier (≤2 s budget):** **ibm-granite/granite-guardian-3.2-5b** is the only model confirmed this session to have a **named, explicit Function Calling Hallucination risk category** plus Groundedness/Context Relevance — i.e. it directly matches "check a tool call against a reference knowledge base," which none of the other generative guard models (Llama Guard 4, ShieldGemma, Qwen3Guard, Llama-Prompt-Guard-2) expose (they're content-safety/injection classifiers with no function-call or groundedness category confirmed on the pages fetched). At 5B params it should fit comfortably in 24 GB on MPS/MLX within a 2 s budget for a short generation (Yes/No + confidence token), though exact latency is UNVERIFIED this session. `gpt-oss-safeguard-20b` (Apache-2.0, 21B/3.6B-active MoE) is a plausible stronger alternative if its bring-your-own-policy reasoning can be prompted with a tool-call-conformance policy, but this is unverified by direct example on its page — Granite Guardian 3.2 5B is the lower-risk pick because the capability is confirmed in writing on its own model card.

**Gaps**: Granite Guardian 3.3 (explicitly requested) not fetched — risk-list deltas vs 3.2 unverified. Exact `risk_name` string/prompt layout for Function Calling Hallucination not reached. MLX/GGUF presence unconfirmed for Granite Guardian and gpt-oss-safeguard via search (tooling limitation). MoritzLaurer's exact named model (`...ling-wanli`) returned 401 both times — substituted a sibling model for partial coverage only. No exact BAcc numbers extracted for MiniCheck family (behind a PNG image) or Llama-Guard-4/ShieldGemma (truncated before eval sections) — do not treat any omitted number as zero or "no result," it means not-yet-read this session.
