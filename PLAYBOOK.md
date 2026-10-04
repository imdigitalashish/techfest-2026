# PLAYBOOK — how every project in this repo is run

This repo holds 20 parallel projects for Techfest 2026 (IIT Bombay), one folder per problem statement. Every project follows the same method so the Supervisor and the user can read any project at a glance, and so components can be researched, swapped and auto-improved independently and in parallel.

## 0. Operating mode (since 4 Oct 2026, 10:00 IST)

- **Batch mode (user directive):** at most 5 projects are active at a time; the rest are paused and idle. When an active project meets its definition of done, it messages the Supervisor "DONE — slot free". The Supervisor marks it ✅ Completed in README.md for the user to review, then resumes the next queued project.
- **Do not ask the user anything** (never call `ask_user`). Make the best decision, record the assumption in your thought node, and keep going.
- Real blockers (registrations, a physical phone capture, credentials, purchases) go under *Needs from user*. Work around them meanwhile with public datasets, simulations or mocks, clearly labelled.
- The overnight morning package (§9) was delivered on 4 Oct 2026.
- **Zero hallucination.** Every factual claim cites a source you actually opened. Every number comes from a run that is committed, with the command that reproduces it. Anything unverified is marked **UNVERIFIED**. Synthetic data and estimates are labelled as such.
- Keep GitHub current: commit and push at every step (§6).

## 1. Roles

| Role | Who | Owns |
|---|---|---|
| **User** | Ashish (IIT Delhi student, works with Microsoft) | Registrations, team, physical-world tasks, accounts and money, final calls |
| **Supervisor** | The portfolio chat that spawned the project leads | Root files (`README.md`, `PLAYBOOK.md`, `thought_node.md`, `MORNING_REPORT.md`, `_briefs/`), cross-project alignment, selection gates |
| **Project lead** | One session per problem statement | Its folder `<slug>/`, its `thought_node.md`, architecture, decisions, integration, deliverables |
| **Workers** | Sub-agents (`task`) and child sessions (orchestrate skill) spawned by a lead | One research thread or one component folder; report to their lead |

Leads have the deepest context on their project. The Supervisor aligns by asking — "I'm seeing X and thinking Y; do you agree, or is there a better way?" — not by dictating. Answer candidly with evidence, and push back when you know better.

## 2. The method: component-based innovation

Every system is a set of components with explicit input/output contracts. Most components use the best existing practice. One or two **spike components** carry the innovation. Because contracts are fixed, any component can be researched, swapped or auto-improved on its own, in parallel with the others.

### Phase 0 — Brief
- Read the official statement in `_briefs/` and the seeded Brief in your thought node.
- Extract hard constraints: deliverables per round, dates, judging weights, rules (frozen models, banned tools, team limits).
- Turn the judging criteria into "what we must be able to show". This drives every later choice.

### Phase 1 — State-of-the-art research (primary sources, newest first)
Don't settle for generic summaries. Learn the frontier from the people and companies pushing it:
- **Papers:** arXiv (last 12–18 months first), OpenReview (ICLR/NeurIPS/ICML 2025–2026), ACL Anthology, CVF open access, Hugging Face Papers, citation trails (what cites the classic baseline, and what beat it?).
- **Code and models:** GitHub (stars, last commit, open issues — is it maintained?), Hugging Face models, datasets and Spaces, official reference implementations.
- **Companies and labs:** engineering and research blogs, release notes, docs and launch posts. Cover frontier labs (OpenAI, Anthropic, Google DeepMind, Meta, Microsoft Research, NVIDIA, Apple ML) and the domain leaders for your problem: trading firms' tech talks, 3D-capture startups, ed-tech, agent-security companies, and Indian public-digital-infrastructure bodies.
- **Social signal:** X/Twitter threads from paper authors, labs and founders (search `site:x.com` and open posts in the browser where possible), Hacker News, Reddit (r/MachineLearning, r/LocalLLaMA), conference talks. Treat these as leads and confirm against the primary source.
- **Competitions:** Kaggle winning write-ups and prior hackathon winners for adjacent problems.
- **Rules:** open and read a source before citing it; record the URL and access date; note maturity (paper-only / maintained code / in production); never cite from memory alone; if a search returns nothing, say so — don't fill gaps.
- Fan out parallel research sub-agents (papers · code and models · companies and products · social signal · datasets and benchmarks). Then have an independent agent re-verify the top claims (link opens, claim matches the source).
- Output: `research/landscape.md`, including a **"What companies ship today"** section: who does this in production, how (where public), and where our design borrows from or beats them.

### Phase 2 — Component map and contracts
- Decompose the end-to-end system into as many components as the problem needs (often 6–15).
- For each component define: responsibility (one sentence) · input contract · output contract (typed: JSON Schema, pydantic or TypeScript) · error modes · SLOs (latency, memory, accuracy) · which components it calls and how · the existing baseline that implements it · an **isolated scalar metric** that evaluates it alone.
- Every component knows exactly which component it calls, in what shape, and what comes back. Draw the dependency graph (mermaid).
- Use the `codebase-design` skill (deep modules, seams) and `domain-modeling` (glossary + ADRs).
- Output: `architecture/components.md`, `architecture/contracts/`.

### Phase 3 — Innovation scan per component
- Give each component its own research agent: state of the art for that component and room for innovation (speed, accuracy, adaptivity, robustness, cost, auditability, UX).
- Stress-test every serious candidate with:
  - **Six Thinking Hats** — White (facts and data), Red (gut feel; what will impress the judges), Black (risks, failure modes), Yellow (benefits), Green (alternatives, wild ideas), Blue (decision process).
  - **Thesis → antithesis → synthesis** — argue for it; have an *independent* adversarial agent (e.g. `rubber-duck`) argue against it; synthesise.
  - **First principles** (`First Prinicipals Agent`) — what is the real bottleneck?
- Score candidates 1–5 on: impact on the judged criteria · novelty vs state of the art · feasibility before the deadline · measurability (a scalar metric exists) · demoability. Pick 1–2 spike components; the rest stay best-practice.
- Output: `research/components/<component>.md`, and `architecture/adr/001-spike.md`.

### Phase 4 — Walking skeleton + eval harness
- Build end-to-end with baseline implementations behind the contracts, with contract tests for every component.
- The eval harness is first-class: end-to-end metric plus per-component metrics, fixed seeds, held-out data. Record real baseline numbers.

### Phase 5 — Auto-research loops (the ratchet)
Adapted from [karpathy/autoresearch](https://github.com/karpathy/autoresearch): an agent edits code, runs a short fixed experiment, keeps the change only if a scalar metric improves, reverts otherwise, and repeats. Per spike component:
```
<slug>/components/<component>/autoresearch/
  program.md    # goal, metric, constraints, idea backlog (written by the lead)
  eval.py       # FROZEN evaluator: prints one scalar (+ secondary metrics); the loop never edits it
  results.tsv   # ledger: timestamp · commit · hypothesis · metric · delta · kept? · notes
```
- Only the component's implementation changes; contract tests must pass.
- Keep only improvements beyond noise (several seeds or a held-out split). The lead periodically re-checks on a fresh holdout to catch metric gaming.
- Other optimisers are welcome where they fit: Optuna sweeps, evolutionary code search (OpenEvolve / AlphaEvolve-style), DSPy optimisers for LLM pipelines.

### Phase 6 — Deliverables and demo
Map every judging criterion to concrete evidence. Generate round deliverables (abstract, proposal, roadmap, deck, video script, demo) from the journal and real results. Rehearse Q&A against a hostile `rubber-duck` judge.

Phases overlap. Don't wait for permission between phases; the Supervisor aligns as you go.

## 3. Folder layout (inside `<slug>/`)
```
thought_node.md            # the journal (§5) — lead-owned
research/landscape.md
research/components/<component>.md
architecture/components.md
architecture/contracts/
architecture/adr/NNN-title.md
components/<component>/    # code + tests + autoresearch/ — one folder per component
eval/                      # end-to-end harness and baselines
deliverables/              # round submissions, decks, scripts
.data/  .cache/            # gitignored: datasets, weights, media
```

## 4. Delegation — child sessions, capped
- **Delegate through child sessions with the orchestrate skill (`create_session`), not `task` sub-agents** (user directive, 4 Oct). Sessions are visible and steerable in the user's sidebar.
- **At most 2 child sessions running at a time per active lead**, reviewers included. Many concurrent agents saturated this Mac's uplink overnight and model calls failed with HTTP 408.
- A useful roster: SOTA researchers · company/product scouts · component builders · auto-research loopers · fact-checkers · cross-model reviewers (§10).
- Every spawn gets complete context: this playbook's path, its component contract, metric, folder, definition of done, and how to report back.
- A child session owns `<slug>/components/<component>/` (and `<slug>/research/components/<component>.md`). Only the lead edits `thought_node.md` and `architecture/`.
- Relevant skills: `research`, `codebase-design`, `domain-modeling`, `first-principles-study`, `grilling`, `prototype`, `tdd`, `diagnosing-bugs`, `orchestrate`.

## 5. `thought_node.md` — the journal
The single source of truth for a project, read and written by the user and the Supervisor. Top = current state, rewritten in place. Bottom = append-only log.
- **Inbox** — the user and the Supervisor write here. Check it at the start of every step; act; reply in the Log; move handled items to *Handled*.
- **Now** — Phase · Plan · Doing (and who: which agents and sessions) · Next · Needs from user · Risks. Short enough to read in 30 seconds.
- **Key decisions** (link ADRs) · **Components** table · **Selection memo** · **Log** (timestamped IST entries: what happened, what we learned, links).
- Update it at every meaningful step and always before ending a turn.

## 6. Git — one repo, trunk-based
- Each session works in its own worktree; `main` is the shared trunk.
- Commit small and often (every step, and always before ending a turn), then integrate:
  `git fetch origin && git rebase origin/main && git push origin HEAD:main` — on rejection, repeat. Never force-push; never rewrite pushed history.
- Touch only your own folder. Root files and `_briefs/` belong to the Supervisor.
- **Never use `git stash` or `--autostash`.** All worktrees share one stash list, so a `stash pop` can apply another session's changes (this happened on 4 Oct). Commit before you rebase; a small `<slug>: wip` commit is fine.
- **Timestamps come from the clock, never from memory:** `TZ=Asia/Kolkata date '+%Y-%m-%d %H:%M IST'`. A pre-registration's stated time must match its git commit time, because the commit is the evidence. To fix a wrong time, append a dated correction; never edit registered text.
- Fetch and rebase at the start of each step too, so you see Inbox edits the user made on GitHub. On a conflict in `thought_node.md`, keep the user's text verbatim plus your update.
- Auto-research experiments live on a local branch; push only kept improvements and the `results.tsv` ledger.
- Never commit secrets, or files over 20 MB (datasets, weights, videos). Put them in gitignored `.data/` or `.cache/` and commit a script that fetches or regenerates them.
- Commit messages: `<slug>: <what changed>`. The message ends with its body — no `Co-authored-by` trailer (user preference).

## 7. Communication
- Lead → Supervisor (`send_session_message`): only for needs from the user, cross-project reuse or dependencies, a pivot or scope change, a blocker, or a ready gate deliverable (e.g. the selection memo). Everything else goes in the thought node.
- Supervisor → lead: alignment questions, gate decisions, user decisions. Answer candidly.
- Never ask the user directly. Put it under *Needs from user* and message the Supervisor if it blocks you.

## 8. Ground rules
- **Compute:** Apple M5 Mac locally (MLX, PyTorch MPS, Metal). For CUDA-only or heavy jobs, Azure is available (budget is not a constraint): check `az account show`; if it isn't usable, put the exact ask (SKU, region, hours, purpose) under *Needs from user* and continue on the Mac meanwhile.
- Respect every competition rule (originality, attribution, banned tools, frozen models, team limits).
- Cite sources; never fabricate results; label estimates and synthetic data.
- The user has IIT Delhi end-semester exams **19–25 Nov 2026** (last teaching day 17 Nov; vivas 27–28 Nov). Don't plan user-dependent work in that window.
- Stay inside this repo; don't touch the user's other repositories.

## 9. Morning package — due 08:30 IST, 4 Oct 2026
Each project, committed and pushed:
1. `research/landscape.md` — state of the art plus what companies ship today, cited.
2. `architecture/components.md` + `architecture/contracts/` — every component with contracts and an isolated metric.
3. `research/components/<component>.md` — one per component, with innovation candidates.
4. `architecture/adr/001-spike.md` — the spike choice, via six hats and thesis/antithesis/synthesis.
5. Selection memo (first version) in the thought node.
6. Round-1 deliverable draft in `deliverables/` (named in your brief).
7. Walking skeleton + eval harness with real baseline numbers. If the work is gated on hardware or the user, a simulation or mock with clearly labelled assumptions instead.
8. Stretch: a first auto-research loop on a spike, with results in `results.tsv`.
9. `thought_node.md` current; everything committed and pushed.

## 10. Cross-model review (user directive, 4 Oct)
Leads run on Claude Opus 5.5. Get second opinions from other model families, as child sessions with a model override: `create_session` with `kickoff: { prompt, mode: "autopilot", model, reasoning_effort }`.

| Role | Model | Effort |
|---|---|---|
| Methodology, statistics/maths, novelty, hostile judge (default) | `gpt-6-astra` | `max` |
| Code review, reproducibility, eval correctness | `gpt-6-sol` | `max` |
| Third opinion on contested calls | `grok-4.7` | `xhigh` |
| Long documents and PDFs, cheap reads | `gemini-3.8-flash` | default |

- The role mapping follows Oct-2026 published comparisons (secondary sources: Opus 5.5 leads agentic coding; GPT-6 Astra leads reasoning and maths). Treat it as a hypothesis; the ledger decides.
- **Minimum reviews:** the spike/ADR · the final Round-1 deliverable, before sending DONE · any headline number or claim.
- **Feedback is advisory; the lead decides.** The reviewer writes its raw review to `<slug>/reviews/<YYYY-MM-DD>-<artifact>-<model>.md`. The lead marks each item ACCEPTED or REJECTED with a reason, and adds one line to `<slug>/reviews/ledger.tsv`: date · artifact · model · effort · issues · accepted · rejected · note.
