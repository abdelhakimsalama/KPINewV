# evaluation-testing

Research note on evaluation-first development for the NEW Microsoft Copilot Studio agents experience. Compiled 2026-08-19. Tags: [OFFICIAL] = documented Microsoft behavior (Learn / official Microsoft blog / official Microsoft GitHub repo), [CAT] = Copilot Studio CAT-blog guidance or sample-based practice, [INFERRED] = reasoning by the author of this note. Caveat: learn.microsoft.com could not be fetched directly (network egress blocked); Learn-derived claims come from search-engine synthesis of current Learn pages and are marked [OFFICIAL] only where multiple results agreed. Exact numbers are recorded only where a source stated them.

## 1. What it is and how it works

**The built-in Evaluate tab (agent evaluation).** In the new agents experience, every agent has an **Evaluate** tab providing structured, repeatable testing: you create a named *evaluation* — a test set of conversations plus a *test method* — run it, and get quantitative, per-test-case scored results, all no-code inside the product [OFFICIAL: Learn "Evaluate an agent (preview)" (agents-experience docset); Tech Community GA announcement]. The intent is to replace ad-hoc manual poking in the Preview/Test panel with a measurable quality workflow you re-run after each change [OFFICIAL].

Key documented mechanics:

- **Test sets.** A *single response* test set holds **up to 100 test cases** [OFFICIAL: Learn analytics-agent-evaluation-create]. Test cases can be authored manually, imported from a spreadsheet/CSV, or **AI-generated** from the agent's design, metadata, and knowledge sources; a 2026 update also lets you generate test cases **from analytics, i.e. real user conversations** [OFFICIAL: Learn agents-experience docs; Copilot blog "Updates for scalable agents"].
- **Conversational (multi-turn) test sets.** A conversational test set holds **up to 20 test cases, each up to 12 total messages (6 question/answer pairs)** [OFFICIAL: Learn analytics-agent-evaluation-multi-turn]. You can auto-generate "quick conversation sets" (10 short conversations) or "full conversation sets" from the agent's knowledge, and choose **user profiles to simulate different users** so you don't drive the conversation yourself [OFFICIAL, same page]. Multi-turn evaluation targets context loss, instruction drift, and task completion across turns [OFFICIAL: Learn/Copilot blog].
- **Test methods (judges).** The default judge is **General quality** — an LLM-as-judge assessment scoring relevance, groundedness/completeness of responses [OFFICIAL: Learn analytics-agent-evaluation-overview; Copilot blog "Build smarter, test smarter"]. Additional methods: **Exact match** (whole answer equals expected string), **Text similarity** (wording/structure near-match), **Compare meaning** (semantic equivalence regardless of wording), **intent recognition**, and **Custom graders** — your own criteria expressed as evaluation instructions plus labels (e.g. label HR-agent answers "compliant"/"noncompliant") [OFFICIAL: Learn analytics-agent-evaluation-overview; Copilot blog "Custom Graders in Copilot Studio"]. In the earliest new-experience preview docs, General quality was the only method listed; the method list above reflects the current documentation [OFFICIAL, with the observation that the docsets have evolved — see §4].
- **Runs and results.** Results stream in near-real-time, test case by test case; each case resolves to **Pass, Fail, Invalid, or Error**, and the run gets a **pass-rate score** [OFFICIAL: Learn analytics-agent-evaluation-results]. Results are retained **89 days** in the product; export to CSV for longer retention [OFFICIAL, same page]. 2026 updates added: evaluation across an **entire test set** (not just individual cases), **thumbs up/down feedback on evaluation results** so Microsoft can calibrate its graders, **side-by-side comparison of agent versions** to spot regressions, and integration with the **activity map** so failures link to how the agent executed the task [OFFICIAL: Copilot blog "Updates for scalable agents" and "What's new" posts].
- **Automation surfaces.** (a) An **Evaluation REST API** under the Power Platform API (`api.powerplatform.com`) lets you list test sets, trigger runs, poll for completion, and read per-metric results — explicitly positioned for CI/CD, release validation, and regression testing [OFFICIAL: Learn analytics-agent-evaluation-rest-api; Tech Community "Automate agent evaluation with the Evaluation APIs"]. It can run against **draft** agents, not only published ones [CAT: eval-gate post, `runOnPublishedBot: false`; corroborated by the sample]. The endpoint pattern observed in the CAT sample is `POST /copilotstudio/environments/{envId}/bots/{botId}/api/makerevaluation/testsets/{testSetId}/run` [CAT]. Auth is **delegated only — no app-only path**, so unattended pipelines need a cached refresh token (MSAL refresh tokens expire after 90 days of inactivity) [CAT: eval-gate post]. (b) The **Microsoft Copilot Studio connector** exposes low-code actions ("Evaluate Agent", "Get Agent Test Run Details") so Power Automate flows can schedule recurring evaluations and push results to email/Power BI/Dataverse [OFFICIAL: Learn analytics-agent-evaluation-automate-tools].

**Copilot Studio Kit (a.k.a. Copilot Agent Kit).** A free, open-source Power Platform solution from Microsoft's Copilot Acceleration Team (CAT), installed from GitHub (aka.ms/copilotstudiokit) or AppSource [CAT: Kit post; OFFICIAL: repo]. Its **Test Automation** runs batch tests against agents via the **Direct Line API**, with test records in Dataverse and Excel import/export for bulk authoring [OFFICIAL: Power-CAT-Copilot-Studio-Kit TESTING_CAPABILITIES.md]. Documented test types: **Response match, Attachments match, Topic match** (requires Dataverse conversation-transcript enrichment), **Generative answers** (AI Builder prompts compare the generated answer to a sample answer or validation instructions; Application Insights explains why an answer was/wasn't generated), **Multi-turn** (ordered test cases executed in the same conversation context, usable for end-to-end scenarios and generative-orchestration agents), and **Plan validation** (validate which tools appear in the dynamic plan of a generative-orchestration agent) [OFFICIAL: TESTING_CAPABILITIES.md]. Results are enriched with latencies, transcript-derived topic/intent data, and App Insights telemetry [OFFICIAL]. The Kit also ships **AI-assisted rubric refinement** — create, test, and iteratively align evaluation rubrics until AI grades match human grades — plus multi-agent test runs from one place for admins, and a Compliance Hub that can enforce "agent passes required tests" as a governance policy [CAT: Kit post; OFFICIAL: repo README].

**CI/CD eval gates in Azure DevOps.** The CAT **EvalGateADO** sample (microsoft/CopilotStudioSamples) wires the Evaluation API into an ADO pipeline: pack the solution from `src/` with `pac solution pack` on every PR push, import it into a dedicated CI environment with a service principal, resolve the agent GUID dynamically by schema name via Dataverse OData, run the evaluation **against the draft**, compare pass rate to a configurable threshold, and fail the pipeline (blocking merge via branch policy) when below it. It emits JUnit XML so individual test cases render in ADO's Tests tab and publishes raw JSON as a pipeline artifact; the delegated-auth refresh token lives in Key Vault and is rotated back after each run [CAT: eval-gate post + sample]. Precondition: agent source lives in an ADO repo via **Dataverse git integration** [OFFICIAL: Power Platform ALM docs, as cited by the CAT post].

**Bulk file-based testing.** For document-processing agents, CAT describes a complementary architecture: Dataverse as control plane (test definitions, execution history, pass/fail), SharePoint as configuration layer (input files, gold-standard outputs, prompt assets), Power Automate as orchestrator (read case → fetch file → invoke agent → field-level compare vs gold standard → write outcome), Power BI for pass rates and regression trends. It supports batching, controlled concurrency within Power Automate service limits, retries, and rerunning scenarios across prompt/model versions [CAT: bulk-file-testing post]. A downloadable sample was "coming soon" as of 2026-05-12 [CAT] [STATUS UNVERIFIED whether it has shipped].

**The agentic improvement loop.** CAT demonstrated a fully automated edit→push→publish→test→analyze loop: the open-source **skills-for-copilot-studio** plugin lets an AI coding agent edit agent YAML, push, and **publish** (via the Dataverse `PvaPublish` bound action, polling `publishedon`), while a pytest harness (**PytestAgentsSDK**, M365 Agents SDK + DeepEval's GEval at a 0.75 threshold) scores the published agent; the coding agent iterates on instructions purely from failure scores and judge reasoning [CAT: agentic-improvement-loop post]. Trial results: blank instructions 40% → stable 60% over 7 iterations; expanding from 7 to 14 instruction rules regressed 3/5 → 1/5 [CAT]. A related CAT sample, **ResponseAnalysisAgentsSDK**, intercepts M365 Agents SDK `Activity` events to expose per-query latency statistics (mean/median/σ, length↔latency correlation) and the planner's tool calls and reasoning in a live Gradio dashboard — single-session analysis only [CAT: response-analysis post].

## 2. When to use it / when NOT to use it

**Use the built-in Evaluate tab when:**
- You are iterating on instructions, knowledge, or tools and need a repeatable before/after measure prior to publishing — this is the core regression-testing workflow the feature exists for [OFFICIAL/CAT].
- You want no-code evaluation inside the product with AI-generated test cases, including seeding test sets from real production conversations [OFFICIAL].
- You need CI/CD gating: the Evaluation API is the only documented way to evaluate a **draft** agent server-side before publish, which is what makes PR gates possible [CAT: eval-gate post].

**Use the Copilot Studio Kit when:**
- You need channel-realistic, end-to-end testing through Direct Line, including attachments, topic-trigger verification, plan/tool-selection validation, and adversarial or scripted multi-turn sequences [OFFICIAL: Kit docs; CAT].
- You need to test **many agents centrally** (admin persona) or feed test compliance into governance policy [CAT: Kit post].
- You need custom rubrics with human-alignment tooling (rubric refinement) beyond the product's built-in graders [CAT/OFFICIAL: repo].
- You need unattended batch runs driven from Dataverse records [CAT: eval-gate post's comparison note].

**Use bulk file testing (custom architecture) when** the risk is file-processing at scale — thousands of real documents, field-level extraction accuracy, per-vendor failure patterns. Standard evals score curated prompt-response samples and can look perfect while the agent fails silently on real files [CAT: bulk-file post's invoice anecdote].

**Do NOT use / anti-fit:**
- Don't rely on the Evaluate tab as your only production monitor — it is pre-release quality measurement; conversation analytics, Kit Conversation KPIs, and scheduled connector-driven eval runs cover live drift [CAT/OFFICIAL] [INFERRED framing].
- Don't use single 1–5 LLM scores for gating decisions; CAT explicitly argues these are vague-scale + unsteady-judge and should be decomposed into binary, evidence-backed checks combined by a written rule outside the model [CAT: better-llm-scoring post].
- Don't use built-in evals for deterministic validations a script can do (format checks, arithmetic, required fields) — script them, in a pipeline or Power Automate compare step [CAT: better-llm-scoring; bulk-file post].
- Manual Preview-tab testing "doesn't scale" as the sole validation once multiple contributors change agents [CAT: eval-gate post].

## 3. Classic-experience comparison (what it replaces or simplifies)

- **Classic authoring had no first-class eval story.** In topic-based classic Copilot Studio, quality assurance meant the Test bot pane, topic-trigger checking, and external tooling — the Copilot Studio Kit grew up precisely to fill that gap (Direct Line batch tests, topic match, transcripts) [CAT: Kit post; INFERRED synthesis]. The new experience makes evaluation a **native tab** with test sets, LLM judges, AI test generation, and run history — "no separate tool to install" [OFFICIAL: GA announcement].
- **Topic-match testing loses centrality.** Classic tests asserted "did the right topic trigger"; in the natural-language-first experience with generative orchestration, the analogous assertions are the Kit's **Plan validation** (right tools in the dynamic plan) and the product's activity-map-linked evaluation results [OFFICIAL: Kit docs; Copilot blog] [INFERRED comparison].
- **From transcripts-forensics to judged metrics.** Classic quality review meant reading conversation transcripts/analytics after the fact; the new experience scores responses up front with graders (general quality, compare meaning, custom) and supports version-vs-version comparison [OFFICIAL].
- **ALM integration.** Classic ALM was solution export/import and Power Platform pipelines, which "operate on solution artifacts, not source... no way to gate a deployment on test results"; Dataverse git integration plus the Evaluation API brings PR-gated, source-controlled agent development, aligning agents with mainstream software CI/CD [CAT: eval-gate post]. The CAT ALM-foundation post codifies the practice: run evals in Dev before export **and again in the target environment after import** [CAT: alm-copilot-studio-agents-foundation post].
- **The Kit is complementary, not replaced.** The product's evals run **server-side against drafts with built-in graders**; the Kit runs **through the channel (Direct Line) against published agents with custom rubrics and Dataverse-driven unattended runs** [CAT: eval-gate post info-box]. Both remain relevant in the new experience.

## 4. Limitations, GA/preview status, licensing notes

**Status:**
- Agent Evaluation in Copilot Studio: **generally available as of March 31, 2026** [OFFICIAL: Tech Community GA announcement].
- The **new agents experience itself is a production-ready preview** (Microsoft's term), and the agents-experience docset pages for Evaluate ("Evaluate an agent (preview)", "Run an evaluation (preview)", "View evaluation results (preview)") still carry the **(preview)** label as of mid-2026 [OFFICIAL: Learn page titles]. [INFERRED] Read this as: the evaluation capability is GA at the platform level, while its surfacing inside the new experience (and GitHub Copilot-flavored variants of it) is still labeled preview. Sources are not fully consistent here; treat individual sub-features as preview unless the GA note names them.
- 2026-wave additions (whole-test-set evaluation, thumbs feedback on graders, analytics-sourced test generation, version comparison) were announced as updates/previews during 2026 [OFFICIAL: Copilot blog] [STATUS UNVERIFIED per-feature GA dates].
- Copilot Studio Kit: open-source tooling, not a supported product SKU; several Kit modules are explicitly "(Preview)" in the repo (Agent Insights Hub, Agent Change Tracker, Agent Library, Component Library) [OFFICIAL: repo README]. Test Automation is described by CAT as its most mature feature [CAT].

**Documented limits (exact numbers only where stated):**
- Single response test set: **max 100 test cases** [OFFICIAL].
- Conversational test set: **max 20 test cases; 12 messages (6 Q/A pairs) per case** [OFFICIAL].
- Evaluation results retained **89 days**; CSV export for longer [OFFICIAL].
- Evaluation API: **delegated auth only (no app-only/service-principal path)**; MSAL refresh tokens lapse after **90 days** of inactivity [CAT: eval-gate post — the no-app-only limitation is asserted there; STATUS UNVERIFIED whether Microsoft has since added app-only support].
- Runs are asynchronous and "might take several minutes" depending on test-set size [OFFICIAL].

**Licensing/cost notes:**
- Copilot Studio billing is credit/message-based; search-synthesized guidance indicates **evaluation runs consume Copilot credits equivalent to agent runtime usage** (the agent really executes, including connector/tool actions), while embedded test-chat messages don't count toward billed sessions [OFFICIAL-leaning, via Learn billing FAQ / Microsoft Q&A synthesis; exact wording STATUS UNVERIFIED — verify against the current billing FAQ before budgeting]. [INFERRED] Large recurring eval suites and CI gates therefore have a real credit cost; budget them like load tests, not like free unit tests.
- The Kit is **free and open-source**, but Generative answers testing **requires AI Builder** (AI Builder credits) and full enrichment requires **Azure Application Insights** and Dataverse transcript access [OFFICIAL: Kit docs].
- Grader quality caveat: LLM-as-judge scores are position/verbosity/model-family biased and drift with model versions; Microsoft's own thumbs-feedback loop exists because grader-human alignment is an open problem [CAT: better-llm-scoring; OFFICIAL: blog rationale for feedback feature].

## 5. Security and governance implications

- **Credentials for automation.** The Evaluation API's delegated-only auth forces unattended pipelines to persist a user's refresh token; the CAT sample stores it in **Azure Key Vault** and rewrites rotated tokens after each run [CAT]. [INFERRED] This token represents a real user identity with maker access — scope that account minimally, monitor its use, and prefer a dedicated service account; never commit tokens (a warning CAT repeats verbatim in the response-analysis post [CAT]).
- **Dedicated CI environments.** The gate pattern imports unmanaged solutions into a shared CI Dev environment via service principal; that environment should be non-production, not git-bound, and contain no production data, since PR branches (including unreviewed changes) execute there [CAT + INFERRED].
- **Test data is real data.** Test sets seeded from production conversations (analytics-sourced generation) may contain end-user content; test sets and results live in the platform (results 89 days, exportable to CSV) and in the Kit's case in **Dataverse tables** — apply the same DLP/retention/access review as conversation transcripts [OFFICIAL for the mechanics; INFERRED for the governance obligation].
- **Bulk-testing surfaces.** The CAT bulk architecture deliberately puts gold-standard files and prompts in SharePoint so business users can edit them [CAT]; [INFERRED] that convenience is also an integrity risk — whoever can edit expected outputs can silently redefine "passing." Version and permission those libraries.
- **Governance upside.** Evaluation becomes enforceable policy: branch policies block merges on failed evals [CAT], and the Kit's **Compliance Hub** can require that agents pass defined tests, auto-open compliance cases with SLA timers, and apply enforcement (manual review, quarantine, delete) [OFFICIAL: repo; CAT: Kit post].
- **Auditability of scores.** CAT's scoring guidance — evidence-backed per-check JSON, combining rules versioned outside the model — exists so that gating decisions can be defended and audited months later [CAT: better-llm-scoring]. [INFERRED] For regulated workloads, prefer custom graders/rubrics whose criteria are written down over opaque single-score judges.

## 6. Performance and maintainability implications

- **Latency/throughput.** Eval runs are asynchronous, minutes-scale for full sets [OFFICIAL]; pipelines must poll. Bulk Power Automate testing must respect service limits via controlled concurrency and batching [CAT]. The response-analysis tool exists because per-query latency distributions (mean/median/σ, outliers, length↔latency correlation) are otherwise invisible during development [CAT].
- **Test isolation matters.** Running multiple test questions in one conversation lets one wrong answer poison later turns (two tests dropped to 0.00 in the CAT loop trial); run cases in separate sessions unless you're deliberately testing multi-turn behavior [CAT: improvement-loop "What we learned"].
- **Instruction economy.** The loop trial showed 7 concise, non-overlapping instruction rules stable, 14 rules regressing pass rate from 60% to 20% — regression testing is what catches such prompt-bloat failures [CAT].
- **Grader drift is a maintenance load.** Judges must be recalibrated against human-labeled references and a second judge from a different model family; every scoring change should be validated against a fixed benchmark; drift monitoring is ongoing, not one-time [CAT: better-llm-scoring].
- **Cost/perf trade-off.** Deterministic checks (exact match, scripts, field compare) are cheapest and most reliable; run them first and reserve LLM judges for genuinely fuzzy judgments [CAT]. Credit consumption of eval runs (§4) argues for tiered suites: a small smoke set on every PR, the full set nightly [INFERRED].
- **Maintainability of the gate.** Pack-from-source on every run means CI always tests the PR branch content, never a stale export; dynamic agent-ID resolution by schema name removes per-environment config; JUnit output keeps results in the tooling reviewers already use [CAT]. Refresh-token expiry (90 days idle) means dormant pipelines rot — schedule at least occasional runs [CAT].
- **Retention.** 89-day result retention forces an export pipeline (CSV → Dataverse/Power BI) if you want longitudinal regression trends [OFFICIAL + INFERRED].

## 7. Architecture guidance and anti-patterns

**Recommended architecture (layered testing pyramid)** [CAT: bulk-file post's layering table + eval-gate post; INFERRED consolidation]:
1. **Inner loop:** Evaluate tab in the new experience — AI-generated + curated test sets, general quality plus targeted graders; run before every publish; use version comparison for before/after.
2. **CI gate:** Evaluation API in ADO — pack from source, import to a dedicated CI env, evaluate the **draft**, threshold-gate the merge; publish JUnit + raw JSON.
3. **Channel/E2E layer:** Copilot Studio Kit through Direct Line — multi-turn scripts, plan validation, attachments, topic/tool assertions, adversarial cases, multi-agent admin runs.
4. **Domain-scale layer:** bulk file testing (Dataverse/SharePoint/Power Automate/Power BI) for document workloads with gold-standard field comparison.
5. **Post-deploy:** scheduled connector-triggered evals + Kit Conversation KPIs/analytics for drift; feed real conversations back into test sets.
6. **Optimization loop:** optionally automate iteration (skills-for-copilot-studio publish loop) — but only against a stable, calibrated judge and fixed benchmark, or every iteration is a fresh guess [CAT: better-llm-scoring §7; improvement-loop].

**Regression practice when changing instructions/knowledge/tools:** keep a fixed benchmark test set under version control with the agent source; evaluate draft before publish; evaluate again in target env after deployment [CAT: ALM post]; compare versions head-to-head rather than trusting absolute scores (pairwise judgments are more stable) [CAT: better-llm-scoring]; grow the set with every production edge case [CAT].

**Anti-patterns:**
- **Single-number worship.** Averaging graded labels into a 3.7, or gating on one 1–5 score — decompose into binary checks, gate on dealbreakers, combine outside the model with a written, versioned rule [CAT].
- **Judge grading its relatives.** Calibrating an LLM judge only against itself or same-family models [CAT].
- **Curated-sample overconfidence.** Green evals on 100 curated cases while real files fail silently at scale [CAT: bulk-file post].
- **Testing what's running, not what's in source.** Exporting solutions from a dev sandbox for CI instead of packing the PR branch [CAT].
- **Git-binding the CI environment** (conflicts with developers' git-connected envs) or hardcoding agent GUIDs per environment [CAT].
- **One long test conversation** for independent cases (cascade contamination) [CAT].
- **Instruction rulebooks** grown by appending a rule per failed test until rules compete [CAT].
- **No eval gate at all:** relying on "remember to run the eval before merging" [CAT].
- **Treating eval runs as free:** ignoring credit consumption and real side effects (connector calls, emails) triggered during evaluation — point tools at test doubles/sandboxes where possible [OFFICIAL billing behavior + INFERRED mitigation].

## 8. Sources

**Local CAT blog posts (read in full unless noted):**
- /workspace/microsoft/mcscatblog/_posts/2026-04-19-copilot-studio-eval-gate-azure-devops.md
- /workspace/microsoft/mcscatblog/_posts/2026-05-12-bulk-file-testing-copilot-evals.md
- /workspace/microsoft/mcscatblog/_posts/2026-06-26-better-llm-scoring.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-06-copilot-studio-kit.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-29-agentic-improvement-loop.md
- /workspace/microsoft/mcscatblog/_posts/2026-01-16-response-analysis-copilot-tool.md
- /workspace/microsoft/mcscatblog/_posts/2026-05-20-alm-copilot-studio-agents-foundation.md (evaluation-related excerpts only, via grep)

**Web (Learn pages via WebSearch synthesis — direct fetch blocked; blogs/GitHub as noted):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/analytics-agent-evaluation-intro — "Evaluate an agent (preview)" (new experience)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/analytics-agent-evaluation-results — "Run an evaluation for an agent (preview)"
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/analytics-agent-evaluation-view — "View evaluation results (preview)"
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-intro — About agent evaluation
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview — Choose evaluation methods
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-create — Create a single response test set
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-multi-turn — Create a conversational test set
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-results — Run evaluations and view results
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-rest-api — Automate evaluations with the Power Platform API
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-automate-tools — Trigger agent evaluations with connectors
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/kit-overview and .../guidance/kit-test-capabilities — Copilot Studio Kit overview / testing
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/faq-billing-licensing — billing/licensing FAQ (evaluation credit consumption; exact wording unverified)
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/agent-evaluation-in-microsoft-copilot-studio-is-now-generally-available/4507392 — GA announcement (2026-03-31)
- https://techcommunity.microsoft.com/blog/copilot-studio-blog/automate-agent-evaluation-with-the-evaluation-apis/4511653 — Evaluation APIs blog
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/new-and-improved-agent-evaluations-computer-use-and-advanced-maker-training/ — whole-test-set eval, thumbs feedback, version comparison, activity map
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/custom-graders-in-copilot-studio-setting-high-standards-for-agent-evals/ — custom graders
- https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/build-smarter-test-smarter-agent-evaluation-in-microsoft-copilot-studio/ — general quality judge details
- https://raw.githubusercontent.com/microsoft/Power-CAT-Copilot-Studio-Kit/main/TESTING_CAPABILITIES.md — Kit test types (fetched directly)
- https://raw.githubusercontent.com/microsoft/Power-CAT-Copilot-Studio-Kit/main/README.md — Kit feature/status list (fetched directly)
- https://github.com/microsoft/CopilotStudioSamples/tree/main/testing/evaluation/EvalGateADO — eval gate sample (referenced via CAT post)
- https://github.com/microsoft/skills-for-copilot-studio — improvement-loop plugin (referenced via CAT post)
