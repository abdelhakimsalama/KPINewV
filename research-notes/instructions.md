# instructions

Research note — authoring Instructions in the NEW Microsoft Copilot Studio agents experience (GitHub Copilot harness). Compiled 2026-08-19. Claims tagged [OFFICIAL] (documented Microsoft behavior, Learn or CAT-blog statement of platform fact), [CAT] (CAT-blog guidance/practice), [INFERRED] (reasoned from evidence), plus GA/preview flags.

## 1. What it is and how it works

Instructions are natural-language guidance that shapes the agent's behavior, tone, and scope. In agents powered by the GitHub Copilot harness (the "agents experience"), instructions — not topic flows and triggers — are **the primary mechanism for controlling agent behavior**; the enhanced orchestration runtime interprets them when responding to users. [OFFICIAL — Learn, "Configure agent details and instructions" (agents-experience/authoring-instructions)]

Key documented mechanics:

- **Where they live.** Instructions are edited on the **Build tab**, together with the agent name and icon. The Build tab has two areas: a rich-text instructions editor in the center (role, boundaries, behavior) and a components panel with seven sections — Model, Microsoft IQ, Skills, Tools, Knowledge, Connected agents, Memory. [OFFICIAL — Learn agents-experience/authoring-instructions and agents-experience/build-overview, via search synthesis]
- **Generated or hand-written.** If you create an agent through the natural-language creation experience, Copilot Studio generates initial instructions from your description; starting from a blank agent, you write them directly. [OFFICIAL — Learn authoring-instructions]
- **How the orchestrator consumes them.** The new experience relies on enhanced orchestration to "interpret your instructions, decide when to use knowledge, and determine when to use other capabilities." [OFFICIAL — Learn agents-experience docs] The CAT blog adds the crucial context-loading detail: knowledge sources, tools, and Skills are registered with only their **metadata** (name + description) in context by default, and full content is pulled in on demand — **the agent's own instructions are the exception: always loaded in full, every turn**. [CAT — "Agents Have Skills Now" (2026-06-15)]
- **Referencing components inline.** In the classic generative-orchestration instructions editor, you can type a slash (`/`) to insert a reference to a specific resource — a tool, a topic, another agent, a variable, or a Power Fx expression. [OFFICIAL — Learn authoring-instructions (classic "Write agent instructions" page)] In the new experience, the documented pattern is to name the agent's components (tools, knowledge sources, skills, connected agents) in the instructions text, after first making sure each component's own name and description are accurate and specific, because the orchestrator matches on those. [OFFICIAL — Learn guidance] Whether the exact `/`-picker mechanic exists identically in the new Build-tab editor I could not confirm from a primary source — search synthesis attributes it to both experiences. [STATUS UNVERIFIED for the new editor]
- **Formatting.** The instructions editor is rich-text; structure signals (headings, bullets) are read by the model as meaning: sections group related non-sequential tasks, bullets mark parallel/independent tasks, numbered lists imply order. [OFFICIAL — Learn "Write effective instructions" guidance family; the goal/action/transition step pattern is documented on the closely related M365 declarative-agent-instructions page and echoed in Copilot Studio guidance]
- **Probabilistic, not deterministic.** Instructions are executed by an LLM. The CAT blog states it flatly: "instructions are *probabilistic* (the AI handles them), while the code method … is *deterministic* (math handles it). If you need a 100% guarantee, use the code." [CAT — "Kill the [1]" (2025-12-15)] And: "Response and instruction adherence will vary with different models." [CAT — "Defeating Oversummarization" (2026-01-23)]
- **Instructions steer planning, not just wording.** "Instructions act as guidelines that the orchestrator follows not only to provide context for the answer but also to plan its actions" — e.g., "When the question involves monthly KPIs, use the MCP tool for data and then consult the knowledge base for corrections. If corrections exist, include them in the response." [CAT — "Influencing Agent Planning with Contextual Instructions" (2025-11-11); written against generative orchestration, but the planning-steer principle carries into the new harness, where CAT explicitly cites it as the reference for how always-on instructions steer the agent [CAT — Skills post]]

**What belongs in instructions** (synthesis of Learn + CAT): the agent's identity and primary role/mission; tone and response style; scope — what it handles and what it should decline or redirect; always-on guardrails and safety boundaries; grounding rules (which knowledge to prefer, citation behavior, what to do when nothing is found); cross-cutting tool-use rules ("for X-type questions call tool Y, then reconcile with knowledge Z"); escalation/handoff triggers; handling of ambiguous input. [OFFICIAL — Learn agents-experience/authoring-instructions, via search synthesis; CAT]

## 2. When to use it / when NOT to use it

The CAT blog gives the cleanest published decision procedure [CAT — "Agents Have Skills Now"]:

1. **Can the agent infer it from tool and knowledge descriptions?** If yes, don't write it down at all. A well-described tool or knowledge source usually needs no instruction support. (Classic-guidance corollary: add routing hints only where the right tool/knowledge is genuinely ambiguous. [OFFICIAL — Learn generative-mode-guidance])
2. **Is it true in every conversation, for every scenario?** Then it belongs in **instructions**: tone, the agent's role, always-on guardrails — "valid 100% of the time, so they should always be in context."
3. **Does it only apply to specific scenarios?** Then it belongs in a **Skill**, loaded on demand — playbooks, SOPs, checklists, runbooks, templates, region-specific rules.

Use instructions for:
- Identity/mission/scope and refusal boundaries. [OFFICIAL]
- Global tone, formatting, and citation policy (e.g., "Never include any citation in your knowledge answers" — works "generally well," but is probabilistic. [CAT — remove-citations post])
- Cross-source grounding rules that must hold on every data question (MCP + knowledge-corrections pattern). [CAT — influence-orchestration post]
- Global tool-use discipline: which tool for which class of request, what to validate before calling, when to escalate. [OFFICIAL/CAT]

Do NOT use instructions for:
- **Situational procedures** → Skills. Step-by-step organizational know-how that only matters for certain tasks bloats always-on context and makes agents "bloated and unpredictable." [CAT]
- **Data and reference facts** → Knowledge. The component model: "Instructions carry what's always true, Knowledge the searchable facts, Tools the system actions, Memory the persistent context, Skills the situational procedures, and connected agents the real specialist domains." [CAT — "New Harness, New Rules?" (2026-07-07), quoting the official Deep Dive deck]
- **Guaranteed/exact behavior** → deterministic components. When output must be verbatim or provably clean (exact policy text, citation stripping), instruction-only approaches were "less consistent" than tool/topic pipelines; code is the 100% path. [CAT — oversummarization + remove-citations posts]
- **Security enforcement** → platform controls (see §5). Instructions are not an enforcement boundary. [INFERRED, supported by third-party security research]

## 3. Classic-experience comparison (what it replaces or simplifies)

- **Classic (standard harness):** behavior is shaped by explicit topics, triggers, and branching conversation flows; instructions exist (and matter under generative orchestration) but share the control surface with topic design. The standard harness remains "a dependable option for rule-based agents and structured, repeatable workflows … where you want predictable behavior." [OFFICIAL — Learn agents-experience/classic-vs-new ("Choose a harness")]
- **New (GitHub Copilot harness):** "Instead of authoring explicit conversation topics, flows, and branching logic, you describe your agent in natural language," and enhanced orchestration interprets the instructions at runtime. Instructions replace topic authoring as the primary behavior mechanism. [OFFICIAL — Learn classic-vs-new and authoring-instructions]
- **What instructions simplify:** routing (no trigger phrases/topic disambiguation to hand-author), plan construction (multi-step tool+knowledge plans described in prose), and the nine-tab configuration surface collapsed into Build/Preview/Evaluate/Monitor. [OFFICIAL — Learn; third-party summaries of the harness announcement]
- **What they do NOT replace 1:1:** deterministic interception patterns from classic — e.g., `OnGeneratedResponse` + Power Fx post-processing, `autoSend: false` on generative answers — have no direct instructions equivalent; in the new experience the deterministic role is played by tools, scripts bundled in Skills, and workflows. [CAT — remove-citations (classic patterns) + redlining post (codified script in a Skill); INFERRED mapping]
- **One-way door:** agents cannot be converted between harnesses in either direction; the architectures differ. [OFFICIAL — Learn classic-vs-new]
- **Migration anti-guidance:** the official upgrade plugin *proposes* a new architecture; CAT explicitly warns against porting old designs mechanically — "Don't turn every topic into a Skill and every variable into memory just because they existed, that's archaeology with YAML." [CAT — new-orchestrator-resources]
- **Instruction limits differ by experience:** classic Copilot Studio instructions have a widely documented 8,000-character field limit (community threads report the VS Code extension can push longer strings than the UI allows, i.e., the limit is UI/service-enforced per field). [OFFICIAL-adjacent — Microsoft Q&A/Tech Community + microsoft/vscode-copilotstudio issue #51; exact normative Learn citation not retrievable] For the new experience I found **no documented character limit**. [STATUS UNVERIFIED]

## 4. Limitations, GA/preview status, licensing notes

- **Status of the agents experience:** Learn pages for the new experience carried "(preview)" markers and described it as a **production-ready preview** through mid-2026 (e.g., "Build an agent (preview)", "Skills overview for agents (preview)", "Preview and test an agent (preview)"). In August 2026, GA signals appeared: the new **workflows designer** reached GA on 2026-08-03 (message center MC1442234), and third-party posts (early August 2026) describe "GitHub Copilot harness GA + licensing." Sources conflict on whether the *entire* agents experience is GA as of 2026-08-19; treat the harness/agents experience as at minimum production-ready preview with GA rolling out. [STATUS: conflicting — flagged]
- **Licensing/billing:** the GitHub Copilot harness uses **usage-based billing in Copilot Credits**, charged for LLM tokens, tools (including knowledge and MCP), and the harness itself — and **billing starts from the moment you start building**, unlike the standard harness which bills after publish. The "included with Microsoft 365 Copilot" treatment of other harnesses does not apply. [OFFICIAL — Learn agents-experience/billing-credit-overview, via search synthesis + third-party corroboration] Direct consequence for instruction authoring: every always-on instruction token is billed on every turn. [INFERRED]
- **Instruction length:** no published character limit for the new experience found [STATUS UNVERIFIED]; Microsoft's standing guidance is that instructions "should be concise and to the point — instructions that are too long can lead to latency, timeouts, or issues handling the prompt." [OFFICIAL — Learn prompt/instructions guidance, quoted via community sources]
- **Adherence is model-dependent and probabilistic** — no instruction is guaranteed to be followed; consistency varies with the selected model (CAT tested with Claude Sonnet 4.5 as agent model). [CAT — oversummarization post]
- **Variables cannot be set in instructions** (standard-harness generative orchestration): CAT worked around it by telling the orchestrator in prose what inputs to pass to an AI Prompt tool, noting possible consistency issues. [CAT — oversummarization, Method 3] I found no evidence the new experience adds variable assignment inside instructions. [STATUS UNVERIFIED]
- **Runtime constraint relevant to what instructions can ask for:** the new Copilot Studio runtime does not allow installing Python packages ("no pip install") — instructions/Skills can only direct the agent to use what ships in the container (e.g., `pdfplumber` is present, `pdf2docx`/`pymupdf` are not), and "the skills that are available … may change in the future." [CAT/OFFICIAL-behavior — redlining post (2026-07-15)]
- **No classic↔new conversion** limits reuse of instruction investments across harnesses. [OFFICIAL]

## 5. Security and governance implications

- **Instructions are a soft control layer, not a security boundary.** They are interpreted by an LLM, not enforced deterministically; third-party security research on Copilot Studio documents prompt-injection attacks overriding instruction-level guardrails and an agent "reasoning around" a file-level instruction guardrail to reach the same data by another path. [Third-party — VentureBeat CVE coverage, Princeton IT Services analysis; consistent with CAT's probabilistic-vs-deterministic framing [CAT]] Architectural rule: anything that must never happen has to be enforced outside instructions — connector DLP policies, tool/knowledge scoping, authentication and user-permission trimming on knowledge sources, environment governance. [INFERRED]
- **Do not put secrets or sensitive logic in instructions.** Instruction text is part of the prompt surface and can be extracted through injection; treat it as user-visible. [INFERRED from the above]
- **Instructions interact with a trust surface: Skills.** Because instructions and Skills jointly steer behavior and Skills can bundle executable scripts, CAT advises treating any Skill you did not write as untrusted code: "review it before adding it. Check for prompt injection, instructions to misuse tools, and anything that does not match what the Skill claims to do." [CAT — Skills post] The same review discipline reasonably applies to AI-generated instructions (e.g., produced by the natural-language creation flow or the migration plugin — "treat the output as a first draft"). [CAT — new-orchestrator-resources]
- **Safety boundaries belong in instructions as policy, not as the only defense:** decline/redirect topics, escalation triggers, and grounding-only rules ("answer only from knowledge sources") raise the bar and improve behavior, but must be paired with deterministic controls for guarantees. [OFFICIAL guidance + INFERRED]
- **ALM/governance:** the agent (with its instructions and Skills) travels through Power Platform solutions, so instruction changes can be reviewed, versioned, and promoted like other solution components. [CAT/OFFICIAL — Skills post referencing solutions overview]

## 6. Performance and maintainability implications

- **Every instruction token is paid on every turn.** Instructions are always fully in context [CAT]; under Copilot Credits billing, verbose instructions raise per-turn cost as well as latency. [INFERRED from OFFICIAL billing + CAT context model]
- **Length degrades adherence.** Microsoft's guidance: keep instructions concise; overly long instructions cause latency, timeouts, prompt-handling issues. [OFFICIAL, via community quoting] Community measurement (unofficial, single-author): agents with ~1,000–1,500-character instructions outperformed 6,000+-character agents on orchestration accuracy, tool selection, and coherence — the "lost in the middle" effect. [Third-party — zenchong.substack.com; not Microsoft data]
- **Instructions-only patterns are the least consistent way to force exact behavior.** In CAT's three-method oversummarization test, instructions-only was "somewhat inconsistent even with this test case being the only thing in the instructions. Additional instructions may make it even less consistent" — a direct observation that instruction rules interfere with each other as they accumulate. [CAT — oversummarization]
- **Offloading to Skills keeps the context lean.** "Ten Skills cost you ten short descriptions, not ten full sets of instructions, in every turn." Moving situational guidance out of instructions reduces context saturation, can improve accuracy and cut latency/credits ("fewer knowledge searches, tool calls, and reasoning loops") — but CAT is careful: accuracy/speed gains are use-case dependent, "evaluate it rather than assume it." [CAT — Skills post]
- **Maintainability:** a single ever-growing instruction blob is hard to reason about, review, and version; the modular alternative (lean instructions + named Skills) lets you change one behavior without regression risk to the rest. [CAT] Debugging surfaces: the agent's reasoning view (shows instruction/Skill-driven decisions), transcripts, and evals; CAT recommends running evals against core journeys after any instruction/architecture change. [CAT — Skills post, new-orchestrator-resources]
- **Naming discipline is a performance feature.** Because orchestration matches on component names/descriptions, instructions that reference tools/knowledge work reliably only when those components have accurate, specific names and descriptions — fix descriptions before adding instruction hints. [OFFICIAL — Learn guidance]

## 7. Architecture guidance and anti-patterns

**Guidance (positive patterns):**

1. **Smallest-component rule.** "Every behavior belongs in the smallest component that makes it reliable and inspectable" — instructions: always-true; knowledge: searchable facts; tools: system actions; memory: persistent context; Skills: situational procedures; connected agents: specialist domains. [CAT — new-orchestrator-resources, quoting the official Deep Dive deck]
2. **Write lean, structured instructions.** Distinct headings per concern; bullets for parallel rules; numbered lists only when order matters; short imperative directives over narrative; concrete named references to tools/knowledge; a small number of concrete examples where format matters. [OFFICIAL — Learn instruction-writing guidance family]
3. **Cover the canonical slots:** role/mission; tone/style; in-scope and out-of-scope (decline/redirect); ambiguity handling; escalation/handoff triggers; grounding and citation policy; global tool-use rules. [OFFICIAL — Learn agents-experience/authoring-instructions synthesis]
4. **Prefer positive framing.** "Focus on what Copilot should do, not what to avoid" — state the desired behavior, then add explicit prohibitions only for true red lines. [OFFICIAL — Learn declarative-agent-instructions principle, applicable across Copilot instruction surfaces]
5. **For multi-source grounding, spell out the plan shape once, globally:** which source is authoritative, when to cross-check, how to merge (the MCP-data + knowledge-corrections pattern). [CAT — influence-orchestration]
6. **Codify the expensive path.** If the agent repeatedly re-derives a procedure through the agentic loop, freeze the discovered procedure into a Skill (instructions + generalized pseudocode script) rather than growing the instructions — CAT turned a 15-minute reasoning marathon into a 15-second scripted call this way. [CAT — redlining post]

**Anti-patterns:**

- **The instruction blob.** "An agent shouldn't be one instruction blob with 43 tools and a prayer." [CAT — new-orchestrator-resources]
- **Situational procedures in always-on instructions** — bloats every turn, degrades adherence; move to Skills. [CAT]
- **Data/policy text pasted into instructions** — belongs in knowledge; instructions should say how to use knowledge, not contain it. [CAT/OFFICIAL component model]
- **Using instructions where you need a guarantee** — verbatim output, citation stripping, compliance-critical formatting: use deterministic code/tools; instructions alone were the least consistent method in CAT testing. [CAT]
- **Duplicating what descriptions already convey** — restating every tool's obvious purpose in instructions adds tokens without routing value; add hints only for genuine ambiguity. [OFFICIAL — generative-mode-guidance; CAT]
- **Negative-only rule piles** — long "never do X" lists are weaker signals than positive behavioral specs. [OFFICIAL principle]
- **"Archaeology with YAML" migrations** — porting every classic topic into instructions (or every topic into a Skill) instead of re-mapping responsibilities to the new component model. [CAT]
- **Treating instructions as a security control** — injection-resistant guarantees must come from platform controls, not prompt text. [INFERRED + third-party research]
- **Vague scope language** — if two reasonable makers would disagree on when a rule (or Skill) applies, it isn't specific enough yet. [CAT — Skills post, stated for Skill descriptions; applies to instruction scope rules by the same routing logic — INFERRED extension]
- **Accumulating contradictory rules** — additional instructions can reduce adherence to existing ones; re-test (evals) after each addition. [CAT — oversummarization observation + agentic-improvement-loop practice]

## 8. Sources

**Local files (read in full):**
- /workspace/microsoft/mcscatblog/_posts/2026-01-23-copilot-studio-defeating-oversummarization.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-15-redlining-documents-new-copilot-studio-experience.md
- /workspace/microsoft/mcscatblog/_posts/2025-12-15-remove-citations-in-copilot-studio-answer.md
- /workspace/microsoft/mcscatblog/_posts/2026-06-15-modern-mcs-agent-skills.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-07-new-orchestrator-resources.md
- /workspace/microsoft/mcscatblog/_posts/2025-11-11-influence-orchestration-knowledge.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-10-skills-for-copilot-studio.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-19-open-the-hood-technical-reference.md (read; minimally used)

**Web (Microsoft Learn pages surfaced/synthesized via WebSearch; direct fetch blocked):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/authoring-instructions — Configure agent details and instructions (GitHub Copilot)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-instructions — Write agent instructions (classic/generative orchestration; slash references)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-mode-guidance — Configure high-quality instructions for generative orchestration
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/classic-vs-new — Choose a harness
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview — Build (GitHub Copilot) overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/build-overview — Build an agent (preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview — Skills overview for agents
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-copilot-studio — Knowledge overview (new experience)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview — Overview of usage-based billing (Copilot Credits)
- https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-instructions — Write effective instructions (structure/goal-action-transition/positive framing principles)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas — Requirements and quotas

**Web (non-Microsoft, corroboration/community; used with caution):**
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/more-powerful-agents-and-workflows-for-autonomous-business-processes-introducing/4542969 — harness announcement (Microsoft Community Hub)
- https://github.com/microsoft/vscode-copilotstudio/issues/51 — 8,000-character instructions field limit (classic)
- https://techcommunity.microsoft.com/discussions/microsoft365copilot/ai-agent-instructions-character-limit-in-studio-license/4468072 — instructions character limit discussion
- https://zenchong.substack.com/p/your-copilot-studio-agents-instructions — unofficial instruction-length performance data
- https://lukoplt.blogspot.com/2026/08/copilot-studio-github-copilot-harness.html and https://powerplatstack.substack.com/p/copilot-studios-new-harness-heres — Aug 2026 GA/licensing signals (third-party)
- https://venturebeat.com/security/microsoft-salesforce-copilot-agentforce-prompt-injection-cve-agent-remediation-playbook and https://princetonits.com/blog/ai-security/hardening-agent-instructions-securing-the-soft-layer-of-copilot-studio-governance/ — prompt-injection / instructions-as-soft-layer research
