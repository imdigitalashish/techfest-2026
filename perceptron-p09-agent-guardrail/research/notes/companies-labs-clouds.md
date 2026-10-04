# What companies ship today — checking agent actions/tool calls (official sources only)

Research date: 2026-10-04. Only pages opened this session (web_fetch) are cited. Quotes are verbatim. Unconfirmed items marked UNVERIFIED.

---

## OpenAI

### 1. Agents SDK — Tool Guardrails & Tripwires
- **Status**: Shipping (Python SDK docs, current as of session date; no explicit GA/preview label on page).
- **URL**: https://openai.github.io/openai-agents-python/guardrails/ (accessed 2026-10-04)
- **Mechanism**: Intercepts at three points — input guardrails (on initial user input, first agent only), output guardrails (on final agent output, last agent only), and **tool guardrails** ("run on every guarded function-tool invocation, including local MCP tools when their server configures guardrails, with input guardrails before execution and output guardrails after execution"). Checks against: arbitrary custom guardrail function logic (e.g., a secondary "fast/cheap model" classifier) — the page's own example is "a malicious user asking a smart model to help with math homework," i.e., policy/intent checks, not a fixed KB.
- **Does it check tool-call ARGUMENTS against a knowledge source?** Partially confirmed by a related search excerpt (not a verbatim quote from an opened page): a `tool_input_guardrail`-decorated function receives `ToolGuardrailFunctionOutput` and can inspect `data.context.tool_arguments` before execution — this is argument inspection via custom code, not a built-in KB lookup. The opened docs page itself describes only the general input/output/tool-guardrail architecture and tripwire mechanics (quoted above), not a specific "check args against documents" feature. UNVERIFIED whether any built-in (non-custom) knowledge-source check exists.
- **Tripwire mechanism (quoted)**: "we check if `.tripwire_triggered` is true. If true, an `InputGuardrailTripwireTriggered` exception is raised, so you can appropriately respond to the user or handle the exception." Also: "Blocking execution guarantees that the expensive model does not start; with parallel execution, the expensive model may already have started before the guardrail completes."
- **Published numbers**: None found on this page.
- **Human approval trigger**: Not itself a human-approval UI — guardrails raise exceptions/halt the run programmatically; the calling application decides what to do next (e.g., prompt a human). No built-in approval UI described on this page.

### 2. gpt-oss-safeguard
- **Status**: Released (per search-derived context, not independently verified via an opened OpenAI blog page — the openai.com/index/introducing-gpt-oss-safeguard/ URL returned HTTP 403 when fetched this session, so its date/claims are UNVERIFIED first-hand).
- **URL opened**: https://developers.openai.com/cookbook/articles/gpt-oss-safeguard-guide (accessed 2026-10-04)
- **Mechanism**: "gpt-oss-safeguard is a first open weight reasoning model specifically trained for safety classification tasks to help classify text content based on customizable policies... This enables **bring-your-own-policy** Trust & Safety AI, where your own taxonomy, definitions, and thresholds guide classification decisions." Contrast quoted: "Prebaked safety models (like ShieldGemma, LlamaGuard, RoGuard, etc) come with built-in definitions of what counts as 'unsafe' and fixed policy taxonomies" vs. gpt-oss-safeguard which is "a policy-following model that can reliably interpret and enforce **your own written standards and tell you why it made the decision it made**." Checks against: developer-supplied **policy text** (passed as the system-role content with the "harmony" response format), not tool-call arguments specifically, not a fixed KB — it's a general content/text classifier, applicable to moderation/Trust & Safety, not documented here as a tool-call pre-execution guardrail per se.
- **Does it check tool-call ARGUMENTS against a knowledge source?** No evidence on the opened page — this is a text/content classifier for Trust & Safety moderation (policy prompt + content to classify), not described as a tool-argument-vs-KB verifier.
- **Published numbers**: None on the opened cookbook page.
- **Human approval trigger**: Not applicable / not described — it outputs a classification with chain-of-thought reasoning for a downstream system to act on.

### 3. ChatGPT agent — confirmations / watch mode
- **Status**: Shipping (official Help Center article; no version/date stamp visible on page).
- **URL**: https://help.openai.com/en/articles/11752874-chatgpt-agent (accessed 2026-10-04)
- **Mechanism (quoted)**: "ChatGPT agent incorporates multiple safeguards, including user confirmations for high-impact actions, refusal patterns for disallowed tasks, prompt injection monitoring, and a 'watch mode' requiring user supervision on certain sites." Intercepts at the point of high-impact/sensitive actions (e.g., sites with sensitive data) by pausing for explicit user confirmation, or requiring the user to actively supervise ("watch mode") on certain sites before continuing.
- **Does it check tool-call ARGUMENTS against a knowledge source?** Not described — this is a human-in-the-loop confirmation/supervision gate plus "prompt injection monitoring," not a documented argument-vs-KB verification step. No schema/KB check detailed.
- **Published numbers**: None quoted on page.
- **How human approval is triggered**: Quoted above — "user confirmations for high-impact actions" and "watch mode requiring user supervision on certain sites." Explicit caveat quoted: "these measures don't eliminate all risks. It remains important to monitor ChatGPT agent and exercise care."

---

## Anthropic

### 1. Claude Code hooks — PreToolUse
- **Status**: Shipping (docs reference Claude Code v2.1.x; dated docs, no explicit GA label, actively versioned).
- **URL**: https://code.claude.com/docs/en/hooks (accessed 2026-10-04)
- **Mechanism**: Intercepts "on every tool call inside the agentic loop: `PreToolUse` and `PostToolUse`, except `EndConversation` calls, which skip both." Quoted: "`PreToolUse` | Before a tool call executes. Can block it." Also fires `PermissionRequest` "When a tool call needs a permission decision" and `PermissionDenied` "When auto mode denies a tool call, including denials without a classifier verdict." Checks against: **custom user-defined hook handler logic** — "Hooks are user-defined shell commands, HTTP endpoints, MCP tool calls, LLM prompts, or subagents that execute automatically at specific points." Input arrives via stdin (command hooks) or POST body (HTTP hooks) as JSON tool-call context; the hook script itself decides allow/block — Claude Code supplies the mechanism, not a built-in KB/policy source.
- **Does it check tool-call ARGUMENTS against a knowledge source?** The hook receives full JSON tool-call context (implying arguments) and can inspect/block, but this is developer-written logic — no built-in "check against documents" feature is described on this page.
- **Published numbers**: None quoted.
- **Human approval trigger**: Via `PermissionRequest` hook event ("When a tool call needs a permission decision") and the permission-mode system (see below).

### 2. Permission modes (incl. sandboxing)
- **Status**: Shipping; "With Claude Code v2.1.283 or later, auto mode is the built-in starting permission mode for interactive terminal and VS Code sessions."
- **URL**: https://code.claude.com/docs/en/permission-modes (accessed 2026-10-04); sandbox detail at https://code.claude.com/docs/en/sandboxing (accessed 2026-10-04)
- **Mechanism (quoted)**: "In Manual mode, Claude Code stops and asks you before most actions that edit files, run shell commands, or reach the network. In auto mode, a second model, the classifier, reviews actions instead of you." Modes table: `default` (Reads only), `acceptEdits`, `plan`, `auto` ("Everything, with background safety checks"), `dontAsk`, `bypassPermissions`. Checks against: a **second-model classifier** (in `auto` mode) evaluating the specific action, not a fixed KB — plus static allow/deny/ask rule lists.
- **Sandboxing mechanism (quoted)**: "The Bash sandbox is a boundary that the operating system enforces around the shell commands Claude runs on your machine... Because the operating system applies the limits while a command runs, Claude Code can run sandboxed commands without asking you to approve each one." Enforced via OS primitives: "macOS: sandboxing uses the built-in Seatbelt framework"; "Linux and WSL2: the sandbox relies on `bubblewrap` and `socat`." Network: "No direct route out. Connections go through a proxy on your machine that checks each host against your allowed domains, which start empty." Built on open-source `@anthropic-ai/sandbox-runtime` package. Important scope limit (quoted): "The sandbox covers shell commands only. Claude's file tools, MCP servers, and hooks run outside it."
- **Does it check tool-call ARGUMENTS against a knowledge source?** No — permission modes check actions against **rule lists (allow/deny/ask) and a classifier model's judgment**, not against a document/KB. Sandboxing is a pure OS-level capability restriction (filesystem/network boundary), not an argument-vs-source check.
- **Published numbers**: None quoted on these pages.
- **Human approval trigger**: Manual mode asks before "most actions that edit files, run shell commands, or reach the network"; `auto` mode escalates to human only when the classifier's background safety check doesn't clear the action (exact escalation criteria not quoted verbatim beyond "background safety checks"); ask-rules and `AskUserQuestion`/`requiresUserInteraction`-tagged MCP tools "always fall through to the callback" (from the permissions page fetched earlier) — i.e., explicit always-ask tool tags trigger a human prompt regardless of mode (except `dontAsk`, which denies instead of asking).

### 3. Claude Agent SDK — permissions / `canUseTool`
- **Status**: Shipping (Agent SDK docs).
- **URL**: https://code.claude.com/docs/en/agent-sdk/permissions (accessed 2026-10-04)
- **Mechanism (quoted)**: Six-step evaluation order — "Hooks" → "Deny rules" → "Ask rules" → "Permission mode" → "Allow rules" → "`canUseTool` callback". "If not resolved by any of the above, call your `canUseTool` callback for a decision. In `dontAsk` mode, this step is skipped and the tool is denied." Checks tool name + input against static allow/deny/ask rule lists first, then a developer-supplied runtime callback.
- **Does it check tool-call ARGUMENTS against a knowledge source?** The `canUseTool` callback receives the tool's name and **input (arguments)** for a programmatic decision — this is developer-defined logic, not a built-in KB-verification feature. Scoped rules like `Bash(rm *)` show argument-level pattern matching is supported for deny rules specifically.
- **Published numbers**: None quoted.
- **Human approval trigger**: "Ask rules" and interaction-required tools (`AskUserQuestion`, MCP tools tagged `requiresUserInteraction`) "always fall through to the callback" for confirmation, "even when an allow rule matches" — except in `dontAsk` mode, which denies instead of prompting.

### 4. Published agent-monitoring classifier
- **Status**: Confirmed existence, but Anthropic does not appear to publish it as a separate product on the pages opened this session — it is referenced only as an internal mechanism of Claude Code's `auto` permission mode.
- **URL**: https://code.claude.com/docs/en/permission-modes (accessed 2026-10-04)
- **Mechanism (quoted)**: "In auto mode, a second model, the classifier, reviews actions instead of you; how the classifier evaluates actions lists which actions it reviews and which skip it." The classifier's exact evaluation criteria (beyond what's quoted) were in a section not retrieved (truncated) — UNVERIFIED beyond this summary statement.
- **Does it check tool-call ARGUMENTS against a knowledge source?** UNVERIFIED — page states the classifier "reviews actions" but the detailed evaluation logic section was truncated before fetch; no KB/document check is mentioned in the retrieved text.
- **Published numbers**: None quoted.
- **Human approval trigger**: Actions the classifier does not clear presumably escalate to the user (implied, not verbatim-quoted in retrieved text).

---

## Google

### 1. ADK — `before_tool_callback` / plugins
- **Status**: Shipping. Quoted support line: "Supported in ADK Python v0.1.0 TypeScript v0.2.0 Go v0.1.0 Java v0.1.0 Kotlin v0.1.0."
- **URL**: https://google.github.io/adk-docs/callbacks/ (redirected to https://adk.dev/callbacks/) (accessed 2026-10-04)
- **Mechanism (quoted)**: "Before executing a tool (like a Python function or another agent) or after it finishes: ... `Before Tool` and `After Tool` callbacks give you control points specifically around the execution of tools invoked by the agent." Control flow: "`return None` (Allow Default Behavior)" lets the step proceed; "`return <Specific Object>` (Override Default Behavior)" skips/replaces the step — e.g., a `before_tool_callback` can return a result that skips the actual tool execution. Checks against: **developer-written callback code** with access to `CallbackContext`/`ToolContext` (session state, invocation details) — no built-in KB/policy source is described; it's a generic interception hook, explicitly listed use case: "Implement Guardrails: Enforce safety rules, validate inputs/outputs, or prevent disallowed operations."
- **Does it check tool-call ARGUMENTS against a knowledge source?** Not built-in — the mechanism exposes tool arguments to custom code via context objects, but no native "verify against documents" feature is documented on this page.
- **Published numbers**: None quoted.
- **Human approval trigger**: Not described on this page — purely a programmatic interception point; any human-approval flow would be custom-built in the callback.

### 2. Model Armor
- **Status**: Shipping (Google Cloud service; current doc, no explicit GA/preview tag quoted).
- **URL**: https://docs.cloud.google.com/model-armor/overview (redirected from the security-command-center URL) (accessed 2026-10-04)
- **Mechanism (quoted)**: "It works by proactively screening LLM prompts and responses, protecting against various risks... Model Armor filters both input (prompts) and output (responses) to prevent the LLM from exposure to or generation of malicious or sensitive content." Flow: "1. You provide a prompt... 2. Model Armor inspects the incoming prompt... 3. The prompt (or sanitized prompt) is sent to the LLM. 4. The LLM generates a response. 5. Model Armor inspects the generated response... 6. The response (or sanitized response) is sent to you." Checks against: configurable **"templates"** = "sets of customized filters and thresholds" for "responsible AI safety categories (sexually explicit, dangerous, harassment, and hate speech), prompt injection and jailbreak detection, and sensitive data protection (including topicality)" — i.e., policy/category thresholds, not a document KB, and not specifically tool-call arguments (it screens prompts/responses, agent-framework-agnostic).
- **Does it check tool-call ARGUMENTS against a knowledge source?** Not described as such — it is a prompt/response content screen (PII, jailbreak, hate/harassment categories), not an argument-vs-KB verifier.
- **Published numbers (quoted)**: Confidence-level table: "High | Only flags content with near-certainty of a violation. | Very low [false positive risk]"; "Medium and above | Flags content with a balanced degree of confidence. | Moderate"; "Low and above | Identifies content with a low, medium, or high likelihood of violation." (relative descriptors, not numeric percentages).
- **Human approval trigger**: Not described — it sanitizes/blocks automatically per template; no human-in-the-loop step documented on this page.

### 3. Vertex AI — Check Grounding API
- **Status**: Shipping, part of "Agent Search"/RAG Engine.
- **URL**: https://docs.cloud.google.com/generative-ai-app-builder/docs/check-grounding (accessed 2026-10-04)
- **Mechanism (quoted)**: "The check grounding API returns an overall support score of 0 to 1, which indicates how much the answer candidate agrees with the given facts. The response also includes citations to the facts supporting each claim in the answer candidate... a sentence is considered a single claim." Checks against: **explicit developer-supplied "facts"** (reference documents/text segments, "up to 200 facts, each with a maximum of 10k characters") — this is a genuine text-vs-knowledge-source grounding check, though for generated answer text, not specifically tool-call arguments. Quoted: "By setting a citation threshold, chat bots can filter out responses at inference time that are likely to contain hallucinated claims."
- **Does it check tool-call ARGUMENTS against a knowledge source?** No — it checks **answer-candidate text** against supplied facts, not tool-call arguments/schemas. Could in principle be repurposed to check a tool argument string against a KB, but the API is documented for answer/claim grounding, not tool-call pre-execution.
- **Published numbers (quoted)**: "designed to be fast, with latency less than 500ms"; "An answer candidate can have a maximum length of 4096 tokens"; "The service supports up to 200 facts, each with a maximum of 10k characters."
- **Human approval trigger**: Not described — it returns a score/citations for the calling application to act on (e.g., auto-filter below a threshold); no built-in human approval step.

### 4. Google's "approach to secure AI agents"
- **Status**: UNVERIFIED this session — attempted URL `https://cloud.google.com/blog/topics/google-cloud-security/google-approach-secure-ai-agents` returned 404; attempted `https://cloud.google.com/blog/products/ai-machine-learning/google-cloud-secure-ai-agents` also returned 404. No official page was successfully opened for this item. **Gap** — flagged for follow-up search with exact title.

---

## Meta

### 1. LlamaFirewall
- **Status**: Shipping, open source (Purple Llama project). No explicit version-date stamp retrieved on the opened page.
- **URL**: https://github.com/meta-llama/PurpleLlama/blob/main/LlamaFirewall/README.md (accessed 2026-10-04); companion page https://meta-llama.github.io/PurpleLlama/LlamaFirewall/ (accessed 2026-10-04)
- **Mechanism (quoted)**: "LlamaFirewall is a framework designed to detect and mitigate AI centric security risks, supporting multiple layers of inputs and outputs, such as typical LLM chat and more advanced multi-step agentic operations. It consists of a set of scanners for different security risks." It "operates as a policy engine that orchestrates multiple security scanners... plugged into various stages of an LLM agent's workflow." Components (quoted): "**Layered Defense Architecture**: Combines multiple scanners—PromptGuardScanner, AlignmentCheckScanner, CodeShieldScanner, and customizable regex filters." Specifically: "A chain-of-thought auditing module that inspects the reasoning process of an LLM agent in real time... to detect goal hijacking, indirect prompt injections, and signs of agent misalignment" (AlignmentCheckScanner) — "**Use case**: Verifying that agent decisions remain consistent with user intent."
- **Does it check tool-call ARGUMENTS against a knowledge source?** Not as a KB-lookup — AlignmentCheckScanner audits agent reasoning/intent-consistency via semantic analysis and few-shot prompting, not a document/KB verification of tool arguments. PromptGuardScanner operates on "user inputs and untrusted content such as web data" for injection detection, not structured tool-call args specifically.
- **Published numbers**: None quoted on the opened README excerpt (a benchmark paper is referenced but not opened: "LlamaFirewall: An open source guardrail system for building secure AI agents").
- **Human approval trigger**: Not described on the opened page — it's an automated scanner/policy-engine layer; no built-in human-approval UI documented here.

### 2. Llama Guard 4
- **Status**: Shipping (model card, no explicit release-date line captured in the retrieved excerpt).
- **URL**: https://huggingface.co/meta-llama/Llama-Guard-4-12B (accessed 2026-10-04)
- **Mechanism (quoted)**: "Llama Guard 4 is a natively multimodal safety classifier with 12 billion parameters trained jointly on text and multiple images... it generates text in its output that indicates whether a given prompt or response is safe or unsafe, and if unsafe, it also lists the content categories violated." Checks against: a fixed **hazard taxonomy** (quoted list includes "S1: Violent Crimes" through "S14: Code Interpreter Abuse (text only)"), i.e., a prebaked policy taxonomy (per OpenAI's own contrast, cited above), not a tool-argument/KB check. Notable: "S14: Code Interpreter Abuse (text only)" is "an additional category... for text-only tool-call use cases" — the closest thing to tool-related coverage, but it's a hazard category for classifying abusive code-interpreter content, not a schema/argument verifier.
- **Does it check tool-call ARGUMENTS against a knowledge source?** No — it classifies prompt/response **text** (including now multi-image) against the MLCommons hazard taxonomy; S14 covers code-interpreter abuse patterns but this is content classification, not argument-vs-document grounding.
- **Published numbers**: None quoted in the retrieved excerpt (14 hazard categories listed, not a "number" in the metrics sense).
- **Human approval trigger**: Not applicable — outputs a safe/unsafe label for a downstream system to act on.

### 3. Prompt Guard 2
- **Status**: Shipping, released alongside Llama 4 (per search synthesis cross-referenced against the opened model card; the opened GitHub page itself did not show an explicit date in the retrieved excerpt).
- **URL**: https://github.com/meta-llama/PurpleLlama/blob/main/Llama-Prompt-Guard-2/86M/MODEL_CARD.md (accessed 2026-10-04)
- **Mechanism (quoted)**: "We are launching two classifier models as part of the Llama Prompt Guard 2 series... Llama Prompt Guard 2 86M and a new, smaller version, Llama Prompt Guard 2 22M." "Both Llama Prompt Guard 2 models detect both prompt injection and jailbreaking attacks, trained on a large corpus of known vulnerabilities." "**Simplified binary classification**: Both Prompt Guard 2 models focus on detecting explicit, known attack patterns, labeling prompts as 'benign' or 'malicious'." Checks against: a trained classifier's learned attack-pattern corpus, not a document KB. Intent-based: "This classification considers only the intent to supersede developer or user instructions, regardless of whether the prompt is potentially harmful."
- **Does it check tool-call ARGUMENTS against a knowledge source?** No — it classifies arbitrary input text (prompts, retrieved/untrusted content) for injection/jailbreak intent; not documented as a tool-argument-vs-KB check. Per the LlamaFirewall README, PromptGuardScanner (built on this model family) "operates on user inputs and untrusted content such as web data."
- **Published numbers (quoted)**: "Llama Prompt Guard 2 22M reduces latency and compute costs by 75%, with minimal performance trade-offs." "Both Llama Prompt Guard 2 models support a 512-token context window."
- **Human approval trigger**: Not described — binary classifier output ('benign'/'malicious') for the calling system to act on (block, flag, or escalate).

---

## Microsoft

### 1. Azure AI Content Safety — Prompt Shields
- **Status**: Shipping, in Microsoft Foundry. Page `ms.date: 2026-08-28`.
- **URL**: https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection (accessed 2026-10-04)
- **Mechanism (quoted)**: "Prompt Shields detects and blocks adversarial inputs to large language models (LLMs). It analyzes user prompts and documents before content is generated to help prevent harmful, unsafe, or policy-violating output." Two attack types: "**User prompt attacks**... In Microsoft Foundry, the system scans for these attacks at the **user input** intervention point." "**Document attacks** are hidden instructions in third-party content, such as documents, emails, and web pages... the system scans for these attacks at the **user input** and **tool response** intervention points." This explicitly covers **tool-response** scanning, i.e., it intercepts content coming back from tool calls, not just the initial prompt. Output annotation format (quoted JSON): `"content_filter_results": {"jailbreak": {"filtered": false, "detected": true}}`.
- **Does it check tool-call ARGUMENTS against a knowledge source?** No — it scans user input and tool *responses* (incoming content) for injected instructions/attack patterns via a classifier, not outgoing tool-call arguments against a KB.
- **Published numbers**: None quoted on this page (Spotlighting's numbers are on a different page, below).
- **Human approval trigger**: Not itself a human-approval gate — it "blocks the prompt and asks the user to change it" (per a quoted customer-service scenario) or "redirects the request to a human agent" in the chatbot scenario — i.e., escalation to a human is an application-level response to a `detected`/`filtered` flag.

### 2. Groundedness detection
- **Status**: Shipping, in Azure AI Content Safety. Page `ms.date: 2025-11-21`.
- **URL**: https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness (accessed 2026-10-04)
- **Mechanism (quoted)**: "Groundedness detection in Azure AI Content Safety helps you ensure that large language model (LLM) responses are based on your provided source material, reducing the risk of non-factual or fabricated outputs." Requires "document embedding and formatting." Checks against: **developer-supplied RAG source documents**, explicitly defined via the RAG pattern (quoted definition of RAG included on page) — this is a text-output-vs-document check, analogous to Google's Check Grounding API and AWS's contextual grounding, not a tool-argument check.
- **Does it check tool-call ARGUMENTS against a knowledge source?** No — it checks LLM **response text** against embedded source documents, not tool-call arguments.
- **Published numbers**: Not reached in the retrieved excerpt (truncated before any stats section).
- **Human approval trigger**: Not reached in the retrieved excerpt — UNVERIFIED beyond the detection mechanism itself.

### 3. Task Adherence (agents)
- **Status**: Shipping, Azure AI Content Safety / Foundry Tools. Page `ms.date: 2025-08-13`.
- **URL**: https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/task-adherence (accessed 2026-10-04)
- **Mechanism (quoted)**: "The Task Adherence feature identifies discrepancies such as misaligned tool invocations, improper tool input or output relative to user intent, and inconsistencies between responses and customer input. This feature lets system developers proactively mitigate misaligned actions by blocking them or escalating the issue for human intervention." Objectives (quoted): "To detect tool actions that are misaligned with user goals or input intent, or improper tool input/output relative to user intent... To provide reasoning when tool calls are misaligned... To provide a signal for downstream tool invocation blocking and escalation to human-in-the-loop review when task alignment is at risk." Worked example (quoted): user asks "Can you check how much data I've used this month?"; "The assistant plans to invoke a `change_data_plan()` tool. Task Adherence detects a misalignment between the user's intent (information request) and the proposed action (subscription change). The tool invocation can be blocked, and the system either halts execution or asks the user for review." This is THE most directly on-point feature found this session for "pre-execution guardrail checking a proposed tool call against verifiable intent."
- **Does it check tool-call ARGUMENTS against a knowledge source?** It checks **tool invocation choice + tool input/output** against **user intent / conversation context** (goal/rule/procedural adherence, per search-derived summary of a related evaluator page, not independently verified verbatim) — this is an intent-consistency check, not a check against an external document/KB. The opened page itself frames it as "tool input or output relative to user intent," i.e., user-intent grounding, not KB grounding.
- **Published numbers**: None quoted in the retrieved excerpt.
- **Human approval trigger (quoted)**: "escalating the issue for human intervention"; in the examples, misaligned tool calls are blocked and "the system either halts execution or asks the user for review" / "prompts user review."

### 4. Spotlighting
- **Status**: Shipping as part of Microsoft's defense-in-depth guidance; originates from Microsoft Research.
- **URL**: https://learn.microsoft.com/en-us/security/zero-trust/sfi/defend-indirect-prompt-injection (accessed 2026-10-04)
- **Mechanism (quoted)**: "**Spotlighting**: Use data marking and metaprompting to isolate and neutralize external content within prompts." Listed alongside other layers: "Prompt shields," "Plan drift detection," "Critic agents," "Tool chain analysis," "Security guardrails," "Information flow control (IFC)," "Principle of least privilege," "Human-in-the-loop: The last line of defense against an attack is to verify risky actions with the user." Checks against: distinguishing untrusted/external content from trusted instructions via markup — a content-provenance technique, not a KB-verification step. (A quantitative claim about attack-success-rate reduction appeared only in web-search-synthesized text citing the Microsoft Research paper, not in the Microsoft Learn page I opened directly — so that specific number is **UNVERIFIED** this session and is excluded from quotes.)
- **Does it check tool-call ARGUMENTS against a knowledge source?** No — it's an input-marking technique to help the model distinguish data from instructions, not an argument/KB check.
- **Published numbers**: None independently verified via an opened page this session (see caveat above).
- **Human approval trigger (quoted)**: "Human-in-the-loop: The last line of defense against an attack is to verify risky actions with the user."

### 5. Agent Framework / Semantic Kernel filters
- **Status**: Shipping (Semantic Kernel docs, `ms.date: 2026-04-29`). "Microsoft Agent Framework" specifically (the newer unification of Semantic Kernel + AutoGen) was **not** independently opened this session — **gap/UNVERIFIED** for that exact product name; findings below are Semantic-Kernel-specific.
- **URL**: https://learn.microsoft.com/en-us/semantic-kernel/concepts/enterprise-readiness/filters (accessed 2026-10-04)
- **Mechanism (quoted)**: "Filters enhance security by providing control and visibility over how and when functions run." Three filter types: "**Function Invocation Filter** - this filter is executed each time a `KernelFunction` is invoked. It allows: Access to information about the function being executed and its arguments[,] Handling of exceptions during function execution[,] Overriding of the function result, either before... or after execution (for instance for responsible AI scenarios)[,] Retrying of the function in case of failure." "**Prompt Render Filter** - this filter is triggered before the prompt rendering operation, enabling: Viewing and modifying the prompt that will be sent to the AI (e.g., for RAG or PII redaction)[,] Preventing prompt submission to the AI by overriding the function result." "**Auto Function Invocation Filter** - ... providing additional context, including chat history, a list of all functions to be executed, and iteration counters. It also allows termination of the auto function calling process."
- **Does it check tool-call ARGUMENTS against a knowledge source?** The Function Invocation Filter explicitly has "Access to information about the function being executed **and its arguments**" — this is argument-level interception, but the check logic is developer-written (custom code), not a built-in KB-verification feature.
- **Published numbers**: None quoted.
- **Human approval trigger**: Not described on this page — filters are a programmatic interception point; example given is permission-checking logic ("filters are leveraged to validate permissions before an approval flow begins"), implying developers build their own approval gates on top.

### 6. Foundry guardrails (overview)
- **Status**: Referenced by the Prompt Shields page ("In Foundry, Prompt Shields is part of the guardrails and controls system") but the dedicated overview URL guessed this session (`/azure/ai-foundry/concepts/guardrails-overview`) returned 404 — **not independently opened**. **Gap** for a standalone Foundry-guardrails-overview citation.

---

## AWS

### 1. Bedrock Guardrails — overview
- **Status**: Shipping/GA (customer-named references imply production use).
- **URL**: https://aws.amazon.com/bedrock/guardrails/ (accessed 2026-10-04)
- **Mechanism (quoted)**: "Amazon Bedrock Guardrails integrates seamlessly across your AI application stack, from individual model inference to complex multi-step workflows. Apply guardrails to foundation model interactions, associate them with agents using frameworks like Strands Agents for conversational AI, integrate with knowledge bases for retrieval-augmented generation, and embed within flows for sophisticated multi-node processes." Customers quoted: "Companies like Chime Financial, KONE, Panorama, Strava, Remitly, and PwC trust Bedrock Guardrails for their AI applications."
- **Published numbers**: None beyond the customer name-list quoted above.

### 2. Automated Reasoning checks
- **Status**: Shipping (AWS user guide; referenced "2026/06" what's-new post for a policy-refinement feature addition per search, not independently opened).
- **URL**: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html (accessed 2026-10-04)
- **Mechanism (quoted)**: "Automated Reasoning checks in Amazon Bedrock Guardrails help solve this problem by using mathematical techniques to validate natural language content against policies you define... uses formal logic to provide structured feedback about *why* a response is correct or incorrect." Capabilities (quoted): "Detect factually incorrect statements in LLM responses by mathematically proving that generated content contradicts your policy rules;" "Highlight unstated assumptions where a response is consistent with your policy but doesn't address all relevant rules;" "Provide mathematically verifiable explanations for why accurate statements are correct, citing the specific policy rules and variable assignments that support the conclusion." Contrast (quoted): "Content filters and topic policies act as binary gates — they block or allow content. Automated Reasoning checks act as a verification layer." Workflow (quoted ASCII diagram): "Source Document ──► Extracted Policy ──► Testing ──► Deployment ──► Integration." Checks against: a **formal-logic policy extracted from a source document** you upload — this IS a genuine "verify generated content/claims against a verifiable source" mechanism, the closest built-in analogue found this session to the hackathon's own guardrail concept, though AWS documents it for validating response *content*, not explicitly framed as pre-execution tool-argument validation.
- **Does it check tool-call ARGUMENTS against a knowledge source?** Not explicitly framed as such — it validates "natural language content" (LLM responses) against an extracted formal-logic policy. Explicitly quoted limitation: "**No prompt injection protection.** Automated Reasoning checks validate exactly what you send them." Nothing on this page claims it inspects structured tool-call argument payloads specifically, though nothing precludes sending argument text as the content to validate — UNVERIFIED for that specific use.
- **Published numbers**: No percentage/accuracy benchmark numbers quoted (the page describes a qualitative "fidelity report" with "coverage and accuracy scores" but no specific figures were in the retrieved excerpt).
- **Human approval trigger**: Not described — it returns `VALID`/invalid-type findings with explanations for the application to act on programmatically; no built-in human-approval UI documented.

### 3. Contextual grounding check
- **Status**: Shipping, part of Bedrock Guardrails.
- **URL**: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html (accessed 2026-10-04)
- **Mechanism (quoted)**: "Amazon Bedrock Guardrails supports contextual grounding checks to detect and filter hallucinations in model responses when a reference source and a user query is provided." Two paradigms (quoted): "**Grounding** – This checks if the model response is factually accurate based on the source and is grounded in the source... **Relevance** – This checks if the model response is relevant to the user query." Checks against: an explicit **grounding source** (reference text, "maximum of 100,000 characters") + "query" + "content to guard" (the model response, "maximum... 5,000 characters") — this is a genuine response-vs-source-document verification.
- **Does it check tool-call ARGUMENTS against a knowledge source?** No — documented for **model responses** (summarization/paraphrasing/QA), explicitly: "Conversational QA / Chatbot use cases are not supported," and no mention of tool-call arguments.
- **Published numbers (quoted)**: "You can configure threshold values of grounding and relevance between 0 and 0.99. A threshold of 1 is invalid as that will block all content." Size limits: "100,000 characters for grounding source, 1,000 characters for query, and 5,000 characters for response."
- **Human approval trigger**: Not described — automatic filtering/blocking based on configured thresholds; no human-approval step documented.

### 4. Bedrock AgentCore Gateway / Policy (Cedar) — existence/status verified
- **Status**: CONFIRMED to exist and be documented (dedicated AWS devguide pages exist and were opened) — exact GA/preview label was not present in the retrieved excerpt, so that label specifically is UNVERIFIED, but the feature's existence and mechanism are directly confirmed (not a rumor).
- **URL**: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy-understanding-cedar.html (accessed 2026-10-04)
- **Mechanism (quoted)**: "Policy in AgentCore uses Cedar policies to control access to AgentCore Gateway tools." Structure: "Cedar policies consist of three main components: 1. Effect - Determines whether to allow or deny access (`permit` or `forbid`) 2. Scope - Specifies the principal, action, and resource the policy applies to 3. Condition - Defines additional logic... and can refer to the tool parameters (through the context) and the OAuth token (through the tags)." Example policy quoted restricts a `RefundTool___process_refund` action to principal "John" with `context.input.amount < 500` — this is a direct **tool-call-argument check** (the refund `amount` argument) against a declarative policy. Evaluation (quoted): "All actions are denied by default. If no policies match a request, Cedar returns DENY... Cedar uses a forbid-overrides-permit evaluation model."
- **Does it check tool-call ARGUMENTS against a knowledge source?** **YES, precisely** — the `when { ... context.input.amount < 500 }` clause directly inspects a tool-call argument (`amount`) against a declarative Cedar policy rule before the Gateway permits the tool call to execute. This is the single clearest "pre-execution tool-argument-vs-policy" mechanism found across all companies this session, though the "source" here is a hand-authored Cedar policy, not a document/KB.
- **Published numbers**: None quoted (no performance/accuracy stats on this page).
- **Human approval trigger**: Not described on this page — Cedar evaluation is a deterministic allow/deny gate at the Gateway, not a human-in-the-loop prompt; the policy itself is how "approval" is encoded (via `permit`/`forbid`), not a runtime human ask.

---

## NVIDIA

### 1. NeMo Guardrails — execution/tool rails
- **Status**: Shipping, open source library + production microservice.
- **URL**: https://docs.nvidia.com/nemo/guardrails/latest/index.html (served as markdown) (accessed 2026-10-04)
- **Mechanism (quoted)**: "The NVIDIA NeMo Guardrails library... is an open-source Python package for adding programmable guardrails to LLM-based applications. Use it to block, alter, or validate unsafe, off-topic, malicious, or policy-violating user inputs and model responses." Core building block (quoted): "**Rails**: Input, retrieval, dialog, execution, and output rails run at different stages of an LLM interaction." Benefit (quoted): "Inspect and control user inputs, retrieved content, **tool calls**, and model outputs in one guardrails workflow." Configuration via "YAML files define models, prompts, rails, tracing, and other runtime settings" plus "Colang flows" for conversational/guardrail logic, and "Custom actions: Python functions, tools, or external APIs extend guardrails with application-specific checks." Checks against: a combination of "LLM self-checking," "NVIDIA safety models" (e.g., content-safety NIMs), "community models" (LlamaGuard, Fiddler), and "third-party APIs" (ActiveFence, Cisco AI Defense) — i.e., pluggable classifier/model checks per rail, not inherently a fixed KB, though retrieval rails can incorporate retrieved content checks.
- **Does it check tool-call ARGUMENTS against a knowledge source?** The "execution" rail category exists specifically to wrap tool/action calls ("Add guardrails before and after LLM calls... Inspect and control... tool calls"), but the opened page describes this at the architecture level (a rail stage + custom Python actions) rather than demonstrating a built-in tool-argument-vs-KB check; the actual verification logic is supplied via custom actions or an attached safety-model/NIM.
- **Published numbers**: None quoted (library/microservice comparison table is structural, not numeric performance data).
- **Human approval trigger**: Not described on this page — guardrails block/alter/validate programmatically; no built-in human-approval UI documented here.

### 2. NemoGuard NIMs
- **Status**: Shipping (NVIDIA-hosted inference endpoint / downloadable NIM container).
- **URL**: https://build.nvidia.com/nvidia/llama-3_1-nemoguard-8b-content-safety (accessed 2026-10-04)
- **Mechanism (quoted)**: "This open Nemotron safety model, *Llama 3.1 NemoGuard Content Safety*, is a content safety model that moderates human-LLM interaction content and classifies user prompts and LLM responses as safe or unsafe. If the content is unsafe, the model additionally returns a response with a list of categories that the content violates." Base model: "Llama-3.1-8B-Instruct... LoRa-tuned... better conforms NVIDIA's content safety risk taxonomy." Explicitly: "This model is supported in the open NVIDIA NeMo Guardrails library, designed to simplify scalable AI guardrail orchestration for safeguarding agentic AI applications." Checks against: "a system prompt, including the Aegis2.0 safety taxonomy, which is a safety policy that contains a list of unsafe categories" — a fixed/extensible taxonomy, plus "novel safety risk categories and policies can be provided in the instruction," so developer-extensible policy text. The NeMo Guardrails overview page also names a companion "**NemoGuard Jailbreak Detection NIM**" for jailbreak-specific checks.
- **Does it check tool-call ARGUMENTS against a knowledge source?** No — it's a prompt/response content-safety classifier (taxonomy-based), not a tool-argument/KB verifier.
- **Published numbers**: None quoted (architecture details given: "Rank: 16, Alpha: 32" LoRA params — not performance numbers).
- **Human approval trigger**: Not described — classifier output (safe/unsafe + violated categories) for the calling guardrails pipeline to act on.

---

## IBM

### 1. Granite Guardian
- **Status**: Shipping, current version "Granite Guardian 4.1 8B."
- **URL**: https://www.ibm.com/granite/docs/models/guardian (accessed 2026-10-04)
- **Mechanism (quoted)**: "Risk detection models and LoRA adapters for evaluating AI safety, RAG groundedness, and agentic function calling — with support for custom bring-your-own criteria (BYOC)." Specifically for agents (quoted): "**Function calling risk detection within agentic workflows, where Granite Guardian evaluates intermediate steps for syntactic and semantic hallucinations. This includes assessing the validity of function calls and detecting fabricated information, particularly during query translation.**" Also: "**Bring Your Own Criteria (BYOC)**: Users can define arbitrary evaluation rules to judge whether LLM outputs satisfy diverse requirements such as formatting rules, length constraints, or domain-specific instructions." Modes: "thinking mode (with detailed reasoning traces) and non-thinking mode (low-latency yes/no judgements)." For RAG specifically: "context relevance (whether the retrieved context is relevant to the query), groundedness (whether the response is accurate and faithful to the provided context), and answer relevance."
- **Does it check tool-call ARGUMENTS against a knowledge source?** Closest-to-yes among the classifier-style products: it "evaluates intermediate steps for syntactic and semantic hallucinations" in function calling and "assess[es] the validity of function calls" — this directly targets tool/function-call correctness, though the "source" is the model's own learned judgment (+ optional BYOC custom criteria text), not a fixed external document store by default — BYOC lets a developer supply policy/criteria text to check against.
- **Published numbers (quoted)**: "Since its inception, Granite Guardian has remained in the top 3 on the LLM-Aggrefact Leaderboard (as of 10/2/2025)."
- **Human approval trigger**: Not described on this page — outputs a `<score>` (and optional `<think>` reasoning trace) for a downstream pipeline to act on; no built-in human-approval UI documented here.

### 2. watsonx.governance
- **Status**: Shipping (IBM product page; no version/date stamp captured).
- **URL**: https://www.ibm.com/products/watsonx-governance (accessed 2026-10-04)
- **Mechanism (quoted — page returned only a brief tagline on this fetch)**: "IBM watsonx.governance helps enterprises govern any AI, anywhere with real-time visibility, enterprise controls, and continuous accountability, powered by AI-native governance and enterprise-grade GRC."
- **Does it check tool-call ARGUMENTS against a knowledge source?** UNVERIFIED — the retrieved excerpt is a marketing tagline only; no mechanism detail (interception point, policy source) was present in what was fetched. **Gap**: needs a deeper product/docs page (e.g., a watsonx.governance technical documentation page) to confirm any agent/tool-call-specific checks.
- **Published numbers**: None quoted.
- **Human approval trigger**: Not described in the retrieved excerpt.

---
