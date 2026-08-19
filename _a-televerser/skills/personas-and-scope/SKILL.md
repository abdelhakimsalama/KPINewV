---
name: personas-and-scope
description: Use when the user asks which SAC queries are available for a Target Persona, mentions one of the six official personas (Finance, Operations, Supply, Merchant Retail, Merchant Fashion, Merchant Dining), asks which persona a given query belongs to, or asks for a recommendation tailored to their own role or job. Typical wording: "quelles requetes pour le persona X", "which queries for Supply", "je suis supply planner que puis-je consulter", "a quel persona appartient la requete X", "what should I use for my role". Do NOT use when the user asks for the meaning or formula of a field, how a field was renamed, or what a specific query contains without mentioning a persona or a role.
---

Answer questions about Target Personas, using only "KPIDictionary".

## The six official personas

"Finance", "Operations", "Supply", "Merchant Retail", "Merchant Fashion", "Merchant Dining".

Quote them exactly as written above. There is no other valid persona value.

## How persona information works

The persona of a SAC query is carried by the rows of "KPIDictionary". A query belongs to a persona ONLY when a retrieved row shows it. There is no other way to establish it.

## Queries for a persona

1. Search "KPIDictionary" with the persona name.
2. Answer with a single de-duplicated bullet list of the SAC queries you found, each quoted exactly.
3. Say the list is partial only when it actually is. Do not add a routine disclaimer.
4. You may give how many queries a persona has when the data establishes it. Give the figure directly, without explaining how you obtained it. Never estimate it.

## Which persona a query belongs to

1. Search with the exact SAC query name.
2. Give the persona shown by the retrieved rows, quoted exactly.
3. If no row shows a persona for that query, say that the persona is not documented for it. Never guess it from the query name or its subject.

## Job titles are not personas

This is the rule that matters most here.

- A job title such as "supply planner", "business analyst", "controleur de gestion", "category manager" or "store manager" is NOT a persona.
- Never map a job title to a persona, even when the resemblance looks obvious. "Supply planner" does not establish the "Supply" persona.
- Never organise an answer around a persona you inferred from a role the user described.

## When the user asks for a personal recommendation

If, and only if, the user asks what they personally should use and has not stated an official persona:

1. Ask them which of the six official personas applies to them, and list the six values.
2. Wait for their answer before filtering anything.

In every other case, do not ask. List the matching queries with their persona shown on each line, and offer to narrow down if the user states a persona.

## Never

- Never filter results on an assumed persona.
- Never estimate a number of queries or fields for a persona. A figure comes from the data or is not given.
- Never translate a persona value: the six values are quoted as they are in every language.
- Never treat a persona as an access right. "KPIDictionary" documents which persona a query targets; it does not grant or deny anyone access to anything.
