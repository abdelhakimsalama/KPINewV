# Exercise 07: Adventure Works Executive Assistant

Architectural emphasis: **Microsoft IQ + Memory** — how far the new experience gets with *almost no custom components*.

## 1. Business need

Adventure Works executives (M365 Copilot-licensed, authenticated, 1:1 chat in Teams/M365 Copilot) want a personal agent that: (a) briefs them on their day (calendar, urgent mail, overnight Teams activity); (b) summarizes email threads and Teams discussions they missed; (c) drafts replies in their personal style; (d) remembers per-user preferences — briefing format, priority projects, writing tone. Everything is scoped to the *signed-in user's own data*; nothing is shared across users.

## 2. Classic-style architecture

In classic Copilot Studio (Standard harness) this is a large build, because every capability needs a topic, every data fetch needs a flow, and every preference needs maker-managed state:

**Topics (11 custom):** `Daily Briefing` ("brief me", "what's my day", ~10 trigger-phrase variants), `Email Catch-Up`, `Summarize Thread` (Question node to disambiguate which thread), `Teams Catch-Up`, `Draft Reply` (Question nodes: recipient, tone, length), `Set Preferences` (branching per preference type), `View Preferences`, `Update Priority Projects`, `Reset Preferences`, `Escalate/Fallback`, `Greeting`.

**Power Automate agent flows (6):** `GetCalendarToday`, `GetUnreadPriorityMail` (Office 365 Outlook connector), `GetTeamsActivity` (Graph via custom connector — missed-channel-message retrieval is genuinely hard), `ReadUserPreferences`, `SaveUserPreferences` (Dataverse), `ComposeBriefing` — each squeezed under the 100-second / Text-Boolean-Number tool contract.

**State:** 1 Dataverse table `ExecPreferences` (userId, briefingFormat, tone, priorityProjects) — maker-visible personal data with its own retention/GDPR obligations; ~15 global variables; ~25–30 condition branches; ~20 Power Fx expressions; 2 AI Builder prompts (`SummarizeThread`, `DraftInTone`).

**Rough count: ~55 authored artifacts** (11 topics + ~40 trigger phrases + 6 flows + 1 table + 2 prompts + variables/branches). And the classic build still does permission-trimmed retrieval badly — every mailbox/calendar call is a hand-wired connector action.

## 3. New-experience redesign

Agent on the **GitHub Copilot harness** (GA 2026-08-03; several sub-features below remain preview):

- **Instructions (lean, ~1,200 chars):** identity ("You are a personal executive assistant for the signed-in user only"), tone, scope/refusals, grounding rule ("answer only from the user's own work data via Work IQ; say so when you find nothing"), drafting policy ("always produce drafts; never send"), and one memory rule ("apply remembered briefing format, tone, and priority projects; when a preference is stated, confirm and remember it").
- **Microsoft IQ [preview]:** **Work IQ** enabled with **Mail, Calendar, Teams, OneDrive** toggled on; User Profile + Microsoft 365 Copilot Search come on by default. This is the entire data layer: permission-trimmed, identity-scoped, dynamic. Requires an M365 Copilot USL per user and admin consent for WorkIQAgent.Ask; write operations (draft creation into Outlook) only if the admin enables writes — otherwise the agent returns draft text in chat.
- **Knowledge sources: none.** Everything the agent needs is user-scoped and dynamic — exactly what Work IQ provides and what pre-enumerated knowledge sources cannot. (Optional later: one SharePoint source for the corporate comms style guide, [preview] in the new experience.)
- **Skills (1):** `daily-briefing` — SKILL.md holding the briefing procedure (section order, prioritization rules, "priority projects first", length budget). Routing description: "Use when the user asks for their daily/morning briefing or an overview of their day. Handles the initial request and follow-up refinements to the same briefing. Do not use for single-thread summaries or drafting replies." Summarize/draft need no skill — the model does both natively under instructions.
- **Tools: none custom.** Work IQ supplies retrieval and (if enabled) drafting actions.
- **Workflows: none.** No approvals, no transactions, no scheduled runs in scope (see §14 for the scheduled-briefing caveat).
- **Memory [preview]: ON** — replaces the Dataverse table, both preference topics, both preference flows, and all preference variables. Per-user, platform-managed, maker-invisible.
- **Connected agents: none** (§11).
- **Model:** GPT-5 Auto — routes between fast chat and deep reasoning per request; briefing composition benefits from reasoning, "summarize this thread" doesn't. An Anthropic model is defensible for drafting quality but adds a governance decision (processing outside Microsoft-managed environments); not justified here.

**Total: instructions + 1 IQ configuration (4 source toggles) + 1 skill + Memory toggle + model choice ≈ 5 authored components.**

## 4. Removed components

| Component | Classic | New | What disappears |
|---|---:|---:|---|
| Custom topics | 11 | 0 | Orchestrator plans from instructions + skill description |
| Trigger phrases | ~40 | 0 | Description-based routing |
| Power Automate flows | 6 | 0 | Work IQ handles retrieval; no aggregation flow needed |
| Dataverse tables | 1 | 0 | Memory (per-user, platform-managed) |
| Global variables | ~15 | 0 | No variable concept in the new harness; Memory + conversation history |
| Condition branches | ~25–30 | 0 | Reasoning loop |
| AI Builder prompts | 2 | 0 | Native model capability under instructions |
| Skills | 0 | 1 | Briefing procedure, loaded on demand |
| Knowledge sources | 0 | 0 | — |
| **Total** | **~55** | **~5** | **~90% reduction** |

## 5. Role of Instructions

**In:** identity and single-user scope; tone; the draft-don't-send rule; grounding/empty-result behavior; the one cross-cutting memory rule; refusal boundaries (no answering about other people's mail beyond what the user's own permissions surface — note this is *enforced* by Work IQ permission trimming, instructions just set expectations).

**Deliberately NOT in:** the briefing template (situational → skill); user preferences (per-user state → Memory); any data or facts (Work IQ); tool-by-tool routing hints (Work IQ source descriptions carry that); security enforcement (instructions are probabilistic — the CAT rule "if you need a 100% guarantee, use code" applies; here the guarantees come from permission trimming and the admin write-toggle, not prose). Instructions load in full every turn and every token bills every turn — leanness is a cost and adherence feature.

## 6. Role of Knowledge

Deliberately empty, and that is the architectural point of this exercise. Knowledge is *content you explicitly add*; Microsoft IQ is *context that flows dynamically from the signed-in user*. An executive's day cannot be pre-indexed: their mail, calendar, and chats are per-user, permission-trimmed, and minutes fresh. Adding SharePoint/file knowledge here would only add cost and routing noise. The trade to acknowledge: tenant-graph-grounded responses bill ~12 credits vs ~2 for ordinary knowledge — Work IQ is the expensive retrieval tier, justified because nothing cheaper can answer these questions at all.

## 7. Role of Skills

One skill, `daily-briefing`, because the briefing format is a *situational procedure* — a template that applies only when a briefing is requested and would bloat always-on instructions otherwise (the two-question placement test: not inferable from descriptions; not true in every conversation → skill). Its description explicitly claims follow-ups ("make it shorter", "lead with the board meeting") so it doesn't drop out mid-task — a documented stickiness failure mode. Summarization and drafting stay skill-less: they are native model behaviors steered by instructions plus remembered tone; wrapping them in skills would be migration archaeology.

## 8. Role of Tools

None. Every classic flow existed to *fetch or persist* something: fetching is Work IQ's job, persistence is Memory's. The only candidate tool — "send the reply" — is deliberately excluded: sending email on an executive's behalf is an irreversible action that should stay with the human (the agent drafts; the user sends, or the admin-gated Work IQ write action creates an Outlook draft the user reviews). Zero tools also means zero connector consent friction and zero DLP surface beyond Work IQ itself.

## 9. Role of Workflows

None. There is no multi-step deterministic sequence, no approval, no transaction, and no cross-system side effect in scope. If a scheduled 7 a.m. push briefing is later required, that *is* a workflow/trigger job (deterministic schedule → agent node) — flagged in §14 as the boundary where the pure-conversational design stops.

## 10. Memory decision

**ON.** This scenario is Memory's documented design center: repeat, authenticated, 1:1 users whose preferences should persist. **Remember:** briefing format, writing tone, priority projects, VIP senders, preferred summary length. **Never remember (route elsewhere or nowhere):** commitments, approvals, delegated decisions, anything compliance-relevant — memories are user-deletable, maker-invisible, and auto-expire after **28 days of inactivity**; Memory must never be a system of record. Privacy model is a feature for this persona: the maker cannot read an executive's memories; the user can ask "what do you remember about me?", correct or delete in chat, or wipe via the memory portal. Constraint to design around: **Memory is off in group chats and Teams channels** — publish guidance must say the assistant personalizes only in 1:1 chat.

**Testing ON vs OFF:** because memories are per-user and maker-invisible, a fixed-persona eval can't see personalization — run it as an experiment. Two identical agent copies (Memory ON / OFF) against dedicated test accounts with seeded mailboxes. Conversational test sets: session 1 states a preference ("five bullets, projects first"); a later session requests a briefing with nothing restated. Custom grader: "reflects the previously stated format unprompted → pass." Compare pass rates and turn counts (ON should eliminate re-asking; OFF quantifies the extra turns/credits of amnesia). [ASSUMPTION] The Evaluate tab can drive genuinely separate conversations under one test identity so cross-conversation persistence is exercised; if not, fall back to scripted sessions or Copilot Studio Kit multi-turn runs via Direct Line.

## 11. Connected Agents decision

**No.** One audience, one security boundary (the user's own M365 data), three closely related tasks — the canonical "one agent with a skill, not three agents" case. There is no specialist domain, no reuse across parents, no separate team ownership, and no tool-overload signal (zero tools). Delegation hops would add latency and a second orchestration bill for nothing. Revisit only if a genuinely different boundary appears (e.g., a finance-data specialist over Fabric IQ owned by another team).

## 12. Evaluation plan

Work IQ answers are user- and time-dependent, so **exact-match expected answers are mostly unusable**; the suite leans on custom graders and structural checks against seeded test accounts.

- **Expected answers (~30 single-response cases):** seeded mailbox/calendar; graders check structure and grounding ("briefing lists all 4 seeded meetings", "summary names the decision and owner"); Compare meaning where phrasing varies.
- **Unsupported questions (~10):** "What's on the CFO's calendar?", "Show me Dana's inbox" → refuse/explain permission scope, never fabricate; "book the flight" → decline as out of scope.
- **Ambiguity (~10):** "Catch me up" (mail? Teams? both?), "summarize the thread" with three active threads → one clarifying question, not a guess.
- **Wrong-source activation (~8):** activity-trace checks that calendar questions don't fan out into mail search or M365 Copilot Search (cost control at ~12 credits per tenant-graph response).
- **Skill activation (~8):** briefing requests fire `daily-briefing` (trace-verified); "summarize this email" must NOT; follow-ups stay inside it. Misfires → fix the description before touching instructions.
- **Hallucination resistance (~8):** empty calendar → "nothing scheduled", no invented meetings; project with zero matching content → says so.
- **Edge cases (~8):** back-from-3-weeks-leave backlog (summary stays bounded); contradictory preference update; memory-wiped user; non-English thread.
- **Memory experiment** (§10) as a separate conversational suite.

**Regression triggers (full re-run):** any instruction/skill edit; **any model change** (summarization and citation behavior demonstrably vary by model); Memory or any Work IQ source toggled; monthly scheduled run (platform drift); pre-publish via an Evaluation REST API gate in CI (delegated-auth token in Key Vault). Budget it — eval runs burn real credits against the priciest retrieval tier.

## 13. Risks and mitigations

- **[PREVIEW] Memory** — behavior, quotas, and admin controls may change; no confirmed tenant kill-switch for Copilot Studio agent memory. *Mitigation:* nothing durable lives only in Memory; document the 28-day wipe; re-verify status before rollout.
- **[PREVIEW] Microsoft IQ / Work IQ in Copilot Studio** — this agent's entire data layer is preview inside a GA harness. *Mitigation:* small exec pilot; don't decommission the alternative until it passes; per-feature status check each release.
- **[PREVIEW] Evaluate surfaces** in the agents experience still carry preview labels. *Mitigation:* keep a Kit/Direct Line test path as a harness-independent second layer.
- **[GOVERNANCE] Exec mail/calendar content transits conversation context and transcripts** — maximum-sensitivity PII. *Mitigation:* Bot Transcript Viewer granted to almost no one, four-eyes access, App Insights sensitive-logging OFF, employee-only environment with *Require Microsoft authentication*.
- **[GOVERNANCE] Write actions:** Work IQ is read-only unless an admin enables writes — keep writes off initially; drafts returned in chat.
- **[LICENSING] M365 Copilot USL per user** required for Work IQ, plus WorkIQAgent.Ask admin consent. Fine for execs; blocks any "everyone" rollout without a licensing decision.
- **[COST] Tenant graph grounding ≈12 credits/response**, billing from the first maker preview, evals on the expensive tier. *Mitigation:* agent-level monthly limit + alert threshold in PPAC from day one; maker-dev environment off tenant-pool draw; `isCLIAgent` inventory monitoring.
- **[BEHAVIORAL] Memory recall is model-mediated, not guaranteed.** *Mitigation:* the §10 experiment sets a measured floor; users correct in chat.
- **[EDGE] 28-day inactivity deletion** (a sabbatical returns to an amnesiac assistant) and no group-chat personalization. *Mitigation:* user-facing docs; the agent re-learns quickly by design.

## 14. Verdict

This is close to the best case for the new experience: **~55 authored components collapse to ~5**, and — the exercise's point — the two components doing the heavy lifting (Work IQ, Memory) are *configuration, not construction*. The classic build's hardest problems (permission-trimmed retrieval across four M365 workloads; per-user preference storage with privacy obligations) simply stop being the maker's problems: the platform owns retrieval, trimming, storage, retention, and user privacy controls. Almost no custom components are needed because nothing in this scenario is a system action, a transaction, or shared organizational fact — it is all *user-scoped context plus judgment*, which is exactly instructions + IQ + Memory.

Where the new design does **not** win, and what stays deterministic: (1) **sending email** — kept out of the agent; draft-only is the approval gate, and if auto-send is ever demanded it belongs in a workflow with explicit human approval, not in instructions; (2) **a scheduled morning push** — the conversational agent can't wake itself; that needs a workflow trigger invoking the agent; (3) **preference guarantees** — Memory is probabilistic recall with a TTL; anything that must never be forgotten or must be auditable needs a Dataverse tool, reintroducing a classic-style component by design; (4) **cost predictability** — classic per-flow metering was flat; an agentic loop over 12-credit retrievals is variable, so governance limits are the compensating control. Bottom line: adopt the new design, flag the data-and-memory layer as preview-dependent, and hold draft-only as the one non-negotiable deterministic boundary.
