# Exercise 01: Northwind Policies & Procedures Assistant

## 1. Business need

Northwind Manufacturing (12,000 employees) needs an assistant that answers HR policy, safety procedure, and internal documentation questions, grounded in ~800 SharePoint documents spread across 6 sites, in English and German. The risk asymmetry is explicit: a wrong answer about a safety procedure (lockout/tagout, PPE, machine operation) is worse than no answer. The design goal is therefore **conservative grounding**: answer only from approved sources, cite everything, refuse gracefully, escalate to a human owner when unsure. This is a pure knowledge-retrieval agent — no transactions, no records written, no approvals.

## 2. Classic-style architecture

On the Standard harness this would have been a topic-and-flow build:

- **12 topics**: Greeting (customized Conversation Start); Language Detection (condition branches setting `Global.UserLanguage`); HR Policy Q&A (generative answers node scoped to the 2 HR sites); Safety Procedures Q&A (generative answers scoped to the safety sites, plus a mandatory disclaimer Message node fired deterministically before every answer); Internal Documentation Q&A; Safety Escalation (EHS contact card); HR Escalation; customized Fallback (capture unanswered question, call logging flow); tuned Multiple Topics Matched; End of Conversation/CSAT; an `OnGeneratedResponse` citation post-processing topic (Power Fx parsing `<page_X>` markers into `#page=N` deep links); Reset.
- **~150 trigger phrases** — roughly 15 phrases × 5 user-facing topics, duplicated for English and German.
- **~18 condition branches** (language forks in every Q&A topic, empty-result checks, disclaimer routing, confidence gates).
- **~10 variables** (`Global.UserLanguage`, search results, last citation, escalation flags) and **~12 Power Fx expressions** (citation formatting, language literals).
- **2 Power Automate agent flows**: "Log unanswered question" (append to a SharePoint list) and "Escalate to HR/EHS" (email with transcript snippet).

Total: ~14 structural artifacts (topics + flows) carrying ~200 authored moving parts — most of it routing and language plumbing, not policy behavior.

## 3. New-experience redesign

GitHub Copilot harness agent (GA 2026-08-03), minimal component set:

- **Instructions** (one lean page, always in context): role ("Northwind policies & procedures assistant"), conservative grounding rules, citation policy, refusal + escalation contacts, language behavior, ambiguity handling. Detail in §5.
- **Knowledge — 6 SharePoint (Work IQ) sources** [PREVIEW], one per site, deliberately site-scoped (not per-library) to stay far below the 25-source description-filtering threshold. Each named by business function with a routing-grade description, e.g.:
  - `HR-Policies-DE-EN` — "German and English HR policies: leave, benefits, working time, conduct (Urlaub, Arbeitszeit, Verhaltenskodex). Not for safety or IT topics."
  - `EHS-Safety-Procedures` — "Plant safety procedures: lockout/tagout, PPE, machine operation, incident reporting (Arbeitssicherheit, PSA). The only authoritative source for safety questions."
  - Four more: `Plant-Operations-Docs`, `IT-Internal-Docs`, `Quality-Compliance-Docs`, `Facilities-Site-Info`.
- **Skills: none at launch** (§7; one deferred candidate defined there).
- **Tools: none** (§8). **Workflows: none** (§9). **Connected agents: none** (§11).
- **Memory: OFF** (§10).
- **Model**: a GA chat-class model (GPT-5.5 Chat per the current GA lineup) as default; Claude Sonnet 4.6 as evaluated alternative because it emits per-chunk citations (better traceability for safety answers) — contingent on subprocessor governance sign-off, since Anthropic models process outside Microsoft-managed environments. No reasoning-model pinning: high-volume FAQ traffic, latency- and credit-sensitive.
- **Agent settings (hard toggles, not prose)**: general knowledge OFF, web search OFF — the agent can only answer from the 6 sources. Tenant graph grounding ON (tenant holds M365 Copilot licenses, so files up to 200 MB index; without it, SharePoint files over 7 MB are silently skipped — a real gap for large safety manuals).

Eight configured items total.

## 4. Removed components

| Component class | Classic build | New build |
|---|---|---|
| Topics (incl. customized system topics) | 12 | 0 |
| Trigger phrases (EN + DE) | ~150 | 0 |
| Condition branches | ~18 | 0 |
| Variables | ~10 | 0 |
| Power Fx expressions | ~12 | 0 |
| Power Automate / agent flows | 2 | 0 |
| Knowledge sources | 6 (wired per generative-answers node) | 6 (agent-level) |
| Instructions | 1 (shared with topic logic) | 1 (sole behavior surface) |
| Skills / Tools / Workflows / Connected agents | n/a | 0 |
| **Authored moving parts** | **~200 (~14 structural units)** | **~8 configured items** |

What disappears and why: intent routing (orchestrator selects sources from names/descriptions); the entire language-forking layer (the model converses in the user's language — instruction, not topic; cross-lingual *retrieval* remains an eval target, §12); the unanswered-question logging flow (replaced by built-in analytics question lists and analytics-sourced test generation); the citation post-processing topic (accept default citations; no documented `OnGeneratedResponse` equivalent in the new experience — the page-deep-link nicety is **lost**, [STATUS UNVERIFIED]).

## 5. Role of Instructions

Every instruction token is billed on every turn and adherence degrades with length, so this stays under ~1,500 characters, positively framed:

**Goes in (always true, every conversation):**
1. Identity/scope: Northwind HR policy, safety, and internal-docs assistant; decline everything else.
2. Conservative grounding: answer **only** from the knowledge sources; if nothing relevant is found, say so plainly and give the HR or EHS contact — never fill gaps from general knowledge (belt-and-braces with the hard toggle).
3. Safety posture: for safety-procedure questions, quote the procedure's steps closely, always cite the source document, state the document is authoritative and the user must follow it as written, and offer the EHS contact. Never present a partial list of steps as complete.
4. Citation policy: cite every grounded claim.
5. Language: respond in the user's language (English or German); if a source exists only in the other language, say so and cite it anyway.
6. Ambiguity: if a question could span HR vs. safety, or documents conflict across sites, ask one clarifying question or surface both citations and flag the conflict.

**Deliberately NOT in instructions:** any policy text (that's Knowledge); per-source routing hints (the six descriptions carry routing — add hints only if evals show ambiguity); step-by-step response templates for niche scenarios (Skill territory if ever needed); "never do X" pile-ups; and any pretense of security enforcement — instructions are a probabilistic soft layer, not a boundary. Isolation is enforced by SharePoint permissions and the general-knowledge/web toggles.

## 6. Role of Knowledge

Knowledge is the whole architecture. Design decisions:

- **SharePoint (Work IQ) over file upload**: per-user permission trimming and sensitivity-label honoring for free; uploaded files have **no RBAC** (every user would see everything — disqualifying for restricted HR content). Work IQ also rides the M365 tenant semantic index (meaning-based retrieval), avoiding the Dataverse-sync ingestion pipeline whose large-library indexing can take days; freshness follows the M365 index, so annually refreshed policies surface without a re-ingestion project.
- **Six site-scoped sources, not source sprawl**: registering per-library sources could exceed 25, which triggers an internal GPT pre-filtering hop over source descriptions — extra latency and a new misrouting failure mode. At 6 sources, the orchestrator selects directly from descriptions. Description quality is the routing table; each description states what the source covers, in both languages' vocabulary, **and what it does not cover**.
- **Why NO custom retrieval flow**: classic builds bolted on `OnKnowledgeRequested` custom-search topics, Azure AI Search side-cars, or custom-search + AI Prompt pipelines to fix scoping, citations, or verbatim output. None earns its place here: the semantic index handles fuzzy multilingual policy questions; the orchestrator plans retrieval across 6 well-described sources; retrieved files land whole in the sandbox for analysis; and the custom-topic route would reintroduce YAML plumbing plus a 15-snippet cross-topic budget for zero retrieval gain. The one thing custom pipelines bought that we give up is guaranteed verbatim quoting — addressed as a residual risk (§13).
- **Known retrieval limits, instructed around**: knowledge returns top-N, never exhaustive — the agent must never claim a complete enumeration ("all 14 safety procedures"); classic-era "search only selected sources" was prioritization, not isolation, and the new orchestration-driven equivalent must likewise be treated as routing, not a wall — the hard wall is site permissions.

## 7. Role of Skills

**Zero at launch.** The two-question test: conservative grounding, citation, refusal, and safety posture are true in *every* conversation → instructions. The facts are in Knowledge. Nothing situational and procedural remains.

One deferred candidate, added only if evals show global instructions carry the safety protocol inconsistently: `safety-procedure-response` — routing description: "Use for questions about plant safety procedures: lockout/tagout, PPE, machine operation, chemical handling, incident reporting, including all follow-up questions in the same task. Do not use for HR, benefits, IT, or general documentation questions." Its body would hold the heavier answer protocol (step-quoting format, mandatory EHS escalation lines, German phrasing). Keeping it out until evidence demands it keeps context lean and avoids a skill-activation failure mode we would otherwise have to test.

## 8. Role of Tools

**None.** There is no system action: no ticket creation, no record writes, no live data. Escalation is a contact reference in the answer, not an automated handoff. Every omitted tool is one less wrong-activation risk on a safety-critical agent, one less consent/DLP surface, and one less credit meter. If Northwind later wants "log my question with HR," that becomes a single connector tool — a deliberate scope extension with its own eval cases, not part of this design.

## 9. Role of Workflows

**None.** Workflows exist for deterministic multi-step procedures, approvals, and transactions — this agent has none. There is no approval gate, no exact-value computation, no irreversible action anywhere in scope, so the "deterministic spine" this scenario needs is not a workflow: it is the pair of hard platform toggles (general knowledge off, web off) plus SharePoint permissions.

## 10. Memory decision

**OFF.** Reasons: (a) policy and safety answers must be identical for every employee — per-user memory creates answer drift on exactly the content where drift is dangerous; (b) Memory is [PREVIEW]; (c) it is disabled in group chats/Teams channels anyway, a likely deployment surface; (d) 28-day expiry and user-deletability make it useless as anything auditable; (e) evals against fixed personas cannot capture personalized behavior, weakening the regression net.

**How to test the difference**: run the identical single-response and conversational test sets against two otherwise-identical agent versions (Memory on/off) using the Evaluate tab's version comparison; seed the memory-on variant with plausible user context ("I work in the Hamburg plant, I prefer short answers") in prior turns, then measure answer divergence on the safety set with the custom compliance grader. Acceptance rule: any safety-set divergence confirms OFF.

## 11. Connected Agents decision

**None.** One audience (all employees), one security boundary (enforced per-user by SharePoint trimming, not by agent separation), six genuinely related sources. Learn's own guidance applies verbatim: splitting agents over sources that aren't genuinely different domains adds orchestration hops and latency with no value. The classic temptation — an "HR agent" and a "Safety agent" behind a router — would recreate the routing problem the new experience just deleted. Revisit only if the corpus or audience splits (e.g., a works-council-restricted agent with a different security boundary).

## 12. Evaluation plan

Evaluation is where "wrong answers are worse than no answer" becomes enforceable.

**Test sets (Evaluate tab, agent evaluation GA 2026-03-31; new-experience surface pages still preview-labeled):**
1. **Grounded-answer set** (~80 single-response cases, ≤100/set): questions with known answers across all 6 sites, ~40% German. Judges: General quality + Compare meaning against expected answers; plus a **custom grader** `safety-compliance` labeling safety answers compliant/noncompliant (must cite the source; must not state steps absent from the document; must not present partial step lists as complete).
2. **Unsupported-question set** (~25 cases): questions with no source document ("what's the policy on remote work from Spain?" when none exists). Expected: explicit "not found" + correct HR/EHS contact, zero fabricated policy. Custom grader on refusal correctness.
3. **Hallucination-resistance set** (~20 adversarial near-misses): "what's step 6 of the lockout procedure" when there are five; plausible-sounding invented policy names; leading questions embedding false premises ("since gloves are optional on line 3…"). Any invented step or accepted false premise = fail, gating.
4. **Ambiguity set** (~15 cases): questions spanning HR vs. safety; documents that conflict between sites. Expected: clarifying question or dual-citation with conflict flagged.
5. **Cross-language set** (~15 cases): German questions answerable only from English documents and vice versa. This directly covers the [ASSUMPTION] that the semantic index retrieves cross-lingually — the fact base does not document it, so it must be measured, not assumed.
6. **Conversational sets** (20 cases, up to 6 Q/A pairs): follow-up drift, context retention, and the safety posture surviving turn 5.
7. **Wrong activation checks**: no tools/skills configured, so the assertion is *absence* — activity-trace review that answers came only from expected knowledge sources (the trace shows sources consulted per message), and no sandbox improvisation substituted for retrieval. If the deferred safety skill ships, add fires-when-it-should / stays-silent-when-it-shouldn't cases.

**Regression triggers** (re-run full suite): any instruction edit; any model change (citation and summarization behavior are model-dependent); knowledge source add/remove; the annual policy-refresh cycle; monthly scheduled run via the Copilot Studio connector. CI: Evaluation REST API gate on the draft agent (delegated-auth-only — dedicated account, token in Key Vault, note the 90-day refresh-token rot). Export results to CSV (89-day retention) into a trend store. Post-launch, seed new cases from real conversations via analytics-sourced test generation. Budget note: eval runs consume credits like runtime — tier a smoke set per change, full set nightly/weekly.

## 13. Risks and mitigations

- **Verbatim wording is not guaranteed** [structural]. The summarization step cannot be removed, and instruction-only "quote exactly" was CAT's least consistent method. Mitigation: citation-as-authority UX (the document, one click away, is the norm; the chat answer is a guide), hallucination graders as release gates. If legal ever mandates exact in-chat wording, that requirement cannot be met reliably on this harness — see §14.
- **Preview surfaces** [PREVIEW]: SharePoint Work IQ knowledge, the new-experience Knowledge and Evaluate doc surfaces (harness GA'd 2026-08-03, but status must be tracked per feature, not per experience); Memory (unused). Mitigation: pin the design to GA pieces (harness, model, agent evaluation platform), monitor What's-new, re-run evals on platform change.
- **Cross-language retrieval** [ASSUMPTION]: undocumented; covered by eval set 5; fallback is per-language duplicate sources or translated summaries in the corpus.
- **Cost/credit** [GOVERNANCE]: GitHub Copilot harness agents are **always billed in Copilot Credits — including design time — with no M365 Copilot license offset** (unlike the standard harness, where licensed users' Teams usage is zero-rated: a genuine economics argument *against* the new harness at 12,000 users). Tenant-graph-grounded responses have billed at ~12 credits vs. ~2 for other knowledge [rate-card drift — verify current]. Mitigations: PPAC environment allocation, agent-level monthly limit set to **alert, not stop** (stop-at-limit would take a safety assistant offline — an availability incident), consumption review in Monitor, pilot-then-scale rollout.
- **Content poisoning / prompt injection via documents** [GOVERNANCE]: instructions are not a security boundary; a malicious edit to a source document steers answers. Mitigation: tight write-governance on the 6 sites (they are now production configuration), curated libraries only.
- **Permission-trimmed answers differ per user** [by design]: users without site access get refusals; evaluate with personas holding representative permission sets and document the behavior for the helpdesk.
- **Anthropic model choice** [GOVERNANCE]: processing outside Microsoft-managed environments; requires tenant opt-in and DPA review before the citation-granularity benefit is taken.
- **One-way door**: no conversion back to classic; the exit path is a rebuild.

## 14. Verdict

This scenario is the new experience's best case, and the numbers show it: ~200 authored moving parts across 12 topics and 2 flows collapse to ~8 configured items — instructions, six described knowledge sources, a model pick, and a Memory toggle set to off. Everything deleted was routing, language forking, and plumbing; nothing deleted was business behavior. No custom retrieval flow is needed because Work IQ + the tenant semantic index + description-driven orchestration cover scoping, permissions, multilinguality, and large files natively.

Where it is honestly *not* better: (1) the classic build could fire a deterministic disclaimer Message node before every safety answer and force verbatim text via a custom pipeline — the new design replaces both with probabilistic instruction-following plus eval gates, acceptable only because the cited source document remains the authority; (2) per-conversation cost is less predictable and, for an M365-Copilot-licensed workforce, the always-billed harness is likely *more expensive* than a zero-rated standard-harness equivalent — the simplicity is bought, not free; (3) the page-level citation deep-link polish has no documented new-experience equivalent. Nothing in scope demands a workflow or classic topic — there are no approvals, transactions, or exact values — so the deterministic residue lives correctly in hard platform toggles and SharePoint permissions, with the Evaluate suite as the standing enforcement mechanism for the safety posture.

*(Word count: ~2,150)*
