# 10.02 — Options si l'évaluation échoue ou si le besoin évolue

## Objectif du fichier

- **À quoi sert ce fichier** : préparer à l'avance les réponses possibles si l'architecture simple ne suffit pas, pour que la décision soit prise avec un coût connu plutôt que dans l'urgence.
- **Étape du développement** : étape 10, lucidité. À ouvrir seulement si un seuil de `06_03` ne peut pas être atteint, ou si le métier refuse une limite de `10_01`.
- **Ce que vous faites dans Copilot Studio à partir de ce fichier** : rien tant que le besoin n'est pas démontré.
- **Résultat attendu** : toute extension future est un choix documenté, jamais un réflexe.

---

## La règle d'escalade

> **On n'ajoute un composant que si un besoin fonctionnel réel, constaté et documenté, ne peut pas être couvert autrement.**

Un « ce serait bien si » ne franchit pas ce seuil. Un « le métier refuse de valider sans cela » le franchit. Entre les deux, mesurez avant de décider.

Avant toute escalade, épuisez systématiquement les leviers gratuits, dans cet ordre :

1. **Reformuler une règle** dans les Instructions — plus court et plus explicite bat plus long.
2. **Reformuler une description de Skill** — la plupart des problèmes d'activation viennent de là.
3. **Changer de modèle** et re-mesurer — l'adhérence aux règles varie sensiblement d'un modèle à l'autre.
4. **Corriger la donnée** dans `KPIDictionary` — beaucoup de « bugs d'agent » sont des données absentes ou ambiguës.

Ces quatre leviers coûtent une édition de fichier et une exécution de tests. Ils résolvent la majorité des situations. N'allez au-delà qu'ensuite.

## Les options d'extension, par ordre de complexité croissante

### Option A — Enrichir la table de vocabulaire *(coût : minime)*

**Quand :** l'agent ne trouve pas ce que les utilisateurs cherchent, parce qu'ils emploient des mots absents de la table.

**Ce que vous faites :** ajoutez les entrées observées dans le Skill 4 (voir `05_04`), sur la base du relevé de `08_01`.

**Coût :** l'édition d'un fichier Markdown, plus la famille E rejouée. Aucune complexité ajoutée. **C'est presque toujours la bonne première réponse.**

### Option B — Découper ou fusionner des Skills *(coût : faible)*

**Quand :** un Skill ne se déclenche jamais, ou capte des questions qui ne le concernent pas, et les descriptions ont déjà été retravaillées deux fois.

**Ce que vous faites :** découpez un Skill trop large en deux périmètres nets, ou fusionnez deux Skills qui se disputent les mêmes questions.

**Coût :** une réécriture de fichiers et la famille G rejouée en entier. La plateforme autorise 100 Skills : la contrainte n'est pas le nombre, c'est la netteté des frontières.

### Option C — Restaurer les décomptes et l'exhaustivité *(coût : élevé — c'est un changement d'architecture)*

**Quand :** et seulement quand le métier refuse formellement la limite 1 ou 2 de `10_01`, par écrit, avec un cas d'usage précis à l'appui.

**Ce que cela suppose :** un composant capable de parcourir l'intégralité des lignes et de calculer. C'est-à-dire, concrètement, un **outil** — connecteur, workflow ou exécution de code — qui rend des données brutes que l'agent ne fait que restituer.

**Ce que cela coûte vraiment :**

| Ce que vous gagnez | Ce que vous payez |
|---|---|
| Décomptes exacts, exhaustivité, croisements prouvés | Un composant technique de plus à développer, tester et maintenir |
| Les cas de test retirés redeviennent valides | Un contrat entre l'agent et l'outil, qu'il faut garder synchronisé — le défaut n° 1 de l'ancienne architecture |
| | Une consommation de crédits supérieure à chaque question |
| | La simplicité, qui était l'objectif du projet |

**Avant de choisir cette option, posez la vraie question :** combien de questions réelles, sur un mois d'usage mesuré dans Monitor, exigent un décompte exact ? Si la réponse est « trois par mois », la bonne solution est un lien vers la liste SharePoint dans la réponse de l'agent — pas un moteur de calcul.

### Option D — Deuxième source de Knowledge *(coût : moyen, risque élevé)*

**Quand :** un besoin apparaît sur des données qui ne sont pas dans `KPIDictionary`.

**Le risque à mesurer :** avec deux sources, l'origine d'une réponse devient indécidable, et la règle « source unique » tombe. Dans la nouvelle expérience, il n'existe pas de bascule de connaissances générales à désactiver : le nombre de sources est votre principal levier de contrôle **[OFFICIEL]**.

**Si vous y allez malgré tout :** une description très explicite pour chaque source, et des cas de test dédiés vérifiant que la bonne source répond à la bonne question.

### Option E — Second agent, connecté *(coût : élevé)*

**Quand :** un domaine réellement distinct apparaît — un autre référentiel, un autre public, un autre propriétaire.

**Le test de décision :** l'autre domaine tiendrait-il debout comme agent autonome, utilisé pour lui-même ? Si oui, c'est un agent. Si non, c'est un Skill de plus.

**Ce qui n'est PAS un motif :** « l'agent commence à faire beaucoup de choses ». Avec cinq Skills et une source, vous êtes très loin des seuils où la décomposition se justifie.

## Ce qu'il ne faut pas faire, quel que soit le problème

| Réflexe | Pourquoi c'est une mauvaise réponse |
|---|---|
| Allonger les Instructions à chaque échec | Elles sont chargées à chaque tour ; c'est le mécanisme exact qui a saturé l'ancien agent |
| Ajouter un Skill par cas particulier | Multiplie les occasions de se déclencher au mauvais moment ; cinq périmètres nets valent mieux que quinze approximatifs |
| Autoriser l'agent à estimer un nombre « approximatif » | Un chiffre estimé sera lu comme un fait. C'est précisément le défaut que le projet interdit |
| Reconstruire l'ancienne architecture composant par composant | Vous retrouveriez tous ses défauts, plus le coût de la migration |
| Ajouter un composant « au cas où » | Chaque composant a un coût permanent de compréhension et de maintenance |

## Fiche de décision d'extension

À remplir **avant** toute escalade, et à archiver dans `01_02`.

```
Date :
Besoin constaté (cas d'usage précis, pas une hypothèse) :
Fréquence mesurée dans Monitor sur un mois :
Leviers gratuits déjà essayés (les quatre de la règle d'escalade) :
  1. Reformulation de règle .......... essayé / résultat :
  2. Reformulation de description .... essayé / résultat :
  3. Changement de modèle ............ essayé / résultat :
  4. Correction de la donnée ......... essayé / résultat :
Option retenue (A / B / C / D / E) :
Coût accepté en complexité et en maintenance :
Décision prise par :
```

## Critères de fin d'étape

- [ ] Je connais les quatre leviers gratuits à épuiser avant toute escalade.
- [ ] Je sais que l'option C est un changement d'architecture, pas un réglage.
- [ ] Toute extension future passera par la fiche de décision ci-dessus.
- [ ] **Le développement est terminé.** L'agent est construit, testé, publié et maintenable.
