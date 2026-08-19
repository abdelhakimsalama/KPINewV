# 00.02 — L'architecture en un coup d'œil

## Objectif du fichier

- **À quoi sert ce fichier** : donner l'image complète de l'agent avant de le construire, pour que chaque étape suivante ait un sens.
- **Étape du développement** : étape 00, cadrage.
- **Ce que vous faites dans Copilot Studio à partir de ce fichier** : rien. C'est la carte, pas le terrain.
- **Résultat attendu avant de passer à l'étape suivante** : vous savez nommer les trois composants de l'agent et dire ce que chacun porte.

---

## L'agent cible

```
Utilisateur (français ou anglais, dans Teams)
        │
        ▼
Agent « KPI Dictionary Assistant »
   harness GitHub Copilot · modèle OpenAI/Microsoft
        │
        ├── INSTRUCTIONS ......... ce qui est vrai à chaque tour
        │                          identité, périmètre, zéro invention, verbatim,
        │                          langue, ne jamais choisir, ne jamais compter,
        │                          personas, format, hors périmètre
        │
        ├── KNOWLEDGE (1) ........ la liste SharePoint « KPIDictionary »
        │                          connectée en direct, lue avec les droits de
        │                          l'utilisateur, source unique de vérité
        │
        └── SKILLS (5) ........... chargés à la demande selon la question
             01 kpi-field-details ................ définitions, formules, types
             02 mybi-sac-mapping ................. renommages MyBI → SAC, champs nouveaux
             03 sac-query-lookup ................. quelle requête, contenu d'une requête
             04 business-vocabulary-and-ambiguity  vocabulaire métier, ambiguïtés
             05 personas-and-scope ............... les six personas

   Memory : OFF · Tools : aucun · Agents connectés : aucun · Microsoft IQ : non
```

## Comment ça marche à l'exécution

L'utilisateur pose une question. Le moteur d'orchestration lit les **Instructions**, qui sont toujours entièrement en contexte. Il regarde ensuite les **métadonnées** des composants disponibles — le nom et la description de la source de Knowledge, le nom et la description de chaque Skill — et décide seul quoi mobiliser. Si la question porte sur une formule, il charge le Skill `kpi-field-details` et lui seul ; les quatre autres Skills restent en dehors du contexte. Il interroge `KPIDictionary`, puis compose la réponse en respectant les Instructions.

Vous ne programmez donc **aucun aiguillage**. Vous écrivez des règles, vous branchez une source, et vous décrivez cinq comportements avec assez de précision pour que l'orchestrateur sache lequel appeler.

## Ce que chaque composant a le droit de porter

| Composant | Porte | Ne porte jamais |
|---|---|---|
| **Instructions** | Ce qui est vrai dans **100 %** des conversations | Une procédure qui ne sert que dans certains cas |
| **Knowledge** | Les **données** officielles | Une règle de comportement |
| **Skill** | Une **procédure** situationnelle : quoi chercher, quoi montrer, dans quel ordre | Des données métier qui vivent déjà dans la liste |

Ce tableau est la règle d'arbitrage de tout le projet. Quand vous hésiterez sur l'endroit où écrire quelque chose, revenez-y.

## Ce que cette architecture sait faire — et ce qui reste à prouver

Une liste SharePoint branchée en Knowledge dans la nouvelle expérience prend nativement en charge **la recherche en langage naturel** et **les requêtes analytiques et d'agrégation** : décomptes, filtres, synthèses, calculs simples, questions de type « combien de… » **[OFFICIEL, préversion]**.

Tous les cas d'usage du produit restent donc au périmètre, décomptes et croisements multi-critères compris. **Rien n'est retiré par hypothèse.**

Trois choses en découlent, à tenir ensemble :

1. **L'agent a le droit de compter** — à partir des données de la liste, et en disant ce qu'il compte.
2. **Il n'a jamais le droit d'estimer.** Un chiffre vient des données ou n'est pas donné. C'est la seule frontière absolue sur ce sujet.
3. **La fiabilité réelle se mesure.** L'étape 06 confronte les réponses analytiques à des valeurs de référence connues (192 renommages, 188 `Primary KPI`, 2 requêtes couvrant `duty free` et `duty paid`…). Une capacité n'est déclarée non fiable qu'après avoir échoué de façon reproductible — et elle est alors inscrite dans `10_BACKLOG` **avec ses preuves**.

Deux réserves documentées à garder en tête : la fonctionnalité est en **préversion**, et les questions portant sur la totalité d'une grande liste peuvent être limitées en débit ou très lentes **[OFFICIEL]**.

## Critères de fin d'étape

- [ ] Je sais citer les trois composants et ce que chacun porte.
- [ ] J'ai compris que l'agent n'a aucun outil et ne calcule rien.
- [ ] J'ai compris que les décomptes sont autorisés depuis les données, jamais estimés, et validés par la mesure.
