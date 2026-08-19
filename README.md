# KPI Dictionary Assistant — Guide de développement pas à pas

Documentation de référence pour construire l'agent **KPI Dictionary Assistant** dans la **nouvelle expérience Microsoft Copilot Studio** (harness GitHub Copilot).

Lisez les dossiers dans l'ordre `00 → 10`. Chaque dossier est une étape, chaque fichier une tâche. Vous n'avez rien à reconstruire ni à chercher ailleurs : tout ce qui doit être collé dans Copilot Studio est fourni en entier, prêt à l'emploi.

---

## L'architecture en une ligne

**Instructions + Knowledge + Skills.** Aucun outil, aucun flux Power Automate, aucun code, aucune Memory, aucun agent connecté.

```
Agent « KPI Dictionary Assistant »  ── harness GitHub Copilot · modèle OpenAI/Microsoft
   ├── INSTRUCTIONS ...... les règles vraies à chaque tour
   ├── KNOWLEDGE (1) ..... la liste SharePoint « KPIDictionary », en direct
   └── SKILLS (5) ........ kpi-field-details · mybi-sac-mapping · sac-query-lookup
                           business-vocabulary-and-ambiguity · personas-and-scope
```

## Les étapes

| Dossier | Étape | Ce que vous obtenez |
|---|---|---|
| [`00_LISEZ-MOI`](00_LISEZ-MOI/) | Cadrage | Le mode d'emploi, l'architecture cible, le glossaire |
| [`01_PREREQUIS_ET_DECISIONS`](01_PREREQUIS_ET_DECISIONS/) | Prérequis | Accès, licences, décisions d'architecture, répartition des règles |
| [`02_CREATION_DE_LAGENT`](02_CREATION_DE_LAGENT/) | Création | Un agent qui répond, avec le bon modèle |
| [`03_KNOWLEDGE_SHAREPOINT`](03_KNOWLEDGE_SHAREPOINT/) | Données | L'agent lit `KPIDictionary` en direct |
| [`04_INSTRUCTIONS`](04_INSTRUCTIONS/) | Comportement permanent | Les 26 règles globales, prêtes à copier |
| [`05_SKILLS`](05_SKILLS/) | Comportements situationnels | Les 5 Skills, chacun avec son `SKILL.md` complet |
| [`06_EVALUATION`](06_EVALUATION/) | Qualité | 53 cas de test, repères de non-régression, seuils, politique de régression |
| [`07_PUBLICATION`](07_PUBLICATION/) | Mise en service | L'agent publié dans Teams, bascule depuis l'ancien |
| [`08_MONITORING_ET_COUTS`](08_MONITORING_ET_COUTS/) | Exploitation | Ce que fait l'agent, ce qu'il coûte |
| [`09_ALM_ET_MAINTENANCE`](09_ALM_ET_MAINTENANCE/) | Durée de vie | Modifier une règle sans effet de bord |
| [`10_BACKLOG`](10_BACKLOG/) | Lucidité | Le registre des limites **mesurées**, et quoi faire alors |

## Les trois fichiers à lire en premier

1. [`00_02_architecture-en-un-coup-doeil.md`](00_LISEZ-MOI/00_02_architecture-en-un-coup-doeil.md) — l'image complète de l'agent.
2. [`01_02_journal-des-decisions-darchitecture.md`](01_PREREQUIS_ET_DECISIONS/01_02_journal-des-decisions-darchitecture.md) — pourquoi il a cette forme, et ce qui a été écarté.
3. [`10_01_limites-a-confirmer-par-les-tests.md`](10_BACKLOG/10_01_limites-a-confirmer-par-les-tests.md) — le registre des limites, vide au départ : **rien n'y entre sans mesure**.

## Le principe directeur

> On part toujours du plus simple et du plus natif. Un composant supplémentaire ne s'ajoute que si un besoin fonctionnel réel, constaté et documenté, ne peut pas être couvert autrement — et la justification s'écrit dans le journal des décisions.

Les deux conséquences les plus importantes de ce principe :

- **Aucune capacité n'est retirée par hypothèse.** Les listes SharePoint en Knowledge prennent nativement en charge les requêtes analytiques et d'agrégation, décomptes compris ([documentation officielle](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-sharepoint-lists), préversion). Les décomptes et croisements restent donc au périmètre, et l'étape 06 mesure ce qui tient réellement.
- **L'agent raisonne, il n'applique pas un barème.** Il comprend la demande et détermine le résultat à partir des données de la liste. Aucun chiffre métier n'est figé dans les Instructions ni dans un Skill ; les repères de l'ancien runtime servent uniquement au contrôle en test.
- **L'objectif est le résultat juste, dit simplement.** La réponse ne contient que ce qui sert le résultat demandé, jamais la méthode interne employée pour l'obtenir — les champs qui répondent aux critères s'affichent, les colonnes interrogées et les filtres non. Si l'utilisateur demande une justification, l'agent cite les entrées du dictionnaire qui l'établissent : c'est de la preuve métier, pas de la méthode. La traçabilité technique, elle, reste dans la trace d'activité, sur laquelle l'étape 06 s'appuie avant de contrôler chaque chiffre **dans la liste SharePoint**.
- **Le dépôt est la source du comportement, pas son reflet.** Les Instructions et les Skills sont du texte : on les modifie ici d'abord, on les reporte ensuite dans le produit.

## Conventions

- Les fichiers sont en **français** ; tout ce qui se colle **dans** Copilot Studio est en **anglais**.
- **[OFFICIEL]** = documenté par Microsoft · **[CHOIX PROJET]** = décision de ce projet · **[À VÉRIFIER]** = à confirmer dans votre environnement.
- Copilot Studio évolue vite : vérifiez les limites et les statuts de préversion dans la documentation courante avant toute décision de production.

## Contenus prêts à téléverser

Le dossier [`_a-televerser/`](_a-televerser/) contient les six artefacts qui vont réellement dans Copilot Studio : `instructions.md` et les cinq `skills/<nom>/SKILL.md`. Ils sont **générés** depuis les fiches d'étape par `python3 outils/extraire-contenus-agent.py` — les fiches restent la source de vérité, le dossier ne s'édite jamais à la main. `--verifier` contrôle que les deux sont synchronisés.

## Documentation de référence

Le dossier [`_reference-copilot-studio/`](_reference-copilot-studio/) contient le corpus d'expertise sur la nouvelle expérience Copilot Studio qui a servi à concevoir cette architecture : le guide d'architecture complet, 10 études de cas et 14 notes de recherche. Il n'est pas nécessaire à l'exécution de ce guide.
