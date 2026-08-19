# 08.01 — Surveiller l'agent : Monitor et trace d'activité

## Objectif du fichier

- **À quoi sert ce fichier** : savoir ce que fait réellement l'agent en production, et diagnostiquer un comportement à partir de preuves plutôt que d'hypothèses.
- **Étape du développement** : étape 08, exploitation. Elle commence dès le pilote de l'étape 07.
- **Ce que vous faites dans Copilot Studio** : vous prenez en main l'onglet **Monitor** et la **trace d'activité**, et vous instaurez une revue régulière.
- **Résultat attendu avant de passer à l'étape suivante** : vous savez répondre à « pourquoi l'agent a-t-il répondu ça ? » sans deviner.

---

## La règle d'or du diagnostic

**Ne diagnostiquez jamais depuis la réponse finale.** Une réponse correcte peut avoir été produite sans le bon Skill, et une réponse fausse peut venir d'une donnée absente plutôt que d'une règle mal écrite. Les deux cas se corrigent à des endroits opposés.

La trace d'activité vous dit ce qui s'est réellement passé : quel Skill a été chargé, quelle recherche a eu lieu, ce qui est remonté.

## Les deux surfaces d'observation

**La trace d'activité** — pour un échange précis, en développement comme en production. C'est votre outil de diagnostic principal. Vous l'ouvrez depuis un échange, dans Preview ou depuis Monitor.

**L'onglet Monitor** — pour la vue d'ensemble après publication : l'activité, les tâches, les fichiers consultés, les erreurs, et une zone **Performance** qui rassemble les réactions pouce vers le haut / pouce vers le bas et les commentaires laissés par les utilisateurs.

## Les cinq questions à poser aux données, chaque semaine

| Question | Où regarder | Ce qui doit vous alerter |
|---|---|---|
| Les utilisateurs sont-ils satisfaits ? | Monitor > Performance, réactions et commentaires | Une série de pouces vers le bas sur un même type de question |
| Quels Skills se déclenchent, et lesquels jamais ? | Traces d'activité, par échantillon | Un Skill qui ne se charge **jamais** : sa description ne correspond pas au vocabulaire réel |
| Sur quoi l'agent ne trouve-t-il rien ? | Échanges avec « non trouvé » | Un terme métier récurrent : candidat pour la table de vocabulaire du Skill 4 |
| Y a-t-il des erreurs techniques ? | Monitor > erreurs | Erreurs d'accès à la source : connexion ou droits SharePoint |
| L'agent a-t-il compté ou promis une liste complète ? | Relecture d'échantillon | **Toute occurrence est un incident**, à traiter comme une régression |

La dernière ligne mérite une vigilance particulière : c'est le comportement le plus difficile à détecter automatiquement, et le plus dommageable. Réservez-lui une relecture d'échantillon régulière.

## Le vocabulaire réel : votre meilleure source d'amélioration

Le bénéfice le plus concret de cette surveillance est la découverte du **vocabulaire que vos utilisateurs emploient vraiment**. Chaque recherche infructueuse sur un mot métier est un candidat pour la table du Skill 4.

Procédure d'amélioration, à répéter mensuellement :

1. Relevez les termes qui ne trouvent rien, et leur fréquence.
2. Identifiez le libellé officiel visé, en vérifiant dans `KPIDictionary`.
3. N'ajoutez que les termes **récurrents** et **non ambigus** — un terme vu une fois n'est pas un motif.
4. Ajoutez l'entrée dans le Skill 4 (voir `05_04`), rejouez la suite de tests, republiez.

C'est ce cycle qui fait progresser l'agent dans la durée, et il ne coûte rien d'autre que l'édition d'un fichier Markdown.

## Limites d'observabilité à connaître

- La trace montre **ce que l'agent a fait**, pas **pourquoi le modèle a décidé ainsi**. Vous observez des effets, vous inférez des causes.
- Les données de conversation ont une **rétention limitée** dans le produit ; exportez ce que vous voulez conserver.
- Le comportement est **probabiliste** : deux exécutions de la même question peuvent différer. Ne concluez jamais sur un échantillon de un — c'est aussi vrai pour un succès que pour un échec.

## Rythme de surveillance

| Période | Ce que vous faites |
|---|---|
| Pendant le pilote | Relecture **quotidienne** des échanges : c'est là que vous apprenez le plus |
| Premier mois après bascule | Revue hebdomadaire des cinq questions ci-dessus |
| En régime établi | Revue mensuelle + suite de tests complète (voir `06_03`) |

## Critères de fin d'étape

- [ ] J'ai ouvert la trace d'activité sur au moins cinq échanges réels.
- [ ] Je sais y lire quel Skill s'est chargé.
- [ ] La revue hebdomadaire est planifiée et attribuée à quelqu'un.
- [ ] Un relevé des termes non trouvés est en place.
