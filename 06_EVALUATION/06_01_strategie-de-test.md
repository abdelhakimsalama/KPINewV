# 06.01 — Stratégie de test

## Objectif du fichier

- **À quoi sert ce fichier** : définir ce qu'on teste, avec quel outil, et pourquoi l'évaluation n'est pas une phase de fin mais l'instrument de pilotage du projet.
- **Étape du développement** : étape 06, qualité. Elle dépend des étapes 03, 04 et 05.
- **Ce que vous faites dans Copilot Studio** : vous préparez l'onglet **Evaluate** et vous importez le jeu de tests de `06_02`.
- **Résultat attendu avant de passer à l'étape suivante** : une évaluation nommée existe, exécutable, et vous savez lire ses résultats.

---

## Pourquoi cette étape est la plus importante du projet

Dans cette architecture, **rien n'est garanti par construction**. Les Instructions sont interprétées par un modèle, les Skills se chargent sur un jugement de pertinence, la recherche et les agrégations s'exécutent côté plateforme.

Conséquence directe : **ce qui n'est pas testé n'est pas garanti** — mais aussi, et c'est le pendant tout aussi important, **ce qui n'est pas testé n'est pas disqualifié**. L'évaluation est le seul mécanisme qui transforme une intention écrite en comportement vérifié, et le seul qui autorise à déclarer qu'une capacité ne marche pas.

Microsoft prescrit d'ailleurs exactement cette démarche pour les listes SharePoint en Knowledge : *« run evaluations and validate your queries before production rollout »* **[OFFICIEL]**.

## Le principe de non-disqualification

Aucune capacité n'est retirée du périmètre par hypothèse. Les décomptes, les agrégations et les croisements multi-critères sont des besoins fonctionnels du produit ; la source les prend nativement en charge **[OFFICIEL, préversion]** ; ils sont donc **testés avec de vraies valeurs de référence**.

Une capacité n'est documentée comme limitation dans `10_01` qu'après avoir été mesurée, avoir échoué **de façon reproductible**, et avoir résisté aux ajustements de règle et de Skill. Pas avant.

## Les huit familles de tests

| Famille | Ce qu'elle vérifie | Criticité |
|---|---|---|
| **A. Exactitude et verbatim** | Les valeurs officielles sont citées telles quelles, préfixes et coquilles compris | Bloquante |
| **B. Non-invention** | Face à une information absente, l'agent dit qu'elle est absente | **Bloquante — la plus importante** |
| **D. Ambiguïté** | Plusieurs candidats exposés, aucun choisi, une question posée | Bloquante |
| **E. Vocabulaire métier** | Les termes de la table sont résolus, les termes écartés ne le sont pas | Importante |
| **F. Langue** | Réponse dans la langue du message, libellés jamais traduits | Importante |
| **G. Activation des Skills** | Le bon Skill se charge, les autres non | Importante |
| **H. Périmètre et conversation** | Hors périmètre refusé, salutation sans recherche | Importante |

Les familles B et C sont celles qui portent la valeur du produit. Un agent qui échoue en B invente ; un agent qui échoue en C affirme des chiffres faux. Les deux produisent une réponse fausse d'apparence officielle — le défaut que le projet interdit absolument.

## L'outil : l'onglet Evaluate

`Onglet Evaluate > créer une évaluation.` Une évaluation associe un **jeu de tests** à une ou plusieurs **méthodes de notation**, puis produit un résultat par cas et un taux de réussite.

**Ce que vous devez savoir avant de commencer :**

- Un jeu de tests à réponse unique accepte jusqu'à **100 cas** ; un jeu conversationnel jusqu'à **20 cas** de 12 messages **[OFFICIEL]**. Notre jeu de référence tient largement dans ces limites.
- Les résultats sont conservés **89 jours** et exportables en CSV **[OFFICIEL]**. Au-delà, exportez si vous voulez garder l'historique.
- **Chaque exécution consomme des Copilot Credits** **[OFFICIEL]**. C'est la principale source de consommation en phase de projet : lancez la suite complète aux moments qui comptent, pas à chaque micro-ajustement.

## Deux façons de noter, et pourquoi il en faut deux

**La notation automatique** (juge de qualité générale, correspondance exacte, similarité) traite le volume et détecte les régressions franches.

**La relecture humaine** reste indispensable sur les familles B, C et D, parce que l'échec y est souvent **une nuance de formulation**, pas une erreur factuelle. Exemple : à la question « quelles requêtes contiennent A et B », la réponse « ces deux requêtes couvrent vos critères » est un échec même si les deux requêtes sont les bonnes — parce qu'elle affirme une couverture sans citer la preuve. Aucun juge automatique ne le verra de façon fiable.

**Règle pratique :** automatisez A, G, H, I. Relisez **B, C, D et E** à chaque exécution complète — ce sont les familles où l'échec est une nuance de formulation ou une justification manquante. F se relit à chaque modification de la table de vocabulaire.

**Pour C et D spécifiquement :** trois essais par cas, dans des conversations séparées, et consignation de l'écart au repère **et** de la latence. Une capacité analytique est déclarée fiable à 3 succès sur 3, à surveiller à 2 sur 3, non fiable en dessous.

## Deux conseils qui évitent des faux résultats

**Isolez les cas.** Exécutez chaque cas dans une conversation neuve. Un agent qui a déjà parlé de `Plant: Plant` répondra différemment à la question suivante : vous testeriez alors le contexte, pas la règle.

**Vérifiez l'activation, pas seulement la réponse.** Pour la famille H, la réponse finale ne prouve rien : ouvrez la trace d'activité. Une bonne réponse produite sans le bon Skill est un test qui passe pour une mauvaise raison, et qui cassera au prochain changement.

**Mesurez la latence sur les cas analytiques.** Microsoft signale que les questions portant sur la totalité d'une grande liste peuvent être limitées en débit ou très lentes **[OFFICIEL]**. C3 (1 767 lignes) et D3 (18 requêtes) sont vos cas sentinelles : notez leur temps de réponse à chaque campagne.

## Ce que ce jeu de tests ne couvre pas

Deux choses, par construction : la **charge** (l'onglet Evaluate teste le comportement, pas la tenue en volume simultané) et la **fraîcheur des données** (elle dépend de SharePoint, pas de l'agent). La latence, elle, **est** couverte, mais à la main : notez-la sur les cas sentinelles.

## Critères de fin d'étape

- [ ] J'ai lu les neuf familles et je sais lesquelles sont bloquantes.
- [ ] J'ai compris que B, C, D et E se relisent à la main.
- [ ] J'ai compris le principe de non-disqualification : rien n'est retiré du périmètre sans mesure.
- [ ] Le jeu de tests de `06_02` est importé dans une évaluation nommée.
- [ ] Je sais que chaque exécution consomme des crédits.
