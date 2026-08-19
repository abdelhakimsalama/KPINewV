# new-experience-overview

Research note, compiled 2026-08-19. Claim tags: [OFFICIAL] = documented Microsoft behavior (Learn page or announcement), [CAT] = Copilot Studio CAT blog guidance/practice, [INFERRED] = analyst reasoning from the sources. Status flags noted inline; [STATUS UNVERIFIED] where confirmation failed.

## 1. What it is and how it works

**Definition.** The "new agents experience" in Microsoft Copilot Studio is a redesigned authoring and runtime environment in which you describe an agent in natural language instead of building topic flows. Under the hood it is Copilot Studio running agents on the **GitHub Copilot harness** — the orchestration and runtime layer that also powers GitHub Copilot's agentic experiences [OFFICIAL — Learn `agents-experience/overview` ("Agents powered by GitHub Copilot Harness overview") and `harnesses-overview` ("Choose a harness")]. The docs live in a dedicated URL space, `microsoft-copilot-studio/agents-experience/*`, with page titles suffixed "(new experience)" or "(GitHub Copilot)" — the mixed suffixes suggest a rebranding in flight from "new experience" to harness-based naming [INFERRED from observed Learn page titles].

**The harness concept.** A harness is the runtime and orchestration layer that runs an agent. You pick it at creation time and cannot change it later. Three exist [OFFICIAL — Learn `harnesses-overview`]:
- **GitHub Copilot harness** — powers the new experience: agents (and the new visual **workflows**) for reasoning-heavy, multi-step work.
- **Standard harness** — powers classic rule-based agents (topics/triggers/nodes) and agent flows.
- **Copilot Chat harness** — for extending Microsoft 365 Copilot.

**Authoring surface.** The new experience is a single-page app with four tabs: **Build, Preview, Evaluate, Monitor** [OFFICIAL — Learn `agents-experience/build-overview`, `preview-overview`, `analytics-agent-evaluation-intro`, `authoring-review-activity`]. The **Build tab** has two areas [OFFICIAL — `build-overview`]:
- Center: a **rich-text instructions editor** where you define the agent's role, tone, goals, boundaries, and response style in natural language.
- Right: a **components panel** with seven sections: **Model** (choose the primary AI model), **Microsoft IQ** (connect work context/business data — org emails, calendar, files, Teams messages, people signals), **Skills** (modular, on-demand instruction sets), **Tools** (connectors, MCP servers, REST APIs, workflows), **Knowledge** (SharePoint, uploaded files, websites), **Connected agents**, and **Memory** (per-user persistent context).

**The component model (where behavior lives).** CAT's Technical Deep Dive frames it as: *"every behavior belongs in the smallest component that makes it reliable and inspectable. Instructions carry what's always true, Knowledge the searchable facts, Tools the system actions, Memory the persistent context, Skills the situational procedures, and connected agents the real specialist domains"* [CAT — new-orchestrator-resources post]. Skills follow the **Agent Skills open format** (agentskills.io, originally from Anthropic): a `SKILL.md` with name, description, and instructions, optionally bundling `scripts/`, `references/`, and `assets/` [CAT — modern-mcs-agent-skills post; OFFICIAL — Learn `agents-experience/skills-overview` referenced therein].

**How a request flows through the runtime** [OFFICIAL for the loop shape — Learn `agents-experience/overview` describes a plan → act → observe agentic loop; CAT for the context mechanics]:
1. **User request** arrives (Preview tab chat or a published channel).
2. **Orchestration.** The harness starts a reasoning loop. The agent's **instructions are always loaded in full**; Knowledge sources, Tools, and Skills sit in context **as metadata only** (names + descriptions) [CAT — modern-mcs-agent-skills]. The orchestrator interprets the request against instructions and that metadata.
3. **Selection and action.** Per iteration the agent can: search **Knowledge** (retrieved files land in the sandbox where the agent can open and analyze them whole, not just as snippets [CAT — agent-sandbox post]); **load a Skill's** full instructions/resources when its description matches; call a **Tool** (connector, MCP server, REST API, or workflow); delegate to a **Connected agent**; read/write **Memory**; or **write and run code in the agent sandbox**.
4. **Observe and adapt.** It reads tool/code output, corrects course, and iterates — the "plan → execute → adjust" loop — rather than following a scripted path.
5. **Response.** It composes the answer, optionally returning generated files (Word/Excel/PowerPoint/PDF). Every step is recorded in the **activity trace** for inspection [OFFICIAL — Learn `agents-experience/authoring-activity-trace`; CAT — agent-sandbox post].

**The agent sandbox** is the execution environment: a Copilot-Studio-managed container with a Python runtime, local files, preinstalled libraries, and shell tools. A CAT inventory of an empty agent on 2026-07-21 found **Python 3.12.9**, **99 Python libraries**, **11 built-in tools**, and **8 built-in Skills** [CAT — agent-sandbox post; explicitly noted as changeable]. The sandbox has **no outbound network path** — code cannot call APIs or send email; the only external reach is via configured Knowledge and Tools — and it is **temporary** (files must be returned to the user or saved via a Tool) [CAT — agent-sandbox post]. There is **no `pip install`**; what ships in the container is all you get [CAT — redlining post].

**Which agent types use it.** New-experience (GitHub Copilot harness) agents and the new visual workflows. Classic topic-based agents and agent flows stay on the Standard harness; M365 Copilot extensions use the Copilot Chat harness [OFFICIAL — `harnesses-overview`]. Harness agents are identifiable in Power Platform Inventory by the `isCLIAgent = true` property [CAT — cost-governance post, with the Inventory API query]. Publishing from the new experience covers channels documented at `agents-experience/publication-channels-overview`; publishing Copilot Studio agents to Microsoft 365 Copilot/Teams is GA, with SharePoint and WhatsApp channels added [OFFICIAL — Copilot blog publish announcement; channel-by-channel parity for new-experience agents: STATUS UNVERIFIED].

## 2. When to use it / when NOT to use it

**Use the new experience when** [CAT + OFFICIAL]:
- The work is **reasoning-heavy and multi-step**: many steps, many sources, ambiguous decision points where scripting every path is impractical [OFFICIAL — harness overview positioning].
- The agent must **produce artifacts or compute exactly**: file generation (docx/xlsx/pptx/pdf), data analysis over whole files, deterministic math done in sandbox code rather than "in the model's head" [CAT — agent-sandbox post].
- You need **multi-agent designs** — a parent coordinating specialists (CAT's BlastBox Omega sample: multi-turn reasoning, delegation, real actions, generated deliverables) [CAT — new-orchestrator-resources].
- The task sits inside a **repeatable business process** — fixed templates, routing rules, consistent outputs — where a packaged Skill beats ad-hoc work in Cowork. CAT's rule: no surrounding process → Cowork; a specific process/template/pipeline → Copilot Studio [CAT — redlining post].
- You want **on-demand modularity**: Skills load only when relevant, keeping context lean as capability count grows [CAT — modern-mcs-agent-skills].

**Do NOT use it (Classic topics are still the right answer) when** [CAT + third-party guidance echoing Learn]:
- The conversation must follow a **fixed, auditable, compliance-locked path** — exact question order, validation, scripted branches (Learn's voice-agent guidance: choose deterministic control when the flow must be exact) [OFFICIAL — Learn `guidance/voice-agents-control-conversation`].
- You depend on **topic-level mechanics** that have no new-experience equivalent: trigger phrases, condition nodes, Recognize intent, Power Fx variable logic, message nodes fired at exact points. CAT's topics post shows the leverage of these (CoT logger topics, transcript-capture via input-variable descriptions, Recognize intent as a programmatic orchestrator trigger) — all Standard-harness patterns [CAT — power-of-topics post].
- An **existing classic agent is stable and tested** — there is no conversion path, so an upgrade is a redesign; don't migrate without a reason [CAT — migration-plugin post; OFFICIAL — `switch-experiences`].
- You need capabilities **not yet in the new experience** (see Section 4), or predictable per-conversation cost — the agentic loop's variable number of reasoning/tool iterations makes credit consumption less predictable than scripted topic runs [INFERRED from the billing model + loop behavior].
- **Mixed answer:** deterministic workflows don't disappear in the new model — the recommended pattern is deterministic workflow steps as the guardrail/execution layer around an agentic core (irreversible or compliance-critical actions in workflows, ambiguity to the orchestrator) [CAT-adjacent community consensus; the Workflow Designer is the new-experience home for this — OFFICIAL].

## 3. Classic-experience comparison (what it replaces or simplifies)

| Dimension | Classic (Standard harness) | New experience (GitHub Copilot harness) |
|---|---|---|
| Authoring model | Topics, trigger phrases, node canvas, Power Fx, variables, agent flows | Natural-language instructions + declarative components (Skills/Tools/Knowledge/Memory/Connected agents) |
| Control | Deterministic: you script every path | Orchestrator plans the path; you constrain via instructions/Skills/workflows |
| Situational logic | Topics triggered by intent recognition | Skills loaded on demand by description matching |
| State | Variables (topic/global) | Memory (per-user, cross-conversation) + sandbox files (ephemeral) |
| Automation | Agent flows (Power Automate-style) | Workflows on a visual canvas with agent nodes (Workflow Designer) |
| Code execution | None native (call flows/connectors) | Agent sandbox: Python + shell in a managed container |
| Debugging | Topic checker, test canvas, Activity tab | Activity trace / reasoning view; Preview, Evaluate, Monitor tabs |
| Conversion | — | **None in either direction** [OFFICIAL — `switch-experiences`] |

- **Trade summarized:** Classic trades reasoning quality for deterministic control; the new experience trades exact path control for adaptive reasoning [OFFICIAL — Learn framing via search synthesis; consistent with CAT].
- **Coexistence, not forced migration.** Both experiences run side by side. A homepage **"New experience" toggle** switches the maker UI, and "New classic agent" opens the classic canvas in a new tab without switching [OFFICIAL — Learn `agents-experience/switch-experiences`, "Access standard harness agents and agent flows"].
- **Migration is a redesign.** CAT's `/migrate` command in the experimental [copilot-studio-plugin](https://github.com/microsoft/copilot-studio-plugin) pulls a Standard-harness agent, analyzes capabilities, and *proposes* a new architecture. Guidance: upgrade by **capabilities and outcomes, not components one-for-one** — e.g., in the demo, a classic travel-advice child agent became a *Skill*, "the best fit… not a universal rule." Don't turn every topic into a Skill and every variable into memory ("archaeology with YAML"); requires Power Platform CLI > 2.9.3; treat output as a first draft and re-run evals [CAT — new-orchestrator-resources + migration-plugin-video-demo].
- **Reported gains:** the announcement of the rebuilt studio cites roughly **20% evaluation-performance gain** and close to **50% lower net token consumption** versus the prior orchestration, from stronger instruction adherence and staying on task across recursive multi-step work [OFFICIAL — Microsoft Community Hub announcement "More powerful agents and workflows… Introducing a new harness," via search synthesis; single-source vendor figure, not independently verified].

## 4. Limitations, GA/preview status, licensing notes

**Status — the picture is mixed; sources partially conflict:**
- Learn's new-experience pages (build, preview, evaluate, publish, knowledge, tools) carried **"(preview)"** in their titles and the experience was consistently described as a **production-ready preview** — a preview *supported for production use* under supplemental terms, unlike ordinary public previews [OFFICIAL — Learn `agents-experience/*` titles and status text, observed via search 2026-08].
- Microsoft 365 message center **MC1446644** states the **GitHub Copilot harness in Copilot Studio is generally available as of 2026-08-03** for building agents and workflows [OFFICIAL announcement, read via third-party mirror; exact scope of the GA vs individual features not fully verifiable]. The **Workflow Designer** likewise reached GA on 2026-08-03 [third-party reporting; STATUS UNVERIFIED against a first-party page].
- Reconciliation [INFERRED]: the harness/runtime GA'd in early August 2026 while several *features inside* the experience remain preview and some Learn titles lag. Treat status **per feature**, not per experience. One third-party claim of "GA worldwide June 2026" appears to conflate the Build-2026-era announcement with GA — discount it.
- Feature-level status found: **Memory — preview** [OFFICIAL — Learn `agents-experience/memory-overview` "(preview)"]. **Microsoft IQ** — announced for the new experience Aug 2026; [STATUS UNVERIFIED]. **Model choice**: Claude Sonnet 4.5/4.6, Claude Opus, Claude Sonnet 5, GPT-5.5 Chat GA as primary models (excluding GCC for some); experimental/preview models require an admin environment toggle [OFFICIAL — Learn `authoring-select-agent-model` + What's new, via search].

**Hard limitations (as documented):**
- **No conversion** between experiences/harnesses in either direction [OFFICIAL — `switch-experiences`, `harnesses-overview`].
- **No topics.** The workaround for structured conversations — a Skill carrying conversation-structure instructions — "may not work for some complex scenarios" (as of June 2026) [third-party citing Learn; consistent with CAT].
- **Sandbox:** no network egress, no `pip install`, ephemeral storage; Memory stores facts, **not files** [CAT — agent-sandbox + redlining posts].
- **Skills are per-agent** (as of June 2026): they travel with the agent through solutions/ALM; no in-product cross-agent catalog yet (one is being worked on; the community CAT Agent Skills gallery fills the gap externally) [CAT — modern-mcs-agent-skills].
- **Evaluate tab** at launch lacked some classic test methods (text similarity, keyword match, tool-use, exact match) [third-party (Power GI); STATUS UNVERIFIED].
- Classic **Activity tab** equivalents are not fully replicated [third-party; STATUS UNVERIFIED].

**Licensing/billing:**
- The GitHub Copilot harness uses **usage-based billing in Copilot Credits**; the Standard harness keeps the existing licensing model [OFFICIAL — `harnesses-overview` via search].
- Crucially, **charges apply to maker creation activities as well as runtime**: building, previewing, and evaluating consume credits *before* an agent is ever published [OFFICIAL — MC1446644; CAT — cost-governance post: "Maker development can now incur Copilot Credit consumption before an agent enters a formal production lifecycle"].
- Controls (PPAC → Licensing → Copilot Studio): per-environment credit **allocations** with enforcement rules (Alert / TenantPool / PayGo / Deny), and **agent-level monthly limits** with notification thresholds and stop-usage (Manage Agents), also settable via the Power Platform Licensing API (`allocationsByEnvironment`, resource `threshold` endpoints; currency type `MCSMessages`) [OFFICIAL API surface as documented in CAT — cost-governance post].
- Preview features bill at their published Copilot Credit rates and count against purchased capacity [OFFICIAL — Learn billing FAQ via search].

## 5. Security and governance implications

- **Egress containment is the core security story.** Sandbox code cannot reach the network regardless of imports (`requests` is installed but can't leave); the *only* external paths are configured Knowledge and Tools, so everything the agent does externally stays inside existing governance and **DLP policies** [CAT — agent-sandbox post, citing Learn `admin-data-loss-prevention`]. [INFERRED] This makes Tools/Knowledge configuration the effective policy enforcement point — govern connectors/MCP servers, and the sandbox inherits the boundary.
- **Skills are a trust surface.** A Skill shapes behavior and can bundle executable scripts; treat any Skill you didn't write (community, AI-generated, reused) as untrusted code — review for prompt injection, tool-misuse instructions, and mismatches with its stated purpose before adding [CAT — modern-mcs-agent-skills, explicit warning].
- **Memory** keeps a separate store per user in Microsoft-managed storage; one user's context is never visible to another; users can ask what's remembered, tell the agent to forget, or wipe via a memory portal [OFFICIAL — `memory-overview` (preview)].
- **Discovery and inventory.** Governance starts with finding harness agents: Power Platform Inventory / Azure Resource Graph / Inventory API filtered on `properties.isCLIAgent == true`, joined to environment and owner; classify environments as maker-development vs funded-production and apply matching credit controls [CAT — cost-governance post].
- **Consumption governance is now a pre-production concern**: apply default agent limits in maker environments, route capacity increases through approval, and note that built-in limit alerts go to tenant/environment admins, **not necessarily the agent owner** — define who triages [CAT — cost-governance post].
- **Transcripts/PII** guidance carries over from classic: conversation content can hold PII; send only what's needed, secure storage, retention, scoped permissions [CAT — power-of-topics post].
- [INFERRED] Because the model decides which Skill/Tool fires, authorization must live in the tools themselves (connections, connector auth, workflow gates) — never rely on instructions alone as a security control; CAT's own sample gates a write action behind an identity check.

## 6. Performance and maintainability implications

- **Reported runtime gains:** ~20% evaluation performance improvement and ~50% lower net token consumption vs the prior stack [OFFICIAL announcement figure; treat as vendor-reported].
- **Context economics drive performance.** Only metadata of Knowledge/Tools/Skills sits in context by default; full content loads on demand; instructions always load fully. Ten Skills cost ten short descriptions per turn, not ten instruction sets — keeping the context lean is a structural benefit; accuracy and speed gains are use-case dependent — "validate rather than assume" [CAT — modern-mcs-agent-skills].
- **Codify repeatable work into Skill scripts.** CAT's redlining Skill went from a ~15-minute agentic fail/rewrite loop (agent deriving Python live) to ~15 seconds by packaging the generalized script in the Skill — same output, ~60x faster. Pattern: let the loop discover the solution once, strip hardcoding, ship the pseudocode/script in `scripts/` [CAT — redlining post]. Generated-on-the-fly code is fine for novel work but is slower and varies between runs [CAT — agent-sandbox post].
- **Cost behavior differs from classic:** the loop's variable iteration count means variable credit burn; forcing extra steps (e.g., a log-after-every-step instruction) multiplies calls and credits [CAT — power-of-topics trade-off note; INFERRED generalization].
- **Maintainability model:** instructions = always-true baseline; each Skill a self-contained, reviewable, versionable unit; Skills/agents move through **solutions and standard ALM**; use the **Evaluate** tab plus eval quality gates (e.g., the Azure DevOps gate pattern) so refactors are regression-tested [CAT — modern-mcs-agent-skills, agent-sandbox; OFFICIAL — Learn `guidance/alm`, `analytics-agent-evaluation-intro`].
- **Observability:** the activity trace / reasoning view is the primary debugging surface — Skill misfires usually trace to descriptions that are too broad (fires too often) or too narrow (never fires) [CAT — modern-mcs-agent-skills].

## 7. Architecture guidance and anti-patterns

**Guidance** [CAT unless noted]:
1. **Smallest reliable component.** Place each behavior in the smallest component that makes it reliable and inspectable: Instructions (always true) / Knowledge (facts) / Tools (actions) / Memory (persistent context) / Skills (situational procedures) / Connected agents (specialist domains).
2. **Two-question placement test:** Can the agent infer it from tool/knowledge descriptions? If yes, write nothing. If no: is it true in every conversation? → Instructions. Only in specific scenarios? → Skill.
3. **Write Skill descriptions as routing metadata**, not documentation: name specifically ("HR Leave Eligibility Triage," not "HR Help"), state when to use *and when not to*. If two reasonable makers would disagree on when it applies, it's not specific enough.
4. **Skill before new agent.** Three tasks for the same audience behind one security boundary = one agent with three Skills. Build a separate (connected) agent only when the capability stands alone (different audience/security boundary) or when one agent's tool/context load has degraded accuracy.
5. **Exact work in code, judgment in the model.** Calculations and exact payloads go to the sandbox; packaged, reviewed scripts for repeatable work; freshly generated code for novel work.
6. **Deterministic spine, agentic edges.** Put irreversible/compliance-critical actions in workflows (or keep them on classic topics where the whole conversation must be scripted); let the orchestrator handle the ambiguous surround [community consensus aligned with OFFICIAL Workflow Designer positioning; INFERRED synthesis].
7. **Migrate by capability, validated by evals.** Understand the task, keep the outcomes that must work, map each responsibility to the right component, then run evals against core journeys before trusting any upgrade — human or plugin-generated.
8. **Govern from day zero:** default credit limits on maker environments, agent-level limits, periodic inventory scans for `isCLIAgent` agents [CAT — cost-governance].

**Anti-patterns** (all named or directly implied by CAT):
- *"One instruction blob with 43 tools and a prayer"* — a monolithic agent with no modularity.
- **Literal migration / "archaeology with YAML"** — porting every topic to a Skill and every variable to Memory because they existed.
- **Designing around sandbox persistence** — expecting a file created in one conversation to exist in the next; Memory is not file storage.
- **Format-conversion pipelines in the sandbox** — e.g., DOCX→PDF→DOCX round-trips destroy fidelity; operate on the native format (redlining lesson).
- **Vague Skill descriptions** ("Helps with HR questions") — wrong Skill fires, or none.
- **Agent-per-task proliferation** where Skills would do.
- **Instructions as a security boundary** — natural-language guards (e.g., recursion guards, "don't call X") are best-effort, not hard stops [CAT — power-of-topics notes this explicitly for instruction-based guards].
- **Unbounded maker development** — treating build/preview/eval as free when it now consumes credits.

## 8. Sources

**Local (CAT blog clone, read in full):**
- /workspace/microsoft/mcscatblog/_posts/2026-07-07-new-orchestrator-resources.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-13-power-of-topics-copilot-studio.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-14-migration-plugin-video-demo.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-15-redlining-documents-new-copilot-studio-experience.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-20-copilot-studio-agent-sandbox.md
- /workspace/microsoft/mcscatblog/_posts/2026-06-15-modern-mcs-agent-skills.md
- /workspace/microsoft/mcscatblog/_posts/2026-08-07-copilot-harness-cost-governance.md

**Web (via WebSearch synthesis of Microsoft Learn and Microsoft announcements; learn.microsoft.com direct fetch blocked):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview (Agents powered by GitHub Copilot Harness overview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/build-overview (Build an agent (preview))
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview (Choose a harness)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/switch-experiences (Access standard harness agents and agent flows)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-copilot-studio
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/tools-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/preview-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/analytics-agent-evaluation-intro
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/publication-fundamentals-publish-channels
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/publication-channels-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/memory-overview (Memory (preview))
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/authoring-select-agent-model
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/voice-agents-control-conversation
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/faq-billing-licensing
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/more-powerful-agents-and-workflows-for-autonomous-business-processes-introducing/4542969 (harness announcement; fetch blocked, content via search)
- https://pupuweb.com/mc1446644-microsoft-copilot-studio-github-copilot-harness-now-generally-available-for-building-autonomous-agents-and-workflows/ (mirror of message center MC1446644, GA 2026-08-03)
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/publish-your-microsoft-copilot-studio-agents-to-microsoft-365-copilot/
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/new-and-improved-computer-using-agents-a-new-workflows-experience-and-real-time-voice-experiences/ (May 2026 what's new)
- Third-party corroboration (used with caution, flagged where load-bearing): https://powergi.net/blog/copilot-studio-update-june-2026/ ; https://rpabotsworld.com/microsoft-copilot-studio-august-2026-rebuilt-agent-platform-guide/ ; https://holgerimbery.blog/copilot-studio-reimagined ; https://www.wrvishnu.com/copilot-studio-new-agent-experience/ ; https://chatforest.com/builders-log/microsoft-copilot-studio-rebuilt-july-2026-orchestrator-workflow-designer-builder-guide/ (its "GA June 2026" claim judged unreliable)
