# 05.01 — Skill 1 : `kpi-field-details`

## Objectif du fichier

- **À quoi sert ce fichier** : créer le Skill qui traite les questions de sens, de définition, de formule et de type d'un champ ou d'un KPI — le cas d'usage le plus fréquent de l'agent.
- **Étape du développement** : étape 05, premier des cinq Skills.
- **Ce que vous faites dans Copilot Studio** : vous créez un Skill avec le nom, la description et les instructions ci-dessous, puis vous vérifiez son activation.
- **Résultat attendu avant de passer à l'étape suivante** : le Skill se charge sur les questions de définition et de formule, et **pas** sur les questions de requête ou de renommage.

---

## Les trois champs à renseigner

**Name**

```
kpi-field-details
```

**Description** *(c'est le déclencheur — collez-la telle quelle)*

```
Use when the user asks what a KPI, a field or a dimension means, asks for its business definition, its calculation formula, or its field type (Primary KPI, Derived KPI, Dimension). Also use when the user asks whether a definition or formula exists in French or in English. Typical wording: "what does X mean", "que signifie X", "definition of X", "quelle est la formule de X", "how is X calculated", "comment est calcule X", "is X a KPI or a dimension". Do NOT use when the user asks which SAC query contains a field, what a query contains, how a MyBI field was renamed in SAC, or which persona a query belongs to.
```

**Instructions** *(le corps du Skill)*

```markdown
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
4. The SAC queries where the field appears, each with its persona. Present them as a bullet list, and state that other queries may also carry this field.
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
- The same field on many queries: list the queries you found, and say that others may exist.

## Never

- Never state how many queries carry the field, and never write "all the queries".
- Never translate an official label in your answer.
- Never present the MyBI value "new" as a field name: it means "new field, with no MyBI equivalent".
- If you found the entry through its former MyBI name, say so at the top of the answer before anything else.
```

## Le fichier `SKILL.md` complet

Si vous utilisez le téléversement (méthode recommandée en `05_00`), créez le fichier `SKILL.md` ainsi : l'en-tête YAML ci-dessous, puis **le corps du Skill donné plus haut**.

```yaml
---
name: kpi-field-details
description: Use when the user asks what a KPI, a field or a dimension means, asks for its business definition, its calculation formula, or its field type (Primary KPI, Derived KPI, Dimension). Also use when the user asks whether a definition or formula exists in French or in English. Typical wording: "what does X mean", "que signifie X", "definition of X", "quelle est la formule de X", "how is X calculated", "comment est calcule X", "is X a KPI or a dimension". Do NOT use when the user asks which SAC query contains a field, what a query contains, how a MyBI field was renamed in SAC, or which persona a query belongs to.
---
```

## Vérification

Six contrôles, dans **Preview**, trace d'activité ouverte à chaque fois.

| # | Question | Le Skill doit-il se charger ? | Ce que la réponse doit montrer |
|---|---|---|---|
| 1 | `What does "Plant: Plant" mean?` | **Oui** | La définition officielle, le type `Dimension`, des requêtes porteuses, **aucun décompte** |
| 2 | `Que signifie "Mat: Product category" ?` | **Oui** | Réponse en français, libellé anglais cité tel quel, définition mentionnant alcool / parfum / soin |
| 3 | `Quelle est la formule de "Downstream service rate in quantity (Argon)" ?` | **Oui** | Formule **en bloc de code**, verbatim, sauts de ligne préservés |
| 4 | `What is "% Backorders"?` | **Oui** | Définition anglaise ; si la définition française manque, il le **dit** au lieu de la produire |
| 5 | `Which queries contain "Gross Sales"?` | **Non** → c'est `sac-query-lookup` | Si celui-ci se charge, resserrez la description |
| 6 | `Comment s'appelait "Received (line)" dans MyBI ?` | **Non** → c'est `mybi-sac-mapping` | Idem |

Les contrôles 5 et 6 sont les plus utiles : ils vérifient que le Skill **ne déborde pas**. Un Skill qui se charge partout annule le bénéfice du chargement à la demande.

## Ajustements courants

| Symptôme | Correction |
|---|---|
| Ne se charge pas sur les questions françaises | Ajoutez d'autres formulations françaises dans la description |
| Se charge aussi sur « quelle requête contient X » | Renforcez le « Do NOT use » de la description, et vérifiez celle de `sac-query-lookup` |
| Écrit une définition quand il n'y en a pas | La section « When information is missing » n'a pas été collée en entier |
| Donne le nombre de requêtes porteuses | Vérifiez la section « Never » ici, et la règle 5 des Instructions |

## Critères de fin d'étape

- [ ] Le Skill `kpi-field-details` existe et est enregistré.
- [ ] Les contrôles 1 à 4 se chargent et rendent le format attendu.
- [ ] Les contrôles 5 et 6 **ne** le chargent **pas**.
- [ ] Aucune réponse ne contient de décompte ni de tableau Markdown.
