# 01.02 — Journal des décisions d'architecture

## Objectif du fichier

- **À quoi sert ce fichier** : garder la trace de **pourquoi** l'agent a cette forme, pour que personne — vous compris dans six mois — ne rajoute un composant sans savoir ce qui avait été écarté et sur quel motif.
- **Étape du développement** : étape 01, décisions. À relire avant toute évolution.
- **Ce que vous faites dans Copilot Studio à partir de ce fichier** : rien. C'est la mémoire du projet.
- **Résultat attendu avant de passer à l'étape suivante** : vous adhérez aux six décisions, ou vous les modifiez ici avant de construire.

---

## DA-01 — Architecture à trois composants : Instructions + Knowledge + Skills

**Décision.** L'agent n'a que trois composants. Aucun outil, aucun flux, aucun code.

**Motif.** L'objectif du projet est de tirer parti de la nouvelle expérience pour obtenir quelque chose de plus simple à développer, à comprendre et à maintenir. Toute couche technique supplémentaire doit être justifiée par un besoin fonctionnel qu'aucun composant natif ne couvre. Au démarrage, aucun besoin ne franchit ce seuil.

**Ce que cela coûte.** Les garanties apportées par un moteur externe — décomptes calculés, intersections prouvées — ne sont plus assurées par construction. Elles ne sont pas abandonnées pour autant : la plateforme couvre nativement une partie de ces besoins (voir DA-04), et c'est l'évaluation qui établit ce qui tient réellement.

**Ce qui rouvrirait la décision.** Une évaluation (étape 06) qui échoue de façon répétée sur des cas jugés indispensables par le métier. Les options sont préparées dans `10_02`.

## DA-02 — La liste SharePoint reste la source unique, connectée en Knowledge

**Décision.** `KPIDictionary` est branchée directement comme source de Knowledge, en connexion temps réel. Pas d'export, pas de copie, pas de fichier intermédiaire.

**Motif.** La liste doit rester la référence vivante : ce qui est modifié dans SharePoint doit être visible par l'agent sans étape de synchronisation. Une copie créerait une seconde vérité et une procédure de rafraîchissement à maintenir.

**Bénéfice de sécurité.** La lecture se fait avec les droits SharePoint de l'utilisateur : les permissions de la liste restent la frontière d'accès, et l'agent n'y ajoute rien.

## DA-03 — Aucune source de Knowledge en dehors de `KPIDictionary`

**Décision.** Une seule source, jamais deux.

**Motif.** La règle métier n°1 est « source unique ». Une deuxième source rendrait indécidable l'origine d'une réponse. Point important à connaître : dans la nouvelle expérience, **il n'existe pas de bascule « connaissances générales » à désactiver** — l'accès aux connaissances se gouverne uniquement par les sources que vous ajoutez **[OFFICIEL]**. Ne pas en ajouter d'autres est donc le principal levier de contrôle disponible, avec les Instructions.

## DA-04 — Les décomptes et agrégations restent dans le périmètre, et se valident par la mesure

**Décision.** Les questions analytiques — décomptes, filtres, agrégations, croisements de critères — **restent des besoins fonctionnels du produit**. Elles ne sont ni interdites, ni classées comme abandonnées. Leur fiabilité réelle est établie par l'évaluation de l'étape 06, avec des valeurs de référence connues.

**Motif.** Les listes SharePoint utilisées comme source de Knowledge dans la nouvelle expérience prennent en charge les **requêtes analytiques et d'agrégation** sur les données structurées de la liste, y compris les questions de type « combien » **[OFFICIEL, préversion — [Add SharePoint lists](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-sharepoint-lists)]**. Retirer ces cas d'usage par précaution reviendrait à reproduire une limitation de l'ancienne architecture dans la nouvelle, alors même que la plateforme a comblé l'écart.

**La frontière qui reste, elle, est absolue.** Un chiffre vient des données de la liste, ou il n'est pas donné. Jamais d'estimation, jamais d'extrapolation depuis un échantillon, jamais un nombre « plausible ». C'est la règle 6 des Instructions, et c'est elle qui protège l'utilisateur — pas une interdiction générale de compter.

**Ce que dit Microsoft sur la méthode.** Les bonnes pratiques de la page officielle demandent explicitement d'*« exécuter des évaluations et valider vos requêtes avant le déploiement en production »* **[OFFICIEL]**. C'est exactement la démarche de l'étape 06.

**Ce qui est connu et doit être surveillé :**

| Point | Conséquence |
|---|---|
| La fonctionnalité est en **préversion** | Le comportement peut évoluer ; rejouez la suite de tests régulièrement |
| Les questions portant sur **la totalité** d'une grande liste peuvent être limitées en débit ou très lentes **[OFFICIEL]** | Les décomptes globaux sont les cas les plus à risque : ce sont ceux que l'étape 06 mesure en priorité |
| Un modèle de langage prédit, il ne calcule pas | D'où la règle 6, et d'où la vérification par valeurs de référence plutôt que par confiance |

**Ce qui rouvrirait la décision.** Des tests réels, documentés, montrant qu'un type de question analytique n'est pas fiable. À ce moment-là — et à ce moment-là seulement — la limitation est écrite dans `10_01` avec ses preuves.

## DA-05 — La table des synonymes vit dans un Skill

**Décision.** Les 12 entrées de vocabulaire métier (`point de vente` → `Plant: Plant`, `catégorie produit` → deux cibles, etc.) sont écrites dans le Skill `business-vocabulary-and-ambiguity`.

**Motif.** Les listes SharePoint utilisées comme Knowledge **ne prennent en charge ni glossaire ni synonymes** **[OFFICIEL]** : il faut donc que la résolution vive ailleurs. Un Skill est l'endroit natif pour cela, et il apporte un gain net : la table devient modifiable en éditant un fichier Markdown, sans intervention informatique — ce qui était impossible auparavant.

**Ce que cela change.** La résolution devient interprétée par le modèle au lieu d'être une égalité stricte. Elle est donc plus souple (variantes, pluriels, accents) et moins prévisible. Les cas de test de l'étape 06 la surveillent.

## DA-06 — Memory désactivée, aucun agent connecté, pas de Microsoft IQ

**Décision.** Trois « non ».

**Motifs.** **Memory** : la règle métier interdit d'inférer un persona ; une mémoire qui retiendrait « cet utilisateur est du Supply » influencerait silencieusement les réponses suivantes. Elle est de surcroît en préversion. **Agents connectés** : un seul domaine, un seul propriétaire, un seul périmètre — rien à décomposer. **Microsoft IQ** : introduirait du contexte organisationnel non autoritaire dans un agent dont toute la valeur tient à sa source unique.

## Tableau de synthèse

| Composant disponible | Retenu ? | Motif en une ligne |
|---|---|---|
| Instructions | **Oui** | Les règles vraies à chaque tour |
| Knowledge (liste `KPIDictionary`) | **Oui** | La source unique, en direct |
| Skills (5) | **Oui** | Les procédures situationnelles |
| Sélection du modèle | **Oui** | Un choix, arbitré à l'étape 06 |
| Outils (connecteurs, MCP, workflows) | Non | Aucun besoin d'action externe : l'agent lit, il n'écrit nulle part |
| Power Automate / flux | Non | DA-01 |
| Code / bac à sable | Non | DA-01 |
| Memory | Non | DA-06 |
| Agents connectés | Non | DA-06 |
| Microsoft IQ | Non | DA-06 |
| Topics | Sans objet | N'existent pas dans la nouvelle expérience |

## Critères de fin d'étape

- [ ] Les six décisions sont lues et acceptées.
- [ ] DA-04 en particulier est comprise : **les décomptes restent au périmètre et se valident par la mesure**, et un chiffre vient toujours des données.
- [ ] Toute modification apportée à ces décisions est écrite ici avant de construire.
