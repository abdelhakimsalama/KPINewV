# 09.01 — Solution et cycle de vie

## Objectif du fichier

- **À quoi sert ce fichier** : organiser le transport de l'agent entre environnements et faire du dépôt Git la référence de son comportement.
- **Étape du développement** : étape 09, durée de vie. À mettre en place dès que l'agent est stable.
- **Ce que vous faites dans Copilot Studio** : vous vérifiez que l'agent appartient à une solution, et vous instaurez la sauvegarde de ses Skills dans ce dépôt.
- **Résultat attendu avant de passer à l'étape suivante** : l'agent est transportable, et son comportement est lisible dans Git.

---

## Le principe

Un agent Copilot Studio se transporte entre environnements via une **solution** Power Platform. Les Skills d'un agent voyagent **avec lui** dans la solution.

Pour ce projet, la chaîne complète tient en peu de choses, parce qu'il y a peu de choses :

| Ce qui voyage dans la solution | Ce qui ne voyage pas |
|---|---|
| L'agent, ses Instructions, ses 5 Skills | La **liste SharePoint** — elle vit dans SharePoint, indépendamment |
| La configuration de la source de Knowledge | Les **connexions** — elles se revalident par environnement |
| | Les **résultats d'évaluation** — exportez-les si vous voulez les garder |

## Une organisation à deux environnements suffit

Beaucoup de projets copient un schéma Dev / Test / Prod par principe. Ici, l'agent n'a ni code ni intégration : **Développement → Production** suffit, et la simplicité est le but du projet.

```
Environnement de DÉVELOPPEMENT          Environnement de PRODUCTION
  vous construisez et testez              les utilisateurs consomment
  suite d'évaluation exécutée ici         republication après import
              │                                    ▲
              └────── export de solution ──────────┘
```

**Un troisième environnement ne se justifierait que si** plusieurs personnes construisaient en parallèle, ou si une recette formelle par un tiers était exigée. Ce n'est pas le cas aujourd'hui ; ne l'ajoutez pas par habitude.

## La règle de transport

**On n'édite jamais directement en production.** Une correction faite à chaud en production sera écrasée au prochain import, et vous perdrez la trace de ce qui a réellement changé. Le cycle est toujours : corriger en développement → évaluer → exporter → importer → republier.

## Git comme référence du comportement

C'est le gain de maintenabilité le plus concret de cette architecture, et il mérite une discipline explicite.

Les Instructions et les cinq Skills sont **du texte**. Ils peuvent donc vivre dans ce dépôt, être relus en diff, et porter un historique. Ce que la configuration d'un agent ne permet pas de voir — « qu'est-ce qui a changé, quand, et pourquoi ? » — le dépôt le donne.

**Discipline à tenir :**

1. Toute modification d'une Instruction ou d'un Skill se fait **d'abord ici**, dans `04_01` ou `05_0x`.
2. Le texte modifié est **ensuite** collé ou téléversé dans Copilot Studio.
3. Le commit décrit le motif : `Skill 4 : ajout du synonyme "enseigne" (observé 12 fois en septembre)`.

Ainsi, `04_01` et `05_0x` ne sont pas de la documentation qui se périme : ce sont **les sources** du comportement de l'agent, et le produit en est le déploiement. Faites l'inverse — modifier dans le produit puis « penser à mettre à jour le dépôt » — et vous retrouverez en trois mois la situation que ce projet cherchait à sortir : un état déployé que personne ne peut prouver.

## Sauvegarde des Skills

Copilot Studio permet d'**exporter un Skill** en Markdown. Faites-le après chaque modification et conservez le fichier dans le dépôt : c'est votre preuve de l'état réellement déployé, indépendante de toute mémoire humaine.

## Rythme d'entretien

| Fréquence | Action |
|---|---|
| À chaque modification | Modifier le dépôt, puis le produit ; commit avec le motif |
| Mensuelle | Suite d'évaluation complète (voir `06_03`) ; revue des termes non trouvés (voir `08_01`) |
| Trimestrielle | Relire `01_02` : les décisions d'architecture tiennent-elles toujours ? |
| À chaque évolution de la liste | Vérifier que les colonnes citées en `03_01` sont inchangées ; si non, corriger les Skills concernés et rejouer les tests |

La dernière ligne est celle qu'on oublie : une colonne renommée dans SharePoint ne casse rien visiblement, mais dégrade silencieusement les réponses. C'est exactement le type de défaut que ce projet s'attache à ne plus laisser passer.

## Critères de fin d'étape

- [ ] L'agent appartient à une solution.
- [ ] Le chemin Développement → Production est établi et testé une fois.
- [ ] Les cinq Skills sont exportés et conservés dans le dépôt.
- [ ] La règle « on modifie le dépôt d'abord » est comprise et acceptée.
