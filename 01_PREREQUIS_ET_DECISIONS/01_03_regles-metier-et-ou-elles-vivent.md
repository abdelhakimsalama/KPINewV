# 01.03 — Les règles métier et où chacune vit

## Objectif du fichier

- **À quoi sert ce fichier** : répartir les 14 règles non négociables du projet entre Instructions et Skills, et dire honnêtement lesquelles changent de nature dans cette architecture.
- **Étape du développement** : étape 01, décisions. C'est la table de correspondance qui pilote les étapes 04 et 05.
- **Ce que vous faites dans Copilot Studio à partir de ce fichier** : rien encore, mais ne rédigez ni les Instructions (étape 04) ni les Skills (étape 05) sans l'avoir sous les yeux.
- **Résultat attendu avant de passer à l'étape suivante** : vous savez, pour chaque règle, dans quel fichier elle sera écrite.

---

## La règle d'arbitrage

Une règle va dans les **Instructions** si elle est vraie dans **100 %** des conversations. Sinon elle va dans un **Skill**. Si elle décrit une donnée et non un comportement, elle n'est écrite nulle part : elle est déjà dans la liste.

## Répartition des 14 règles

| # | Règle non négociable | Où elle vit | Forme dans cette architecture |
|---|---|---|---|
| 1 | **Source unique** — la liste `KPIDictionary`, jamais autre chose | Instructions | Inchangée |
| 2 | **Zéro invention** — n'affirmer que ce que la source montre | Instructions | Inchangée. **C'est la règle la plus importante du projet** |
| 3 | **Verbatim** — citer les valeurs officielles exactement, coquilles et préfixes compris | Instructions | Inchangée |
| 4 | **Ne jamais choisir à la place de l'utilisateur** | Instructions + Skill 04 | Le principe est permanent ; le protocole d'ambiguïté est situationnel |
| 5 | **Ne jamais compter soi-même** | Instructions | **REFORMULÉE → interdiction de compter tout court** (voir ci-dessous) |
| 6 | **Persona prouvé, jamais inféré** | Instructions + Skill 05 | Le principe est permanent ; le détail des six valeurs et la conduite à tenir sont dans le Skill |
| 7 | **Absence honnête** — dire « non trouvé » et ce qui a été cherché | Instructions | Inchangée |
| 8 | **Troncature toujours annoncée avec le total réel** | Instructions | **REFORMULÉE → avertissement permanent de non-exhaustivité** (voir ci-dessous) |
| 9 | **`new` n'est pas un nom de champ** | Instructions + Skill 02 | Rappel court en Instructions, traitement détaillé dans le Skill mapping |
| 10 | **Synonymes : table figée, l'agent n'en crée pas** | Skill 04 | La table devient un tableau Markdown dans le Skill |
| 11 | **Langue de réponse = langue du message ; traduire pour chercher oui, pour citer non** | Instructions | Inchangée |
| 12 | **Signaler en tête toute correspondance obtenue via l'ancien nom MyBI** | Instructions + Skill 02 | Inchangée |
| 13 | **Pas de tableaux Markdown** dans les réponses | Instructions | Inchangée |
| 14 | **Hors périmètre annoncé comme tel** — pas de web, pas de temps réel | Instructions | Inchangée |

## Les deux règles qui changent de nature — et pourquoi c'est un progrès

### Règle 5 : de « ne compte pas toi-même » à « ne compte pas »

**Avant**, un moteur externe fournissait les décomptes (`typeCounts`) et la règle disait à l'agent de ne jamais les recalculer. **Maintenant**, il n'y a plus de fournisseur de décompte fiable. La règle devient donc : **l'agent ne donne aucun chiffre, aucun total, et n'emploie ni « tous » ni « la liste complète »**.

Ce n'est pas un affaiblissement de la véracité, c'est l'inverse. L'agent actuel annonce « 202 champs renommés » — un chiffre que le projet sait faux (le nombre réel de renommages distincts est 192). Le nouvel agent ne produira plus ce genre d'erreur, parce qu'il n'a plus le droit d'affirmer un nombre.

### Règle 8 : de « annonce la troncature » à « annonce que ce n'est jamais garanti complet »

**Avant**, le moteur signalait explicitement une troncature et donnait le total réel. **Maintenant**, une recherche rend un sous-ensemble pertinent sans indicateur de complétude. La règle devient : **toute réponse de type liste porte la mention que d'autres entrées peuvent exister**.

L'utilisateur est ainsi averti en permanence, au lieu de l'être seulement quand un indicateur technique se déclenchait.

## Les règles qui n'ont plus d'objet

| Ancienne règle | Statut |
|---|---|
| Cascade à 7 étages, `matchLevel`, `matchMode` | **Supprimée** — c'était le contrat d'un moteur qui n'existe plus |
| Lecture des clés `synonymApplied`, `conceptMatches`, `partialWithout`, `evidenceCount` | **Supprimée** — même motif |
| Mode `intersect` avec preuves par critère | **Remplacée** — le croisement multi-critères devient une réponse explicitement non garantie (Skill 03) |
| Mode `renamed` global (« toutes les paires ») | **Remplacée** — l'agent montre des renommages trouvés, jamais la liste entière (Skill 02) |
| Plafonds de sortie (40 / 60 / 200 / 250 lignes) | **Sans objet** |

**Bénéfice de maintenance :** la désynchronisation permanente entre les instructions et le contrat d'un moteur externe — un défaut ouvert du projet actuel — disparaît, puisqu'il n'y a plus de contrat à synchroniser.

## Critères de fin d'étape

- [ ] Je sais dire pour chacune des 14 règles où elle sera écrite.
- [ ] J'ai validé la reformulation des règles 5 et 8.
- [ ] J'ai noté quelles anciennes règles disparaissent, et pourquoi.
- [ ] Je passe au dossier `02_CREATION_DE_LAGENT`.
