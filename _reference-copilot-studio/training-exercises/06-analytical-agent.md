# Exercise 06: Proseware Sales KPI Analyst

## 1. Business need

Regional managers upload weekly Excel sales exports and ask conversational questions: "What was West region's margin last week?", "Compare attach rate Q1 vs Q2", "Flag anything unusual", "Chart revenue growth by region." Finance's non-negotiable: every KPI number must be **exact and reproducible** — computed by governed formulas, never estimated by a model. The KPI definitions (growth, margin, attach rate) are owned by Finance and versioned. Outputs: numbers, comparisons, anomaly flags, and charts, returned in the conversation.

## 2. Classic-style architecture

In classic Copilot Studio (Standard harness) this is a topic-and-flow machine, because the platform has no native compute:

**Topics (11):** T1 Greeting & Menu; T2 Upload Weekly Export (Question node, File entity, validation branches); T3 Calculate Growth; T4 Calculate Margin; T5 Calculate Attach Rate; T6 Compare Periods; T7 Compare Regions; T8 Flag Anomalies; T9 Generate Chart; T10 KPI Definitions FAQ (generative answers over the policy doc); T11 Fallback/Escalate. Each KPI topic carries trigger phrases plus condition branches to disambiguate period/region and handle flow errors.

**Power Automate agent flows (5):** F1 Parse Sales Export (drop file to SharePoint, Excel Online connector/Office Script reads rows, returns JSON string — Text-only I/O, 1 MB return cap forces pagination); F2 Compute KPIs (calls an Azure Function implementing the governed formulas — Power Fx cannot own them credibly); F3 Compare Periods/Regions (parameterized wrapper on F2); F4 Detect Anomalies (z-score thresholds in the Function); F5 Render Chart (Azure Function with a chart library, writes PNG to SharePoint, returns URL).

**Supporting infrastructure:** 1 Azure Function app (~3 functions — this is where "exact math in code" lived classically), 1 SharePoint library for staged files/charts, connection references for each connector.

**Component count:** 11 topics, ~11 trigger-phrase sets, ~28 condition branches, ~22 topic/global variables with Power Fx glue (JSON parse/serialize at every flow boundary), 5 flows, 3 Azure Functions, 1 SharePoint staging library. Every flow call fights the 100-second synchronous limit and Text/Boolean/Number-only parameters; every schema tweak risks `FlowActionBadRequest` until tools are refreshed. Roughly **50 moving parts across four services**.

## 3. New-experience redesign

One GitHub Copilot harness agent (GA 2026-08-03). The architectural insight of this exercise: **the sandbox replaces the entire compute/plumbing stack**, and because the work is self-contained — file in via chat, compute local, file out via chat, no side effects — the agent needs **zero tools and zero workflows**.

- **Instructions (summary):** Role — Proseware Sales KPI Analyst for regional managers. Every KPI value must come from executing the `proseware-kpi-calculations` skill's script; never compute KPIs mentally; reproduce the script's results block verbatim. If period/region is ambiguous, ask before computing. Decline forecasts and any question the uploaded data cannot answer; state plainly when data is absent. If no file has been uploaded this conversation, request one — never answer from memory of prior files. Cite the KPI Policy Handbook for definition questions.
- **Knowledge (1):** *Proseware KPI Policy Handbook* (uploaded PDF) — human-readable definitions, fiscal calendar, anomaly-threshold policy; used for cited definition Q&A only, never for computation. (Uploaded-file knowledge has no per-user RBAC — acceptable, the handbook is not sensitive.)
- **Skills (1):** `proseware-kpi-calculations` — SKILL.md + `scripts/kpi_calc.py` (governed formulas: growth, margin, attach rate; period/region comparison; anomaly z-scores; canonical rounding and formatted results block) + `scripts/kpi_charts.py` (standard chart styles) + `references/column-mapping.md` and `references/kpi-definitions.md` (machine-readable formula spec, mirroring the Handbook). Routing description: "Use for ANY calculation, comparison, anomaly check, or chart over an uploaded Proseware sales export, including every follow-up refinement in the same task. Do not use for KPI definition questions (use knowledge) or for data the user has not uploaded." The follow-up clause matters — skills can silently drop out on refinements (CAT-documented bug).
- **Tools:** none (see §8).
- **Workflows:** none (see §9).
- **Memory:** OFF (see §10).
- **Connected agents:** none (see §11).
- **Model:** a GA primary model — GPT-5.5 Chat or Claude Sonnet 4.5/4.6. No reasoning-model premium needed: the hard part is deterministic code, not deep reasoning. If Anthropic is chosen, tenant opt-in is required and processing occurs on Anthropic-hosted infrastructure outside Microsoft-managed environments — a governance decision, not just a quality one.

**Authored components: 3** (instructions, one knowledge source, one skill). The sandbox (Python 3.12.9, ~99 preinstalled libraries, no egress, ephemeral) is ambient, not configured.

## 4. Removed components

| Component | Classic | New | What disappears |
|---|---|---|---|
| Topics | 11 | 0 | Orchestrator routes; skill description replaces trigger phrases |
| Trigger-phrase sets | ~11 | 0 | Description-based routing |
| Condition branches | ~28 | 0 | Reasoning loop handles disambiguation/errors |
| Variables + Power Fx glue | ~22 | 0 | Loop reasons over conversation and code output |
| Agent flows | 5 | 0 | Sandbox executes locally; no 100 s / 1 MB / Text-only boundaries |
| Azure Functions | 3 | 0 | Governed math moves into the skill script |
| SharePoint staging library | 1 | 0 | Files travel in-conversation |
| Instructions | 1 blob | 1 lean doc | — |
| Knowledge sources | 1 | 1 | — |
| Skills | 0 | 1 (2 scripts) | New, replaces the Function app |
| **Total** | **~82 authored artifacts (~50 major)** | **3** | — |

## 5. Role of Instructions

**In:** identity/audience; the always-true grounding rule ("KPI numbers only from the skill script, reproduced verbatim"); ambiguity handling (ask which periods/regions); refusal policy (no forecasts, no invented data, no answers without an upload); citation policy for definition questions; output shape (results block first, brief narrative after).

**Deliberately NOT in:** the KPI formulas (they live in the script — instructions are probabilistic, code is deterministic); column mappings and calculation procedure (skill references — situational, loaded on demand); the Handbook text (knowledge); per-tool routing hints (no tools). Instructions load fully every turn and bill every turn — keep them lean. Instructions are also **not a guarantee**: "reproduce verbatim" raises the bar; the eval suite (§12) is what enforces it.

## 6. Role of Knowledge

One uploaded file: the KPI Policy Handbook, for cited, human-readable answers to "how does Proseware define attach rate?" It is deliberately **not** the computation source — knowledge retrieval is top-N and synthesized, unacceptable for formulas of record. The machine-readable formula spec is duplicated in the skill's `references/` so the executing code path never depends on retrieval. The weekly exports themselves are **not** knowledge: they change weekly and are conversation-scoped uploads that land in the sandbox, where the script reads every row (no retrieval-snippet truncation). Dual-maintenance of Handbook vs `references/kpi-definitions.md` is a real cost — a documented release-checklist item.

## 7. Role of Skills

The skill is the load-bearing wall — this exercise's core trade: **generated code vs a Skill-packaged script**. Letting the agent write pandas code per conversation works but is slower, costs credits per fail/rewrite iteration, and — decisively — allows run-to-run variance in *governed financial definitions* (is growth QoQ or WoW? which rounding?). Finance requires one reviewed, versioned implementation. So: use CAT's four-phase method — prototype with the agentic loop on real exports, let it fail and converge, strip hardcoding, freeze the generalized logic into `scripts/kpi_calc.py` (the redlining case measured ~60x speedup, 15 min → 15 s, plus identical output every run). The script ships through solutions/ALM and is code-reviewed like any Finance asset. Chart generation stays in `kpi_charts.py` for consistent house style, but chart cosmetics may tolerate model adaptation — numbers may not. Generated code remains the fallback for genuinely novel ad-hoc analysis the script doesn't cover, and the instructions permit it **only** for non-KPI exploration, clearly labeled.

## 8. Role of Tools

**None — and that is the design.** Every classical reason for a tool is absent: data arrives by in-conversation upload; compute is local (sandbox); outputs (tables, charts, an Excel summary if asked) return in-conversation; there is no system of record to write. The sandbox's **no-egress boundary becomes a governance feature**: commercially sensitive sales data physically cannot leave the agent except through the conversation itself. Zero tools also deletes an entire failure class (wrong-tool activation) and its DLP surface. The one trigger to add a tool later: "archive this report to SharePoint" → a single SharePoint connector tool with end-user credentials. Until a user asks, adding it is speculative surface area.

## 9. Role of Workflows

**None.** Workflows earn their place for deterministic *side effects* — approvals, transactions, multi-system sequences. This agent has no side effects: it is read-compute-respond. The determinism the scenario demands is *computational*, and it is already satisfied by the deterministic script inside the skill — a workflow wrapping the same Python would add a 100-second synchronous ceiling, Text/Boolean/Number I/O conversions, and a second ALM artifact for zero gain. If Finance later requires "publish approved KPIs to the reporting mart with sign-off," that specific step becomes a workflow (approval gate + write), invoked async — the agentic core stays as-is.

## 10. Memory decision

**OFF.** Memory [PREVIEW] is per-user persistent context; here it is actively harmful: (a) **reproducibility** — Finance requires the same file + question to yield the same answer for every manager; per-user memory introduces per-user behavioral drift; (b) users may believe last week's uploaded file persists ("what was growth again?" answered from remembered numbers rather than a fresh run) — memory stores facts, not files, and stale remembered KPIs are exactly the hallucination class we must prevent; (c) 28-day expiry and user-deletability make it unusable as any record. The instructions' "never answer without an upload in this conversation" rule pairs with memory-off.

**Test the difference:** duplicate the agent, memory ON; run the same conversational eval set under two simulated user profiles across two sessions (upload in session 1, ask for KPIs in session 2). The memory-off agent must request a fresh upload; measure whether the memory-on agent ever emits a number without executing the script (activity-trace check). Also diff answers across the two profiles for drift.

## 11. Connected Agents decision

**No.** One audience (regional managers), one security boundary, one domain, ~1 skill — far below the context-saturation threshold that justifies splitting ("three agents are often one agent with three skills"). Each delegation hop would add latency and a second orchestration's credit burn for nothing. Future exception worth naming: if Proseware lands its sales data in Microsoft Fabric, a **Fabric data agent** connection [preview/GA in transition — verify per page] could replace file uploads with governed live queries — a genuinely different data boundary, and the legitimate trigger for multi-agent.

## 12. Evaluation plan

Numeric correctness cannot be judged by an LLM grader — use deterministic checks first (CAT's better-llm-scoring rule: binary, evidence-backed checks; no 1–5 vibes).

**Fixtures:** 8 synthetic weekly exports + gold-standard expected values computed twice independently (the reviewed script AND a hand-built spreadsheet), versioned with the agent source.

**Single-response test set (≤100 cases), Evaluate tab:**
- *Expected answers (~40):* every KPI × period × region against gold values; grade with **Exact match** on the script's canonical results block (fixed rounding makes exact match viable). [PREVIEW flag: Evaluate pages in the new experience still carry preview labels, and third-party reports questioned exact-match availability at launch — verify in-tenant; fallback = Evaluation REST API + scripted comparison, or Copilot Studio Kit.]
- *Unsupported questions (~10):* "Forecast next quarter", "What's our stock price?", "Which rep will hit quota?" → custom grader labels compliant only if the agent declines/labels estimates.
- *Ambiguity (~8):* "What's growth?" (no period), "How's margin?" (no region) → must ask a clarifying question, not guess.
- *Hallucination resistance (~10):* region "Atlantis" not in file → "not present"; KPI question before any upload → request upload; a column referenced that doesn't exist → explicit error, not silence.
- *Edge cases (~15):* zero prior-period revenue (division by zero → policy answer "n/a", not ∞), negative margin, duplicate rows, missing column, mixed currencies (must flag, not sum), 100k-row file (resource-quota probe), Excel dates as text.
- *Skill activation (~10):* paraphrases ("how'd West do vs last week?") must load the skill; definition questions must NOT (knowledge instead). With zero tools, wrong-tool activation is structurally impossible — the analogue is **mental-math bypass**: activity-trace review confirms code actually executed for every numeric answer; make "no number without a code run" a written release criterion.

**Conversational set (≤20 cases, ≤6 Q/A pairs):** follow-up refinements ("now just hardware", "same but Q1") — catches the skill drop-out failure the description clause targets.

**Regression triggers (re-run full suite):** any instructions/SKILL.md/script edit; model change; monthly scheduled run (connector-triggered) to catch **sandbox library drift** — pair with an agent-harness-explorer inventory snapshot diff; before export and after import in each ALM stage; Evaluation REST API gate in the ADO PR pipeline (delegated-auth token in Key Vault; note the 90-day refresh-token idle expiry). Budget evals like load tests — runs consume credits at runtime rates.

## 13. Risks and mitigations

- **Verbatim-number risk (the honest one):** the final response is composed by the model; it can paraphrase or transpose a script-produced figure. Instructions reduce this; only exact-match evals *detect* it; classic's deterministic `SendActivity` "send exact message" has **no new-experience equivalent**. Mitigation: script emits one canonical block; exact-match gate on every release; spot-audit activity traces. Residual risk is real and must be stated to Finance.
- **Sandbox dependency churn [GOVERNANCE]:** no `pip install`; ~99 libraries observed 2026-07-21 and explicitly changeable. [ASSUMPTION] pandas/openpyxl/matplotlib are present — inventory with agent-harness-explorer **before** writing the script; code against confirmed libraries with stdlib fallbacks; monthly drift snapshot + eval gate.
- **Preview surfaces [PREVIEW]:** Memory (unused — good), uploaded-file knowledge in the new experience, file collections, Evaluate-tab labels/methods, Evaluation REST API auth model (delegated-only). Harness itself GA 2026-08-03, but treat status per feature; verify page banners before production commitments.
- **Cost/credit [COST]:** billing starts at build time (authoring, preview, evals all bill); the agentic loop's iteration count varies per conversation, so per-conversation cost varies — less predictable than classic's flat meters. Mitigations: agent-level monthly credit limit with alert threshold; environment allocation with Deny off tenant pool for the dev environment; the packaged script itself is the biggest cost control (no fail/rewrite loops); smoke evals per PR, full suite nightly.
- **Data governance [GOVERNANCE]:** sales exports are commercially sensitive; they flow through conversations, so **transcripts hold the data** — restrict Bot Transcript Viewer, review retention; no-egress sandbox means no other exit path. Uploaded knowledge has no RBAC (Handbook only — keep it that way). Anthropic model choice requires sign-off for processing outside Microsoft-managed environments; otherwise pin GPT-5.5 Chat.
- **Resource quotas [UNVERIFIED]:** sandbox time/CPU/memory limits are unpublished; cap accepted file sizes in instructions and test the 100k-row case; very large estates belong in Fabric (§11).
- **Dual-source definitions:** Handbook vs skill references can diverge — single release checklist updates both, eval definition-questions catch drift.

## 14. Verdict

This scenario is close to the new experience's best case: **~50 major classic components (11 topics, 5 flows, 3 Azure Functions, ~28 branches, ~22 variables, plus SharePoint plumbing) collapse to 3 authored components** — lean instructions, one knowledge source, one skill — with zero tools and zero workflows, because the sandbox absorbs compute, file handling, and charting, and its no-egress boundary doubles as the data-governance story. The determinism Finance demands is **kept, not sacrificed**: it moves from an Azure Function into a reviewed, versioned skill script — arguably *more* governable, since it ships through the same solution as the agent and is regression-gated by evals. Where the new experience does **not** help: (1) no hard guarantee the model transcribes script output verbatim — a residual probabilistic layer classic's direct message nodes didn't have; mitigated, not eliminated, by exact-match eval gates; (2) per-conversation cost is variable where classic was flat-metered; (3) several load-bearing surfaces (Evaluate methods, uploaded-file knowledge) still carry preview labels. None of these justify the classic build's 50-part machine — but the eval suite is not optional polish here; it is the compensating control that makes the probabilistic layer acceptable to Finance. If the scope ever grows a side effect (publishing KPIs of record, approvals), that step — and only that step — gets a deterministic workflow.
