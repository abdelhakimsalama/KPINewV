# 05.00 — Principes des Skills et ordre de création

## Objectif du fichier

- **À quoi sert ce fichier** : expliquer ce qu'est un Skill dans ce projet, comment on en crée un, et dans quel ordre créer les cinq.
- **Étape du développement** : étape 05, comportements situationnels. Elle dépend des étapes 03 et 04.
- **Ce que vous faites dans Copilot Studio** : rien encore — vous lisez la méthode, puis vous enchaînez `05_01` à `05_05`, dans l'ordre.
- **Résultat attendu avant de passer à l'étape suivante** : vous savez créer un Skill et vérifier qu'il s'active au bon moment.

---

## Ce qu'est un Skill ici

Un Skill est un fichier Markdown : un **nom**, une **description**, des **instructions**. L'orchestrateur garde en permanence le nom et la description de chaque Skill sous les yeux, mais **ne charge le contenu que lorsque la description correspond à la demande** de l'utilisateur.

C'est ce mécanisme qui permet à ce projet d'avoir des Instructions courtes : cinq procédures détaillées existent, mais une seule entre en jeu à la fois, et seulement quand elle est pertinente.

**Conséquence directe :** la description n'est pas un résumé de courtoisie, c'est **le déclencheur**. Un Skill mal décrit ne se charge jamais, ou se charge tout le temps.

## Les cinq Skills et leur périmètre

| Ordre | Skill | Se déclenche sur | Ne se déclenche pas sur |
|---|---|---|---|
| 1 | `kpi-field-details` | Sens, définition, formule, type d'un champ ou KPI | Quelle requête le contient, renommages, personas |
| 2 | `mybi-sac-mapping` | Renommages MyBI → SAC, champs nouveaux | Définitions, formules |
| 3 | `sac-query-lookup` | Quelle requête contient X, contenu d'une requête, croisement de critères | Sens d'un champ isolé |
| 4 | `business-vocabulary-and-ambiguity` | Vocabulaire métier non officiel, plusieurs candidats possibles | Une question qui donne déjà le libellé officiel exact |
| 5 | `personas-and-scope` | Les six personas, requêtes d'un persona, recommandation personnelle | Tout le reste |

Créez-les **dans cet ordre** : chaque fichier de vérification suppose que les précédents existent, et l'ordre permet de détecter tôt les activations croisées.

## Comment créer un Skill

`Onglet Build > panneau Composants (à droite) > Skills > + Ajouter.`

Deux entrées possibles, au choix :

**A. Créer depuis un modèle vierge** *(le plus simple pour démarrer)* — la boîte demande trois champs : **Name**, **Description**, **Instructions**. Chaque fichier `05_0x` vous donne les trois, prêts à coller.

**B. Téléverser un fichier `SKILL.md`** *(le plus proche de la gestion en dépôt)* — les cinq `SKILL.md` complets, en-tête YAML incluse, sont déjà prêts dans [`_a-televerser/skills/`](../_a-televerser/skills/), un dossier par Skill. Vous n'avez rien à assembler : vous téléversez le fichier.

> **Recommandation de ce projet** : utilisez la méthode **B**. Le `SKILL.md` que vous téléversez est exactement celui qui est versionné ici : le dépôt reste la référence, et une modification se relit dans un diff. C'est l'un des gains les plus concrets de la nouvelle expérience — le comportement de l'agent devient du texte suivi en Git, au lieu d'une configuration invisible.
>
> Les fichiers de `_a-televerser/` sont **générés** depuis les fiches `05_0x` par `python3 outils/extraire-contenus-agent.py`. On modifie donc toujours la fiche, puis on régénère : aucune divergence n'est possible entre ce que documente le dépôt et ce que vous téléversez.

## Comment écrire une description qui route juste

Trois règles, tirées de l'expérience du terrain :

1. **Nommer précisément.** `kpi-field-details`, pas `kpi-helper`.
2. **Dire quand utiliser ET quand ne pas utiliser.** La deuxième moitié compte autant que la première : c'est elle qui empêche un Skill de capter les questions d'un autre.
3. **Employer les mots de vos utilisateurs**, dans les deux langues du projet. Un Skill décrit uniquement en anglais ne se déclenchera pas de façon fiable sur une question française.

Test de contrôle : si deux personnes raisonnables peuvent être en désaccord sur le moment où le Skill s'applique, la description n'est pas encore assez précise.

## Comment vérifier qu'un Skill s'active

Ne jugez **jamais** depuis la réponse finale : une bonne réponse peut avoir été produite sans le Skill, et une mauvaise malgré lui.

1. Onglet **Preview**, posez la question.
2. Ouvrez la **trace d'activité** de l'échange.
3. Lisez quel Skill a été chargé.

| Ce que vous constatez | Diagnostic | Correction |
|---|---|---|
| Le Skill ne se charge jamais | Description trop étroite, ou vocabulaire éloigné de celui des utilisateurs | Élargissez les formulations, ajoutez les termes français |
| Le Skill se charge sur presque tout | Description trop vague | Resserrez, et renforcez la partie « ne pas utiliser pour » |
| Deux Skills se chargent en concurrence | Périmètres qui se recouvrent | Ajoutez une exclusion explicite dans les deux descriptions |
| Le Skill se charge mais n'est pas suivi | Instructions trop longues ou contradictoires avec les règles globales | Raccourcissez ; vérifiez la cohérence avec `04_01` |

## Ce qu'un Skill n'a pas le droit de contenir

- **Des données métier.** Elles sont dans `KPIDictionary`. Seule exception assumée, la table des synonymes du Skill 4 : la source de Knowledge ne prend en charge ni glossaire ni synonymes, il n'existe donc aucun autre endroit natif **[OFFICIEL]**.
- **Une règle déjà écrite dans les Instructions.** La dupliquer, c'est créer deux vérités qui divergeront.
- **Une contradiction avec les Instructions.** En cas de conflit, le comportement devient imprévisible. Les Instructions posent le cadre, le Skill décrit la procédure **à l'intérieur** de ce cadre.

## Marge disponible

La plateforme autorise **100 Skills par agent** **[OFFICIEL]**. Vous en aurez cinq. Ce n'est pas une invitation à en ajouter : chaque Skill supplémentaire est une occasion de plus de se déclencher au mauvais moment. Cinq périmètres nets valent mieux que quinze approximatifs.

## Critères de fin d'étape

- [ ] Je sais où créer un Skill et par quelle méthode.
- [ ] J'ai compris que la description est le déclencheur, pas de la documentation.
- [ ] Je sais lire la trace d'activité pour vérifier une activation.
- [ ] Je passe à `05_01`.
