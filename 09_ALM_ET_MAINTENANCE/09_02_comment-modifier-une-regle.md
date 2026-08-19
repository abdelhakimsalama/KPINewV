# 09.02 — Comment modifier une règle sans rien casser

## Objectif du fichier

- **À quoi sert ce fichier** : donner la procédure à suivre pour toute évolution du comportement de l'agent, une fois le projet en exploitation.
- **Étape du développement** : étape 09, durée de vie. C'est le fichier que vous rouvrirez le plus souvent.
- **Ce que vous faites dans Copilot Studio** : vous appliquez la modification au bon endroit, puis vous vérifiez.
- **Résultat attendu** : une modification appliquée, testée, publiée et tracée — sans effet de bord.

---

## Étape 1 : trouver le bon endroit

C'est 90 % du travail. Une modification placée au mauvais endroit fonctionne un temps, puis produit des effets de bord incompréhensibles.

| Ce que vous voulez changer | Où | Fichier |
|---|---|---|
| Une règle vraie dans **toutes** les conversations | Instructions | `04_01` |
| La façon de présenter une définition ou une formule | Skill 1 | `05_01` |
| La façon de présenter un renommage MyBI → SAC | Skill 2 | `05_02` |
| La façon de lister des requêtes ou de traiter le multi-critères | Skill 3 | `05_03` |
| Un synonyme métier, ou la conduite face à une ambiguïté | Skill 4 | `05_04` |
| Une règle sur les personas | Skill 5 | `05_05` |
| Une donnée métier — définition, formule, libellé, persona | **La liste SharePoint** | Ni Instructions ni Skill |

**Les deux erreurs à ne pas commettre :**

- **Ajouter une procédure dans les Instructions** parce que c'est plus rapide. Ce texte est chargé à **chaque** tour, pour **toutes** les questions. C'est exactement le mécanisme qui a mené le bloc d'instructions de l'ancien agent à la saturation.
- **Corriger une donnée dans un Skill.** Si une définition est fausse, elle se corrige dans `KPIDictionary`. Un Skill qui contient une donnée crée une seconde vérité, qui divergera de la première.

## Étape 2 : appliquer, dans cet ordre

1. **Modifiez le fichier de ce dépôt** (`04_01` ou `05_0x`).
2. **Reportez dans Copilot Studio** : collez les Instructions, ou téléversez le `SKILL.md`.
3. **Ne publiez pas encore.**

L'ordre compte : le dépôt d'abord, le produit ensuite. C'est ce qui garantit que le dépôt reste la référence et non un reflet approximatif.

## Étape 3 : vérifier

| Nature de la modification | Ce que vous rejouez |
|---|---|
| Une règle des Instructions | Les familles B, C et D, plus les cas liés à la règle touchée |
| Le contenu d'un Skill | Les cas de ce Skill, plus B, C et D |
| **Une description de Skill** | **La famille H en entier** — une description modifiée déplace les frontières entre Skills |
| La table de vocabulaire | La famille F en entier, plus E1 et D5 |
| **Le modèle** | **La suite complète, deux fois** |

Les deux lignes en gras sont celles qui produisent des effets de bord invisibles. Une description élargie peut faire capter à un Skill les questions d'un autre, sans qu'aucune réponse ne paraisse fausse — jusqu'au jour où la mise en forme dérive.

## Étape 4 : publier et tracer

1. **Publiez** — sans publication, les utilisateurs ne voient rien.
2. **Commitez** dans ce dépôt, avec un message qui dit **pourquoi** :

```
Skill 4 : ajout du synonyme "enseigne" -> Plant: Plant
Motif : 12 recherches infructueuses en septembre (relevé Monitor)
Tests : famille F et E1 rejouées, 100 %
```

Le motif compte plus que le contenu du changement : dans un an, le diff dira **quoi**, seul le message dira **pourquoi**.

## Trois situations fréquentes, traitées

**« L'agent se trompe sur un cas précis. »** Vérifiez d'abord si la donnée existe dans `KPIDictionary`. Dans la majorité des cas, ce n'est pas une règle à corriger mais une donnée absente ou ambiguë. Corrigez la liste, pas l'agent.

**« L'agent donne un décompte faux. »** Regardez **ce qu'il a compté** avant de toucher à une règle : compter des lignes au lieu de valeurs distinctes est l'erreur n° 1, et c'est exactement celle que faisait l'ancien moteur (202 au lieu de 192). La correction est une précision de définition dans le Skill concerné, pas une interdiction de compter.

**« L'agent respecte la règle 9 fois sur 10. »** C'est la variabilité normale d'un comportement probabiliste, pas un bug ponctuel. N'ajoutez surtout pas une règle supplémentaire : empiler dilue au lieu de stabiliser. Deux leviers, dans l'ordre — rendre la règle existante plus courte et plus explicite, puis changer de modèle et re-mesurer.

**« Faut-il afficher telle information dans la réponse ? »** Posez la question d'arbitrage de la règle 7 : *l'utilisateur a-t-il demandé cette information, ou est-ce la façon dont l'agent l'a trouvée ?* Le champ qui répond à un critère de recherche est du résultat, il s'affiche. La colonne sur laquelle la recherche a porté est de la méthode, elle ne s'affiche pas. Et si l'utilisateur demande explicitement une justification, les entrées du dictionnaire qui l'établissent s'affichent aussi (règle 8) — c'est de la preuve, pas de la méthode. Ces deux questions tranchent seules la quasi-totalité des cas, sans qu'il faille ajouter une règle.

**« Les utilisateurs demandent une fonction qui n'existe pas. »** Ne l'improvisez pas dans un Skill. Allez à `10_02` : les extensions possibles y sont décrites avec leur coût en complexité. Puis décidez consciemment — c'est-à-dire en écrivant la décision dans `01_02`.

## Ce qui doit rester interdit

Quel que soit le besoin exprimé, trois choses ne se négocient pas, sauf à réviser explicitement `01_02` :

1. **Ajouter une deuxième source de Knowledge** — l'origine d'une réponse deviendrait indécidable.
2. **Autoriser l'agent à estimer un chiffre** — un nombre vient des données ou n'est pas donné. Compter depuis la liste est permis ; extrapoler ne l'est jamais.
3. **Laisser l'agent choisir seul entre deux candidats** — c'est se tromper une fois sur deux avec assurance.
4. **Faire raconter à l'agent sa méthode interne dans la réponse** — colonnes, filtres, étapes. Cette information existe déjà dans la trace d'activité ; la répéter alourdit chaque échange sans rien apporter à l'utilisateur. *À ne pas confondre avec la justification métier* : si l'utilisateur demande sur quelle base une réponse a été donnée, citer les entrées du dictionnaire qui l'établissent est attendu (règle 8).

Si l'une de ces trois interdictions devient réellement bloquante pour le métier, ce n'est plus une modification : c'est un changement d'architecture. Il se traite dans `10_02`.

## Critères de fin d'étape

- [ ] Je sais placer une modification au bon endroit.
- [ ] Je connais l'ordre : dépôt, puis produit, puis tests, puis publication, puis commit.
- [ ] Je sais qu'une description modifiée impose de rejouer toute la famille H.
- [ ] Je passe au dossier `10_BACKLOG`.
