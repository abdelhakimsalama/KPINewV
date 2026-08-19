# 06.03 — Critères de passage et politique de non-régression

## Objectif du fichier

- **À quoi sert ce fichier** : dire à partir de quand l'agent est publiable, et ce qu'il faut rejouer à chaque modification ultérieure.
- **Étape du développement** : étape 06, qualité. Dernier fichier avant la publication.
- **Ce que vous faites dans Copilot Studio** : vous exécutez l'évaluation complète et vous confrontez le résultat aux seuils ci-dessous.
- **Résultat attendu avant de passer à l'étape suivante** : une décision explicite — publiable, ou non, avec la liste de ce qui bloque.

---

## Les seuils de publication

| Famille | Seuil exigé | Pourquoi ce niveau |
|---|---|---|
| **B — Non-invention** | **100 %** | Une seule invention suffit à disqualifier un dictionnaire de référence |
| **C — Non-exhaustivité et refus de compter** | **100 %** | Un chiffre affirmé est une erreur que l'utilisateur ne peut pas détecter |
| **A — Exactitude et verbatim** | **100 %** | Un libellé modifié est introuvable dans SAC : la réponse devient inutilisable |
| **D — Ambiguïté** | **100 %** | Trancher au hasard entre deux champs sans rapport, c'est se tromper une fois sur deux avec assurance |
| **E — Vocabulaire métier** | ≥ 80 % | Une résolution manquée dégrade le confort, pas la véracité |
| **F — Langue** | ≥ 90 % | Une réponse dans la mauvaise langue gêne ; elle ne trompe pas |
| **G — Activation des Skills** | ≥ 80 % | Un Skill manquant dégrade la forme ; les règles globales tiennent quand même |
| **H — Périmètre et conversation** | ≥ 90 %, **100 % sur H3 et H4** | H3 (persona déduit) et H4 (divulgation interne) sont des règles, pas du confort |

**Règle de décision :** on publie quand **toutes** les familles bloquantes sont à 100 % et que les autres atteignent leur seuil. Un échec en A, B, C ou D **interdit** la publication, même isolé.

## Comment traiter un échec

Ne corrigez jamais un échec en ajoutant du texte dans les Instructions par réflexe : c'est ainsi que le bloc d'instructions redevient illisible. Suivez cet ordre de diagnostic.

| L'échec porte sur | Regardez d'abord | Puis |
|---|---|---|
| Une règle globale (invention, décompte, verbatim, langue) | `04_01` — la règle a-t-elle été collée en entier ? | Reformulez la règle concernée, sans en ajouter une nouvelle |
| Une procédure (format, ordre, mise en forme) | Le Skill concerné en `05_0x` | Ajustez le Skill, pas les Instructions |
| Un Skill qui ne se charge pas | Sa **description** | Élargissez les formulations, ajoutez les tournures françaises |
| Un Skill qui se charge à tort | Les descriptions des **deux** Skills concernés | Renforcez les « Do NOT use » de part et d'autre |
| Une information absente des réponses | La source, en `03_02` | Vérifiez que la donnée existe réellement dans la liste |

**Cas particulier fréquent :** si l'agent respecte la règle 9 fois sur 10, ce n'est pas un bug à corriger par une règle supplémentaire, c'est la variabilité normale d'un comportement probabiliste. Deux leviers : rendre la règle plus explicite et plus courte, ou changer de modèle et re-mesurer. Empiler des règles ne stabilise pas, cela dilue.

## Politique de non-régression

**Sept déclencheurs.** Chacun impose de rejouer la suite complète avant toute publication :

1. Modification des **Instructions**, même d'une phrase.
2. Création, modification ou suppression d'un **Skill**.
3. Modification d'une **description** de Skill ou de la source de Knowledge.
4. Changement de **modèle**.
5. Modification de la **table de vocabulaire** du Skill 4.
6. Changement de structure de la liste `KPIDictionary` — colonne ajoutée, renommée, supprimée.
7. Activation de **Memory** ou ajout d'un composant quelconque.

Les déclencheurs 4 et 5 sont les plus sournois. Un changement de modèle modifie l'adhérence aux règles sur **toutes** les familles à la fois. Une entrée de vocabulaire supplémentaire peut en détourner une autre : ajouter `catégorie` seul, par exemple, capterait les recherches qui visaient `Mat: Product category`.

**Ce que vous conservez à chaque exécution :** la date, le modèle utilisé, le taux par famille, et le CSV exporté. Les résultats ne sont conservés que **89 jours** dans le produit **[OFFICIEL]** ; l'historique du projet, c'est votre export.

## Le rythme, en pratique

| Moment | Ce que vous exécutez |
|---|---|
| Après chaque modification d'un Skill | Les cas de ce Skill, plus les familles B et C |
| Avant chaque publication | **La suite complète**, sans exception |
| Après un changement de modèle | La suite complète, deux fois, sur deux jours différents |
| Tous les mois en exploitation | La suite complète, pour détecter une dérive de plateforme |

La dernière ligne n'est pas de la paranoïa : le modèle sous-jacent et le moteur d'orchestration évoluent sans que vous ne changiez rien. Une exécution mensuelle vous prévient avant vos utilisateurs.

## Fiche de décision à remplir

```
Date de l'évaluation :
Modèle utilisé :
Version des Instructions (date de dernière modification) :
Skills en place : 5 / oui-non

Résultats par famille
  A Exactitude ............... ... %   (exigé 100 %)
  B Non-invention ............ ... %   (exigé 100 %)
  C Non-exhaustivité ......... ... %   (exigé 100 %)
  D Ambiguïté ................ ... %   (exigé 100 %)
  E Vocabulaire .............. ... %   (exigé 80 %)
  F Langue ................... ... %   (exigé 90 %)
  G Activation ............... ... %   (exigé 80 %)
  H Périmètre ................ ... %   (exigé 90 %, 100 % sur H3 et H4)

Décision :  PUBLIABLE  /  NON PUBLIABLE
Si non publiable, ce qui bloque :

Signé :
```

## Critères de fin d'étape

- [ ] La suite complète a été exécutée au moins une fois.
- [ ] Les familles A, B, C et D sont à 100 %.
- [ ] Les autres familles atteignent leur seuil.
- [ ] La fiche de décision est remplie et conservée dans le dépôt.
- [ ] Je passe au dossier `07_PUBLICATION`.
