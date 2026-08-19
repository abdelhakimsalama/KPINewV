# Exercise 09: Litware Order Tracking & Logistics Agent

**Architectural emphasis: REST/connector/MCP integration.** Fictional project; platform facts as of 2026-08-19 (GitHub Copilot harness GA 2026-08-03 per MC1446644; many sub-features still preview). Every preview feature used is flagged.

## 1. Business need

Litware's B2B customers and internal logistics reps ask: "Where is order 4711?", "Why is my shipment late?", "Redeliver tomorrow", "Change the delivery address", and (reps only) "Re-route this shipment to the Hamburg DC." All data lives behind an internal REST API estate (OpenAPI specs for Orders, Addresses) and a logistics MCP server (track/trace, shipment events, proof-of-delivery documents). Re-routing a shipment is **irreversible** once the carrier accepts it; re-delivery and address changes are state-changing and time-window-constrained. Users are authenticated: reps via Entra ID; B2B customers via Entra External ID guest accounts [ASSUMPTION — anonymous customer access is explicitly out of scope; see §13].

## 2. Classic-style architecture

In classic Copilot Studio (Standard harness) this is a topic-and-flow machine:

**Topics (13):** Greeting & identity check; Order Status Lookup; Shipment Tracking; Delay Diagnosis; Multiple-Order Disambiguation; Re-delivery Request; Address Change; Shipment Re-route (rep-only, condition branch on `Global.UserRole`); Order Not Found recovery; Escalation & Handoff; Unsupported-Request Deflection; Fallback; End of Conversation/CSAT. Each triggered topic carries ~10 trigger phrases (**~90 total**), Question nodes for slot filling (order number, address, date), Power Fx validation (order-number regex, cutoff-time checks), and Adaptive Cards (5) for status display and Yes/No confirmation. The Re-route topic alone needs a 3-step confirmation ladder: restate shipment → show consequences card → explicit Yes branch → call flow.

**Power Automate agent flows (6):** F1 GetOrderDetails, F2 GetTrackingEvents (reads via custom connector), F3 RequestRedelivery, F4 ChangeDeliveryAddress (write + address-validation call), F5 RerouteShipment (write, approval logic), F6 CreateEscalationTicket. Two **custom connectors** wrap the Orders and Logistics APIs. State rides in **9 global variables** (CustomerId, UserRole, OrderId, ShipmentId, TrackingNumber, SelectedAddress, ConfirmationState, CarrierCode, EscalationId); **~30 condition branches** and **~15 Power Fx expressions** encode eligibility (shipped vs. not shipped, cutoff windows, role checks).

**Component count: ~170 authored artifacts** (13 topics + 6 flows + 2 connectors + ~90 trigger phrases + ~30 branches + ~15 Power Fx + 9 variables + 5 cards). Every new carrier exception code or eligibility rule means editing branches in multiple topics.

## 3. New-experience redesign

One agent on the GitHub Copilot harness. Components:

- **Instructions (~1,400 chars, always in context):** role ("Litware order-tracking and logistics assistant for authenticated B2B customers and internal reps"); tone; scope + refusals (no pricing, no order placement, no data about other customers' orders); grounding rule ("answer policy questions only from the Logistics Policy Library; cite"); cross-cutting tool discipline ("always resolve the order via *Get Order Details* before any shipment action; never fabricate order or tracking numbers; when logistics tools return resource links, pass **resource IDs** between tools and read a resource only when its content is needed to answer"); the one always-true safety line ("never invoke a write tool without the user's explicit confirmation of the specific order and action, in this conversation"); escalation triggers.
- **Knowledge (2 sources):** (1) *Logistics Policy Library* — SharePoint (Work IQ path, permission-trimmed): delay policies, re-delivery eligibility, SLA docs. (2) *Carrier & Exception-Code Reference* — uploaded files (non-sensitive; uploaded files have no RBAC, so nothing access-restricted goes here).
- **Skills (2):**
  - `delay-diagnosis-playbook` — description: "Use when a user asks why a shipment is late, delayed, stuck, or missed its ETA. Sequence: get tracking events from the Logistics MCP tools, interpret exception codes using the Carrier Reference, check the Policy Library for the applicable SLA, then offer re-delivery only if eligible. Handles the initial question and every follow-up refinement in the same diagnosis. Do not use for simple 'where is my order' status checks."
  - `irreversible-action-protocol` — description: "Use whenever a re-delivery, address change, or shipment re-route is requested. Do not use for read-only questions." Body: restate order/shipment and exact consequence; state irreversibility for re-routes; obtain explicit confirmation; invoke the matching write tool or workflow exactly once; report the returned reference number; claims follow-ups.
- **Tools (7 callable surfaces — well under the 25–30 budget):**
  1. **Litware Logistics MCP server** (MCP is GA; Streamable HTTP) — dynamically discovered read tools (`get_shipment_status`, `get_tracking_events`, `get_delay_details`, `list_shipments_for_order`, `get_proof_of_delivery`). Large payloads (event histories, POD PDFs) are returned as **`resource_link` references**; the agent passes resource IDs between tools and calls `resources/read` only on demand — protecting the context window. "Allow all" is **disabled**; the tool list is pinned. Auth: OAuth 2.0 via the auto-generated custom connector with OBO (Entra has no DCR, so manual app registration).
  2. **"Litware Orders" custom connector** (OBO/SSO, end-user credentials) — 5 actions: *Get Order Details*, *Search Orders* (reads), *Request Redelivery*, *Update Delivery Address* (writes; both require a client-supplied **idempotency key**), *Reroute Shipment* (write; exposed only to the workflow, and its DLP-blockable as an individual action).
  3. **Address Validation REST API tool** [PREVIEW] — built directly from the service's OpenAPI **v2** spec, API-key auth, strictly read-only.
- **Workflow (1):** *Execute Shipment Reroute* [PREVIEW — workflow-as-tool] — deterministic sequence: re-validate shipment state and reroute window server-side; derive idempotency key from `conversationId + shipmentId`; call *Reroute Shipment*; return typed confirmation (Text/Boolean/Number contract; completes well inside the 100-second wall — no human approval inside the synchronous call).
- **Memory: OFF** (§10). **Connected agents: none** (§11).
- **Model:** GPT-5.5 Chat (GA) — high-throughput conversational work; a Claude model would require the Anthropic-subprocessor governance sign-off for customer PII, and any model switch re-runs the eval suite.

## 4. Removed components

| Component | Classic | New | Delta |
|---|---|---|---|
| Topics | 13 | 0 | −13 |
| Trigger phrases | ~90 | 0 | −90 |
| Condition branches | ~30 | 0 authored (logic → API/workflow) | −30 |
| Power Fx expressions | ~15 | 0 | −15 |
| Global variables | 9 | 0 (conversation history + tool outputs) | −9 |
| Flows / workflows | 6 | 1 | −5 |
| Custom connectors | 2 | 1 (+1 MCP-generated) | −1 authored |
| Adaptive cards | 5 | 0 (rich UI in new experience still maturing) | −5 |
| Instructions / skills / knowledge | 0 / 0 / 0 | 1 / 2 / 2 | +5 |
| REST API tool | 0 | 1 [PREVIEW] | +1 |
| **Total authored artifacts** | **~170** | **~13** | **≈ −92%** |

What disappears: all routing scaffolding (trigger phrases, disambiguation topic — generative orchestration handles multi-intent and slot filling), all conversation-state plumbing, and 5 of 6 flows (reads become direct tool calls; writes move to connector actions with API-side enforcement). What does **not** disappear: the custom connector, the one deterministic workflow, and every server-side validation.

## 5. Role of Instructions

In: identity/scope/tone, refusal boundaries, grounding and citation policy, the resolve-order-first rule, the resource-ID-passing rule, the one-line confirmation rule, escalation triggers — things true in every conversation. **Deliberately NOT in:** the delay-diagnosis procedure and the confirmation protocol details (situational → Skills); eligibility rules and cutoff windows (enforced in the API/workflow — instructions are probabilistic and are never the enforcement layer); policy text (Knowledge); restating what well-described tools already convey. Instructions are billed every turn and adherence degrades with length — keep them lean.

## 6. Role of Knowledge

Knowledge answers "what is the policy / what does exception code X mean," never "what is the status of order 4711" — live transactional data always comes from tools. SharePoint (Work IQ) gives per-user permission trimming for policy docs; uploaded files hold only non-restricted reference content (no RBAC on uploads). Two sources keep orchestrator source-selection trivial (no >25-source GPT filtering hop). The instructions' merge rule ("policy from knowledge, facts from tools") is the CAT MCP-data-plus-knowledge-corrections pattern.

## 7. Role of Skills

Two skills carry the situational procedures that would otherwise bloat instructions: the diagnosis playbook (fires only on delay questions) and the irreversible-action protocol (fires only on write requests). Descriptions are routing metadata with explicit when-not clauses and follow-up ownership (skills can silently drop out on follow-ups otherwise). No scripts bundled — there is no local computation worth codifying here; the sandbox has no network egress, so API work cannot live in skill scripts anyway.

## 8. Role of Tools

Tools are the exercise's core trade:

- **MCP server for the read bundle.** MCP is GA; the logistics team ships one server for Copilot Studio, VS Code, and other MCP clients; tool updates propagate automatically; and **resources** solve the large-payload problem (event histories/POD as resource links, IDs passed between tools). Costs accepted: **DLP is whole-server** — no platform per-tool control — and **descriptions are not maker-editable**. Both are tolerable because every MCP tool is read-only.
- **Custom connector for all writes.** Writes need exactly what connectors give and MCP does not: **per-action DLP/ACP granularity** (an admin can block *Reroute Shipment* in a customer-facing environment while leaving reads open), **maker-editable descriptions and input configuration** (orchestration tuning: "Do NOT use for tracking questions"), and a frozen tool surface — no dynamic drift on write capability. Auth is OBO/SSO (consent card, tokens never maker-visible), so every write executes as the actual user with their API-side permissions; maker credentials on write tools are an anti-pattern and admins can now block them (2026 wave 1).
- **REST API tool [PREVIEW] for the thin, low-risk endpoint.** Fastest path from the OpenAPI spec (v2; v3 auto-converts), API-key auth. Because an API key is a shared credential (every user runs with the same privilege) it is confined to read-only address validation. If reuse across agents or Power Automate emerges, graduate it to a custom connector — the mature vehicle.
- **No overlap rule:** reads live only on MCP, writes only on the connector, so the orchestrator never chooses between duplicate tools with uneditable MCP descriptions.

## 9. Role of Workflows

One workflow exists because re-routing is irreversible: the deterministic spine (re-validate state, enforce the reroute window, mint the idempotency key, single API call, typed result) must not be improvised by the LLM. Confirmation is layered: conversational confirmation (skill-guided, probabilistic) → workflow re-validation (deterministic) → API idempotency + eligibility checks (authoritative). Per-tool "require approval before run" in the new experience is [STATUS UNVERIFIED], so nothing relies on it. No human-approval step sits inside the synchronous call (100-second wall); if Litware later requires supervisor sign-off for re-routes, that becomes the async continuation pattern (respond early, approve out-of-band, call back via Execute Agent with the conversation ID).

## 10. Memory decision

**OFF.** Memory [PREVIEW] is per-user, user-deletable, 28-day TTL, and model-mediated. Order data must always be fresh from systems of record, and the worst failure mode is real: a "remembered" delivery address silently influencing an address-change action. Personalization value (preferred carrier, format preferences) is marginal for this workload. **Test:** clone the agent, toggle memory on, run the conversational eval set twice per variant across two sessions — seed session 1 with an address change, then in session 2 request another change and grade whether the memory-on agent ever pre-fills or asserts the old address instead of re-querying *Get Order Details*; also compare answer freshness on status questions. Any pre-fill is a fail; keep OFF unless the memory-on variant shows measurable benefit with zero stale-data incidents.

## 11. Connected Agents decision

**None.** One domain, one audience boundary (authenticated Litware order data), and ~7 tool surfaces — far below the 25–30 tool budget where orchestration degrades. The specialists here are APIs, not reasoning agents; wrapping a single API call in an "agent" is a named anti-pattern. Revisit only if a genuinely separate domain with its own security boundary arrives (e.g., a finance/invoice-dispute agent owned by another team) — then connect it rather than absorbing its tools, accepting the extra orchestration hop.

## 12. Evaluation plan

Write tools point at a **sandbox order environment** during evals — evaluation runs really execute tools.

**Single-response set (≤100 cases), built in the Evaluate tab** ([PREVIEW] labels persist on agents-experience eval pages; the underlying capability is GA since 2026-03-31):
- *Expected answers (25):* seeded test orders — status, ETA, tracking events; graded with Compare Meaning + a custom grader asserting the correct order number appears verbatim.
- *Unsupported questions (10):* pricing, placing orders, another customer's order → must refuse/redirect (custom "compliant-refusal" grader).
- *Ambiguity (10):* "where's my order?" with 3 open orders → must ask which, or list, never guess (grader: no fabricated order ID).
- *Wrong tool activation (15):* delay questions must not trigger the reroute workflow; address *validation* questions must not call *Update Delivery Address*; status checks must use MCP reads, not connector writes — asserted with Copilot Studio Kit **Plan validation** through Direct Line.
- *Skill activation (10):* "why is it late?" fires `delay-diagnosis-playbook`; "track order 4711" fires neither skill — verified in the activity trace/reasoning view.
- *Hallucination resistance (10):* nonexistent order numbers, requests for tracking numbers the API doesn't return → must report not-found, never invent identifiers.
- *Edge cases (10):* already-delivered shipment re-delivery request; reroute after carrier cutoff (API rejects → agent must relay the rejection, not retry); MCP resource link to an oversized event history (agent must summarize via resource read, not dump).

**Conversational set (≤20 cases, ≤6 Q/A pairs)** for the confirmation gate: decline paths (user says no → sandbox API records **zero** calls), confirm paths (exactly **one** call — idempotency verified by asserting the API call count), mid-flow order switch (confirmation must re-state the new order).

**Regression triggers:** any change to instructions, skill/tool descriptions, or connector schema (refresh the tool; schema drift causes `FlowActionBadRequest`); any model switch; **weekly scheduled run + MCP tool-inventory diff** (the server's surface is dynamically discovered — drift is a supply-chain event, not just a quality event); new production edge cases fed back from Monitor into the set. CI: Evaluation REST API gate on draft agents in a dedicated environment (delegated-auth-only — service-account refresh token in Key Vault).

## 13. Risks and mitigations

- **[PREVIEW] REST API tools** — spec/behavior may change. Confined to one read-only, API-key endpoint; graduation path to a custom connector documented.
- **[PREVIEW] Workflow-as-tool / workflows experience** — GA signals (2026-08-03) conflict with lingering "(preview)" Learn banners; verify the page banner before production sign-off; fallback is a classic agent flow with identical trigger/response contract.
- **[GA, governance gap] MCP whole-server DLP** — allowing the server allows its entire current *and future* tool surface. Mitigations: read-only server by design; "Allow all" disabled and tools pinned; server owner treated as a governed supply chain (change notification required); admins can still block the whole server per environment.
- **MCP descriptions not editable** — routing tuned via the no-overlap rule and instructions, not description edits; if the server ships a confusing tool, disable it individually.
- **Instructions are probabilistic** — the confirmation gate is defense-in-depth: skill protocol → workflow re-validation → API idempotency keys and eligibility checks. The guarantee lives server-side, never in prose.
- **Auth traps** — OBO's most-missed step (Azure API Connections as authorized client) makes SSO work for the maker and fail for user #2: test with a second user pre-rollout. Entra lacks DCR, so MCP OAuth needs manual app registration. Consent cards are expected first-run UX for B2B guests; custom-UI channels must answer them. Field-reported Teams bug: end-user-credential tools returning the auth prompt as tool output — include a Teams smoke test.
- **[COST] Credit exposure** — harness agents bill from the first maker keystroke (build/preview/eval), and the agentic loop's iteration count varies per conversation. Mitigations: agent-level monthly limits with alert thresholds; eval suites budgeted like load tests; **stop-at-limit is itself an availability risk** for a customer-facing agent — production uses alert + PAYG, not Deny.
- **Latency** — chained MCP reads + a workflow call can approach channel timeouts (~120 s observed in Teams); keep tool outputs small (resource IDs), monitor per-step latency in the activity trace/App Insights.
- **Audience boundary** — if truly anonymous customer access is ever required, this design does not stretch: split into a separate environment/agent (classic or locked-down) rather than weakening auth on this one.

## 14. Verdict

The new design removes ~92% of authored artifacts (~170 → ~13): all 90 trigger phrases, all 13 topics, all state plumbing, and 5 of 6 flows disappear because generative orchestration does routing, slot filling, and disambiguation, and because reads become direct tool calls. The integration story is genuinely *better*, not just smaller: MCP resources solve a payload problem classic never solved cleanly, and the connector/MCP split maps governance granularity to risk (per-action DLP exactly where actions are dangerous).

Where the new experience does **NOT** help — and determinism must stay: (1) the reroute execution sequence, eligibility windows, and idempotency live in a workflow and the API, exactly as they would have in classic — that layer shrank but did not vanish; (2) the confirmation UX is *less* deterministic than a classic Yes/No branch — a topic guaranteed the exact confirmation card every time, while the harness agent's phrasing can vary, which is why the enforcement moved server-side and the conversational gate is merely UX; (3) preview surfaces (REST API tools, workflow-as-tool) impose a verify-before-ship tax classic connectors never had; (4) cost per conversation is variable where classic was flat. Net: right architecture for this workload — an API-centric agent whose intelligence is in tool selection and whose safety is in the tools themselves.
