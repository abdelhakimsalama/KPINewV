# 03.01 — Connecter la liste SharePoint `KPIDictionary`

## Objectif du fichier

- **À quoi sert ce fichier** : brancher la source unique de vérité de l'agent, en direct, sans copie ni export.
- **Étape du développement** : étape 03, données. Elle dépend de l'étape 02 (l'agent doit exister).
- **Ce que vous faites dans Copilot Studio** : vous ajoutez la liste `KPIDictionary` comme source de Knowledge, vous validez la connexion, vous vérifiez qu'elle rend des résultats.
- **Résultat attendu avant de passer à l'étape suivante** : l'agent cite un contenu réel de la liste dans l'onglet Preview.

---

## Avant de commencer : le prérequis vérifié

La **recherche Dataverse doit être activée sur l'environnement**. Ce n'est pas une précaution : Microsoft l'énonce explicitement — *« Copilot Studio agents require Dataverse search to use a SharePoint list as a knowledge source. If Dataverse search is turned off in the environment, the list can't be queried and no results are returned »* **[OFFICIEL — [SharePoint Knowledge Sources Don't Return Results](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/knowledge/sharepoint-no-response)]**.

Le symptôme trompe : la source se connecte normalement, puis ne rend jamais rien. On croit à une erreur d'agent ou à une mauvaise description, alors que c'est un réglage d'environnement. Vérifiez-le **avant** de brancher la source, pas après.

> Power Platform admin center > **Environnements** > votre environnement > **Paramètres** > **Produit** > **Fonctionnalités** > **recherche Dataverse** activée.

## Ce que vous faites

1. `Onglet Build > panneau Composants (à droite) > Knowledge`.
2. Dans la boîte **Add knowledge**, choisissez le type de source **SharePoint**.
3. Choisissez **Browse items** pour retrouver la liste, ou saisissez directement son URL :

```
https://<votre-tenant>.sharepoint.com/sites/ReportingTower10/Lists/KPIDictionary
```

> Si la liste n'apparaît pas dans **Browse items** : ouvrez-la une fois dans SharePoint depuis le même navigateur, elle apparaîtra ensuite dans **Recent Lists** **[OFFICIEL]**.

4. Sélectionnez **uniquement** `KPIDictionary`. **Aucune autre liste, aucun autre site** — c'est la décision DA-03.
5. Validez l'ajout.
6. Renseignez le nom et la description de la source : c'est l'objet du fichier `03_02`, et ce n'est pas cosmétique.

## Ce que cette source sait faire

C'est le point qui change tout par rapport à l'ancienne architecture, et il mérite d'être lu attentivement.

Une liste SharePoint branchée en Knowledge dans la nouvelle expérience prend en charge **deux modes d'interrogation** **[OFFICIEL, préversion — [Add SharePoint lists](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-sharepoint-lists)]** :

1. **La recherche en langage naturel**, avec compréhension sémantique plutôt que correspondance exacte — l'utilisateur n'a pas besoin du libellé officiel pour trouver un champ.
2. **Les requêtes analytiques et d'agrégation** sur les données structurées : décomptes, filtres, synthèses et calculs simples. Les questions de type « combien de… » sont explicitement prises en charge.

Autrement dit, une bonne partie de ce que l'ancien moteur calculait est désormais **natif**. C'est précisément pour cela que le projet ne retire aucun cas d'usage par précaution : les décomptes et les croisements restent au périmètre, et l'étape 06 établit ce qui tient réellement.

## Ce qu'il faut savoir sur cette source

| Caractéristique | Conséquence pour vous |
|---|---|
| **Préversion** | La fonctionnalité évolue. Rejouez la suite de tests régulièrement, et ne considérez pas un comportement acquis parce qu'il a marché une fois **[OFFICIEL]** |
| **Connexion temps réel** | Une modification dans SharePoint est visible immédiatement. Pas de synchronisation à gérer **[OFFICIEL]** |
| **Authentification utilisateur** | La lecture se fait avec les droits SharePoint de l'utilisateur : les permissions de la liste restent la frontière d'accès **[OFFICIEL]** |
| **Consentement au premier usage** | Le premier utilisateur — vous — devra valider une connexion. C'est attendu |
| **Volumétrie** | 2 464 lignes : très confortable. Au-delà de **35 000 lignes**, la qualité et la latence se dégradent **[OFFICIEL]** |
| **Questions portant sur la totalité** | Une question qui exige d'analyser toute la liste peut être **limitée en débit ou très lente** **[OFFICIEL]**. Ce sont les cas à mesurer en priorité |
| **Nombre de listes** | Jusqu'à 10 à la fois, 10 au maximum par agent recommandé **[OFFICIEL]**. Nous en aurons une |
| **Types de colonnes pris en charge** | text, multilineText, number, boolean, dateTime, choice, lookup, personOrGroup, hyperlink, currency, calculated **[OFFICIEL]** — les 12 colonnes de `KPIDictionary` sont toutes en texte ou texte long, donc couvertes |
| **Vues non sélectionnables** | Impossible de pointer une vue filtrée : c'est la liste entière ou rien **[OFFICIEL]** |
| **Ni glossaire ni synonymes** | Le vocabulaire métier est porté par le Skill 04 — c'est la décision DA-05 **[OFFICIEL]** |

**Bonnes pratiques officielles**, reprises telles quelles : données propres et structurées, noms de colonnes clairs et descriptifs, nom de liste explicite au moment de l'ajout, données liées gardées dans une même liste — et **exécuter des évaluations et valider vos requêtes avant le déploiement en production** **[OFFICIEL]**. Ce dernier point est la raison d'être de l'étape 06.

## Les 12 colonnes que l'agent va voir

Elles sont écrites ici parce que les Skills de l'étape 05 s'y réfèrent **au caractère près**.

| Libellé exact de la colonne | Contenu |
|---|---|
| `Title` | Le **Target Persona** |
| `MyBI Query Name (EN)` | Nom du rapport dans l'ancien outil |
| `SAC Query Name - EN` | Nom officiel du rapport SAC (anglais uniquement) |
| `SAC Field name - EN` | Nom officiel du champ, anglais |
| `SAC Field name - FR` | Nom officiel du champ, français |
| `MyBI  Field name - EN` | Ancien nom du champ, anglais. **⚠ double espace après `MyBI`** |
| `MyBI Field name - FR` | Ancien nom du champ, français |
| `KPI / dimension` | `Primary KPI`, `Derived KPI` ou `Dimension` |
| `Formula - EN` | Formule de calcul, anglais |
| `Formula - FR` | Formule de calcul, français |
| `Business definition - EN` | Définition métier, anglais |
| `Business definition - FR` | Définition métier, français |

**Une ligne = un couple (requête, champ).** Un même champ apparaît sur autant de lignes qu'il y a de requêtes qui le portent — jusqu'à 34 pour le plus répandu. C'est la clé de lecture de toutes les réponses de l'agent.

## Ce que vous ne faites PAS

- Vous n'ajoutez **aucune** autre source, même « juste pour tester ».
- Vous ne téléversez **aucun** fichier, même un export de cette même liste : cela créerait une seconde vérité.
- Vous ne créez **aucune** vue dédiée : ce n'est pas sélectionnable.

## Vérification

Onglet **Preview**. L'agent n'a pas encore ses vraies instructions ; testez donc la source, pas le comportement. Deux essais :

```
What does "Plant: Plant" mean?
```

L'agent doit citer un contenu qui vient réellement de la liste — la définition officielle mentionne un magasin reconnu comme division, pouvant aussi servir d'entrepôt.

```
How many rows have the field type "Primary KPI"?
```

Cet essai teste la capacité analytique. La valeur de référence connue est **188** ; ne la donnez pas à l'agent. Peu importe ici que le compte soit exact au premier essai : ce que vous vérifiez, c'est que l'agent **tente** un décompte sur les données au lieu de refuser ou d'inventer. L'exactitude, elle, se mesure à l'étape 06 sur l'ensemble des valeurs de référence.

Si vous obtenez une réponse générique et non liée à la liste, la source ne fonctionne pas : voir le tableau ci-dessous.

## En cas de problème

| Symptôme | Cause probable | Correction |
|---|---|---|
| Aucun résultat, sur toutes les questions | **Recherche Dataverse désactivée** — cause n° 1, documentée par Microsoft | Activez-la (voir en tête de ce fichier) |
| « Vous n'avez pas accès » | Connexion SharePoint non validée, ou droits manquants sur la liste | Validez la connexion ; vérifiez vos droits SharePoint |
| Réponse générique, sans lien avec la liste | La source n'est pas interrogée | Vérifiez sa description (`03_02`) : c'est elle qui déclenche la sélection de la source |
| La liste n'apparaît pas dans Browse items | Elle n'est pas dans les listes récentes | Ouvrez-la une fois dans SharePoint, puis réessayez |

## Critères de fin d'étape

- [ ] `KPIDictionary` apparaît dans **Knowledge**, à l'état prêt.
- [ ] C'est la **seule** source.
- [ ] Dans Preview, l'agent cite un contenu réel de la liste.
- [ ] L'agent **tente** un décompte sur les données quand on lui en demande un.
- [ ] J'ai noté le libellé à double espace `MyBI  Field name - EN`.
