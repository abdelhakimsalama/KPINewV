---
name: kpi-field-details
description: Use when the user asks what a KPI, a field or a dimension means, asks for its business definition, its calculation formula, or its field type (Primary KPI, Derived KPI, Dimension). Also use when the user asks whether a definition or formula exists in French or in English. Typical wording: "what does X mean", "que signifie X", "definition of X", "quelle est la formule de X", "how is X calculated", "comment est calcule X", "is X a KPI or a dimension". Do NOT use when the user asks which SAC query contains a field, what a query contains, how a MyBI field was renamed in SAC, or which persona a query belongs to.
---

Answer questions about the meaning, definition, formula and type of a KPI, field or dimension, using only "KPIDictionary".

## How to search

1. Search "KPIDictionary" with the most distinctive term of the question: the official field name if the user gave one, otherwise the most specific business term.
2. Resolve follow-up references before searching. If the user asks "and its formula?", search again on the KPI or field currently being discussed.
3. Drop filler words. Keep official names, distinctive keywords and meaningful multi-word expressions.
4. The source holds both French and English labels. Search first with the user's own wording.
5. If nothing useful comes back, search again with the equivalent term in the other language when you can identify one reliably.
6. If that still returns nothing, try once more with a shorter, more distinctive keyword before answering that the term was not found.

## What the answer must contain, in this order

1. A direct answer in one or two sentences.
2. The official definition. Quote the official labels exactly; you may explain the definition in your own words in addition to quoting it, never instead of quoting it.
3. The field type, quoted exactly: "Primary KPI", "Derived KPI" or "Dimension".
4. The SAC queries where the field appears, each with its persona. Present them as a bullet list. Say the list is partial only when it actually is.
5. When relevant, say in which languages the definition and formula exist.

## Formulas

- Quote the formula verbatim, inside a fenced code block, preserving its line breaks exactly.
- Never rewrite, simplify, translate or "correct" a formula.
- After the code block, explain it in plain language only if a business definition exists to support the explanation. If none exists, do not improvise one.

## When information is missing

- No business definition for this field: say that no definition is documented in "KPIDictionary" for it. Never write one yourself, and never fill the gap from general knowledge.
- No formula: say that no formula is documented for this field. A dimension normally has none; a KPI without one is simply undocumented.
- Definition present in one language only: quote the language that exists, verbatim, and say which language it is.

## When several entries come back

- Several different definitions for the same field name: show them all. Never merge them, never pick the longest, never elect one as the right one.
- Several different fields matching the term: this is an ambiguity. Present each candidate with its own official labels and its own definition, and ask the user which one they mean.
- The same field on many queries: list the queries you found.

## Never

- You may say how many queries carry the field when the data establishes it. Give the figure directly, without explaining how you obtained it. Never estimate it, and never extrapolate from the rows you happened to see.
- If the user asks on what basis you answered, quote the "KPIDictionary" content that supports it — the official definition, the field type, the queries concerned. That is evidence and it is welcome. How you searched for it is not.
- Never translate an official label in your answer.
- Never present the MyBI value "new" as a field name: it means "new field, with no MyBI equivalent".
- If you found the entry through its former MyBI name, say so at the top of the answer before anything else.
