# Exercise 05: Woodgrove Contract Review Agent

## 1. Business need

Woodgrove's legal-ops team receives supplier contracts (10-80 page PDFs and DOCX). For each contract they must: extract key clauses (liability, indemnification, termination, payment, IP, data protection), compare each against the company playbook, flag deviations by severity, and produce **a redlined Word file with genuine tracked changes** plus a findings summary. Today this is 2-4 hours of paralegal work per contract. The process is repeatable — fixed playbook, fixed template, fixed severity taxonomy — exactly the CAT criterion for Copilot Studio over ad-hoc Cowork use: a specific process/template/pipeline exists.

## 2. Classic-style architecture

In classic (Standard-harness) Copilot Studio this scenario is barely buildable, and what is buildable is heavy:

**Topics (9):** `Greeting`, `Upload Contract` (Question node, File entity, "Include file metadata"), `Route Document Type` (PDF vs DOCX condition branches), `Extract Clauses`, `Playbook Comparison`, `Deviation Report`, `Request Redline`, `Escalate to Counsel`, `Fallback/Unsupported`. Roughly **30 condition branches** and **~25 topic/global variables** (fileContent, clauseTable, deviationList, severityCounts, matterId…) with Power Fx glue such as `{ contentBytes: Topic.contract.Content, name: Topic.contract.Name }`.

**Power Automate flows (5):** `Extract Contract Text` (chunking — classic reads only ~30,000 characters per file without code interpreter, and prompt document processing caps at 50 pages/100 seconds, so an 80-page contract must be split), `Compare Clause Batch` (loops an AI Builder prompt per clause), `Assemble Findings Report`, `Generate Redline` (calls out to external compute), `Save to SharePoint`.

**AI Builder prompts (2):** clause extraction, clause-vs-playbook comparison.

**External service (1 Azure Function):** classic has no native code execution that can emit OOXML tracked changes, so redlining requires a custom OpenXML/`python-docx` service — its own hosting, auth, ALM, and the 100-second flow-tool timeout looming over every call.

**Component count: 9 topics + 5 flows + 2 prompts + 1 Azure Function = 17 major components**, plus ~30 branches, ~25 variables, and per-file chunking logic. Even then, the 1 MB flow-return cap forces a store-and-link pattern for the redlined file.

## 3. New-experience redesign

One GitHub Copilot harness agent (GA 2026-08-03; several sub-features below still preview — flagged in §13).

- **Instructions (summary):** role ("contract review assistant for Woodgrove legal-ops"), scope and refusals (supplier contracts only; no litigation advice), the always-true pipeline shape ("for any uploaded contract, run the contract-clause-review skill; every review ends with the redlined file OR a findings-only report for PDFs, plus the findings summary citing playbook rule IDs"), citation policy, escalation rule ("critical-severity deviations: tell the user to route to counsel"), and the save rule ("save to SharePoint only when the user explicitly asks").
- **Knowledge (1 source):** the **playbook (uploaded file / file collection)** for ad-hoc Q&A ("what does our playbook say about liability caps?") with citations. Contracts are **NOT** knowledge — they arrive as conversation uploads and land in the ephemeral sandbox (§6).
- **Skills (1):** `contract-clause-review` — packaged, reviewed redlining pipeline (§7) with a routing description: "Use when the user uploads a supplier contract or asks to review, extract clauses from, compare, or redline a contract. Handles the initial request and every follow-up refinement in the same review. Do not use for general playbook questions without a contract."
- **Tools (1):** SharePoint connector, end-user credentials — "Save review outputs to the Contract Review library" (durable file egress from the ephemeral sandbox).
- **Workflows:** none (§9).
- **Memory:** OFF (§10).
- **Connected agents:** none (§11).
- **Model:** a deep-reasoning-class model. Claude Sonnet 4.6-class is attractive (strong long-document behavior, per-chunk citations), **but** Anthropic models process outside Microsoft-managed environments (Anthropic as subprocessor) — legal must sign off; otherwise GPT-5 Reasoning-class. Model choice is a governance decision here, not just quality.

**Total: instructions + 1 knowledge source + 1 skill + 1 tool + model config = 5 components.**

## 4. Removed components

| Component | Classic | New | What disappears |
|---|---:|---:|---|
| Topics | 9 | 0 | Orchestrator + skill routing replace trigger phrases and branching |
| Condition branches | ~30 | 0 | Reasoning loop handles routing; format branch lives in skill references |
| Variables / Power Fx | ~25 | 0 | No variable concept; conversation history + sandbox files carry state |
| Power Automate flows | 5 | 0 | Sandbox does extraction, comparison, assembly, redlining in-conversation |
| AI Builder prompts | 2 | 0 | Folded into the skill's instructions |
| Azure Function (redline) | 1 | 0 | `scripts/redline.py` in the skill, run in the sandbox |
| Knowledge sources | 1 | 1 | Playbook stays |
| Connector tools | 1 | 1 | SharePoint save stays |
| **Total major components** | **17 (+55 branches/vars)** | **5** | **~70% fewer components; chunking, 1 MB return caps, and external hosting eliminated** |

## 5. Role of Instructions

**In:** identity, audience, scope/refusal boundaries, the always-true output contract (file + findings summary, playbook rule IDs cited), severity language, escalation trigger, the explicit-consent save rule, and one routing hint naming the skill and the SharePoint tool (components are referenced by name only after their own descriptions are accurate).

**Deliberately NOT in:** the review procedure, clause taxonomy, playbook rules, redlining method, or format-specific handling — all situational, all in the skill (instructions are always fully in context and billed every turn; CAT's data shows long rulebooks degrade adherence). No playbook text pasted in (that's knowledge/skill-reference material). No security guarantees — instructions are probabilistic, not an enforcement boundary; anything that must never happen is enforced by tool configuration and DLP, not prose.

## 6. Role of Knowledge

Two distinct file populations, deliberately split:

1. **Playbook as uploaded-file knowledge** — for conversational Q&A with citations outside a review ("is a 30-day cure period acceptable?"). Uploaded-file limits are comfortable (512 MB/file, 500 files/agent). Governance note: **uploaded-file knowledge has no RBAC** — every agent user sees answers from all uploaded content. Acceptable for the playbook (whole team may see it); it is exactly why **contracts are never added as knowledge**.
2. **Contracts as conversation uploads** — the exercise's core mechanic: uploaded files **land in the sandbox**, where the agent opens the *whole file* with Python rather than retrieval snippets. A 10-80 page contract is analyzed clause-by-clause in full — the classic 30,000-character/50-page ceilings simply don't exist. This also keeps confidential supplier terms out of any persistent index; they live only for the conversation.

Knowledge is not used for the comparison step itself — top-N retrieval is the wrong contract for "check *every* rule," which needs the complete rule set (see §7).

## 7. Role of Skills

The `contract-clause-review` skill is the center of this architecture — the CAT redlining pattern applied end-to-end:

```text
contract-clause-review/
├── SKILL.md            # procedure: extract → compare → grade → redline → summarize
├── scripts/
│   ├── extract_clauses.py   # python-docx / pdfplumber extraction, native format only
│   └── redline.py           # OOXML tracked-changes writer (w:ins / w:del)
├── references/
│   ├── playbook-rules.md    # machine-readable rules: id, standard text, fallbacks, severity
│   ├── docx-submissions.md  # DOCX path: operate on the file directly, full redline
│   └── pdf-submissions.md   # PDF path: pdfplumber; findings report + proposed-edits doc, NO redline
└── assets/
    └── findings-template.md
```

**Codify-the-loop:** prototype by letting the agentic loop derive the redlining code once (~15 minutes of fail/rewrite in CAT's build), strip hardcoding, ship the generalized script — production runs execute in ~15 seconds, the documented **~60x** speedup, with run-to-run consistency the live loop can't give. **The playbook rides in `references/`, not only in Knowledge:** during a review the agent needs the *complete, exact* rule set loaded with the procedure — not a relevance-ranked top-N retrieval that silently drops rule 7 of 12. Knowledge serves fuzzy Q&A; the skill reference serves exhaustive comparison. (Cost: two playbook copies to keep in sync — a documented maintenance duty with an owner.) Scripts use only confirmed-present libraries (`python-docx`, `pdfplumber`, `lxml`, `difflib`; no `pip install`; `pdf2docx`/`pymupdf` absent — verified via the harness-explorer inventory first). The format split honors the redlining lesson: **never DOCX→PDF→DOCX** — conversion destroys fidelity and produces noise redlines; PDFs get a findings report, honestly, because a PDF has no tracked changes.

## 8. Role of Tools

One tool: the **SharePoint connector** (end-user credentials, so saves respect the user's permissions and DLP). It exists because the sandbox is **ephemeral with no egress** — code cannot push files anywhere; outputs must be returned in chat or persisted via a configured tool, and legal-ops wants redlines in the matter library. The skill soft-points at it by name ("save via the SharePoint tool when the user confirms"); the pointer grants nothing — capability lives in the tool config. No REST API tools, no MCP: there is no external system in the loop, and every avoided tool keeps the orchestrator's decision space small.

## 9. Role of Workflows

**None in v1.** There is no transactional or irreversible action here: the agent produces documents; a human sends the redline to the supplier. The only side effect (SharePoint save) is a single connector call — wrapping one action in a workflow is pure overhead. If Woodgrove later adds an intake pipeline (new contract in a library → auto-review → post findings), that becomes a scheduled/event workflow calling the agent — a deterministic spine around the agentic core. Deliberately avoided now also because workflow-as-tool is still **[PREVIEW]** and carries the 100-second synchronous limit, which an 80-page review could breach.

## 10. Memory decision

**OFF.** Four reasons: (1) legal review must be reproducible — the same contract must yield the same findings for any reviewer; per-user memory injects invisible per-person variance into a compliance-relevant output. (2) Memory is user-private, user-deletable, and auto-expires at 28 days — the opposite of an audit trail; review records belong in SharePoint. (3) Memory stores facts, not files — it can't hold contracts anyway. (4) Memory is **[PREVIEW]**. **Test:** run the same test set against two agent copies (memory on/off), the memory-on copy first seeded with reviewer-preference conversations ("I only care about liability clauses"); diff findings completeness. If the memory-on agent omits clauses to please the persona, the risk is confirmed. Re-run per model change.

## 11. Connected Agents decision

**No.** One audience (legal-ops), one security boundary, one knowledge domain, a 1-tool/1-skill load nowhere near the 25-30-tool degradation zone. This is CAT's canonical "that's not three agents, that's one agent with skills" case. Delegation would add an orchestration hop, latency, and a second billing/audit surface for zero specialization gain. Revisit only if a genuinely separate domain with a different boundary appears (e.g., a procurement agent serving a different audience wanting to *call* contract review — then this agent gets published as a connected agent, unchanged).

## 12. Evaluation plan

Layered, because standard prompt-response evals can look green while real files fail silently:

- **Gold-standard corpus (the core):** 25 real (redacted) contracts + 10 synthetic ones with **seeded deviations** (known count, type, severity, location), plus edge cases: an 80-page contract, a scanned-ish PDF, a DOCX with existing tracked changes, a non-contract memo, a non-English contract. Bulk file-testing architecture: SharePoint holds inputs + expected findings; Power Automate drives runs; **deterministic script compare** on outputs — findings fields vs gold standard, plus OOXML checks on the redline (file opens, `w:ins`/`w:del` present, change count in tolerance, no body-text corruption). Deterministic checks first; LLM judges only for fuzzy quality.
- **Evaluate tab test sets [PREVIEW labels on agents-experience pages]:** single-response set (≤100 cases) for playbook Q&A with expected answers; conversational set (≤20 cases, 6 Q/A pairs) for upload → review → follow-up refinement. Custom grader: "findings summary cites playbook rule IDs; severity taxonomy respected."
- **Unsupported/ambiguity/hallucination cases:** "review this contract" with no file (must ask, not invent); litigation-advice request (must decline); "what does clause 14.2 say?" when no clause 14.2 exists (must say so); ambiguous "compare these" with two files.
- **Activation checks (activity trace):** skill fires on every contract-upload phrasing variant; does NOT fire for plain playbook questions; SharePoint tool never invoked without explicit request (wrong-tool-activation cases); skill stays active across follow-ups (the documented drop-out failure its description guards against).
- **Regression triggers:** any edit to instructions, skill, or playbook (both copies); any model change; sandbox library drift (scheduled harness-explorer inventory); monthly scheduled run. Gate merges via the Evaluation REST API in CI (delegated-auth token in Key Vault), thresholded on pass rate. Budget eval credits like load tests — evaluation runs execute the agent for real.

## 13. Risks and mitigations

- **[PREVIEW] status sprawl:** harness is GA (2026-08-03) but new-experience Knowledge pages, Evaluate-tab pages, Memory, file collections, and workflow-as-tool remain preview-labeled. Mitigation: this design leans only on GA-or-core surfaces (sandbox, skills, connector tools); verify per-page banners before go-live; treat status per feature, not per experience.
- **Library churn / no pip install:** `python-docx`/`pdfplumber` presence is point-in-time observed, not contractual. Mitigation: scripts degrade gracefully, inventory re-checked on schedule; a library removal is a regression-trigger event. [ASSUMPTION: python-docx remains available — it powered the CAT redlining build, but the set "may change."]
- **Sandbox quotas:** time/CPU/memory limits are unpublished; an 80-page contract with hundreds of deltas could hit them. Mitigation: the eval corpus includes the worst case; fall back to per-section processing in the script.
- **Confidentiality/governance:** contracts stay out of knowledge (no RBAC on uploads); no-egress sandbox means the only exits are the SharePoint tool (DLP-governed) and the chat itself; transcripts hold contract text — restrict Bot Transcript Viewer, review retention. Anthropic model choice requires subprocessor sign-off or defaults to OpenAI-family.
- **Cost/credit risk:** GitHub Copilot harness bills **from build time** — 80-page reasoning runs and bulk eval suites are real spend. Mitigation: per-agent monthly limit with alert threshold, environment allocation with Deny on the maker environment, the ~60x scripted path (fewer loop iterations = fewer credits), tiered eval suites (smoke per PR, full nightly).
- **Probabilistic adherence:** the save-only-on-request rule and verbatim clause quoting are instruction-level, i.e., best-effort. Mitigation: end-user credentials bound the blast radius of an unwanted save; verbatim clause text is produced by the extraction *script*, not the model's paraphrase.

## 14. Verdict

The new design is dramatically simpler where it counts: **17 major components (plus ~30 branches and ~25 variables) collapse to 5**, and — the decisive point — the classic build was not merely heavier, it was *worse*: tracked-changes redlining required an external Azure Function, and 80-page files required chunking gymnastics around 30k-character and 100-second ceilings. The sandbox + skill pattern isn't a refactor of the classic design; it makes the deliverable natively possible for the first time.

Where the new experience does NOT help, and determinism is deliberately kept: (1) the **redline engine itself is a frozen, reviewed script** — the one step where run-to-run variance is unacceptable lives in code, not the model (exact work in code, judgment in the model); (2) the **playbook rule set loads exhaustively from the skill reference**, never via top-N retrieval; (3) **output validation is deterministic script comparison** in the eval pipeline, not LLM vibes; (4) the **counsel approval gate stays human** — no instruction is trusted as a compliance control, and if Woodgrove ever wants an in-band approval step, it goes into a deterministic workflow, not prose. The honest residual: skill activation and the save-consent rule remain probabilistic, which is why the evaluation suite — not the instructions — is the real guarantee.
