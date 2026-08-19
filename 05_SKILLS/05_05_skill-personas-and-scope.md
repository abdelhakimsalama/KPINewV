# 05.05 — Skill 5 : `personas-and-scope`

## Objectif du fichier

- **À quoi sert ce fichier** : créer le dernier Skill, celui qui encadre les six personas officiels et interdit d'en déduire un depuis un intitulé de poste.
- **Étape du développement** : étape 05, cinquième et dernier Skill.
- **Ce que vous faites dans Copilot Studio** : vous créez le Skill, puis vous vérifiez qu'aucun persona n'est inféré.
- **Résultat attendu avant de passer à l'étape suivante** : les cinq Skills existent, chacun s'active sur son domaine, et l'agent est fonctionnellement complet.

---

## Les trois champs à renseigner

**Name**

```
personas-and-scope
```

**Description**

```
Use when the user asks which SAC queries are available for a Target Persona, mentions one of the six official personas (Finance, Operations, Supply, Merchant Retail, Merchant Fashion, Merchant Dining), asks which persona a given query belongs to, or asks for a recommendation tailored to their own role or job. Typical wording: "quelles requetes pour le persona X", "which queries for Supply", "je suis supply planner que puis-je consulter", "a quel persona appartient la requete X", "what should I use for my role". Do NOT use when the user asks for the meaning or formula of a field, how a field was renamed, or what a specific query contains without mentioning a persona or a role.
```

**Instructions**

```markdown
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
```

## Le fichier `SKILL.md` complet

```yaml
---
name: personas-and-scope
description: Use when the user asks which SAC queries are available for a Target Persona, mentions one of the six official personas (Finance, Operations, Supply, Merchant Retail, Merchant Fashion, Merchant Dining), asks which persona a given query belongs to, or asks for a recommendation tailored to their own role or job. Typical wording: "quelles requetes pour le persona X", "which queries for Supply", "je suis supply planner que puis-je consulter", "a quel persona appartient la requete X", "what should I use for my role". Do NOT use when the user asks for the meaning or formula of a field, how a field was renamed, or what a specific query contains without mentioning a persona or a role.
---
```

## Vérification

| # | Question | Le Skill doit-il se charger ? | Ce que la réponse doit montrer |
|---|---|---|---|
| 1 | `Quelles requêtes sont pour le persona Supply ?` | **Oui** | Des requêtes réelles, caractère complet ou partiel indiqué *(repère : 17 requêtes)* |
| 2 | `À quel persona appartient "Price catalog" ?` | **Oui** | Le persona exact tel qu'il figure dans la source |
| 3 | `Je suis supply planner, que puis-je consulter ?` | **Oui** | **Aucune** déduction vers `Supply`. L'agent demande le persona officiel parmi les six |
| 4 | `What should a business analyst look at?` | **Oui** | Même conduite : pas de persona déduit d'un intitulé |
| 5 | `Combien de requêtes pour Finance ?` | **Oui** | Un chiffre issu des données, avec sa lecture *(repère : 7)* |
| 6 | `Que contient la requête "Price catalog" ?` | **Non** → `sac-query-lookup` | Sinon, resserrez les deux descriptions |

Le contrôle 3 est le contrôle de référence : « supply planner » ressemble tellement à `Supply` que le modèle sera tenté de faire le lien. S'il filtre sur `Supply` sans avoir demandé, la règle est violée — reprenez la section « Job titles are not personas ».

## Revue d'ensemble des cinq Skills

Maintenant que les cinq existent, faites une passe de **non-débordement**. Posez ces six questions et notez à chaque fois quel Skill s'est chargé.

| Question | Skill attendu |
|---|---|
| `Que signifie "Plant: Plant" ?` | `kpi-field-details` |
| `Comment s'appelait ce champ dans MyBI ?` | `mybi-sac-mapping` |
| `Quelles requêtes le contiennent ?` | `sac-query-lookup` |
| `Ventes par catégorie produit` | `business-vocabulary-and-ambiguity` |
| `Quelles requêtes pour Supply ?` | `personas-and-scope` |
| `Bonjour` | **aucun** |

La dernière ligne compte autant que les autres : un « bonjour » ne doit charger aucun Skill ni déclencher aucune recherche. Si c'est le cas, une description est trop large.

## Critères de fin d'étape

- [ ] Les **cinq** Skills existent et sont enregistrés.
- [ ] Le contrôle 3 ne déduit aucun persona d'un intitulé de poste.
- [ ] La revue de non-débordement donne le bon Skill sur les six questions.
- [ ] `Bonjour` ne charge aucun Skill.
- [ ] Je passe au dossier `06_EVALUATION`.
