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

**Ce que cela coûte.** Les garanties d'exactitude qui reposaient sur du calcul disparaissent (voir DA-04). Ce coût est accepté et traité par la règle, pas par la technique.

**Ce qui rouvrirait la décision.** Une évaluation (étape 06) qui échoue de façon répétée sur des cas jugés indispensables par le métier. Les options sont préparées dans `10_02`.

## DA-02 — La liste SharePoint reste la source unique, connectée en Knowledge

**Décision.** `KPIDictionary` est branchée directement comme source de Knowledge, en connexion temps réel. Pas d'export, pas de copie, pas de fichier intermédiaire.

**Motif.** La liste doit rester la référence vivante : ce qui est modifié dans SharePoint doit être visible par l'agent sans étape de synchronisation. Une copie créerait une seconde vérité et une procédure de rafraîchissement à maintenir.

**Bénéfice de sécurité.** La lecture se fait avec les droits SharePoint de l'utilisateur : les permissions de la liste restent la frontière d'accès, et l'agent n'y ajoute rien.

## DA-03 — Aucune source de Knowledge en dehors de `KPIDictionary`

**Décision.** Une seule source, jamais deux.

**Motif.** La règle métier n°1 est « source unique ». Une deuxième source rendrait indécidable l'origine d'une réponse. Point important à connaître : dans la nouvelle expérience, **il n'existe pas de bascule « connaissances générales » à désactiver** — l'accès aux connaissances se gouverne uniquement par les sources que vous ajoutez **[OFFICIEL]**. Ne pas en ajouter d'autres est donc le principal levier de contrôle disponible, avec les Instructions.

## DA-04 — L'agent ne compte pas et ne promet jamais l'exhaustivité

**Décision.** Il est **interdit** à l'agent d'annoncer un total, de compter des lignes, ou de dire « tous », « la liste complète », « il y a N champs ». Toute réponse de type liste s'accompagne de la mention que d'autres entrées peuvent exister.

**Motif.** Une recherche dans une source de Knowledge rend un sous-ensemble pertinent ; elle ne garantit ni l'exhaustivité, ni l'absence de troncature silencieuse. La documentation Microsoft indique que les requêtes de décompte et de filtrage par valeur de colonne ne sont pas prises en charge sur les listes **[OFFICIEL]**. Faire promettre à l'agent ce que l'architecture ne garantit pas produirait des réponses fausses d'apparence officielle — le pire défaut possible selon les règles du projet.

**Conséquence assumée.** L'agent d'aujourd'hui répond « 202 champs renommés » (chiffre d'ailleurs faux, voir le défaut connu du projet). Le nouvel agent répondra : « voici les renommages que j'ai trouvés ; je ne peux pas garantir une liste complète ni en donner le nombre exact — consultez la liste `KPIDictionary` pour un décompte définitif. » **C'est un progrès de véracité, pas une régression fonctionnelle.**

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
- [ ] DA-04 en particulier est comprise : **l'agent ne comptera plus**.
- [ ] Toute modification apportée à ces décisions est écrite ici avant de construire.
