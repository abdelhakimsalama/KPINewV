# 05.02 — Skill 2 : `mybi-sac-mapping`

## Objectif du fichier

- **À quoi sert ce fichier** : créer le Skill qui traite les correspondances entre les anciens noms MyBI et les noms officiels SAC, ainsi que les champs nouveaux sans équivalent.
- **Étape du développement** : étape 05, deuxième des cinq Skills. Suppose `05_01` créé.
- **Ce que vous faites dans Copilot Studio** : vous créez le Skill, puis vous vérifiez son activation et le traitement du littéral `new`.
- **Résultat attendu avant de passer à l'étape suivante** : l'agent restitue une correspondance avec **les deux** libellés SAC, et ne présente jamais `new` comme un nom de champ.

---

## Les trois champs à renseigner

**Name**

```
mybi-sac-mapping
```

**Description**

```
Use when the user asks how a MyBI field or report was renamed in SAC, what an old MyBI name corresponds to today, what a SAC field used to be called in MyBI, which fields are new in SAC with no MyBI equivalent, or asks about renamed fields in general. Typical wording: "comment s'appelait X dans MyBI", "what is X called now", "ancien nom de X", "quels champs ont ete renommes", "which fields are new in SAC", "correspondance MyBI SAC", "mapping". Do NOT use when the user asks for the meaning or the formula of a field, which query contains a field, or which persona a query belongs to.
```

**Instructions**

```markdown
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

Work out the answer from the data, and make your reading explicit.

"How many fields were renamed?" can be read in more than one way, and the readings give different numbers: distinct former MyBI field names, distinct (former name, current name) pairs, or rows in the source. Each row is one (query, field) pair, so the same field repeats across queries.

1. Determine the reading that best matches what the user asked, from the wording of their question and the shape of the data.
2. State the reading you used, in one short sentence, so the number is interpretable. For example: counting distinct former MyBI field names.
3. When the wording is genuinely ambiguous and the readings would give materially different numbers, either give the reading you chose and say so, or ask one clarifying question. Do not present one reading as if it were the only one.
4. If you cannot establish the figure reliably, say so and give what you could establish.

## Never

- Never estimate a number, and never extrapolate one from the rows you happened to see.
- Never give a figure without being able to say what it counts.
- Never translate or correct an official label on either side of the mapping.
- Never infer a renaming from a resemblance between two names. Only a row in "KPIDictionary" establishes a mapping.
```

## Le fichier `SKILL.md` complet

En-tête YAML, puis le corps ci-dessus :

```yaml
---
name: mybi-sac-mapping
description: Use when the user asks how a MyBI field or report was renamed in SAC, what an old MyBI name corresponds to today, what a SAC field used to be called in MyBI, which fields are new in SAC with no MyBI equivalent, or asks about renamed fields in general. Typical wording: "comment s'appelait X dans MyBI", "what is X called now", "ancien nom de X", "quels champs ont ete renommes", "which fields are new in SAC", "correspondance MyBI SAC", "mapping". Do NOT use when the user asks for the meaning or the formula of a field, which query contains a field, or which persona a query belongs to.
---
```

## Vérification

| # | Question | Le Skill doit-il se charger ? | Ce que la réponse doit montrer |
|---|---|---|---|
| 1 | `Comment s'appelait "Downstream service rate in quantity (Argon)" dans MyBI ?` | **Oui** | L'ancien nom `Service Rate (Quantity)`, et **les deux** libellés SAC |
| 2 | `What is "Received (line)" called in MyBI?` | **Oui** | « nouveau champ, pas d'équivalent MyBI » — **jamais** le mot `New` présenté comme un nom |
| 3 | `Combien de champs ont été renommés ?` | **Oui** | **Un chiffre issu des données**, accompagné de la lecture retenue (« noms MyBI distincts », « paires », « lignes »…) |
| 4 | `Quels champs ont été renommés ?` | **Oui** | Une liste, avec mention explicite du caractère complet ou partiel |
| 5 | `Que signifie "Plant: Plant" ?` | **Non** → `kpi-field-details` | Sinon, resserrez la description |

Le contrôle 3 est le plus instructif du projet. L'ancien agent répondait **202** sans jamais dire ce qu'il comptait ; le chiffre correspondait à des quadruplets, et personne ne pouvait s'en rendre compte. C'est ce défaut-là que le nouvel agent doit éviter — pas le fait de donner un nombre.

Le critère de jugement est donc la **lisibilité du chiffre**, pas sa conformité à une valeur imposée :

| Ce que répond l'agent | Verdict |
|---|---|
| Un chiffre **et** la lecture retenue (« noms MyBI distincts », « paires », « lignes ») | **Réussite** — même si le nombre diffère du repère de non-régression : c'est une autre lecture, elle est légitime dès lors qu'elle est énoncée |
| Un chiffre **sans** dire ce qu'il compte | **Échec** — c'est exactement l'erreur de l'ancien agent |
| Une estimation, ou un chiffre extrapolé | **Échec** |
| Un refus motivé, quand la donnée ne permet pas d'établir le chiffre | Acceptable — à consigner et à re-mesurer |

Notez la valeur obtenue et la lecture annoncée : c'est ce couple qui sert de repère de non-régression pour les campagnes suivantes.

## Ajustements courants

| Symptôme | Correction |
|---|---|
| `New` présenté comme un nom de champ | La section « The literal value new » n'a pas été collée, ou la règle 10 des Instructions manque |
| Un seul libellé SAC restitué | Renforcez le point 2 de « What the answer must contain » |
| Un chiffre donné sans dire ce qu'il compte | Renforcez le point 2 de « Answering how many about renamings » |
| L'agent refuse de compter | Vérifiez que la règle 5 des Instructions a bien été collée : elle **autorise** les décomptes issus des données |
| Se charge sur les questions de définition | Renforcez le « Do NOT use » des deux descriptions concernées |

## Critères de fin d'étape

- [ ] Le Skill `mybi-sac-mapping` existe et est enregistré.
- [ ] Le contrôle 2 ne présente jamais `New` comme un nom de champ.
- [ ] **Le contrôle 3 produit un chiffre issu des données, et l'agent dit ce qu'il compte.** La valeur et la lecture annoncée sont consignées comme repère.
- [ ] Le contrôle 5 ne charge pas ce Skill.
