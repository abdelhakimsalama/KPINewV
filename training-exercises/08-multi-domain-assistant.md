# Exercise 08: Globex Employee Front-Door Assistant

Architecture focus: **Primary agent + Connected Agents** on the GitHub Copilot harness (harness GA 2026-08-03; several sub-features still preview — flagged inline).

## 1. Business need

Globex (40,000 employees) wants ONE Teams entry point — "Ask Globex" — for HR, IT support, Finance/expenses, and Facilities. Each domain is owned by a different department with its own knowledge estate, line-of-business tools (Workday, ServiceNow, SAP Concur, a booking system), its own security/permission boundaries, and its own release cadence. Employees should never need to know which department owns their question; departments must be able to ship changes without coordinating a shared release train.

## 2. Classic-style architecture

Classic Copilot Studio would build either one mega-bot or a Bot Framework skill mesh. The realistic mega-bot:

- **Topics: ~48.** Per domain ~10 custom topics — HR: `Leave Balance`, `Leave Request`, `Benefits Enrollment`, `Payroll Dates`, `HR Policy Q&A` (generative answers node); IT: `Password Reset`, `Ticket Status`, `New Laptop Request`, `Software Install`, `Outage Check`; Finance: `Submit Expense`, `Expense Status`, `Per-Diem Lookup`, `Corporate Card`; Facilities: `Desk Booking`, `Badge Access`, `Maintenance Ticket`, `Office Info` — plus customized system topics (Greeting, Fallback, Escalate, Multiple Topics Matched, End of Conversation) and 2 hand-built router/disambiguation topics ("Did you mean HR leave or Facilities leave-the-building access?").
- **Trigger phrases: ~480** (10+ per topic), continuously tuned as misroutes appear.
- **Condition branches: ~140** (eligibility checks, channel checks, entity-filled vs. not, error paths).
- **Variables: ~18 global** (user UPN, department, office, ticketId, expenseId…) plus per-topic locals, wired with Power Fx for formatting and slot passing.
- **Power Automate flows: 14** — `CreateServiceNowIncident`, `GetIncidentStatus`, `ResetPasswordRequest`, `GetLeaveBalance` (Workday), `SubmitLeaveRequest`, `GetExpenseStatus` (Concur), `SubmitExpenseWithApproval`, `GetPerDiemRates`, `BookDesk`, `CreateMaintenanceTicket`, `RequestBadgeAccess`, `EscalateToHelpdesk`, `NotifyApprover`, `LogCSAT`.
- **Composition tax:** the four-department alternative was Bot Framework skills (4 registrations, app registrations, manual slot filling) or topic redirects — either way one solution, one publish pipeline, so an HR trigger-phrase tweak redeploys IT's bot.

Rough total: **48 topics + 480 trigger phrases + 140 branches + 18 globals + 14 flows + 4 skill registrations ≈ 700 hand-maintained routing/logic artifacts.**

## 3. New-experience redesign

**One primary agent + four Copilot Studio connected agents**, all in the **same environment**, each **published**, each **opted in** to "allow connections from other agents", each named **under 30 characters** [OFFICIAL constraint set]: `Ask Globex` (primary), `Globex HR`, `Globex IT Support`, `Globex Finance`, `Globex Facilities`.

**Ask Globex (primary / front door)**
- *Instructions (summary):* identity/tone; **single-voice rule** ("you are the only agent that speaks to the user; combine specialist findings into one response"); delegation policy ("delegate domain questions to the matching connected agent; ask one clarifying question when two domains plausibly apply; never answer HR/IT/Finance/Facilities policy from general knowledge"); escalation to human helpdesk; out-of-scope refusals (personal legal/medical/financial advice).
- *Knowledge:* 1 SharePoint source — enterprise-wide FAQ (holiday calendar, office locations, "who owns what"). Nothing domain-specific.
- *Skills:* 1 — `new-hire-onboarding-concierge` ("Use when a manager or new hire asks about onboarding, first-day setup, or joiner tasks; orchestrates HR, IT, and Facilities requests in sequence; do not use for a single-domain question"). Cross-domain journeys are the front door's only real logic.
- *Tools:* 1 — `EscalateToHelpdesk` workflow (creates a triage ticket when no specialist matches).
- *Connected agents:* the four specialists, routed purely by **description** (see §11).
- *Memory:* **ON** [PREVIEW] — per-user preferences only (home office, preferred language).
- *Model:* fast high-throughput class (GPT-5 Auto-style) — the front door mostly routes; every delegation already adds a hop, so keep planning cheap.

**Specialists** (each owned, versioned, and published by its department):
- `Globex HR`: knowledge = HR SharePoint (permission-trimmed) + Dataverse policy table; tools = 5 Workday connector actions + `SubmitLeaveRequest` workflow; skill `leave-eligibility-triage`; Memory OFF.
- `Globex IT Support`: knowledge = ServiceNow Knowledge real-time connector [PREVIEW]; tools = 6 ServiceNow actions + `PasswordReset` workflow; skill `incident-triage-playbook`.
- `Globex Finance`: knowledge = T&E policy SharePoint; tools = 5 Concur actions + `ExpenseSubmission` workflow (approval-gated, async pattern); skill `expense-audit-precheck`; sandbox code for per-diem/proration math (exact math in code, never model arithmetic).
- `Globex Facilities`: knowledge = SharePoint list of buildings/desks [PREVIEW] + facilities guide; tools = 4 (booking connector, `CreateMaintenanceTicket` and `BadgeAccess` workflows, floor-map file tool).

All five agents' instructions include the paired discipline: specialists carry "you are a specialist invoked by Ask Globex; return findings, do not address the user directly" [OFFICIAL multi-agent pattern].

Totals: 5 instruction sets, 7 knowledge sources, 4 skills, ~22 tools (incl. 6 workflows), 4 routing descriptions, Memory on 1 agent.

## 4. Removed components

| Component | Classic | New | What disappears |
|---|---:|---:|---|
| Topics | 48 | 0 | routing + dialog trees → orchestrator + descriptions |
| Trigger phrases | ~480 | 0 | replaced by 4 connected-agent descriptions + skill/tool descriptions |
| Condition branches | ~140 | ~10 (inside workflows) | branching only where determinism is required |
| Global/topic variables | 18+ | 0 | no variables in the harness; conversation history + Memory + typed workflow I/O |
| Power Automate flows | 14 | 6 workflows | only transactional/approval sequences survive as deterministic tools |
| Bot Framework skill registrations | 4 | 0 | connected agents: no app registrations, no manual slot plumbing |
| Router/disambiguation topics | 2 (+ system topic tuning) | 0 | planner disambiguates; instructions define the clarifying-question policy |

Net: ~700 routing/logic artifacts → **~40 described components**. What does *not* disappear: the 6 deterministic workflows and their approval gates.

## 5. Role of Instructions

**In (front door):** single-voice rule; delegation and clarifying-question policy; grounding rule ("domain answers only via specialists or the enterprise FAQ; if nothing matches, say so and offer escalation"); tone; escalation triggers. **In (specialists):** subagent role, "return findings to the parent", domain-scope boundaries, citation policy.
**Deliberately NOT in:** domain procedures (→ Skills), policy text (→ Knowledge), per-tool routing hints already carried by good descriptions, exact wording or calculations (instructions are probabilistic — CAT's tested finding), and security rules (instructions are not an enforcement boundary; enforcement lives in connector auth, DLP, permission-trimmed sources). Keep each set lean: every instruction token is loaded and billed every turn.

## 6. Role of Knowledge

Knowledge follows ownership: each specialist carries only its department's sources, so **the agent boundary is also the knowledge/security boundary** — the only hard isolation the platform offers (source scoping is prioritization, not isolation). HR content stays on permission-trimmed SharePoint (uploaded files have no RBAC — disqualified for HR). IT uses the ServiceNow real-time connector [PREVIEW] for always-fresh KB answers. Front door holds a single small enterprise FAQ. No agent approaches the >25-source GPT pre-filtering threshold; each stays at 1–2 well-described sources, which keeps retrieval routing trivial.

## 7. Role of Skills

Skills carry situational procedures *inside* the owning boundary: leave-eligibility triage, incident-triage playbook, expense-audit precheck, and the front door's cross-domain onboarding concierge. Each description is routing metadata with explicit when-NOT-to-use clauses and follow-up ownership ("handles the initial request and follow-up refinements"). The skill-vs-agent rule is applied both ways: procedures for the same audience inside one boundary are Skills, not more agents — which is precisely why HR is one agent with skills, not three agents (§11).

## 8. Role of Tools

Combined, Globex needs ~22 tools. In a single agent that already crowds the **25–30 recommended** band (hard cap 128) and would keep growing — the documented signal to split. Distributed, each specialist holds 4–7 tools: a small, coherent decision space per orchestrator. The front door holds exactly one tool (escalation), so its planning problem is almost purely "which specialist". End-user credentials on all connectors so results respect the caller's permissions; no maker-credential write tools.

## 9. Role of Workflows

Everything transactional or approval-gated stays deterministic: `ExpenseSubmission` (multi-stage approval — inherently exceeds the **100-second synchronous wall**, so it acknowledges fast, dehydrates, and calls back via Execute Agent with `System.Conversation.Id`), `SubmitLeaveRequest`, `PasswordReset`, `BadgeAccess`, `CreateMaintenanceTicket`, `EscalateToHelpdesk`. Same input → same output, flat 13-credits/100-actions metering, auditable run history. Workflow-as-tool is [PREVIEW]. The LLM never improvises a financial transaction or an access grant.

## 10. Memory decision

**ON for Ask Globex only; OFF for all specialists.** Rationale: the front door owns the user relationship (preferences: office, language, preferred summary style); specialists answering through the single voice would fragment personalization and multiply preview surface. Memory is [PREVIEW], per-user, disabled in group chats/Teams channels (fine — "Ask Globex" is a personal Teams app), auto-expires after 28 days, and is never the system of record (requests are persisted via workflows into ServiceNow/Concur/Workday).
**Testing the difference:** paired eval runs — the same 30-case routing/answer set executed (a) memory-off, (b) memory-on after a scripted seeding conversation ("I work in the Berlin office") — comparing routing decisions and answer deltas via the activity map; plus multi-session conversational sets verifying the seeded fact is applied ("book me a desk" → Berlin) but never distorts domain routing; plus a forget-test ("forget my office") verified in the memory portal.

## 11. Connected Agents decision

**Yes — and this is one of the rare scenarios where all four documented justifications hold simultaneously:**
1. **Ownership/ALM cadence:** four departments publish independently; the parent depends only on each callee's description + contract, not internals. HR can ship weekly while Facilities ships quarterly.
2. **Knowledge/security boundaries:** genuinely different corpora and permission models per domain — the inverse of the anti-pattern ("one knowledge source → don't split").
3. **Tool-count pressure:** ~22 tools and growing vs. the 25–30 guidance; per-agent 4–7.
4. **Reuse:** `Globex HR` is also planned as a specialist behind a future Manager Assistant — connected agents (not child agents) are the reuse construct.

**Constraints designed in:** all five agents in the **same environment** (departments build in their own dev environments and promote via managed-solution pipelines into the shared prod environment — an ALM consequence of the same-environment rule); callees **published** before connection; callee-side **opt-in** enabled and reviewed at publish (an opted-in agent is an internal API); every name **< 30 characters** or the connection fails. Delegation is **description-driven**: e.g., `Globex Finance`: "Expense reports, reimbursement status, per-diem and corporate card questions for Globex employees. Do not use for payroll dates or salary questions (HR) or for purchasing hardware (IT Support)." Descriptions are written as a set — mutually exclusive, with cross-references — because vague/overlapping descriptions are the documented cause of misrouting and double answers.

**Latency:** every delegation adds an orchestration hop and the callee runs its **own full orchestration** — budget roughly one extra planning cycle per hop. Mitigations: flat hub-and-spoke, delegation depth 1, no specialist connects onward; fast model on the parent; monitor end-to-end latency against the observed ~120 s Teams timeout.

**Counter-case — why NOT 8 (or 12) agents:** splitting HR into Payroll/Benefits/Leave, or Facilities into Booking/Maintenance, fails every justification: same owner, same knowledge boundary, same cadence — those are **Skills** inside one agent. A desk-booking API is a **tool**, not an agent — a specialist must *reason* over its domain to earn agent status. Extra agents add hops (latency), audit surface, five more eval suites, and [STATUS UNVERIFIED] possibly double credit metering per delegated turn. Four is the floor the org chart forces and the ceiling the architecture tolerates.

## 12. Evaluation plan

Five test assets, each owned by the team that owns the agent; the front-door team owns the routing suite (the "contract test" across teams).

- **Routing suite (front door):** 100-case single-response set; each case asserts the *delegation target*, verified via activity-map-linked results and Copilot Studio Kit **plan validation** (right connected agent/tool in the plan), not just answer text. Includes: clean single-domain asks; **ambiguity** cases ("I need leave" → clarifying question expected, not a guess; "expense my new laptop" → Finance, not IT); **cross-domain** onboarding cases (skill activation asserted); **unsupported questions** ("what's Globex's stock price?", "should I sell my shares?" → decline + no delegation); **wrong-tool traps** (a question answerable from FAQ must not trigger escalation workflow).
- **Per-specialist suites:** expected answers with groundedness/compare-meaning graders; **hallucination resistance** (questions whose answer is absent from knowledge → "not found" + escalation offer, custom grader labels compliant/noncompliant); **skill-activation** checks (leave-eligibility skill fires for eligibility, not for payroll); workflow-invocation checks against sandboxed test connections (evals execute real tools — point them at test doubles; eval runs consume credits, budget them like load tests).
- **Multi-turn sets** (20 cases, ≤6 Q/A pairs): follow-up stickiness, memory on/off pairs (§10), context retention across a delegation.
- **Regression triggers:** any change to a connected agent's *description* (a breaking change to the routing table), any model change on any of the five agents, tool additions, instruction edits, monthly scheduled drift run. CI: Evaluation API gate in Azure DevOps against draft agents, pass-rate threshold blocking merge (delegated-auth token in Key Vault); post-deploy re-run in the target environment.

## 13. Risks and mitigations

- **[PREVIEW] "Add a connected agent" in the new experience** — the core pattern rides a preview surface even though multi-agent orchestration is GA on the platform side. Mitigation: pin behavior with the routing suite; verify page-level status before go-live.
- **[PREVIEW] Workflow-as-tool, Memory, SharePoint-lists knowledge, ServiceNow real-time connector** — each individually degradable: fallbacks are classic agent-flow tools, memory-off, static SharePoint pages.
- **Misrouting / double answers** — description overlap is the known failure mode. Mitigation: description authoring as a governed, jointly-reviewed artifact; single-voice instructions on all five agents; routing suite as merge gate.
- **Governance:** conversation history crosses the agent boundary on delegation — acceptable intra-tenant here, but all five agents inherit DLP; the PPAC **Connected Agents** environment toggle is a kill-switch to account for in DR planning; callee opt-in reviewed at each publish; per-agent transcript/analytics ownership assigned per department or incident tracing becomes archaeology.
- **Cost/credit:** harness agents bill **from design time** (build/preview/eval) — set per-agent monthly limits + alerts in PPAC for all five, dev-environment allocations for four departments; delegated turns may meter on **both** parent and callee orchestration [STATUS UNVERIFIED — validate with consumption analytics before scaling to 40k users]; eval suites and the routing gate are recurring spend.
- **Latency:** hop cost + specialist tool calls can approach the ~120 s Teams timeout (observed, not documented) — monitor P95 end-to-end, keep delegation depth at 1.
- **[ASSUMPTION]** Typed input/output contracts for connected agents work parity in the new harness UI (documented for the Standard harness via YAML) — validated in a spike before committing to structured returns.

## 14. Verdict: why the new design is simpler — or where it is NOT and what must stay deterministic/classic

Simpler, decisively, on routing and ownership: ~700 hand-tuned artifacts (48 topics, ~480 trigger phrases, ~140 branches, 18 variables, 4 skill registrations) collapse to ~40 described components and 4 routing descriptions, and — the real win — four departments get independent ALM instead of one shared release train. That is what connected agents are *for*, and this scenario legitimately triggers all four decomposition criteria.

Where it is NOT simpler: (1) **determinism didn't get cheaper — it moved.** Six workflows still carry every approval gate, transaction, and exact value; the expense approval still needs the async continuation pattern to survive the 100-second wall. None of that should ever be delegated to the loop. (2) **Routing quality is now prose.** Trigger phrases were tedious but inspectable; descriptions are terser but every edit is a behavioral change, so the eval suite is not optional QA — it is the routing table's compiler check. (3) **Cost and latency predictability regress:** variable reasoning iterations, design-time billing, possible double metering per hop, and an extra planning cycle per delegation. A pure classic build would still be defensible for a shop that needs fixed per-conversation cost and scripted compliance dialogs — but for four owners behind one front door, the primary-plus-connected-agents design is the smaller, more honest system.
