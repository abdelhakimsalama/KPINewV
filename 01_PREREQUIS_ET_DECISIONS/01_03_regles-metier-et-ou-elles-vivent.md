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
| 5 | **Ne jamais compter soi-même** | Instructions | **PRÉCISÉE → un chiffre vient des données, jamais d'une estimation ; donné sans explication de méthode** (voir ci-dessous) |
| 6 | **Persona prouvé, jamais inféré** | Instructions + Skill 05 | Le principe est permanent ; le détail des six valeurs et la conduite à tenir sont dans le Skill |
| 7 | **Absence honnête** — dire « non trouvé » et ce qui a été cherché | Instructions | Inchangée |
| 8 | **Troncature toujours annoncée avec le total réel** | Instructions | **PRÉCISÉE → signaler un résultat partiel quand il l'est réellement, sans avertissement de routine** (voir ci-dessous) |
| 9 | **`new` n'est pas un nom de champ** | Instructions + Skill 02 | Rappel court en Instructions, traitement détaillé dans le Skill mapping |
| 10 | **Synonymes : table figée, l'agent n'en crée pas** | Skill 04 | La table devient un tableau Markdown dans le Skill |
| 11 | **Langue de réponse = langue du message ; traduire pour chercher oui, pour citer non** | Instructions | Inchangée |
| 12 | **Signaler en tête toute correspondance obtenue via l'ancien nom MyBI** | Instructions + Skill 02 | Inchangée |
| 13 | **Pas de tableaux Markdown** dans les réponses | Instructions | Inchangée |
| 14 | **Hors périmètre annoncé comme tel** — pas de web, pas de temps réel | Instructions | Inchangée |

## Les deux règles qui se précisent — et pourquoi ce n'est pas un renoncement

### Règle 5 : de « ne compte pas toi-même » à « un chiffre vient des données »

**Avant**, un moteur externe fournissait les décomptes et la règle interdisait à l'agent de les recalculer. **Maintenant**, la source de Knowledge prend nativement en charge les requêtes analytiques et d'agrégation sur la liste **[OFFICIEL, préversion]**. L'agent a donc le droit de répondre à « combien » — à une condition absolue : **le chiffre vient des données de la liste, jamais d'une estimation, d'une extrapolation ou d'un échantillon**.

L'intention d'origine est intégralement préservée. Ce que la règle protégeait, ce n'était pas l'absence de chiffres : c'était l'absence de **chiffres fabriqués**. C'est exactement ce que dit la nouvelle formulation, sans priver le produit d'une capacité que la plateforme offre.

### Règle 8 : de « annonce la troncature » à « dis si c'est complet ou partiel »

**Avant**, le moteur signalait explicitement une troncature et donnait le total réel. **Maintenant**, l'agent doit dire, pour chaque liste qu'il produit, si elle est complète ou partielle au vu de ce qui est réellement remonté — et le dire clairement lorsqu'il ne parvient pas à établir un chiffre de façon fiable.

Deux situations à surveiller particulièrement, documentées par Microsoft : les questions portant sur **la totalité** d'une grande liste peuvent être limitées en débit ou très lentes **[OFFICIEL]**, et un modèle de langage prédit au lieu de calculer. C'est précisément ce que l'étape 06 mesure, avec des valeurs de référence connues.

## Les règles qui n'ont plus d'objet

| Ancienne règle | Statut |
|---|---|
| Cascade à 7 étages, `matchLevel`, `matchMode` | **Supprimée** — c'était le contrat d'un moteur qui n'existe plus |
| Lecture des clés `synonymApplied`, `conceptMatches`, `partialWithout`, `evidenceCount` | **Supprimée** — même motif |
| Plafonds de sortie (40 / 60 / 200 / 250 lignes) | **Sans objet** |

En revanche, les **besoins fonctionnels** que ces mécanismes servaient restent au périmètre : le croisement multi-critères (Skill 03), la liste des renommages (Skill 02) et les décomptes sont conservés comme cas d'usage, et leur fiabilité est établie par l'étape 06. Ce qui disparaît, ce sont les mécanismes internes d'un moteur ; pas les questions que les utilisateurs posent.

**Bénéfice de maintenance :** la désynchronisation permanente entre les instructions et le contrat d'un moteur externe — un défaut ouvert du projet actuel — disparaît, puisqu'il n'y a plus de contrat à synchroniser.

## Critères de fin d'étape

- [ ] Je sais dire pour chacune des 14 règles où elle sera écrite.
- [ ] J'ai validé la reformulation des règles 5 et 8.
- [ ] J'ai noté quelles anciennes règles disparaissent, et pourquoi.
- [ ] Je passe au dossier `02_CREATION_DE_LAGENT`.
