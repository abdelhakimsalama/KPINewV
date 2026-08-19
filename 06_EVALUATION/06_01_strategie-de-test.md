# 06.01 — Stratégie de test

## Objectif du fichier

- **À quoi sert ce fichier** : définir ce qu'on teste, avec quel outil, et pourquoi l'évaluation n'est pas une phase de fin mais l'instrument de pilotage du projet.
- **Étape du développement** : étape 06, qualité. Elle dépend des étapes 03, 04 et 05.
- **Ce que vous faites dans Copilot Studio** : vous préparez l'onglet **Evaluate** et vous importez le jeu de tests de `06_02`.
- **Résultat attendu avant de passer à l'étape suivante** : une évaluation nommée existe, exécutable, et vous savez lire ses résultats.

---

## Pourquoi cette étape est la plus importante du projet

Dans cette architecture, **rien n'est garanti par construction**. Les Instructions sont interprétées par un modèle, les Skills se chargent sur un jugement de pertinence, la recherche rend un sous-ensemble. Il n'existe aucun code qui contraigne le comportement.

Conséquence directe : **ce qui n'est pas testé n'est pas garanti**. L'évaluation n'est pas un contrôle final, c'est le seul mécanisme qui transforme une intention écrite en comportement vérifié. C'est aussi ce qui remplace, dans cette architecture, les garanties que fournissait autrefois un moteur déterministe.

## Les huit familles de tests

| Famille | Ce qu'elle vérifie | Criticité |
|---|---|---|
| **A. Exactitude et verbatim** | Les valeurs officielles sont citées telles quelles, préfixes et coquilles compris | Bloquante |
| **B. Non-invention** | Face à une information absente, l'agent dit qu'elle est absente | **Bloquante — la plus importante** |
| **C. Non-exhaustivité et refus de compter** | Aucun chiffre, aucun « tous », mention systématique que la liste peut être incomplète | **Bloquante** |
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

**Règle pratique :** automatisez A, F, G, H. Relisez B, C, D à chaque exécution complète. E se relit à chaque modification de la table de vocabulaire.

## Deux conseils qui évitent des faux résultats

**Isolez les cas.** Exécutez chaque cas dans une conversation neuve. Un agent qui a déjà parlé de `Plant: Plant` répondra différemment à la question suivante : vous testeriez alors le contexte, pas la règle.

**Vérifiez l'activation, pas seulement la réponse.** Pour la famille G, la réponse finale ne prouve rien : ouvrez la trace d'activité. Une bonne réponse produite sans le bon Skill est un test qui passe pour une mauvaise raison, et qui cassera au prochain changement.

## Ce que ce jeu de tests ne couvre pas

Trois choses, par construction : la **latence** (mesurez-la à part si elle devient un sujet), la **charge** (l'onglet Evaluate teste le comportement, pas la tenue en volume), et la **fraîcheur des données** (elle dépend de SharePoint, pas de l'agent).

## Critères de fin d'étape

- [ ] J'ai lu les huit familles et je sais lesquelles sont bloquantes.
- [ ] J'ai compris que B et C se relisent à la main.
- [ ] Le jeu de tests de `06_02` est importé dans une évaluation nommée.
- [ ] Je sais que chaque exécution consomme des crédits.
