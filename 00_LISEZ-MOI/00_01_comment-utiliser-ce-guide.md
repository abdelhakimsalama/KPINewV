# 00.01 — Comment utiliser ce guide

## Objectif du fichier

- **À quoi sert ce fichier** : expliquer comment lire et exécuter ce dépôt comme une procédure de développement, du début à la fin.
- **Étape du développement** : étape 00, avant toute action dans Copilot Studio.
- **Ce que vous faites dans Copilot Studio à partir de ce fichier** : rien encore. Vous lisez, vous vérifiez que vous avez les accès, vous commencez ensuite par le dossier `01_`.
- **Résultat attendu avant de passer à l'étape suivante** : vous savez dans quel ordre avancer et à quoi ressemble l'agent final.

---

## Le principe de ce dépôt

Chaque dossier est une **étape**, numérotée dans l'ordre d'exécution. Chaque fichier est une **tâche** de cette étape. Vous lisez les dossiers dans l'ordre `00 → 10`, et à l'intérieur d'un dossier vous lisez les fichiers dans l'ordre `01 → 0n`. Vous n'avez jamais besoin de deviner l'ordre ni de chercher dans plusieurs fichiers pour une même tâche.

Chaque fichier suit toujours la même forme :

1. **Objectif du fichier** — les quatre points ci-dessus.
2. **Ce que vous faites** — chemin exact dans l'interface, paramètres, valeurs.
3. **Contenu à copier** — quand du texte doit être collé dans Copilot Studio, il est donné en entier, prêt à l'emploi, dans un bloc de code.
4. **Vérification** — comment prouver que ça marche.
5. **Critères de fin d'étape** — la case à cocher qui autorise à passer au fichier suivant.

## L'ordre des étapes

| Dossier | Étape | Ce que vous obtenez à la fin |
|---|---|---|
| `00_LISEZ-MOI` | Cadrage | Vous savez ce que vous construisez |
| `01_PREREQUIS_ET_DECISIONS` | Prérequis | Accès, licences et décisions d'architecture tracées |
| `02_CREATION_DE_LAGENT` | Création | Un agent vide qui répond, avec le bon modèle |
| `03_KNOWLEDGE_SHAREPOINT` | Données | L'agent lit la liste `KPIDictionary` en direct |
| `04_INSTRUCTIONS` | Comportement permanent | L'agent respecte les règles globales |
| `05_SKILLS` | Comportements situationnels | Les 5 Skills métier, un par cas d'usage |
| `06_EVALUATION` | Qualité | Une suite de tests qui passe, et qui protège des régressions |
| `07_PUBLICATION` | Mise en service | L'agent publié dans Teams |
| `08_MONITORING_ET_COUTS` | Exploitation | Vous voyez ce que fait l'agent et ce qu'il coûte |
| `09_ALM_ET_MAINTENANCE` | Durée de vie | Vous savez modifier une règle sans tout casser |
| `10_BACKLOG` | Lucidité | Ce que cette architecture ne fait pas, et quoi faire alors |

## Règle de conduite du projet

> **On part toujours du plus simple et du plus natif.** Un composant supplémentaire ne s'ajoute que si un besoin fonctionnel réel ne peut pas être couvert autrement, et cette justification s'écrit dans `01_02_journal-des-decisions-darchitecture.md`.

Concrètement, pour ce projet, cela veut dire **trois composants et rien d'autre** : des Instructions, une source de Knowledge, cinq Skills. Pas de Power Automate, pas de code, pas d'outil, pas d'agent connecté, pas de Memory.

## Langue

Les fichiers de ce dépôt sont en **français** : ils s'adressent à vous. Tout ce qui se colle **dans** Copilot Studio — instructions, descriptions, Skills — est en **anglais**, parce que c'est la langue dans laquelle l'agent raisonne le mieux et parce que les règles existantes du projet le sont déjà. L'agent, lui, répond à l'utilisateur final en français comme en anglais.

## Critères de fin d'étape

- [ ] J'ai lu `00_02` (l'architecture cible) et `00_03` (le glossaire).
- [ ] Je comprends que l'agent final n'a **aucun** outil ni flux.
- [ ] Je passe au dossier `01_PREREQUIS_ET_DECISIONS`.
