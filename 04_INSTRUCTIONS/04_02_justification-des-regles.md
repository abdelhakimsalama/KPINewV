# 04.02 — Pourquoi chaque règle est là (et pourquoi elle n'est pas ailleurs)

## Objectif du fichier

- **À quoi sert ce fichier** : justifier chacune des 23 règles collées en `04_01`, pour que vous puissiez en modifier une plus tard **sans casser** ce qu'elle protégeait.
- **Étape du développement** : étape 04, comportement permanent. À lire une fois maintenant, à relire avant toute modification.
- **Ce que vous faites dans Copilot Studio à partir de ce fichier** : rien. C'est la notice des Instructions.
- **Résultat attendu avant de passer à l'étape suivante** : vous savez quelle règle protège quoi, et laquelle vous n'avez pas le droit de retirer.

---

## Lecture par bloc

| Bloc de `04_01` | Ce qu'il protège | Si vous le retirez |
|---|---|---|
| **Identity and scope** (règles 1 à 3 du bloc) | Le périmètre : l'agent sait ce qu'il couvre et ce qu'il ne couvre pas | L'agent répond à des questions de culture générale avec l'autorité d'un dictionnaire officiel |
| **Grounding** (1 → 4) | La règle métier n°2, zéro invention | Le défaut le plus grave du projet réapparaît : une réponse fausse que rien ne signale |
| **Figures, counts and completeness** (5 → 8) | Les règles précisées 5 et 8 | L'agent réinvente des chiffres, comme le fait l'agent actuel avec ses « 202 champs renommés » |
| **Verbatim** (9 → 11) | La règle métier n°3 | Les libellés officiels sont traduits ou « corrigés », et deviennent inutilisables pour retrouver un champ dans SAC |
| **Never choose for the user** (12, 13) | La règle métier n°4 | L'agent tranche seul entre deux champs sans rapport, avec l'air d'être sûr |
| **Target Personas** (14, 15) | La règle métier n°6 | L'agent déduit un persona d'un intitulé de poste et filtre sur une hypothèse |
| **Language** (16 → 18) | La règle métier n°11 | Réponses dans la mauvaise langue, ou pire : libellés officiels traduits |
| **Answer format** (19 → 22) | Lisibilité et règles 12, 13 | Retour des tableaux Markdown et perte du signalement des anciens noms MyBI |
| **Conversation** (23, 24) | Ce que faisaient les topics `Greeting` et `Fallback` | Consommation inutile sur un « bonjour », et réponses hasardeuses hors périmètre |

## Les quatre règles auxquelles il ne faut pas toucher

Elles portent la valeur du produit. Toutes les autres sont ajustables.

1. **Règle 1 et 2 — ne rien affirmer que la source ne montre.** C'est la raison d'être d'un dictionnaire de référence. Un agent qui invente une définition de KPI est pire qu'une absence d'agent, parce que l'erreur se propage dans des rapports.
2. **Règle 6 — un chiffre vient des données, jamais d'une estimation.** L'agent a le droit de compter, parce que la source le permet nativement ; il n'a jamais le droit d'estimer. C'est l'origine du chiffre qui est contrôlée, pas le fait d'en donner un.
3. **Règle 9 — verbatim.** Un libellé officiel modifié ne se retrouve plus dans SAC. La coquille fait partie de l'identifiant.
4. **Règle 12 — ne jamais choisir.** Deux champs peuvent répondre au même mot métier sans avoir le moindre rapport : `Mat: Product category` désigne un secteur d'activité (alcool, parfum, soin), `Fashion : Prod. Categ` un attribut mode (permanent, réassort, saisonnier). Trancher au hasard, c'est répondre faux une fois sur deux avec assurance.

## Trois erreurs classiques à ne pas commettre en modifiant ces Instructions

**Ajouter une procédure de cas d'usage.** La tentation viendra au premier test raté : « il suffirait d'ajouter ici comment traiter les formules ». Non — cela va dans le Skill `kpi-field-details`. Une procédure écrite dans les Instructions est chargée à **chaque** tour, y compris pour les questions qui n'ont rien à voir : c'est ainsi que le bloc d'instructions actuel a atteint la saturation.

**Coller des données.** Une liste de champs, une correspondance, un exemple de valeur : tout cela vit dans `KPIDictionary`. Les Instructions décrivent un comportement, jamais un contenu.

**Croire que la règle garantit le comportement.** Ces règles sont interprétées par un modèle. Elles orientent fortement, elles ne contraignent pas absolument. C'est pourquoi l'étape 06 existe : ce qui n'est pas testé n'est pas garanti.

## Ce qui n'est volontairement pas dans les Instructions

| Sujet | Où il vit | Motif |
|---|---|---|
| La table des synonymes (12 entrées) | Skill `business-vocabulary-and-ambiguity` | N'est utile que si l'utilisateur emploie un mot métier |
| Le protocole d'ambiguïté détaillé | Même Skill | N'est utile que face à plusieurs candidats |
| La mise en forme d'une formule en bloc de code | Skill `kpi-field-details` | Ne concerne que les questions de formule |
| Le format d'une correspondance MyBI → SAC | Skill `mybi-sac-mapping` | Ne concerne que les questions de renommage |
| La conduite des questions multi-critères et des décomptes par requête | Skill `sac-query-lookup` | Cas particulier des questions de requête |
| La liste des six personas et leur conduite | Skill `personas-and-scope` (rappel court en règle 13) | Le détail n'est utile que sur les questions de persona |

Cette répartition est ce qui rend le système maintenable : pour changer la façon dont l'agent présente une formule, vous éditez **un** fichier de 60 lignes, sans risquer d'effet de bord sur le reste du comportement.

## Critères de fin d'étape

- [ ] Je sais quelle règle protège quoi.
- [ ] J'ai identifié les quatre règles intouchables.
- [ ] J'ai compris qu'une procédure de cas d'usage ne doit **jamais** être ajoutée ici.
- [ ] Je passe au dossier `05_SKILLS`.
