# Exercise 10: Humongous Pharma Regulatory Affairs Assistant

## 1. Business need

Humongous Pharma's Regulatory Affairs (RA) team needs an assistant over controlled SOPs and regulatory submission records. Non-negotiables, because GxP compliance review applies: every answer cites its source; no speculation beyond the controlled corpus; every interaction logged for audit; authorized RA users only; and any action — the flagship being creation of a change-control record — requires human approval and deterministic execution. The design question is not "how agentic can we make it" but "how little probabilistic surface can we get away with."

## 2. Classic-style architecture

In classic Copilot Studio (Standard harness, generative orchestration off or tightly scoped), this would be a scripted estate:

**Topics (12):** (1) Greeting & Disclaimer; (2) Authentication Gate (condition branches on group membership); (3) SOP Question — generative answers node, "search only selected sources" over the SOP library; (4) Submission Status Lookup — question nodes + flow call; (5) Glossary/Definition; (6) Change-Control Intake — 8 question nodes with validation branches (change type, affected SOP, justification, markets); (7) Change-Control Confirmation — summary + "Confirm/Cancel" branch; (8) Escalation to RA Lead; (9) Fallback/Unsupported — hard refusal wording; (10) Citation Formatter — `OnGeneratedResponse` topic with Power Fx over `System.Response.Citations` forcing page-level citations; (11) Audit Logger — fires after every answer, calls a flow; (12) End of Conversation/CSAT.

**Agent flows (5):** Audit Log Writer (Dataverse audit table); Submission Status Lookup (RIM/Dataverse); Create Change-Control Record — multistage approval on the async continuation pattern, since approvals blow the 100-second synchronous limit; Approval Callback (Execute Agent, correlated by `System.Conversation.Id`); Escalation Notification.

**Glue:** ~35 condition branches, ~28 topic/global variables, ~15 Power Fx expressions, 9 hand-maintained trigger-phrase sets. Total: **12 topics + 5 flows + ~35 branches + ~28 variables**. It works and audits well — and every new question type is another topic, every wording change a redeploy.

## 3. New-experience redesign

Minimal new-native architecture on the GitHub Copilot harness (GA 2026-08-03; several sub-features still preview — flagged below):

- **Instructions (~600 words):** identity ("regulatory affairs assistant over controlled documents"), grounding-only rule (general knowledge disabled; answer solely from configured knowledge, always cite, state "not found in the controlled corpus" otherwise), refusal scope (no interpretation of regulations, no advice on circumventing procedures, no speculation), escalation trigger to RA Lead, and the tool-use rule: "Change-control record creation happens only through the Create Change-Control Record workflow, never by any other means."
- **Knowledge (2 sources):** (a) SharePoint SOP library via the SharePoint/Work IQ connector path — chosen specifically because it authenticates as the user and permission-trims results; sensitivity labels honored. Explicitly **not** uploaded files (see §6). (b) Dataverse submissions table — end-user auth means Dataverse row-level security applies per user.
- **Skills (1):** `change-control-intake` — description: "Use when the user wants to create, prepare, or submit a change-control request against an SOP or submission. Handles the initial request and every follow-up refinement in the same task. Do not use for informational questions about the change-control process." Contains the intake checklist (required fields, validation rules, the confirmation-summary step) and soft-points at the workflow tool.
- **Tools (2):** the **Create Change-Control Record workflow** exposed as a tool [PREVIEW — workflow-as-tool]; and a **Dataverse List Rows connector tool** for submission status — deterministic, complete result sets rather than top-N knowledge retrieval, with per-action DLP governance (a deliberate reason to avoid MCP here: no platform-enforced per-tool DLP for MCP).
- **Workflows (1):** Create Change-Control Record — deterministic canvas: validate inputs → write draft record to Dataverse → multistage human approval (async continuation: respond to the agent within 100 s, dehydrate on the approval, call back via Execute Agent with `System.Conversation.Id`) → finalize record → notify QA. Same input always produces the same output.
- **Memory: OFF.** Connected agents: none. **Model:** GPT-5.5 Chat (GA primary model). Anthropic models are deliberately excluded: they run on Anthropic-hosted infrastructure outside Microsoft-managed environments and the standard DPA — a subprocessor sign-off this GxP review does not need.
- **Platform shell (config, not agent components):** *Require Microsoft authentication* environment policy [PREVIEW]; DLP allowing only the SharePoint and Dataverse connectors; Application Insights (sensitive-logging toggle decided by data protection); transcript retention/export pipeline (§13); eval suite as CI gate (§12).

## 4. Removed components

| Component | Classic | New | Delta |
|---|---|---|---|
| Topics | 12 | 0 | −12 (routing → orchestrator; refusal/citation policy → instructions) |
| Flows/workflows | 5 | 1 workflow (+1 notification step inside it) | −3 to −4 |
| Condition branches | ~35 | ~6 (inside the workflow only) | −29 |
| Variables / Power Fx | ~28 / ~15 | 0 (no variables in the new model) | −43 |
| Trigger-phrase sets | 9 | 0 | −9 |
| Skills | 0 | 1 | +1 |
| Knowledge sources | 2 (node-scoped) | 2 (agent-level) | 0 |
| Tools | 0 (flows via topics) | 2 | +2 |

Net: **~100 authored artifacts collapse to ~7 configured components.** What disappears entirely: trigger phrases, the citation-formatting `OnGeneratedResponse` topic (no equivalent exists — see §14), the audit-logger topic (replaced by platform transcripts + App Insights), and the intake question-node tree (replaced by generative slot-filling under the Skill's checklist).

## 5. Role of Instructions

In: always-true policy only — identity, grounding-only + mandatory citation rule, refusal boundaries, escalation trigger, the single cross-cutting tool rule. Short (every token bills every turn on the harness), positively framed, structured with headings.

Deliberately NOT in: the change-control procedure (situational → Skill); SOP content or policy text (→ Knowledge); any security enforcement. Instructions are probabilistic — prompt-injection research shows instruction-level guardrails can be reasoned around — so nothing that *must never happen* relies on them. Authorization lives in the auth policy and end-user-credential tools; the approval lives in the workflow. Instructions raise the bar; the platform enforces it.

## 6. Role of Knowledge

The RBAC decision is the heart of this design. **Uploaded files have no RBAC** — every agent user gets answers from all uploaded content. For access-restricted SOPs that is disqualifying, so the corpus stays in SharePoint behind the connector/Work IQ path, where retrieval runs on behalf of the user: no permission, no answer; sensitivity labels honored. Caveats accepted: tenant graph grounding needs ≥1 M365 Copilot license in the tenant (else 7 MB file cap), and grounded responses bill ~12 credits vs ~2. General knowledge and web search are disabled — Bing egress leaves the enterprise boundary. Knowledge answers "what does SOP-041 say"; it is *not* used for "list all open submissions" (top-N truncation silently drops rows) — that is the List Rows tool. Honest limitation: the orchestrator may consult any attached source for any query — source scoping is prioritization, not isolation. With two sources both in-scope for all authorized users, acceptable; it would not be if sources with different audiences shared one agent.

## 7. Role of Skills

One skill, not zero: the change-control intake is genuinely situational, procedural, and too long for always-on instructions. Its description is routing metadata (states when *not* to fire, claims follow-ups). It contains no script — no computation is needed — just the checklist and the pointer to the workflow tool. No other skills: the temptation to add a "citation formatting" skill is resisted because a skill *guides* rather than guarantees, and citation presence is enforced by evals + human process instead. The skill is reviewed like code in ALM (skills travel in solutions) — a GxP-friendly property.

## 8. Role of Tools

Two, both connector-framework, both end-user credentials so results respect the user's actual permissions and every call stays inside DLP. No MCP (no per-tool DLP granularity, dynamic tool drift is an uncontrolled change under GxP change management), no REST API tools [PREVIEW], no computer use. The workflow tool's description states plainly: "Creates a change-control record after human approval. Never use for questions about the process."

## 9. Role of Workflows

The deterministic spine. Record creation is irreversible and compliance-critical, so it is rule-based end-to-end: validation, the Dataverse write, the multistage approval, notification. The agent only gathers inputs and invokes; it cannot vary the execution path. The 100-second synchronous wall forces the async continuation pattern for the approval — a feature here, not a bug: the approval *should* be out-of-band, and the dehydrated flow waits for days at no cost. Workflow-as-tool is [PREVIEW] — the single most load-bearing preview dependency in this design (mitigation in §13).

## 10. Memory decision

**OFF.** Memory is preview, per-user, invisible to makers, user-deletable, and auto-expires after 28 days of inactivity — the exact opposite of an auditable record. A GxP system of record cannot include a store the QA auditor cannot inspect and the user can silently erase. Anything durable (the change-control record itself) goes through the workflow into Dataverse. There is also no personalization need that justifies per-user behavioral drift, which would undermine eval reproducibility.

**How to test the difference:** run the fixed eval suite twice against a clone with Memory ON, seeding user preferences in a prior conversation ("always answer briefly, skip citations"), then verify the OFF-configuration agent's answers are identical across users and sessions while the ON clone drifts — demonstrating to the compliance reviewer that OFF is the reproducible configuration.

## 11. Connected Agents decision

**None.** One audience (authorized RA users), one security boundary, two knowledge sources, two tools — far below any context-saturation threshold (25–30 tools). Splitting adds orchestration hops, latency, a second audit surface, and per-delegation metering ambiguity for zero domain benefit. Connected agents would also pass conversation history across an agent boundary — a data-flow the GxP review would have to assess for nothing. Revisit only if a genuinely separate domain (e.g., pharmacovigilance, different audience and ACLs) must join; that would be a second agent, not a merged one.

## 12. Evaluation plan

Evals are a compliance control here, not a quality nicety — the pass record is audit evidence.

**Test set design** (single-response set, 100-case cap; conversational set for the intake journey, 20-case cap):
- **Expected answers (30):** known SOP questions with gold answers; *Compare meaning* method plus a **custom grader** labeling responses "compliant/noncompliant" on two binary checks: citation present, and no content beyond the cited source.
- **Unsupported questions (15):** speculation bait ("Can we skip stability testing for EU batches?"), out-of-corpus topics — expected behavior is refusal + escalation offer; graded by custom grader, dealbreaker threshold 100%.
- **Hallucination resistance (10):** questions about non-existent SOPs ("What does SOP-999 say?") — must answer "not found," never fabricate.
- **Ambiguity (10):** underspecified asks ("what's the status?") — must ask a clarifying question, not guess.
- **Wrong tool activation (10):** hypotheticals near the workflow ("what would happen if I created a change control?") — the workflow must NOT fire. Verified with Copilot Studio Kit **Plan validation** (tools in the dynamic plan), since the built-in judges score text, not tool choice.
- **Skill activation (10):** phrasing variants of "I need to raise a change control" must load `change-control-intake` (activity trace assertion); informational process questions must not.
- **Edge cases (15):** superseded SOP versions, permission-trimmed access tested **with a second user** who lacks SharePoint access (the maker's own session is not evidence), mid-intake abandonment, approval-callback correlation.

**Regression triggers:** any change to instructions, skill, knowledge, tool descriptions, or **model** re-runs the full suite. CI gate: Evaluation REST API in Azure DevOps against the **draft** agent, threshold-gated merge (100% on dealbreaker graders, ≥95% overall), JUnit output archived. Caveats managed: delegated-auth-only API (dedicated service account, refresh token in Key Vault, scheduled runs so it never idles past 90 days); 89-day result retention (CSV export to Dataverse for the GxP record); and eval runs consume credits and execute real tools — the CI environment uses test-double connections, never production Dataverse.

## 13. Risks and mitigations

- **[PREVIEW] Workflow-as-tool** — the approval spine rides a preview feature. Mitigation: the underlying trigger/response contract is shared with GA agent flows; keep the flow importable to a Standard-harness agent as fallback; verify the Learn banner before each release.
- **[PREVIEW] "Require Microsoft authentication" admin policy** (June 2026) — the authorization backstop. Mitigation: pair with DLP blocking "Chat without Entra ID authentication" and channel restriction to Teams/M365; enforcement is retroactive, so inventory before flipping.
- **[PREVIEW] Evaluate-tab surfaces in the agents experience**, SharePoint-lists knowledge, Microsoft IQ — the first is core to the compliance story; export results externally so evidence survives product change. Memory [PREVIEW] is OFF.
- **[GOVERNANCE] Audit completeness — the hardest problem.** Transcripts write ~30 minutes after inactivity, default retention is 30 days, responses grounded in sensitive-labeled SharePoint content are *excluded by design*, the assembled prompt is never exposed, and how completely harness runs (skill loads, sandbox activity) land in `ConversationTranscript` is [STATUS UNVERIFIED]. Mitigation: extend the retention job; a Fabric/Synapse export pipeline with its own retention and access policy (avoid building a shadow PII archive); App Insights (up to 730 days) as the second plane; Bot Transcript Viewer granted sparingly, four-eyes for live access; and document to QA that transcripts are *not* a complete verbatim record — if the regulator requires one, that gap is an explicit validation-file decision, not an assumption.
- **[GOVERNANCE] Injection and trust surfaces.** SOPs are controlled documents, but any future third-party skill is untrusted code — review mandated; MCP excluded partly for this reason.
- **[COST] Credits from the first maker keystroke.** Harness agents bill at design time, and eval suites bill like load tests. Mitigation: dedicated maker environment with agent-level limits and Deny enforcement; production limit set from expected volume — noting stop-at-limit takes the agent *offline*, so alerts route to a named owner, not just tenant admins. Graph-grounded answers at ~12 credits/response are budgeted, not discovered.

## 14. Verdict

The knowledge half of this agent is a genuine, quantifiable win for the new experience: 12 topics, 9 trigger-phrase sets, ~35 branches and ~43 variables/Power Fx artifacts collapse into one instruction sheet, two permission-trimmed knowledge sources, and one skill — with better answers, native citations, an activity trace, and a built-in eval harness classic never had. The compliance shell, however, is exactly where the new experience must *not* be trusted with the work: the approval and record write stay in a deterministic workflow; authorization stays in the platform auth policy and end-user-credential tools; audit stays in transcripts + App Insights + an export pipeline, honestly documented as incomplete; Memory stays off. Two things the new experience still cannot do at all: guarantee verbatim SOP wording (the summarization pass cannot be removed, and the classic `OnGeneratedResponse`/custom-search defeat patterns have no harness equivalent — we mitigate by citing page-level links instead of quoting), and provide a fixed, scripted conversation path if the validation plan demands one. A team whose QA insists on scripted dialog and complete verbatim logging should keep the classic agent — no conversion path exists in either direction, so this is a build decision, not a migration. For everyone else: agentic surface for retrieval and drafting, deterministic spine for anything a regulator will ever ask about.
