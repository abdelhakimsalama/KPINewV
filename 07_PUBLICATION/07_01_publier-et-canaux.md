# 07.01 — Publier l'agent et le mettre à disposition

## Objectif du fichier

- **À quoi sert ce fichier** : publier l'agent et le rendre accessible aux utilisateurs, avec la bonne authentification.
- **Étape du développement** : étape 07, mise en service. Elle exige que l'étape 06 soit passée.
- **Ce que vous faites dans Copilot Studio** : vous publiez, vous configurez le canal Teams, vous partagez à un groupe pilote.
- **Résultat attendu avant de passer à l'étape suivante** : un utilisateur pilote, qui n'est pas vous, obtient une réponse correcte depuis Teams.

---

## Avant de publier : trois vérifications

1. **La fiche de décision de `06_03` conclut PUBLIABLE.** Ce n'est pas une formalité : publier un agent qui invente est pire que ne pas publier d'agent.
2. **Aucun composant n'a été ajouté** en dehors de l'architecture prévue : une source de Knowledge, cinq Skills, zéro outil.
3. **Memory est toujours sur OFF.**

## Publier

`En haut à droite du concepteur > Publish.`

La publication prend un instant. Elle rend disponible la version en cours **sur les canaux configurés** ; tant que vous ne publiez pas, vos modifications ne concernent que l'onglet Preview.

> **À retenir pour la suite du projet :** modifier une Instruction ou un Skill ne change **rien** pour les utilisateurs tant que vous n'avez pas republié. C'est une protection : vous pouvez travailler et tester sans impacter la production.

## Le canal : Microsoft Teams

C'est le canal cible du projet, là où se trouvent les utilisateurs du dictionnaire.

1. `Onglet Channels (ou Publish) > Microsoft Teams.`
2. Activez le canal et suivez la procédure de mise à disposition.
3. Selon la politique de votre organisation, la mise à disposition à l'échelle de l'entreprise peut demander une **validation par un administrateur**. Anticipez ce délai : c'est le principal point de blocage calendaire de cette étape. **[À VÉRIFIER]**

**Ce que vous ne configurez pas :** aucun autre canal en phase pilote. Un agent publié sur un canal public sans authentification exposerait le contenu du dictionnaire à des utilisateurs non authentifiés — et ferait tomber la protection décrite ci-dessous.

## Authentification et accès aux données : le point important

L'agent lit `KPIDictionary` **avec les droits SharePoint de l'utilisateur qui pose la question** **[OFFICIEL]**. Cette phrase porte toute la sécurité du dispositif :

- Un utilisateur sans accès à la liste n'obtient rien de la liste. Vous n'avez **aucune** règle d'accès à écrire dans l'agent.
- Réciproquement, l'agent **n'ajoute aucune protection** : quiconque a accès à la liste dans SharePoint y a accès via l'agent.
- Les permissions se gèrent donc **dans SharePoint**, pas dans Copilot Studio. Si le périmètre d'accès doit changer, il change sur la liste.

**Ce que l'agent ne protège pas :** les Instructions ne sont pas une frontière de sécurité. Une règle qui dit « ne divulgue pas l'URL de la liste » réduit fortement le risque, elle ne le supprime pas. La vraie frontière est la permission SharePoint.

## Partage à un groupe pilote

Partagez d'abord avec **cinq à dix utilisateurs représentatifs** — idéalement plusieurs personas différents, et au moins un utilisateur francophone et un anglophone.

`Bouton Share > ajouter les personnes ou le groupe de sécurité.`

**Ce que vous leur demandez explicitement :**

- de poser leurs **vraies** questions, avec leurs **propres** mots ;
- de signaler toute réponse qui semble inventée, tout chiffre, toute liste présentée comme complète ;
- d'utiliser le pouce vers le haut ou vers le bas dans Teams — ces réactions remontent dans l'onglet Monitor (étape 08).

Le vocabulaire réel qu'ils emploieront est la matière première de l'évolution du Skill 4 : c'est là que vous verrez quels synonymes ajouter, sur des usages observés plutôt que supposés.

## Vérification

1. Demandez à un utilisateur pilote — **pas vous** — d'ouvrir l'agent dans Teams.
2. Il valide la connexion SharePoint au premier usage : c'est attendu.
3. Il pose : `Que signifie "Plant: Plant" ?`
4. Il doit obtenir la définition officielle.

Le fait que ce soit **un autre utilisateur** est essentiel : c'est le seul moyen de valider la chaîne d'authentification. Un agent qui fonctionne pour son créateur et échoue pour tous les autres est un grand classique, et la cause est presque toujours une connexion validée par vous seul.

## Critères de fin d'étape

- [ ] L'agent est publié.
- [ ] Le canal Teams est configuré et accessible.
- [ ] **Un autre utilisateur que moi** a obtenu une réponse correcte.
- [ ] Le groupe pilote est constitué et sait quoi signaler.
