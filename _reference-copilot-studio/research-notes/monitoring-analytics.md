# monitoring-analytics

Research note, compiled 2026-08-19. Claim tags: [OFFICIAL] = documented Microsoft behavior (Learn page, Microsoft "What's new" entry, or Microsoft-authored GitHub content, cited); [CAT] = Copilot Studio CAT blog guidance/practice; [INFERRED] = analyst reasoning. [STATUS UNVERIFIED] where confirmation failed. Sourcing caveat: direct fetching of learn.microsoft.com was blocked and the WebSearch budget was exhausted by sibling research tasks, so Learn-derived claims come from (a) Learn citations already verified in sibling notes from earlier searches, (b) public Microsoft GitHub repositories that carry Learn/official content (MicrosoftDocs/power-platform, microsoft/agent-academy, Azure/Copilot-Studio-and-Azure), and (c) a mirror of the official "What's new in Copilot Studio" feed. Each is identified inline; residual uncertainty is flagged.

## 1. What it is and how it works

**Where monitoring lives in the new experience.** The new agents experience (GitHub Copilot harness) is a four-tab surface: **Build, Preview, Evaluate, Monitor** [OFFICIAL — Learn `agents-experience/build-overview`, `preview-overview`, `analytics-agent-evaluation-intro`, `authoring-review-activity`, per sibling-verified search; corroborated by Microsoft's agent-academy training: Build = "identity, knowledge, tools, skills, model", Preview = "test it interactively", Evaluate = "run test sets to measure quality", Monitor = "review tasks, files accessed, and activity after you ship"]. The division of labor is explicit: Preview is manual, one-conversation-at-a-time exploration; Evaluate is automated multi-test-case quality measurement; **Monitor is what the agent is doing after it is published** [OFFICIAL — agent-academy; third-party learning-hub phrasing agrees].

**What the Monitor area shows.** Per Microsoft's own GA framing, "Dedicated Evaluate and Monitor tabs let teams create test sets, run evals, and review **task history, file access, and activity** after deployment" [OFFICIAL — Microsoft harness GA announcement of 2026-08-03, read via a third-party mirror]. A community training source itemizes the Monitor tab as: **recent tasks** (what the agent completed or attempted), **task status** (successful / failed / in-progress), **files accessed**, **activity context** of conversations and actions, **analytics** (response times, user satisfaction, usage patterns), and **errors** [third-party — krazykap learning hub; the item list is consistent with the official one-liners but is NOT independently confirmed against Learn — STATUS UNVERIFIED at that granularity]. Microsoft training also documents a **Monitor → Performance** area that consolidates user-feedback analytics: a **Reactions card** (thumbs-up vs thumbs-down counts per period), a **total reactions tile**, and drill-down to user comments filtered by feedback type — described as replacing the classic **Analytics → Satisfaction** page [OFFICIAL — microsoft/agent-academy, operative-v2 module 11].

**The unified activity + transcript view.** Copilot Studio ships a unified **activity and transcript view** where makers can inspect sessions, **pin sessions**, and **submit feedback**, positioned for "faster, more effective troubleshooting" — a GA update announced 2025-10-01 on the official What's new feed, pointing at Learn `authoring-review-activity` [OFFICIAL — What's new entry via digest mirror]. The **activity map** is the per-turn execution view: Microsoft's Azure troubleshooting docs call it "the call stack for a conversation turn" — it shows the execution chain (connected agents, topics, tools, knowledge lookups) for each turn, and you select individual steps to inspect their inputs and outputs [OFFICIAL — Azure/Copilot-Studio-and-Azure diagnostic toolbox]. In the new experience, every step of the agentic loop is recorded in an **activity trace** (Learn `agents-experience/authoring-activity-trace`) and CAT calls the **reasoning view** "your main debugging surface" — e.g., watching which Skill loads and how its steps execute [OFFICIAL — Learn via sibling-verified search; CAT — modern-mcs-agent-skills].

**The analytics metric set.** The built-in Analytics surface provides, with no setup: session outcomes (Resolved / Escalated / Abandoned), AI-generated **themes** clustering user questions (preview as of 2025-10), **generated answer rate and quality** scoring with drill-down to individual questions, **sentiment analysis**, **CSAT**, **tool use metrics**, and **estimated savings / ROI analytics** (time and cost saved per successful autonomous run, customizable to org metrics) [CAT — open-the-hood post, citing Learn `analytics-overview`, `analytics-themes`, `analytics-improve-agent-effectiveness`, plus OFFICIAL What's-new entries for `analytics-cost-savings`]. Later official additions: **question and reaction lists** — view/filter detailed lists of user questions and thumbs reactions, downloadable to CSV for users holding the transcript-viewer permission (2026-03); **session identifiers included in downloaded session transcripts** (2026-03); and **custom analytics metrics** — define your own analytics categories visualized alongside built-in analytics (preview, 2026-04) [OFFICIAL — What's new via digest mirror: `analytics-question-reaction-lists`, `analytics-drill-down-lists#download-underlying-data-to-a-csv-file`, `analytics-transcripts-studio#work-with-session-transcripts`, `analytics-custom-metrics`].

**Transcripts and the underlying data model** [CAT — open-the-hood technical reference, all of the following]. Conversation data persists in the Dataverse **`ConversationTranscript`** table, written automatically (pull model) about **30 minutes after conversation inactivity**. Four concepts must not be conflated: **ConversationId** (thread GUID, embedded in the `Name` column as `{ConversationId}_{BotId}`); **record** (one row = one inactivity window = one `ConversationStartTime`; content over **1 MB** splits into multiple records reassembled by `Metadata.BatchId`); **session** (the analytics unit — starts at first user message, ends after **30 minutes of inactivity**, carries a `SessionInfo` activity with outcome); and **conversation** (the human concept, reconstructed by grouping records by `Name`). Transcript JSON contains the diagnostic layer: `IntentRecognition` activities with `TopicName` and confidence `Score`, `DialogRedirect`s, event activities for tool/connector/HTTP/MCP/child-agent invocations including payloads, **generative orchestration trace data showing the plan**, `SearchAndSummarizeContent` results in `nodeTraceData` (which knowledge sources were searched and what chunks returned), per-activity timestamps, `SessionInfo` outcomes, and `CSATSurveyResponse`.

**Inspecting orchestrator decisions.** You can always see *what* the orchestrator planned (search these sources, call this tool, then summarize). With a **deep reasoning model**, the chain of thought is shared in the transcript — the *why*; without it you see only the resulting plan [CAT — open-the-hood]. In custom UIs, agents on **Anthropic models** stream reasoning as incremental `typing` activities with `channelData.streamType: "informative"` (grouped by `streamId`) through the Microsoft 365 Agents SDK, ahead of the final `message` activity — GPT-family models did not emit thinking traces as of that writing [CAT — show-reasoning-agents-sdk, 2025-11]. The same Activity-protocol interception supports custom developer tooling that captures the planner's "thoughts," tool calls, and per-utterance latency statistics [CAT — response-analysis tool post].

**Session/conversation IDs and correlating users.** End users self-serve the conversation ID: **`/debug conversationid`** in custom agents (M365 Copilot chat, Teams, webchat), **`/debug`** for declarative agents, returning a GUID [CAT — conversationid-users post]. That GUID is the correlation key everywhere: filter the Dataverse `Name` column where it starts with the ID; in Application Insights, `customEvents | extend conversationId = tostring(customDimensions["conversationId"]) | where conversationId == '…'` [CAT]. `/debug clearstate` forces a full conversation reset in Teams [CAT — technical reference]. Caveat on user correlation: in anonymous channels (webchat), App Insights `user_Id` is a **session-based identifier that changes per conversation** — "distinct users" is really "unique conversations"; only authenticated channels give a stable identity [CAT].

**Application Insights integration.** Configured at **Settings > Advanced > Application Insights** with a connection string, with three toggles: **Log activities** (incoming/outgoing messages and events), **Log sensitive Activity properties** (user IDs, names, message text), **Log node tools** (an event per topic-node execution) [CAT — technical reference, citing Learn `advanced-bot-framework-composer-capture-telemetry`]. App Insights delivers near-real-time push telemetry: per-turn request/response timing, dependency calls (knowledge lookups, tool/connector invocations), errors/exceptions/stack traces, and built-in alerting; queryable in KQL, with an official **Analytics Template Workbook** for out-of-box dashboards [CAT citing Learn]. All telemetry carries a `DesignMode` custom dimension to separate test-pane traffic from production [CAT]. Cost/consumption monitoring is separate: the Power Platform admin center exposes consumption at **tenant, environment, agent, and downloadable-report** levels, and GitHub Copilot harness agents are identifiable via **`properties.isCLIAgent`** in Azure Resource Graph / the Power Platform API [OFFICIAL — MicrosoftDocs/power-platform `manage-usage-github-copilot-harness.md`; CAT — cost-governance post].

## 2. When to use it / when NOT to use it

CAT structures the choice by persona [CAT — open-the-hood]:

- **Maker debugging (building, something's off):** use the test pane and its **Save snapshot** (`...` menu → downloads a `botcontent` zip with `dialog.json` transcript + full agent configuration); in the new experience, the activity trace / reasoning view in Preview. Not the place for Dataverse or App Insights.
- **Support/ops triage (user-reported problem in production):** get the conversation ID from the user (`/debug conversationid`), check **App Insights first** (errors, latency, dependency failures, near real-time), pull the **Dataverse transcript** when you need orchestration context. "App Insights shows you the error. The transcript shows you the context."
- **Analyst trends (patterns at scale):** start with **built-in Analytics** (no setup), use the **Copilot Studio Kit** (Conversation KPIs generated twice daily or on demand, transcript visualizer, Conversation Analyzer running custom AI prompts against transcripts) as middle ground, and **Dataverse link to Microsoft Fabric** + Power BI for fully custom pipelines and long-term retention.

**Use the Monitor tab** for post-publish operational review — "especially useful for agents that take autonomous actions, such as sending emails, updating records, or interacting with Microsoft 365 services" [third-party learning hub; consistent with OFFICIAL "after you ship" framing] — and, on the harness, to watch credit consumption against limits [OFFICIAL — GA announcement guidance to "monitor the Monitor tab and set appropriate limits or alerts"].

**Do NOT rely on these surfaces when:**
- **You need real-time alerting.** Dataverse transcripts land ~30 minutes after inactivity and have no alerting (needs Power Automate); only App Insights offers built-in alerts [CAT].
- **You need session outcomes or CSAT in App Insights** — they exist only in Dataverse; App Insights has neither, and knowledge-source detail, intent confidence scores, and orchestration plans are absent there too (tool invocations surface only as `TopicStart` events) [CAT — explicit warning].
- **You need token-level cost accounting.** Token counts are not tracked in transcripts; billing is Copilot Credits, monitored in PPAC [CAT/OFFICIAL].
- **You need per-user cost attribution.** "Copilot Studio usage is billed at the environment and agent level, not at the user level" [OFFICIAL — manage-usage doc].
- **You are in a developer environment** — transcripts are not written there at all, regardless of settings [CAT citing Learn].
- **You want full prompt auditing** — the assembled system prompt is deliberately never exposed [CAT].
- **Pre-release quality measurement** belongs in Evaluate (test sets, LLM-judged), not Monitor [OFFICIAL framing; INFERRED boundary: Monitor tells you what happened, Evaluate tells you whether a change is safe to ship].

## 3. Classic-experience comparison (what it replaces or simplifies)

- **Navigation collapse.** Classic scattered observability across the Analytics section, the test pane's Activity map, and Settings-level integrations. The new experience consolidates the operational view into one **Monitor** tab of a four-tab surface [OFFICIAL]. Concretely documented replacement: **Monitor → Performance** supersedes classic **Analytics → Satisfaction** for reactions/CSAT [OFFICIAL — agent-academy].
- **Unified activity + transcript view** (GA 2025-10) merges what used to be separate transcript downloads/browsing and activity inspection, adding session pinning [OFFICIAL — What's new].
- **From topic vocabulary to task vocabulary.** Classic diagnostics speak in topics fired, trigger scores, node traces; the new Monitor speaks in **tasks, task status, files accessed, tool/skill activity** — matching the agentic loop rather than the topic graph [OFFICIAL one-liners + third-party detail; INFERRED characterization].
- **What is NOT replaced — the classic data plane persists.** Dataverse `ConversationTranscript`, the Bot Transcript Viewer role, Analytics CSV export, App Insights integration, and the Copilot Studio Kit all remain the underlying machinery; the App Insights setup doc is literally still the Bot-Framework-Composer-era page [CAT]. [INFERRED] The new Monitor tab is best understood as a new *presentation layer* over largely pre-existing telemetry stores, so classic-era limits (30-min delay, retention, role model) continue to bind new-experience monitoring. Confidence caveat: how completely new-harness runs (skill loads, sandbox code runs, file access) are written into `ConversationTranscript` versus a harness-specific store is not documented in any source consulted — [STATUS UNVERIFIED].
- **Known regression at launch:** classic Activity-tab equivalents were reported as not fully replicated in the new experience [third-party; STATUS UNVERIFIED].
- **Orchestrator inspection improved.** Classic gave IntentRecognition scores; generative orchestration added plan traces in transcripts; the new experience adds a first-class reasoning/activity trace on every run, plus model-level reasoning streams (Anthropic models) and shared chain-of-thought under deep reasoning [CAT; OFFICIAL].

## 4. Limitations, GA/preview status, licensing notes

**Status ledger (as learned, per feature):**
- Unified activity & transcript view (`authoring-review-activity`): **GA update 2025-10-01** [OFFICIAL — What's new].
- Analytics **themes**: **preview** as of 2025-10 [OFFICIAL — What's new].
- **Generated answer rate and quality**: announced **GA 2025-08** on What's new; the CAT post (2026-03) still links an anchor named `…-preview` — sources conflict on labeling; treat as GA per the later official announcement, flag the drift [OFFICIAL vs CAT anchor].
- **Agent evaluations**: preview 2025-10 → **GA announced 2026-03**; multi-turn evaluation and version-comparison added around then [OFFICIAL — What's new].
- **Custom analytics metrics**: **preview**, 2026-04 [OFFICIAL — What's new].
- **GitHub Copilot harness** (with its Evaluate and Monitor tabs): **GA 2026-08-03** per message center MC1446644 and the harness announcement; individual Monitor-tab features' statuses not separately verified — [STATUS UNVERIFIED per-feature].
- ROI / cost-savings analytics: GA updates through 2025-09/10 [OFFICIAL — What's new].

**Documented limits and numbers:**
- Transcript write delay: **~30 minutes after inactivity**; default retention **30 days** (a Power Apps bulk-delete job, reschedulable); **1 MB** per `Content` record (split via `BatchId`); session boundary = **30 minutes** of inactivity [CAT citing Learn].
- Analytics UI download: only the **last 29 days**; `ChatTranscript` CSV truncates at **512 characters per bot response** [CAT].
- App Insights retention: up to **730 days** (configurable); Dataverse 30 days by default [CAT].
- Synchronous response timeout **~120 seconds** with silent failure in Teams — *observed behavior from community reports, explicitly not official documentation* [CAT, so labeled].
- Transcripts are **not written in developer environments** [CAT citing Learn].
- Not captured anywhere: the full assembled LLM prompt; token counts; agent responses grounded in SharePoint documents containing sensitive data (excluded by design, leaving gaps); orchestrator reasoning without a deep-reasoning model [CAT citing Learn].

**Licensing/roles:**
- Viewing/downloading transcripts (Analytics UI, Power Apps, Web API) requires the Dataverse **Bot Transcript Viewer** security role; App Insights queries need Azure RBAC **Reader**/**Log Analytics Reader**; transcript settings need environment/system admin [CAT — technical reference].
- The transcript-based analytics themselves carry no extra Copilot Studio license, but App Insights is a billable Azure resource [INFERRED from the integration model; Azure billing not quantified in sources].
- Harness monitoring context: usage-based Copilot Credits billing applies **including maker build/preview/evaluate activity**; **developer and trial environments move to usage-based billing 2026-09-01**; "Non-billed Copilot Credits" report data is marked preview [OFFICIAL — manage-usage doc; MC1446644 relays].

## 5. Security and governance implications

- **Transcripts are PII.** They hold personal interactions, business data, and identifiers. CAT's explicit guidance: grant **Bot Transcript Viewer sparingly** and apply a **four-eyes principle** for live conversation access; admin-level transcript controls exist (Learn `admin-transcript-controls`) [CAT]. User-feedback comments are stored in conversation transcripts too, adding a free-text PII channel [OFFICIAL — agent-academy].
- **The App Insights toggles are a governance decision.** "Log sensitive Activity properties" ships user IDs, names, and message text into an Azure resource governed by Azure RBAC, outside the Dataverse security model. [INFERRED] Enabling it duplicates regulated data into a second store with its own (up to 730-day) retention — data-protection review belongs before the toggle, and the Azure resource's access list must mirror the Dataverse role discipline.
- **Diagnostic artifacts leak.** Test-pane snapshots, App Insights query results, and HAR files "contain tokens, cookies, user messages, and business data — always redact before external sharing" [OFFICIAL — Azure diagnostic toolbox].
- **Compliance completeness cuts both ways.** Sensitive-grounded responses are excluded from transcripts as a privacy safeguard — which also means transcripts are **not** a complete record for audit purposes; do not represent them as such [CAT fact; INFERRED audit consequence].
- **Retention pipelines inherit the obligation.** Syncing `ConversationTranscript` to Fabric/Synapse for long-term analytics deliberately outlives the 30-day Dataverse purge; [INFERRED] the lakehouse then needs its own retention, minimization, and access policy or you have built a shadow PII archive.
- **Access to conversation details is role-gated by design**: makers see their own agents' conversations; admins per assigned environment/tenant roles; support staff need explicit data permissions [CAT — conversationid post].
- **Consumption governance is observability too.** Monitor harness agents via PPAC allocations/limits and the Licensing API (entitlement consumption reads, resource thresholds with notify-at-% and stop-usage); note in-product limit alerts go to admins, not necessarily the agent owner — assign triage explicitly [CAT — cost-governance; OFFICIAL — Licensing API endpoints cited there].

## 6. Performance and maintainability implications

- **Latency evidence is first-class.** Per-activity timestamps in transcripts and full timing/dependency data in App Insights make step-level latency attribution routine; CAT's ~200-line KQL trace query ships five output modes (chronological trace, conversation summary, topic timing, response latency, action breakdown) [CAT — technical reference]. The canonical case study: a 34 s connector call + a 62 s catch-all Azure AI Search scan + LLM generation ≈ 130 s → past the ~120 s timeout → silent failure; fixes (repoint stale knowledge sources, add semantic ranking / narrower scope, timeout + graceful fallback in the catch-all) brought average response to ~35 s [CAT — open-the-hood]. That is the template for "runtime evidence improves architecture."
- **Filter hygiene affects every metric.** Exclude test traffic with `customDimensions['DesignMode'] == "False"`; count **sessions** (not records, not "conversations") as the analytics unit, since one user interaction can be 1 or 3 sessions depending on idle gaps [CAT].
- **Conversation-boundary management is an agent-design task.** A 30-minute session tick does not reset state; in Teams the thread persists indefinitely and stale context degrades answers. Mitigations: an inactivity-trigger reset topic, explicit end-of-conversation signals, `/debug clearstate` — all Standard-harness mechanics; new-experience equivalents are undocumented in consulted sources [CAT; STATUS UNVERIFIED for the new harness].
- **Scale paths protect the platform.** For reporting at scale, sync to Fabric rather than hammering the Dataverse Web API (avoids API limits, controls data shape and refresh); Kit Conversation KPIs precompute outcomes twice daily [CAT].
- **Maintainability:** monitoring here is mostly configuration (toggles, roles, workbook) rather than code — but KQL queries, Fabric notebooks that flatten transcript JSON, and custom dashboards become real artifacts that must be versioned and re-validated as the transcript schema and the What's-new cadence evolve [INFERRED; the analytics surface demonstrably changed multiple times between 2025-08 and 2026-04].
- **Observability has a cost gradient.** Forcing extra logging steps through orchestrator instructions (e.g., CoT-logger patterns) multiplies model calls and credits; deep-reasoning transparency bills at reasoning-model rates [CAT trade-off notes].

## 7. Architecture guidance and anti-patterns

**Guidance:**
1. **Run two planes, on purpose.** Dataverse transcripts for content, orchestration plans, outcomes, CSAT; Application Insights for errors, latency, dependencies, alerting. "Most production setups need both" — design triage to start in App Insights and pivot to the transcript for context [CAT].
2. **Make the conversation ID the spine of support.** Publish `/debug conversationid` (and `/debug` for declarative agents) in help text and ticket templates; every store — transcript `Name`, App Insights `customDimensions.conversationId` — keys off it [CAT].
3. **Instrument before launch.** Connect App Insights as a production best practice; decide the sensitive-logging toggle with governance; deploy the Analytics Template Workbook; verify you are NOT in a developer environment if you expect transcripts [CAT/OFFICIAL].
4. **Close the loop into architecture.** Treat Monitor/transcript findings as design inputs: knowledge sources returning 0 chunks → fix source configuration; slow catch-alls → scope or index work; Skills firing too often/never → rewrite the Skill description; repeated task failures on a tool → move that action behind a deterministic workflow [CAT patterns; INFERRED last mapping].
5. **Tier retention deliberately.** 30-day Dataverse for operational lookback; Fabric lakehouse (or Synapse Link) for trend history; App Insights/Log Analytics for operational history — each with an owner and a retention policy [CAT + INFERRED].
6. **Evaluate gates, Monitor verifies.** Use Evaluate (now GA) plus CI eval gates pre-ship; use Monitor + feedback lists post-ship; feed Monitor evidence back into new eval cases [OFFICIAL surfaces; CAT eval-gate practice; INFERRED loop].
7. **For autonomous harness agents, watch actions and credits together**: Monitor tab for task history/file access, PPAC + threshold APIs for spend, from day zero [OFFICIAL — GA announcement + manage-usage doc; CAT — cost-governance].

**Anti-patterns:**
- **Alerting off Dataverse** — ~30-minute-delayed, alert-less store; incidents surface via App Insights or not at all [CAT-grounded].
- **Expecting session outcomes/CSAT in App Insights** — "the most common source of confusion" [CAT].
- **Building content analytics on the Analytics CSV** — 512-char truncation per response silently corrupts text analysis [CAT].
- **Counting `user_Id` as users on anonymous channels**; skipping the `DesignMode` filter and mixing test traffic into production KPIs [CAT].
- **Treating transcripts as a complete audit record** — sensitive-grounded responses are excluded; prompts and tokens never appear [CAT].
- **Broad Bot Transcript Viewer grants** or an ungoverned Fabric transcript archive [CAT + INFERRED].
- **KPI-ing "conversations"** instead of sessions — idle-gap semantics make it unmeasurable as stored [CAT].
- **Diagnosing by guesswork** — tweaking instructions/settings without opening the trace; "the difference between guessing and debugging with data" [CAT].
- **Assuming classic monitoring mechanics transfer to the harness unverified** — e.g., inactivity-reset topics or App Insights event vocabulary (`TopicStart`) may not map 1:1 to task-based runs [INFERRED; flagged UNVERIFIED above].

## 8. Sources

**Local files (read in full):**
- /workspace/microsoft/mcscatblog/_posts/2026-03-19-open-the-hood-copilot-studio-transcripts.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-19-open-the-hood-technical-reference.md (note: front matter `published: false` — CAT-authored draft in the clone)
- /workspace/microsoft/mcscatblog/_posts/2026-01-24-conversationid-users.md
- /workspace/microsoft/mcscatblog/_posts/2025-11-05-show-reasoning-agents-sdk.md
- /workspace/microsoft/mcscatblog/_posts/2026-01-16-response-analysis-copilot-tool.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-06-copilot-studio-kit.md
- /workspace/microsoft/mcscatblog/_posts/2026-08-07-copilot-harness-cost-governance.md (targeted grep)

**Sibling research notes cross-referenced (Learn citations therein verified by earlier WebSearch in this workflow):**
- /tmp/claude-0/-home-user-KPINewV/67aff1a0-22fc-5b39-b5bb-dfa7459e10d0/scratchpad/research/new-experience-overview.md
- /tmp/claude-0/-home-user-KPINewV/67aff1a0-22fc-5b39-b5bb-dfa7459e10d0/scratchpad/research/orchestration.md

**Official Microsoft content fetched directly (GitHub raw):**
- https://raw.githubusercontent.com/MicrosoftDocs/power-platform/main/power-platform/admin/manage-usage-github-copilot-harness.md
- https://raw.githubusercontent.com/MicrosoftDocs/power-platform/main/power-platform/guidance/adoption/observability.md
- https://raw.githubusercontent.com/microsoft/agent-academy/main/docs/operative-v2/11-obtain-user-feedback/index.md
- https://raw.githubusercontent.com/microsoft/agent-academy/main/docs/recruit-nextgen/02-copilot-studio-fundamentals/index.md
- https://raw.githubusercontent.com/Azure/Copilot-Studio-and-Azure/main/docs/troubleshooting/00-diagnostic-toolbox.md
- https://raw.githubusercontent.com/aktsmm/m365-copilot-update-digest/main/summaries/daily/2025-10-01.md and .../2026-03-01.md (mirror of the official "What's new in Copilot Studio" feed; also GitHub code-search fragments from 2025-07-01, 2025-08-01, 2025-12-01, 2026-01-01, 2026-04-01)

**Microsoft Learn pages cited through the above (direct fetch blocked by egress proxy):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-review-activity
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/authoring-activity-trace
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-themes
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-cost-savings
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-custom-metrics
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-question-reaction-lists
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-drill-down-lists#download-underlying-data-to-a-csv-file
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-transcripts-studio and analytics-transcripts-powerapps
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-create / -results / -multi-turn
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-bot-framework-composer-capture-telemetry (App Insights setup + Analytics Template Workbook)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-transcript-controls
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management
- https://learn.microsoft.com/en-us/power-apps/maker/data-platform/azure-synapse-link-view-in-fabric
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/reference/conversationtranscript

**Third-party (used with caution, flagged inline):**
- https://raw.githubusercontent.com/krazykap/copilot-studio-learning-hub/main/14.%20Copilot%20Studio%20New%20Interface%20and%20Features/02.%20Build-Preview-Evaluate%20Monitor.md (Monitor tab item list)
- https://raw.githubusercontent.com/smfworks/aiclearinghouse-site/main/content/blog/2026-08-04-copilot-studio-github-copilot-harness-ga.md (harness GA 2026-08-03 relay incl. Evaluate/Monitor tab description)

**Tools/community assets referenced by sources:** Copilot Studio Kit (https://github.com/microsoft/Power-CAT-Copilot-Studio-Kit), MCS Agent Analyser (https://github.com/Roelzz/mcs-agent-analyser), ResponseAnalysisAgentsSDK and Thinking-Activities samples (https://microsoft.github.io/CopilotStudioSamples/).
