# orchestration

Research note — Enhanced/generative orchestration in Microsoft Copilot Studio, with emphasis on the new "agents experience" (GitHub Copilot harness) orchestrator. Compiled 2026-08-19. Claims are tagged [OFFICIAL] (documented Microsoft behavior on Learn or in a CAT post citing product behavior), [CAT] (CAT-blog practice/guidance), or [INFERRED] (analyst reasoning). Status flags per claim.

## 1. What it is and how it works

There are now **three distinct orchestration generations** in Copilot Studio, and terminology matters:

1. **Classic orchestration** — NLU-based: user input matches configured trigger phrases, one topic fires, its authored dialog runs. [OFFICIAL — Learn "AI-based agent authoring overview", third-party corroboration]
2. **Generative orchestration** (the "enhanced" mode of the classic/standard experience) — an LLM-driven planning layer that "interprets user intent, breaks down complex requests, selects the right tools and knowledge, and executes multistep plans with guardrails." GA for English (en-US) agents since **March 2025**. [OFFICIAL — Learn "Apply generative orchestration capabilities"; GA date from Microsoft Copilot Blog March 2025]
3. **The new-experience orchestrator** — the runtime under the **GitHub Copilot harness** in the new "agents experience". It is an "enhanced orchestration model that improves response quality and reasoning capability", supports deep reasoning, Skills, memory, and Microsoft IQ, and is the **default with no toggle** for agents created in the new experience. [OFFICIAL — Learn agents-experience/overview] The CAT team describes it as "a big shift… agents are far more adaptive and sophisticated," with a new component model: Instructions, Knowledge, Tools, Memory, Skills, connected agents. [CAT — "New Harness, New Rules?" 2026-07-07]

### How the planner works (generative orchestration and newer)

- The orchestrator receives the user message (or a `Recognize intent` node's text — a "programmatic way to trigger the orchestrator on demand" [CAT — "The Orchestrator's Secrets"]), identifies intent(s), and constructs a **plan**: which topics/tools/agents to invoke, in what sequence, and the data flow between steps. [OFFICIAL — Learn "Orchestrate agent behavior with generative AI"]
- It runs a **"plan → execute → adjust" loop**, especially with reasoning models or when an MCP server requires multiple tool calls to converge on an answer. [CAT — "The Orchestrator's Secrets", 2026-03]
- **Slot filling is generative**: the orchestrator generates its own questions to collect missing tool inputs instead of authored Question nodes. Tool and input descriptions drive both. [OFFICIAL — Learn "Add tools to custom agents"]
- **Model choice is the orchestrator's engine.** "An agent's orchestration model powers how it interprets instructions, generates a plan, uses tools, and responds." Options include GPT-5 (with **GPT-5 Auto** routing between high-throughput and deep-reasoning variants, or **GPT-5 Reasoning** pinned), Claude Sonnet/Opus (Claude Sonnet 5 and GPT-5.5 Chat available per Learn "whats-new"). Separate model settings exist for deep reasoning (preview), generative responses (preview), and prompt builder — models can be mixed inside one agent. [OFFICIAL — Learn "Select a primary AI model"] A separate **deep reasoning model** feature (Azure OpenAI o3) is preview, US and EU (excl. UK) only. [OFFICIAL — Learn "Add a deep reasoning model (preview)"]

### How the orchestrator selects components — names and descriptions are the routing signal

- [OFFICIAL — Learn "Apply generative orchestration capabilities"]: "provide a high-quality description for each of its child agents, connected agents, topics, tools, and knowledge sources… the name and description must be accurate and specific, because the agent uses these fields to determine what to call." Learn also advises using descriptions to say **what NOT to do** "if you see the agent calling them at the wrong time."
- **Topics**: under generative orchestration the trigger node reads "The agent chooses" (description-based) instead of "User says a phrase". Switching a classic agent auto-generates a description per topic from its trigger phrases. [OFFICIAL — Learn "Create and edit topics"] In YAML the field is `modelDescription` (visible in CAT samples). [CAT — oversummarization post YAML]
- **Knowledge**: generative orchestration searches all agent-level knowledge sources by default; when there are **more than 25 knowledge sources**, an **internal GPT model filters to the most relevant sources using their descriptions** before searching. You cannot force one specific article; to scope a search you must use a generative answers node or `SearchKnowledgeSources` custom search inside a topic. [OFFICIAL — Learn "Knowledge sources summary" / generative-orchestration FAQ]
- **Connected agents**: "Descriptions drive delegation — the orchestrator uses the connected agent's description to decide when to route to it." The primary agent passes relevant conversation history plus the user message. [OFFICIAL — Learn "Connected agents overview" (agents-experience)] Inputs/outputs "inform the main agent" and simultaneously define the child's task; on the main-agent side a connected agent is a `TaskDialog` with `modelDisplayName`/`modelDescription`. [CAT — "Using Inputs and Outputs in Child and Connected Agents"]
- **Input variable descriptions are instructions.** "The orchestrator reads input variable descriptions to decide what data to pass in, so the description doubles as an instruction" — this is powerful enough that CAT uses it to make the orchestrator dump its chain-of-thought or the entire best-effort conversation transcript into a topic input variable. [CAT — "The Orchestrator's Secrets"]
- **Skills (new experience)**: only Skill **name + description metadata** sits in context by default; full instructions/resources load on demand when the orchestrator judges the task matches. This lazy-metadata model applies uniformly: "knowledge sources, tools, and Skills are all registered the same way — only their metadata sits in context by default" (agent instructions are the exception, always fully loaded). [CAT — "Agents Have Skills Now", 2026-06, describing product behavior]

### How to influence orchestration

- **Contextual instructions steer the plan**: "Instructions act as guidelines that the orchestrator follows not only to provide context for the answer but also to plan its actions." Canonical pattern: "When the question involves monthly KPIs, use the MCP tool for data and then consult the knowledge base for corrections; if corrections exist, include them" — makes the orchestrator chain MCP + knowledge and merge, but only conditionally. [CAT — "Influencing Agent Planning with Contextual Instructions", 2025-11]
- **Reference components exactly** using the slash (`/`) syntax in the instructions editor so names resolve to the exact tool/topic/agent/variable. [OFFICIAL — Learn "Write agent instructions"; CAT — "The Orchestrator's Secrets"]
- Learn's guidance: add instructions **only where the right tool/knowledge choice is ambiguous**; otherwise let descriptions carry the routing. [OFFICIAL — Learn "Configure high-quality instructions for generative orchestration"]

### How to debug what the orchestrator did

- **Activity map / test pane** (standard experience): shows the orchestrator's plan in real time — which topics/tools were invoked, in what order. Learn suggests turning off "Show activity map" only for convenience when not debugging. [OFFICIAL — Learn "Test your agent", "authoring-review-activity"]
- **Reasoning view** (new experience): "your main debugging surface" — watch the agent load a Skill and follow its steps; "if a Skill fires too often, the description is probably too broad; if it never fires, the description is too narrow." [CAT — "Agents Have Skills Now"]
- **Test-pane snapshot**: `... → Save snapshot` downloads a `botcontent` zip with `dialog.json` containing: `IntentRecognition` activities with `TopicName` and `Score`, `DialogRedirect`s, tool/MCP/connected-agent event activities with payloads, **generative orchestration trace data showing the plan**, `SearchAndSummarizeContent` in `nodeTraceData` (knowledge searched + chunks returned), per-activity timestamps, `SessionInfo` outcomes, CSAT. [CAT — "Open the Hood", 2026-03]
- **Dataverse `ConversationTranscript`** (full JSON incl. orchestration plan; ~30-min write delay; 30-day default retention; 1 MB per record, split by `BatchId`; not written in developer environments) vs. **Application Insights** (near real-time; errors/latency/dependencies; tool calls appear as `TopicStart` events; **no** plan, knowledge detail, intent scores, or session outcomes). [CAT — "Open the Hood: Technical Reference"]
- **Chain-of-thought visibility**: with a deep reasoning model, "the chain of thought is shared in the transcript… Without deep reasoning, you only see the resulting plan — not the reasoning behind it." The full assembled system prompt is deliberately never exposed. [CAT — "Open the Hood", citing Learn billing page for reasoning]

## 2. When to use it / when NOT to use it

**Use generative/new-experience orchestration when:**
- Requests are multi-intent, multi-step, or ambiguous — the planner decomposes and chains tools, topics, knowledge, and agents without authored routing. [OFFICIAL]
- You need automatic slot-filling, disambiguation without "Multiple topics matched" system topics, and cross-source synthesis (e.g., live MCP data + knowledge-base corrections). [OFFICIAL / CAT]
- You want Skills, memory, code execution, deep reasoning, Microsoft IQ grounding — these are exclusive to generative orchestration or the new harness (e.g., computer-use agents require generative orchestration). [OFFICIAL — Learn whats-new]

**Prefer classic/deterministic constructs when:**
- **Exact, approved wording must survive.** Instructions-only attempts to stop summarization were "somewhat inconsistent"; a topic with custom search + AI Prompt + direct `SendActivity` (bypassing the orchestrator's final summarization) was the most consistent. [CAT — "Defeating Oversummarization", 2026-01]
- **Intent control must be tight/regulated**: classic trigger-phrase NLU is "more controlled" than LLM selection. [OFFICIAL — Learn]
- **You depend on unsupported knowledge types**: generative orchestration does not support custom data or Bing Custom Search at agent level (embed in a generative answers node instead). [OFFICIAL — Learn "Knowledge sources summary"]
- **Cost sensitivity**: generative answers (2 credits) vs classic (1); actions 5; Graph grounding 10; reasoning models add a premium meter on top; the CAT chain-of-thought logging trick explicitly "costs more Copilot credits." [OFFICIAL rates from Learn billing page via search; CAT trade-off note] The exact reasoning-meter unit is reported inconsistently across sources ("100 credits per 10 responses" vs "per 10 tokens") — [STATUS UNVERIFIED, verify on Learn "requirements-messages-management"].
- [INFERRED] Latency-critical channels: every planning iteration adds a model round-trip; the CAT silent-failure case shows chained steps can breach channel timeouts (~120 s in Teams, observed not documented).

## 3. Classic-experience comparison (what it replaces or simplifies)

| Dimension | Classic orchestration | Generative orchestration (standard harness) | New-experience orchestrator (GitHub Copilot harness) |
|---|---|---|---|
| Routing | Trigger phrases → single topic | LLM plan over topics/tools/knowledge/agents via names+descriptions | Agentic reasoning loop; default, no toggle [OFFICIAL] |
| Primary authoring unit | Topics + nodes | Topics + tools + instructions | Natural-language **instructions + Skills**; topics absent as primary unit [OFFICIAL/CAT] |
| Situational logic | Topic branches | Instructions (always in context) | Skills loaded on demand (metadata-only by default) [CAT] |
| Missing inputs | Question nodes | Generated questions from descriptions | Same, plus richer reasoning [OFFICIAL] |
| Disambiguation | "Multiple topics matched" system topic | Planner handles it; that system topic unused [OFFICIAL] | Planner/reasoning loop |
| Debugging | Test pane, topic trace | Activity map + plan trace in transcript | Reasoning view; Build/Preview/Evaluate/Monitor surface [OFFICIAL] |

What the new experience **replaces or simplifies** [CAT — Deep Dive deck framing]: "every behavior belongs in the smallest component that makes it reliable and inspectable. Instructions carry what's always true, Knowledge the searchable facts, Tools the system actions, Memory the persistent context, Skills the situational procedures, and connected agents the real specialist domains." Migration from the Standard harness is assisted by the **Copilot Studio plugin** (`/migrate`), which proposes — not guarantees — a new architecture; CAT warns against "turning every topic into a Skill and every variable into memory… that's archaeology with YAML." [CAT — 2026-07-07] Agents/workflows created in the new experience **cannot be converted back** to classic. [OFFICIAL — Learn]

Note also the naming drift: CAT/Learn use "Standard harness" for the pre-existing (classic + generative orchestration) stack and "GitHub Copilot harness" for the new one; one Learn-adjacent source describes three harnesses in total. [STATUS UNVERIFIED on the exact three-harness taxonomy]

## 4. Limitations, GA/preview status, licensing notes

**Status:**
- Generative orchestration: **GA** since March 2025 (en-US). [OFFICIAL]
- Deep reasoning model add-on: **preview**, US + EU (excl. UK), o3. [OFFICIAL]
- New agents experience / GitHub Copilot harness: Learn pages describe a **production-ready preview**, and many agents-experience pages still carry "(preview)" markers; a Microsoft Community Hub announcement (early Aug 2026, per multiple secondary writeups) declares the harness **generally available**. Sources conflict as of 2026-08-19 — treat as *GA announced, docs still partially marked preview*. [STATUS partially UNVERIFIED]
- Model-selection features: separate deep-reasoning / generative-responses model pickers flagged **preview**. [OFFICIAL — Learn]

**Documented limits (only where a source states them):**
- **128 tools max** per agent under generative orchestration; **25–30 recommended** for best results. [OFFICIAL — Learn "Add tools to custom agents"]
- **25 SharePoint site URLs** max per agent with generative orchestration; **>25 knowledge sources** triggers GPT-based description filtering. [OFFICIAL — Learn]
- Transcript record `Content` column: **1 MB**, split via `BatchId`; sessions bound at **30 min inactivity**; transcripts written **~30 min** after inactivity; default retention **30 days**; Analytics CSV truncates bot responses at **512 chars**. [OFFICIAL, via CAT technical reference citing Learn]
- New-experience code runtime: **no `pip install`** — only pre-shipped Python packages (e.g., `pdfplumber` present; `pdf2docx`, `pymupdf` absent), and "the skills available today may change." [CAT — Redlining post]
- Synchronous response timeout **~120 s** with silent failure in Teams — observed behavior + community reports, **not official documentation**. [CAT, explicitly flagged as unofficial]

**Licensing/billing:**
- Currency is **Copilot Credits** (renamed from messages 2025-09-01): classic answer 1, generative answer 2, agent action 5, Graph tenant grounding 10, agent flows 13/100 actions; reasoning adds a premium meter (unit disputed across sources, see §2). M365 Copilot-licensed users' usage in Teams/M365 channels doesn't draw down packs for those answer types. [OFFICIAL — Learn "billing-licensing" / "requirements-messages-management" via search]
- **New-harness twist**: makers consume credits **at design time** (authoring, preview/test pane, evaluations), before any production lifecycle. Harness agents are identifiable via the `isCLIAgent` property in Power Platform Inventory; admins can allocate credits per environment, gate tenant-pool draw and PAYG, and set **agent-level monthly limits** (alert %, stop-at-limit) in PPAC or via the licensing API. [OFFICIAL/CAT — "Adopting the GitHub Copilot Harness: Cost Control and Governance", 2026-08-07]
- Token counts are not exposed in transcripts because billing is credit-based. [CAT/OFFICIAL]

## 5. Security and governance implications

- **The orchestrator's system prompt is intentionally hidden** from transcripts (guardrails/internal logic), so full prompt-level auditability is impossible by design. [CAT/OFFICIAL — "Open the Hood"]
- **Transcripts are PII**: grant the Dataverse **Bot Transcript Viewer** role sparingly, four-eyes for live access; App Insights `Log sensitive Activity properties` toggle controls user IDs/message text; responses grounded in sensitive SharePoint documents are **excluded from transcripts** (audit gap). [OFFICIAL — Learn admin-transcript-controls, via CAT]
- **Descriptions and Skills are an injection surface.** Because names/descriptions/`SKILL.md` content steer the planner, any Skill or component you didn't author "is a trust surface… review it before adding: check for prompt injection, instructions to misuse tools." [CAT — "Agents Have Skills Now"] [INFERRED] The same logic extends to MCP tool descriptions fetched at runtime — they enter the planning context from an external server.
- **Dynamic tool routing can bypass policy**: DLP and connector-action-control policies "do not block URLs that are resolved at runtime by C# scripts" in custom connectors; VNet integration is currently the reliable containment for connector egress. [OFFICIAL note inside CAT — "Dynamic MCP Routing", 2026-03]
- **Orchestrator-driven data movement**: patterns where the orchestrator fills an input variable with the whole conversation history and hands it to an email/Dataverse MCP tool mean sensitive data can flow anywhere a tool reaches — CAT tells builders to treat transcript-in-a-variable as sensitive, minimize, and scope permissions. [CAT — "The Orchestrator's Secrets"]
- **Cost governance is now a security-adjacent control**: unbounded maker experimentation on the new harness burns tenant credits; classify environments (maker dev vs funded production), set default agent limits, monitor via Inventory API/PPAC. [CAT — cost-governance post]

## 6. Performance and maintainability implications

- **Every planning step is latency and credits.** The CAT silent-failure case: 34 s connector call + empty knowledge sources + 62 s catch-all Azure AI Search → ~130 s total → silent Teams timeout; fixed by repointing knowledge, semantic ranking/scoped index, and a graceful-fallback catch-all → ~35 s average. Debug with data (snapshot + MCS Agent Analyser), not by tweaking settings. [CAT — "Open the Hood"]
- **Context economy is the design driver in the new experience**: Skills keep situational guidance out of the default context ("ten Skills cost you ten short descriptions"), which CAT credits with manageability + context-management gains structurally, and accuracy/speed gains *per-case, to be evaluated not assumed*. Accuracy "can degrade as more is loaded into an agent's context" — a growing toolset is part of that load; past a point, split into a connected agent. [CAT — "Agents Have Skills Now"]
- **Tool count discipline**: hard cap 128, recommended 25–30. [OFFICIAL] "An agent shouldn't be one instruction blob with 43 tools and a prayer." [CAT]
- **Codify what the loop discovers**: letting the new orchestrator's agentic loop derive a Python solution took ~15 minutes of fail/rewrite; shipping the generalized script inside the Skill (`scripts/redline.py`) made the same task ~15 seconds — "roughly 60x faster." Pattern: run the loop once, strip hardcoding, ship pseudocode/scripts as Skill resources. [CAT — Redlining post]
- **Observability has cost**: forcing CoT logging after every step burns extra credits — gate it behind debug flags/channels. [CAT]
- **Maintainability = description hygiene + evals**: descriptions are routing metadata, so changing them is a behavioral change; CAT's improvement-loop tooling (author → publish → DeepEval-scored test harness) exists precisely because orchestration behavior must be regression-tested; also isolate test cases in separate conversations to avoid context contamination cascading failures. [CAT — "Closing the Loop", 2026-03-29]

## 7. Architecture guidance and anti-patterns

**Guidance:**
1. **Smallest reliable component rule** [CAT]: always-true behavior → instructions; searchable facts → knowledge; system actions → tools; persistent context → memory; situational procedures → Skills; genuine specialist domains → connected agents.
2. **Write names/descriptions as routing metadata** [CAT/OFFICIAL]: specific names (`HR Leave Eligibility Triage`, not `HR Help`); state when to use **and when not to**; "if two reasonable makers would disagree on when a Skill applies, the description is not specific enough."
3. **Instructions only for ambiguity and cross-source policy** [OFFICIAL/CAT]: let descriptions route the obvious; use instructions for conditional chaining ("MCP for data, then knowledge for corrections, merge"), always with `/` references to exact component names.
4. **Skill vs new agent** [CAT]: same audience + same knowledge/security boundary → Skill; standalone capability, different audience/security boundary, or an overloaded toolset → separate (connected) agent.
5. **Deterministic islands inside a generative sea** [CAT/INFERRED]: when output must be exact (compliance text, calculations), route into a topic/tool that ends with a direct `SendActivity`/"send exact message after running," denying the orchestrator a final rewrite pass; put exact math in code, not the model.
6. **Debug in layers** [CAT]: activity map / reasoning view → test-pane snapshot (`dialog.json` plan trace) → Dataverse transcript → App Insights; use deep-reasoning models when you need the *why* in the transcript, and evaluate orchestration end-to-end (plan chosen + executed), not just answer text.
7. **Design for the loop's failure modes** [CAT/INFERRED]: recursion guards in instructions are best-effort natural language — add condition nodes as hard guards; set timeouts and graceful fallbacks on catch-alls.

**Anti-patterns (all sourced):**
- **Vague descriptions** ("Helps with HR questions") → wrong Skill/tool fires or none at all (missed activation). [CAT]
- **One instruction blob + dozens of tools** — degraded selection accuracy, context saturation. [CAT/OFFICIAL 25–30 guidance]
- **Migration archaeology**: mechanically converting every classic topic to a Skill and every variable to memory. [CAT]
- **Relying on agent-level instructions for verbatim/critical output** — demonstrably inconsistent. [CAT]
- **Assuming the orchestrator will consult a second source unprompted** — without contextual instructions the KPI agent returned uncorrected MCP data even though corrections existed in knowledge. [CAT]
- **Stale knowledge sources left attached** — empty searches silently push the planner into expensive fallbacks. [CAT]
- **Ungoverned maker environments on the new harness** — design-time credit burn with no limits. [CAT]

## 8. Sources

**Local (CAT blog clone, read in full):**
- /workspace/microsoft/mcscatblog/_posts/2026-07-07-new-orchestrator-resources.md
- /workspace/microsoft/mcscatblog/_posts/2025-11-11-influence-orchestration-knowledge.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-19-open-the-hood-copilot-studio-transcripts.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-19-open-the-hood-technical-reference.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-27-dynamic-mcp-routing-copilot-studio.md
- /workspace/microsoft/mcscatblog/_posts/2026-01-23-copilot-studio-defeating-oversummarization.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-13-power-of-topics-copilot-studio.md ("The Orchestrator's Secrets")
- /workspace/microsoft/mcscatblog/_posts/2026-06-15-modern-mcs-agent-skills.md
- /workspace/microsoft/mcscatblog/_posts/2026-08-07-copilot-harness-cost-governance.md
- /workspace/microsoft/mcscatblog/_posts/2025-09-20-copilot-studio-child-connected-agents-inputs-outputs.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-15-redlining-documents-new-copilot-studio-experience.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-29-agentic-improvement-loop.md (grep excerpts)

**Web (via WebSearch synthesis of Microsoft Learn and announcements; learn.microsoft.com not directly fetchable):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-generative-orchestration
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot ; …/authoring-review-activity
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-instructions
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-reasoning-models
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview ; …/agents-experience/skills-overview ; …/agents-experience/authoring-add-other-agents ; …/agents-experience/authoring-select-agent-model
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents ; …/guidance/multi-agent-patterns
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas ; …/billing-licensing ; …/requirements-messages-management
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-gpt-overview
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/whats-new-in-copilot-studio-march-2025/ (generative orchestration GA)
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/more-powerful-agents-and-workflows-for-autonomous-business-processes-introducing/4542969 (harness announcement)
- Secondary corroboration (used cautiously, flagged where relied on): holgerimbery.blog (orchestrator/agents-experience posts), rajeevpentyala.com and aguidetocloud.com (harness explainers), cloudzero.com (credit stacking), microsoft.github.io/mcs-labs (orchestration lab).
