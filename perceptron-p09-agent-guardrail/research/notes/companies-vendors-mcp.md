# What companies ship today — Agent/Tool-Call Guardrails (cited, official sources only)

Research date: 2026-10-04. Only pages actually opened this session are cited. All quotes are verbatim. Unconfirmed items marked UNVERIFIED.

---

## 1. MCP specification — Tool Annotations (readOnlyHint / destructiveHint / idempotentHint / openWorldHint)

- **Product/spec**: Model Context Protocol (MCP) specification
- **Status/version**: Protocol revision **2025-06-18** (live default on site at time of access). Repo also shows later dated revisions `2025-11-25` and `2026-07-28` exist in the spec repo's `schema/` folder, listed but not fetched this session — UNVERIFIED whether `2026-07-28` is the site's current default as of 2026-10-04.
- **URLs**:
  - https://modelcontextprotocol.io/specification/2025-06-18/server/tools (accessed 2026-10-04)
  - https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/2025-06-18/schema.ts (accessed 2026-10-04)
- **Where it intercepts**: Client-side, at tool discovery (`tools/list`) — annotations are metadata attached to a tool definition, read by the MCP *client* before/around invocation; the spec does not define a separate runtime guardrail process.
- **What it checks against**: Nothing externally verifiable — annotations are server-self-declared metadata, not checked against any independent source.
- **Does it verify tool-call ARGUMENTS against a knowledge source?** **No.** Annotations describe tool *behavior* (readOnlyHint/destructiveHint/idempotentHint/openWorldHint), not argument values, and the spec explicitly tells clients not to trust them for decisions.
- **Exact quotes**:
  - From the live tools page: "For trust & safety and security, clients **MUST** consider tool annotations to be untrusted unless they come from trusted servers." (`modelcontextprotocol.io/specification/2025-06-18/server/tools`, Data Types → Tool section)
  - From `schema/2025-06-18/schema.ts` lines ~869–877 (interface `ToolAnnotations` doc comment): "Additional properties describing a Tool to clients. NOTE: all properties in ToolAnnotations are **hints**. They are not guaranteed to provide a faithful description of tool behavior (including descriptive properties like `title`). Clients should never make tool use decisions based on ToolAnnotations received from untrusted servers."
  - Field doc-comments (same file, lines ~892–922): `readOnlyHint`: "If true, the tool does not modify its environment. Default: false"; `destructiveHint`: "If true, the tool may perform destructive updates to its environment. If false, the tool performs only additive updates. (This property is meaningful only when `readOnlyHint == false`) Default: true"; `idempotentHint`: "If true, calling the tool repeatedly with the same arguments will have no additional effect on the its environment. (This property is meaningful only when `readOnlyHint == false`) Default: false"; `openWorldHint`: "If true, this tool may interact with an \"open world\" of external entities. If false, the tool's domain of interaction is closed. ... Default: true"
  - Also from the live tools page, "Security Considerations": Clients **SHOULD** "Show tool inputs to the user before calling the server, to avoid malicious or accidental data exfiltration" and "Validate tool results before passing to LLM" — no mention of validating tool-call *arguments* against an external ground truth.
- **Published numbers**: None found.

---

## 2. Invariant Labs — "Invariant Guardrails"

- **Product/status**: Open-source "comprehensive rule-based guardrailing layer for LLM or MCP-powered AI applications," deployed as an MCP/LLM proxy ("Gateway"). No explicit version/date string found on the README itself.
- **URL**: https://github.com/invariantlabs-ai/invariant (README.md, accessed 2026-10-04, file SHA `2add5438d92f8851badcadeecc85cbe1c677702b`)
- **Where it intercepts**: "deployed between your application and your MCP servers or LLM provider" — i.e., a proxy/gateway sitting in the request path, checking "automatically based on your rules," both LLM and MCP requests "(before and after)" via the companion `invariant-gateway`.
- **What it checks against**: User-authored declarative policy rules (a Python-inspired DSL) matching over message/tool-call traces, plus a built-in `prompt_injection()` detector run over tool output content.
- **Does it verify tool-call ARGUMENTS against a knowledge source?** **Partially, via author-defined patterns, not an external knowledge base.** Rules can match specific argument fields directly, e.g. quoted verbatim: `call2 is tool:send_email({ to: ".*@[^ourcompany.com$].*" })` — a regex check on the `to` argument of a `send_email` tool call, chained after a `get_inbox` call via `(call: ToolCall) -> (call2: ToolCall)`. This is rule-author-specified static matching (regex/value patterns), not verification against a live/external "source of truth."
- **Policy-rule example (quoted verbatim from README)**:
  ```
  raise "External email to unknown address" if:
      # detect flows between tools
      (call: ToolCall) -> (call2: ToolCall)

      # check if the first call obtains the user's inbox
      call is tool:get_inbox

      # second call sends an email to an unknown address
      call2 is tool:send_email({
        to: ".*@[^ourcompany.com$].*"
      })
  ```
  Second example chaining a prompt-injection detector on tool *output* to a subsequent tool *call*: `raise "Don't use send_email after get_website" if: (output: ToolOutput) -> (call2: ToolCall) \n output is tool:get_website \n prompt_injection(output.content, threshold=0.7) \n call2 is tool:send_email`
- **Published numbers**: None found (no accuracy/latency/benchmark figures on this page).

---

