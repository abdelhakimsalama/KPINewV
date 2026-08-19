# 10.01 — Limites : ce qui est confirmé, ce qui reste à mesurer

## Objectif du fichier

- **À quoi sert ce fichier** : distinguer rigoureusement ce que l'architecture **ne fait pas** (prouvé par des tests) de ce qui **reste à mesurer**, et servir de registre où l'on inscrit une limitation seulement quand elle est établie.
- **Étape du développement** : étape 10, lucidité. À remplir pendant l'étape 06, à présenter au métier avant la bascule de `07_02`.
- **Ce que vous faites dans Copilot Studio à partir de ce fichier** : rien. C'est le registre de vérité du projet.
- **Résultat attendu** : aucune capacité n'est déclarée absente sans preuve, et aucune n'est promise sans mesure.

---

## La règle de ce registre

> **Rien n'entre ici par hypothèse.** Une capacité n'est inscrite comme limitation qu'après avoir été testée avec des valeurs de référence, avoir échoué **de façon reproductible** (moins de 2 essais réussis sur 3), et avoir résisté aux ajustements de règle et de Skill.

C'est la contrepartie exacte du principe de non-disqualification de `06_01` : on ne retire rien du périmètre sans mesure — et symétriquement, on n'annonce rien aux utilisateurs sans mesure non plus.

---

## Ce que la plateforme prend nativement en charge

Établi par la documentation, à confirmer par vos tests dans votre environnement.

| Capacité | Statut documentaire | Vérifié chez vous ? |
|---|---|---|
| Recherche en langage naturel avec compréhension sémantique | **[OFFICIEL, préversion]** | à remplir |
| Requêtes analytiques et d'agrégation : décomptes, filtres, synthèses, calculs simples | **[OFFICIEL, préversion]** | à remplir |
| Questions de type « combien de… » | **[OFFICIEL, préversion]** | à remplir |
| Lecture temps réel de la liste | **[OFFICIEL]** | à remplir |
| Trimmage par les permissions SharePoint de l'utilisateur | **[OFFICIEL]** | à remplir |

**Deux réserves documentées à garder en tête pendant les mesures :**

1. La fonctionnalité est en **préversion** : le comportement peut évoluer, y compris en votre défaveur. D'où la campagne mensuelle de `06_03`.
2. Les questions exigeant d'analyser **la totalité** d'une grande liste peuvent être limitées en débit ou très lentes **[OFFICIEL]**. Ce sont les cas sentinelles C3 et D3.

---

## Registre des limitations confirmées

**Ce tableau est vide au démarrage du projet. C'est volontaire.** Il se remplit à l'étape 06, uniquement avec ce qui a été mesuré.

| Capacité testée | Cas | Oracle | Résultat mesuré | Essais réussis | Ajustements tentés | Verdict | Date |
|---|---|---|---|---|---|---|---|
| *(à remplir à l'étape 06)* | | | | | | | |

**Rappel du barème** (`06_03`) : 3/3 = fiable · 2/3 = à surveiller · < 2/3 après ajustements = non fiable, et **seulement alors** la ligne devient une limitation à annoncer.

**Ce qu'une ligne doit contenir pour être recevable :** la question exacte, la valeur de référence, ce que l'agent a répondu à chaque essai, ce que vous avez tenté pour corriger (règle, Skill, modèle), et la date. Une limitation sans ces éléments n'est pas une limitation, c'est une impression.

---

## Ce qui a été mesuré côté ancien agent, et qui sert d'oracle

Ces valeurs viennent du runtime de l'ancien moteur. Elles ne décrivent pas ce que le nouvel agent **doit** faire : elles décrivent la réalité des données, et permettent de noter objectivement.

Elles sont listées en tête de `06_02`. Deux méritent une attention particulière :

- **192 renommages distincts**, et non 202. L'ancien agent annonçait 202 — un chiffre faux, qu'aucun utilisateur ne pouvait détecter. Si le nouvel agent trouve 192, c'est une amélioration mesurable ; s'il trouve 202, il reproduit l'erreur d'un comptage de lignes au lieu de valeurs distinctes, et c'est corrigeable dans le Skill.
- **0 requête** couvrant `gross sales` + `shop` + `product category`. Un cas d'intersection vide est le meilleur test d'honnêteté qui soit : un agent qui « trouve » quelque chose ici invente.

---

## Les limites qui ne dépendent pas de l'architecture

Elles sont dans les données. Aucun agent ne les corrigera, et elles ne relèvent pas du registre ci-dessus.

| Limite | Portée |
|---|---|
| 119 lignes sans définition anglaise, 616 sans définition française | L'agent dira « non documenté » — c'est le comportement correct |
| Un même champ peut porter plusieurs définitions officielles | L'agent les montre toutes, sans en élire une |
| Un même champ peut porter plusieurs libellés français officiels | Aucune règle canonique n'existe ; le sujet reste ouvert côté métier |
| Un libellé français peut recouvrir deux champs anglais distincts | L'agent doit montrer les deux — **meilleur** que l'ancien comportement, qui n'avertissait pas |
| Des définitions génériques partagées par de nombreux champs | Formellement présentes, faiblement informatives |
| Écart 194 anciens noms distincts / 192 renommages | Question de définition du « renommage », à trancher avec le métier avant de noter C1 |

---

## Les défauts anciens qui disparaissent

L'équilibre n'est pas à sens unique. Ces défauts ouverts de l'ancienne architecture n'ont plus lieu d'être :

| Ancien défaut | Statut |
|---|---|
| Définitions non transmises en correspondance partielle | **Disparu** — plus de projection à deux niveaux |
| `totalPairs` annonçait 202 au lieu de 192 | **À vérifier, et corrigeable** — c'est le cas C1 |
| Plafond de 5 000 éléments franchi sans signalement | **Disparu** — plus de lecture plafonnée |
| Instructions désynchronisées du contrat du moteur | **Disparu** — plus de contrat à synchroniser |
| Budget d'instructions saturé (7 996 / 8 000) | **Disparu** — les procédures vivent dans les Skills |
| Description d'outil saturée (1 022 / 1 024) | **Disparu** — plus d'outil |
| Libellé français recouvrant deux champs sans aucun signal | **Traité** — la règle « ne jamais choisir » impose de montrer les deux |
| État déployé non prouvable, registre divergent du runtime | **Fortement réduit** — Instructions et Skills sont du texte versionné dans Git |

---

## Ce que le métier doit valider, et quand

**Avant la bascule**, et seulement à partir du registre rempli. La formulation à faire valider dépend de ce que les mesures auront montré :

- **Si les capacités analytiques sont fiables** : *« L'assistant répond aux questions de décompte et de croisement à partir des données du dictionnaire, et indique toujours ce qu'il a compté. »*
- **Si certaines sont à surveiller** : ajouter la liste nominative des cas concernés et la réserve associée.
- **Si certaines sont non fiables** : *« Pour les questions suivantes — [liste], l'assistant ne fournit pas de résultat fiable ; la liste `KPIDictionary` fait foi. »*

**Ne faites pas signer une limitation que vous n'avez pas mesurée.** C'est la raison d'être de ce fichier.

## Critères de fin d'étape

- [ ] Le registre des limitations confirmées est rempli à partir des mesures de l'étape 06 — ou reste vide si rien n'a échoué.
- [ ] Chaque ligne inscrite porte sa question, son oracle, ses essais et ses tentatives de correction.
- [ ] Les limites liées aux données sont distinguées de celles liées à l'architecture.
- [ ] La formulation présentée au métier correspond à ce qui a été **mesuré**.
