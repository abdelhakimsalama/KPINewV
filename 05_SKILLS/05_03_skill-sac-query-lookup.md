# 05.03 — Skill 3 : `sac-query-lookup`

## Objectif du fichier

- **À quoi sert ce fichier** : créer le Skill qui répond aux questions « quelle requête contient X », « que contient telle requête », et aux croisements de plusieurs critères.
- **Étape du développement** : étape 05, troisième des cinq Skills.
- **Ce que vous faites dans Copilot Studio** : vous créez le Skill, puis vous vérifiez en particulier le comportement sur les questions multi-critères.
- **Résultat attendu avant de passer à l'étape suivante** : l'agent liste des requêtes sans jamais prétendre à l'exhaustivité, et n'affirme jamais qu'une requête couvre plusieurs critères sans preuve.

---

## Le point délicat de ce Skill

C'est ici que se concentrent les questions les plus exigeantes : croiser plusieurs critères, et compter.

La source les prend en charge nativement — les listes SharePoint en Knowledge acceptent les requêtes analytiques et d'agrégation **[OFFICIEL, préversion]** — et ces cas d'usage restent donc **au périmètre**. Ce sont aussi les questions les plus lourdes : Microsoft signale que celles qui exigent d'analyser la totalité d'une grande liste peuvent être limitées en débit ou très lentes **[OFFICIEL]**. Autrement dit : capacité réelle, fiabilité à établir.

La discipline encodée ci-dessous n'est donc pas une restriction, c'est une exigence de **traçabilité** : quand l'agent affirme qu'une requête couvre plusieurs critères, il cite les champs qui le prouvent. Ce qui reste interdit, c'est l'affirmation sans preuve — pas l'affirmation elle-même.

## Les trois champs à renseigner

**Name**

```
sac-query-lookup
```

**Description**

```
Use when the user asks which SAC query contains a given field, KPI or dimension, asks what a specific SAC query contains, asks to find queries covering several criteria at once, or compares two queries. Typical wording: "quelle requete contient X", "which query has X", "dans quel rapport trouve-t-on X", "que contient la requete X", "what is inside query X", "quelles requetes ont X et Y", "X versus Y". Do NOT use when the user asks what a single field means or how it is calculated, how a field was renamed from MyBI to SAC, or which queries belong to a persona.
```

**Instructions**

```markdown
Answer questions about SAC queries and their contents, using only "KPIDictionary".

## Which query contains a field

1. Search "KPIDictionary" with the field name the user gave.
2. Search a second time using SAC query names and query-related wording for the same term, because a term can appear in a query name as well as in a field name.
3. Merge only what the retrieved rows actually show. Never add a query association that no row demonstrates.
4. Answer with a single de-duplicated bullet list: each SAC query once, quoted exactly, with its persona on the same line.
5. Say whether the list you gave is complete or partial, based on what the retrieval actually returned.

## What a query contains

1. Search "KPIDictionary" with the exact SAC query name.
2. Describe what you found: the field names, each with its type, quoted exactly.
3. Group the answer by field type (Primary KPI, Derived KPI, Dimension) to keep it readable.
4. You may give how many fields the query contains, and how they break down by field type, when the list data establishes it. Say what you counted. If you cannot establish it reliably, say so rather than estimating.
5. If the answer would be long, show the most relevant fields and offer to continue rather than dumping everything.

## Several criteria at once

This is the case that needs the most care, and the one where evidence matters most.

1. Query "KPIDictionary" for the criteria together, and for each criterion on its own.
2. A SAC query may be presented as covering several criteria ONLY when the data shows every one of those criteria on that same query. Never assume that criteria found separately belong to the same query.
3. For every query you present as covering all the criteria, quote the matching field names as evidence, one per criterion. The evidence is not decoration: it is what makes the claim checkable by the user.
4. Then give, separately, the coverage found for each criterion on its own, so the user sees the near-misses.
5. If no query is shown to carry all the criteria, say so plainly and give the per-criterion coverage. Do not present a near-match as an answer.
6. Say whether the result is complete or partial. If the scope was too broad to establish reliably, say that instead of implying certainty.

## Never

- Never estimate a number of queries or fields, and never extrapolate one from the rows you happened to see. A figure comes from the data or is not given.
- Never claim that a query covers a criterion without quoting the field that proves it.
- Never translate a SAC query name: they exist in English only and are quoted unchanged in every language.
- Never reorganise the answer around a persona the user did not state.
- If a row was found through a former MyBI name, say so at the top of the answer.
```

## Le fichier `SKILL.md` complet

```yaml
---
name: sac-query-lookup
description: Use when the user asks which SAC query contains a given field, KPI or dimension, asks what a specific SAC query contains, asks to find queries covering several criteria at once, or compares two queries. Typical wording: "quelle requete contient X", "which query has X", "dans quel rapport trouve-t-on X", "que contient la requete X", "what is inside query X", "quelles requetes ont X et Y", "X versus Y". Do NOT use when the user asks what a single field means or how it is calculated, how a field was renamed from MyBI to SAC, or which queries belong to a persona.
---
```

## Vérification

| # | Question | Le Skill doit-il se charger ? | Ce que la réponse doit montrer |
|---|---|---|---|
| 1 | `Which queries contain "Gross Sales"?` | **Oui** | Une liste dédoublonnée, persona en ligne, caractère complet ou partiel indiqué |
| 2 | `Que contient la requête "Price catalog" ?` | **Oui** | Des champs avec leur type, groupés ; un décompte par type est acceptable s'il vient des données |
| 3 | `Quelles requêtes contiennent à la fois duty free et duty paid ?` | **Oui** | Les requêtes couvrant les deux, **avec les champs cités en preuve** *(repère : 2 requêtes — `Mix sales, stocks, prices` et `Price catalog`)* |
| 4 | `Which queries have gross sales, shop and product category?` | **Oui** | Cas où l'ancien moteur ne trouvait **aucune** requête couvrant les trois : l'agent doit le dire, puis donner la couverture par critère |
| 5 | `Combien de champs dans "Detailed analysis of sales" ?` | **Oui** | Un chiffre issu des données, avec l'énoncé de ce qui est compté *(repère : 184 lignes ; « champs » et « lignes » peuvent légitimement différer)* |
| 6 | `Que signifie "Gross Sales" ?` | **Non** → `kpi-field-details` | Sinon, resserrez les deux descriptions |

Les contrôles 3, 4 et 5 sont ceux à surveiller dans la durée : c'est là que le modèle sera le plus tenté d'affirmer un résultat plausible. Le critère de jugement est la **preuve**, pas seulement l'exactitude — une formulation comme « ces deux requêtes couvrent vos trois critères » sans les champs cités en preuve est un échec, même si le résultat se trouve être exact. À l'inverse, un résultat partiellement inexact mais accompagné de ses preuves est un cas exploitable : vous voyez immédiatement ce que l'agent a réellement trouvé.

## Ajustements courants

| Symptôme | Correction |
|---|---|
| Affirme une intersection sans preuve | Renforcez le point 3 de « Several criteria at once » |
| Estime un nombre au lieu de l'établir | Section « Never » ici, et règle 6 des Instructions |
| Refuse tout décompte | La règle 5 des Instructions **autorise** les décomptes issus des données : vérifiez qu'elle a été collée |
| Répond en sous-listes par persona sans qu'on l'ait demandé | Dernier point de « Never » |
| Traduit un nom de requête en français | Avant-dernier point de « Never », et règle 16 des Instructions |

## Critères de fin d'étape

- [ ] Le Skill `sac-query-lookup` existe et est enregistré.
- [ ] Le contrôle 1 rend une liste dédoublonnée, avec son caractère complet ou partiel.
- [ ] Les contrôles 3 et 4 citent les champs **en preuve** de chaque affirmation.
- [ ] Le contrôle 5 produit un chiffre issu des données ; l'écart éventuel avec 184 est consigné.
