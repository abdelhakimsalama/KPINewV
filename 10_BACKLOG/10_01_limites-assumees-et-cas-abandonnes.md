# 10.01 — Limites assumées et cas abandonnés

## Objectif du fichier

- **À quoi sert ce fichier** : dire noir sur blanc ce que cette architecture ne fait pas, pour que personne ne le découvre en production et que le métier puisse arbitrer en connaissance de cause.
- **Étape du développement** : étape 10, lucidité. À lire avant la bascule de `07_02`, et à présenter au métier.
- **Ce que vous faites dans Copilot Studio à partir de ce fichier** : rien. C'est le document de vérité du projet.
- **Résultat attendu** : les limites sont connues, acceptées par écrit, et personne ne les prend pour des bugs.

---

## Les trois limites structurelles

### 1. L'agent ne compte pas

**Ce qu'il ne fait plus :** répondre « il y a 192 champs renommés », « cette requête contient 184 champs », « 17 requêtes pour le persona Supply ».

**Pourquoi :** une recherche dans une source de Knowledge rend un sous-ensemble pertinent. Aucun composant de cette architecture ne parcourt l'intégralité des lignes pour en établir un total.

**Ce qu'il fait à la place :** il montre ce qu'il a trouvé, dit qu'il ne peut pas garantir un décompte, et renvoie vers la liste `KPIDictionary` pour un chiffre définitif.

**À dire au métier :** l'ancien agent annonçait « 202 champs renommés ». Le chiffre était **faux** — le nombre réel de renommages distincts est 192 — et rien ne permettait à l'utilisateur de s'en apercevoir. On remplace une réponse fausse et invisible par une réponse honnête.

### 2. L'agent ne garantit pas l'exhaustivité

**Ce qu'il ne fait plus :** affirmer « voici toutes les requêtes qui contiennent ce champ ».

**Pourquoi :** même raison. Rien ne garantit que la recherche a rendu la totalité des lignes correspondantes.

**Ce qu'il fait à la place :** il présente ce qu'il a trouvé et signale systématiquement que d'autres entrées peuvent exister.

**Effet secondaire positif :** l'avertissement devient permanent, là où l'ancien agent ne signalait la troncature que lorsqu'un indicateur technique se déclenchait.

### 3. L'agent ne prouve pas un croisement multi-critères

**Ce qu'il ne fait plus :** établir « exactement 2 requêtes contiennent à la fois duty free et duty paid », avec les lignes de preuve.

**Pourquoi :** il n'y a pas de calcul d'intersection.

**Ce qu'il fait à la place :** il montre les requêtes pour lesquelles la source démontre tous les critères, avec les champs cités en preuve, **puis** la couverture par critère, explicitement marquée comme partielle. Et il dit que la couverture complète n'est pas garantie.

**Nuance importante :** la réponse reste utile — souvent même exacte. Ce qui disparaît, c'est la **garantie**, et l'agent le dit au lieu de le taire.

## Les cas de test retirés du périmètre

Ces cas validaient l'ancien moteur. Ils ne sont pas des régressions à corriger : ils sont **hors périmètre par décision DA-04**, et n'ont plus d'objet.

| Ancien cas | Statut | Remplacé par |
|---|---|---|
| `Stock Value` → exactement 5 résultats, 3 Primary KPI + 2 Derived KPI | Retiré | A6 : le contenu est juste, le décompte n'est plus affirmé |
| `P&L` → 98/98, non tronqué | Retiré | C5 : liste avec mention de non-exhaustivité |
| `duty free;duty paid` → intersection = 2 | Retiré | C5 et la couverture partielle du Skill 3 |
| `sales;stock` → 18 requêtes, 798 preuves, troncature signalée | Retiré | Même chose |
| `*` mode `renamed` → 202 paires | Retiré | C1 et C6 : refus du décompte |
| Rognage de ponctuation, terme vide, ponctuation non latine | Retiré | Comportements internes d'un moteur qui n'existe plus |
| Plafond de 5 000 éléments signalé | Retiré | Sans objet : plus de lecture plafonnée |
| Restitution de `matchLevel`, `matchMode`, `typeCounts`, `truncated` | Retiré | Plus de contrat de moteur à restituer |

## Les défauts anciens qui disparaissent

L'équilibre n'est pas à sens unique. Six défauts ouverts de l'ancienne architecture n'ont plus lieu d'être :

| Ancien défaut | Statut |
|---|---|
| Définitions non transmises en correspondance partielle | **Disparu** — plus de projection à deux niveaux |
| `totalPairs` annonçait 202 au lieu de 192 | **Disparu** — l'agent ne compte plus |
| Plafond de 5 000 éléments franchi sans signalement | **Disparu** — plus de lecture plafonnée |
| Instructions désynchronisées du contrat du moteur | **Disparu** — plus de contrat à synchroniser |
| Budget d'instructions saturé (7 996 / 8 000) | **Disparu** — les procédures vivent dans les Skills |
| Description d'outil saturée (1 022 / 1 024) | **Disparu** — plus d'outil |
| État déployé non prouvable, registre divergent du runtime | **Fortement réduit** — Instructions et Skills sont du texte versionné dans Git |

## Les limites qui restent, héritées des données

Elles ne dépendent pas de l'architecture : elles sont dans la liste, et aucun agent ne les corrigera.

| Limite | Portée |
|---|---|
| 119 lignes sans définition anglaise, 616 sans définition française | L'agent dira « non documenté » — c'est le comportement correct |
| Un même champ peut porter plusieurs définitions officielles | L'agent les montre toutes, sans en élire une |
| Un même champ peut porter plusieurs libellés français officiels | Aucune règle canonique n'existe ; le sujet reste ouvert côté métier |
| Un libellé français peut recouvrir deux champs anglais distincts | L'agent montre les deux ; c'est mieux que l'ancien comportement, qui n'avertissait pas |
| Des définitions génériques partagées par de nombreux champs | Formellement présentes, faiblement informatives |

**La quatrième ligne mérite d'être signalée au métier comme une amélioration :** l'ancien moteur renvoyait les deux champs comme une correspondance unique, **sans aucun signal**. Le nouvel agent, qui doit exposer tous les candidats, traite mieux ce cas.

## Ce que le métier doit signer

Avant la bascule, faites acter explicitement les trois limites structurelles. La formulation suivante est utilisable telle quelle :

> *L'assistant ne fournit ni décompte, ni liste exhaustive, ni croisement multi-critères garanti. Il présente ce que le dictionnaire démontre et signale ce qui n'est pas garanti. Pour tout chiffre définitif, la liste `KPIDictionary` fait foi.*

## Critères de fin d'étape

- [ ] Les trois limites structurelles sont comprises.
- [ ] Les cas de test retirés ne sont plus considérés comme des régressions.
- [ ] La formulation ci-dessus est validée par le métier, par écrit.
