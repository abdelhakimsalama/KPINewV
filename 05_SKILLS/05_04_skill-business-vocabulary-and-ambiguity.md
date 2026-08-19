# 05.04 — Skill 4 : `business-vocabulary-and-ambiguity`

## Objectif du fichier

- **À quoi sert ce fichier** : créer le Skill qui traduit le vocabulaire métier des utilisateurs en libellés officiels, et qui encadre les cas où plusieurs champs sans rapport répondent au même mot.
- **Étape du développement** : étape 05, quatrième des cinq Skills.
- **Ce que vous faites dans Copilot Studio** : vous créez le Skill, table de vocabulaire comprise, puis vous vérifiez le cas d'ambiguïté de référence.
- **Résultat attendu avant de passer à l'étape suivante** : sur « catégorie produit », l'agent expose **les deux** candidats, les contraste, et **demande** — sans jamais trancher seul.

---

## Pourquoi ce Skill existe

Une liste SharePoint utilisée comme source de Knowledge **ne prend en charge ni glossaire ni synonymes** **[OFFICIEL]**. Le vocabulaire métier doit donc vivre ailleurs, et un Skill est le seul endroit natif pour cela (décision DA-05).

C'est aussi un gain : la table est désormais un tableau Markdown que vous modifiez vous-même en éditant un fichier. Auparavant, ajouter un synonyme exigeait de modifier un flux, donc une intervention informatique.

**Contrepartie à connaître :** la résolution devient interprétée par le modèle au lieu d'être une égalité stricte. Elle est plus souple — variantes, pluriels, accents sont gérés naturellement — et moins prévisible. Les contrôles ci-dessous et la suite de tests de l'étape 06 la surveillent.

## Les trois champs à renseigner

**Name**

```
business-vocabulary-and-ambiguity
```

**Description**

```
Use when the user describes a field with everyday business vocabulary instead of an official label, for example "point de vente", "magasin", "boutique", "shop", "store", "categorie produit", "categorie de produit", "secteur d'activite". Also use whenever several different official fields could match what the user asked and the right one must be clarified before answering. Do NOT use when the user already gave an exact official field name or query name and there is no ambiguity about what they mean.
```

**Instructions**

```markdown
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
```

## Le fichier `SKILL.md` complet

```yaml
---
name: business-vocabulary-and-ambiguity
description: Use when the user describes a field with everyday business vocabulary instead of an official label, for example "point de vente", "magasin", "boutique", "shop", "store", "categorie produit", "categorie de produit", "secteur d'activite". Also use whenever several different official fields could match what the user asked and the right one must be clarified before answering. Do NOT use when the user already gave an exact official field name or query name and there is no ambiguity about what they mean.
---
```

## Vérification

| # | Question | Le Skill doit-il se charger ? | Ce que la réponse doit montrer |
|---|---|---|---|
| 1 | `Quelles requêtes utilisent le point de vente ?` | **Oui** | La résolution annoncée vers `Plant: Plant`, puis des requêtes |
| 2 | `Ventes par catégorie produit` | **Oui** | **Les deux** candidats, contrastés par leurs définitions, **une** question posée |
| 3 | `Que signifie secteur d'activité ?` | **Oui** | Résolution vers `Mat: Product category`, **sans** ambiguïté déclarée |
| 4 | `Que signifie "Mode : catégorie de produit" ?` | Peu importe | Le libellé exact est cherché tel quel : **la table ne doit pas détourner** la recherche |
| 5 | `Qu'est-ce qu'un pdv ?` | Peu importe | `pdv` **n'est pas** traité comme synonyme de `Plant: Plant` |
| 6 | `Que signifie "Plant: Plant" ?` | **Non** attendu | Libellé officiel exact, pas d'ambiguïté : `kpi-field-details` suffit |

Le contrôle 2 est le contrôle de référence de ce Skill : les deux familles doivent apparaître, et **aucune ne doit être choisie**. Le contrôle 5 vérifie le sens inverse — que le Skill ne sur-interprète pas des termes volontairement écartés.

## Comment faire évoluer la table

C'est le seul endroit du projet que vous modifierez régulièrement.

1. N'ajoutez une entrée qu'à partir d'un usage **réellement observé** en recette ou en production (l'onglet Monitor vous les montrera), jamais par anticipation.
2. Ajoutez la ligne dans le tableau, éditez le `SKILL.md`, téléversez la nouvelle version.
3. **Rejouez la suite de tests de l'étape 06** : une entrée de vocabulaire peut en détourner une autre.
4. Consignez l'ajout dans le dépôt : c'est ce qui garde la table lisible dans un an.

Deux garde-fous à conserver : un terme trop générique (`produit`, `catégorie` seul) détourne plus de recherches qu'il n'en résout, et au-delà de deux cibles pour un même mot, la réponse devient illisible — mieux vaut alors traiter le sujet en posant une question.

## Critères de fin d'étape

- [ ] Le Skill `business-vocabulary-and-ambiguity` existe, table de vocabulaire comprise.
- [ ] Le contrôle 2 expose **les deux** candidats et pose **une** question.
- [ ] Le contrôle 4 n'est pas détourné par la table.
- [ ] Le contrôle 5 ne traite pas `pdv` comme un synonyme.
