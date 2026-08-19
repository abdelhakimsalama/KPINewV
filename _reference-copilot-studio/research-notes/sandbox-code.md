# sandbox-code

Research note — Copilot Studio agent sandbox / code execution (new "agents experience" on the GitHub Copilot harness), plus the related computer use agent (CUA) capability. Date of research: 2026-08-19. Claims are tagged [OFFICIAL] (documented Microsoft behavior, Learn or Microsoft blog), [CAT] (Copilot Studio CAT blog guidance/practice), [3P] (third-party reporting used only for status/timeline corroboration), or [INFERRED] (analyst reasoning).

## 1. What it is and how it works

**The agent sandbox** is the code-execution environment that every Copilot Studio agent built on the new GitHub Copilot harness (the natural-language-first "agents experience") gets by default. It is described by the CAT team as "a container with a Python runtime, local files, preinstalled libraries, and shell tools, all managed by Copilot Studio" [CAT: 2026-07-20 agent-sandbox post]. Microsoft Learn's harness comparison states that the GitHub Copilot harness "runs each task in a secure sandbox" governed by Copilot Studio, and that this lets agents process large files and natively create or edit Word, Excel, PowerPoint, and PDF outputs [OFFICIAL: learn.microsoft.com harnesses-overview, via search synthesis].

**Why it exists.** The motivating principle: an LLM should not directly perform calculations or emit large exact payloads (a valid `.docx`, a filled spreadsheet, long JSON) because it *predicts* rather than *computes*; what LLMs are good at is writing the code that computes. The sandbox is where that code runs [CAT: agent-sandbox post].

**How code reaches the sandbox** — two paths, chosen by the model at runtime, not by the maker per conversation [CAT: agent-sandbox post]:

1. **Code generated for the task.** The agent writes Python, runs it, inspects output/tracebacks, revises, and retries — the full agentic loop. Best for novel work (understanding an unfamiliar export, ad-hoc charting). Trade-off: slower and implementation may vary between runs.
2. **A script packaged in a Skill.** Skills (SKILL.md + optional `scripts/`, `references/`, `assets/` folders) can bundle pre-written, reviewed Python that the agent executes immediately. Faster and more consistent for repeatable work; versionable like any code asset [CAT: agent-sandbox post; 2026-06-15 modern-mcs-agent-skills post].

**Observed contents.** A CAT-run inventory of an otherwise-empty agent on 2026-07-21 (using the `agent-harness-explorer` Skill) found **Python 3.12.9** running in a **container**, with **99 Python libraries**, **11 built-in tools**, **8 Skills**, and no MCP servers configured [CAT: agent-sandbox post — a point-in-time observation, not a documented contract]. The CAT guidance is explicitly that "the exact package names are less important than the agentic loop they enable," and the recommended way to know what is installed is to ask the agent or run the harness-explorer Skill, because contents may change over time [CAT].

**Known-available / known-absent libraries** (from the CAT redlining build log, 2026-07-15): `pdfplumber`, `python-docx`, `pypdfium2`, `lxml`, `difflib` (stdlib), and `requests` (installed but useless externally — see below) are present; `pdf2docx` and `pymupdf` are **not** available, and **there is no `pip install`** — "what ships in the container is what you get" [CAT: redlining post; agent-sandbox post].

**File flow in.** Files arrive in the sandbox from (a) Knowledge retrieval — when the agent retrieves files from Knowledge they "land in the sandbox," so the agent can open the *whole file* and analyze it with Python rather than being limited to retrieval snippets (Copilot Studio uses the sandbox for its own retrieval pipeline) [CAT: agent-sandbox post]; (b) user uploads during conversation; (c) assets/scripts bundled inside Skills [CAT: redlining post].

**File flow out.** The sandbox is a working area, not storage. Output files (e.g., a redlined `contract-redlined.docx`) must be **returned to the user** in the conversation or **saved somewhere durable via a configured Tool** (connector/MCP). Nothing persists after the conversation; Agent Memory persists facts/context, *not files* [CAT/OFFICIAL: agent-sandbox post citing Learn memory-overview].

**Network.** The sandbox has **no outbound network path**. Code cannot call an API, send email, or write to SharePoint regardless of what it imports; `requests` is installed but nothing built with it can leave the sandbox. All external reach happens only through configured Knowledge sources and Tools (connectors, MCP servers), which remain under DLP/governance [CAT: agent-sandbox post; corroborated by [OFFICIAL] M365 code-interpreter security architecture: VMs "don't allow any inbound or outbound traffic"].

**Related capability: computer use agents (CUA).** A separate tool (not the sandbox) that lets an agent operate Windows apps and websites through the UI — clicking, typing, navigating — driven by vision and natural-language goals, for systems with no API [CAT: 2026-01-09 Cloud PC pool post; OFFICIAL: learn.microsoft.com/microsoft-copilot-studio/computer-use]. Three runtimes [CAT/OFFICIAL]:
- **Hosted browser** — Microsoft-managed, zero setup; browser plus built-in Windows apps on a non-customer-Entra-joined VM; not Intune-managed; explicitly not recommended for production and may be throttled [OFFICIAL: configure-where-computer-use-runs, via search].
- **Cloud PC pool** — Microsoft-hosted Windows 11 Cloud PCs ("Windows 365 for Agents"), Entra-ID-joined and Intune-enrolled, auto-scaling, provisioned in your Power Platform geography; SSO into internal systems; enterprise-governable [CAT: Cloud PC pool post; OFFICIAL: use-cloud-pc-pool]. **Preview** as of research date [OFFICIAL].
- **Bring your own machine (BYOM)** — your Windows machine/VM with Power Automate Machine Runtime, with the machine's "Enable for computer use" toggle on; enabling it removes the machine from the standard desktop-flow pool and breaks existing desktop-flow connections tied to it [CAT: 2026-04-01 legacy-desktop-apps post].

## 2. When to use it / when NOT to use it

**Use the sandbox when** [CAT: agent-sandbox post, unless noted]:
- Exact arithmetic matters: prorated bonuses, what-if analyses, formula validation — "arithmetic done in code rather than in the model's head."
- Building or transforming files: cleaned workbooks, calculated summaries, charts; comparing documents and returning a redlined `.docx` with genuine Word tracked changes; extracting PDF content, applying checks, producing findings reports; turning data into presentations.
- Working across *entire* structured files from Knowledge (every row of a CSV), beyond what retrieval snippets allow.
- You would otherwise "build a separate service for every calculation or file transformation" — the sandbox removes that need for local, self-contained compute [CAT].

**Sandbox vs. external services** [INFERRED, grounded in the above]: the sandbox wins when the work is (a) stateless per conversation, (b) needs no external calls, (c) operates on files already in the conversation/Knowledge, and (d) benefits from LLM-adaptive code. An external service (connector, Azure Function, MCP server) wins when you need network access, secrets, persistent state, packages not in the container, long-running or scheduled jobs, or hard SLAs.

**Do NOT rely on the sandbox for**:
- Anything requiring outbound network I/O — impossible by design [CAT/OFFICIAL].
- Persistence across conversations — the sandbox is temporary; "do not design the next conversation around finding that same file in the sandbox" [CAT].
- Packages outside the preinstalled set — no `pip install` [CAT: redlining post].
- Deterministic high-volume pipelines where per-run code generation variance is unacceptable — package a reviewed Skill script instead, or move the work to a deterministic workflow/flow [CAT + INFERRED].

**CUA vs. RPA decision** (for UI-level automation, from the CAT comparison) [CAT: legacy-desktop-apps post]: use RPA (Power Automate desktop flows) when the UI is stable, rules are clear, speed/volume matter, an RPA team owns it, and GA-grade stability is mandatory; use CUA when UIs shift or vary, decisions are fuzzy and need visual reasoning/self-correction, the RPA backlog is full, and retry tolerance exists (e.g., read-only scenarios). CUA is outcome-based, not action-based — instructions are goals, and it will use any means visible on screen to achieve them [CAT].

## 3. Classic-experience comparison (what it replaces or simplifies)

The classic (standard-harness) world had **narrower, opt-in code-execution features**, and the new sandbox generalizes them:

- **Classic "code interpreter"** exists in two scoped forms: (1) in **prompts/Prompt Builder** — generate and execute Python inside a prompt (makers can also define Python at design time); announced **generally available** in Copilot Studio and Copilot Studio lite [OFFICIAL: Microsoft Copilot blog "What's new September 2025"; Learn code-interpreter-for-prompts]; (2) for **analyzing structured data in knowledge/uploads** (CSV/Excel analysis, charts) — **(preview)** per the Learn page title as of research date [OFFICIAL: knowledge-code-interpreter-structured-data]. Both require explicit toggles (Settings > Generative AI > File uploads + Code interpreter) [OFFICIAL via search synthesis].
- **The new agent sandbox is ambient, not a toggle-scoped feature**: it is part of the harness itself, used even by the Knowledge retrieval pipeline, available for model-generated code and Skill scripts alike [CAT: agent-sandbox post] [INFERRED: contrast with classic opt-in model].
- **What it replaces/simplifies** [CAT + INFERRED]:
  - Custom Azure Functions / Power Automate cloud flows built solely to do math, transform files, or generate documents for a classic bot — now done in-conversation.
  - Classic topic authoring with Power Fx expressions for calculations — replaced by real Python.
  - Document-generation services (Word/PDF assembly APIs) for many cases — the sandbox natively builds `.docx` (including OOXML tracked changes), Excel, PowerPoint, PDF outputs [CAT: redlining post; OFFICIAL: harnesses-overview].
  - Classic per-file reading limits: without code interpreter the classic experience reads only ~30,000 characters per file; code execution removes that ceiling for supported structured-data scenarios [OFFICIAL: Learn FAQ/add-inputs, via search — note these numbers are documented for the classic prompt/file-input surface, not the new sandbox].
- **CUA vs. classic RPA**: CUA replaces selector-based, visually scripted desktop flows with vision-driven, natural-language, self-correcting automation — at the cost of latency and determinism (see §6) [CAT: legacy-desktop-apps post].
- **No migration path**: an agent created on one harness cannot be transferred to the other; building on the new harness is one-way [3P: multiple partner reports of the GA announcement, e.g., FiveForward/Schneider; STATUS UNVERIFIED on Learn].

## 4. Limitations, GA/preview status, licensing notes

**Status:**
- **GitHub Copilot harness / agents experience** (which includes the sandbox): **generally available 2026-08-03**, announced via message center MC1442234 [3P: multiple Microsoft-partner writeups; consistent with Learn agents-experience docs carrying no preview label]. [INFERRED] The sandbox itself carries no separate status flag in the 2026-07-20 CAT post; treat it as GA with the harness. [STATUS UNVERIFIED for any per-feature sandbox preview flags.]
- **Classic code interpreter in prompts**: GA [OFFICIAL: Microsoft blog Sept 2025]. **Code interpreter for structured data in knowledge**: preview [OFFICIAL: Learn page title].
- **Computer use**: public preview from 2025-09-10 (First Release + US regions; during preview only US-region environments) [OFFICIAL: Microsoft Copilot blog preview announcement; CAT legacy-desktop-apps post]; **GA announced 2026-05-13**, expanding to all commercial Power Platform geographies, with sovereign clouds (GCC/GCC High/DoD) excluded initially [3P: digitalapplied GA deep-dive and others; the Learn "computer-use" page title no longer shows "(preview)" — corroborating]. Models: OpenAI CUA and Claude Sonnet 4.5 GA; Claude Sonnet 4.6 / Opus 4.6 listed "Experimental" [3P summarizing the Learn model table; STATUS UNVERIFIED at first hand]. **Cloud PC pool runtime: still preview** [OFFICIAL: use-cloud-pc-pool "(preview)"]. Note the CAT 2026-04-01 post's "CUA is still in preview" caveat predates GA and is stale on that point [CAT, stale].

**Sandbox limits (documented or observed):**
- No outbound/inbound network [CAT/OFFICIAL]. No `pip install`; fixed preinstalled library set (~99 libs observed 2026-07-21, subject to change) [CAT]. Ephemeral storage only [CAT].
- The M365 code-interpreter security architecture (which Learn cites as covering "Copilot and agents") documents: fresh isolated Azure VM per execution, destroyed after session with no data persisted; resource quotas on **time, CPU, memory, and disk** (exact values not published); real-time code scanning with session termination on suspicious activity [OFFICIAL: code-interpreter-security]. [INFERRED] The Copilot Studio agent sandbox is governed by the same or a closely related architecture; Microsoft has not published a Copilot-Studio-specific quota sheet.
- Classic-surface numbers (documented for prompt/file-input code interpreter, NOT verified for the new sandbox): 15 MB per uploaded file; 30,000 characters read per file without code interpreter; document processing capped at 100 seconds; documents must be under 50 pages; multi-file analysis or multi-file output in a single prompt not supported [OFFICIAL: Learn FAQ-code-interpreter / add-inputs-prompt, via search].

**Licensing / billing:**
- The GitHub Copilot harness uses **Copilot Credits, usage-based**, and **billing starts at build time**: creating via natural language, previewing, testing, and running evals all consume credits — before publish [OFFICIAL: Learn billing-credit-overview via search; CAT: 2026-08-07 cost-governance post]. Capacity packs: 25,000 credits at $200/pack/month (US list); pay-as-you-go $0.01/credit via Azure subscription [OFFICIAL: Copilot Studio pricing page / licensing guide, via search; figures as of mid-2026]. Agents created before 2026-08-03 keep prior pricing until 2026-09-01, then move to credit billing [3P; STATUS UNVERIFIED].
- There is **no separate sandbox meter** in any source found — sandbox execution is subsumed in harness credit consumption [INFERRED from absence; flag if a dedicated meter appears].
- **Cloud PC pool**: consumptive pay-as-you-go via Azure meters; no separate Windows or Power Automate licenses needed; embedded test-chat usage not billable; **50 free hours per tenant** of Cloud PC pool usage for published autonomous agents [OFFICIAL: use-cloud-pc-pool, via search].
- Admin cost controls: environment-level credit allocation with Alert/TenantPool/PayGo/Deny enforcement rules, and per-agent monthly credit limits (PPAC **Licensing > Copilot Studio > Manage Agents**, or the licensing API `resource-threshold` endpoint); harness agents are discoverable via the Power Platform Inventory property `isCLIAgent = true` [CAT: cost-governance post, citing official APIs].

## 5. Security and governance implications

- **Egress is architecturally closed.** Sandbox code cannot exfiltrate: no outbound path exists, so the only external reach is through maker-configured Knowledge and Tools, which stay inside Power Platform DLP and data policies. For admins this is the core reassurance: "everything the agent does externally stays within your governance controls" [CAT: agent-sandbox post; OFFICIAL: admin-data-loss-prevention referenced therein].
- **Isolation.** Per the official code-interpreter security architecture: isolated per-session Azure VMs, no cross-session sharing, fresh VM per run, destroyed afterwards, no persisted data; runtime monitoring scans executing code and kills sessions on malicious patterns (e.g., privilege-escalation or restricted-file access attempts) [OFFICIAL: code-interpreter-security]. Data access is limited to files/inputs explicitly provided in session — no ambient tenant data [OFFICIAL].
- **Skills are a trust surface.** Because Skills can bundle executable scripts that run in the sandbox, any Skill you did not write (community, AI-generated, reused) must be reviewed like untrusted code — check for prompt injection, tool misuse instructions, and behavior not matching the description [CAT: modern-mcs-agent-skills post].
- **Cost is now a security-adjacent governance concern**: maker experimentation consumes credits pre-publish, so ungoverned dev environments create financial exposure; apply environment credit allocations, disable tenant-pool draw for maker environments, and set default per-agent limits [CAT: cost-governance post].
- **CUA governance** [OFFICIAL, via search of human-supervision-computer-use / monitor-computer-use / administer-computer-use]: session replay with screenshots; step-level action logs (type, coordinates, timestamps); run summaries (duration, action counts, escalations); logs stored in Dataverse by default with optional Purview audit export (activity `CUAOperation`); human-supervision reviewers can be assigned and are notified when the model detects potentially malicious instructions, deciding continue/stop; Purview Information Protection can redact sensitive on-screen fields before screenshots are stored; only the tool's maker gets human-review requests and verbose logs. Hosted browser is un-governed territory (not Entra-joined, not Intune-managed) — keep it out of production and internal-resource scenarios; Cloud PC pool or hardened BYOM with a dedicated CUA account is the enterprise path [CAT: Cloud PC pool + legacy-desktop-apps posts; OFFICIAL: computer-use best practices].
- [INFERRED] Residual sandbox risks to manage: prompt-injected *content* in uploaded files could steer generated code (mitigated by egress denial — impact is limited to in-conversation outputs), and sandbox-produced files flow onward through Tools, so DLP on connectors remains the enforcement point for where outputs land.

## 6. Performance and maintainability implications

- **Generated code is slow the first time; codified scripts are fast every time.** The CAT redlining build is the canonical datapoint: letting the agentic loop derive a working redline engine took ~15 minutes of fail/rewrite cycles; freezing the discovered logic into a generalized Skill script cut the same task to ~15 seconds — roughly **60x** [CAT: redlining post]. The four-phase method (run with no code → let it loop → strip hardcoding → ship generalized pseudocode as `scripts/*.py`) is reusable practice [CAT].
- **Repeatability**: model-generated code may vary between runs; Skill scripts run identically and can be tested, versioned, and shipped through normal ALM, then guarded with evals (the eval quality-gate pattern in Azure DevOps) [CAT: agent-sandbox post].
- **Library churn risk**: preinstalled packages "may change in the future" [CAT: redlining post] — Skill scripts should stick to stable, definitely-present libraries and degrade gracefully; re-run the harness-explorer inventory (optionally snapshotting via Agent Memory) to detect changes over time [CAT: agent-sandbox post].
- **CUA latency**: goal-based reasoning navigates UI step-by-step and is materially slower than deterministic RPA at machine speed — a stated poor fit for high-volume or time-sensitive scenarios [CAT: legacy-desktop-apps post]. The Separation-of-Concerns alternative (scheduled desktop flow → Dataverse table → agent Knowledge) trades freshness for instant, scalable, auditable reads [CAT].
- [INFERRED] Sandbox work is bounded by per-session resource quotas (time/CPU/memory/disk) [OFFICIAL basis], so very large datasets or long computations belong in external services; and every sandbox iteration consumes Copilot Credits, so verbose fail/rewrite loops have a direct cost — another argument for codified Skills in production.

## 7. Architecture guidance and anti-patterns

**Guidance:**
1. **Route work to the right executor**: LLM for language/judgment; sandbox for computation and file assembly; Tools/connectors/MCP for anything external; workflows/flows for deterministic multi-step processes; CUA only where no API exists and UI automation is unavoidable [CAT synthesis + INFERRED].
2. **Novel → generated; repeatable → Skill script.** Give the model room to write code for one-off analysis; package reviewed scripts with clear descriptions for anything recurring, and let the model choose at runtime [CAT: agent-sandbox post].
3. **Codify the loop's discovery** (redlining method): prototype with the agentic loop, then de-hardcode and freeze into a Skill so production runs execute instead of re-derive [CAT: redlining post].
4. **Design explicit file egress**: every conversation that produces a file must end by returning it to the user or persisting it via a Tool (SharePoint/OneDrive/Dataverse connector) [CAT: agent-sandbox post].
5. **Verify the environment, don't assume it**: inventory the sandbox (harness-explorer Skill) before writing Skill scripts; write against confirmed libraries [CAT].
6. **Gate with evals + ALM**: treat Skill scripts as code assets — eval gates in CI (Azure DevOps pattern), solution-based deployment [CAT: agent-sandbox post referencing eval-gate post and Learn ALM guidance].
7. **Govern credits from day one**: classify environments (maker dev vs. funded production), allocate credits, set per-agent limits, automate discovery via `isCLIAgent` [CAT: cost-governance post].
8. **For CUA**: prefer Cloud PC pool (or hardened BYOM with dedicated CUA account) for anything touching internal systems; hosted browser for experimentation only; write outcome-oriented instructions; enable human supervision and Purview audit [CAT + OFFICIAL].

**Anti-patterns:**
- Designing conversations that expect files or state to persist in the sandbox between sessions [CAT].
- Using Agent Memory as a file store — it holds facts/context only [CAT/OFFICIAL].
- Writing Skill scripts that assume `pip install` or unlisted packages [CAT: redlining post].
- Lossy format conversion inside the sandbox pipeline (e.g., DOCX→PDF→DOCX destroyed formatting and produced noise redlines; read formats natively instead — `pdfplumber` for PDFs, operate on the Word template directly) [CAT: redlining post].
- Letting the LLM do arithmetic or emit exact large payloads directly instead of via sandbox code [CAT: agent-sandbox post].
- Rebuilding a calculation/file-transform microservice externally when the sandbox already covers it (cost + latency + surface area for no benefit) [CAT/INFERRED].
- Installing unreviewed community Skills containing scripts [CAT: modern-mcs-agent-skills].
- Using CUA where a stable API/connector or deterministic RPA exists, or for high-volume time-critical paths [CAT: legacy-desktop-apps post].
- Enabling "computer use" on a machine that active desktop flows depend on (it breaks those connections) [CAT: legacy-desktop-apps post].
- Ungoverned maker environments with tenant-pool credit draw enabled [CAT: cost-governance post].

## 8. Sources

**Local (CAT blog clone, read in full):**
- /workspace/microsoft/mcscatblog/_posts/2026-07-20-copilot-studio-agent-sandbox.md
- /workspace/microsoft/mcscatblog/_posts/2026-07-15-redlining-documents-new-copilot-studio-experience.md
- /workspace/microsoft/mcscatblog/_posts/2026-01-09-cua-cloudpcpool-in-copilotstudio.md
- /workspace/microsoft/mcscatblog/_posts/2026-04-01-connecting-legacy-desktop-apps-to-copilot-studio.md
- /workspace/microsoft/mcscatblog/_posts/2026-01-26-meeting-transcript-analyzer.md (read; minimal sandbox relevance — autonomous agent + connectors example)
- /workspace/microsoft/mcscatblog/_posts/2026-08-07-copilot-harness-cost-governance.md
- /workspace/microsoft/mcscatblog/_posts/2026-06-15-modern-mcs-agent-skills.md (grep excerpts: Skill structure, scripts, trust warning)

**Microsoft Learn / Microsoft official (via WebSearch synthesis; direct fetch blocked):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/faq-code-interpreter
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/code-interpreter-for-prompts
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-code-interpreter-structured-data
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-inputs-prompt
- https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/code-interpreter-security (also published under /microsoft-365/copilot/extensibility/)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/computer-use
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/configure-where-computer-use-runs
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/use-cloud-pc-pool
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/human-supervision-computer-use
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/monitor-computer-use
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/administer-computer-use
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-computer-use
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/computer-use-is-now-in-public-preview-in-microsoft-copilot-studio/
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/whats-new-in-copilot-studio-september-2025/ (code interpreter GA)
- https://www.microsoft.com/en-us/microsoft-365-copilot/pricing/copilot-studio
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/more-powerful-agents-and-workflows-for-autonomous-business-processes-introducing/4542969
- https://microsoft.github.io/cat-agent-skills/skills/agent-harness-explorer/ (referenced from CAT post)

**Third-party (status/timeline corroboration only):**
- https://www.digitalapplied.com/blog/copilot-studio-computer-use-agents-ga-deep-dive (CUA GA 2026-05-13, geo expansion, model table)
- https://fiveforward.co.uk/insights/copilot-studio-github-copilot-harness-what-changes-and-what-it-costs/ and https://www.schneider.im/microsoft-copilot-studio-github-copilot-harness-available/ (harness GA 2026-08-03, MC1442234, pricing transition)
- https://www.aguidetocloud.com/blog/copilot-credits-explained/ and https://samexpert.com/copilot-studio-licensing-guide/ (credit pricing corroboration)
