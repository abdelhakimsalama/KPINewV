# memory-model-iq

Research note on three pillars of the NEW Copilot Studio agents experience (agents powered by the **GitHub Copilot harness**): **Memory**, **Model selection**, and **Microsoft IQ**. Compiled 2026-08-19. All Microsoft Learn content was obtained via web-search synthesis (direct fetch of learn.microsoft.com blocked in this environment); CAT-blog content was read directly from the local clone. Tags: [OFFICIAL] = documented Microsoft behavior, [CAT] = Copilot Studio CAT-blog guidance, [INFERRED] = reasoning by this author, [STATUS UNVERIFIED] = could not confirm.

---

## 1. What it is and how it works

### 1.1 Memory (per-user persistent agent memory)

- [OFFICIAL] The Learn page is titled **"Memory (preview)"** and lives under the new-experience docs tree (`agents-experience/memory-overview`). Memory "helps an agent remember details from its interactions and use that context for future interactions," so the agent delivers more relevant and consistent results over time.
- [OFFICIAL] **Lifecycle: Capture → Store → Apply.** The agent (1) *captures* signals such as user preferences and relevant context shared during conversation, (2) *stores* them **as files in a dedicated per-user folder in Microsoft-managed storage** that the agent reads from and writes to, and (3) *applies* them on subsequent interactions to inform responses or decisions.
- [OFFICIAL] **Per-user isolation.** When Memory is on, the agent keeps a **separate memory store for every user**; one person's context is never shared with another. Memories are private to the user — **the maker and other users cannot see them**.
- [OFFICIAL] **Maker enablement.** Memory is an agent-level toggle: on the **Build** tab, in the components panel, the maker turns the **Memory** toggle on or off per agent.
- [OFFICIAL] **User controls.** Two management paths: (a) **in chat** — the user asks the agent what it remembers, tells it to update a specific memory, or to forget something; (b) a **memory portal** (opens in a new browser tab) listing everything the agent stored for that user, with view/delete-all controls.
- [OFFICIAL] **Retention:** if a user does not interact with the agent for **28 days**, the system deletes that user's memories for that agent. **Memory is switched off in group chats and Microsoft Teams channels.**
- [CAT] Memory persists *facts and context*, **not files** — the agent-sandbox post is explicit that Memory "does not store files, so it is not a way to keep sandbox output around" (`2026-07-20-copilot-studio-agent-sandbox.md`).
- [CAT] In the new component model presented in the Technical Deep Dive deck, Memory's job is "**the persistent context**" — one of six components (instructions, knowledge, tools, memory, Skills, connected agents), each with its own job (`2026-07-07-new-orchestrator-resources.md`).
- [CAT] Practical use seen in the wild: with Memory enabled, an agent can "Capture a snapshot" of its harness capabilities and compare it in a later conversation (`2026-07-20-copilot-studio-agent-sandbox.md`).
- [INFERRED] Because storage is file-based in Microsoft-managed storage and keyed per user, Memory behaves like a lightweight per-user profile store, not a queryable database or shared org knowledge layer.

### 1.2 Model selection (the model powering the agent)

- [OFFICIAL] The new-experience Learn page **"Select a model for an agent"** (`agents-experience/authoring-select-agent-model`) documents choosing/configuring the AI model for GitHub-Copilot-harness agents: open the agent → **Build** tab → components panel → **Model** list → pick a model → **Save**. The model choice affects **reasoning depth** (multi-step reasoning capability), **response quality** (nuance/accuracy), and **speed** (faster models may be less capable).
- [OFFICIAL] In the classic experience the analogous page is **"Select a primary AI model for your agent"** (Overview page → Model section). There, **GPT-5 Auto** uses GPT-5's real-time router to pick between the high-throughput chat model and the deep-reasoning model per request; **GPT-5 Reasoning** pins the agent primarily to the deep-reasoning model. Separate (preview) settings existed for deep-reasoning models, generative-responses models, and the prompt builder.
- [OFFICIAL] **Anthropic models are available in Copilot Studio** (announced by Microsoft: "Anthropic joins the multi-model lineup," initially Claude Sonnet 4 and Claude Opus 4.1). Admins control availability; if Anthropic models are disabled, agents built with them **automatically fall back to the default OpenAI model** (stated as GPT-4o at announcement time; the default has since moved — see below) with no reconfiguration required.
- [CAT] Concrete model line-up evidence from CAT posts (models actually selectable in-product): "Tested with: **GPT-4.1, GPT-5 Chat, GPT-5 Auto, GPT-5 Reasoning, and Claude (Sonnet + Opus)**" (March 2026, `2026-03-13-power-of-topics-copilot-studio.md`); **Claude Sonnet 4.5** used as the agent model (Jan 2026, `2026-01-23-copilot-studio-defeating-oversummarization.md`); **Claude Sonnet 4.6** and GPT-5 Chat compared for citation behavior (May 2026, `2026-05-19-pdf-page-level-citations.md`).
- [CAT] **Behavioral differences are real and observable.** As of May 2026, GPT-5 Chat tends to return a single citation per source file while Claude Sonnet 4.6 returns multiple citations per file when multiple chunks ground the answer — "factor citation behaviour into your model selection" (`2026-05-19-pdf-page-level-citations.md`). Agents on **Anthropic models expose reasoning ("thinking") traces** as informative typing activities in the Agents SDK activity stream; as of Nov 2025, "GPT-family models in Copilot Studio do not emit thinking traces yet" — the agent model is set in Settings → Agent model (`2025-11-05-show-reasoning-agents-sdk.md`).
- [OFFICIAL] **Admin gate on non-GA models:** an environment setting **"Preview and experimental AI models"** must be on for makers to add preview/experimental models; admins can allow or block this per environment.
- [OFFICIAL] Newer models roll into early-release-cycle environments first (e.g., "GPT-5.5 Thinking is now available in Copilot Studio early release cycle environments as GPT-5.5 Reasoning," June-2026 what's-new roundup). Third-party trackers additionally list experimental variants (e.g., Grok models); exact current catalog per region/cycle is [STATUS UNVERIFIED] — check the model list in-product.
- [OFFICIAL] **Billing coupling:** GitHub-Copilot-harness agents use **Copilot Credits** usage-based billing; "Copilot credits are charged for large language model (LLM) tokens, tools (including knowledge and MCPs), and the harness itself" (`agents-experience/billing-credit-overview`). More reasoning → more tokens → more credits.

### 1.3 Microsoft IQ (organizational context layer)

- [OFFICIAL] Learn page: **"Microsoft IQ overview for agents (preview)"** (`agents-experience/use-microsoft-iq`). Microsoft IQ is a **context layer** that connects an agent to organizational data through specialized sources, configured **separately from knowledge sources** via the **Microsoft IQ** button in the Build-tab components panel.
- [OFFICIAL] **Three source families** (from `microsoft-iq-enable` / `microsoft-iq-sources` / `microsoft-iq-manage`):
  - **Work IQ** — connects the agent to the organization's **emails, chats, files, and activity**. Individual sources (**Mail, Calendar, Teams, OneDrive**) can be toggled per agent; **User Profile** and **Microsoft 365 Copilot Search** turn on by default when Work IQ is enabled.
  - **Fabric IQ** — connects the agent to business data and analytics in **Microsoft Fabric** for data-driven insights.
  - **Foundry IQ (preview)** — connects the agent to enterprise knowledge bases indexed by **Azure AI Search** / built in Azure AI Foundry.
- [OFFICIAL] **What an IQ-enabled agent can do:** answer questions about recent emails, upcoming meetings, and Teams conversations; look up people and org structure; search files in OneDrive/SharePoint; **take actions such as drafting emails or creating documents**; and use Microsoft 365 Copilot search for broad organizational queries.
- [OFFICIAL] **How it differs from knowledge sources:** knowledge sources (SharePoint, files, websites, Azure AI Search, Dataverse, Dynamics 365, Salesforce, ServiceNow, Azure SQL, etc.) are **content you explicitly add**; Microsoft IQ provides M365 organizational data that **flows dynamically based on the signed-in user's context** (`agents-experience/knowledge-copilot-studio`, `use-microsoft-iq`).
- [OFFICIAL] The broader Work IQ platform is described as three integrated layers — **Data, Memory, Inference** — unifying signals from files, emails, meetings, chats, and business systems (`microsoft-365/copilot/extensibility/work-iq`). Web sources describe Work IQ access being routed through the **Agent 365 MCP gateway / M365Copilot MCP server** ([STATUS UNVERIFIED] for the exact Copilot Studio wiring; the Work IQ MCP tool reference lives under `microsoft-agent-365/mcp-server-reference`).
- [CAT] Work IQ surfaced first as **tools/MCP servers** in Copilot Studio: the meeting-transcript autonomous agent used an MCP server renamed to "**Work IQ Copilot**" on March 13, 2026 (`2026-01-26-meeting-transcript-analyzer.md`). The **Work IQ SharePoint** connector-tool "lets your agent converse over list data, abstracting the retrieval pipeline… it handles schema discovery, query generation, retrieval, and response formatting internally… WorkIQ is not just a retrieval toolset, it's a full document management toolset" (`2026-04-30-tool-inputs-sharepoint-list.md`).
- [CAT] Work IQ also shows up inside knowledge tooling: the SharePoint knowledge method "**Connector Powered by Work IQ**" supports dynamic URL variables as of March 10, 2026 (`2026-02-11-dynamic-knowledge-urls-copilot-studio.md`).

---

## 2. When to use it / when NOT to use it

**Memory — use when:**
- [OFFICIAL→INFERRED] The agent serves **repeat, authenticated 1:1 users** whose preferences (formats, tone, recurring context, role details) should carry across conversations — the documented design center is personalization and consistency over time.
- [CAT] The behavior you want to persist is genuinely **per-user persistent context** — the component-model rule: put each behavior "in the smallest component that makes it reliable and inspectable."

**Memory — do NOT use when:**
- [OFFICIAL] The channel is a **group chat or Teams channel** — memory is disabled there.
- [CAT] You need to persist **files/artifacts** — memory stores facts/context only; return files to the user or write them somewhere durable via a Tool.
- [INFERRED] You need **shared, org-wide facts** (use Knowledge), **auditable records** (memory is user-private, user-deletable, auto-expiring at 28 days), or **guaranteed recall** (memory application is model-mediated, not a deterministic lookup).
- [CAT] Migration anti-pattern: "Don't turn… every variable into memory just because they existed — that's archaeology with YAML" (`2026-07-07-new-orchestrator-resources.md`).

**Model selection — guidance:**
- [OFFICIAL] Pick faster/high-throughput models (GPT-5 Chat-class) for routine conversational work; reasoning models (GPT-5 Reasoning-class, Claude Opus-class) for complex, multi-step tasks where accuracy beats speed; **GPT-5 Auto** delegates that choice to a per-request router (classic-experience doc).
- [CAT] Choose Anthropic models when you need **visible reasoning traces** in custom UIs (`2025-11-05`), or when citation granularity matters (`2026-05-19`). Model choice also matters for LLM-as-judge evaluation — "there is no universal best judge… treat model choice as part of the evaluation design" (`2026-06-26-better-llm-scoring.md`).
- [INFERRED] Avoid pinning reasoning models for high-volume, latency-sensitive FAQ agents: cost (credits ∝ tokens) and latency rise with little quality benefit.
- [OFFICIAL] Avoid Anthropic models if your compliance posture cannot accept **processing outside Microsoft-managed environments** (see §5).

**Microsoft IQ — use when:**
- [OFFICIAL→INFERRED] The agent serves **authenticated employees** and needs the *user's own work context* (their mail, calendar, chats, files, colleagues) or broad tenant search — things you cannot pre-enumerate as knowledge sources.
- [CAT] "If your use case is straightforward — authenticated users querying a well-structured list — start there" (Work IQ SharePoint), because it handles schema discovery/NL2Query/retrieval internally and survives schema drift (`2026-04-30`).

**Microsoft IQ — do NOT use when:**
- [INFERRED] The agent is **anonymous/external-facing** (no M365 identity → no user-context grounding; licensing requires an M365 Copilot USL per user for Work IQ — see §4).
- [CAT] You need **tight control over retrieval** — scoping tools to query patterns, shaping columns/row counts: configure connectors as tools yourself instead; "out-of-the-box tools get you started fast; configuring your own gives you precision" (`2026-04-30`).
- [INFERRED] Static curated content answers the question — plain knowledge sources are cheaper per response than tenant-graph-grounded retrieval (see §6).

---

## 3. Classic-experience comparison (what it replaces or simplifies)

- **Memory** replaces ad-hoc state hacks. [CAT] Classic agents had only conversation-scoped context: "this isn't about 'memory' à-la ChatGPT. The agent still knows what you talked about if you resume the conversation" — persistence beyond that required custom work (`2026-02-20-webchat-conversation-history-m365-sdk.md`); Teams deployments needed manual handling of "persistent memory" nuances (`2025-11-11`). [INFERRED] In classic, makers simulated personalization with global variables, Dataverse tables, or channel-passed context — all maker-visible and maker-managed. New-experience Memory is platform-managed, user-private, and toggle-simple, but correspondingly less controllable (no maker read access, fixed 28-day TTL).
- **Model selection** is simplified and unified. [OFFICIAL] Classic exposed a *primary model* plus separate (preview) model settings for deep reasoning, generative responses, and prompt builder; the new experience exposes **one agent model** in the Build components panel that powers the whole harness loop. [CAT] The migration plugin (`/migrate`) rebuilds Standard-harness agents for the new harness rather than porting settings 1:1 (`2026-07-07`).
- **Microsoft IQ** consolidates what classic scattered across **tenant graph grounding** of generative answers, Graph-connector knowledge, SharePoint knowledge methods, and **Work IQ tools/MCP servers** ("Work IQ in Microsoft Copilot Studio (preview)", `add-work-iq`). [INFERRED] In the new experience these become one governed panel (Work IQ / Fabric IQ / Foundry IQ) with per-source toggles, rather than N separately configured tools and knowledge entries. The CAT posts show the transition mid-flight: Work IQ as MCP tools (Jan–Apr 2026) → Microsoft IQ as a first-class component (docs, preview).
- [OFFICIAL] Harness context: the **GitHub Copilot harness became generally available and the default on ~Aug 3, 2026** (Learn "Choose a harness" + third-party reporting, date via schneider.im — treat exact day as [STATUS UNVERIFIED]); Standard-harness agents remain supported, and agents **cannot be transferred between harnesses**.

---

## 4. Limitations, GA/preview status, licensing notes

- **Statuses (as of 2026-08-19):**
  - GitHub Copilot harness / new agents experience: **GA** (default harness) [OFFICIAL].
  - **Memory: preview** — page titled "Memory (preview)" [OFFICIAL].
  - **Microsoft IQ in Copilot Studio: preview** — overview, enable, and manage pages all "(preview)"; **Foundry IQ explicitly (preview)** within it [OFFICIAL]. Broader "Microsoft IQ" platform positioning (Build 2026) claims GA of the context layer overall — status differs by surface; the Copilot Studio surface is preview [OFFICIAL, third-party corroborated].
  - **Model selection**: the new-experience model page carries no visible preview marker in search results [STATUS UNVERIFIED whether GA]; **preview/experimental models** are gated by the environment setting; GPT-5 was announced GA in Copilot Studio (Aug 2025, excluding GCC) [OFFICIAL]; classic deep-reasoning/generative-response model pickers were (preview) [OFFICIAL].
- **Memory limits:** 28-day inactivity deletion; disabled in group chats/Teams channels; per-agent, per-user scoping; no file storage [OFFICIAL/CAT]. No documented size/count quota found [STATUS UNVERIFIED].
- **Licensing/billing:**
  - [OFFICIAL] New-harness agents bill via **Copilot Credits** (tokens + tools/knowledge + harness). Reported per-feature rates from Learn billing pages via search synthesis: **tenant graph grounding ≈ 12 credits per response; other knowledge ≈ 2 credits per response; tool invocations ≈ 5 credits per call; standalone agent flows 13 credits per 100 actions**; credit ≈ $0.01 pay-as-you-go, or capacity packs of **25,000 credits / $200 / month**. Exact current rate card evolves — verify against `billing-credit-overview` before costing [OFFICIAL, numbers stated by sources but rate-card drift possible].
  - [CAT] **Design-time consumption is real:** makers consume Copilot Credits while building, previewing, and evaluating new-harness agents (identified by the `isCLIAgent` property via Power Platform API); PPAC supports environment allocations, agent-level monthly limits, notification thresholds, and stop-on-limit (`2026-08-07-copilot-harness-cost-governance.md`).
  - [OFFICIAL] **Work IQ requires a Microsoft 365 Copilot license per user**; employee-facing agent usage is included in the M365 Copilot USL when running under a licensed user's authenticated identity (Copilot Studio Licensing Guide, Aug 2026). Admin consent for **WorkIQAgent.Ask** is required before users can authenticate ([OFFICIAL via secondary summary — verify]). Work IQ is **read-only unless an admin enables write operations** in the M365 admin center [OFFICIAL via search synthesis].
  - [OFFICIAL] **Anthropic model use requires tenant-admin opt-in** in the M365 admin center plus PPAC controls for Copilot Studio/Power Platform.
- **Conflicts/staleness observed:** third-party posts name newer models (Claude Sonnet 4.6+, "GPT-5.5 Thinking", Grok variants) and different defaults (GPT-4o → GPT-4.1 → GPT-5-era) at different dates; the *default model* for new-harness agents today is [STATUS UNVERIFIED]. One search response surfaced apparently confused model names ("GPT-5.6 Sol", "Opus 5", "Fable 5") from a low-quality source — **not** treated as fact here.

---

## 5. Security and governance implications

- **Memory:**
  - [OFFICIAL] Strong privacy defaults: user-private (invisible to makers/other users), user-controllable (in-chat forget/update + memory portal delete-all), auto-expiry after 28 days of inactivity, off in shared surfaces. Data sits in **Microsoft-managed storage**.
  - [INFERRED] Because users can silently delete memories and the system expires them, memory must never be the system of record for anything compliance-relevant (consents, commitments, case data) — persist those via Tools into Dataverse/appropriate systems.
  - [STATUS UNVERIFIED] Tenant-level admin kill-switch specifically for *Copilot Studio agent* Memory: the documented PowerShell/Graph tenant controls (disable memory, exclude groups) belong to **Microsoft 365 Copilot personalization/memory** (`copilot-personalization-memory`); whether they also govern Copilot Studio agent Memory was not confirmed.
- **Model selection:**
  - [OFFICIAL] **Anthropic models run on Anthropic-hosted infrastructure (AWS), outside Microsoft-managed environments**; Microsoft states its standard customer agreements/DPA **do not apply** to Anthropic's processing (Anthropic acts as a subprocessor with contractual safeguards; Customer Copyright Commitment applies where the product is covered). Tenant admins must explicitly enable; disabling triggers automatic fallback to the default OpenAI model (`microsoft-365/copilot/connect-to-ai-subprocessor`, Anthropic-lineup blog).
  - [OFFICIAL] Preview/experimental models are governable per environment ("Preview and experimental AI models" setting).
  - [INFERRED] Data-residency/EU-boundary commitments should be re-validated whenever the agent model is switched across providers; model choice is now a *governance* decision, not just a quality one.
- **Microsoft IQ:**
  - [OFFICIAL] Grounding **enforces existing M365 permissions** — agents see what the signed-in user can see (Microsoft IQ positioning; Work IQ identity-scoped access). Write actions (draft email, create documents) are off unless admins enable write operations.
  - [OFFICIAL] Environment-level availability is admin-controlled ("Microsoft IQ must be available in your environment — contact your administrator").
  - [INFERRED] Because IQ output is dynamic per-user data, transcript/analytics handling inherits personal-data sensitivity (emails, calendars, chats appear in conversation context). DLP policies and the no-egress sandbox boundary ([CAT] `2026-07-20`: external reach only via configured Knowledge/Tools, all within governance controls and data policies) remain the enforcement points.

---

## 6. Performance and maintainability implications

- **Memory:** [INFERRED] Applying memory adds retrieval/context overhead per turn but is platform-managed; the bigger effect is *behavioral drift per user* — the same agent answers differently for different users, so evals against a fixed persona won't capture personalized behavior. [CAT] Keep memory to its job (persistent context); overloading it degrades inspectability (`2026-07-07`).
- **Model selection:**
  - [OFFICIAL] Explicit trade-off triangle: reasoning depth vs response quality vs speed; reasoning models are slower and consume more tokens → more Copilot Credits [INFERRED coupling via billing doc].
  - [CAT] **Re-run evals on every model change**: citation behavior, oversummarization tendencies, and judge reliability all vary by model (`2026-05-19`, `2026-01-23`, `2026-06-26`); the eval-gate pattern (`2026-04-19`, referenced from sandbox post) automates regression checks.
  - [OFFICIAL] GPT-5 Auto's router is a maintainability convenience (no manual per-scenario model pinning) at the cost of run-to-run variability [INFERRED].
- **Microsoft IQ:**
  - [CAT] Work IQ's dynamic schema discovery removes a whole maintenance class: hand-built connector tools "break silently" when someone renames a SharePoint column; "Work IQ doesn't have this problem because it discovers the schema dynamically" (`2026-04-30`).
  - [OFFICIAL] Cost asymmetry: tenant-graph-grounded responses bill several times higher than ordinary knowledge responses (≈12 vs ≈2 credits per response in the reported rate card) — high-volume agents should reserve IQ for queries that need it [INFERRED from official rates].
  - [CAT] Retrieval is not the response: whatever IQ or tools return still has to fit and be reasoned over in context; filter early, keep result sets small (`2026-04-30`).

---

## 7. Architecture guidance and anti-patterns

**Guidance:**
1. [CAT] **Component-first design:** instructions = always-true behavior; Knowledge = searchable facts; Tools = system actions; **Memory = persistent context**; Skills = situational procedures; connected agents = specialist domains. Put each behavior in the smallest reliable, inspectable component (`2026-07-07`).
2. [CAT+INFERRED] **Layer your data access:** curated Knowledge for stable documents; Microsoft IQ for dynamic, user-scoped org context; self-configured connector tools (dynamic inputs/NL2Query) when you need precision, scoping, or response shaping; hybrid semantic-then-structured chaining when both matter (`2026-04-30`).
3. [INFERRED] **Memory for preferences, systems for records:** route durable business facts through Tools into Dataverse/line-of-business systems; let Memory hold only per-user context you can afford to lose (28-day TTL, user deletion).
4. [CAT] **Model changes are releases:** pair any model switch with the agent's eval suite (bulk file testing, eval gates) and re-verify citation/format behavior (`2026-05-19`, `2026-04-19`).
5. [CAT] **Govern spend from day one:** classify environments, allocate credits, set agent-level limits with alerts — maker experimentation on the new harness burns credits pre-production (`2026-08-07`).
6. [OFFICIAL→INFERRED] **Match IQ scope to need:** enable only the Work IQ sources (Mail/Calendar/Teams/OneDrive) the scenario requires; remember User Profile + M365 Copilot Search come on by default with Work IQ.

**Anti-patterns:**
- [CAT] Migrating classic agents by mapping every topic→Skill and every variable→Memory ("archaeology with YAML").
- [CAT] Designing conversations that expect sandbox files or prior outputs to persist — Memory doesn't store files; the sandbox is temporary.
- [OFFICIAL→INFERRED] Relying on Memory in Teams channels/group chats (disabled) or for cross-user "shared memory" (per-user by design).
- [INFERRED] Enabling Microsoft IQ on anonymous/external agents (no user identity, no license coverage) or as a substitute for curated Knowledge on static content (cost, precision).
- [INFERRED] Choosing an Anthropic model without a governance sign-off on extra-Microsoft processing, or pinning a deep-reasoning model on a high-volume FAQ agent (latency + credit burn).
- [CAT] One instruction blob with dozens of tools and no component separation — "an agent shouldn't be one instruction blob with 43 tools and a prayer" (`2026-07-07`).

---

## 8. Sources

**Local CAT-blog posts (read in full or in relevant part):**
- /workspace/microsoft/mcscatblog/_posts/2026-01-26-meeting-transcript-analyzer.md (Work IQ Copilot MCP rename; autonomous M365 agent)
- /workspace/microsoft/mcscatblog/_posts/2026-07-07-new-orchestrator-resources.md (component model incl. Memory; migration guidance)
- /workspace/microsoft/mcscatblog/_posts/2026-07-20-copilot-studio-agent-sandbox.md (Memory ≠ file storage; snapshot pattern; governance boundary)
- /workspace/microsoft/mcscatblog/_posts/2026-04-30-tool-inputs-sharepoint-list.md (Work IQ vs self-configured tools; schema drift; hybrid retrieval)
- /workspace/microsoft/mcscatblog/_posts/2025-11-05-show-reasoning-agents-sdk.md (Anthropic model config; reasoning traces; GPT no-thinking caveat)
- /workspace/microsoft/mcscatblog/_posts/2026-05-19-pdf-page-level-citations.md (model-dependent citation behavior, May 2026) — via grep excerpts
- /workspace/microsoft/mcscatblog/_posts/2026-03-13-power-of-topics-copilot-studio.md (models tested list, reasoning loop) — via grep excerpts
- /workspace/microsoft/mcscatblog/_posts/2026-01-23-copilot-studio-defeating-oversummarization.md (Claude Sonnet 4.5 as agent model) — via grep excerpt
- /workspace/microsoft/mcscatblog/_posts/2026-02-11-dynamic-knowledge-urls-copilot-studio.md (SharePoint "Powered by Work IQ" knowledge method) — via grep excerpts
- /workspace/microsoft/mcscatblog/_posts/2026-02-20-webchat-conversation-history-m365-sdk.md (classic "not memory" clarification) — via grep excerpt
- /workspace/microsoft/mcscatblog/_posts/2026-08-07-copilot-harness-cost-governance.md (design-time credit consumption; isCLIAgent; PPAC limits) — via grep excerpts
- /workspace/microsoft/mcscatblog/_posts/2026-06-26-better-llm-scoring.md (judge model selection) — via grep excerpt

**Microsoft Learn / Microsoft sources (accessed via WebSearch synthesis; direct fetch blocked):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/memory-overview — Memory (preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/use-microsoft-iq — Microsoft IQ overview (preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/microsoft-iq-enable — Turn on Microsoft IQ (preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/microsoft-iq-manage — Manage Microsoft IQ sources (preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/microsoft-iq-sources — Available knowledge/IQ sources
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-copilot-studio — Knowledge overview (preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/authoring-select-agent-model — Select a model for an agent (new experience)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model — Select a primary AI model (classic)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview — GitHub Copilot harness overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview — Choose a harness
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview — Usage-based billing (Copilot Credits)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-work-iq — Work IQ in Copilot Studio (preview, classic surface)
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/ — Work IQ overview (Data/Memory/Inference)
- https://learn.microsoft.com/en-us/microsoft-agent-365/tooling-servers-overview — Work IQ MCP overview (preview)
- https://learn.microsoft.com/en-us/microsoft-365/copilot/connect-to-ai-subprocessor — Anthropic models in Microsoft Online Services
- https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-personalization-memory — M365 Copilot personalization/memory admin controls
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/anthropic-joins-the-multi-model-lineup-in-microsoft-copilot-studio/ — Anthropic lineup announcement
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/available-today-gpt-5-in-microsoft-copilot-studio/ — GPT-5 in Copilot Studio (GPT-5 Auto/Reasoning)
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/more-powerful-agents-and-workflows-for-autonomous-business-processes-introducing/4542969 — new harness announcement
- Microsoft Copilot Studio Licensing Guide (Aug 2026 PDF, cdn-dynmedia-1.microsoft.com) — M365 Copilot USL coverage of agent usage

**Third-party (used only for corroboration/dates; flagged where load-bearing):**
- https://www.schneider.im/microsoft-copilot-studio-github-copilot-harness-available/ — GA date claim (~2026-08-03)
- https://powerplatstack.substack.com/p/copilot-studio-now-supports-claude — model catalog snapshots
- https://holgerimbery.blog/iqs ; https://windowsnews.ai/article/microsoft-iq-at-build-2026-context-layer-powering-enterprise-agents-work-iq-fabric-iq.423529 — Microsoft IQ positioning
- https://chasingnext.com/updates/copilot-studio-agent-memory — memory preview summary (fetch blocked; search snippet only)
