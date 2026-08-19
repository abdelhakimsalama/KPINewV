---
name: business-vocabulary-and-ambiguity
description: Use when the user describes a field with everyday business vocabulary instead of an official label, for example "point de vente", "magasin", "boutique", "shop", "store", "categorie produit", "categorie de produit", "secteur d'activite". Also use whenever several different official fields could match what the user asked and the right one must be clarified before answering. Do NOT use when the user already gave an exact official field name or query name and there is no ambiguity about what they mean.
---

Translate everyday business vocabulary into official "KPIDictionary" labels, and handle cases where several official fields could match the same wording.

## Vocabulary table

When the user's wording matches an entry on the left, also search "KPIDictionary" for the official label on the right.

| User wording | Official label to search |
| --- | --- |
| point de vente, points de vente | Plant: Plant |
| magasin, magasins | Plant: Plant |
| boutique | Plant: Plant |
| shop | Plant: Plant |
| store | Plant: Plant |
| categorie produit, catégorie produit | Mat: Product category AND Fashion : Prod. Categ |
| categorie de produit, catégorie de produit | Mat: Product category AND Fashion : Prod. Categ |
| secteur d'activite, secteur d'activité | Mat: Product category |

## How to use the table

1. Search BOTH the user's original wording AND the official label from the table. Adding the official label must never remove a result the original wording would have found.
2. Say which official label you searched for, so the user can see how their wording was interpreted. For example: I searched for the official field "Plant: Plant".
3. Never invent a new entry for this table, and never treat a term as a synonym because it looks similar. Only the entries above are established.
4. If the user's wording is already an exact official label, do not apply the table. For example "Mode : catégorie de produit" is itself an official label and must be searched as it is.
5. These terms are deliberately NOT in the table and must not be treated as synonyms: pdv, famille de produit, rayon, categorie alone, produit alone, article alone, entrepot, site, category product. Search them as ordinary terms.

## Ambiguity: two unrelated fields, one business word

"categorie produit" is the known ambiguous case. Two official fields answer to it and they have nothing to do with each other:

- "Mat: Product category", French label "Art: Secteur d activité", is the business sector: alcohol, perfume, skincare and so on.
- "Fashion : Prod. Categ", French label "Mode : catégorie de produit", is a fashion-specific attribute at item level: P for permanent, R for reappointed, S for seasonal.

When the user's wording is ambiguous:

1. Present BOTH candidates. Never silently pick one.
2. Contrast them using their official definitions, because the definitions are what actually distinguishes them.
3. Ask the user which one matches their need. Ask exactly one question.
4. If you order the candidates, order is not a recommendation. Say so if there is any chance of it being read as one.

## Any other ambiguity

The same conduct applies beyond the known case. Whenever several official fields could match:

- show each candidate with its own official labels and its own definition;
- explain what distinguishes them, from the source only;
- ask one clarifying question;
- never answer for the most likely candidate and never merge the candidates into one answer.

## Never

- Never extend the vocabulary table on your own initiative.
- Never substitute the official label for the user's wording silently: both are searched, and the resolution is announced.
- Never state how many fields or queries match. Never claim the candidate list is complete.
