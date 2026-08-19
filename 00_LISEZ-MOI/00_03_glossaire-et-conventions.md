# 00.03 — Glossaire et conventions

## Objectif du fichier

- **À quoi sert ce fichier** : fixer le vocabulaire, pour que « Skill », « harness » ou « orchestration » veuillent dire la même chose dans tout le dépôt.
- **Étape du développement** : étape 00, cadrage.
- **Ce que vous faites dans Copilot Studio à partir de ce fichier** : rien.
- **Résultat attendu avant de passer à l'étape suivante** : plus aucune ambiguïté de vocabulaire.

---

## Vocabulaire plateforme

| Terme | Définition retenue dans ce dépôt |
|---|---|
| **Nouvelle expérience** | Les agents propulsés par le **harness GitHub Copilot**, disponibles en GA depuis le 3 août 2026. C'est ce que nous construisons. |
| **Harness** | Le moteur d'exécution entre votre configuration et le modèle : il décide quand appeler le modèle, quels composants lui envoyer, et quels outils appeler. Copilot Studio en propose trois : GitHub Copilot, standard, Copilot chat. **Le choix est figé à la création de l'agent et n'est pas convertible.** |
| **Expérience classique / harness standard** | L'ancien modèle : topics, phrases déclencheuses, nœuds de condition, variables, Power Fx. C'est ce que l'agent actuel utilise. Nous n'y revenons pas. |
| **Orchestration** | Le raisonnement qui, à chaque tour, décide s'il faut chercher dans le Knowledge, charger un Skill, et comment composer la réponse. Vous ne la programmez pas ; vous l'influencez par les Instructions et par la qualité des descriptions. |
| **Instructions** | Le texte en langage naturel qui définit le comportement de l'agent. **Toujours entièrement en contexte, à chaque tour.** |
| **Knowledge** | Une source de données que l'agent peut interroger pour fonder ses réponses. Ici : la liste SharePoint `KPIDictionary`. |
| **Skill** | Un fichier Markdown (`SKILL.md` : un nom, une description, des instructions) chargé **à la demande** quand la description correspond à la demande de l'utilisateur. Limite plateforme : 100 Skills par agent. |
| **Description (d'un Skill ou d'une source)** | Ce n'est pas de la documentation pour humains : c'est **la métadonnée de routage** que l'orchestrateur lit pour décider quoi mobiliser. Elle se rédige comme telle. |
| **Trace d'activité** | La vue qui montre, après un échange, ce que l'agent a fait : quel Skill s'est chargé, quelle recherche a eu lieu. C'est votre principal outil de débogage. |
| **Copilot Credits** | L'unité de facturation à l'usage du harness GitHub Copilot. Elle est consommée **aussi pendant la construction, la préversion et les évaluations**. |

## Vocabulaire métier du projet

| Terme | Définition |
|---|---|
| **KPIDictionary** | La liste SharePoint, source unique de vérité de la migration MyBI → SAC. 2 464 lignes, 12 colonnes métier. |
| **MyBI** | L'ancien outil de reporting. Ses noms de champs sont l'historique. |
| **SAC** | SAP Analytics Cloud, l'outil cible. Ses noms de champs et de requêtes sont **officiels**. |
| **Requête SAC** | Un rapport SAC. 39 au total. Son nom n'existe **qu'en anglais**. |
| **Persona** | Le public cible d'une requête. Six valeurs officielles : `Finance`, `Operations`, `Supply`, `Merchant Retail`, `Merchant Fashion`, `Merchant Dining`. Chaque requête en a exactement un. |
| **Type de champ** | `Primary KPI`, `Derived KPI` ou `Dimension`, dans la colonne `KPI / dimension`. |
| **Ligne** | Une ligne = **un couple (requête, champ)**. Un même champ se répète sur autant de lignes qu'il y a de requêtes qui le portent. |
| **`new` / `New`** | Dans une colonne MyBI, ce n'est **pas** un nom de champ : cela signifie « nouveau champ, sans équivalent MyBI ». |
| **Verbatim** | Citer une valeur officielle exactement, coquilles et préfixes compris, sans traduire ni corriger. |

## Conventions d'écriture du dépôt

- Les **noms de dossiers et de fichiers** sont numérotés dans l'ordre d'exécution : `NN_DOSSIER/NN_MM_sujet.md`.
- Tout ce qui doit être **collé dans Copilot Studio** est dans un bloc de code, en anglais, complet, sans passage à compléter.
- Les **chemins d'interface** sont écrits ainsi : `Onglet Build > panneau Composants > Skills > + Ajouter`.
- Une affirmation issue de la documentation Microsoft est marquée **[OFFICIEL]**. Une recommandation propre à ce projet est marquée **[CHOIX PROJET]**. Un point à vérifier dans votre environnement est marqué **[À VÉRIFIER]**.

## Critères de fin d'étape

- [ ] Le vocabulaire est clair, en particulier la différence entre Instructions, Knowledge et Skill.
- [ ] J'ai noté qu'une description est une métadonnée de routage, pas de la documentation.
- [ ] Je passe au dossier `01_PREREQUIS_ET_DECISIONS`.
