# Exercise 03: Contoso IT Service Desk Agent

**Architectural emphasis: Agent + Tools.** Connector tools vs MCP for ServiceNow, end-user auth vs maker credentials, consent cards, tool description discipline, one Skill for the triage playbook — and why this agent needs **zero workflows**.

## 1. Business need

A Teams agent that (a) troubleshoots common issues (password, VPN, printer, Outlook) from the IT knowledge base, (b) creates and updates ServiceNow incidents, (c) checks ticket status, and (d) orders replacement peripherals from an internal pre-approved catalog — **acting as the signed-in user** so tickets carry the real caller identity and ServiceNow ACLs apply. Employee-facing, Entra-authenticated, high volume, latency-sensitive.

## 2. Classic-style architecture

In classic Copilot Studio (Standard harness) this is a topic forest plus a flow farm:

**Topics (14):** Greeting; Password / VPN / Printer / Outlook Troubleshooting (4); Create Ticket; Ticket Status; Update Ticket; My Open Tickets; Browse Catalog; Place Order; Confirm Order; Escalate to Human; Fallback — plus stock system topics. Each troubleshooting topic is a Question/Condition decision tree ("Which OS?", "Error code?"), ~3–8 branches each (**~45 condition branches**), and **~140 trigger phrases** to hand-tune against misrouting.

**Variables:** ~8 global (`DeviceType`, `TicketNumber`, `Urgency`, `CatalogItemId`, `Quantity`…) + ~20 topic-scoped; **~30 Power Fx expressions** for validation (ticket-number regex, quantity bounds) and slot plumbing.

**Power Automate agent flows (5, ~40 actions):** `SN-CreateIncident`, `SN-GetIncident`, `SN-UpdateIncident`, `SN-ListMyIncidents`, `Catalog-CreateOrder` — each with the agent trigger, Respond-to-agent action, Text/Boolean/Number I/O conversion, and connection references. **3 adaptive cards** (catalog carousel, ticket summary, order confirmation). Generative answers nodes wired to the SharePoint KB inside each troubleshooting topic.

**Total: ~35 authored artifacts**, plus 140 trigger phrases and 45 branches to regression-maintain by hand.

## 3. New-experience redesign

One GitHub Copilot harness agent (harness GA 2026-08-03; sub-feature preview flags in §13). Minimal component set:

- **Instructions (lean, ~350 words):** identity/scope ("Contoso IT Service Desk agent for employees; IT topics only"), tone, grounding rule ("attempt KB-grounded troubleshooting before offering a ticket; cite the article"), one cross-cutting write rule ("before any Create/Update/Order tool call, echo the exact field values back and get explicit confirmation"), escalation triggers (user asks for a human; two failed troubleshooting rounds), out-of-scope refusals (HR, payroll).
- **Knowledge (2):** SharePoint IT KB site (Work IQ path — per-user permission trimming); ServiceNow Knowledge real-time connector **[PREVIEW]** for KB articles mastered in ServiceNow (metadata-only indexing, live query at runtime).
- **Skills (1):** `it-incident-triage-playbook`. Routing description: *"Use when an employee reports an IT problem (broken, error, can't connect, slow) and no ticket exists yet. Runs Contoso's triage sequence: classify category, gather device/OS/error details, apply the matching KB checklist, then assemble impact/urgency and a structured description for ticket creation. Owns the initial report and every follow-up in the same troubleshooting exchange. Do not use for ticket status, ticket updates, or peripheral orders."* Body: category checklists, P1–P4 priority matrix, required-fields incident template, soft pointers to the ServiceNow tools.
- **Tools (6 connector actions, all end-user auth):** ServiceNow connector — Create Incident, Get Incident by Number, Update Incident, List My Incidents; internal catalog **custom connector** (OBO/SSO configured) — Search Catalog, Create Order. Descriptions maker-tuned (§8); `caller_id` bound to the signed-in user, `assignment_group` defaulted — not AI-filled.
- **Workflows:** none (§9).
- **Memory:** OFF (§10).
- **Connected agents:** none (§11).
- **Model:** a GA fast chat-class model (e.g., GPT-5.5 Chat) — high volume, latency-sensitive, no deep-reasoning need; an Anthropic model would add a subprocessor governance sign-off (Anthropic-hosted processing) for no benefit here.

**Total: 11 configured components.**

## 4. Removed components

| Component | Classic | New | What disappears |
|---|---:|---:|---|
| Topics | 14 | 0 | Routing moves to orchestrator + descriptions |
| Trigger phrases | ~140 | 0 | Description-based selection |
| Condition branches | ~45 | 0 | Triage logic → Skill playbook; slot-filling is generative |
| Variables (global + topic) | ~28 | 0 | No variable concept; conversation history + tool outputs |
| Power Fx expressions | ~30 | 0 | Validation → tool input config + instructions |
| Agent flows | 5 (~40 actions) | 0 | Every action is a single connector call (§9) |
| Adaptive cards | 3 | 0 | Rich-UI parity in new experience still in progress — a real loss, see §14 |
| Instructions | 1 | 1 | Stays, leaner |
| Knowledge sources | 2 | 2 | Same |
| Tools (agent-level) | 0 | 6 | Flow bodies collapse into direct connector actions |
| Skills | 0 | 1 | New |
| **Authored artifacts** | **~35** | **11** | **~69% fewer; ~185 hand-tuned routing signals (phrases + branches) → 7 descriptions** |

## 5. Role of Instructions

**In:** identity, scope/refusals, tone, the KB-before-ticket grounding rule, the confirm-before-write rule, escalation triggers — all true in every conversation, the placement test for instructions.

**Deliberately NOT in:** the triage procedure (situational → Skill); KB content (→ Knowledge); tool how-tos that descriptions already carry ("use Get Incident for status" adds tokens, not routing value); priority matrices and templates (→ Skill body); any *security* rule — "act only as the signed-in user" is enforced by end-user auth on the tools, not prose. Instructions load fully on every turn and every token is billed, so lean matters commercially too.

## 6. Role of Knowledge

The SharePoint KB grounds troubleshooting with **per-user permission trimming** (uploaded files have no RBAC — wrong for anything restricted). The ServiceNow Knowledge real-time connector **[PREVIEW]** keeps ServiceNow-mastered articles live with no sync job; only metadata is indexed. Two sources, named by business function, well under the 25-source filtering threshold. Knowledge is *not* used for "list my tickets" — retrieval is top-N, never exhaustive; complete result sets come from the List My Incidents tool.

## 7. Role of Skills

One Skill: the situational procedure the LLM cannot infer — Contoso's category checklists, priority matrix, required-fields template. It loads only during triage (metadata-only otherwise), explicitly claims follow-ups (the documented stickiness fix), and states when *not* to fire so it never activates on plain status checks. No script bundle yet — the playbook is judgment plus a template, not exact computation. Status/update/order paths need no Skill: a well-described tool needs no manual.

## 8. Role of Tools

The heart of this exercise.

**Connector vs MCP for ServiceNow — connector wins here.** Pick the connector when you must (a) **control tool descriptions and inputs** (the orchestration tuning surface), (b) get **per-action DLP/ACP governance**, and (c) keep a **frozen, predictable tool surface** — all three are hard requirements for write actions into the ITSM system of record. An MCP server would mean descriptions and schemas fixed by the server owner (not maker-editable), **no platform-enforced per-tool DLP** (allow the server = allow its entire, dynamically drifting tool surface), and supply-chain exposure when the owner ships changes. Revisit MCP only if Contoso later builds a custom ServiceNow MCP server with thick server-side logic serving *multiple* MCP clients (VS Code, Claude, other agents) — build-once-reuse-everywhere is MCP's genuine advantage. [ASSUMPTION: no first-party ServiceNow MCP server with per-tool governance exists as of 2026-08; the fact base documents ServiceNow as a connector and a knowledge connector only.]

**Tool description discipline.** Descriptions are routing metadata, not documentation — the planner selects on name + description. Examples:

- *Create Incident:* "Creates a new ServiceNow incident for the signed-in employee. Use only after triage has produced category, urgency, and a structured description, and the user confirmed. Do not use to modify an existing ticket."
- *Get Incident by Number:* "Returns status, assignee, and latest work notes for one incident identified by number (INC0012345). Do not use to list multiple tickets — use List My Incidents."
- *Create Order:* "Places an order for one pre-approved catalog item for the signed-in user. Use only after Search Catalog returned the item and the user confirmed item, quantity, and delivery location. Never invent an item ID."

Inputs: `caller_id` bound to the signed-in identity, `assignment_group` hardcoded, free-text fields AI-filled. Outputs kept small (ticket number, state, short description — not full records) to protect the context window. Test: if two reasonable makers would disagree which tool a request hits, the description isn't done. Validate with the activity trace, then evals — fix descriptions before touching instructions.

**End-user auth vs maker credentials — end-user everywhere.** The scenario *requires* acting as the signed-in user: tickets carry the true caller, ServiceNow ACLs and catalog entitlements trim results per user, ServiceNow audit stays honest. Maker credentials on write tools are a privilege masquerade (every user acts as the maker), break the audit chain, and the 2026 wave 1 admin policy lets tenants block them outright — a design built on them is brittle. No tool here fits the legitimate maker-cred niche (shared, non-privileged service reads).

**Consent cards.** First-run consent is expected UX, not misconfiguration: one Allow click per user per connection, then silent. The lightweight consent card appears for Entra-native connections; the ServiceNow connector falls back to the heavier connection-manager dialog unless SSO is engineered [ASSUMPTION: Contoso's ServiceNow is Entra-federated]. For the catalog custom connector, configure **OBO/SSO** fully (API app registration, connector app registration, **Azure API Connections service as authorized client** — the commonly missed step) and test with a **second user**: the maker's own working session proves nothing (the maker-works/user-fails trap). Field caution for UAT: a reported new-experience-on-Teams bug can return the connect/authorize message as tool output instead of data.

## 9. Role of Workflows

**None — deliberately.** Every business action is a *single* connector call: create, get, update, list tickets; search catalog; place order. Wrapping single calls in workflows would add the 100-second synchronous ceiling, the Text/Boolean/Number I/O conversion tax, schema-refresh breakage (`FlowActionBadRequest`), and one more artifact per action — for zero determinism gain, since determinism here lives in the connector action contract and the input bindings. The multi-step sequencing (triage → then create) is judgment: the Skill's job, not a flow's.

**Where a workflow returns:** a manager approval gate (orders above a cost threshold, non-catalog hardware) is a human-in-the-loop wait that *cannot* run inside a synchronous tool (approvals exceed 100 seconds by definition) — it would come back as a workflow via the async continuation pattern (respond early, run the approval after "Respond to the agent," call back via Execute Agent with the conversation ID). Today's catalog is pre-approved standard items, so no gate exists [ASSUMPTION: stated catalog policy].

## 10. Memory decision

**OFF at launch.** Memory is **[PREVIEW]**; it is disabled in group chats and Teams channels anyway (only 1:1 chat would benefit); everything durable here — tickets, orders, asset data — belongs in ServiceNow, the auditable system of record, not a user-private, user-deletable store with a 28-day inactivity TTL; and per-user memory makes the same agent answer differently per user, complicating fixed-persona evals.

**How to test the difference:** run the fixed benchmark suite against two otherwise-identical agents (Memory on/off). For the ON agent, seed context ("I use a Surface Laptop 6, Amsterdam office"), then measure in later sessions: (a) does triage skip redundant device questions (turn-count delta), (b) pass-rate delta on the standard suite (drift check), (c) latency delta. Promote Memory only if (a) improves with no regression on (b)/(c) — and after the preview flag clears.

## 11. Connected Agents decision

**No.** One audience (employees), one security boundary (Entra + ServiceNow ACLs), 6 tools — far under the 25–30-tool quality budget. Troubleshooting, tickets, and orders are not separate specialist domains; they are one service-desk agent with one Skill ("often those are not three agents"). Each delegation would add an orchestration hop (latency) and another audit/publishing surface. Revisit only if a genuinely different boundary appears (a facilities agent over a different tool estate) or tool growth degrades selection accuracy.

## 12. Evaluation plan

Test sets in the **Evaluate tab** (single-response ≤100 cases; conversational ≤20 cases × 6 Q/A pairs), versioned with the agent source; run against the **draft** before every publish via the Evaluation API in CI (delegated-auth token in Key Vault), threshold-gated.

- **Expected answers (25):** top KB issues → Compare-meaning vs gold answers; custom grader requires a citation to the named KB source.
- **Unsupported questions (10):** HR/payroll/personal — polite refusal + redirect (custom grader: compliant/noncompliant).
- **Ambiguity (10):** "my laptop is broken" — expect clarifying triage questions; no Create Incident in the plan before confirmation (conversational set).
- **Wrong-tool activation (15):** "status of INC0012345" must hit Get Incident, not List or Create; "order a mouse" must hit Search Catalog first — asserted via Copilot Studio Kit **Plan validation** plus activity-trace review.
- **Skill activation (10):** problem reports must load the triage Skill; status/order requests must not. Fix misfires by tightening the description, not the instructions.
- **Hallucination resistance (10):** nonexistent KB topic, fake ticket number — expect "not found"/escalation, never invented steps or fabricated states; general knowledge disabled.
- **Edge cases (10):** ticket-number typos, quantity 0/999, closed-ticket update, zero open tickets, consent-card first run (manual UAT, second user, in Teams).

**Side-effect isolation:** eval runs really execute tools — point connections at the ServiceNow **sub-production instance** and a catalog sandbox, or every run files real tickets. Budget eval credits like load tests: smoke set per PR, full set nightly.

**Regression triggers (re-run full suite):** any instruction, tool-description, Skill, or model change; KB restructure; connector schema change; every environment promotion; monthly scheduled run via the Copilot Studio connector. Feed each production misroute from the Monitor tab back in as a new case.

## 13. Risks and mitigations

- **[PREVIEW] ServiceNow Knowledge real-time connector** — prerelease docs, subject to change. Mitigation: SharePoint KB is primary; the ServiceNow source drops out without redesign.
- **[PREVIEW] Evaluate-tab surface in the new experience** (pages still preview-labeled even though platform agent evaluation went GA 2026-03-31): keep the Kit/Direct Line layer as the second net. **[PREVIEW] Memory** and **[PREVIEW] workflow-as-tool** — deliberately not used. **Harness GA'd 2026-08-03, but treat status per feature, not per experience.**
- **Probabilistic confirm-before-write:** the "echo fields and confirm" rule is instructions, i.e., best-effort. Mitigations: ServiceNow-side validation/ACLs as the hard layer; minimally scoped write tools; eval cases asserting no unconfirmed writes; per-tool "require approval before run" is [STATUS UNVERIFIED] in sources — verify in-product, adopt if real.
- **Prompt injection via KB content:** a poisoned KB article could steer tool use. Instructions are not a security boundary — enforcement is end-user auth (blast radius = the user's own permissions), DLP on connectors, KB write-access governance.
- **Teams end-user-auth bug** (consent message returned as tool output — community-reported): UAT in Teams with fresh users; document the connection-manager fallback for helpdesk.
- **Cost/credit risk:** harness agents are **always billed, including design time** — building, previewing, and evals burn Copilot Credits before launch, no M365 Copilot license offset. Mitigations: agent-level monthly limit with alert threshold; Deny enforcement on the maker environment, deliberate posture on production (stop-at-limit takes the desk offline — an availability trade-off); nightly not per-commit full evals; PPAC monitoring plus `isCLIAgent` inventory. Variable loop iterations make per-conversation cost less predictable than scripted topics — watch Monitor against the credit meter for the first month.
- **Governance:** end-user creds keep results permission-trimmed, and this design already complies with the wave 1 forced-end-user-credentials policy. All six tools sit under DLP/ACP with per-action granularity (the benefit MCP would have cost us). ALM: agent + Skill in a solution, custom connector in its own solution, managed export, pipeline promotion, evals pre-export and post-import.

## 14. Verdict

**The new design is genuinely simpler — for this Agent + Tools shape, dramatically so.** ~35 authored artifacts drop to 11 (~69%); ~185 hand-tuned routing signals (140 trigger phrases + 45 branches) collapse into 7 descriptions plus a lean instruction block; 5 flow wrappers (~40 actions) vanish because every business action was always a single API call that the flows merely chaperoned. Maintenance shifts from re-balancing trigger phrases to editing descriptions, with the Evaluate tab as the regression harness classic never had.

**Where it is NOT better, honestly:** (1) **Rich UI** — the classic catalog card carousel has no confirmed new-experience equivalent yet; catalog browsing degrades to text until rich-UI parity ships. (2) **Determinism at the write boundary** — classic Question/Condition gates *guaranteed* a confirmation step; here it is probabilistic instructions backed by tool config and ServiceNow validation. Acceptable for pre-approved catalog items and standard incidents; the moment a real approval gate or a multi-write transaction (order + asset assignment + ticket link committing together) enters scope, that piece must become a deterministic workflow (async continuation for approvals) — deterministic spine, agentic edges. (3) **Cost predictability** — scripted topic runs metered flat; the agentic loop's iteration count varies, and billing now starts at design time. The simplification is real, but it is bought with description discipline, eval rigor, and credit governance — all three now first-class engineering artifacts, not afterthoughts.
