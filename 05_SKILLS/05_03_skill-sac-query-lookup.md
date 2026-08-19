# 05.03 — Skill 3 : `sac-query-lookup`

## Objectif du fichier

- **À quoi sert ce fichier** : créer le Skill qui répond aux questions « quelle requête contient X », « que contient telle requête », et aux croisements de plusieurs critères.
- **Étape du développement** : étape 05, troisième des cinq Skills.
- **Ce que vous faites dans Copilot Studio** : vous créez le Skill, puis vous vérifiez en particulier le comportement sur les questions multi-critères.
- **Résultat attendu avant de passer à l'étape suivante** : l'agent liste des requêtes sans jamais prétendre à l'exhaustivité, et n'affirme jamais qu'une requête couvre plusieurs critères sans preuve.

---

## Le point délicat de ce Skill

C'est ici que se concentre la principale limite assumée de l'architecture. Dans l'ancienne version, un moteur calculait une **intersection prouvée** : les requêtes contenant à la fois A, B et C, avec les lignes de preuve. Cette architecture ne calcule rien.

La règle devient donc : l'agent **ne promet pas** qu'une requête couvre tous les critères ; il montre ce que la source démontre, critère par critère, et dit clairement ce qui n'est pas garanti. Le Skill ci-dessous encode cette honnêteté. Ne la retirez pas pour « faire plus utile » : une intersection fausse présentée comme un fait est exactement le défaut que le projet interdit.

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
5. Close with a sentence saying that other queries may also contain this field and that the list is not guaranteed complete.

## What a query contains

1. Search "KPIDictionary" with the exact SAC query name.
2. Describe what you found: the field names, each with its type, quoted exactly.
3. Group the answer by field type (Primary KPI, Derived KPI, Dimension) to keep it readable.
4. Never state how many fields the query has. Say instead that these are the fields you found and that the query may contain others.
5. If the answer would be long, show the most relevant fields and offer to continue rather than dumping everything.

## Several criteria at once

This is the case that needs the most care.

1. Search each criterion separately.
2. A SAC query may be presented as covering several criteria ONLY when the retrieved rows show every one of those criteria on that same query. Never assume that criteria found separately belong to the same query.
3. Present the result in this order:
   - the queries for which the source shows ALL the requested criteria, each with the matching field names quoted as evidence;
   - then, separately and explicitly labelled as partial, the coverage found for each criterion on its own.
4. Always state that this comparison is based on what was found and that full coverage cannot be guaranteed.
5. If no query is shown to carry all the criteria, say so plainly, then give the per-criterion coverage as partial information. Do not present a near-match as an answer.

## Never

- Never state a number of queries, a number of fields, or write "all the queries", "the complete list of fields", "there are N queries".
- Never claim that a query covers a criterion unless a retrieved row shows it.
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
| 1 | `Which queries contain "Gross Sales"?` | **Oui** | Une liste dédoublonnée, persona en ligne, mention de non-exhaustivité, **aucun décompte** |
| 2 | `Que contient la requête "Price catalog" ?` | **Oui** | Des champs avec leur type, groupés, sans total |
| 3 | `Quelles requêtes contiennent à la fois duty free et duty paid ?` | **Oui** | Ce qui est démontré, **puis** la couverture par critère marquée comme partielle |
| 4 | `Which queries have gross sales, shop and product category?` | **Oui** | Aucune affirmation d'intersection non prouvée ; couverture partielle explicite |
| 5 | `Combien de champs dans "Detailed analysis of sales" ?` | **Oui** | **Aucun chiffre**, refus du décompte, proposition de consulter la liste |
| 6 | `Que signifie "Gross Sales" ?` | **Non** → `kpi-field-details` | Sinon, resserrez les deux descriptions |

Les contrôles 3 et 4 sont ceux à surveiller dans la durée : c'est là que le modèle sera le plus tenté d'affirmer une intersection plausible. Relisez la réponse mot à mot — une formulation comme « ces deux requêtes couvrent vos trois critères » sans les champs cités en preuve est un échec, même si le résultat se trouve être exact.

## Ajustements courants

| Symptôme | Correction |
|---|---|
| Affirme une intersection sans preuve | Renforcez le point 2 de « Several criteria at once » |
| Donne le nombre de requêtes | Section « Never » ici, et règle 5 des Instructions |
| Répond en sous-listes par persona sans qu'on l'ait demandé | Dernier point de « Never » |
| Traduit un nom de requête en français | Avant-dernier point de « Never », et règle 16 des Instructions |

## Critères de fin d'étape

- [ ] Le Skill `sac-query-lookup` existe et est enregistré.
- [ ] Le contrôle 1 rend une liste dédoublonnée avec mention de non-exhaustivité.
- [ ] Les contrôles 3 et 4 n'affirment **aucune** intersection non prouvée.
- [ ] Le contrôle 5 ne produit aucun chiffre.
