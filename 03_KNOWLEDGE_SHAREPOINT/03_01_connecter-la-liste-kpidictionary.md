# 03.01 — Connecter la liste SharePoint `KPIDictionary`

## Objectif du fichier

- **À quoi sert ce fichier** : brancher la source unique de vérité de l'agent, en direct, sans copie ni export.
- **Étape du développement** : étape 03, données. Elle dépend de l'étape 02 (l'agent doit exister).
- **Ce que vous faites dans Copilot Studio** : vous ajoutez la liste `KPIDictionary` comme source de Knowledge, vous validez la connexion, vous vérifiez qu'elle rend des résultats.
- **Résultat attendu avant de passer à l'étape suivante** : l'agent cite un contenu réel de la liste dans l'onglet Preview.

---

## Avant de commencer

La **recherche Dataverse** doit être activée sur l'environnement (voir `01_01`). Sans elle, la source se connecte mais ne rend rien, et le symptôme trompe : on croit à une erreur d'agent alors que c'est un réglage d'environnement. **[À VÉRIFIER]**

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

## Ce qu'il faut savoir sur cette source

| Caractéristique | Conséquence pour vous |
|---|---|
| **Connexion temps réel** | Une modification dans SharePoint est visible immédiatement. Pas de synchronisation à gérer **[OFFICIEL]** |
| **Authentification utilisateur** | La lecture se fait avec les droits SharePoint de l'utilisateur : les permissions de la liste restent la frontière d'accès **[OFFICIEL]** |
| **Consentement au premier usage** | Le premier utilisateur — vous — devra valider une connexion. C'est attendu |
| **Volumétrie** | 2 464 lignes, très en deçà des seuils documentés (jusqu'à 15 listes et 35 000 lignes ; la qualité et la latence se dégradent au-delà) **[OFFICIEL]** |
| **Vues non sélectionnables** | Impossible de pointer une vue filtrée : c'est la liste entière ou rien **[OFFICIEL]** |
| **Ni glossaire ni synonymes** | Le vocabulaire métier est porté par le Skill 04 — c'est la décision DA-05 **[OFFICIEL]** |
| **Ni décompte ni filtrage par valeur de colonne** | L'agent ne peut pas répondre « combien » ni « liste toutes les lignes où la colonne X vaut Y ». C'est la décision DA-04 **[OFFICIEL]** |

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

Onglet **Preview**. L'agent n'a pas encore ses vraies instructions ; testez donc la source, pas le comportement :

```
What does "Plant: Plant" mean?
```

L'agent doit citer un contenu qui vient réellement de la liste — la définition officielle mentionne un magasin reconnu comme division, pouvant aussi servir d'entrepôt. Si vous obtenez une réponse générique et non liée à la liste, la source ne fonctionne pas : voir le tableau ci-dessous.

## En cas de problème

| Symptôme | Cause probable | Correction |
|---|---|---|
| Aucun résultat, sur toutes les questions | Recherche Dataverse désactivée | `01_01`, section 2 |
| « Vous n'avez pas accès » | Connexion SharePoint non validée, ou droits manquants sur la liste | Validez la connexion ; vérifiez vos droits SharePoint |
| Réponse générique, sans lien avec la liste | La source n'est pas interrogée | Vérifiez sa description (`03_02`) : c'est elle qui déclenche la sélection de la source |
| La liste n'apparaît pas dans Browse items | Elle n'est pas dans les listes récentes | Ouvrez-la une fois dans SharePoint, puis réessayez |

## Critères de fin d'étape

- [ ] `KPIDictionary` apparaît dans **Knowledge**, à l'état prêt.
- [ ] C'est la **seule** source.
- [ ] Dans Preview, l'agent cite un contenu réel de la liste.
- [ ] J'ai noté le libellé à double espace `MyBI  Field name - EN`.
