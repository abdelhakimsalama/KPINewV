# Microsoft Copilot Studio — New Experience Expert Training

Expert-level training corpus and architecture guide for the **new Microsoft Copilot Studio agent experience** (agents powered by the GitHub Copilot harness, GA August 3, 2026).

Produced 2026-08-19 from current primary sources: the official Microsoft Copilot Studio CAT blog (cloned at `microsoft/mcscatblog`, current through 2026-08-13) and current Microsoft Learn documentation (via web research; every claim in these documents is tagged by provenance).

## Contents

| Path | What it is |
| --- | --- |
| [`copilot-studio-expert-guide.md`](copilot-studio-expert-guide.md) | **The final deliverable**: "Microsoft Copilot Studio New Experience — Expert Architecture Guide" (25 sections: mental model, components, orchestration, decision trees, migration strategy, anti-patterns, checklists, current limitations, sources) |
| [`training-exercises/`](training-exercises/) | The required training exercise: 10 diverse fictional project architectures, each with a classic-style design, a new-native redesign, quantified simplification, determinism analysis, evaluation plan, and honest verdict |
| [`research-notes/`](research-notes/) | 14 structured research notes underlying the guide, one per architectural area, with per-claim provenance tags |

## Provenance tags used throughout

- `[OFFICIAL]` — documented Microsoft behavior (Microsoft Learn, message center, official repos)
- `[CAT]` — Microsoft Copilot Studio CAT (Customer Advisory Team) guidance and observed behavior
- `[INFERRED]` — architectural reasoning, not documented platform behavior
- `[STATUS UNVERIFIED]` / `[ASSUMPTION]` — flagged uncertainty; verify against current docs before relying on it

Copilot Studio evolves rapidly: **always re-verify availability, limits, and GA/preview status against current Microsoft documentation before using these documents for a production decision.**
