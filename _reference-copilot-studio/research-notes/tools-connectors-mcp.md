# tools-connectors-mcp

Research note, 2026-08-19. Scope: tools in the NEW Copilot Studio agents experience (natural-language-first authoring, agents powered by the GitHub Copilot harness), plus tool infrastructure shared with the standard harness. Tags: [OFFICIAL] = documented Microsoft behavior (Learn/Microsoft blog), [CAT] = Copilot Studio CAT blog guidance, [INFERRED] = analyst reasoning. Status flags noted where learned.

## 1. What it is and how it works

**Tools are the action layer of a Copilot Studio agent.** In the new agents experience, tools are "external capabilities your agent can invoke during a conversation"; the orchestrator selects a tool based on conversation context and the tool's description — no explicit triggers or topic flows are required per tool call [OFFICIAL, Learn agents-experience/tools-overview]. The new experience is a "production-ready preview" as of mid-2026, and its docs are titled "Microsoft Copilot Studio (new experience)" / "(GitHub Copilot)" under the `agents-experience` path [OFFICIAL]. The CAT team frames the component model as: Instructions carry what's always true, Knowledge the searchable facts, Tools the system actions, Memory the persistent context, Skills the situational procedures, and connected agents the specialist domains [CAT, "New Harness, New Rules?"].

**Tool types.** The Learn "Add tools" pages enumerate these tool types [OFFICIAL, Learn add-tools-custom-agent; agents-experience/tools-available]:

- **Connector tools** — actions from prebuilt or custom Power Platform connectors (hundreds of services: SharePoint, Outlook, Salesforce, ServiceNow, SAP…). The maker explicitly adds each action, edits its description, and configures inputs/defaults.
- **REST API tools** — created from an OpenAPI **v2** specification (v3 specs are automatically translated to v2); the maker supplies endpoints, auth details, and descriptions the model uses to decide when to invoke the API. The dedicated Learn page is titled "Extend your agent with tools from a REST API **(preview)**" [OFFICIAL — preview status as of the page title].
- **MCP servers** — connect to a Model Context Protocol server; Copilot Studio discovers the server's tools dynamically at runtime. MCP is **generally available** in Copilot Studio [OFFICIAL, Microsoft Copilot blog "MCP is now generally available"]. Transport is **Streamable HTTP only**; the older SSE transport was deprecated and unsupported after August 2025 [OFFICIAL, Learn mcp-add-existing-server-to-agent + Microsoft blog; corroborated by community write-ups].
- **Custom connectors** — the Power Platform path to wrap an internal API; also the substrate under MCP and A2A connections (see below).
- **Prompts as tools** — AI Builder-style prompts added as tools (Tools tab → New tool → Prompt); prompts can reference knowledge, use input variables, run a code interpreter (generate/execute Python), and can even bring-your-own-model [OFFICIAL, Learn prompts-overview, create-custom-prompt, code-interpreter-for-prompts, bring-your-own-model-prompts].
- **Agent flows / workflows as tools** — deterministic multi-step automations exposed to the agent. In the standard harness these are "agent flows" (need the "When an agent calls the flow" trigger + "Respond to the agent" action, async toggle Off, inside a Solution, running under the Copilot Studio plan) [CAT, "Combining Agent Flows with Agents"]. In the new experience they surface as **workflows**: "Add a workflow to your agent as a tool (preview)"; the redesigned workflows experience (visual designer with explicit AI vs deterministic steps) is in **public preview** as of May 2026 [OFFICIAL, Learn agents-experience/tools-add-workflow; Microsoft blog May 2026].
- **Computer use** — AI-driven UI automation ("clicks buttons, fills forms" on websites and Windows apps) for systems with no API. **Generally available** since ~May 13, 2026 across commercial geographies [OFFICIAL, Microsoft Community Hub GA post]. Runtime options: Microsoft-hosted browser (zero setup, not Entra-joined), **Cloud PC pool** (Windows 365 Cloud PCs, Entra ID-joined and Intune-enrolled — the enterprise-grade option), or bring-your-own-machine [CAT, Cloud PC pool post; OFFICIAL, Learn FAQ]. Computer use requires generative orchestration [OFFICIAL, Learn faqs-computer-use].

**MCP mechanics.** Adding an MCP server via the onboarding wizard creates, under the hood, a **custom connector** in the Power Platform environment whose OpenAPI spec has a single `InvokeServer` action tagged `x-ms-agentic-protocol: mcp-streamable-1.0`; that action is the Streamable HTTP POST carrying JSON-RPC to the server's `/mcp` endpoint for both `tools/list` and `tools/call` [CAT, "Five Minutes to Your First MCP Connector"]. The wizard also creates a **connection reference** (solution-aware pointer) and a **connection** (per-environment, per-user, not in the solution) — standard Power Platform ALM applies [CAT, same post]. MCP protocol surface supported by Copilot Studio: **tools and resources** [CAT, MCP-vs-connectors post, Jan 2026: "Copilot Studio supports only tools and resources today"]. Note a source conflict: the earlier custom-headers post (Oct 2025) parenthetically says MCP connectors provide "tools (and prompts as of recently)", and the Learn page for adding components is titled "Add tools **and resources** from an MCP server" — treat MCP *prompts* support as [STATUS UNVERIFIED]; tools + resources are the safely documented set. Sampling, roots, and elicitation are not supported [CAT].

**MCP resources.** Copilot Studio's orchestrator lists resources **only through tools, never via direct `resources/list` enumeration** — a tool returns either `resource_link` references (which the agent can then fetch via `resources/read`) or embedded resources (content delivered inline) [CAT, "Using MCP Resources in Copilot Studio"]. Resource links need not be pre-registered; URIs can be generated dynamically, which scales to large catalogs (the UI may show only ~5 resources or a limiting error — irrelevant when using `resource_link`) [CAT].

**Inputs/outputs contracts.** Connector-tool inputs can be AI-filled, hardcoded, defaulted, or set with Power Fx/system variables; makers can also edit each tool's description — "instructions without instructions" that steer the orchestrator [CAT, MCP-vs-connectors]. MCP tool schemas and descriptions are fixed by the server owner; makers **cannot override MCP tool descriptions or input configurations** in Copilot Studio today, though individual tools can be toggled off by disabling "Allow all" [CAT + OFFICIAL, Learn mcp-add-components-to-agent]. Agent flows natively support only **Text, Boolean, and Number** input/output parameters — Tables/Records need conversion, and schema drift causes `FlowActionBadRequest` until the tool node is refreshed [OFFICIAL, Learn advanced-flow-input-output; CAT gotchas post]. Custom headers on an MCP connection (server-level context such as tenant/user tier, distinct from per-call tool inputs) require hand-editing the connector's swagger — no UI as of Oct 2025; `X-`-prefixed header names were broken at that time; after a swagger change the tool must be **removed and re-added** in every agent [CAT, custom-headers post — recheck currency of both caveats].

**Authentication modes.** Two credential modes for tools: **end-user credentials** (default for connectors; the agent acts as the user, and users are prompted to sign in/connect) and **maker-provided credentials** [OFFICIAL, Learn advanced-connectors]. For agent flows, the tool-level "Maker-provided credentials" setting only governs the flow invocation — each action inside the flow authenticates via its own **connection reference**, which must be updated separately [CAT, gotchas post]. First-party Entra connectors using end-user auth show a lightweight **consent card** (Allow/Cancel) rather than the connection manager [CAT, consent-card post]. Custom connectors (and thus custom MCP servers) can achieve the same seamless SSO via **OBO (on-behalf-of)** configuration: app registration for the API, app registration for the connector with the **Azure API Connections service as an authorized client**, OAuth settings on the connector, and connector sharing — documented in Learn's "Configure OBO Authentication for custom connectors" [OFFICIAL, advanced-custom-connector-on-behalf-of; CAT, "Seamless SSO with Custom Connectors"]. The MCP wizard offers **None, API key, and OAuth 2.0** auth; OAuth supports **Dynamic Client Registration (DCR)** discovery where the server supports it [OFFICIAL, Learn mcp-add-existing-server-to-agent]. Entra ID does **not** support DCR, so Entra-protected MCP endpoints (e.g., Dataverse MCP cross-environment) require manual app registration, application-user setup, and PPAC "Allowed MCP Client" authorization [CAT, Dataverse-MCP-cross-environments post].

**Limits (documented numbers).** Generative orchestration handles a maximum of **128 tools per agent**; Microsoft recommends **no more than 25–30** for quality [OFFICIAL, Learn add-tools-custom-agent]. Agent-triggered agent flows have a hard **100-second** synchronous response limit (`FlowActionTimedOut`) [CAT + OFFICIAL error-codes reference]. Generative AI request quotas range 10 RPM/200 RPH (trial/dev) to 100 RPM/2,000 RPH (PAYG / M365 Copilot) [OFFICIAL, Learn requirements-quotas].

## 2. When to use it / when NOT to use it

The CAT decision guide splits the choice into two independent decisions [CAT, "MCP Servers or Connectors in Copilot Studio? A Maker's Guide"]:

**Built-in MCP server vs built-in connector (both exist for Dataverse, SharePoint, Outlook, Teams, Dynamics 365):**
- Pick the **MCP server** when: the capability is MCP-only (standout: Microsoft 365 Copilot Search — multi-turn reasoning with M365 Copilot, no connector equivalent); you want automatic tool updates without reconfiguration; you want protocol features like resources; you want a coherent bundled tool package the agent can chain (e.g., Dataverse MCP: `list_tables`, `describe_table`, `read_query`, DDL ops with no connector equivalent).
- Pick the **connector** when: you must control tool descriptions and inputs (orchestration tuning); admins need per-tool DLP/ACP governance; you want a frozen, predictable tool surface.
- **You can use both in one agent** — but watch for overlapping tools confusing the orchestrator [CAT].

**Custom MCP server vs custom connector (internal API, you build it):**
- **Custom MCP server** when: the integration must serve agents on multiple platforms (VS Code, Claude, any MCP client — build once); the logic is "thick" (aggregation of multiple APIs, RAG, vector search, conditional orchestration, non-REST protocols, own LLM calls); you want code-first ALM (git + CI/CD); you want MCP resources for large-payload patterns.
- **Custom connector** when: the integration is a thin API wrapper with no cross-platform need; you don't want to host server infrastructure; the agent builder needs description/input control; you want per-tool admin governance. Custom connectors do support post-call C# scripting for response trimming, but "the constraints are tight" [CAT].

**Other tool types:**
- **REST API tool**: quickest path from an OpenAPI spec without creating a reusable connector; preview — for shared/governed reuse across agents and Power Automate, a custom connector is the more mature vehicle [OFFICIAL status; INFERRED trade-off].
- **Workflows/agent flows as tools**: use for deterministic multi-step business logic, approvals, and transactional sequences the LLM shouldn't improvise. NOT for anything that must block a conversation >100 seconds — human approvals and RFI inherently exceed it; use the async continuation pattern (respond early, run long logic after "Respond to the agent," call back via the Copilot Studio connector's "Execute Agent" action passing `System.Conversation.Id`) [CAT, gotchas post].
- **Prompts as tools**: single-turn model tasks (classification, extraction, structured generation, Python-based analysis) that benefit from a fixed prompt contract rather than free orchestration [OFFICIAL].
- **Computer use**: last-resort integration when no API/connector/MCP exists ("if a human can do it through a UI, Computer Use can too") — data entry, invoice processing on legacy UIs. NOT for anything API-accessible (cost, latency, fragility) and not on classic orchestration [CAT + OFFICIAL FAQ; INFERRED on cost/fragility].
- **NOT via tools at all**: static reference content belongs in Knowledge; repeatable procedures belong in Skills; specialist domains in connected agents [CAT, component model].

## 3. Classic-experience comparison (what it replaces or simplifies)

- **Topic wiring per action → description-driven orchestration.** Classic topic-based authoring required explicit trigger phrases, topic flows, and action nodes per capability. In the new experience the orchestrator picks tools from names/descriptions in context; no per-tool topic scaffolding [OFFICIAL, agents-experience docs]. What replaces the control you lose: tool descriptions, input configuration, and instructions become the steering surface [CAT + OFFICIAL guidance].
- **Chained topic logic → thick tools.** Multi-step logic previously encoded in topics/Power Automate is better placed in workflows, MCP servers, or connector code: "complex orchestration logic belongs in the server or connector, not in agent topics" [CAT, MCP-vs-connectors]. Topics and flows "get unwieldy for sophisticated orchestration" [CAT].
- **Agent flows → workflows.** The new experience re-skins flow authoring as workflows on a visual canvas "with much more control over which steps are handled by AI" (public preview) [CAT "New Harness" + OFFICIAL May 2026 blog]. The 100-second sync wall and Text/Boolean/Number parameter contract carry over from agent flows [CAT; STATUS of these limits under the new workflows experience specifically: UNVERIFIED — verify before relying on relaxation].
- **Manual authentication → "Authenticate with Microsoft" + connector SSO.** Classic guidance often defaulted to manual OAuth config (two app registrations, token exchange URL, not solution-aware). CAT's position: for B2E/Entra scenarios use "Authenticate with Microsoft" (zero config on Teams/M365/SharePoint channels) and custom-connector OBO for downstream APIs; manual auth remains for B2C/non-Entra IdPs. Manual auth exposes `System.User.AccessToken` to makers and supports only **one OAuth resource**; connector SSO supports multiple resources and hides tokens [CAT, "You Probably Don't Need Manual Authentication"].
- **Bot Framework skills → tools/Skills.** Azure Bot Service skills are legacy (supported only for old SDK versions; new development should use the M365 Agents SDK), and the new experience introduces file-based agent "Skills" (SKILL.md) as the reuse unit — a different concept from classic skills [OFFICIAL, Learn tools-skills-legacy/configuration-add-skills; CAT skills gallery].
- **A2A connections** follow the same custom-connector + connection-reference pattern as MCP [CAT, hello-world post].

## 4. Limitations, GA/preview status, licensing notes

**Status ledger (as learned, 2026-08):**
- New agents experience: **production-ready preview** [OFFICIAL].
- MCP in Copilot Studio: **GA** [OFFICIAL, Microsoft blog]; Streamable HTTP required, SSE dead post-Aug 2025 [OFFICIAL].
- REST API tools: **preview** (per Learn page title) [OFFICIAL].
- Workflows (redesigned experience): **public preview** since May 2026 [OFFICIAL]; workflow-as-tool page marked "(preview)" [OFFICIAL].
- Computer use: **GA** (~May 13, 2026, all commercial geos) [OFFICIAL]; a third-party deep-dive reports GA models = OpenAI CUA and Claude Sonnet 4.5 — plausible but not confirmed on Learn here [STATUS UNVERIFIED].
- Agent 365 MCP servers (SharePoint/OneDrive, Outlook Mail/Calendar, Teams, Word, User Profile, Copilot Search, Dataverse, admin servers): require tenant enrollment in the **Frontier program** AND a **full Microsoft 365 Copilot license** for agent users [CAT, A365 post, Nov 2025 — licensing gates may have evolved; recheck].
- MCP prompts support: conflicting signals; tools + resources documented, prompts [STATUS UNVERIFIED].
- Block maker-provided credentials (admin policy): listed in the **2026 release wave 1** plan [OFFICIAL, release-plan page — check current rollout state].

**Hard limits and known constraints:**
- **128 tools max** per agent under generative orchestration; **25–30 recommended** [OFFICIAL].
- **100-second** synchronous limit for agent-flow tools (`FlowActionTimedOut`) [CAT/OFFICIAL].
- Agent flow I/O parameters: **Text, Boolean, Number** only [OFFICIAL].
- REST API tools require OpenAPI **v2** (v3 auto-converted) [OFFICIAL].
- MCP tool descriptions/inputs not maker-editable; per-tool platform governance not available for MCP (see §5) [CAT/OFFICIAL].
- Custom connectors must live **in their own solution** for cross-environment deployment; the MCP wizard puts the connector in the agent's solution, so you must separate it before shipping [OFFICIAL known limitation via CAT hello-world post].
- Swagger edits to MCP connectors (e.g., custom headers) require delete/re-add of the tool per agent; `X-` header prefix broken as of Oct 2025 [CAT — recheck].
- Dataverse MCP built-in tool connects only to the environment selected in-studio; cross-environment needs the custom-connector OAuth bridge [CAT, cross-environments post].
- Token/context limits: oversized tool outputs cause token-limit failures or degraded runs [CAT, resources-as-inputs post].
- Known bug report (Microsoft Q&A): in the new experience on Teams, end-user-credential tools can return the connect/authorize message as tool output instead of data [community signal, not a Learn-documented limitation — treat as field intel].

**Licensing/cost notes:** generative orchestration message quotas vary by billing model (PAYG, M365 Copilot user, prepaid capacity) [OFFICIAL, requirements-quotas]; A365 MCP requires full M365 Copilot licenses [CAT]; computer use consumes Copilot Studio capacity and (for Cloud PC pool) Windows 365-based infrastructure [OFFICIAL/CAT; exact metering not captured here].

## 5. Security and governance implications

- **Shared Power Platform substrate.** MCP servers and connectors alike ride the connector framework: token acquisition/storage/refresh, DLP and Advanced Connector Policies (ACP), Application Insights telemetry for tool executions, and VNet integration (custom MCP servers inherit VNet support because they're backed by custom connectors) [CAT, MCP-vs-connectors "infrastructure you share either way"].
- **Governance granularity gap — the big one.** Admins can block **individual connector actions** in DLP/ACP and set default behavior for newly published actions. **For MCP tools, platform-enforced per-tool control isn't available**: if a server is allowed, its full, dynamically discovered tool surface is allowed. Mitigations: block the whole MCP server as a connector in ACP/DLP; some built-in servers appear as an "action" on their base connector and can be toggled there; some servers (e.g., Outlook Mail) self-enforce DLP per-tool controls, but that's server behavior, not platform guarantee [CAT, citing Learn ACP docs].
- **Dynamic tool drift.** MCP tool surfaces change when the server owner ships changes — agents pick up new tools automatically. That's a supply-chain consideration: a compromised or careless server owner silently changes what your agent can do [CAT fact; INFERRED risk framing]. Disable "Allow all" and pin the tool list where this matters [OFFICIAL toggle].
- **Credential hygiene.** Maker-provided credentials make every user run with the maker's permissions — admins can now (2026 wave 1) force end-user credentials environment-wide, which also breaks autonomous/scheduled agents that had relied on stored maker creds [OFFICIAL, release plan]. End-user credentials align tool results with the user's actual permissions [OFFICIAL]. OBO/SSO for custom connectors keeps tokens inside the connector framework (makers never see them), unlike manual auth's exposed `System.User.AccessToken`; manual auth also locks you to one OAuth resource [CAT].
- **Consent is not misconfiguration.** First-run consent cards for user-credential tools are expected and (currently) unavoidable — one "Allow" click, then remembered [CAT, OBO post]. Headless/custom-UI clients must detect and answer the consent adaptive card themselves or user-credential tools will never run [CAT, consent-card post].
- **HITL callback URLs.** The webhook-action HITL pattern's `notificationUrl` is SAS-signed but unauthenticated — anyone holding it can resume the flow; keep it server-side only [CAT, HITL post].
- **Computer use governance.** Hosted browser is not Entra-joined/Intune-managed — unsuitable for internal systems or production; Cloud PC pool gives identity-joined, policy-enforced, auditable runtimes (admin controls + audit logs) [CAT, Cloud PC pool post].
- **Custom code caveat.** C# scripts in connectors may be restricted by DLP/governance in some orgs — patterns that depend on them (response trimming, dynamic MCP routing) need a gateway/proxy fallback [CAT, dynamic-routing post].

## 6. Performance and maintainability implications

- **Tool count is a quality knob.** 128 is the ceiling; 25–30 is the practical budget — beyond that, tool-selection accuracy and latency degrade [OFFICIAL]. CAT's memorable anti-pattern: "an instruction blob with 43 tools and a prayer" [CAT].
- **Context-window economics.** Every tool output is fed to the LLM. Massive payloads slow runs, degrade reasoning, or fail with token-limit errors. Two mitigations: (1) trim at the connector boundary with C# custom code; (2) MCP-native: tools write large outputs as **resources** and pass **resource IDs** between tools — the orchestrator only pulls content via `resources/read` when reasoning actually requires it. Steer this with explicit instructions ("pass resource IDs between tools; don't expand large resources unless asked") [CAT, resources-as-inputs post].
- **Naming/description discipline.** The planner selects tools mostly on name + description quality; descriptions should be accurate, specific, and can state what NOT to use the tool for; inspect the activity map/plan during testing and refine descriptions before touching instructions [OFFICIAL, Learn generative-orchestration guidance; CAT]. With MCP you don't own descriptions — a reason to prefer connectors when orchestration tuning is needed [CAT].
- **Latency structure.** Agent flows must answer in 100s; Express mode speeds the synchronous portion; long work goes async with a callback [CAT/OFFICIAL]. Computer use is inherently slower/costlier than API calls [INFERRED].
- **Maintainability.** MCP centralizes updates (server ships a fix, all agents inherit it — also all clients on other platforms); connectors freeze the contract per agent (no surprises, but N agents × M tools of description upkeep). Swagger-level changes to MCP connectors currently require re-adding the tool in every consuming agent — a real maintenance tax [CAT]. ALM: connectors live in solutions/pipelines; MCP servers live in git/CI-CD; mixing both means maintaining two lifecycle models for one agent [CAT]. Connection references resolve per environment; connections are never in the solution and must be recreated on import [CAT, hello-world].
- **Connector sprawl** across regions/instances: the catalog + `x-ms-dynamic-values` dropdown + C# URL-rewrite pattern collapses N per-endpoint connectors into one; MCP suits this because tools aren't in the swagger at all [CAT, dynamic-routing post].

## 7. Architecture guidance and anti-patterns

**Guidance:**
1. **Place behavior in the smallest reliable component** (instructions / knowledge / tools / memory / skills / connected agents) — tools are for system actions only [CAT].
2. **Budget tools.** Stay ≤25–30; if you need more, split into connected specialist agents or consolidate related operations behind a thick MCP server/workflow [OFFICIAL limit; CAT/INFERRED remedy].
3. **Choose the integration per the two-decision framework** (§2). Default: built-in connector for tunable, governable actions; built-in MCP for MCP-only capabilities and auto-updating bundles; custom connector for thin wrappers; custom MCP for thick, cross-platform logic [CAT].
4. **Design tool I/O contracts deliberately.** Keep outputs small and semantically dense; return summaries/IDs, not dumps; use MCP resources or connector C# for bulk data; for agent flows convert everything to Text/Boolean/Number at the boundary [CAT/OFFICIAL].
5. **Write orchestration-grade descriptions** — purpose, when to use, when NOT to use; keep names distinct across overlapping tools; validate with the activity map and evals [OFFICIAL guidance; CAT].
6. **Auth by default:** "Authenticate with Microsoft" for B2E; end-user credentials for tools so results respect the user's permissions; OBO custom-connector SSO for custom APIs/MCP; maker credentials only for genuinely shared, non-privileged service actions — and expect admins to be able to ban them [CAT/OFFICIAL].
7. **Human-in-the-loop:** put approvals in workflows (multistage approvals, Request-for-Information, AI Approvals) behind the async continuation pattern; at scale, replace email/Teams-card channels with a custom webhook-action connector (`x-ms-notification-url` + `x-ms-notification-content`, no `x-ms-trigger`) so the flow dehydrates and any UI can resume it [OFFICIAL RFI/AI-approvals blog; CAT HITL post]. Per-tool "require approval before run" settings in the new experience: not confirmed in sources reviewed [STATUS UNVERIFIED].
8. **Plan ALM from day one:** custom connector in its own solution; connection references mapped per environment; document the re-add procedure for MCP swagger changes [CAT/OFFICIAL].

**Anti-patterns:**
- One mega-agent with 40+ tools and instruction spaghetti ("43 tools and a prayer") [CAT].
- Complex orchestration logic in topics instead of the server/connector/workflow layer [CAT].
- Passing raw 100k-token payloads between tools instead of resource IDs [CAT].
- Enabling an MCP server's full surface via "Allow all" when you need only two tools — and assuming per-tool DLP will save you (it won't, for MCP) [CAT/OFFICIAL].
- Maker credentials on write-capable tools in user-facing agents (privilege masquerade; also brittle under the new admin block) [OFFICIAL/INFERRED].
- Manual authentication for Entra B2E scenarios; expecting one manual-auth token to cover multiple resources [CAT].
- Blocking a conversation on an approval inside a synchronous agent-flow tool (guaranteed 100s timeout) [CAT].
- Computer use where an API/connector exists [INFERRED from CAT/OFFICIAL positioning].
- Duplicate MCP server + connector tools for the same operations without disambiguated descriptions — orchestrator confusion [CAT].
- Treating the migration plugin's proposed architecture as final ("archaeology with YAML" — porting every topic to a Skill) [CAT].

## 8. Sources

**Local (CAT blog clone, read in full unless noted):**
- /workspace/microsoft/mcscatblog/_posts/2026-01-29-compare-mcp-servers-pp-connectors.md
- /workspace/microsoft/mcscatblog/_posts/2026-04-10-hello-world-mcp-copilot-studio.md
- /workspace/microsoft/mcscatblog/_posts/2025-10-29-mcp-tools-resources.md
- /workspace/microsoft/mcscatblog/_posts/2025-10-22-mcp-custom-headers.md
- /workspace/microsoft/mcscatblog/_posts/2025-11-25-mcp-resources-as-tool-inputs.md
- /workspace/microsoft/mcscatblog/_posts/2026-05-20-human-in-the-loop-custom-connector.md
- /workspace/microsoft/mcscatblog/_posts/2025-11-18-you-dont-need-manual-auth.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-03-connecting-copilot-studio-dataverse-mcp-endpoint-across-environments.md
- /workspace/microsoft/mcscatblog/_posts/2025-12-05-obo-for-custom-connectors.md
- /workspace/microsoft/mcscatblog/_posts/2025-09-21-connector-consent-card-obo.md
- /workspace/microsoft/mcscatblog/_posts/2026-01-09-cua-cloudpcpool-in-copilotstudio.md
- /workspace/microsoft/mcscatblog/_posts/2026-04-17-combining-agent-flows-and-agents-gotchas-errors-and-patterns.md
- /workspace/microsoft/mcscatblog/_posts/2025-11-19-a365-mcp-servers-copilot-studio.md (first ~120 lines)
- /workspace/microsoft/mcscatblog/_posts/2026-03-27-dynamic-mcp-routing-copilot-studio.md (first ~150 lines)
- /workspace/microsoft/mcscatblog/_posts/2026-07-07-new-orchestrator-resources.md

**Web (Microsoft Learn / Microsoft blogs, via WebSearch synthesis — Learn direct fetch blocked):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/tools-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/tools-available
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/add-tools-custom-agent
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/tools-add-workflow
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/tools-skills-legacy
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-connectors
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/configure-no-maker-authentication
- https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/block-use-maker-provided-credentials-authentication
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-custom-connector-on-behalf-of
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/prompts-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/create-custom-prompt
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/code-interpreter-for-prompts
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/bring-your-own-model-prompts
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-computer-use
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/model-context-protocol-mcp-is-now-generally-available-in-microsoft-copilot-studio/
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/computer-using-agents-in-microsoft-copilot-studio-are-now-generally-available/4519427
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/new-and-improved-computer-using-agents-a-new-workflows-experience-and-real-time-voice-experiences/
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/introducing-request-for-information-in-copilot-studio-agent-flows/
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/more-powerful-agents-and-workflows-for-autonomous-business-processes-introducing/4542969
- https://www.developerscantina.com/p/mcp-copilot-studio-streamable-http/ (community corroboration of SSE deprecation)
- https://learn.microsoft.com/en-ca/answers/questions/5940814/copilot-studio-new-experience-end-user-credential (Microsoft Q&A field report)
