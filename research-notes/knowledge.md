# knowledge

Research note — Knowledge in the NEW Microsoft Copilot Studio agents experience (natural-language-first authoring). Compiled 2026-08-19. Claims tagged [OFFICIAL] (documented Microsoft behavior), [CAT] (Copilot Studio CAT blog guidance/practice), [INFERRED] (analyst reasoning). Status flags noted where known; [STATUS UNVERIFIED] where not.

## 1. What it is and how it works

Knowledge is the grounding layer of a Copilot Studio agent: the set of retrieval sources the orchestrator can query to ground answers in organizational content instead of the model's general training. In the new agents experience, knowledge is configured at the agent level from the **Build tab** (components panel → Knowledge → "Add knowledge" dialog), not per-topic [OFFICIAL — Learn "Knowledge overview for agents (preview)", agents-experience section].

**Supported source types in the new experience** [OFFICIAL — Learn "Available knowledge sources for agents (preview)" and "Add knowledge sources to an agent (preview)"]:

- **Uploaded files** — PDF, Word, Excel, PowerPoint; drag-and-drop in the Add knowledge dialog. Files are stored and indexed in Dataverse ("unstructured data" pipeline). A newer enhancement lets you group multiple related files into a **file collection** used as a single knowledge source, with natural-language instructions to help the agent pick the right document in the collection [OFFICIAL].
- **Public websites** — grounded via the Bing index; Copilot Studio issues Bing searches scoped exclusively to the configured URLs [OFFICIAL — Learn "Add a public website as a knowledge source"].
- **SharePoint** — in the new experience surfaced as "SharePoint (Work IQ)", i.e., connector-powered retrieval over the Microsoft 365 tenant graph/semantic index [OFFICIAL]. The classic-era alternative ingestion path (upload/Dataverse-sync of SharePoint files) also exists; the two paths behave differently (see below) [CAT — dynamic-knowledge-URLs post; pdf-page-level-citations post].
- **SharePoint lists (preview)** — a first-class real-time source: agents query the list at runtime so answers reflect current data; no sync [OFFICIAL — Learn "Add SharePoint lists (preview)", agents-experience].
- **Dataverse** — structured tables as knowledge; natural-language-to-structured-query ("NL2Query") rewriting over the table schema plus a maker-authored glossary (term definitions + synonyms per column) [OFFICIAL — Learn "knowledge-add-dataverse"; CAT — Dataverse retrieval patterns post].
- **Real-time enterprise connectors (preview)** — Salesforce, ServiceNow Knowledge, Zendesk, Azure SQL, Dynamics 365. Microsoft indexes **only metadata** (table/column names); no data movement. At runtime the platform generates a real-time query against the source system ("real-time RAG") [OFFICIAL — Learn "Add Power Platform connectors as knowledge (preview)"; prerelease documentation, subject to change].
- **Copilot connectors (formerly Microsoft Graph connectors)** — tenant-admin-configured connectors that index third-party enterprise data into Microsoft Graph; makers select pre-configured connections as knowledge [OFFICIAL — Learn "Add Copilot connectors as a knowledge source"].
- **Azure AI Search** — enterprise-scale search index as a knowledge source, including the ability to control citation URLs at index level [OFFICIAL — Learn "knowledge-azure-ai-search", referenced by CAT pdf-citations post].
- **Foundry IQ (preview)** — new-experience-only: connect the agent through the "Microsoft IQ" component to a knowledge base built and tuned in Azure AI Foundry. The knowledge base performs *agentic retrieval*: it plans sub-queries, retrieves in parallel, reranks, and hands merged results to the agent [OFFICIAL — Learn "Connect to Foundry IQ from an agent (preview)"; Microsoft Community Hub "Foundry IQ is now in Copilot Studio"].
- **Custom knowledge sources** — a topic with the `OnKnowledgeRequested` trigger (YAML/code view only as of Sept 2025) is invoked whenever the orchestrator decides knowledge retrieval is needed. The topic receives `System.SearchQuery` (semantic-optimized rewrite) and `System.KeywordSearchQuery` (lexical rewrite) — both rewritten with conversation context — calls any search endpoint (HTTP, connector, agent flow), and returns results by assigning a table of `Content` (mandatory), `ContentLocation`, `Title` to `System.SearchResults`. Up to **15 snippets total across all knowledge topics combined** are used for answer generation [CAT — custom-knowledge-source post]. Whether this trigger is authorable inside the new-experience canvas or only via the classic code editor is [STATUS UNVERIFIED]; the mechanism is part of the shared runtime.

**Retrieval/grounding flow.** The RAG pipeline in Copilot Studio: query rewriting with conversation context → information retrieval against selected knowledge → summarization/synthesis into an answer that follows agent instructions (tone, format), with citations [CAT — defeating-oversummarization post; OFFICIAL — new-experience knowledge overview: "the orchestration runtime evaluates whether knowledge sources are needed, searches relevant sources, retrieves content, and uses it to formulate a response, with citations"]. In the new experience the enhanced orchestration runtime decides *whether* and *which* knowledge sources to search based on the user's question, the source **names and descriptions**, and agent instructions; description quality "has a substantial impact" on selection [OFFICIAL — Learn generative orchestration guidance]. When an agent has **more than 25 knowledge sources**, an internal GPT model first filters/pre-selects candidate sources [OFFICIAL — Learn generative orchestration]. Instructions can direct multi-source plans, e.g., "query the MCP tool for KPI data, then consult knowledge for corrections, merge results" — the orchestrator follows such contextual instructions when planning [CAT — influence-orchestration-knowledge post].

**Indexed vs real-time retrieval** [OFFICIAL, synthesized]: uploaded files and Dataverse-synced SharePoint files are *indexed* (semantic chunking into Dataverse); SharePoint via Work IQ uses the *tenant graph semantic index* (meaning-based retrieval, not purely lexical); websites use *Bing's index*; SharePoint lists and the enterprise real-time connectors are *queried live at runtime* with no content indexing; Dataverse table knowledge generates structured queries at runtime over the (Dataverse-search-indexed) table.

**Tenant graph grounding with semantic search.** For SharePoint sources, a setting toggles use of the Microsoft 365 semantic index. With a Microsoft 365 Copilot license anywhere in the tenant (maker does not personally need one), agents leverage the same semantic index as M365 Copilot and can process SharePoint/Copilot-connector files up to **200 MB**; the setting is on by default. Without an M365 Copilot license in the tenant, the setting must be off and generative answers **skip SharePoint files over 7 MB** [OFFICIAL — Learn "knowledge-add-sharepoint"].

**Citations.** Grounded responses carry a citations footer; the runtime exposes `System.Response.Citations` (columns `Name`, `Url`, `Text`) and `System.Response.FormattedText` to `OnGeneratedResponse` topics, enabling citation customization. PDF chunks may carry page markers — `<page_X>` for SharePoint sources, `<page value=X>` for uploaded files — which can be parsed to build `#page=N` deep links; markers are not guaranteed on every citation. Citation shape is **model-dependent**: as of May 2026, GPT-5 Chat tends to return one citation per source file while Claude Sonnet 4.6 returns multiple citations per file (one per grounding chunk) [CAT — pdf-page-level-citations post]. Uploaded-file citations point at Dataverse-hosted chunk previews, not the original document, unless swapped [CAT]. The new experience's **activity trace** shows which knowledge sources were consulted and which citations were used, per message [OFFICIAL — Learn "Preview and test an agent (preview)"].

**Source restrictions.** Agent-wide: disabling **general knowledge** stops the agent answering from model training; the **Web search** setting (Knowledge section of the agent Overview page / "Use information from the web" in Generative AI settings) controls open Bing web grounding [OFFICIAL — Learn web-search data-privacy page]. Node-level "Search only selected sources" belongs to the classic generative-answers node; per Microsoft Q&A responses it *prioritizes* rather than hard-isolates sources — agent-level knowledge is not fully walled off from node scoping [OFFICIAL Q&A guidance; treat isolation claims cautiously]. In classic authoring, `SearchKnowledgeSources` actions can target specific named sources programmatically [CAT — defeating-oversummarization YAML].

## 2. When to use it / when NOT to use it

**Use Knowledge when** [CAT — Dataverse retrieval patterns; OFFICIAL]:
- Q&A over unstructured documents (policies, manuals, KB articles) where a synthesized, cited answer is the goal.
- Fast setup, minimal configuration; general lookups and basic filtering over Dataverse tables for **authenticated** users, including automatic traversal of table relationships (e.g., many-to-many follow-ups).
- Fuzzy, conversational, multi-turn questions where context-aware query rewriting adds value.
- Grounding to public web content scoped to specific sites.

**Do NOT rely on Knowledge when** [CAT — Dataverse retrieval patterns; searchQuery post; oversummarization post]:
- **Exhaustive results are required.** Knowledge returns top-N relevance-ranked matches; "show me all 47 facilities in the North district" gets 5–10. Use the Dataverse **List Rows** tool (orchestrator-generated OData/FetchXML) for deterministic, complete result sets.
- **Anonymous/unauthenticated agents need structured Dataverse data.** Dataverse knowledge requires user auth. Use `searchQuery` (Dataverse relevance search as an unbound-action tool) or List Rows with maker/service-principal credentials [CAT — searchQuery post].
- **You need full control of the generated query** — Knowledge's query generation is automatic and opaque; tools give you the input-description contract.
- **Verbatim, unsummarized text is mandatory** (legal/HR/insurance wording). The summarization step cannot be removed; defeat it with a custom-search topic + AI Prompt ("quote verbatim, don't summarize"), instructions-only (least consistent), or instructions + prompt tool [CAT — oversummarization post].
- **Aggregation/calculation** ("how many…", sums, comparisons) — use MCP, searchQuery facets, or a Prompt tool (≤1000 rows of prefiltered data) [CAT].
- **Semantic intent-matching over free text at query time** ("where can I play basketball" vs. descriptions saying "multi-purpose gym") — keyword-based indexes miss it; a Prompt tool reasoning over filtered rows handles it [CAT].
- [INFERRED] High-stakes deterministic workflows (pricing, eligibility, compliance lookups) should use tools/workflows with controlled queries, keeping Knowledge for explanatory content.

## 3. Classic-experience comparison (what it replaces or simplifies)

- **Agent-level knowledge + orchestrator planning replaces per-topic Generative Answers wiring.** Classic authoring attached knowledge either agent-wide or per generative-answers node ("Search only selected sources"); the new experience is natural-language-first — instructions + source descriptions drive when/which knowledge is searched, reducing the need to author flow logic up front [OFFICIAL — Learn "Build an agent (preview)"]. The classic node-level scoping mechanism is effectively replaced by orchestration-driven selection plus instruction steering [INFERRED from both doc sets].
- **Source counts:** classic orchestration allowed 4 public-website sources; generative orchestration raised this to 25 [OFFICIAL — Learn public-websites guidance]. The >25-source GPT filtering step exists only under generative orchestration [OFFICIAL].
- **Same categories, new additions.** The new experience "supports the same categories of knowledge sources as the classic experience" (websites, SharePoint, files) and adds/surfaces Work IQ-powered SharePoint, SharePoint lists, Foundry IQ (Microsoft IQ), and file collections — several of which are new-experience-only [OFFICIAL — agents-experience docs].
- **Dynamic knowledge URLs** (variable-parameterized website and SharePoint-Work-IQ URLs) replace the classic pattern of registering many near-duplicate sources per region/product/environment, and remove post-deployment URL rewriting from ALM pipelines (use environment variables instead) [CAT — dynamic-knowledge-URLs post; feature introduced ~Feb 2026, SharePoint support added March 10, 2026; the upload/Dataverse-sync SharePoint method does **not** support variables].
- **Continuity:** the underlying knowledge runtime (query rewriting, `System.SearchResults`, `OnKnowledgeRequested`, `OnGeneratedResponse`, citations table) is shared with classic authoring; CAT patterns written against classic code view still describe engine behavior relevant to the new experience [CAT posts; INFERRED for full applicability inside the new canvas].

## 4. Limitations, GA/preview status, licensing notes

**Status (as of 2026-08-19):**
- New agents experience overall: **production-ready preview**; Learn pages in the agents-experience section are labeled "(preview)" [OFFICIAL]. A third-party blog claims the "rebuilt Copilot Studio" reached GA on 2026-08-03 — this conflicts with Learn's preview labels; treat GA as **unconfirmed** [CONFLICTING SOURCES — flagged].
- Knowledge in the new experience: preview-labeled [OFFICIAL]. SharePoint lists knowledge: preview [OFFICIAL]. Real-time enterprise connectors (Salesforce/ServiceNow/Zendesk/Azure SQL): **preview, prerelease docs subject to change** [OFFICIAL]. Foundry IQ connection: **preview** [OFFICIAL]. Work IQ in Copilot Studio: preview [OFFICIAL — Learn "add-work-iq"]. Dataverse knowledge, SharePoint, websites, uploaded files: long-standing, generally treated as GA in the classic docs [OFFICIAL; exact per-source GA dates not re-verified — STATUS PARTIALLY UNVERIFIED].

**Documented limits (numbers only where a source states them):**
- Uploaded files: max **512 MB per file**; up to **500 files per agent** (practically bounded by Dataverse file storage capacity); encrypted/sensitivity-labeled/password-protected files unsupported; requires Dataverse search enabled [OFFICIAL — Learn "knowledge-add-file-upload"].
- SharePoint: **200 MB** per file with M365 Copilot license + tenant graph grounding; **7 MB** cap (files above are skipped) without [OFFICIAL].
- SharePoint/Copilot connectors: files up to 512 MB for PDF/PPTX/DOCX extensions per the knowledge summary page [OFFICIAL — Learn "knowledge-copilot-studio"; note the 200 MB vs 512 MB figures appear in different Learn pages — likely different pipelines; flagged as potentially stale/conflicting].
- Public websites: Bing indexes only **2 levels deep** from the provided URL; URL must be Bing-indexed and publicly accessible; ownership attestation required at publish; 25 website sources max under generative orchestration (4 classic) [OFFICIAL + CAT — dynamic-URLs post].
- SharePoint lists: up to **10 lists** recommended/selectable per agent (one third-party source says 15 — Learn's 10 is authoritative); a list is truncated beyond **20,000 items or 50 MB raw text** (truncation noted in the response); **>35,000 rows** degrades quality/latency; the Attachments column is not indexed [OFFICIAL — Learn "knowledge-sharepoint-lists"].
- Dataverse knowledge: up to **15 tables** per knowledge source; glossary/synonym updates take up to **15 minutes** to apply; returns top-N relevance-scored rows, never exhaustive sets [OFFICIAL — Learn "knowledge-add-dataverse"; CAT].
- Custom knowledge (`OnKnowledgeRequested`): **15 snippets max across all knowledge topics combined** feed answer generation [CAT].
- Dataverse relevance search (powers Dataverse knowledge indexing, searchQuery, Dataverse MCP): only text-type columns indexable; indexes roughly the **first 1–2 MB** of text in file attachments [CAT — Dataverse retrieval patterns / searchQuery posts].

**Licensing:**
- Tenant graph grounding/semantic index requires ≥1 M365 Copilot license in the tenant; maker doesn't need one personally [OFFICIAL].
- For users with M365 Copilot licenses, agent usage in Teams/SharePoint/M365 Copilot channels is **zero-rated** (doesn't consume Copilot Studio message packs/PAYG), including generative answers and tenant graph grounding [OFFICIAL — Learn licensing guidance via search].
- Web search: data sent to Bing falls under the Microsoft Privacy Statement, **not** the Products and Services DPA — it leaves the enterprise boundary [OFFICIAL — Learn "data-privacy-security-web-search"].
- Real-time connectors and Dataverse knowledge availability can depend on environment/licensing configuration (generative AI features enabled in Power Platform admin center) [OFFICIAL].

## 5. Security and governance implications

- **Per-user permission trimming vs. flat access.** SharePoint (Work IQ/connector path) authenticates on behalf of the user and surfaces only content the user can access — no permission, no answer; sensitivity labels honored [OFFICIAL + CAT]. **Uploaded files have no RBAC**: every agent user gets answers from all uploaded content — a decisive selection criterion when documents are access-restricted [CAT — pdf-citations post, explicitly warned; OFFICIAL].
- **Dataverse knowledge requires end-user auth**, so row-level Dataverse security applies per user. For anonymous agents using searchQuery/List Rows with maker (service principal) credentials, *the service principal's security role is the effective ACL for every anonymous user* — grant read-only on exactly the tables/columns safe for public exposure [CAT — searchQuery post, danger callout].
- **Real-time connectors** index metadata only (no data replication); connections are Power Platform connections, so existing **DLP policies** govern them. DLP granularity differs by pattern: per-knowledge-source (Knowledge), per-connector (List Rows/searchQuery/Prompt), all-or-nothing for the Dataverse MCP server (disable unwanted operations in tool config instead) [OFFICIAL + CAT — Dataverse retrieval patterns].
- **Web/general knowledge governance:** disable general knowledge to force answers only from supplied sources; disable web search where Bing egress is unacceptable; note Copilot Studio's web-search controls are independent of the M365 Copilot tenant web-search toggle [OFFICIAL].
- **Website ownership attestation** at publish acts as a governance gate on which public sites an org grounds against [OFFICIAL].
- [INFERRED] Because orchestration auto-selects sources, governance must assume *any* attached source can be consulted for *any* query; "search only selected sources"-style prioritization is not an isolation boundary — separate agents (or removal of sources) is the only hard boundary.
- Conditional Access policies must permit Copilot Studio's on-behalf-of Dataverse/SharePoint access when user auth is required [CAT].

## 6. Performance and maintainability implications

- **Over-scoped grounding costs latency and relevance.** Many broad sources (e.g., root-domain websites) slow retrieval and pull irrelevant pages; scope URLs tightly, and use **dynamic knowledge URL variables** to collapse per-region/product/environment source sprawl into one parameterized source — improving latency, relevance, and ALM (environment variables repoint sources per environment without post-deploy edits) [CAT — dynamic-URLs post].
- **Indexing latency:** uploaded/SharePoint-synced content must index before it answers; large libraries (thousands of files) can take days [OFFICIAL Q&A — community-grade, treat as anecdotal]. Dataverse relevance-search indexing can be slow to start; adding the table to Knowledge kicks off indexing immediately (removable afterwards — the index persists) [CAT — searchQuery post].
- **Glossaries and descriptions are the tuning surface.** Dataverse knowledge quality is "made or broken" by glossary term definitions/synonyms; cryptic logical column names without glossary entries defeat NL2Query. Knowledge-source names/descriptions drive orchestrator routing — name sources by business function [CAT — Dataverse retrieval patterns; OFFICIAL — orchestration guidance].
- **>25 sources introduces an extra GPT filtering hop** — [INFERRED] keep source counts lean to avoid a selection stage that can misroute or add latency.
- **Model selection changes knowledge behavior**: citation granularity (single vs. per-chunk citations), summarization fidelity, and instruction adherence all vary by model (documented differences between GPT-5 Chat and Claude Sonnet 4.6); maintain ongoing evaluations because model behavior drifts [CAT — pdf-citations and oversummarization posts].
- **Real-time sources trade freshness for per-query cost:** SharePoint lists and enterprise connectors always reflect live data (no sync jobs to maintain) but every question hits the source system at runtime [OFFICIAL; INFERRED consequence].
- Use the **activity trace / Activity tab** (rewritten queries, sources consulted, chain-of-thought) as the primary debugging tool for retrieval issues [OFFICIAL + CAT].

## 7. Architecture guidance and anti-patterns

**Guidance:**
- **Match retrieval pattern to question shape** (CAT decision framework for Dataverse, generalizable): precise + exhaustive → List Rows (OData/FetchXML tool); precise + top-N acceptable → Knowledge; fuzzy discovery/large datasets → searchQuery (relevance search), often as the **two-step pattern** searchQuery (find candidates) → List Rows (full record by ID); semantic reasoning over ≤1000 prefiltered rows → Prompt tool; exploration/prototyping → Dataverse MCP (then graduate to dedicated tools for production) [CAT — Dataverse retrieval patterns].
- **Combine Knowledge with tools deliberately** via instructions: e.g., live data from a tool + corrections/context from knowledge, merged per instruction ("for KPI questions, call the MCP tool, then check knowledge for corrections") [CAT — influence-orchestration post].
- **Custom knowledge sources** (`OnKnowledgeRequested` + `System.SearchResults`) integrate proprietary search APIs, Azure AI Search, or even Dataverse searchQuery into the unified grounded-answer/citation flow; multiple knowledge topics can implement fallback strategies within the shared 15-snippet budget [CAT].
- **Engineer citations as UX**: page-level PDF citations via `OnGeneratedResponse` (parse `<page_X>`/`<page value=X>`, append `#page=N`, suppress default with `System.ContinueResponse = false`); swap Dataverse-chunk URLs for public URLs for uploaded files; or map citation URLs at the Azure AI Search index level [CAT — pdf-citations post].
- **Bake dynamic URL variables into baseline architecture** for multi-market/multi-product/multi-environment agents [CAT].
- **Consider Foundry IQ** when a central team should own retrieval tuning: build/tune the knowledge base once in Azure AI Foundry, reuse across Copilot Studio agents via Microsoft IQ (preview) [OFFICIAL; INFERRED positioning].

**Anti-patterns:**
- Registering a domain root as website knowledge (over-scoped grounding, noise, latency) instead of scoped/parameterized paths [CAT].
- Treating "search only selected sources" or instruction phrasing as a **security boundary** for knowledge isolation — it is prioritization, not isolation; split agents for hard boundaries [OFFICIAL Q&A; INFERRED].
- Uploading access-restricted documents as files (no RBAC) instead of SharePoint with permission trimming [CAT + OFFICIAL].
- Using Knowledge for "show me ALL X" — top-N truncation silently drops rows; users trust an incomplete list [CAT].
- Expecting keyword indexes (Dataverse relevance search, website/Bing) to do meaning-based matching; either add explicit attribute columns, enrich search inputs with AI-generated synonyms, or use a Prompt tool [CAT].
- Cryptic column names with empty glossaries; skipping tool/source business-function naming [CAT].
- One-retrieval-method dogma: production agents typically combine two or three methods; "start simple, hit the wall, add another method" [CAT].
- Shipping without DLP review, or assuming MCP allows per-operation DLP (it doesn't) [CAT].

## 8. Sources

**Local CAT blog posts (read in full):**
- /workspace/microsoft/mcscatblog/_posts/2025-09-24-copilot-studio-custom-knowledge-source.md
- /workspace/microsoft/mcscatblog/_posts/2026-02-11-dynamic-knowledge-urls-copilot-studio.md
- /workspace/microsoft/mcscatblog/_posts/2026-04-10-dataverse-retrieval-patterns-copilot-studio.md
- /workspace/microsoft/mcscatblog/_posts/2026-03-20-dataverse-search-in-copilot-studio-unauthenticated-structured-data.md
- /workspace/microsoft/mcscatblog/_posts/2026-05-19-pdf-page-level-citations.md
- /workspace/microsoft/mcscatblog/_posts/2026-01-10-search-enabled.md (read; about the blog's own Algolia search — not relevant to platform knowledge, not used for claims)
- /workspace/microsoft/mcscatblog/_posts/2025-11-11-influence-orchestration-knowledge.md
- /workspace/microsoft/mcscatblog/_posts/2026-01-23-copilot-studio-defeating-oversummarization.md (additional relevant post found via grep)

**Microsoft Learn / official (via WebSearch synthesis; learn.microsoft.com direct fetch blocked):**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-copilot-studio (Knowledge overview, new experience, preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-sources-overview (Available knowledge sources, new experience)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-add-existing-copilot (Add knowledge sources, new experience)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-sharepoint-lists (SharePoint lists, preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-edit-source (Manage knowledge sources, preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/foundry-iq-connect (Foundry IQ connection, preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/preview-overview (activity trace / testing, preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/build-overview (Build tab, preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio (Knowledge sources summary, classic)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload (file upload limits)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint (SharePoint, tenant graph grounding, 200 MB / 7 MB)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-public-website (public websites)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-dataverse (Dataverse knowledge, 15 tables)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-real-time-connectors (real-time connectors, preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-connectors (Copilot connectors)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-graph-vs-power-platform-connectors (Copilot vs Power Platform connectors)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration (orchestration, >25-source filtering)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/data-privacy-security-web-search (web search privacy)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-ai-public-websites (website source limits: 25/4)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-boost-node (generative answers node, "search only selected sources")
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-work-iq (Work IQ, preview)
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
- https://learn.microsoft.com/en-us/answers/questions/5666256/generative-answers-node-search-only-selected-sourc (Q&A: prioritization, not isolation)
- https://learn.microsoft.com/en-us/answers/questions/5646141/is-there-any-limit-on-number-of-sources-and-their (Q&A: source count/indexing time)

**Other official Microsoft channels:**
- https://www.microsoft.com/en-us/power-platform/blog/2025/03/27/knowledge-in-microsoft-copilot-studio/ (real-time RAG for enterprise connectors)
- https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/foundry-iq-is-now-in-copilot-studio-bring-your-enterprise-data-to-every-agent-co/4534635
- https://techcommunity.microsoft.com/blog/microsoft365copilotblog/a-closer-look-at-work-iq/4499789
- https://techcommunity.microsoft.com/blog/microsoft365copilotblog/what%E2%80%99s-new-in-microsoft-365-copilot--june-2026/4529572

**Third-party (used only for status cross-check, flagged where conflicting):**
- https://rpabotsworld.com/microsoft-copilot-studio-august-2026-rebuilt-agent-platform-guide/ (claims GA 2026-08-03 — conflicts with Learn preview labels)
- https://blog.ciaops.com/2025/07/13/the-critical-nature-of-website-ownership-attestation-in-microsoft-copilot-studio-for-public-knowledge-sources/
