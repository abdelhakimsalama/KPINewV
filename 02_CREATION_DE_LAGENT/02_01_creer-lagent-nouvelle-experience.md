# 02.01 — Créer l'agent dans la nouvelle expérience

## Objectif du fichier

- **À quoi sert ce fichier** : créer l'agent, sur le bon harness, avec la bonne identité — la seule étape irréversible du projet.
- **Étape du développement** : étape 02, création.
- **Ce que vous faites dans Copilot Studio** : vous créez un agent, vous saisissez son nom, sa description et une instruction provisoire, puis vous l'enregistrez.
- **Résultat attendu avant de passer à l'étape suivante** : un agent existe, s'ouvre sur l'onglet **Build**, et répond dans l'onglet **Preview** — même mal, puisqu'il n'a encore ni règles ni données.

---

## ⚠️ Deux choix irréversibles

1. **Le harness.** Il se choisit à la création et **aucune conversion n'existe dans un sens ni dans l'autre** **[OFFICIEL]**. Vous devez créer un agent de la **nouvelle expérience** (harness GitHub Copilot).
2. **Le nom de schéma.** Le dernier nom saisi **avant le premier enregistrement** détermine le nom de schéma, qui devient ensuite en lecture seule **[OFFICIEL]**. Saisissez donc le nom définitif avant d'enregistrer.

## Ce que vous faites

1. Ouvrez `https://copilotstudio.microsoft.com/` et **vérifiez l'environnement** en haut à droite : ce doit être votre environnement de développement, pas celui de l'agent actuel.
2. Sur la page **Home**, vérifiez que la bascule **New experience** est **activée**. Si vous voyez « Other ways to build », c'est l'entrée vers le harness standard : ce n'est pas ce que nous voulons.
3. Sélectionnez la tuile **Agent**. L'agent s'ouvre dans le concepteur, onglet **Build**, le curseur dans le champ du nom.
4. Saisissez le nom :

```
KPI Dictionary Assistant
```

5. Avant d'enregistrer, ouvrez les options pour vérifier la **langue principale**, la **solution** et le **nom de schéma**. Langue principale : `English (United States)` **[CHOIX PROJET]** — l'agent répondra malgré tout en français, la règle de langue étant portée par les Instructions ; la langue principale n'est pas une restriction de la langue de conversation.
6. Dans **Instructions**, collez ce texte provisoire — il sera intégralement remplacé à l'étape 04 :

```
You are the KPI Dictionary Assistant for the MyBI-to-SAC reporting migration.
You are under construction. Until your instructions and knowledge are configured,
answer every question with: "I am not configured yet."
```

7. Sélectionnez l'icône **Save**.

## Description de l'agent

Après l'enregistrement, renseignez la description de l'agent. Elle est visible des utilisateurs et sert aussi à l'identifier dans les catalogues.

```
Answers questions about the MyBI-to-SAC reporting migration dictionary: KPI and field definitions, formulas, field types, SAC queries, MyBI-to-SAC name mappings, and Target Personas. Grounded exclusively in the official KPIDictionary list.
```

## Vérification

1. Ouvrez l'onglet **Preview**.
2. Écrivez « bonjour ».
3. L'agent doit répondre — probablement « I am not configured yet. »

Si l'onglet **Preview** n'est pas disponible, c'est que l'agent n'a pas été enregistré.

> **Rappel de coût** : ce premier échange consomme déjà des Copilot Credits. C'est normal et documenté : la facturation à l'usage couvre aussi la construction et les tests **[OFFICIEL]**.

## En cas de problème

| Symptôme | Cause probable | Correction |
|---|---|---|
| Pas de tuile **Agent** sur la page d'accueil | La bascule **New experience** est désactivée | Activez-la sur la page Home |
| Le concepteur affiche des **Topics** | Vous avez créé un agent du harness standard | Supprimez-le et recommencez : il n'est pas convertible |
| Erreur de capacité au premier message | Aucune allocation de crédits sur l'environnement | Retournez à `01_01`, section 3 |

## Critères de fin d'étape

- [ ] L'agent `KPI Dictionary Assistant` existe dans l'environnement de développement.
- [ ] Le concepteur affiche **Build / Preview / Evaluate / Monitor** et **aucun onglet Topics**.
- [ ] Le panneau de composants à droite affiche Model, Skills, Tools, Knowledge, Connected agents, Memory.
- [ ] L'agent répond dans **Preview**.
