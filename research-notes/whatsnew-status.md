# whatsnew-status

Research note on the current state (August 2026) of the NEW Microsoft Copilot Studio agents experience — the natural-language-first experience powered by the **GitHub Copilot harness** — covering the last ~12 months of platform evolution, GA/preview status, licensing, channels, integration APIs, and the classic-to-new migration story.

**Methodology note.** Evidence tags: **[OFFICIAL]** = documented Microsoft behavior (Learn source markdown read from public MicrosoftDocs GitHub repos, or Learn pages cited verbatim by CAT posts); **[CAT]** = Microsoft Copilot Studio CAT-team blog/mini-site/plugin guidance; **[INFERRED]** = my own reasoning; **[STATUS UNVERIFIED]** = could not confirm. Constraint disclosure: the WebSearch budget for this session was exhausted before any query could run, and learn.microsoft.com / techcommunity.microsoft.com / aka.ms are blocked by the egress proxy. I compensated by reading Learn **source markdown** from public MicrosoftDocs GitHub repos (power-platform, microsoft-365-docs, m365copilot-docs, fabric-docs, SupportArticles-docs — all with 2026 `ms.date` stamps) and two official Microsoft GitHub repos (copilot-studio-plugin, new-copilot-studio-tech-guide). GA/preview labels on the Copilot Studio docset itself (`/microsoft-copilot-studio/agents-experience/*`) could not be read directly because that docset's source repo is private; statuses derived only indirectly are flagged.

## 1. What it is and how it works

**The new agents experience is Copilot Studio rebuilt around an agentic loop.** Copilot Studio agents "can now be powered by the GitHub Copilot harness" — the orchestration stack behind GitHub Copilot's coding agent — announced via the Copilot Studio product blog post "Meet the new Copilot Studio, rebuilt for more complex, multi-step work" (techcommunity, linked from CAT posts; the page itself was unreachable from this sandbox) [CAT, citing OFFICIAL]. Microsoft now describes Copilot Studio as a **multi-harness platform**: "The Power Platform admin center (PPAC) provides a unified capacity management experience across all Copilot Studio harnesses, including **Copilot Chat, Standard, and GitHub Copilot**" [OFFICIAL — MicrosoftDocs/power-platform `manage-copilot-studio-messages-capacity.md`, ms.date 08/03/2026]. The new experience is documented on Learn under `/microsoft-copilot-studio/agents-experience/` (overview, knowledge, skills-overview, tools-overview, memory-overview, preview-overview, authoring-activity-trace, analytics-agent-evaluation-intro, billing-credit-overview, enforcement-policy-credits — all URLs cited by CAT posts) [OFFICIAL, existence of pages; content only as relayed by CAT].

**Component model.** "Every behavior belongs in the smallest component that makes it reliable and inspectable. Instructions carry what's always true, Knowledge the searchable facts, Tools the system actions, Memory the persistent context, Skills the situational procedures, and connected agents the real specialist domains" [CAT — Deep Dive deck summary, July 2026]. In the runtime, "the agent reasons, acts, and adapts in a loop": it decides per turn whether to answer, retrieve knowledge, call a tool, invoke a skill, ask a question, or stop [CAT — tech-guide mini-site and plugin architect spec]. Knowledge sources, tools, and Skills register only their **metadata** in default context; full content is pulled in on demand (instructions are the exception — always fully loaded) [CAT].

- **Build tab / instructions**: authoring happens on a **Build tab** with a right-hand panel for adding components (e.g., "Skills +"), plus a **Preview** tab and an **activity trace** / reasoning view for inspecting what the agent did [CAT, citing agents-experience Learn pages].
- **Skills**: based on the **Agent Skills open format** (agentskills.io, originally from Anthropic). A `SKILL.md` (name, description, instructions) optionally bundled as a `.zip` with `scripts/`, `references/`, `assets/`. Loaded on demand when the description matches; can "soft-point" at the agent's tools without binding to them. Scoped **per agent** as of June 2026, traveling with the agent through solutions/ALM; a cross-agent catalog is "being worked on" [CAT, June 2026]. Community skills exist in the CAT Agent Skills gallery (microsoft.github.io/cat-agent-skills) [CAT].
- **Agent sandbox / code interpreter**: a Copilot Studio-managed **container with a Python runtime, local files, preinstalled libraries, and shell tools**. A CAT inventory on 2026-07-21 found **Python 3.12.9, 99 Python libraries, 11 built-in tools** in an otherwise empty agent [CAT]. **No `pip install`** — what ships in the container is what you get — and **no outbound network egress**; the only paths out are configured Knowledge and Tools [CAT]. Knowledge-retrieved files land in the sandbox so the agent can analyze whole files with code, not just retrieval snippets [CAT]. The sandbox is **temporary** — files must be returned to the user or persisted through a tool [CAT].
- **Memory**: "Agent Memory, when enabled, persists facts and context across conversations. It does not store files" [CAT, citing `agents-experience/memory-overview`]. Enable/disable is a maker choice ("when enabled") [CAT]. GA/preview status: [STATUS UNVERIFIED].
- **Tools / MCP / connectors**: tools include Power Platform connector actions, agent flows (as `WorkflowTool`), and **MCP servers**; the reference sample runs a parent agent calling **4 MCP servers** and chained skills [CAT — BlastBox Omega]. Dataverse ships an MCP server with an environment setting "Allow MCP clients to interact with Dataverse MCP server" (default On; non-Copilot Studio clients like Claude gated behind Advanced Settings) [OFFICIAL — power-platform `settings-features.md`].
- **Connected agents**: parent agents delegate to specialist agents; the FAQ states "we have a cleaner model now with connected agents: less overlap, and most of the role that child agents played can be covered by skills" [CAT — official mini-site FAQ]. A2A-protocol external agents could already be attached as connected agents in Dec 2025 [CAT].
- **Workflows**: the new stack's automation surface — "workflows let you build automated processes on a visual canvas with much more control over which steps are handled by AI"; classic AI **prompts "become inline agents"** inside workflows [CAT — July 2026 post + mini-site FAQ]. Workflows appear as a billed feature row in official billing docs ("Workflows — covered by a Microsoft 365 Copilot license when run inside a standard harness agent by a licensed user; billed in all other cases") [OFFICIAL — `manage-usage-github-copilot-harness.md`, ms.date 08/14/2026].
- **Evaluations**: an **Evaluate tab** plus an **Evaluation REST API** under `api.powerplatform.com` (`.../makerevaluation/testsets/{id}/run`) that lists test sets, triggers runs against **draft or published** agents, and returns per-metric results (general quality, compare meaning, exact match, custom graders). Delegated auth only — no app-only path [CAT, citing `analytics-agent-evaluation-rest-api`]. The agents-experience docset has its own evaluation intro page [OFFICIAL, existence].
- **Microsoft IQ**: officially, "Microsoft IQ [is] a set of capabilities that form the enterprise intelligence layer of the Microsoft stack" comprising **Work IQ** (how employees work — "the intelligence layer behind Microsoft 365 Copilot"), **Fabric IQ** (business entities/data; Fabric *IQ workload* and *ontology* are **preview**), **Foundry IQ** (policies/authoritative documents), and **Web IQ** [OFFICIAL — fabric-docs `iq/overview.md`, ms.date 07/08/2026; m365copilot-docs]. Work IQ enablement **requires a usage-based billing plan set up in Copilot Studio** [OFFICIAL — m365copilot-docs `enable-work-iq.md`, ms.date 06/16/2026]; Dataverse exposes a "Dataverse intelligence (Work IQ) for agents" environment setting (default Off) [OFFICIAL]. How "Microsoft IQ" surfaces *inside* the Copilot Studio new-experience UI (e.g., as a knowledge type): [STATUS UNVERIFIED].

**What's new, ~12-month timeline** (CAT blog corpus unless noted): Sep–Dec 2025 — connected/child agents with typed inputs/outputs, MCP tools+resources and custom headers, A2A multi-agent support, Azure AI Foundry agent connections, live-agent handover. Jan–Mar 2026 — Computer Use with Cloud PC pools (Windows 365 for Agents, **preview** [OFFICIAL — pay-as-you-go meters]), adaptive-card generation, terminal-first authoring plugin ("Skills for Copilot Studio", Mar 10), Evaluation REST API ("recently shipped" as of Apr 2026 [CAT]), native mobile Agents Client SDK (**preview**, no-auth only, Mar 2026 [CAT]), API decision guide (Mar 2). Apr 2026 — standalone prepaid Copilot Credits without Azure (rollout began **April 20, 2026**, MC1279072) with **Copilot Credit Policies** scoped to Entra ID groups [CAT, citing Message Center]; "enhanced task completion" orchestration flagged **experimental** [CAT]; declarative agents authored from Copilot Studio listed in **release plan 2026 wave 1** as upcoming [CAT, citing release plan]. Jun 2026 — GitHub Copilot harness arrives in Copilot Studio with the Skills tab [CAT]; end of June: the Copilot Studio for Teams app stops creating classic bots and redirects to the web app [CAT]. Jul 2026 — CAT ships the Deep Dive deck, BlastBox Omega mini-site/sample, the **copilot-studio-plugin** with `/migrate`, and the CAT Agent Skills gallery; sandbox and redlining deep dives. Aug 2026 — official admin docs for harness cost governance (ms.date 08/14/2026) and the multi-harness capacity statement (08/03/2026) [OFFICIAL].

## 2. When to use it / when NOT to use it

**Use the new experience when** the job is genuinely agentic: multi-step reasoning, delegation to specialists, real actions with generated deliverables. The reference scenarios are exactly that — identity-gated card reissue with a generated file; a multi-agent trade-up settling warranty + stock + prorated refund + loyalty points into a PDF [CAT]. Use it when you need **exact computation or file manufacturing** (sandbox code beats LLM arithmetic/file-emission) [CAT], when procedures are situational (Skills), or when one agent would otherwise fragment into many micro-agents ("often those are not three agents, they are one IT support agent with three Skills") [CAT].

**Do NOT use it / hold off when:**
- **A working standard-harness agent is in production.** Official FAQ: "If it does the job, don't rush into an upgrade… upgrade when there's a clear reason to" [CAT — official mini-site FAQ].
- **The task is simple conversational Q&A** without complex task handling — a declarative agent in Agent Builder (or, upcoming, from Copilot Studio) may fit better and rides the M365 Copilot orchestrator [CAT — FAQ + Apr 2026 post].
- **You want AI-flavored automation, not conversation** — "you probably want a workflow with AI nodes" instead of an agent [CAT — FAQ].
- **Cost predictability during build matters and governance isn't in place**: harness agents consume Copilot Credits **while being built, previewed and evaluated**, with no M365 Copilot license offset [OFFICIAL]. Ungoverned maker exploration is a real spend risk [CAT].
- **One-off document work with no surrounding business process** — CAT explicitly points such jobs at Microsoft 365 Cowork instead; Copilot Studio "pulls ahead" when there's a fixed template, routing, rules, i.e., a repeatable pipeline [CAT].
- **You need deterministic dialog control** (exact scripted flows, PowerFX, variables) — the new model deliberately has none of these (see §3); if the requirement is truly deterministic end-to-end, classic topics or workflows are the fit [CAT/INFERRED].

## 3. Classic-experience comparison (what it replaces or simplifies)

The orchestration lineage: **classic orchestration** (NLU, trigger phrases, topic trees) → **generative orchestration** ("mainline"/Standard harness — LLM routes across topics, knowledge, tools) → **GitHub Copilot harness** (agentic loop) [CAT, Apr 2026 + Jul 2026]. Concrete mappings from the official FAQ and the migration plugin's architect spec:

| Classic/standard concept | New-experience answer |
|---|---|
| Topics (conversational flows) | **Not coming back** ("Not likely"). Conversational logic → instructions and/or Skills; data-transforming topics → sandbox code execution or workflows [CAT — FAQ]. "There are no deterministic topics" [CAT — plugin architect spec]. |
| AI Prompts | "No longer the unit of work." In workflows → inline agents; in agents → usually a Skill [CAT — FAQ]. Not auto-converted by the migration tooling [CAT]. |
| PowerFX | "There is no concept of PowerFX" — replace per intent with a skill, tool, instruction, or embedded Python [CAT — plugin spec]. |
| Global/topic variables | "NOT supported… no concept of a variable set and retrieved across steps"; the loop reasons over conversation history and tool outputs; Memory covers persistent context [CAT — plugin spec]. |
| Child agents | Superseded by **connected agents** (real specialist domains) and, for most cases, **Skills** [CAT — FAQ]. |
| Adaptive cards / rich UI | "Rich UI component options in agents are still being actively worked on" [CAT — FAQ]. [STATUS UNVERIFIED what ships today]. |
| Actions (connectors, flows) | Become **Tools** (`ConnectorTool`, MCP tools, `WorkflowTool`) [CAT — plugin]. |
| Manual authoring canvas | Natural-language Build tab + YAML-under-the-hood (`agent.mcs.yml`, `settings.mcs.yml`, `capabilities/knowledge|tools`, `behaviors/` InlineAgentSkill, `infrastructure/connections`) manageable via pac CLI ≥ 2.9.3 and AI coding agents [CAT — plugin repo]. |

What it *simplifies*: no separate service for calculations/file generation (sandbox), no topic sprawl for situational procedures (Skills), no bespoke multi-bot plumbing (connected agents), evaluation built in. Classic entitlements persist in parallel: E3/E5's bundled "Copilot Studio for Microsoft Teams" plan still allows **classic-only** agents in Dataverse-for-Teams environments (no generative orchestration, no credits consumed in Teams), now more visible since the June 2026 web-app redirect [CAT, citing Learn licensing FAQ].

## 4. Limitations, GA/preview status, licensing notes

**Status board (as of 2026-08-19):**
- New agents experience / GitHub Copilot harness overall: shipped and documented as one of three harnesses [OFFICIAL]; formal GA-vs-preview label [STATUS UNVERIFIED]. Strong signal it is still exiting a preview billing phase: "Prepare for the end of preview billing — Developer environments and trial environments move to usage-based billing **September 1, 2026**" [OFFICIAL, ms.date 08/14/2026]. [INFERRED] the experience was in (production-ready) preview with non-billed dev/trial usage through mid-2026.
- Skills: available (Skills tab, blank or upload; full open-format bundle shape) [CAT]; "early in Copilot Studio, and intentionally focused"; per-agent distribution only [CAT]. Label [STATUS UNVERIFIED].
- Sandbox/code interpreter, Memory, Preview tab, activity trace, evaluations (agents-experience variants): documented Learn pages exist [OFFICIAL existence]; labels [STATUS UNVERIFIED]. Memory is opt-in ("when enabled") [CAT].
- Workflows: in-market and billed [OFFICIAL billing table]; label [STATUS UNVERIFIED].
- MCP in Copilot Studio: mature through 2025-2026 CAT coverage (tools, resources, headers, Dataverse MCP) [CAT/OFFICIAL]; connected agents incl. A2A: shipped [CAT]; labels [STATUS UNVERIFIED].
- Enhanced task completion: **experimental** (Apr 2026) [CAT]. Computer Use Cloud PC pool / Windows 365 for Agents: **preview** [OFFICIAL]. Native mobile Agents Client SDK: **preview**, No-Authentication only (Mar 2026) [CAT]. Fabric IQ workload & ontology: **preview** [OFFICIAL]. Declarative agents authored from Copilot Studio: release-plan 2026w1 item, "upcoming" [CAT]. Rich UI/adaptive cards in new experience: in progress [CAT]. Migration plugin: **experimental research project, not officially supported, not for production** [OFFICIAL repo disclaimer].

**Licensing / credit model:**
- Unit of consumption: **Copilot Credits** (superseding "messages"; admin APIs still use currency type `MCSMessages`) [OFFICIAL].
- Pay-as-you-go: **$0.01 per credit**, billed to a linked Azure subscription; per-credit cost varies with task complexity [OFFICIAL — power-platform `pay-as-you-go-meters.md`]. Only production and sandbox environments support pay-as-you-go [OFFICIAL — support article, ms.date 07/17/2026].
- Prepaid: **capacity packs of 25,000 credits/month** (tenant-level, allocated to environments) [OFFICIAL]; **Copilot Credits Pre-Purchase Plan (P3)** via Azure [OFFICIAL]. Since **April 20, 2026**, prepaid packs work **without** pay-as-you-go/Azure, with **Copilot Credit Policies** for Entra-group allocation and hard-stop overage ("usage stops when prepaid capacity runs out") [CAT, citing MC1279072 + Learn].
- License coverage matrix [OFFICIAL — harness cost doc]: **Standard harness agents** — covered by a Microsoft 365 Copilot license in Microsoft 365 channels; billed otherwise. **Workflows / Prompts** — covered when run inside a standard-harness agent by a licensed user; billed otherwise. **Computer use** — always billed. **GitHub Copilot harness agents — always billed, including creation/design-time, regardless of license.**
- End users need **no** M365 Copilot license to use agents in M365 Copilot Chat — Copilot Chat + credits suffices [CAT].
- Prepaid credits are a **shared pool** across PPAC-managed Copilot Studio and M365 usage-based experiences (Copilot Chat agents, SharePoint agents, **Cowork**, **Work IQ**) — coordinate across both admin centers [OFFICIAL].
- Controls: environment allocation with enforcement rules (Alert / TenantPool / PayGo / Deny), **agent-level monthly limits** with notify threshold and stop-usage, programmatic management via Power Platform Licensing APIs, `properties.isCLIAgent` inventory flag to find harness agents [OFFICIAL]. Costs are **not attributable to individual users** — environment/agent level only [OFFICIAL].
- Rate limits: per-Dataverse-environment generative AI quotas; enforcement errors documented; rate-limit increases only for pay-as-you-go environments [OFFICIAL — support article].

## 5. Security and governance implications

- **Sandbox containment is the headline control**: no network egress from executed code — `requests` is installed but can't reach anything; all external reach flows through configured Knowledge/Tools, which stay inside DLP and connector governance [CAT, citing admin-data-loss-prevention]. [INFERRED] this makes tool/connector policy, not code review, the effective perimeter for harness agents.
- **Skills are a trust surface**: they steer behavior and can bundle executable scripts. CAT explicitly: treat third-party/AI-generated skills as untrusted code; review for prompt injection and tool misuse before adding [CAT].
- **Design-time consumption is a governance event**: makers can burn credits before anything is published; classify environments (maker dev vs funded production), apply default agent limits, and automate detection of new `isCLIAgent` agents [CAT + OFFICIAL]. Watch the tenant setting that lets environment admins allocate credits — it grants allocation power across **all** environments [CAT].
- **Enforcement cuts both ways**: Deny/stop rules prevent surprise spend but can take a production agent offline ("This agent is currently unavailable. It has reached its usage limit") [OFFICIAL]; alerts go to tenant/environment admins, not owners, so define an ownership/escalation path [CAT].
- **Existing Power Platform governance still applies**: Managed Environments, environment groups, DLP, solutions/ALM carry skills and agents [CAT/OFFICIAL]. Transcript access and Viva Insights sharing are tenant-settable [OFFICIAL]. Classic-agent sprawl from E3/E5 is controlled by disabling the `Power Virtual Agents for Office 365` service plan [CAT, citing Learn FAQ].
- **Auth boundaries in integration**: M365 Agents SDK client requires delegated Entra auth (no app-only/service-principal yet — on roadmap); native mobile SDK is no-auth-only in preview; hosted web embed cannot do SSO [CAT]. Evaluation API likewise delegated-only [CAT].
- **Work IQ** keeps reasoning inside the M365 trust boundary — requests run as the signed-in user, honoring permissions and sensitivity labels [OFFICIAL].

## 6. Performance and maintainability implications

- **On-demand loading is the core scaling mechanism**: ten Skills cost ten short descriptions per turn, not ten instruction sets; accuracy and latency benefits are "use-case dependent… evaluate rather than assume" [CAT].
- **Codify discovered procedures**: letting the loop derive code each run is slow (redlining case: ~15 minutes of fail/rewrite); freezing the generalized script into a Skill made the same output run in ~15 seconds — "roughly 60x faster" [CAT]. Pattern: no-code first → let it loop → strip hardcoding → ship pseudocode/scripts in the Skill.
- **Skill descriptions are routing metadata**: too broad fires wrongly, too narrow never fires; the reasoning view/activity trace is the debugging surface [CAT].
- **Context saturation degrades accuracy**: past some tool/skill count, split into connected agents rather than piling on ("An agent shouldn't be one instruction blob with 43 tools and a prayer") [CAT].
- **Statelessness matters**: sandbox files don't persist across conversations; Memory persists facts, not files [CAT]. No variables — design around conversation history, tool outputs, and Memory [CAT].
- **Maintainability = evals in CI**: the Evaluation API runs against **draft** agents, enabling PR-gated pipelines (EvalGateADO sample with Dataverse git integration); re-run evals after every instruction/model/knowledge change and after any migration [CAT]. The sandbox's installed library set "may change in the future" — the agent-harness-explorer Skill snapshots it for drift comparison (Memory-assisted) [CAT].
- **Channel behavior differs per channel** (e.g., M365 Copilot: no Conversation Start, no GIFs, no `Action.Execute`, no live-agent handoff) — "Don't assume that because your agent evaluates well in one, it'll behave the same in the other. Test in both" [CAT].

## 7. Architecture guidance and anti-patterns

**Guidance (largely CAT, converging with official FAQ):**
- **Smallest-reliable-component rule**: instructions = always true; knowledge = searchable/citable facts; tools = actions, live data, deterministic compute; Skills = situational multi-step know-how; Memory = persistent context; connected agents = standalone specialist domains with their own audience/security boundary [CAT].
- Two-question placement test: can the agent infer it from tool/knowledge descriptions? If yes, write nothing. If no: always true → instructions; situational → Skill [CAT].
- Knowledge vs skill+tool: RAG-searchable corpus → knowledge; a procedure file the agent should *execute against* → skill + "Get a File" tool [CAT — plugin architect spec].
- Deterministic/exact work → sandbox code or a packaged script, never model arithmetic; repeatable file outputs → reviewed script in a Skill; novel analysis → let the model write code [CAT].
- Channel/integration decision path (custom agents): Teams/M365 publish (no code) → Microsoft-hosted web embed (no code, no SSO) → self-hosted WebChat (M365 Agents SDK for B2E SSO + streaming + Tenant Graph Grounding; Direct Line for B2C/non-Entra) → BYO UI → server-side connector (SDK for delegated Entra; Direct Line-over-HTTP for anonymous) [CAT — decision guide]. Note the March 2026 guide predates the harness; per-channel support of harness agents is [STATUS UNVERIFIED].
- Migration: use the plugin's `/mcs-assistant:migrate` for a **capability-led** redesign — "capabilities and outcomes, not components one for one" — with a mandatory human-approved migration plan, then evals against core journeys [CAT].

**Anti-patterns (named by CAT/official material):**
- "Archaeology with YAML": mechanically turning every topic into a Skill and every variable into memory during migration [CAT].
- One instruction blob + dozens of tools instead of structured components [CAT].
- A new agent per task when one agent + Skills serves the same audience/knowledge boundary [CAT].
- Vague skill descriptions ("Helps with HR questions") that break routing [CAT].
- Relying on sandbox files across conversations, or on Memory as file storage [CAT].
- Converting document formats when a byte-perfect template exists (redlining lesson: never DOCX→PDF→DOCX) [CAT].
- Trusting migration output without review/evals; using the experimental plugin as a production dependency [OFFICIAL disclaimer + CAT].
- Leaving maker-dev environments on tenant-pool draw with no agent limits — unbounded design-time spend [CAT/OFFICIAL].
- [INFERRED] Assuming standard-harness channel/licensing behavior transfers to harness agents — the license-coverage and billing rules are explicitly different.

## 8. Sources

**Local CAT blog posts (read in full):**
- /workspace/microsoft/mcscatblog/_posts/2026-04-17-no-copilot-license-m365-channel.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-02-copilot-studio-api-decision-guide.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-14-migration-plugin-video-demo.md
- /workspace/microsoft/mcscatblog/_posts/2025-12-05-subscribe-rss-feed.md (unpublished stub; no substantive content)
- /workspace/microsoft/mcscatblog/_posts/2026-07-07-new-orchestrator-resources.md
- /workspace/microsoft/mcscatblog/_posts/2026-06-15-modern-mcs-agent-skills.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-15-redlining-documents-new-copilot-studio-experience.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-20-copilot-studio-agent-sandbox.md
- /workspace/microsoft/mcscatblog/_posts/2026-08-07-copilot-harness-cost-governance.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-09-e3-users-build-agents-turn-it-off.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-10-skills-for-copilot-studio.md (partial)
- /workspace/microsoft/mcscatblog/_posts/2026-04-19-copilot-studio-eval-gate-azure-devops.md (partial)
- /workspace/microsoft/mcscatblog/_posts/2026-03-26-claude-copilot-skills-copilot-studio-plugin-demo.md (partial)
- Grep excerpts: 2025-12-02-copilot-studio-a2a-multi-agents.md, 2026-01-09-cua-cloudpcpool-in-copilotstudio.md, 2026-04-30-tool-inputs-sharepoint-list.md

**Official Microsoft Learn source markdown (public MicrosoftDocs GitHub repos, fetched via raw.githubusercontent.com):**
- https://raw.githubusercontent.com/MicrosoftDocs/power-platform/main/power-platform/admin/manage-usage-github-copilot-harness.md (ms.date 08/14/2026)
- https://raw.githubusercontent.com/MicrosoftDocs/power-platform/main/power-platform/admin/manage-copilot-studio-messages-capacity.md (ms.date 08/03/2026)
- https://raw.githubusercontent.com/MicrosoftDocs/power-platform/main/power-platform/admin/pay-as-you-go-meters.md
- https://raw.githubusercontent.com/MicrosoftDocs/power-platform/main/power-platform/admin/settings-features.md
- https://raw.githubusercontent.com/MicrosoftDocs/microsoft-365-docs/public/copilot/pay-as-you-go/copilot-capacity-packs.md (ms.date 10/20/2025)
- https://raw.githubusercontent.com/MicrosoftDocs/m365copilot-docs/main/docs/work-iq/enable-work-iq.md (ms.date 06/16/2026)
- https://raw.githubusercontent.com/MicrosoftDocs/m365copilot-docs/main/docs/planning-guide.md
- https://raw.githubusercontent.com/MicrosoftDocs/fabric-docs/main/docs/iq/overview.md (ms.date 07/08/2026)
- https://raw.githubusercontent.com/MicrosoftDocs/SupportArticles-docs/main/support/power-platform/copilot-studio/licensing/throttling-errors-agents.md (ms.date 07/17/2026)

**Official Microsoft GitHub repos (cloned/fetched):**
- https://github.com/microsoft/copilot-studio-plugin (README.md, commands/migrate.md, agents/copilot-studio-architect.md)
- https://github.com/microsoft/new-copilot-studio-tech-guide (src/pages/index.astro, src/pages/faq.astro — source of aka.ms/MCSTechGuide)

**Learn URLs cited via the above sources (existence/content relayed; direct fetch blocked):** /microsoft-copilot-studio/agents-experience/{overview, knowledge-copilot-studio, skills-overview, skills-add-existing, tools-overview, memory-overview, preview-overview, authoring-activity-trace, analytics-agent-evaluation-intro, billing-credit-overview, enforcement-policy-credits}; /microsoft-copilot-studio/{billing-licensing, requirements-messages-management, requirements-licensing-subscriptions, requirements-quotas, analytics-agent-evaluation-rest-api}; /power-platform/release-plan/2026wave1/microsoft-copilot-studio/create-agents-optimized-365-365-copilot-users; techcommunity announcement "Meet the new Copilot Studio, rebuilt for more complex, multi-step work" (id 4526488); MC1279072 (Message Center).

**Access failures (for transparency):** WebSearch budget exhausted (0 queries possible); EGRESS_BLOCKED on learn.microsoft.com, techcommunity.microsoft.com, aka.ms, microsoft.github.io, mc.merill.net.
