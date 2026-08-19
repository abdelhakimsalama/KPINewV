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
| **A — Exactitude et verbatim** | **100 %** | Un libellé modifié est introuvable dans SAC : la réponse devient inutilisable |
| **B — Non-invention** | **100 %** | Une seule invention suffit à disqualifier un dictionnaire de référence |
| **C — Chiffres** *(critère origine)* | **100 %** | Un chiffre que l'agent ne peut pas justifier est indétectable pour l'utilisateur |
| **C — Chiffres** *(critère exactitude)* | **Mesuré, pas seuillé** | Voir la règle de décision analytique ci-dessous |
| **D — Croisements** *(critère preuve)* | **100 %** | Une couverture affirmée sans champ cité n'est pas vérifiable |
| **D — Croisements** *(critère exactitude)* | **Mesuré, pas seuillé** | Idem |
| **E — Ambiguïté** | **100 %** | Trancher au hasard entre deux champs sans rapport, c'est se tromper une fois sur deux avec assurance |
| **F — Vocabulaire métier** | ≥ 80 % | Une résolution manquée dégrade le confort, pas la véracité |
| **G — Langue** | ≥ 90 % | Une réponse dans la mauvaise langue gêne ; elle ne trompe pas |
| **H — Activation des Skills** | ≥ 80 % | Un Skill manquant dégrade la forme ; les règles globales tiennent quand même |
| **I — Périmètre et conversation** | ≥ 90 %, **100 % sur I3 et I4** | I3 (persona déduit) et I4 (divulgation interne) sont des règles, pas du confort |

**Règle de décision générale :** on publie quand toutes les familles bloquantes atteignent 100 % et que les autres atteignent leur seuil.

## La règle de décision analytique

Les familles C et D ne se jugent pas comme les autres, parce qu'on y mesure deux choses différentes.

**Le critère d'origine et de preuve est bloquant, sans exception.** Un chiffre que l'agent ne peut pas justifier, ou une couverture affirmée sans champ cité, interdit la publication. C'est la garantie qui remplace celle qu'apportait l'ancien moteur.

**Le critère d'exactitude, lui, décide du périmètre annoncé, pas de la publication :**

| Résultat mesuré | Décision |
|---|---|
| Exact **3 fois sur 3** contre l'oracle | La capacité est **fiable**. Elle est annoncée aux utilisateurs comme telle |
| Exact **2 fois sur 3**, ou écart faible et explicable | La capacité est **à surveiller**. Elle reste active ; l'agent la présente avec sa réserve habituelle ; le cas revient à chaque campagne |
| Exact **moins de 2 fois sur 3**, après ajustement des règles et du Skill | La capacité est **non fiable sur ce cas**. On l'écrit dans `10_01` **avec les preuves** — et seulement à ce moment-là |

Aucune capacité ne descend au troisième niveau sans être passée par les deux premiers. C'est la contrepartie du principe de non-disqualification : on ne retire rien sans mesure, mais on n'annonce rien non plus sans mesure.

## Comment traiter un échec

Ne corrigez jamais un échec en ajoutant du texte dans les Instructions par réflexe : c'est ainsi que le bloc d'instructions redevient illisible. Suivez cet ordre de diagnostic.

| L'échec porte sur | Regardez d'abord | Puis |
|---|---|---|
| Une règle globale (invention, origine du chiffre, verbatim, langue) | `04_01` — la règle a-t-elle été collée en entier ? | Reformulez la règle concernée, sans en ajouter une nouvelle |
| Un décompte faux | **Ce que l'agent a compté** — lignes plutôt que valeurs distinctes est l'erreur n° 1, et c'est celle que faisait l'ancien moteur | Précisez la définition dans le Skill concerné, puis re-mesurez |
| Un décompte refusé | La règle 5 de `04_01` — elle **autorise** les décomptes issus des données | Vérifiez qu'elle a été collée ; ne la durcissez pas |
| Un décompte très lent ou sans réponse | Le périmètre de la question : les questions portant sur toute la liste peuvent être limitées en débit **[OFFICIEL]** | Consignez la latence ; c'est un candidat pour `10_01` si c'est reproductible |
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

La fonctionnalité de liste SharePoint en Knowledge étant en **préversion**, ajoutez un neuvième déclencheur implicite : le temps. Rejouez les familles C et D une fois par mois même sans modification de votre part.

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
  A Exactitude ............................ ... %   (exigé 100 %)
  B Non-invention ....................... ... %   (exigé 100 %)
  C Chiffres — origine .................. ... %   (exigé 100 %)
  C Chiffres — exactitude vs oracle ..... ... / 9 cas   (mesuré)
  D Croisements — preuve ................ ... %   (exigé 100 %)
  D Croisements — exactitude vs oracle .. ... / 5 cas   (mesuré)
  E Ambiguïté ........................... ... %   (exigé 100 %)
  F Vocabulaire ......................... ... %   (exigé 80 %)
  G Langue .............................. ... %   (exigé 90 %)
  H Activation .......................... ... %   (exigé 80 %)
  I Périmètre ........................... ... %   (exigé 90 %, 100 % sur I3 et I4)

Capacités analytiques — classement après mesure
  Fiables (3/3) :
  À surveiller (2/3) :
  Non fiables (<2/3), à documenter dans 10_01 :

Latence des cas sentinelles
  C3 (1 767 lignes) : ... s      D3 (18 requêtes) : ... s

Décision :  PUBLIABLE  /  NON PUBLIABLE
Si non publiable, ce qui bloque :

Signé :
```

## Critères de fin d'étape

- [ ] La suite complète a été exécutée au moins une fois.
- [ ] Les familles A, B et E sont à 100 %.
- [ ] Les critères **origine** (C) et **preuve** (D) sont à 100 %.
- [ ] Chaque capacité analytique est classée fiable / à surveiller / non fiable, **sur mesure**.
- [ ] Les autres familles atteignent leur seuil.
- [ ] La fiche de décision est remplie et conservée dans le dépôt.
- [ ] Je passe au dossier `07_PUBLICATION`.
