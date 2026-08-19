# 07.02 — Basculer depuis l'agent actuel

## Objectif du fichier

- **À quoi sert ce fichier** : organiser le remplacement de l'agent existant sans coupure ni perte de service, et fixer les critères qui autorisent la bascule.
- **Étape du développement** : étape 07, mise en service. Dernier fichier avant l'exploitation.
- **Ce que vous faites dans Copilot Studio** : vous exploitez les deux agents en parallèle, puis vous retirez l'ancien.
- **Résultat attendu avant de passer à l'étape suivante** : un seul agent en service, l'ancien retiré proprement.

---

## Le principe : parallèle, jamais bascule sèche

Les deux agents coexistent sans conflit : ce sont deux agents distincts, sur deux harnesses différents, dont aucun n'est convertible en l'autre **[OFFICIEL]**. Vous n'avez donc rien à migrer, et surtout rien à casser pour avancer.

```
Semaines 1-2   ancien agent = production   ·   nouvel agent = pilote (5-10 personnes)
Semaines 3-4   ancien agent = production   ·   nouvel agent = ouvert plus largement
Bascule        ancien agent = retiré       ·   nouvel agent = production
Après          ancien agent conservé désactivé pendant un mois, puis supprimé
```

## Les cinq critères de bascule

Ne basculez pas sur une impression. Ces cinq conditions doivent être vraies **en même temps** :

| # | Critère | Comment le constater |
|---|---|---|
| 1 | La suite de tests complète passe aux seuils de `06_03` | Fiche de décision signée |
| 2 | Deux semaines de pilote sans **aucune** invention signalée | Retours du groupe pilote + onglet Monitor |
| 3 | Aucun chiffre estimé, aucune couverture affirmée sans preuve pendant le pilote | Relecture des échanges dans Monitor |
| 4 | Les utilisateurs pilotes préfèrent le nouvel agent, ou le jugent équivalent | Demandez-le explicitement, ne le supposez pas |
| 5 | Le registre de `10_01` est rempli et **accepté par le métier**, par écrit | Voir la section suivante |

Le critère 5 est celui qu'on oublie et qui fait revenir un projet en arrière trois mois plus tard.

## Ce que le métier doit valider, explicitement

**Ce que vous présentez dépend de ce que vous avez mesuré**, et de rien d'autre. Prenez le registre de `10_01` rempli à l'étape 06, et présentez trois choses :

1. **Les capacités analytiques déclarées fiables** (3 essais réussis sur 3) — annoncez-les comme telles, elles font partie du produit.
2. **Celles classées à surveiller** (2 sur 3) — nommez-les, avec la réserve qui les accompagne.
3. **Celles déclarées non fiables**, s'il y en a — nommez-les, avec les preuves, et dites que la liste `KPIDictionary` fait foi sur ces points.

**Un point à porter en réunion dans tous les cas :** l'ancien agent annonçait « 202 champs renommés » sans jamais dire ce qu'il comptait, et aucun utilisateur ne pouvait vérifier. Le nouvel agent détermine le résultat depuis les données et **énonce sa lecture** — noms distincts, paires, lignes. Ce que le projet garantit désormais, ce n'est pas un chiffre unique et définitif : c'est qu'un chiffre vient des données et qu'on sait ce qu'il mesure.

Si le métier juge qu'une capacité classée non fiable est indispensable, **ne basculez pas** : allez lire `10_02`, qui décrit ce qu'il faudrait ajouter et ce que cela coûte.

## Retirer l'ancien agent

Une fois la bascule décidée :

1. **Annoncez** la date aux utilisateurs, avec le lien vers le nouvel agent.
2. **Retirez l'ancien de ses canaux** — commencez par là : c'est réversible en quelques minutes si un problème surgit.
3. **Attendez une semaine** avant toute action irréversible.
4. **Désactivez** l'ancien agent, sans le supprimer.
5. **Conservez-le désactivé un mois**, puis supprimez-le.

Ne supprimez pas le flux Power Automate en même temps que l'agent : il peut être référencé ailleurs, et sa suppression est définitive. Vérifiez ses dépendances avant d'y toucher.

## Plan de repli

Si un défaut sérieux apparaît après la bascule :

1. **Republiez l'ancien agent sur son canal** — c'est l'action la plus rapide, quelques minutes.
2. Reproduisez le défaut dans l'onglet **Preview** du nouvel agent.
3. Ouvrez la **trace d'activité** de l'échange fautif : elle vous dit quel Skill s'est chargé et ce qui a été cherché.
4. Corrigez au bon endroit selon le tableau de diagnostic de `06_03`.
5. Rejouez la suite complète, republiez, reprenez le pilote.

Tant que l'ancien agent existe, le repli coûte quelques minutes. C'est précisément pourquoi on le conserve un mois.

## Critères de fin d'étape

- [ ] Les cinq critères de bascule sont vrais simultanément.
- [ ] Le registre de `10_01`, rempli à partir des mesures, est accepté **par écrit** par le métier.
- [ ] L'ancien agent est retiré de ses canaux, puis désactivé.
- [ ] Le plan de repli est connu de l'équipe.
- [ ] Je passe au dossier `08_MONITORING_ET_COUTS`.
