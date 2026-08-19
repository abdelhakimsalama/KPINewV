---
name: mybi-sac-mapping
description: Use when the user asks how a MyBI field or report was renamed in SAC, what an old MyBI name corresponds to today, what a SAC field used to be called in MyBI, which fields are new in SAC with no MyBI equivalent, or asks about renamed fields in general. Typical wording: "comment s'appelait X dans MyBI", "what is X called now", "ancien nom de X", "quels champs ont ete renommes", "which fields are new in SAC", "correspondance MyBI SAC", "mapping". Do NOT use when the user asks for the meaning or the formula of a field, which query contains a field, or which persona a query belongs to.
---

Answer questions about MyBI-to-SAC field and report renaming, using only "KPIDictionary".

## How to search

1. Search with the name the user gave, whichever side it comes from. The MyBI columns and the SAC columns are both searchable, so an old name finds its row and so does a current one.
2. If the user gave a French label, search it as is; if nothing comes back, try the English equivalent when you can identify one reliably.
3. For a general question about renamed fields, or for a count of them, query "KPIDictionary" analytically over the MyBI and SAC columns. Base the answer on what the list data establishes.

## What the answer must contain, in this order

1. A direct answer in one or two sentences: the old name and the current name.
2. The mapping itself, with the former MyBI name and, for the SAC side, BOTH official labels, English and French. This is the one case where you quote both languages whatever the language of the question. If only one SAC label exists, quote it and say which language it is.
3. The SAC query concerned and the field type.
4. Whether what you gave is the complete set or a partial view, based on what the retrieval actually returned.

## The literal value "new"

When a MyBI column holds the value "new" or "New", it is NOT a field name. It means the SAC field is new and has no MyBI equivalent.

- Say it in words: this field is new in SAC and has no MyBI equivalent.
- Never write that the field was "called new" in MyBI.
- Never quote "new" as if it were an official label.

## When the MyBI value is empty

An empty MyBI column is not the same as "new". It means the correspondence is not documented in "KPIDictionary". Say that no MyBI equivalent is documented for this field, and do not conclude that the field is new.

## When several entries come back

- The same MyBI name mapping to several SAC fields: show every mapping. Never pick one.
- The same SAC field appearing on several queries: give the mapping once, then list the queries you found.

## Answering "how many" about renamings

"How many fields were renamed?" can be read in more than one way, and the readings give different numbers: distinct former MyBI field names, distinct (former name, current name) pairs, or rows in the source. Each row is one (query, field) pair, so the same field repeats across queries.

1. Work out which reading matches what the user actually asked, from the wording of their question and the shape of the data. A question about fields is about fields, not about rows.
2. Establish the figure over the whole of the list data for that reading. Do not derive it from the rows you happened to retrieve or list: those are a sample of the answer, not the answer.
3. Answer with the figure, directly. Do not explain how you obtained it and do not describe the reading you applied. If the user then asks what the figure covers, answer in business terms — fields, entries, queries — not in terms of columns or filters.
4. When the wording is genuinely ambiguous and the readings would give materially different numbers, ask one short clarifying question in the user's own terms — for example, whether they mean fields or entries — rather than guessing.
5. If you cannot establish the figure reliably, say so in one sentence.

## Never

- Never estimate a number, and never extrapolate one from the rows you happened to see.
- Never pad the answer with your internal method: no column names, no filters, no counting rules, no account of the steps you took. If the user asks on what basis a mapping was given, cite the "KPIDictionary" entry that establishes it — the former and current official labels and the query they belong to. That is evidence, not method.
- Never translate or correct an official label on either side of the mapping.
- Never infer a renaming from a resemblance between two names. Only a row in "KPIDictionary" establishes a mapping.
