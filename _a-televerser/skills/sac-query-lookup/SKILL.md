---
name: sac-query-lookup
description: Use when the user asks which SAC query contains a given field, KPI or dimension, asks what a specific SAC query contains, asks to find queries covering several criteria at once, or compares two queries. Typical wording: "quelle requete contient X", "which query has X", "dans quel rapport trouve-t-on X", "que contient la requete X", "what is inside query X", "quelles requetes ont X et Y", "X versus Y". Do NOT use when the user asks what a single field means or how it is calculated, how a field was renamed from MyBI to SAC, or which queries belong to a persona.
---

Answer questions about SAC queries and their contents, using only "KPIDictionary".

## Which query contains a field

1. Search "KPIDictionary" with the field name the user gave.
2. Search a second time using SAC query names and query-related wording for the same term, because a term can appear in a query name as well as in a field name.
3. Merge only what the retrieved rows actually show. Never add a query association that no row demonstrates.
4. Answer with a single de-duplicated bullet list: each SAC query once, quoted exactly, with its persona on the same line.
5. Say that the list is partial only when it actually is. Do not add a routine disclaimer to every answer.

## What a query contains

1. Search "KPIDictionary" with the exact SAC query name.
2. Describe what you found: the field names, each with its type, quoted exactly.
3. Group the answer by field type (Primary KPI, Derived KPI, Dimension) to keep it readable.
4. You may give how many fields the query contains, and how they break down by field type, when the list data establishes it. Give the figures directly, without explaining how you obtained them. If you cannot establish them reliably, say so rather than estimating.
5. If the answer would be long, show the most relevant fields and offer to continue rather than dumping everything.

## Several criteria at once

This is the case that needs the most care, and the one where evidence matters most.

1. Query "KPIDictionary" for the criteria together, and for each criterion on its own.
2. A SAC query may be presented as covering several criteria ONLY when the data shows every one of those criteria on that same query. Never assume that criteria found separately belong to the same query.
3. For every query you present as covering all the criteria, name the matching fields, one per criterion. Which field answers which criterion is part of the result the user asked for, so it belongs in the answer. How you searched for it does not.
4. Then give, separately, the coverage found for each criterion on its own, so the user sees the near-misses.
5. If no query carries all the criteria, say so plainly and give the per-criterion coverage. Do not present a near-match as an answer.
6. If the scope was too broad to establish the result reliably, say so in one sentence instead of implying certainty.

## Never

- Never estimate a number of queries or fields, and never extrapolate one from the rows you happened to see. A figure comes from the data or is not given.
- Never claim that a query covers a criterion without naming the field that matches it.
- Never describe your search method in the answer: no column names, no filters, no account of the steps you took. Name the fields that answer the criteria, not the way you found them. If the user asks why a query was included, cite the fields and values from "KPIDictionary" that place it there.
- Never translate a SAC query name: they exist in English only and are quoted unchanged in every language.
- Never reorganise the answer around a persona the user did not state.
- If a row was found through a former MyBI name, say so at the top of the answer.
