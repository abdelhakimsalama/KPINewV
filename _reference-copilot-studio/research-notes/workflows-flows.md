# workflows-flows

Research note — Workflows in the new Copilot Studio agents experience, and agent flows. Compiled 2026-08-19. Claims tagged [OFFICIAL] (documented Microsoft behavior), [CAT] (Copilot Studio CAT blog guidance), [INFERRED] (reasoning from the above), [STATUS UNVERIFIED] where confirmation failed.

## 1. What it is and how it works

**Context: the multi-harness platform.** Copilot Studio is now a multi-harness platform: the GitHub Copilot harness (the "new experience" / agents experience), the Standard harness (classic), and the Copilot Chat harness. The GitHub Copilot harness became generally available on **2026-08-03** (Message Center MC1446644); before that it ran as public preview under the "new Copilot Studio experience" label [OFFICIAL — MC1446644 relays + Microsoft Community Hub blog "More powerful agents and workflows for autonomous business processes"]. The new stack is "a new paradigm for agents and workflows: agents are far more adaptive and sophisticated, and workflows let you build automated processes on a visual canvas with much more control over which steps are handled by AI" [CAT — new-orchestrator-resources post].

**Workflows** are the new experience's deterministic automation primitive. Per Microsoft Learn ("Workflows overview", `workflows-experience/flows-overview`): workflows automate repetitive tasks and integrate apps/services; they can be triggered manually, on a schedule, by external events, or by agents; and they are **deterministic — they execute actions following a rule-based path where the same input always produces the same output** [OFFICIAL]. The workflows experience is described as "a new, agentic-led way to build automation in Copilot Studio with a redesigned visual canvas, native AI actions, agent handoffs, and node-level testing" [OFFICIAL — Learn workflows overview / May 2026 Copilot Studio blog]. Naming note: workflows are the new-experience evolution of **agent flows** — the classic-experience Learn page is titled "Agent flows and workflows overview" and community coverage describes workflows as replacing "what were previously called agent flows and Power Automate cloud flows in the context of agents" [OFFICIAL for coexistence of the two names; the "replaces" framing is community/blog, not verbatim Learn]. Much of the underlying machinery (triggers, "Respond to the agent", solution/Dataverse storage, Copilot Credits billing) is shared between agent flows and workflows [INFERRED from the paired Learn doc sets].

**The workflows designer.** Design, edit, and automation happen directly in Copilot Studio on a unified visual canvas, with AI-driven suggestions for triggers, actions, and steps; you can also build a flow by describing it in natural language (Learn: "Build an agent flow with natural language", `flow-nl`) [OFFICIAL]. Designer behaviors documented on the Learn `workflows-experience/flow-designer` page: errors on actions are indicated in red; a "health center" banner lists all errors in the workflow; **a workflow with errors cannot be published**; the Activity tab shows run history with status and duration per run [OFFICIAL]. **Node-level testing**: a Play button on individual nodes runs a single action without executing the preceding steps, and testing AI prompt nodes shows output **without consuming credits** during testing [OFFICIAL — May 2026 What's-new blog + Learn designer page]. Community coverage adds drag-and-drop composition and a "variation view & versioning" for comparing variations of a workflow [STATUS UNVERIFIED — third-party writeups only]. Native **AI actions** (classification, content generation, decision support) can be embedded directly as workflow steps [OFFICIAL — April 2026 What's-new blog].

**Exposing workflows as tools to agents.** Learn page "Add a workflow to your agent as a tool (preview)" (`agents-experience/tools-add-workflow`, also `workflows-experience/flow-agent`) [OFFICIAL]:
- The workflow must have the **"When an agent calls the flow" trigger** and a **"Respond to the agent" action**, be configured to respond in real time (**not asynchronously**), be **published**, and respond within the **100-second action limit**.
- Add it via Agent > **Tools** > **Add a tool** > filter to **Workflows**. The Details tab shows the workflow's name, description, input parameters and output parameters. Under **Inputs** you choose how the agent fills each input (dynamically with AI vs. custom value); under **Completion** you choose what the agent does after the tool finishes.
- Test in the **Preview** tab and inspect the **activity trace** to verify which tool was invoked, the arguments passed, and what was returned.

**The reverse direction — agent nodes inside workflows.** A workflow can call an agent mid-sequence via an **agent node** (Learn: `workflows-experience/agent-node-workflow`, classic `agent-node-workflow`): add an "Add an agent" step, pick the agent, provide instructions/context from earlier steps; the workflow pauses, the agent reasons and returns a structured output, and the workflow continues [OFFICIAL + CAT]. CAT frames this as the way to inject AI reasoning into one step while "the agent flow stays fully in charge," preserving determinism everywhere else [CAT — gotchas post #7]. This is the control-flow inverse of workflow-as-tool [CAT].

**Passing files and data.** Agent-flow inputs/outputs natively support only **Text, Boolean, and Number** (Learn `advanced-flow-input-output`); Tables, Records, and complex objects need conversion [OFFICIAL, quoted by CAT]. A **File** input type exists for flows; passing files from an agent to a flow requires Copilot Studio version **2025.7.2 or higher** [CAT — passing-files post]. The pattern: capture the file with a Question node (entity = File, "Include file metadata" checked) or via `First(System.Activity.Attachments)`, then pass it with Power Fx as `{ contentBytes: Topic.userReceipt.Content, name: Topic.userReceipt.Name }`; some connector actions need `base64ToBinary()` for binary content; on the Tools page, file inputs only work via the **"Custom value"** Power Fx option, not "Dynamically fill with AI" [CAT]. An agent can receive at most **1 MB of data from a flow in a single action** [OFFICIAL — advanced-flow-input-output, surfaced via search]. Note the passing-files post describes the classic/topic surface; the Power Fx and type constraints carry into new-experience tool configuration via custom values [INFERRED].

## 2. When to use it / when NOT to use it

**Use a workflow when** ([OFFICIAL] Learn guidance, echoed by the "Automate business processes with agents plus workflows" Microsoft blog):
- The process is a **repeated, deterministic, multi-step procedure** the agent should run on demand — approvals, data transformations, multi-system business logic — where the same input must always produce the same output.
- The automation should run **trigger-to-completion with no user present** (schedule, external event, manual run).
- You need **consistency, auditability, and predictability** — compliance-relevant sequences, transactional side effects.

**Let the agent reason when** [OFFICIAL — same sources]: the system must hold a conversation, interpret unstructured input, or make independent, goal-driven choices beyond fixed logic. Agents bring reasoning and adaptability; workflows bring structure and consistency.

**Combine them** — the explicitly recommended pattern [OFFICIAL blog + CAT]: an agent calls a workflow when it needs a reliable sequence of actions; a workflow defers one step to an agent node when that step needs interpretation. CAT's rule of thumb: "keep the automation deterministic everywhere it can be" and hand only the genuinely ambiguous step to AI [CAT — gotchas post #7].

**Do NOT use a synchronous workflow tool for**:
- **Human approvals / human-in-the-loop invoked from a live chat**: multistage approvals and "request information" steps by definition exceed the 100-second synchronous window, so they cannot run inside a synchronous conversational tool call; restructure with the async continuation pattern (section 7) or keep them to autonomous scenarios [CAT — gotchas post #2].
- **A single connector call**: if the "process" is one action, a plain connector tool (or MCP tool) is simpler than wrapping it in a workflow [INFERRED].
- **Logic that genuinely needs judgment on most steps** — forcing it into rule-based branches produces brittle automations; that is what agent instructions are for [INFERRED from the official agents-vs-workflows guidance].

## 3. Classic-experience comparison (what it replaces or simplifies)

- **Attachment point**: classic agent flows are wired into **topics** as Action nodes (and later as tools); the tool's schema is refreshed manually via the Action node's "..." > Refresh [CAT — gotchas #3]. In the new experience, workflows attach at the **agent level as tools**, and the orchestrator decides invocation from the tool's name/description, with per-input fill strategy (AI vs. custom value) and per-tool completion behavior [OFFICIAL — tools-add-workflow].
- **Designer**: classic agent flows use the embedded Power-Automate-style "classic visual designer" in Copilot Studio [OFFICIAL — flow-designer classic page]; the new experience adds the redesigned canvas with native AI actions, agent nodes/handoffs, node-level testing (no need to run the whole flow to debug), and NL-first authoring [OFFICIAL].
- **What it replaces**: in the agent context, workflows subsume the roles of both classic agent flows and Power Automate cloud flows called from bots [community framing; STATUS partially UNVERIFIED as an official statement]. The new experience drops classic **topic decision trees** as the structured-logic surface; deterministic logic now lives in workflows instead [community reporting; STATUS UNVERIFIED on Learn].
- **One-way door**: agents and workflows created in the new experience **cannot be converted to the classic experience** [OFFICIAL — Learn, surfaced via search]. Separately, converting a Power Automate cloud flow into an agent flow is **permanent** — no conversion back [OFFICIAL — flows-faqs].
- **What carries over**: the "When an agent calls the flow" trigger + "Respond to the agent" action contract, the 100-second synchronous limit, solution packaging, and Dataverse-recorded version history are common to classic agent flows and new-experience workflows [OFFICIAL for each item; the continuity claim itself INFERRED from the mirrored doc sets].

## 4. Limitations, GA/preview status, licensing notes

**Status** (as of 2026-08-19):
- GitHub Copilot harness (new agents experience): **GA on 2026-08-03** [OFFICIAL — MC1446644 relays].
- Workflows experience: Learn's "Workflows overview" page carried a **(preview)** label and the May 2026 What's-new blog announced the redesigned workflows experience as **public preview, rolling out first to early release environments** [OFFICIAL]. "Add a workflow to your agent as a tool" is still titled **(preview)** on Learn as of this research [OFFICIAL]. Some community coverage reports the workflow designer reached GA on 2026-08-03 together with the harness; other mid-2026 community sources still said "not GA, avoid for production." **Sources conflict — treat workflow-as-tool and parts of the designer as preview or freshly-GA; verify per-page banners before committing production designs** [STATUS UNVERIFIED].
- Express mode for agent flows: **preview** [OFFICIAL — agent-flow-express-mode].

**Hard limits (documented numbers only)**:
- **100-second** synchronous response limit for a flow/workflow invoked as an agent tool; exceeding it raises `FlowActionTimedOut` [OFFICIAL — tools-add-workflow prerequisites; CAT gotchas #2; error-codes reference].
- **1 MB** maximum data returned from a flow to the agent in a single action [OFFICIAL — advanced-flow-input-output].
- Native input/output types: **Text, Boolean, Number** (plus File inputs); complex types need conversion [OFFICIAL — advanced-flow-input-output; CAT].
- Express mode targets flows with **fewer than 100 actions** and small payloads, "logic-heavy but data-light", and "increases the likelihood that agent flows can complete within the two-minute window" [OFFICIAL — agent-flow-express-mode]. (Note: Learn's express-mode page speaks of a two-minute window while the tool contract enforces 100 seconds for the synchronous response; the CAT post treats 100 seconds as the operative hard limit for tool calls — flagging the discrepancy rather than resolving it.)
- File passing from agent to flow requires Copilot Studio version **2025.7.2+** [CAT — passing-files].

**Licensing / billing**:
- **Agent flows are licensed by Copilot Credit consumption, not per-user licenses**: no Power Automate license is required for the flow itself; billing runs through Copilot Studio (capacity packs or pay-as-you-go) [OFFICIAL — flows-faqs; Copilot Studio licensing guide]. The documented meter: **13 Copilot Credits per 100 actions** [OFFICIAL — Microsoft Copilot Studio pricing/licensing pages, corroborated by multiple licensing guides]. Capacity: **25,000 credits / $200 per month per pack**, or PAYG at roughly **$0.01 per credit** [OFFICIAL — pricing page/licensing guide].
- **Cloud flows** are licensed through Power Automate (user plans, per-flow/process licenses) — the biggest practical difference between the two [OFFICIAL — flows-faqs + licensing guides].
- The flow must be set to run under the **Copilot Studio plan** to surface as an agent tool [CAT — gotchas #1; also an express-mode prerequisite, OFFICIAL].
- New-harness billing: usage on the GitHub Copilot harness is billed in Copilot Credits **from the moment makers begin building — including previews, tests, and evaluations**; Microsoft 365 Copilot licenses do **not** cover GitHub Copilot harness consumption; cost management is in the Power Platform admin center [OFFICIAL — MC1446644 relays].
- Sharing model limits: agent flows **can't be copied, shared, co-owned, or given run-only permissions from Copilot Studio** [OFFICIAL — flows-faqs]; the CAT workaround is adding a co-owner in the Power Automate portal (section 5).

**Where they run** [OFFICIAL, pieced from Learn]: agent flows/workflows are created natively in Copilot Studio (or Power Automate), are **solution-aware**, record version history in **Microsoft Dataverse**, and execute on Power Platform flow infrastructure under Copilot Studio billing; express mode additionally requires the environment to be on Power Automate's "new infrastructure". Monitoring lives in Copilot Studio (Activity tab / flow monitoring page) rather than requiring the Power Automate portal.

## 5. Security and governance implications

- **Two-layer credential model (top gotcha)**: setting a workflow tool's Credentials to "Maker-provided credentials" in Copilot Studio only changes how the *agent invokes the flow*; every action inside the flow authenticates via its own **Connection Reference**. To truly run under maker credentials you must update the connection references inside the flow itself [CAT — gotchas #4]. Governance implication: flows can silently run with a different identity than the tool setting suggests; audit both layers [INFERRED].
- **Maker-credential flows are a privilege-escalation surface**: any user of the agent exercises the maker's connections. Prefer end-user credentials where the connector supports it, and treat maker-credential flows as service accounts with least privilege [INFERRED from CAT #4].
- **Sharing semantics differ by artifact**: sharing an agent with editor permissions also grants access to its agent flows; sharing a flow *independently* is not possible from Copilot Studio — add a **co-owner in Power Automate**, which grants full flow edit access with **no access to the agent** (useful scoped-access pattern) [CAT — gotchas #5].
- **ALM/solution governance**: agents, workflows, connection references, and environment variables must live in a **solution**; anything built outside one can't be promoted through Dev→Test→Prod pipelines. Deploy managed solutions downstream; bind connections per environment via connection references at deployment [CAT — ALM foundation post]. Flows outside solutions also frequently fail to appear as agent tools at all [CAT — gotchas #1].
- **Callback/webhook exposure**: in pause-and-resume (webhook action) patterns, the platform-generated `notificationUrl` is SAS-signed but **requires no authentication — anyone with the URL can resume the flow**. Keep it server-side only; never expose it to browsers or end users [CAT — HITL post]. Implement webhook unsubscribe (DELETE) for cancelled flows [CAT].
- **External triggering**: triggering agents over HTTP requires Direct Line secrets — never hard-code them, store in Azure Key Vault, rotate regularly, and enable "Require secured access" on the web channel [CAT — HTTP triggering post].
- **Cost governance**: because the new harness bills credits from the first maker test, unmonitored experimentation is itself a spend event; use PPAC cost management and budgets [OFFICIAL — MC1446644 relays; INFERRED emphasis].

## 6. Performance and maintainability implications

- **The 100-second wall dominates design**. Any workflow exposed as a synchronous tool must respond inside 100 seconds or the agent surfaces `FlowActionTimedOut` [OFFICIAL + CAT]. Mitigations, in order: optimize the flow; adopt the async continuation pattern; move heavy processing out of the synchronous call path [CAT — gotchas #2].
- **Express mode (preview)** speeds up agent-invoked flows: requires the "When an agent calls a flow" (or "When an app calls a flow") trigger + Response action, a Copilot Studio plan on the flow, and new Power Automate infrastructure; best for logic-heavy, data-light flows under 100 actions [OFFICIAL — agent-flow-express-mode].
- **Paused flows dehydrate**: webhook-action-based waits consume no resources and can wait minutes to days before rehydrating on callback — long human waits are cheap if you architect for them asynchronously [CAT — HITL post].
- **Payload discipline**: Base64 encoding inflates files ~33%; combined with the 1 MB return cap, inline Base64 is only for small images/files. For anything larger: store in Azure Blob / SharePoint / Dataverse file column and return a link (SAS URL, sharing link, or authenticated proxy) [CAT — gotchas #6; OFFICIAL for the 1 MB cap].
- **Schema drift is the top runtime breakage**: `FlowActionBadRequest` almost always means the tool's cached input/output schema no longer matches the flow — refresh the tool/Action node after any parameter change, and check for unsupported types (only Text/Boolean/Number natively; Choice/ClosedListOptionSet values error) [CAT — gotchas #3; community corroboration].
- **Maintainability wins in the new designer**: node-level testing (run one node in place, AI prompt preview without credit consumption), inline error surfacing with a publish gate, and run history with per-run duration shorten the debug loop versus classic run-the-whole-flow debugging [OFFICIAL — designer page + May 2026 blog].
- **Cost/latency predictability**: a deterministic workflow bills a flat, low action meter (13 credits/100 actions) and executes the same path every run, whereas agentic reasoning over the same steps costs more and varies per run — pushing stable logic into workflows is both a reliability and a cost optimization [INFERRED from official billing rates].

## 7. Architecture guidance and anti-patterns

**Patterns that work:**
1. **Workflow-as-tool for deterministic subroutines** — the agent handles conversation and judgment; every stable multi-step procedure becomes a named workflow tool with typed inputs/outputs and a clear description the orchestrator can select on [OFFICIAL + CAT].
2. **Agent node inside a workflow** — for one AI-dependent step (classify, extract, interpret) inside an otherwise rule-based process; the workflow keeps control, sequencing, and audit trail [OFFICIAL blog + CAT gotchas #7].
3. **Async continuation for long-running work** [CAT — gotchas #2]: split the flow at "Respond to the agent" — quick acknowledgment logic before it (<100 s), long-running work (approvals, human input) after it; finish with the **"Execute Agent"** action (Microsoft Copilot Studio connector) to call the agent back with results. **Pass `System.Conversation.Id`** into the flow and back through Execute Agent so the callback session correlates with the original conversation; update agent instructions to handle both the initial call and the asynchronous callback.
4. **Custom human-in-the-loop via webhook actions** [CAT — HITL post]: a custom connector with `x-ms-notification-url` + `x-ms-notification-content` and *no* `x-ms-trigger` creates an action that pauses (dehydrates) the workflow until your own backend POSTs to the callback URL — plug in any approval UI instead of email/Teams cards.
5. **External triggering**: fire-and-forget into an agent from outside via a cloud flow ("When an HTTP request is received" → "Execute Copilot" → return conversationId) or raw Direct Line REST (token → conversation → activity → poll) [CAT — HTTP triggering post].
6. **File hand-off**: Question node with File entity + metadata (or `System.Activity.Attachments`) → Power Fx `{ contentBytes, name }` record into a File-typed flow input; `base64ToBinary()` inside the flow where actions need binary [CAT — passing-files post].

**Anti-patterns:**
- **Synchronous approvals in chat** — "Run a multistage approval" or "Request information" inside a synchronous tool call will always time out; there is currently no way to run these through a synchronous conversational experience without the async pattern [CAT].
- **Monolithic flows** that do acknowledgment, heavy processing, and notification in one synchronous body [CAT #2].
- **Agent-for-everything** — re-implementing stable rule-based processes as agent instructions sacrifices determinism, auditability, and cost predictability for no benefit [OFFICIAL guidance + INFERRED].
- **Editing flow parameters without refreshing the tool** — guaranteed `FlowActionBadRequest` later [CAT #3].
- **Passing Tables/Records/complex objects directly** into flow inputs — unsupported without conversion [OFFICIAL + CAT].
- **Building outside solutions** (invisible to ALM, may not even appear as a tool) and **forgetting the Copilot Studio plan setting or leaving the Asynchronous response toggle on** (tool never appears in the picker) [CAT #1, ALM post].
- **Trusting the tool-level credentials setting alone** — connection references inside the flow decide the real identity [CAT #4].
- **Large Base64 payloads through the agent** — 33% inflation against a 1 MB cap; use storage + link [CAT #6 + OFFICIAL].
- **Exposing the webhook `notificationUrl`** to any client-side surface [CAT — HITL].

## 8. Sources

**Local files (read in full):**
- /workspace/microsoft/mcscatblog/_posts/2026-04-17-combining-agent-flows-and-agents-gotchas-errors-and-patterns.md
- /workspace/microsoft/mcscatblog/_posts/2025-10-15-copilot-studio-passing-files-flows-connectors.md
- /workspace/microsoft/mcscatblog/_posts/2025-09-25-triggering-copilot-studio-http.md
- /workspace/microsoft/mcscatblog/_posts/2026-05-20-human-in-the-loop-custom-connector.md (read in full)
- /workspace/microsoft/mcscatblog/_posts/2026-07-07-new-orchestrator-resources.md (relevant excerpts)
- /workspace/microsoft/mcscatblog/_posts/2026-05-20-alm-copilot-studio-agents-foundation.md (relevant excerpts)
- /workspace/microsoft/mcscatblog/_posts/2026-07-15-redlining-documents-new-copilot-studio-experience.md (relevant excerpt)

**Microsoft Learn (via WebSearch synthesis; direct fetch blocked):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/workflows-experience/flows-overview — Workflows overview (new experience, preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/flows-overview — Agent flows and workflows overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/tools-add-workflow — Add a workflow to your agent as a tool (preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/workflows-experience/flow-agent — Add a workflow as a tool to an agent
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/workflows-experience/flow-designer — Edit and manage your workflow in the designer
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/workflows-experience/agent-node-workflow — Add an agent node to a workflow
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-node-workflow — Add an agent node to an agent flow (classic)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/flow-designer — Edit and manage your agent flow in the designer (classic)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/flows-faqs — Agent flows FAQ
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-flow-input-output — Input/output variables (types, 1 MB limit)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-flow-create — Create an agent flow as a tool
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/flow-agent — Add an agent flow as a tool (classic)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/flow-nl — Build an agent flow with natural language
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-flow-express-mode — Express mode (preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/flow-manage-monitor — Monitor your agent flows
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/faq-billing-licensing — Billing/licensing FAQ
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing — Standard harness licensing
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/troubleshooting-error-codes — Error codes (new experience)
- https://learn.microsoft.com/troubleshoot/power-platform/copilot-studio/authoring/error-codes — Error codes reference

**Microsoft blogs / announcements (via WebSearch):**
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/new-and-improved-computer-using-agents-a-new-workflows-experience-and-real-time-voice-experiences/ — What's new May 2026 (workflows public preview)
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/new-and-improved-agent-governance-intelligent-workflows-and-connected-app-experiences/ — What's new April 2026 (AI actions in workflows)
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/automate-business-processes-with-agents-plus-workflows-in-microsoft-copilot-studio/ — Agents + workflows guidance
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/more-powerful-agents-and-workflows-for-autonomous-business-processes-introducing/4542969 — New harness announcement
- https://www.microsoft.com/en-us/microsoft-365-copilot/pricing/copilot-studio — Copilot Studio pricing

**Third-party corroboration (used cautiously, tagged where relied on):**
- https://pupuweb.com/mc1446644-microsoft-copilot-studio-github-copilot-harness-now-generally-available-for-building-autonomous-agents-and-workflows/ — MC1446644 relay (GA 2026-08-03)
- https://mwpro.co.uk/blog/2026/08/03/mc1446644-microsoft-copilot-studio-makes-github-copilot-harness-generally-available-for-building-agents-and-workflows/ — MC1446644 relay
- https://rpabotsworld.com/microsoft-copilot-studio-august-2026-rebuilt-agent-platform-guide/ — workflow designer GA claim (conflicting)
- https://samexpert.com/copilot-studio-licensing-guide/ and https://www.cloudzero.com/blog/copilot-studio-pricing/ — credit rates corroboration (13/100 actions, pack pricing)
- https://www.powerapps911.com/post/workflows-power-automate-cloud-flows-or-copilot-studio-agent-flows — agent flows vs cloud flows licensing
- https://rishonapowerplatform.com/2025/12/15/copilot-studio-using-choice-variable-in-agent-flows/ — ClosedListOptionSet type error
