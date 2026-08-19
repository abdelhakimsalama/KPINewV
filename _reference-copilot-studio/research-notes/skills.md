# skills

Research note — Agent Skills in the NEW Microsoft Copilot Studio agents experience (GitHub Copilot harness). Compiled 2026-08-19. Claims tagged [OFFICIAL] (documented Microsoft behavior on Learn or in official product announcements), [CAT] (Copilot Studio CAT-blog guidance/practice), [INFERRED] (author reasoning), [STATUS UNVERIFIED] where confirmation failed.

**Disambiguation first (three unrelated things are all called "skills"):**
1. **Agent Skills** (this note): SKILL.md-based, on-demand procedural instructions inside a new-experience agent. [OFFICIAL — Learn `agents-experience/skills-overview`]
2. **Legacy Azure Bot Service / Bot Framework "skills"** in classic Copilot Studio: hosted conversational components registered with an agent (app registration, auth, deployment; Bot Framework SDK 4.12.0+ / M365 Agents SDK 1.0.0+). Same word, entirely different format and runtime. [OFFICIAL — Learn `configuration-add-skills`, `advanced-use-skills`]
3. **"Skills for Copilot Studio" plugin** (CAT open-source project, March 2026): skills for *AI coding assistants* (Claude Code / GitHub Copilot CLI) that help a developer author Copilot Studio agents as YAML from the terminal. It is pro-dev tooling *about* Copilot Studio, not a feature *inside* it, and is explicitly "an experimental project… not an officially supported Microsoft product." [CAT — 2026-03-10 post]

## 1. What it is and how it works

**Definition.** In the new agents experience ("GitHub Copilot harness"), a skill is a reusable capability defined by a **name**, a **description**, and a set of **instructions written in Markdown** — a self-contained package of procedural know-how the agent loads on demand when a task matches. Unlike tools, which connect the agent to external services, skills are instructions and logic you can create, share, and reuse. [OFFICIAL — Learn `agents-experience/skills-overview`, `skills-create`]

**Format.** Skills follow the **Agent Skills open format** (agentskills.io), an open standard originally developed by Anthropic (spec published December 2025) and since adopted by Microsoft (VS Code, GitHub Copilot, Visual Studio, Copilot Studio), OpenAI, Cursor and dozens of other tools. [OFFICIAL for the Copilot Studio adoption — CAT 2026-06-15 post links the standard; press coverage confirms Microsoft adoption of the open standard.] The package shape:

```text
my-skill/
├── SKILL.md          # YAML front matter (name, description) + Markdown instructions
├── scripts/          # optional executable code (e.g., Python)
├── references/       # optional documentation loaded as needed
└── assets/           # optional templates and resources
```
[OFFICIAL — Learn skills-overview describes SKILL.md + optional supporting files (scripts, templates, reference documents); CAT 2026-06-15 shows the folder layout and states "Copilot Studio supports this full shape today."]

**Progressive disclosure.** Registration works the same as knowledge and tools: only **metadata (name + description) sits in the agent's context by default**; the full SKILL.md instructions are pulled into context only when the conversation matches, and bundled references/scripts/assets are read only when the loaded skill directs the agent to them. The agent's own instructions are the exception — always loaded in full. [CAT — 2026-06-15 post, explicit; consistent with the open format's three-level model (metadata → SKILL.md body → bundled resources)] Ten skills therefore cost ten short descriptions per turn, not ten instruction sets. [CAT]

**Discovery and activation.** You do **not** call a skill directly. The orchestration runtime decides when to activate a skill based on the user's message and the skill's description; once activated, the skill's instructions guide the agent's behavior for that task. [OFFICIAL — Learn skills-overview] Activation is observable in the agent's reasoning view / activity trace, which is the primary debugging surface: a skill firing too often means the description is too broad; never firing means it is too narrow or does not use your users' vocabulary. [CAT — 2026-06-15] The model retains judgment: a skill *guides* rather than straitjackets, and the agent decides whether to follow it to the letter or adapt. [CAT]

**Skills + tools ("soft pointers").** A skill can run its own bundled script, but it can also *soft-point* at the agent's existing capabilities — actions, flows, connectors, MCP servers — e.g., "use the order-lookup action here." The pointer grants nothing: if the agent does not already have that tool, the instruction cannot be fulfilled, and even when it does, the agent still decides whether to follow it. [CAT — 2026-06-15] Learn states the same complementarity: "a skill might instruct your agent to use a specific tool in a particular way"; skills and MCP tools complement each other (skill = how to handle the task, tool = capability to execute it). [OFFICIAL]

**Scripts and the agent sandbox.** Bundled scripts execute in the Copilot Studio **agent sandbox**: a managed container with a Python runtime, local files, preinstalled libraries and shell tools. A CAT inventory of an empty agent on 2026-07-21 found **Python 3.12.9**, **99 Python libraries**, 11 built-in tools, and 8 built-in Skills. [CAT — 2026-07-20 sandbox post] Two hard properties: **no `pip install`** (what ships in the container is all you get — e.g., `pdfplumber` is present, `pdf2docx`/`pymupdf` are not), and **no outbound network path** from the sandbox (the `requests` package is installed but nothing can leave; external reach happens only via configured Knowledge and Tools). The sandbox is ephemeral — generated files must be returned to the user or saved via a tool. [CAT — 2026-07-15 redlining post; 2026-07-20 sandbox post]

**Authoring, importing, sharing.** [OFFICIAL — Learn `skills-create`, `skills-add-existing`, `skills-manage`, `whats-new`]
- **Create from blank in studio** (Skills area on the Build tab): supply name, description, instructions. Names use only lowercase letters, numbers, and hyphens, and must not start or end with a hyphen (e.g., `customer-support-escalation`).
- **Upload an existing skill**: either a standalone `SKILL.md` or a **.zip package with SKILL.md at the top level** plus supporting files (scripts, templates, references). The Learn "add an existing skill" page also mentions browsing a **skill catalog** as an entry point. [OFFICIAL per search synthesis; catalog specifics — [STATUS UNVERIFIED], see §4]
- **Export/share**: a skill can be **downloaded** (Markdown file or package) to share or back up; Learn's What's New states you can "create a skill once and add it to multiple agents" and export as Markdown to share. [OFFICIAL]
- **ALM**: a skill is part of its agent and travels with it through Power Platform solutions and the normal ALM lifecycle. [OFFICIAL — CAT 2026-06-15 citing solutions; sandbox post links Learn ALM guidance]
- Open-format field limits: name ≤ 64 characters, description ≤ 1024 characters. [OFFICIAL for the open format spec; applied to Copilot Studio — [INFERRED], since Copilot Studio implements that format; not seen stated on a Copilot Studio Learn page directly]

**Community source.** The **CAT Agent Skills gallery** (microsoft.github.io/cat-agent-skills) is a community-driven collection of ready-made skills (each a drop-in SKILL.md, some with script bundles) filterable by platform, downloadable and uploadable into an agent — e.g., `redlining-content`, `generating-podcast-script`, `agent-harness-explorer`. [CAT — 2026-07-07, 2026-07-15, 2026-07-28 posts]

## 2. When to use it / when NOT to use it

**The core decision rule (skill vs. instructions).** [CAT — 2026-06-15, and mirrored in Learn guidance] If the agent can infer the behavior from well-described tools/knowledge alone, write nothing. If it cannot: guidance that is **true in every conversation** (tone, role, always-on guardrails) belongs in **instructions**; guidance that **applies only to specific scenarios** belongs in a **skill**, so it stays out of default context and loads only when its scenario arises.

**Use a skill when** the content is situational, procedural know-how the LLM cannot infer — CAT's taxonomy of shapes a skill can take [CAT — 2026-06-15]: reference manual (proprietary data model/schema), specialist (region-specific tax rules), playbook (support triage), standard operating procedure (refund policy windows), briefing pack, checklist (pre-submission validation), protocol (security-incident handling), runbook (pipeline with failure handling), template (fixed output format/house style). Also use a skill to make behavior **repeatable and fast**: package a reviewed script so the agent runs it rather than re-deriving code every conversation — the redlining skill went from ~15 minutes of agentic trial-and-error to ~15 seconds by codifying the discovered script into `scripts/redline.py`. [CAT — 2026-07-15]

**Skill vs. tool.** Tools give reach into external systems (connectors, MCP, REST, flows); skills tell the agent *how and when* to use that reach. If the need is an external action or live data, it is a tool; if the need is method, sequence, validation, or format, it is a skill; frequently it is both (skill soft-points at the tool). [OFFICIAL — Learn skills-overview; CAT]

**Skill vs. knowledge.** Knowledge gives searchable facts; a skill gives the situational know-how to use facts and tools well. [CAT — 2026-06-15; deep-dive component model: "Instructions carry what is always true, Knowledge the searchable facts, Tools the system actions, Memory the persistent context, Skills the situational procedures, connected agents the real specialist domains." — CAT 2026-07-07]

**Skill vs. a new (connected) agent.** Before skills, every distinct task tended to become another specialized agent. Often "three agents" are really one agent with three skills — if the same agent serves the same audience within the same knowledge/security boundary, a skill is the better unit of modularity. Build a **separate agent** instead when (a) the capability would stand on its own for a different audience behind a different security boundary (HR assistant vs. IT support), or (b) one agent has accumulated too many tools and context load is degrading accuracy — then split and delegate. [CAT — 2026-06-15]

**Do NOT use a skill for:** always-true behavior (instructions), plain facts (knowledge), external actions (tools), the obvious (a well-described tool needs no manual) [CAT]; and do not force Copilot Studio at all when there is no business process around the task — a pure one-off "compare these two documents" job fits Cowork better; Copilot Studio + an authored skill wins when there is a fixed template, routing, rules, and a repeatable pipeline. [CAT — 2026-07-15]

## 3. Classic-experience comparison (what it replaces or simplifies)

- **Replaces the "giant instruction blob."** In classic generative-orchestration agents, all custom guidance competed for space in one instruction field, in context on every turn. Skills modularize that: always-on baseline stays in instructions; everything situational moves into named, on-demand units. [CAT — 2026-06-15; the podcast post is the worked example: a few-thousand-word procedure that would otherwise sit in context "including the turns where someone just says 'hi'"] [CAT]
- **Absorbs much of what topics did.** Classic topics were trigger-phrase/model-description-routed dialog trees (question nodes, conditions, variables) — deterministic authoring of *procedure*. In the new experience the harness component model has no topic canvas; repeatable procedures live in skills, with the LLM (not a topic trigger) deciding activation from the description, and exact/deterministic steps pushed into bundled scripts run in the sandbox. [CAT — 2026-07-07 component model; 2026-03-10 post describes the classic topic machinery this replaces] [INFERRED framing: skills are the new-experience home for the "procedural" share of topics, while workflows cover the fully deterministic share.]
- **Replaces classic "skills" (Azure Bot Service).** The classic feature named "skills" — remotely hosted Bot Framework bots registered into an agent with app registrations and deployment — shares only the name. Agent Skills need no hosting, no registration, no code deployment: a Markdown file (optionally zipped with resources) uploaded into the agent. [OFFICIAL — Learn `configuration-add-skills` vs. `agents-experience/skills-overview`] Dramatic simplification of "add a packaged capability." [INFERRED]
- **Simplifies reuse.** Classic reuse of conversational logic meant exporting topics between agents or standing up shared bot components. Skills are portable Markdown by design (open standard), downloadable, uploadable into any new-experience agent, shareable via a community gallery, and (per What's New) addable to multiple agents. [OFFICIAL/CAT]
- **Simplifies "custom capability = custom service."** Where classic agents needed a flow/connector or external service for every calculation or file transformation, a skill + sandbox script now covers local executable work (docs, spreadsheets, PDFs, charts) with no infrastructure. [CAT — 2026-07-20]

## 4. Limitations, GA/preview status, licensing notes

**Status.**
- The **GitHub Copilot harness** (new agent experience) reached **general availability on August 3, 2026** (message center MC1446644; Tech Community announcement; new workflows designer also GA'd Aug 3). Before that it ran as a **production-ready preview**. [OFFICIAL]
- **Skills specifically**: the en-US Learn pages are now titled "…(GitHub Copilot)" with no "(preview)" suffix, while several localized versions of the same pages still carry "(preview)" — consistent with skills having shipped as preview and moved forward with the harness, with localization lagging. I could not find an explicit "skills are now GA" statement. Treat skills as **shipped with the GA harness but with GA labeling not independently confirmed** [STATUS UNVERIFIED — as of 2026-08-19].
- Skills exist **only in the GitHub Copilot harness**, not the Standard harness. [CAT — 2026-07-28: "Skills live there, not in the Standard harness"]

**Hard limits and constraints found in sources.**
- Skill name in studio: lowercase letters, numbers, hyphens; no leading/trailing hyphen. [OFFICIAL — skills-create]
- Open-format limits: name ≤ 64 chars, description ≤ 1024 chars. [OFFICIAL for agentskills.io spec; Copilot Studio-specific enforcement [STATUS UNVERIFIED]]
- Upload: standalone SKILL.md or .zip with SKILL.md at top level. [OFFICIAL]
- Sandbox: no pip install; no network egress; ephemeral storage; Python 3.12.9 with ~99 preinstalled libraries observed 2026-07-21 (set "may change in the future"). [CAT]
- A claim of "maximum 100 skills per agent" surfaced in one search synthesis but could not be traced to a Learn page — **do not rely on it** [STATUS UNVERIFIED]. No documented max skill package size found [STATUS UNVERIFIED].
- Distribution: as of June 2026 a skill was **scoped to its agent** (travels via solutions/ALM); a product skill catalog was "being worked on." [CAT — 2026-06-15] By August 2026, Learn's What's New describes creating a skill once and **adding it to multiple agents**, and the add-existing page references browsing a **skill catalog** — indicating cross-agent reuse has landed or is landing; the exact mechanics/scope of the catalog were not verifiable from search snippets. [OFFICIAL for the What's New wording; details [STATUS UNVERIFIED]]
- Skill "stickiness" across turns is imperfect: a skill can activate for the initial request and silently drop out for follow-ups unless the description explicitly claims ownership of follow-up refinements. [CAT — 2026-07-28, observed bug + fix]

**Licensing/billing.** Agents on the GitHub Copilot harness use **usage-based billing (Copilot Credits) for all work regardless of Microsoft 365 Copilot licensing**, and — unlike the Standard harness, which bills after publish — **credits are consumed from the moment you start building** (authoring via NL, preview testing, evals). Credits are charged for LLM tokens, tools (including knowledge and MCP), and the harness itself. [OFFICIAL — Learn `agents-experience/billing-credit-overview` per search synthesis] A Copilot Studio capacity pack is $200/month for 25,000 credits (third-party figures consistent with Microsoft pricing) [OFFICIAL pricing figure; per-task credit estimates are third-party — treat as indicative]. Skills have no separate meter in any source found; their cost effect is indirect via tokens/tool calls [INFERRED]. Ancillary: premium connectors invoked per a skill's soft pointer carry normal Power Platform licensing (e.g., Azure TTS connector is premium, throttled at 100 calls/connection/60s). [CAT/OFFICIAL — 2026-07-28]

## 5. Security and governance implications

- **Skills are a trust surface.** A skill shapes agent behavior and can bundle executable scripts. CAT's explicit warning: treat any skill you did not write (community, AI-generated, reused from another environment) as **untrusted code** — review before adding; check for prompt injection, instructions to misuse tools, and behavior that does not match the skill's claimed purpose. [CAT — 2026-06-15]
- **Sandbox containment is the backstop.** Skill scripts run with no outbound network path; the only ways out of the sandbox are configured Knowledge and Tools, which remain inside tenant governance and DLP data policies. A malicious script cannot exfiltrate directly; it would have to persuade the agent to misuse an existing tool — which is why tool-misuse review of third-party skills matters. [CAT — 2026-07-20 (sandbox), 2026-06-15 (review guidance); DLP reference OFFICIAL via Learn admin-data-loss-prevention]
- **Soft pointers grant nothing.** A skill referencing a tool does not bind to it or confer access; capability grants stay with the agent's tool configuration (and connector connections/auth), keeping permissioning where admins already govern it. [CAT — 2026-06-15] [INFERRED implication: least-privilege tool configuration is the effective blast-radius control for a bad skill.]
- **Secrets do not belong in skills.** Credentials go into Power Platform connections (or Entra ID auth), never into a skill file, instruction, or variable. [CAT — 2026-07-28]
- **ALM/audit.** Skills travel in solutions, so they are versionable, reviewable artifacts in normal ALM pipelines; activation is auditable per conversation via the activity trace/reasoning view. [OFFICIAL/CAT]
- **Governance gap to watch** [INFERRED]: SKILL.md upload is effectively "behavior as content" — an org that gates code deployment but lets makers upload zips with Python into production agents has moved code review into the maker workflow; pair the eval quality-gate pattern (CAT) with human review of skill bundles.

## 6. Performance and maintainability implications

- **Context economy.** On-demand loading keeps every turn's context lean (descriptions only), delaying context-window saturation as capability grows; this is structural and applies almost everywhere. [CAT — 2026-06-15]
- **Accuracy.** Use-case dependent but real: targeted tool-use guidance arriving only when relevant can make tool selection/parameterization more reliable, especially with large or overlapping toolsets. Evaluate rather than assume. There is data suggesting accuracy degrades as more is loaded into context; past a point, more skills will not save an overloaded agent — split into connected agents. [CAT — 2026-06-15]
- **Speed and cost.** A skill nudges the agent to the right approach: fewer knowledge searches, tool calls, and reasoning loops → lower latency, higher throughput, lower credit spend per conversation. Per-case; validate. [CAT — 2026-06-15] The strongest documented win: pre-written scripts vs. live code generation — same output, ~60x faster (15 min → 15 s) in the redlining case; live generation remains better for novel work, at the cost of time and run-to-run variance. [CAT — 2026-07-15, 2026-07-20]
- **Maintainability.** Each skill is a focused, self-contained unit to reason about, review, and version one at a time — vs. one ever-growing instruction blob. Bundled scripts can be tested and versioned like any code asset. Auto-updated community distribution (gallery; plugin marketplaces in the coding-agent world) pushes pattern improvements to consumers. [CAT]
- **Observability loop.** Reasoning view/activity trace shows which skill fired and how its steps executed; CAT's eval tooling (agent evaluation, quality-gate in CI) closes the loop on "does the right skill fire at the right moment." [CAT — 2026-06-15, 2026-07-20]

## 7. Architecture guidance and anti-patterns

**Design discipline (positive guidance):**
- **Write the description as routing metadata, not documentation.** Name specifically (`hr-leave-eligibility-triage`, not `hr-help`); state when to use **and when not to** ("Use for leave eligibility and required documentation. Do not use for payroll or benefits enrollment."). Test: if two reasonable makers would disagree about when it applies, it is not specific enough. [CAT — 2026-06-15; OFFICIAL — Learn: good descriptions explain what/when/when-not]
- **Claim follow-ups explicitly.** Add "handles the initial request and every follow-up refinement in the same task" to the description if the skill should own the whole exchange; otherwise it can drop out of context mid-task. [CAT — 2026-07-28]
- **One focused scope per skill; prefer a small set of high-quality, non-overlapping skills** with clear semantic boundaries — overlapping descriptions give the orchestrator no basis to choose and can cause multiple things to fire. [OFFICIAL/CAT — best-practice guidance]
- **Keep SKILL.md lean; push depth into references/**. Guidance associated with the format: keep the body under ~500 lines, move detail into supporting files loaded on demand (the redlining skill loads `docx-submissions.md` or `pdf-submissions.md` depending on input type). [OFFICIAL open-format guidance; CAT worked example]
- **Codify the loop.** Development pattern for script-bearing skills: run with no code → let the agent fail-loop to a working script → strip hardcoding into generalized pseudocode → ship it in `scripts/`. Execution replaces re-derivation. [CAT — 2026-07-15]
- **Smallest reliable component.** Put each behavior in the smallest component that makes it reliable and inspectable: instructions (always true), knowledge (facts), tools (actions), memory (persistent context), skills (situational procedures), connected agents (specialist domains); exact math in code, not the model's head. [CAT — 2026-07-07, 2026-07-20]
- **Design for the sandbox you have:** verify available libraries first (ask the agent, or run the `agent-harness-explorer` skill), avoid approaches needing absent packages, never rely on sandbox persistence or network. [CAT — 2026-07-15, 2026-07-20]

**Anti-patterns:**
- **The instruction blob**: thousands of words of scenario-specific procedure in agent instructions, taxing every turn. [CAT]
- **Vague descriptions** ("Helps with HR questions") → false activation or no activation. [CAT]
- **Agent sprawl**: one agent per task where one agent + N skills serves the same audience/boundary. Converse anti-pattern: piling skills onto an overloaded agent instead of splitting to connected agents. [CAT]
- **"Archaeology with YAML"** when migrating from classic: mechanically converting every topic into a skill and every variable into memory because they existed. Re-derive the architecture from the task. [CAT — 2026-07-07]
- **Secrets or environment-specific values inside skill files.** [CAT]
- **Assuming a soft-pointed tool exists** — the skill breaks silently if the tool is missing or its description was rewritten so the agent no longer matches it by name. [CAT — 2026-07-28: a heavily rewritten tool description "will break the handoff"]
- **Unreviewed third-party skills** added straight to production. [CAT]
- **Expecting deterministic execution**: a skill guides, the model decides; if a step must never vary, put it in a script (or a workflow), not prose. [CAT/INFERRED]

## 8. Sources

**Local (CAT blog clone, read in full):**
- /workspace/microsoft/mcscatblog/_posts/2026-03-10-skills-for-copilot-studio.md
- /workspace/microsoft/mcscatblog/_posts/2026-06-15-modern-mcs-agent-skills.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-28-podcast-script-skill.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-26-claude-copilot-skills-copilot-studio-plugin-demo.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-07-new-orchestrator-resources.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-15-redlining-documents-new-copilot-studio-experience.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-20-copilot-studio-agent-sandbox.md

**Web (Microsoft Learn and official, via WebSearch synthesis — learn.microsoft.com direct fetch blocked):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-create
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-add-existing
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-manage
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/configuration-add-skills (legacy Azure Bot Service skills)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-use-skills (legacy)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/more-powerful-agents-and-workflows-for-autonomous-business-processes-introducing/4542969 (harness announcement/GA)
- https://microsoft.github.io/cat-agent-skills/ (CAT Agent Skills gallery)
- https://github.com/microsoft/skills-for-copilot-studio (coding-assistant plugin, distinct feature)
- https://agentskills.io/ (Agent Skills open format; via CAT post links and press coverage)
- Secondary/press used for status triangulation: pupuweb.com (MC1446644 GA summary), schneider.im, windowsforum.com, lukoplt.blogspot.com, venturebeat.com / unite.ai / paperclipped.de (Anthropic open-standard adoption timeline), agensi.io (open-format field limits).
